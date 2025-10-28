"""
MongoDB Configuration cho AI Promotion System
"""
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MongoDBConfig:
    """Cấu hình MongoDB connection"""
    
    def __init__(self):
        # MongoDB connection string
        self.MONGODB_URL = os.getenv("MONGODB_URL")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME", "test")
        
        # Collections
        self.COLLECTIONS = {
            'orders': 'orders',
            'products': 'products', 
            'users': 'users',
            'ratings': 'ratings',
            'discounts': 'discounts',
            'categories': 'categories',
            'search_histories': 'search_histories',
            'pricing_factors': 'pricing_factors',
            'competitor_data': 'competitor_data',
            'trends_data': 'trends_data',
            'promotion_recommendations': 'promotion_recommendations',
            'ai_insights': 'ai_insights'
        }
    
    def get_sync_client(self) -> MongoClient:
        """Sync MongoDB client cho data processing"""
        try:
            client = MongoClient(self.MONGODB_URL)
            # Test connection
            client.admin.command('ping')
            logger.info("✅ MongoDB sync connection established")
            return client
        except Exception as e:
            logger.error(f"❌ MongoDB sync connection failed: {e}")
            raise
    
    def get_async_client(self) -> AsyncIOMotorClient:
        """Async MongoDB client cho FastAPI"""
        try:
            client = AsyncIOMotorClient(self.MONGODB_URL)
            logger.info("✅ MongoDB async connection established")
            return client
        except Exception as e:
            logger.error(f"❌ MongoDB async connection failed: {e}")
            raise
    
    def get_database(self, client=None, async_client=False):
        """Get database instance"""
        if async_client:
            if client is None:
                client = self.get_async_client()
            return client[self.DATABASE_NAME]
        else:
            if client is None:
                client = self.get_sync_client()
            return client[self.DATABASE_NAME]

# Global config instance
mongodb_config = MongoDBConfig()
