"""
Basic endpoints router
Root, health check, và system information
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
import logging

from infrastructure.db.mongodb_access import mongodb_data

logger = logging.getLogger(__name__)
router = APIRouter()

# Global services (will be injected from main.py)
promotion_service = None
hybrid_system = None

def set_global_services(promo_service, hybrid_sys):
    """Set global services from main.py"""
    global promotion_service, hybrid_system
    promotion_service = promo_service
    hybrid_system = hybrid_sys

@router.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AI Promotion System API v2.0",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "MongoDB Integration",
            "TensorFlow Recommenders",
            "HuggingFace Transformers", 
            "Dynamic Pricing Models",
            "Hybrid Recommendation System",
            "Gemini LLM Integration"
        ],
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Test MongoDB connection
        test_data = mongodb_data.get_products_data()
        
        # Check services
        services_status = {
            "mongodb": "connected",
            "promotion_service": "initialized" if promotion_service else "not_initialized",
            "hybrid_system": "initialized" if hybrid_system else "not_initialized",
            "gemini": "configured" if os.getenv("GEMINI_API_KEY") else "not_configured"
        }
        
        return {
            "status": "healthy",
            "services": services_status,
            "data_availability": {
                "products": len(test_data) if not test_data.empty else 0,
                "orders": len(mongodb_data.get_orders_data()) if not mongodb_data.get_orders_data().empty else 0
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


