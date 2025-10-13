"""
AI Promotion Service - Tích hợp MongoDB
Sử dụng dữ liệu trực tiếp từ MongoDB thay vì CSV files
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

# Optional: Surprise library (needs C compiler on Windows)
try:
    from surprise import SVD, Dataset, Reader
    SURPRISE_AVAILABLE = True
except ImportError:
    SURPRISE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Surprise library not available (optional - needs C compiler)")

import google.generativeai as genai
import json

from infrastructure.db.mongodb_access import mongodb_data
from utils.numpy_serializer import convert_numpy_types

logger = logging.getLogger(__name__)

class AIPromotionService:
    """AI Promotion Service sử dụng MongoDB data"""
    
    def __init__(self, gemini_api_key: str):
        self.data_access = mongodb_data
        self.gemini_api_key = gemini_api_key
        
        # Setup Gemini - Using gemini-2.0-flash (latest stable model)
        # gemini-pro and gemini-1.5-* are all deprecated
        genai.configure(api_key=gemini_api_key)
        self.llm_model = genai.GenerativeModel('gemini-2.5-pro')
        
        logger.info("✅ AI Promotion Service initialized")
    
    def analyze_business_health(self) -> Dict[str, Any]:
        """Phân tích sức khỏe kinh doanh từ MongoDB data"""
        try:
            # Get data from MongoDB
            orders_df = self.data_access.get_orders_data()
            products_df = self.data_access.get_products_data()
            users_df = self.data_access.get_users_data()
            ratings_df = self.data_access.get_ratings_data()
            
            if orders_df.empty:
                return {"error": "No orders data available"}
            
            # Convert createdAt to datetime
            orders_df['createdAt'] = pd.to_datetime(orders_df['createdAt'])
            
            # Business metrics
            total_orders = len(orders_df)
            total_revenue = orders_df['totalPrice'].sum() if 'totalPrice' in orders_df.columns else 0
            total_revenue = float(total_revenue) if pd.notna(total_revenue) else 0.0
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            avg_order_value = float(avg_order_value) if pd.notna(avg_order_value) else 0.0
            
            # Time-based analysis
            orders_df['date'] = orders_df['createdAt'].dt.date
            daily_orders = orders_df.groupby('date').size()
            
            # Product performance
            product_performance = {}
            if not products_df.empty:
                # Flatten orderItems first
                flattened_orders = []
                for _, order in orders_df.iterrows():
                    if 'orderItems' in order and isinstance(order['orderItems'], list):
                        for item in order['orderItems']:
                            if isinstance(item, dict):
                                flattened_orders.append({
                                    'order_id': order['_id'],
                                    'product_id': str(item.get('product', '')),
                                    'quantity': item.get('quantity', 0),
                                    'total': item.get('total', 0)
                                })
                
                flat_df = pd.DataFrame(flattened_orders) if flattened_orders else pd.DataFrame()
                
                for _, product in products_df.iterrows():
                    product_id = str(product['_id'])
                    
                    # Get orders for this product from flattened data
                    if not flat_df.empty:
                        product_orders = flat_df[flat_df['product_id'] == product_id]
                        orders_count = len(product_orders)
                        product_revenue = product_orders['total'].sum() if 'total' in product_orders.columns else 0
                        product_revenue = float(product_revenue) if pd.notna(product_revenue) else 0.0
                    else:
                        orders_count = 0
                        product_revenue = 0
                    
                    product_performance[product_id] = {
                        'name': product.get('productName', 'Unknown'),
                        'price': float(product.get('productPrice', 0)),
                        'orders_count': int(orders_count),
                        'total_revenue': float(product_revenue),
                        'avg_rating': float(product.get('averageRating', 0))
                    }
            
            # Customer analysis
            customer_metrics = {}
            if not users_df.empty:
                customer_metrics = {
                    'total_customers': len(users_df),
                    'active_customers': len(orders_df['userId'].unique()) if 'userId' in orders_df.columns else 0,
                    'repeat_customers': len(orders_df[orders_df['userId'].duplicated()]['userId'].unique()) if 'userId' in orders_df.columns else 0
                }
            
            # Clean daily orders trend
            daily_orders_dict = daily_orders.to_dict()
            daily_orders_dict = {str(k): int(v) for k, v in daily_orders_dict.items()}
            
            business_health = {
                'total_orders': int(total_orders),
                'total_revenue': total_revenue,
                'avg_order_value': avg_order_value,
                'daily_orders_trend': daily_orders_dict,
                'product_performance': product_performance,
                'customer_metrics': customer_metrics,
                'analysis_date': datetime.now().isoformat()
            }
            
            # Convert all numpy types to native Python types for JSON serialization
            business_health = convert_numpy_types(business_health)
            
            logger.info("✅ Business health analysis completed")
            return business_health
            
        except Exception as e:
            logger.error(f"❌ Error analyzing business health: {e}")
            return {"error": str(e)}
    
    def discover_product_combos(self) -> Dict[str, Any]:
        """Khai phá combo sản phẩm từ MongoDB orders"""
        try:
            orders_df = self.data_access.get_orders_data()
            
            if orders_df.empty:
                return {"error": "No orders data available"}
            
            # Prepare transaction data for market basket analysis
            transactions = []
            for _, order in orders_df.iterrows():
                transaction = []
                
                # Extract products from order items
                for i in range(8):  # Max 8 items per order
                    product_col = f'orderItems[{i}].product'
                    if product_col in orders_df.columns and pd.notna(order[product_col]):
                        transaction.append(order[product_col])
                
                if transaction:
                    transactions.append(transaction)
            
            if not transactions:
                return {"error": "No valid transactions found"}
            
            # Market Basket Analysis
            te = TransactionEncoder()
            te_ary = te.fit(transactions).transform(transactions)
            df_transactions = pd.DataFrame(te_ary, columns=te.columns_)
            
            # Find frequent itemsets
            frequent_itemsets = apriori(df_transactions, min_support=0.1, use_colnames=True)
            
            if frequent_itemsets.empty:
                return {"combos": [], "message": "No frequent itemsets found"}
            
            # Generate association rules
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
            
            # Format results
            combos = []
            for _, rule in rules.iterrows():
                antecedents = list(rule['antecedents'])
                consequents = list(rule['consequents'])
                
                combos.append({
                    'antecedents': antecedents,
                    'consequents': consequents,
                    'support': rule['support'],
                    'confidence': rule['confidence'],
                    'lift': rule['lift']
                })
            
            logger.info(f"✅ Discovered {len(combos)} product combos")
            return {"combos": combos}
            
        except Exception as e:
            logger.error(f"❌ Error discovering product combos: {e}")
            return {"error": str(e)}
    
    def generate_recommendations(self) -> Dict[str, Any]:
        """Tạo recommendations từ MongoDB data"""
        try:
            orders_df = self.data_access.get_orders_data()
            products_df = self.data_access.get_products_data()
            ratings_df = self.data_access.get_ratings_data()
            
            if orders_df.empty or products_df.empty:
                return {"error": "Insufficient data for recommendations"}
            
            # Product popularity analysis
            product_popularity = {}
            
            # Flatten orderItems first
            flattened_orders = []
            for _, order in orders_df.iterrows():
                if 'orderItems' in order and isinstance(order['orderItems'], list):
                    for item in order['orderItems']:
                        if isinstance(item, dict):
                            flattened_orders.append({
                                'order_id': order['_id'],
                                'product_id': str(item.get('product', '')),
                                'quantity': item.get('quantity', 0),
                                'total': item.get('total', 0)
                            })
            
            flat_df = pd.DataFrame(flattened_orders) if flattened_orders else pd.DataFrame()
            
            for _, product in products_df.iterrows():
                product_id = str(product['_id'])
                
                # Get orders for this product from flattened data
                if not flat_df.empty:
                    product_orders = flat_df[flat_df['product_id'] == product_id]
                    orders_count = len(product_orders)
                else:
                    orders_count = 0
                
                # Get ratings for this product
                product_ratings = ratings_df[ratings_df['productId'] == product['_id']] if not ratings_df.empty else pd.DataFrame()
                avg_rating = product_ratings['rating'].mean() if not product_ratings.empty else 0
                
                product_popularity[product_id] = {
                    'name': product.get('productName', 'Unknown'),
                    'price': float(product.get('productPrice', 0)),
                    'orders_count': int(orders_count),
                    'avg_rating': float(avg_rating) if pd.notna(avg_rating) else 0.0,
                    'total_ratings': len(product_ratings),
                    'popularity_score': float(orders_count * (avg_rating / 5.0) if avg_rating > 0 else orders_count)
                }
            
            # Sort by popularity score
            sorted_products = sorted(product_popularity.items(), 
                                  key=lambda x: x[1]['popularity_score'], 
                                  reverse=True)
            
            # Top products for promotion
            top_products = [item[1] for item in sorted_products[:5]]
            
            # Low-performing products (need promotion)
            low_performing = [item[1] for item in sorted_products[-3:]]
            
            recommendations = {
                'top_products': top_products,
                'low_performing_products': low_performing,
                'promotion_candidates': low_performing,
                'analysis_date': datetime.now().isoformat()
            }
            
            # Convert all numpy types to native Python types for JSON serialization
            recommendations = convert_numpy_types(recommendations)
            
            logger.info("✅ Generated product recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return {"error": str(e)}
    
    def generate_llm_insights(self, ml_results: Dict[str, Any]) -> Dict[str, Any]:
        """Sử dụng Gemini để tạo insights từ ML results"""
        try:
            prompt = f"""
            Bạn là chuyên gia marketing cho cửa hàng bánh ngọt AVOCADO.
            
            Dữ liệu phân tích từ AI và MongoDB:
            {json.dumps(ml_results, ensure_ascii=False, indent=2)}
            
            Hãy đưa ra phân tích và khuyến nghị chi tiết:
            
            1. **Tình hình kinh doanh hiện tại**:
               - Đánh giá tổng quan
               - Điểm mạnh và điểm yếu
               - Cơ hội cải thiện
            
            2. **Danh sách sản phẩm khuyến mại** (top 5):
               - Sản phẩm nên khuyến mãi
               - Lý do tại sao
               - Mức giảm giá đề xuất
               - Thời gian khuyến mãi
            
            3. **Combo sản phẩm nên gợi ý** (top 3):
               - Combo cụ thể
               - Giá combo đề xuất
               - Target audience
               - Chiến lược marketing
            
            4. **Lịch khuyến mại tối ưu**:
               - Thời điểm thực hiện
               - Chiến lược theo mùa
               - Budget allocation
               - KPI theo dõi
            
            5. **Insights và khuyến nghị**:
               - Xu hướng thị trường
               - Cạnh tranh
               - Rủi ro cần lưu ý
               - Cơ hội phát triển
            
            Format output theo JSON structure rõ ràng và actionable.
            """
            
            response = self.llm_model.generate_content(prompt)
            
            # Parse LLM response
            try:
                insights = json.loads(response.text)
            except json.JSONDecodeError:
                # If not valid JSON, create structured response
                insights = {
                    "raw_response": response.text,
                    "parsed_at": datetime.now().isoformat()
                }
            
            logger.info("✅ Generated LLM insights")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating LLM insights: {e}")
            return {"error": str(e)}
    
    def generate_complete_promotion_strategy(self) -> Dict[str, Any]:
        """Tạo chiến lược promotion hoàn chỉnh từ MongoDB data"""
        try:
            logger.info("🚀 Starting complete promotion strategy generation")
            
            # Step 1: Analyze business health
            business_health = self.analyze_business_health()
            
            # Step 2: Discover product combos
            product_combos = self.discover_product_combos()
            
            # Step 3: Generate recommendations
            recommendations = self.generate_recommendations()
            
            # Step 4: Combine all ML results
            ml_results = {
                "business_health": business_health,
                "product_combos": product_combos,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }
            
            # Step 5: Generate LLM insights
            llm_insights = self.generate_llm_insights(ml_results)
            
            # Step 6: Create final strategy
            final_strategy = {
                "ml_analysis": ml_results,
                "llm_insights": llm_insights,
                "strategy_generated_at": datetime.now().isoformat(),
                "status": "completed"
            }
            
            # Step 7: Save to MongoDB
            self.data_access.save_ai_insights(final_strategy)
            self.data_access.save_promotion_recommendations(final_strategy)
            
            logger.info("✅ Complete promotion strategy generated and saved")
            return final_strategy
            
        except Exception as e:
            logger.error(f"❌ Error generating complete promotion strategy: {e}")
            return {"error": str(e)}
    
    def get_recent_strategies(self, limit: int = 5) -> List[Dict]:
        """Lấy các chiến lược promotion gần nhất"""
        try:
            return self.data_access.get_recent_ai_insights(limit)
        except Exception as e:
            logger.error(f"❌ Error getting recent strategies: {e}")
            return []

# Example usage
def create_promotion_service(gemini_api_key: str) -> AIPromotionService:
    """Factory function để tạo promotion service"""
    return AIPromotionService(gemini_api_key)
