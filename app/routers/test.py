"""
Test router để debug serialization issues
"""
from fastapi import APIRouter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/test/simple")
async def test_simple():
    """Simple test endpoint"""
    return {
        "message": "Hello World",
        "timestamp": datetime.now().isoformat(),
        "status": "ok"
    }

@router.get("/api/test/products")
async def test_products():
    """Test products endpoint with minimal data"""
    try:
        from infrastructure.db.mongodb_access import mongodb_data
        
        products_df = mongodb_data.get_products_data()
        
        if products_df.empty:
            return {"products": [], "count": 0}
        
        # Return only first 3 products with minimal fields
        test_products = []
        for i, row in products_df.head(3).iterrows():
            product = {
                "id": str(row.get('_id', '')),
                "name": str(row.get('productName', '')),
                "price": float(row.get('productPrice', 0)),
                "category": str(row.get('productCategory', ''))
            }
            test_products.append(product)
        
        return {
            "products": test_products,
            "count": len(test_products),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Test products failed: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@router.get("/api/test/business-health")
async def test_business_health():
    """Test business health with minimal data"""
    try:
        from application.services.ai_promotion_service import create_promotion_service
        import os
        
        # Create a simple promotion service
        gemini_key = os.getenv("GEMINI_API_KEY", "test-key")
        service = create_promotion_service(gemini_key)
        
        # Test the method
        result = service.analyze_business_health()
        
        return {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Test business health failed: {e}")
        import traceback
        return {
            "error": str(e), 
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/api/test/data-products")
async def test_data_products():
    """Test data products endpoint with safe serialization"""
    try:
        from infrastructure.db.mongodb_access import mongodb_data
        from utils.numpy_serializer import convert_numpy_types
        
        products_df = mongodb_data.get_products_data()
        
        if products_df.empty:
            return {"products": [], "count": 0}
        
        # Convert DataFrame to dict and sanitize all types
        products = products_df.to_dict('records')
        products = convert_numpy_types(products)
        
        return {
            "products": products,
            "count": len(products),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Test data products failed: {e}")
        import traceback
        return {
            "error": str(e), 
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        }
