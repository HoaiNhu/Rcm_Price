"""
Hugging Face Transformers Integration
Content-based filtering cho bakery products
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# Try to import transformers and torch - make them optional
try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    from sklearn.metrics.pairwise import cosine_similarity
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    logger.warning(f"⚠️ Transformers not available: {e}")

class HuggingFaceContentFilter:
    """Hugging Face Transformers cho content-based filtering"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.product_embeddings = {}
        self.is_loaded = False
        self.transformers_available = TRANSFORMERS_AVAILABLE
        
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("⚠️ Transformers not available - HuggingFace features disabled")
        else:
            logger.info(f"✅ HuggingFace Content Filter initialized with {model_name}")
    
    def load_model(self):
        """Load pre-trained transformer model"""
        try:
            if not TRANSFORMERS_AVAILABLE:
                logger.warning("⚠️ Transformers not available - cannot load model")
                return False
                
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # Set to evaluation mode
            self.model.eval()
            
            self.is_loaded = True
            logger.info("✅ HuggingFace model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading HuggingFace model: {e}")
            return False
    
    def create_product_embeddings(self, products_df: pd.DataFrame):
        """Tạo embeddings cho tất cả sản phẩm"""
        try:
            if not self.is_loaded:
                logger.error("Model not loaded yet")
                return False
            
            self.product_embeddings = {}
            
            for _, product in products_df.iterrows():
                product_id = product['_id']
                product_name = product.get('productName', '')
                product_description = product.get('productDescription', '')
                product_category = product.get('productCategory', '')
                
                # Combine text information
                text_content = f"{product_name} {product_description} {product_category}"
                
                # Create embedding
                embedding = self._get_text_embedding(text_content)
                
                if embedding is not None:
                    self.product_embeddings[product_id] = {
                        'embedding': embedding,
                        'name': product_name,
                        'description': product_description,
                        'category': product_category,
                        'price': product.get('productPrice', 0)
                    }
            
            logger.info(f"✅ Created embeddings for {len(self.product_embeddings)} products")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating product embeddings: {e}")
            return False
    
    def _get_text_embedding(self, text: str) -> Optional[np.ndarray]:
        """Tạo embedding cho text"""
        try:
            if not self.is_loaded:
                return None
            
            # Tokenize
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            return embeddings.numpy().flatten()
            
        except Exception as e:
            logger.error(f"❌ Error creating text embedding: {e}")
            return None
    
    def find_similar_products(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """Tìm sản phẩm tương tự dựa trên text query"""
        try:
            if not self.is_loaded or not self.product_embeddings:
                logger.error("Model or embeddings not ready")
                return []
            
            # Create query embedding
            query_embedding = self._get_text_embedding(query_text)
            if query_embedding is None:
                return []
            
            # Calculate similarities
            similarities = []
            for product_id, product_data in self.product_embeddings.items():
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    product_data['embedding'].reshape(1, -1)
                )[0][0]
                
                similarities.append({
                    'product_id': product_id,
                    'name': product_data['name'],
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'similarity_score': float(similarity),
                    'recommendation_type': 'content_based'
                })
            
            # Sort by similarity and return top-k
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"✅ Found {min(top_k, len(similarities))} similar products for query: {query_text}")
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error finding similar products: {e}")
            return []
    
    def get_product_recommendations(self, product_id: str, top_k: int = 5) -> List[Dict]:
        """Gợi ý sản phẩm tương tự cho một sản phẩm cụ thể"""
        try:
            if not self.is_loaded or not self.product_embeddings:
                logger.error("Model or embeddings not ready")
                return []
            
            if product_id not in self.product_embeddings:
                logger.warning(f"Product {product_id} not found in embeddings")
                return []
            
            product_embedding = self.product_embeddings[product_id]['embedding']
            
            # Calculate similarities with other products
            similarities = []
            for other_product_id, other_product_data in self.product_embeddings.items():
                if other_product_id != product_id:
                    similarity = cosine_similarity(
                        product_embedding.reshape(1, -1),
                        other_product_data['embedding'].reshape(1, -1)
                    )[0][0]
                    
                    similarities.append({
                        'product_id': other_product_id,
                        'name': other_product_data['name'],
                        'description': other_product_data['description'],
                        'price': other_product_data['price'],
                        'similarity_score': float(similarity),
                        'recommendation_type': 'content_based'
                    })
            
            # Sort by similarity and return top-k
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"✅ Generated {min(top_k, len(similarities))} recommendations for product {product_id}")
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error getting product recommendations: {e}")
            return []
    
    def analyze_search_intent(self, search_histories_df: pd.DataFrame) -> Dict[str, Any]:
        """Phân tích search intent từ lịch sử tìm kiếm"""
        try:
            if not self.is_loaded:
                logger.error("Model not loaded yet")
                return {}
            
            # Group searches by user
            user_searches = {}
            for _, search in search_histories_df.iterrows():
                user_id = search.get('userId', '')
                query = search.get('query', '')
                
                if user_id not in user_searches:
                    user_searches[user_id] = []
                user_searches[user_id].append(query)
            
            # Analyze search patterns
            search_analysis = {}
            for user_id, queries in user_searches.items():
                # Combine all queries for this user
                combined_query = ' '.join(queries)
                
                # Find matching products
                recommendations = self.find_similar_products(combined_query, top_k=3)
                
                search_analysis[user_id] = {
                    'queries': queries,
                    'combined_intent': combined_query,
                    'recommended_products': recommendations,
                    'search_count': len(queries)
                }
            
            logger.info(f"✅ Analyzed search intent for {len(user_searches)} users")
            return search_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing search intent: {e}")
            return {}
    
    def get_seasonal_recommendations(self, season: str, products_df: pd.DataFrame) -> List[Dict]:
        """Gợi ý sản phẩm theo mùa"""
        try:
            if not self.is_loaded:
                logger.error("Model not loaded yet")
                return []
            
            # Define seasonal keywords
            seasonal_keywords = {
                'spring': 'bánh hoa xuân mùa xuân tươi mát',
                'summer': 'bánh mùa hè mát lạnh trái cây',
                'autumn': 'bánh mùa thu ấm áp',
                'winter': 'bánh mùa đông ấm áp giáng sinh',
                'valentine': 'bánh tình yêu valentine lãng mạn',
                'birthday': 'bánh sinh nhật party',
                'wedding': 'bánh cưới wedding elegant'
            }
            
            if season.lower() not in seasonal_keywords:
                logger.warning(f"Unknown season: {season}")
                return []
            
            query = seasonal_keywords[season.lower()]
            recommendations = self.find_similar_products(query, top_k=10)
            
            logger.info(f"✅ Generated {len(recommendations)} seasonal recommendations for {season}")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting seasonal recommendations: {e}")
            return []
    
    def get_price_based_recommendations(self, target_price_range: Tuple[float, float], 
                                      products_df: pd.DataFrame) -> List[Dict]:
        """Gợi ý sản phẩm theo khoảng giá"""
        try:
            if not self.is_loaded or not self.product_embeddings:
                logger.error("Model or embeddings not ready")
                return []
            
            min_price, max_price = target_price_range
            
            # Filter products by price range
            price_filtered_products = []
            for product_id, product_data in self.product_embeddings.items():
                price = product_data['price']
                if min_price <= price <= max_price:
                    price_filtered_products.append({
                        'product_id': product_id,
                        'name': product_data['name'],
                        'description': product_data['description'],
                        'price': price,
                        'embedding': product_data['embedding']
                    })
            
            if not price_filtered_products:
                logger.warning(f"No products found in price range {target_price_range}")
                return []
            
            # Calculate average embedding for price range
            avg_embedding = np.mean([p['embedding'] for p in price_filtered_products], axis=0)
            
            # Find most representative products
            similarities = []
            for product in price_filtered_products:
                similarity = cosine_similarity(
                    avg_embedding.reshape(1, -1),
                    product['embedding'].reshape(1, -1)
                )[0][0]
                
                similarities.append({
                    'product_id': product['product_id'],
                    'name': product['name'],
                    'description': product['description'],
                    'price': product['price'],
                    'similarity_score': float(similarity),
                    'recommendation_type': 'price_based'
                })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"✅ Generated {len(similarities)} price-based recommendations")
            return similarities
            
        except Exception as e:
            logger.error(f"❌ Error getting price-based recommendations: {e}")
            return []

# Factory function
def create_hf_content_filter(model_name: str = 'sentence-transformers/all-MiniLM-L6-v2') -> HuggingFaceContentFilter:
    """Create HuggingFace Content Filter instance"""
    return HuggingFaceContentFilter(model_name)
