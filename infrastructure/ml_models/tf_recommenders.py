"""
TensorFlow Recommenders Integration
Production-ready recommendation system cho bakery promotion
"""
# Optional: TensorFlow (heavy dependency, ~300MB)
try:
    import tensorflow as tf
    import tensorflow_recommenders as tfrs
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ TensorFlow not available (optional - large package ~300MB)")

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TensorFlowRecommenderSystem:
    """TensorFlow Recommenders cho bakery promotion system"""
    
    def __init__(self):
        self.user_model = None
        self.product_model = None
        self.task = None
        self.model = None
        self.is_trained = False
        
        logger.info("✅ TensorFlow Recommenders initialized")
    
    def prepare_data(self, orders_df: pd.DataFrame, products_df: pd.DataFrame, users_df: pd.DataFrame):
        """Chuẩn bị dữ liệu cho TF Recommenders"""
        try:
            # Merge data
            merged_data = []
            
            for _, order in orders_df.iterrows():
                user_id = order.get('userId', '')
                if not user_id:
                    continue
                
                # Extract products from order items
                for i in range(8):  # Max 8 items per order
                    product_col = f'orderItems[{i}].product'
                    quantity_col = f'orderItems[{i}].quantity'
                    
                    if product_col in orders_df.columns and pd.notna(order[product_col]):
                        product_id = order[product_col]
                        quantity = order.get(quantity_col, 1)
                        
                        # Get product info
                        product_info = products_df[products_df['_id'] == product_id]
                        if not product_info.empty:
                            product_name = product_info.iloc[0].get('productName', 'Unknown')
                            product_price = product_info.iloc[0].get('productPrice', 0)
                            
                            merged_data.append({
                                'user_id': user_id,
                                'product_id': product_id,
                                'product_name': product_name,
                                'product_price': product_price,
                                'quantity': quantity,
                                'rating': 5.0  # Default rating for purchased items
                            })
            
            if not merged_data:
                logger.warning("No valid data for TF Recommenders")
                return None
            
            # Create TensorFlow dataset
            df = pd.DataFrame(merged_data)
            
            # Convert to TensorFlow dataset
            dataset = tf.data.Dataset.from_tensor_slices({
                'user_id': df['user_id'].values,
                'product_id': df['product_id'].values,
                'product_name': df['product_name'].values,
                'product_price': df['product_price'].values,
                'quantity': df['quantity'].values,
                'rating': df['rating'].values
            })
            
            logger.info(f"✅ Prepared {len(df)} interactions for TF Recommenders")
            return dataset
            
        except Exception as e:
            logger.error(f"❌ Error preparing data for TF Recommenders: {e}")
            return None
    
    def build_model(self, dataset):
        """Build TF Recommenders model"""
        try:
            # Get unique users and products
            user_ids = set()
            product_ids = set()
            
            for example in dataset:
                user_ids.add(example['user_id'].numpy().decode('utf-8'))
                product_ids.add(example['product_id'].numpy().decode('utf-8'))
            
            # User model
            self.user_model = tf.keras.Sequential([
                tf.keras.layers.StringLookup(vocabulary=list(user_ids), mask_token=None),
                tf.keras.layers.Embedding(len(user_ids) + 1, 64)
            ])
            
            # Product model
            self.product_model = tf.keras.Sequential([
                tf.keras.layers.StringLookup(vocabulary=list(product_ids), mask_token=None),
                tf.keras.layers.Embedding(len(product_ids) + 1, 64)
            ])
            
            # Task
            self.task = tfrs.tasks.Retrieval(
                metrics=tfrs.metrics.FactorizedTopK(
                    candidates=dataset.batch(128).map(self.product_model)
                )
            )
            
            # Full model
            self.model = BakeryRecommenderModel(self.user_model, self.product_model, self.task)
            
            logger.info("✅ TF Recommenders model built successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error building TF Recommenders model: {e}")
            return False
    
    def train_model(self, dataset, epochs=3):
        """Train TF Recommenders model"""
        try:
            if not self.model:
                logger.error("Model not built yet")
                return False
            
            # Compile model
            self.model.compile(optimizer=tf.keras.optimizers.Adagrad(0.5))
            
            # Train
            self.model.fit(dataset.batch(4096), epochs=epochs)
            
            self.is_trained = True
            logger.info(f"✅ TF Recommenders model trained for {epochs} epochs")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error training TF Recommenders model: {e}")
            return False
    
    def get_recommendations(self, user_id: str, top_k: int = 5) -> List[Dict]:
        """Get recommendations for a user"""
        try:
            if not self.is_trained:
                logger.error("Model not trained yet")
                return []
            
            # Create user tensor
            user_tensor = tf.constant([user_id])
            
            # Get user embedding
            user_embedding = self.user_model(user_tensor)
            
            # Get all product embeddings
            all_products = list(self.product_model.get_layer('string_lookup').get_vocabulary())
            product_tensors = tf.constant(all_products)
            product_embeddings = self.product_model(product_tensors)
            
            # Compute similarities
            similarities = tf.matmul(user_embedding, product_embeddings, transpose_b=True)
            
            # Get top-k recommendations
            top_indices = tf.nn.top_k(similarities, k=top_k).indices.numpy()[0]
            
            recommendations = []
            for idx in top_indices:
                product_id = all_products[idx]
                score = similarities[0][idx].numpy()
                
                recommendations.append({
                    'product_id': product_id,
                    'score': float(score),
                    'recommendation_type': 'collaborative_filtering'
                })
            
            logger.info(f"✅ Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {e}")
            return []
    
    def get_similar_products(self, product_id: str, top_k: int = 5) -> List[Dict]:
        """Get similar products based on embeddings"""
        try:
            if not self.is_trained:
                logger.error("Model not trained yet")
                return []
            
            # Get product embedding
            product_tensor = tf.constant([product_id])
            product_embedding = self.product_model(product_tensor)
            
            # Get all product embeddings
            all_products = list(self.product_model.get_layer('string_lookup').get_vocabulary())
            product_tensors = tf.constant(all_products)
            product_embeddings = self.product_model(product_tensors)
            
            # Compute similarities
            similarities = tf.matmul(product_embedding, product_embeddings, transpose_b=True)
            
            # Get top-k similar products
            top_indices = tf.nn.top_k(similarities, k=top_k+1).indices.numpy()[0]
            
            similar_products = []
            for idx in top_indices:
                similar_product_id = all_products[idx]
                if similar_product_id != product_id:  # Exclude the product itself
                    score = similarities[0][idx].numpy()
                    
                    similar_products.append({
                        'product_id': similar_product_id,
                        'similarity_score': float(score),
                        'recommendation_type': 'item_based'
                    })
            
            logger.info(f"✅ Found {len(similar_products)} similar products for {product_id}")
            return similar_products
            
        except Exception as e:
            logger.error(f"❌ Error getting similar products: {e}")
            return []

# Only define TF-specific classes if TensorFlow is available
if TF_AVAILABLE:
    class BakeryRecommenderModel(tfrs.Model):
        """Custom TF Recommenders model for bakery recommendations"""
        
        def __init__(self, user_model, product_model, task):
            super().__init__()
            self.user_model = user_model
            self.product_model = product_model
            self.task = task
        
        def compute_loss(self, features, training=False):
            user_embeddings = self.user_model(features['user_id'])
            product_embeddings = self.product_model(features['product_id'])
            
            return self.task(user_embeddings, product_embeddings)

# Factory function
def create_tf_recommender():
    """Create TF Recommenders instance"""
    if not TF_AVAILABLE:
        logger.warning("⚠️ TensorFlow not available - returning stub recommender")
        return StubTensorFlowRecommender()
    return TensorFlowRecommenderSystem()

class StubTensorFlowRecommender:
    """Stub class when TensorFlow is not available"""
    
    def __init__(self):
        self.is_trained = False
        self.user_model = None
        self.product_model = None
        self.task = None
        self.model = None
        logger.info("⚠️ Using stub TF Recommender (TensorFlow not installed)")
    
    def prepare_data(self, orders_df: pd.DataFrame, products_df: pd.DataFrame, users_df: pd.DataFrame):
        """No-op prepare_data method"""
        logger.warning("TensorFlow not available - skipping data preparation")
        return None
    
    def build_model(self, dataset):
        """No-op build_model method"""
        logger.warning("TensorFlow not available - skipping model building")
        return False
    
    def train_model(self, dataset, epochs=3):
        """No-op train_model method"""
        logger.warning("TensorFlow not available - skipping model training")
        return False
    
    def get_recommendations(self, user_id: str, top_k: int = 10) -> List[Dict]:
        """Return empty recommendations"""
        logger.warning("TensorFlow not available - no collaborative filtering recommendations")
        return []
    
    def get_similar_products(self, product_id: str, top_k: int = 5) -> List[Dict]:
        """Return empty similar products"""
        logger.warning("TensorFlow not available - no similar products")
        return []
    
    def train(self, *args, **kwargs):
        """No-op train method"""
        logger.warning("TensorFlow not available - skipping training")
        return False

