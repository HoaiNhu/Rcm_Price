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
        """Sử dụng Gemini để tạo insights từ ML results (Legacy version - basic)"""
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
            
            logger.info("✅ Generated LLM insights (legacy)")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating LLM insights: {e}")
            return {"error": str(e)}
    
    async def generate_enhanced_llm_insights(self, ml_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        🆕 ENHANCED VERSION - Sử dụng Gemini với đầy đủ Week 1-6 ML data
        
        Phase 1 Implementation: Enhanced LLM Integration
        - Fetch comprehensive data from Week 1-6 services
        - Provide full context to Gemini LLM
        - Generate data-driven insights with ML backing
        """
        try:
            logger.info("🚀 Starting enhanced LLM insights generation with Week 1-6 data")
            
            # Import Week 1-6 services
            from application.services.price_elasticity_service import get_elasticity_service
            from application.services.customer_segmentation_service import get_segmentation_service
            from application.services.personalized_pricing_service import get_pricing_service
            from application.services.pricing_simulator_service import get_simulator_service
            from application.services.smart_promotion_service import get_promotion_service
            
            # Fetch comprehensive ML data
            comprehensive_data = {}
            
            # Week 1: Price Elasticity
            try:
                elasticity_service = get_elasticity_service()
                elasticity_data = await elasticity_service.get_all_elasticities()
                comprehensive_data["price_elasticity"] = elasticity_data
                logger.info(f"✅ Fetched elasticity data: {len(elasticity_data.get('products', []))} products")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch elasticity data: {e}")
                comprehensive_data["price_elasticity"] = {"error": str(e)}
            
            # Week 2: Customer Segmentation
            try:
                segmentation_service = get_segmentation_service()
                segments = await segmentation_service.segment_customers()
                comprehensive_data["customer_segments"] = segments
                logger.info(f"✅ Fetched segments: {segments.get('total_customers', 0)} customers")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch segments: {e}")
                comprehensive_data["customer_segments"] = {"error": str(e)}
            
            # Week 3-4: Personalized Pricing
            try:
                pricing_service = get_pricing_service()
                pricing_matrix = await pricing_service.get_pricing_summary()
                comprehensive_data["personalized_pricing"] = pricing_matrix
                logger.info(f"✅ Fetched personalized pricing data")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch pricing data: {e}")
                comprehensive_data["personalized_pricing"] = {"error": str(e)}
            
            # Week 5: Simulation Results (latest runs)
            try:
                simulator_service = get_simulator_service()
                simulations = await simulator_service.get_all_scenarios()
                comprehensive_data["simulation_results"] = simulations
                logger.info(f"✅ Fetched simulation results")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch simulations: {e}")
                comprehensive_data["simulation_results"] = {"error": str(e)}
            
            # Week 6: Active Promotions
            try:
                promotion_service = get_promotion_service()
                promotions = await promotion_service.get_all_promotions()
                comprehensive_data["active_promotions"] = promotions
                logger.info(f"✅ Fetched active promotions: {len(promotions)} promotions")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch promotions: {e}")
                comprehensive_data["active_promotions"] = {"error": str(e)}
            
            # Add traditional business analysis
            comprehensive_data["business_health"] = ml_results.get("business_health", {})
            comprehensive_data["product_combos"] = ml_results.get("product_combos", {})
            comprehensive_data["recommendations"] = ml_results.get("recommendations", {})
            
            # Create enhanced prompt with comprehensive ML data
            prompt = f"""
            Bạn là chuyên gia marketing và data scientist cho cửa hàng bánh ngọt AVOCADO.
            
            🎯 NHIỆM VỤ: Phân tích toàn diện dữ liệu ML và đưa ra chiến lược actionable
            
            📊 DỮ LIỆU PHÂN TÍCH TOÀN DIỆN:
            
            ═══════════════════════════════════════════════════════════════
            1️⃣ PRICE ELASTICITY ANALYSIS (Week 1 - ML Model)
            ═══════════════════════════════════════════════════════════════
            {json.dumps(comprehensive_data.get("price_elasticity", {}), ensure_ascii=False, indent=2)}
            
            📌 Giải thích:
            - Elasticity < 0: Tăng giá → Giảm demand (hàng thông thường)
            - Elasticity > 0: Tăng giá → Tăng demand (hàng cao cấp/status symbol)
            - |Elasticity| > 1: Elastic (nhạy cảm với giá)
            - |Elasticity| < 1: Inelastic (ít nhạy cảm)
            
            ═══════════════════════════════════════════════════════════════
            2️⃣ CUSTOMER SEGMENTATION (Week 2 - RFM + K-Means)
            ═══════════════════════════════════════════════════════════════
            {json.dumps(comprehensive_data.get("customer_segments", {}), ensure_ascii=False, indent=2)}
            
            📌 Segments:
            - VIP: High value, frequent buyers (retention strategy)
            - REGULAR: Medium value, steady buyers (upsell strategy)
            - NEW: Recent first purchase (acquisition strategy)
            - AT_RISK: High value but not recent (win-back strategy)
            - LOST: High value, inactive >90 days (aggressive win-back)
            
            ═══════════════════════════════════════════════════════════════
            3️⃣ PERSONALIZED PRICING MATRIX (Week 3-4 - Rules Engine)
            ═══════════════════════════════════════════════════════════════
            {json.dumps(comprehensive_data.get("personalized_pricing", {}), ensure_ascii=False, indent=2)}
            
            📌 Pricing Rules:
            - VIP: -5% to +5% (loyalty pricing)
            - NEW: -15% to -5% (acquisition discount)
            - AT_RISK: -20% to -10% (win-back discount)
            
            ═══════════════════════════════════════════════════════════════
            4️⃣ MONTE CARLO SIMULATION RESULTS (Week 5 - Risk Analysis)
            ═══════════════════════════════════════════════════════════════
            {json.dumps(comprehensive_data.get("simulation_results", {}), ensure_ascii=False, indent=2)}
            
            📌 Metrics:
            - Mean revenue: Expected outcome
            - Confidence interval: 95% certainty range
            - Probability of success: Likelihood of positive outcome
            
            ═══════════════════════════════════════════════════════════════
            5️⃣ ACTIVE PROMOTIONS (Week 6 - Current Campaigns)
            ═══════════════════════════════════════════════════════════════
            {json.dumps(comprehensive_data.get("active_promotions", []), ensure_ascii=False, indent=2)}
            
            ═══════════════════════════════════════════════════════════════
            6️⃣ BUSINESS HEALTH METRICS (Traditional Analysis)
            ═══════════════════════════════════════════════════════════════
            {json.dumps(comprehensive_data.get("business_health", {}), ensure_ascii=False, indent=2)}
            
            ═══════════════════════════════════════════════════════════════
            
            🎯 YÊU CẦU OUTPUT - Format JSON với cấu trúc sau:
            
            {{
              "executive_summary": {{
                "overview": "Tóm tắt 2-3 câu về tình hình kinh doanh",
                "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
                "overall_health_score": 85
              }},
              
              "pricing_strategy_analysis": {{
                "products_to_increase_price": [
                  {{
                    "product_name": "Tên sản phẩm",
                    "current_price": 260000,
                    "recommended_price": 286000,
                    "elasticity": -0.3,
                    "reasoning": "Elasticity thấp, simulation cho thấy 87% khả năng tăng revenue",
                    "confidence": "high",
                    "expected_revenue_increase_pct": 8.3
                  }}
                ],
                "products_to_decrease_price": [...],
                "products_to_maintain": [...]
              }},
              
              "segment_strategy_recommendations": {{
                "VIP": {{
                  "count": 3,
                  "strategy": "Loyalty program, no discounts",
                  "action": "Tặng bonus points 2x cho mỗi đơn hàng",
                  "expected_impact": "Maintain retention rate >90%"
                }},
                "AT_RISK": {{
                  "count": 5,
                  "strategy": "Win-back campaign",
                  "action": "20% discount voucher, validity 60 days",
                  "expected_impact": "65% conversion rate based on segment profile"
                }},
                "NEW": {{
                  "count": 8,
                  "strategy": "Acquisition optimization",
                  "action": "14% welcome discount for first 3 orders",
                  "expected_impact": "Increase repeat purchase rate from 30% to 50%"
                }}
              }},
              
              "promotion_recommendations": [
                {{
                  "priority": 1,
                  "type": "PRICE_INCREASE_WITH_VOUCHER",
                  "product": "Bánh hoa xuân",
                  "action": "Tăng giá 260k → 286k, kèm voucher 16k cho REGULAR customers",
                  "ml_backing": "Elasticity -0.3, simulation 87% success probability",
                  "timeline": "Tuần tới",
                  "expected_outcome": "+8.3% revenue với 95% CI [6.2%, 10.5%]",
                  "risk_level": "low"
                }},
                {{
                  "priority": 2,
                  "type": "SEGMENT_CAMPAIGN",
                  "segment": "AT_RISK",
                  "action": "Win-back campaign cho 5 customers với 20% discount",
                  "ml_backing": "RFM analysis shows high monetary value, just need trigger",
                  "timeline": "Ngay lập tức",
                  "expected_outcome": "3-4 customers convert (65% rate)",
                  "risk_level": "low"
                }}
              ],
              
              "action_plan": {{
                "immediate_actions": [
                  "Launch win-back campaign cho AT_RISK segment",
                  "Prepare price increase vouchers"
                ],
                "this_week": [
                  "Implement price increase cho sản phẩm có elasticity thấp",
                  "Monitor conversion rates daily"
                ],
                "this_month": [
                  "Analyze promotion performance",
                  "Update ML models với actual results",
                  "Adjust pricing rules based on feedback"
                ]
              }},
              
              "kpis_to_track": [
                {{
                  "metric": "Revenue",
                  "baseline": "42.3M VND/month",
                  "target": "+8.3%",
                  "tracking_frequency": "Weekly",
                  "alert_threshold": "Nếu <+5% sau 2 tuần"
                }},
                {{
                  "metric": "AT_RISK conversion rate",
                  "baseline": "5 customers",
                  "target": "65% (3-4 customers)",
                  "tracking_frequency": "Daily",
                  "alert_threshold": "Nếu <50% sau 1 tuần"
                }}
              ],
              
              "risks_and_mitigation": [
                {{
                  "risk": "Tăng giá có thể ảnh hưởng NEW customers",
                  "probability": "medium",
                  "impact": "medium",
                  "mitigation": "Duy trì 14% welcome discount, monitor churn rate",
                  "fallback_plan": "Rollback price nếu churn >20%"
                }}
              ],
              
              "insights_and_opportunities": [
                "ML data cho thấy cơ hội X",
                "Segment Y đang underserved",
                "Elasticity thấp của product Z = cơ hội premium positioning"
              ]
            }}
            
            🔥 LƯU Ý QUAN TRỌNG:
            1. Tất cả recommendations PHẢI dựa trên ML data cụ thể
            2. Cite elasticity, segments, simulation results để back up mỗi action
            3. Đưa ra confidence level và expected outcomes với numbers
            4. Action plan phải specific, measurable, achievable
            5. Risks phải realistic với mitigation plans rõ ràng
            
            Hãy phân tích sâu và đưa ra insights actionable!
            """
            
            response = self.llm_model.generate_content(prompt)
            
            # Parse LLM response
            try:
                insights = json.loads(response.text)
                insights["data_sources"] = {
                    "price_elasticity": "included" if "error" not in comprehensive_data.get("price_elasticity", {}) else "error",
                    "customer_segments": "included" if "error" not in comprehensive_data.get("customer_segments", {}) else "error",
                    "personalized_pricing": "included" if "error" not in comprehensive_data.get("personalized_pricing", {}) else "error",
                    "simulations": "included" if "error" not in comprehensive_data.get("simulation_results", {}) else "error",
                    "promotions": "included" if "error" not in comprehensive_data.get("active_promotions", {}) else "error"
                }
            except json.JSONDecodeError:
                # If not valid JSON, create structured response
                insights = {
                    "raw_response": response.text,
                    "comprehensive_data": comprehensive_data,
                    "parsed_at": datetime.now().isoformat(),
                    "note": "LLM response was not valid JSON, raw text included"
                }
            
            logger.info("✅ Generated enhanced LLM insights with Week 1-6 data")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating enhanced LLM insights: {e}")
            return {
                "error": str(e),
                "fallback": "Enhanced insights generation failed, use legacy version"
            }
    
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
