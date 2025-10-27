"""
FastAPI endpoints cho AI Promotion System - CLEAN VERSION
Sử dụng routers để tổ chức code tốt hơn
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

# Import routers
from app.routers import basic, hybrid, models, analytics, data, legacy
from application.services.ai_promotion_service import create_promotion_service
from application.services.hybrid_recommender import create_hybrid_recommender

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
        
        # Initialize services
        promotion_service = create_promotion_service(gemini_api_key)
        hybrid_system = create_hybrid_recommender(gemini_api_key)
        
        # Set global services in routers
        basic.set_global_services(promotion_service, hybrid_system)
        hybrid.set_global_services(hybrid_system)
        models.set_global_services(hybrid_system)
        analytics.set_global_services(promotion_service)
        legacy.set_global_services(promotion_service)
        
        logger.info("✅ All AI services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")

# Include routers
app.include_router(basic.router)
app.include_router(hybrid.router)
app.include_router(models.router)
app.include_router(analytics.router)
app.include_router(data.router)
app.include_router(legacy.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)









