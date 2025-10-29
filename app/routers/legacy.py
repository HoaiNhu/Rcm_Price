"""
Legacy endpoints router
Backward compatibility endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Global services (will be injected from main.py)
promotion_service = None

def set_global_services(promo_service):
    """Set global services from main.py"""
    global promotion_service
    promotion_service = promo_service

@router.get("/api/business-health")
async def get_business_health_legacy():
    """Legacy endpoint for business health"""
    # Import here to avoid circular imports
    from app.routers.analytics import get_business_analytics
    return await get_business_analytics()

@router.get("/api/product-combos")
async def get_product_combos_legacy():
    """Legacy endpoint for product combos"""
    try:
        if not promotion_service:
            raise HTTPException(status_code=500, detail="Promotion service not initialized")
        
        combos = promotion_service.discover_product_combos()
        return combos
    except Exception as e:
        logger.error(f"❌ Error getting product combos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/recommendations")
async def get_recommendations_legacy():
    """Legacy endpoint for recommendations"""
    try:
        if not promotion_service:
            raise HTTPException(status_code=500, detail="Promotion service not initialized")
        
        recommendations = promotion_service.generate_recommendations()
        return recommendations
    except Exception as e:
        logger.error(f"❌ Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/generate-strategy")
async def generate_strategy_legacy(background_tasks: BackgroundTasks):
    """Legacy endpoint for strategy generation"""
    try:
        if not promotion_service:
            raise HTTPException(status_code=500, detail="Promotion service not initialized")
        
        background_tasks.add_task(promotion_service.generate_complete_promotion_strategy)
        
        return {
            "message": "Promotion strategy generation started",
            "status": "processing",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error generating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/recent-strategies")
async def get_recent_strategies_legacy(limit: int = 5):
    """Legacy endpoint for recent strategies"""
    try:
        if not promotion_service:
            raise HTTPException(status_code=500, detail="Promotion service not initialized")
        
        strategies = promotion_service.get_recent_strategies(limit)
        return {
            "strategies": strategies,
            "count": len(strategies),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting recent strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))










