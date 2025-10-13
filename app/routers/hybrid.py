"""
Hybrid Recommendation System endpoints router
Tích hợp tất cả các models: TF Recommenders, HuggingFace, Dynamic Pricing
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Global services (will be injected from main.py)
hybrid_system = None

def set_global_services(hybrid_sys):
    """Set global services from main.py"""
    global hybrid_system
    hybrid_system = hybrid_sys

@router.post("/api/hybrid/initialize")
async def initialize_hybrid_system(background_tasks: BackgroundTasks):
    """Initialize hybrid recommendation system"""
    try:
        if not hybrid_system:
            raise HTTPException(status_code=500, detail="Hybrid system not initialized")
        
        # Run initialization in background
        background_tasks.add_task(hybrid_system.initialize_system)
        
        return {
            "message": "Hybrid system initialization started",
            "status": "processing",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error initializing hybrid system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/hybrid/user-recommendations/{user_id}")
async def get_user_recommendations(
    user_id: str = Path(..., description="User ID"),
    top_k: int = Query(10, ge=1, le=50, description="Number of recommendations")
):
    """Get comprehensive recommendations for a specific user"""
    try:
        if not hybrid_system:
            raise HTTPException(status_code=500, detail="Hybrid system not initialized")
        
        if not hybrid_system.is_initialized:
            raise HTTPException(status_code=400, detail="Hybrid system not initialized. Call /api/hybrid/initialize first.")
        
        recommendations = hybrid_system.get_user_recommendations(user_id, top_k)
        
        if not recommendations:
            raise HTTPException(status_code=404, detail=f"No recommendations found for user {user_id}")
        
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/hybrid/product-recommendations/{product_id}")
async def get_product_recommendations(
    product_id: str = Path(..., description="Product ID"),
    top_k: int = Query(10, ge=1, le=50, description="Number of recommendations")
):
    """Get comprehensive recommendations for a specific product"""
    try:
        if not hybrid_system:
            raise HTTPException(status_code=500, detail="Hybrid system not initialized")
        
        if not hybrid_system.is_initialized:
            raise HTTPException(status_code=400, detail="Hybrid system not initialized. Call /api/hybrid/initialize first.")
        
        recommendations = hybrid_system.get_product_recommendations(product_id, top_k)
        
        if not recommendations:
            raise HTTPException(status_code=404, detail=f"No recommendations found for product {product_id}")
        
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting product recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/hybrid/promotion-strategy")
async def get_promotion_strategy():
    """Get comprehensive promotion strategy"""
    try:
        if not hybrid_system:
            raise HTTPException(status_code=500, detail="Hybrid system not initialized")
        
        if not hybrid_system.is_initialized:
            raise HTTPException(status_code=400, detail="Hybrid system not initialized. Call /api/hybrid/initialize first.")
        
        strategy = hybrid_system.get_promotion_strategy()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="No promotion strategy found")
        
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting promotion strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/hybrid/generate-complete-strategy")
async def generate_complete_strategy(background_tasks: BackgroundTasks):
    """Generate complete AI strategy using all models"""
    try:
        if not hybrid_system:
            raise HTTPException(status_code=500, detail="Hybrid system not initialized")
        
        # Run in background for better performance
        background_tasks.add_task(hybrid_system.generate_complete_ai_strategy)
        
        return {
            "message": "Complete AI strategy generation started",
            "status": "processing",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error generating complete strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


