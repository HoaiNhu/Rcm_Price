"""
FastAPI endpoints cho AI Promotion System - ENHANCED VERSION
Tích hợp MongoDB, TensorFlow Recommenders, HuggingFace, Dynamic Pricing
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import os
import pandas as pd
from dotenv import load_dotenv

from application.services.ai_promotion_service import create_promotion_service
from application.services.hybrid_recommender import create_hybrid_recommender
from infrastructure.db.mongodb_access import mongodb_data

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Promotion System API",
    description="Hệ thống AI gợi ý chiến lược promotion cho cửa hàng bánh ngọt với MongoDB, TensorFlow Recommenders, HuggingFace Transformers, và Dynamic Pricing",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
promotion_service = None
hybrid_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global promotion_service, hybrid_system
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.warning("⚠️ GEMINI_API_KEY not found in environment variables")
        
        # Initialize original promotion service
        promotion_service = create_promotion_service(gemini_api_key)
        
        # Initialize hybrid recommendation system
        hybrid_system = create_hybrid_recommender(gemini_api_key)
        
        logger.info("✅ All AI services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")

# =============================================================================
# BASIC ENDPOINTS
# =============================================================================

@app.get("/")
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

@app.get("/health")
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

# =============================================================================
# HYBRID RECOMMENDATION SYSTEM ENDPOINTS
# =============================================================================

@app.post("/api/hybrid/initialize")
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

@app.get("/api/hybrid/user-recommendations/{user_id}")
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

@app.get("/api/hybrid/product-recommendations/{product_id}")
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

@app.get("/api/hybrid/promotion-strategy")
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

@app.post("/api/hybrid/generate-complete-strategy")
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

# =============================================================================
# INDIVIDUAL MODEL ENDPOINTS
# =============================================================================

@app.get("/api/tf-recommenders/recommendations/{user_id}")
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

@app.get("/api/huggingface/similar-products/{product_id}")
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

@app.get("/api/huggingface/search-products")
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

@app.get("/api/pricing/optimize/{product_id}")
async def optimize_product_price(
    product_id: str = Path(..., description="Product ID"),
    target_date: Optional[str] = Query(None, description="Target date (YYYY-MM-DD)")
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

@app.get("/api/pricing/strategy")
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

# =============================================================================
# ANALYTICS & REPORTING ENDPOINTS
# =============================================================================

@app.get("/api/analytics/business-health")
async def get_business_analytics():
    """Get comprehensive business analytics"""
    try:
        if not promotion_service:
            raise HTTPException(status_code=500, detail="Promotion service not initialized")
        
        analytics = promotion_service.analyze_business_health()
        
        return {
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting business analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/product-performance")
async def get_product_performance():
    """Get product performance analytics"""
    try:
        orders_df = mongodb_data.get_orders_data()
        products_df = mongodb_data.get_products_data()
        ratings_df = mongodb_data.get_ratings_data()
        
        if orders_df.empty or products_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Calculate product performance
        product_performance = []
        
        for _, product in products_df.iterrows():
            product_id = product['_id']
            product_orders = orders_df[orders_df['orderItems[0].product'] == product_id]
            
            # Get ratings
            product_ratings = ratings_df[ratings_df['productId'] == product_id] if not ratings_df.empty else pd.DataFrame()
            
            performance = {
                'product_id': product_id,
                'product_name': product.get('productName', ''),
                'price': product.get('productPrice', 0),
                'orders_count': len(product_orders),
                'total_revenue': product_orders['totalPrice'].sum() if 'totalPrice' in product_orders.columns else 0,
                'avg_rating': product_ratings['rating'].mean() if not product_ratings.empty else 0,
                'total_ratings': len(product_ratings),
                'popularity_score': len(product_orders) * (product_ratings['rating'].mean() / 5.0 if not product_ratings.empty else 0)
            }
            
            product_performance.append(performance)
        
        # Sort by popularity score
        product_performance.sort(key=lambda x: x['popularity_score'], reverse=True)
        
        return {
            "product_performance": product_performance,
            "total_products": len(product_performance),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting product performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/customer-insights")
async def get_customer_insights():
    """Get customer insights and segmentation"""
    try:
        orders_df = mongodb_data.get_orders_data()
        users_df = mongodb_data.get_users_data()
        
        if orders_df.empty or users_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Customer analysis
        customer_insights = {
            'total_customers': len(users_df),
            'active_customers': len(orders_df['userId'].unique()) if 'userId' in orders_df.columns else 0,
            'repeat_customers': len(orders_df[orders_df['userId'].duplicated()]['userId'].unique()) if 'userId' in orders_df.columns else 0,
            'avg_orders_per_customer': len(orders_df) / len(users_df) if len(users_df) > 0 else 0
        }
        
        # Top customers by order count
        if 'userId' in orders_df.columns:
            customer_orders = orders_df['userId'].value_counts().head(10)
            top_customers = []
            
            for user_id, order_count in customer_orders.items():
                user_info = users_df[users_df['_id'] == user_id]
                if not user_info.empty:
                    top_customers.append({
                        'user_id': user_id,
                        'user_name': user_info.iloc[0].get('userName', ''),
                        'order_count': order_count
                    })
            
            customer_insights['top_customers'] = top_customers
        
        return {
            "customer_insights": customer_insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting customer insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/trends")
async def get_market_trends():
    """Get market trends and patterns"""
    try:
        orders_df = mongodb_data.get_orders_data()
        search_histories_df = mongodb_data.get_search_histories_data()
        
        if orders_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Time-based trends
        orders_df['createdAt'] = pd.to_datetime(orders_df['createdAt'])
        orders_df['date'] = orders_df['createdAt'].dt.date
        orders_df['month'] = orders_df['createdAt'].dt.month
        orders_df['weekday'] = orders_df['createdAt'].dt.weekday
        
        # Daily trends
        daily_trends = orders_df.groupby('date').size().to_dict()
        
        # Monthly trends
        monthly_trends = orders_df.groupby('month').size().to_dict()
        
        # Weekday trends
        weekday_trends = orders_df.groupby('weekday').size().to_dict()
        
        # Search trends
        search_trends = {}
        if not search_histories_df.empty:
            search_trends = search_histories_df['query'].value_counts().head(10).to_dict()
        
        trends = {
            'daily_trends': daily_trends,
            'monthly_trends': monthly_trends,
            'weekday_trends': weekday_trends,
            'search_trends': search_trends
        }
        
        return {
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# DATA ACCESS ENDPOINTS
# =============================================================================

@app.get("/api/data/orders")
async def get_orders_data(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of records"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get orders data from MongoDB"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        orders_df = mongodb_data.get_orders_data(start_dt, end_dt, limit)
        
        if orders_df.empty:
            return {"orders": [], "count": 0}
        
        orders = orders_df.to_dict('records')
        
        return {
            "orders": orders,
            "count": len(orders),
            "filters": {
                "limit": limit,
                "start_date": start_date,
                "end_date": end_date
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting orders data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/products")
async def get_products_data():
    """Get products data from MongoDB"""
    try:
        products_df = mongodb_data.get_products_data()
        
        if products_df.empty:
            return {"products": [], "count": 0}
        
        products = products_df.to_dict('records')
        
        return {
            "products": products,
            "count": len(products),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting products data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/users")
async def get_users_data():
    """Get users data from MongoDB"""
    try:
        users_df = mongodb_data.get_users_data()
        
        if users_df.empty:
            return {"users": [], "count": 0}
        
        users = users_df.to_dict('records')
        
        return {
            "users": users,
            "count": len(users),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting users data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/ratings")
async def get_ratings_data():
    """Get ratings data from MongoDB"""
    try:
        ratings_df = mongodb_data.get_ratings_data()
        
        if ratings_df.empty:
            return {"ratings": [], "count": 0}
        
        ratings = ratings_df.to_dict('records')
        
        return {
            "ratings": ratings,
            "count": len(ratings),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting ratings data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/discounts")
async def get_discounts_data():
    """Get discounts data from MongoDB"""
    try:
        discounts_df = mongodb_data.get_discounts_data()
        
        if discounts_df.empty:
            return {"discounts": [], "count": 0}
        
        discounts = discounts_df.to_dict('records')
        
        return {
            "discounts": discounts,
            "count": len(discounts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting discounts data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/search-histories")
async def get_search_histories_data():
    """Get search histories data from MongoDB"""
    try:
        search_df = mongodb_data.get_search_histories_data()
        
        if search_df.empty:
            return {"search_histories": [], "count": 0}
        
        search_histories = search_df.to_dict('records')
        
        return {
            "search_histories": search_histories,
            "count": len(search_histories),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting search histories data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# =============================================================================

@app.get("/api/business-health")
async def get_business_health_legacy():
    """Legacy endpoint for business health"""
    return await get_business_analytics()

@app.get("/api/product-combos")
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

@app.get("/api/recommendations")
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

@app.post("/api/generate-strategy")
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

@app.get("/api/recent-strategies")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
