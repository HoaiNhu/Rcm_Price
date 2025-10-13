"""
Hybrid Recommendation System
Tích hợp tất cả các models: TF Recommenders, HuggingFace, Dynamic Pricing
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import json

from infrastructure.ml_models.tf_recommenders import create_tf_recommender
from infrastructure.ml_models.huggingface_filter import create_hf_content_filter
from infrastructure.ml_models.dynamic_pricing import create_dynamic_pricing_model
from infrastructure.db.mongodb_access import mongodb_data
from utils.numpy_serializer import convert_numpy_types

logger = logging.getLogger(__name__)

class HybridRecommendationSystem:
    """Hybrid Recommendation System kết hợp tất cả models"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.data_access = mongodb_data
        
        # Initialize all models
        self.tf_recommender = create_tf_recommender()
        self.hf_filter = create_hf_content_filter()
        self.pricing_model = create_dynamic_pricing_model()
        
        # Model weights for ensemble
        self.model_weights = {
            'collaborative_filtering': 0.4,
            'content_based': 0.3,
            'dynamic_pricing': 0.3
        }
        
        self.is_initialized = False
        
        logger.info("✅ Hybrid Recommendation System initialized")
    
    def initialize_system(self) -> bool:
        """Initialize all models with data"""
        try:
            # Get data from MongoDB
            orders_df = self.data_access.get_orders_data()
            products_df = self.data_access.get_products_data()
            users_df = self.data_access.get_users_data()
            ratings_df = self.data_access.get_ratings_data()
            search_histories_df = self.data_access.get_search_histories_data()
            
            if orders_df.empty or products_df.empty:
                logger.error("Insufficient data for initialization")
                return False
            
            # Initialize TF Recommenders
            try:
                tf_dataset = self.tf_recommender.prepare_data(orders_df, products_df, users_df)
                if tf_dataset:
                    self.tf_recommender.build_model(tf_dataset)
                    self.tf_recommender.train_model(tf_dataset, epochs=3)
                else:
                    logger.warning("TF Recommenders dataset is None - skipping TF initialization")
            except Exception as e:
                logger.warning(f"TF Recommenders initialization failed: {e} - continuing with other models")
            
            # Initialize HuggingFace Content Filter
            self.hf_filter.load_model()
            self.hf_filter.create_product_embeddings(products_df)
            
            # Initialize Dynamic Pricing Model
            pricing_df = self.pricing_model.prepare_pricing_data(orders_df, products_df)
            if not pricing_df.empty:
                self.pricing_model.train_models(pricing_df)
            
            self.is_initialized = True
            logger.info("✅ Hybrid Recommendation System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing hybrid system: {e}")
            return False
    
    def get_user_recommendations(self, user_id: str, top_k: int = 10) -> Dict[str, Any]:
        """Get comprehensive recommendations for a user"""
        try:
            if not self.is_initialized:
                logger.error("System not initialized")
                return {}
            
            # Get collaborative filtering recommendations
            cf_recommendations = self.tf_recommender.get_recommendations(user_id, top_k)
            
            # Get user's search history for content-based recommendations
            search_histories_df = self.data_access.get_search_histories_data()
            user_searches = search_histories_df[search_histories_df['userId'] == user_id]['query'].tolist()
            
            content_recommendations = []
            if user_searches:
                combined_query = ' '.join(user_searches)
                content_recommendations = self.hf_filter.find_similar_products(combined_query, top_k)
            
            # Get user's order history for pricing recommendations
            orders_df = self.data_access.get_orders_data()
            user_orders = orders_df[orders_df['userId'] == user_id]
            
            pricing_recommendations = []
            if not user_orders.empty:
                # Get products user has ordered
                ordered_products = user_orders['orderItems[0].product'].dropna().unique()
                
                for product_id in ordered_products[:3]:  # Limit to 3 products
                    products_df = self.data_access.get_products_data()
                    product_info = products_df[products_df['_id'] == product_id]
                    
                    if not product_info.empty:
                        current_price = product_info.iloc[0].get('productPrice', 0)
                        if current_price > 0:
                            pricing_df = self.pricing_model.prepare_pricing_data(orders_df, products_df)
                            optimization = self.pricing_model.optimize_price(
                                product_id, current_price, datetime.now(), pricing_df
                            )
                            
                            if optimization:
                                pricing_recommendations.append({
                                    'product_id': product_id,
                                    'product_name': product_info.iloc[0].get('productName', ''),
                                    'current_price': current_price,
                                    'optimal_price': optimization['optimal_price'],
                                    'price_change_percentage': optimization['price_change_percentage'],
                                    'recommendation': optimization['recommendation'],
                                    'recommendation_type': 'dynamic_pricing'
                                })
            
            # Combine all recommendations
            combined_recommendations = self._combine_recommendations(
                cf_recommendations, content_recommendations, pricing_recommendations
            )
            
            result = {
                'user_id': user_id,
                'collaborative_filtering': cf_recommendations,
                'content_based': content_recommendations,
                'pricing_optimization': pricing_recommendations,
                'combined_recommendations': combined_recommendations,
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Generated comprehensive recommendations for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting user recommendations: {e}")
            return {}
    
    def get_product_recommendations(self, product_id: str, top_k: int = 10) -> Dict[str, Any]:
        """Get comprehensive recommendations for a product"""
        try:
            if not self.is_initialized:
                logger.error("System not initialized")
                return {}
            
            # Get similar products from content-based filtering
            content_recommendations = self.hf_filter.get_product_recommendations(product_id, top_k)
            
            # Get similar products from collaborative filtering
            cf_recommendations = self.tf_recommender.get_similar_products(product_id, top_k)
            
            # Get pricing optimization
            products_df = self.data_access.get_products_data()
            product_info = products_df[products_df['_id'] == product_id]
            
            pricing_optimization = {}
            if not product_info.empty:
                current_price = product_info.iloc[0].get('productPrice', 0)
                if current_price > 0:
                    orders_df = self.data_access.get_orders_data()
                    pricing_df = self.pricing_model.prepare_pricing_data(orders_df, products_df)
                    pricing_optimization = self.pricing_model.optimize_price(
                        product_id, current_price, datetime.now(), pricing_df
                    )
            
            # Combine recommendations
            combined_recommendations = self._combine_product_recommendations(
                content_recommendations, cf_recommendations
            )
            
            result = {
                'product_id': product_id,
                'product_name': product_info.iloc[0].get('productName', '') if not product_info.empty else '',
                'content_based': content_recommendations,
                'collaborative_filtering': cf_recommendations,
                'pricing_optimization': pricing_optimization,
                'combined_recommendations': combined_recommendations,
                'generated_at': datetime.now().isoformat()
            }
            
            # Convert numpy types to Python native types for JSON serialization
            result = convert_numpy_types(result)
            
            logger.info(f"✅ Generated comprehensive recommendations for product {product_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting product recommendations: {e}")
            return {}
    
    def get_promotion_strategy(self) -> Dict[str, Any]:
        """Get comprehensive promotion strategy"""
        try:
            if not self.is_initialized:
                logger.error("System not initialized")
                return {}
            
            # Get data
            orders_df = self.data_access.get_orders_data()
            products_df = self.data_access.get_products_data()
            
            # Get pricing strategy
            pricing_df = self.pricing_model.prepare_pricing_data(orders_df, products_df)
            pricing_strategy = self.pricing_model.get_promotion_strategy(products_df, pricing_df)
            
            # Get seasonal recommendations
            current_month = datetime.now().month
            season = self._get_current_season(current_month)
            seasonal_recommendations = self.hf_filter.get_seasonal_recommendations(season, products_df)
            
            # Get combo recommendations
            combo_recommendations = self._get_combo_recommendations(orders_df, products_df)
            
            # Get search-based recommendations
            search_histories_df = self.data_access.get_search_histories_data()
            search_analysis = self.hf_filter.analyze_search_intent(search_histories_df)
            
            result = {
                'pricing_strategy': pricing_strategy,
                'seasonal_recommendations': seasonal_recommendations,
                'combo_recommendations': combo_recommendations,
                'search_analysis': search_analysis,
                'current_season': season,
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info("✅ Generated comprehensive promotion strategy")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating promotion strategy: {e}")
            return {}
    
    def _combine_recommendations(self, cf_recs: List[Dict], content_recs: List[Dict], 
                               pricing_recs: List[Dict]) -> List[Dict]:
        """Combine recommendations from different models"""
        try:
            combined = {}
            
            # Add collaborative filtering recommendations
            for rec in cf_recs:
                product_id = rec['product_id']
                if product_id not in combined:
                    combined[product_id] = {
                        'product_id': product_id,
                        'collaborative_score': 0,
                        'content_score': 0,
                        'pricing_score': 0,
                        'combined_score': 0
                    }
                combined[product_id]['collaborative_score'] = rec.get('score', 0)
            
            # Add content-based recommendations
            for rec in content_recs:
                product_id = rec['product_id']
                if product_id not in combined:
                    combined[product_id] = {
                        'product_id': product_id,
                        'collaborative_score': 0,
                        'content_score': 0,
                        'pricing_score': 0,
                        'combined_score': 0
                    }
                combined[product_id]['content_score'] = rec.get('similarity_score', 0)
            
            # Add pricing recommendations
            for rec in pricing_recs:
                product_id = rec['product_id']
                if product_id not in combined:
                    combined[product_id] = {
                        'product_id': product_id,
                        'collaborative_score': 0,
                        'content_score': 0,
                        'pricing_score': 0,
                        'combined_score': 0
                    }
                # Use price change percentage as pricing score
                price_change = abs(rec.get('price_change_percentage', 0))
                combined[product_id]['pricing_score'] = min(price_change / 20, 1.0)  # Normalize to 0-1
            
            # Calculate combined scores
            for product_id, scores in combined.items():
                combined_score = (
                    scores['collaborative_score'] * self.model_weights['collaborative_filtering'] +
                    scores['content_score'] * self.model_weights['content_based'] +
                    scores['pricing_score'] * self.model_weights['dynamic_pricing']
                )
                scores['combined_score'] = combined_score
            
            # Sort by combined score
            sorted_recommendations = sorted(
                combined.values(), 
                key=lambda x: x['combined_score'], 
                reverse=True
            )
            
            return sorted_recommendations
            
        except Exception as e:
            logger.error(f"❌ Error combining recommendations: {e}")
            return []
    
    def _combine_product_recommendations(self, content_recs: List[Dict], 
                                       cf_recs: List[Dict]) -> List[Dict]:
        """Combine product recommendations"""
        try:
            combined = {}
            
            # Add content-based recommendations
            for rec in content_recs:
                product_id = rec['product_id']
                if product_id not in combined:
                    combined[product_id] = {
                        'product_id': product_id,
                        'content_score': 0,
                        'collaborative_score': 0,
                        'combined_score': 0
                    }
                combined[product_id]['content_score'] = rec.get('similarity_score', 0)
            
            # Add collaborative filtering recommendations
            for rec in cf_recs:
                product_id = rec['product_id']
                if product_id not in combined:
                    combined[product_id] = {
                        'product_id': product_id,
                        'content_score': 0,
                        'collaborative_score': 0,
                        'combined_score': 0
                    }
                combined[product_id]['collaborative_score'] = rec.get('similarity_score', 0)
            
            # Calculate combined scores
            for product_id, scores in combined.items():
                combined_score = (
                    scores['content_score'] * 0.6 +
                    scores['collaborative_score'] * 0.4
                )
                scores['combined_score'] = combined_score
            
            # Sort by combined score
            sorted_recommendations = sorted(
                combined.values(), 
                key=lambda x: x['combined_score'], 
                reverse=True
            )
            
            return sorted_recommendations
            
        except Exception as e:
            logger.error(f"❌ Error combining product recommendations: {e}")
            return []
    
    def _get_combo_recommendations(self, orders_df: pd.DataFrame, 
                                 products_df: pd.DataFrame) -> List[Dict]:
        """Get combo recommendations using market basket analysis"""
        try:
            # Use existing combo discovery logic
            from application.services.ai_promotion_service import AIPromotionService
            temp_service = AIPromotionService(self.gemini_api_key)
            combo_result = temp_service.discover_product_combos()
            
            # Format combo recommendations
            combo_recommendations = []
            for combo in combo_result.get('combos', []):
                antecedents = list(combo['antecedents'])
                consequents = list(combo['consequents'])
                
                # Get product names
                antecedent_names = []
                consequent_names = []
                
                for product_id in antecedents:
                    product_info = products_df[products_df['_id'] == product_id]
                    if not product_info.empty:
                        antecedent_names.append(product_info.iloc[0].get('productName', ''))
                
                for product_id in consequents:
                    product_info = products_df[products_df['_id'] == product_id]
                    if not product_info.empty:
                        consequent_names.append(product_info.iloc[0].get('productName', ''))
                
                combo_recommendations.append({
                    'antecedents': antecedents,
                    'consequents': consequents,
                    'antecedent_names': antecedent_names,
                    'consequent_names': consequent_names,
                    'support': combo['support'],
                    'confidence': combo['confidence'],
                    'lift': combo['lift']
                })
            
            return combo_recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting combo recommendations: {e}")
            return []
    
    def _get_current_season(self, month: int) -> str:
        """Get current season based on month"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def generate_complete_ai_strategy(self) -> Dict[str, Any]:
        """Generate complete AI strategy using all models"""
        try:
            if not self.is_initialized:
                if not self.initialize_system():
                    return {"error": "Failed to initialize system"}
            
            # Get comprehensive promotion strategy
            promotion_strategy = self.get_promotion_strategy()
            
            # Get top products for recommendations
            products_df = self.data_access.get_products_data()
            top_products = products_df.head(5)['_id'].tolist()
            
            # Get recommendations for top products
            product_recommendations = {}
            for product_id in top_products:
                product_recs = self.get_product_recommendations(product_id, top_k=3)
                product_recommendations[product_id] = product_recs
            
            # Combine everything
            complete_strategy = {
                'promotion_strategy': promotion_strategy,
                'product_recommendations': product_recommendations,
                'model_performance': {
                    'tf_recommenders': self.tf_recommender.is_trained,
                    'huggingface_filter': self.hf_filter.is_loaded,
                    'dynamic_pricing': self.pricing_model.is_trained
                },
                'generated_at': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            # Save to MongoDB
            self.data_access.save_ai_insights(complete_strategy)
            
            logger.info("✅ Complete AI strategy generated successfully")
            return complete_strategy
            
        except Exception as e:
            logger.error(f"❌ Error generating complete AI strategy: {e}")
            return {"error": str(e)}

# Factory function
def create_hybrid_recommender(gemini_api_key: str) -> HybridRecommendationSystem:
    """Create Hybrid Recommendation System instance"""
    return HybridRecommendationSystem(gemini_api_key)
