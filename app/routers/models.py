"""
Individual Model endpoints router
TensorFlow Recommenders, HuggingFace, Dynamic Pricing
"""
from fastapi import APIRouter, HTTPException, Query, Path
from datetime import datetime
import logging
import pandas as pd

from infrastructure.db.mongodb_access import mongodb_data

logger = logging.getLogger(__name__)
router = APIRouter()

# Global services (will be injected from main.py)
hybrid_system = None

def set_global_services(hybrid_sys):
    """Set global services from main.py"""
    global hybrid_system
    hybrid_system = hybrid_sys

# =============================================================================
# TENSORFLOW RECOMMENDERS ENDPOINTS
# =============================================================================

@router.get("/api/tf-recommenders/recommendations/{user_id}")
async def get_tf_recommendations(
    user_id: str = Path(..., description="User ID"),
    top_k: int = Query(5, ge=1, le=20, description="Number of recommendations")
):
    """Get TensorFlow Recommenders recommendations"""
    try:
        if not hybrid_system or not hybrid_system.is_initialized:
            raise HTTPException(status_code=400, detail="Hybrid system not initialized")
        
        recommendations = hybrid_system.tf_recommender.get_recommendations(user_id, top_k)
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "model": "TensorFlow Recommenders",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting TF recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# HUGGINGFACE TRANSFORMERS ENDPOINTS
# =============================================================================

@router.get("/api/huggingface/similar-products/{product_id}")
async def get_hf_similar_products(
    product_id: str = Path(..., description="Product ID"),
    top_k: int = Query(5, ge=1, le=20, description="Number of similar products")
):
    """Get HuggingFace similar products"""
    try:
        if not hybrid_system or not hybrid_system.is_initialized:
            raise HTTPException(status_code=400, detail="Hybrid system not initialized")
        
        recommendations = hybrid_system.hf_filter.get_product_recommendations(product_id, top_k)
        
        return {
            "product_id": product_id,
            "similar_products": recommendations,
            "model": "HuggingFace Transformers",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting HF similar products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/huggingface/search-products")
async def search_products_by_query(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results")
):
    """Search products using HuggingFace semantic search"""
    try:
        if not hybrid_system or not hybrid_system.is_initialized:
            raise HTTPException(status_code=400, detail="Hybrid system not initialized")
        
        results = hybrid_system.hf_filter.find_similar_products(query, top_k)
        
        return {
            "query": query,
            "results": results,
            "model": "HuggingFace Transformers",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error searching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# DYNAMIC PRICING ENDPOINTS
# =============================================================================

@router.get("/api/pricing/optimize/{product_id}")
async def optimize_product_price(
    product_id: str = Path(..., description="Product ID"),
    target_date: str = Query(None, description="Target date (YYYY-MM-DD)")
):
    """Optimize price for a specific product"""
    try:
        if not hybrid_system or not hybrid_system.is_initialized:
            raise HTTPException(status_code=400, detail="Hybrid system not initialized")
        
        # Parse target date
        if target_date:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        else:
            target_dt = datetime.now()
        
        # Get product info
        products_df = mongodb_data.get_products_data()
        product_info = products_df[products_df['_id'] == product_id]
        
        if product_info.empty:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        
        current_price = product_info.iloc[0].get('productPrice', 0)
        if current_price == 0:
            raise HTTPException(status_code=400, detail="Product price not available")
        
        # Get pricing data
        orders_df = mongodb_data.get_orders_data()
        pricing_df = hybrid_system.pricing_model.prepare_pricing_data(orders_df, products_df)
        
        # Optimize price
        optimization = hybrid_system.pricing_model.optimize_price(
            product_id, current_price, target_dt, pricing_df
        )
        
        if not optimization:
            raise HTTPException(status_code=404, detail="Price optimization failed")
        
        return {
            "product_id": product_id,
            "product_name": product_info.iloc[0].get('productName', ''),
            "optimization": optimization,
            "model": "Dynamic Pricing",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error optimizing price: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/pricing/strategy")
async def get_pricing_strategy():
    """Get comprehensive pricing strategy"""
    try:
        if not hybrid_system or not hybrid_system.is_initialized:
            raise HTTPException(status_code=400, detail="Hybrid system not initialized")
        
        orders_df = mongodb_data.get_orders_data()
        products_df = mongodb_data.get_products_data()
        pricing_df = hybrid_system.pricing_model.prepare_pricing_data(orders_df, products_df)
        
        strategy = hybrid_system.pricing_model.get_promotion_strategy(products_df, pricing_df)
        
        return {
            "pricing_strategy": strategy,
            "model": "Dynamic Pricing",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting pricing strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


