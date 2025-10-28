"""
Data Access Layer cho MongoDB
Tích hợp trực tiếp với MongoDB thay vì CSV files
"""
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from configs.database import mongodb_config
from utils.numpy_serializer import convert_numpy_types

logger = logging.getLogger(__name__)

class MongoDBDataAccess:
    """Data Access Layer cho MongoDB collections"""
    
    def __init__(self, use_async: bool = False):
        """
        Initialize MongoDB access
        
        Args:
            use_async: If True, use async client. Default False for backward compatibility.
        """
        self.config = mongodb_config
        self.use_async = use_async
        
        if use_async:
            self.client = self.config.get_async_client()
            self.db = self.config.get_database(async_client=True)
        else:
            self.client = self.config.get_sync_client()
            self.db = self.config.get_database(self.client)
    
    def get_collection(self, collection_name: str):
        """
        Get MongoDB collection by name
        
        Args:
            collection_name: Name of collection ('orders', 'products', 'users', etc.)
            
        Returns:
            MongoDB collection object (sync or async depending on init)
        """
        return self.db[self.config.COLLECTIONS.get(collection_name, collection_name)]
    
    def get_orders_data(self, 
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       limit: Optional[int] = None) -> pd.DataFrame:
        """Lấy dữ liệu orders từ MongoDB"""
        try:
            collection = self.db[self.config.COLLECTIONS['orders']]
            
            # Build query
            query = {}
            if start_date and end_date:
                query['createdAt'] = {'$gte': start_date, '$lte': end_date}
            
            # Get data
            cursor = collection.find(query)
            if limit:
                cursor = cursor.limit(limit)
            
            # Convert to list and clean ObjectId
            orders_data = list(cursor)
            if not orders_data:
                # Check if it's due to date filter
                if start_date and end_date:
                    logger.warning(f"No orders found between {start_date.date()} and {end_date.date()}")
                    # Get actual date range from all orders
                    all_orders = list(collection.find({}, {'createdAt': 1}).limit(1000))
                    if all_orders:
                        dates = [o.get('createdAt') for o in all_orders if o.get('createdAt')]
                        if dates:
                            min_date = min(dates)
                            max_date = max(dates)
                            logger.info(f"💡 Available date range: {min_date.date()} to {max_date.date()}")
                else:
                    logger.warning("No orders data found in database")
                return pd.DataFrame()
            
            # Convert all ObjectId to string BEFORE creating DataFrame
            orders_data = convert_numpy_types(orders_data)
            
            df = pd.DataFrame(orders_data)
            
            logger.info(f"✅ Retrieved {len(df)} orders from MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error getting orders data: {e}")
            return pd.DataFrame()
    
    def get_products_data(self) -> pd.DataFrame:
        """Lấy dữ liệu products từ MongoDB"""
        try:
            collection = self.db[self.config.COLLECTIONS['products']]
            products_data = list(collection.find())
            
            if not products_data:
                logger.warning("No products data found")
                return pd.DataFrame()
            
            # Convert all ObjectId to string BEFORE creating DataFrame
            products_data = convert_numpy_types(products_data)
            
            df = pd.DataFrame(products_data)
            
            logger.info(f"✅ Retrieved {len(df)} products from MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error getting products data: {e}")
            return pd.DataFrame()
    
    def get_users_data(self) -> pd.DataFrame:
        """Lấy dữ liệu users từ MongoDB"""
        try:
            collection = self.db[self.config.COLLECTIONS['users']]
            users_data = list(collection.find())
            
            if not users_data:
                logger.warning("No users data found")
                return pd.DataFrame()
            
            # Convert all ObjectId to string BEFORE creating DataFrame
            users_data = convert_numpy_types(users_data)
            
            df = pd.DataFrame(users_data)
            
            logger.info(f"✅ Retrieved {len(df)} users from MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error getting users data: {e}")
            return pd.DataFrame()
    
    def get_ratings_data(self) -> pd.DataFrame:
        """Lấy dữ liệu ratings từ MongoDB"""
        try:
            collection = self.db[self.config.COLLECTIONS['ratings']]
            ratings_data = list(collection.find())
            
            if not ratings_data:
                logger.warning("No ratings data found")
                return pd.DataFrame()
            
            # Convert all ObjectId to string BEFORE creating DataFrame
            ratings_data = convert_numpy_types(ratings_data)
            
            df = pd.DataFrame(ratings_data)
            
            logger.info(f"✅ Retrieved {len(df)} ratings from MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error getting ratings data: {e}")
            return pd.DataFrame()
    
    def get_discounts_data(self) -> pd.DataFrame:
        """Lấy dữ liệu discounts từ MongoDB"""
        try:
            collection = self.db[self.config.COLLECTIONS['discounts']]
            discounts_data = list(collection.find())
            
            if not discounts_data:
                logger.warning("No discounts data found")
                return pd.DataFrame()
            
            # Convert all ObjectId to string BEFORE creating DataFrame
            discounts_data = convert_numpy_types(discounts_data)
            
            df = pd.DataFrame(discounts_data)
            
            logger.info(f"✅ Retrieved {len(df)} discounts from MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error getting discounts data: {e}")
            return pd.DataFrame()
    
    def get_search_histories_data(self) -> pd.DataFrame:
        """Lấy dữ liệu search histories từ MongoDB"""
        try:
            collection = self.db[self.config.COLLECTIONS['search_histories']]
            search_data = list(collection.find())
            
            if not search_data:
                logger.warning("No search histories data found")
                return pd.DataFrame()
            
            # Convert all ObjectId to string BEFORE creating DataFrame
            search_data = convert_numpy_types(search_data)
            
            df = pd.DataFrame(search_data)
            
            logger.info(f"✅ Retrieved {len(df)} search histories from MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error getting search histories data: {e}")
            return pd.DataFrame()
    
    def get_all_business_data(self) -> Dict[str, pd.DataFrame]:
        """Lấy tất cả dữ liệu business từ MongoDB"""
        try:
            data = {
                'orders': self.get_orders_data(),
                'products': self.get_products_data(),
                'users': self.get_users_data(),
                'ratings': self.get_ratings_data(),
                'discounts': self.get_discounts_data(),
                'search_histories': self.get_search_histories_data()
            }
            
            logger.info("✅ Retrieved all business data from MongoDB")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error getting all business data: {e}")
            return {}
    
    def save_ai_insights(self, insights: Dict[str, Any]) -> bool:
        """Lưu AI insights vào MongoDB"""
        try:
            collection = self.db[self.config.COLLECTIONS['ai_insights']]
            
            # Convert numpy types to Python native types for MongoDB
            insights = convert_numpy_types(insights)
            
            # Add metadata
            insights['created_at'] = datetime.now()
            insights['version'] = '1.0'
            
            # Insert document
            result = collection.insert_one(insights)
            
            if result.inserted_id:
                logger.info(f"✅ Saved AI insights with ID: {result.inserted_id}")
                return True
            else:
                logger.error("❌ Failed to save AI insights")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error saving AI insights: {e}")
            return False
    
    def save_promotion_recommendations(self, recommendations: Dict[str, Any]) -> bool:
        """Lưu promotion recommendations vào MongoDB"""
        try:
            collection = self.db[self.config.COLLECTIONS['promotion_recommendations']]
            
            # Add metadata
            recommendations['created_at'] = datetime.now()
            recommendations['status'] = 'pending'
            
            # Insert document
            result = collection.insert_one(recommendations)
            
            if result.inserted_id:
                logger.info(f"✅ Saved promotion recommendations with ID: {result.inserted_id}")
                return True
            else:
                logger.error("❌ Failed to save promotion recommendations")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error saving promotion recommendations: {e}")
            return False
    
    def get_recent_ai_insights(self, limit: int = 10) -> List[Dict]:
        """Lấy AI insights gần nhất"""
        try:
            collection = self.db[self.config.COLLECTIONS['ai_insights']]
            
            # Get recent insights
            insights = list(collection.find().sort('created_at', -1).limit(limit))
            
            # Convert ObjectId to string
            for insight in insights:
                if '_id' in insight:
                    insight['_id'] = str(insight['_id'])
            
            logger.info(f"✅ Retrieved {len(insights)} recent AI insights")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting recent AI insights: {e}")
            return []
    
    def close_connection(self):
        """Đóng MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("✅ MongoDB connection closed")


# Alias for backward compatibility
MongoDBAccess = MongoDBDataAccess

# Global data access instance
mongodb_data = MongoDBDataAccess()
