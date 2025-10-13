"""
Minimal FastAPI Application - No Heavy Dependencies
Chạy được ngay cả khi không cài được TensorFlow, PyTorch, etc.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Promotion System API - Minimal Version",
    description="Hệ thống AI gợi ý chiến lược promotion cho cửa hàng bánh ngọt (Minimal Dependencies)",
    version="2.0.0-minimal",
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

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global promotion_service
    try:
        # Try to import MongoDB access
        try:
            from infrastructure.db.mongodb_access import mongodb_data
            logger.info("✅ MongoDB access available")
        except ImportError:
            logger.warning("⚠️ MongoDB access not available")
            mongodb_data = None
        
        # Try to import promotion service
        try:
            from application.services.ai_promotion_service import create_promotion_service
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                promotion_service = create_promotion_service(gemini_api_key)
                logger.info("✅ AI Promotion Service initialized")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not found")
        except ImportError:
            logger.warning("⚠️ AI Promotion Service not available")
        
        logger.info("✅ Minimal API initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")

# =============================================================================
# BASIC ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AI Promotion System API v2.0 - Minimal Version",
        "version": "2.0.0-minimal",
        "status": "running",
        "features": [
            "MongoDB Integration",
            "Basic Analytics",
            "Data Access",
            "Minimal Dependencies"
        ],
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Check services
        services_status = {
            "mongodb": "unknown",
            "promotion_service": "initialized" if promotion_service else "not_initialized",
            "gemini": "configured" if os.getenv("GEMINI_API_KEY") else "not_configured"
        }
        
        # Try to test MongoDB
        try:
            from infrastructure.db.mongodb_access import mongodb_data
            test_data = mongodb_data.get_products_data()
            services_status["mongodb"] = "connected"
            data_availability = {
                "products": len(test_data) if not test_data.empty else 0,
                "orders": len(mongodb_data.get_orders_data()) if not mongodb_data.get_orders_data().empty else 0
            }
        except:
            services_status["mongodb"] = "not_connected"
            data_availability = {"products": 0, "orders": 0}
        
        return {
            "status": "healthy",
            "services": services_status,
            "data_availability": data_availability,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# =============================================================================
# BASIC ANALYTICS ENDPOINTS
# =============================================================================

@app.get("/api/analytics/business-health")
async def get_business_analytics():
    """Get basic business analytics"""
    try:
        if not promotion_service:
            # Return mock data if service not available
            return {
                "analytics": {
                    "message": "AI Promotion Service not available",
                    "total_orders": 0,
                    "total_revenue": 0,
                    "avg_order_value": 0,
                    "product_performance": {}
                },
                "timestamp": datetime.now().isoformat()
            }
        
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
    """Get basic product performance analytics"""
    try:
        try:
            from infrastructure.db.mongodb_access import mongodb_data
            orders_df = mongodb_data.get_orders_data()
            products_df = mongodb_data.get_products_data()
            ratings_df = mongodb_data.get_ratings_data()
        except ImportError:
            return {
                "product_performance": [],
                "total_products": 0,
                "message": "MongoDB access not available",
                "timestamp": datetime.now().isoformat()
            }
        
        if orders_df.empty or products_df.empty:
            return {
                "product_performance": [],
                "total_products": 0,
                "message": "No data available",
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate basic product performance
        product_performance = []
        
        for _, product in products_df.iterrows():
            product_id = product['_id']
            product_orders = orders_df[orders_df['orderItems[0].product'] == product_id] if 'orderItems[0].product' in orders_df.columns else pd.DataFrame()
            
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

# =============================================================================
# DATA ACCESS ENDPOINTS
# =============================================================================

@app.get("/api/data/products")
async def get_products_data():
    """Get products data from MongoDB"""
    try:
        try:
            from infrastructure.db.mongodb_access import mongodb_data
            products_df = mongodb_data.get_products_data()
        except ImportError:
            return {
                "products": [],
                "count": 0,
                "message": "MongoDB access not available",
                "timestamp": datetime.now().isoformat()
            }
        
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

@app.get("/api/data/orders")
async def get_orders_data(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of records")
):
    """Get orders data from MongoDB"""
    try:
        try:
            from infrastructure.db.mongodb_access import mongodb_data
            orders_df = mongodb_data.get_orders_data(limit=limit)
        except ImportError:
            return {
                "orders": [],
                "count": 0,
                "message": "MongoDB access not available",
                "timestamp": datetime.now().isoformat()
            }
        
        if orders_df.empty:
            return {"orders": [], "count": 0}
        
        orders = orders_df.to_dict('records')
        
        return {
            "orders": orders,
            "count": len(orders),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting orders data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/users")
async def get_users_data():
    """Get users data from MongoDB"""
    try:
        try:
            from infrastructure.db.mongodb_access import mongodb_data
            users_df = mongodb_data.get_users_data()
        except ImportError:
            return {
                "users": [],
                "count": 0,
                "message": "MongoDB access not available",
                "timestamp": datetime.now().isoformat()
            }
        
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

# =============================================================================
# MOCK ENDPOINTS (for testing without heavy dependencies)
# =============================================================================

@app.get("/api/mock/recommendations/{user_id}")
async def get_mock_recommendations(
    user_id: str = Path(..., description="User ID"),
    top_k: int = Query(5, ge=1, le=20, description="Number of recommendations")
):
    """Get mock recommendations for testing"""
    mock_recommendations = [
        {
            "product_id": f"product_{i}",
            "product_name": f"Bánh Mock {i}",
            "score": 0.9 - (i * 0.1),
            "recommendation_type": "mock"
        }
        for i in range(1, top_k + 1)
    ]
    
    return {
        "user_id": user_id,
        "recommendations": mock_recommendations,
        "model": "Mock Recommendation System",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/mock/promotion-strategy")
async def get_mock_promotion_strategy():
    """Get mock promotion strategy"""
    return {
        "strategy": {
            "current_season": "Spring 2024",
            "promotion_products": [
                {
                    "product_id": "product_1",
                    "product_name": "Bánh Mock 1",
                    "discount_percentage": 20,
                    "reason": "Sản phẩm bán chạy nhất"
                }
            ],
            "combo_suggestions": [
                {
                    "combo": ["Bánh Mock 1", "Bánh Mock 2"],
                    "price": 450000,
                    "target": "Khách hàng VIP"
                }
            ],
            "promotion_schedule": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "discount_code": "SPRING2024"
            }
        },
        "model": "Mock Promotion Strategy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
