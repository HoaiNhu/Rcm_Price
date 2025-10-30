"""
Price Elasticity API Router
RESTful endpoints cho price elasticity management

Author: RCM_PRICE Team
Date: 2025-10-27
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from application.services.price_elasticity_service import create_price_elasticity_service
from infrastructure.db.mongodb_access import MongoDBDataAccess

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/price-elasticity",
    tags=["Price Elasticity"]
)


# ==================== Pydantic Models ====================

class ElasticityCalculationRequest(BaseModel):
    """Request model for elasticity calculation"""
    days: int = Field(default=90, ge=30, le=365, description="Số ngày data để phân tích")
    min_samples: int = Field(default=10, ge=5, le=100, description="Số samples tối thiểu")
    force_recalculate: bool = Field(default=False, description="Force tính lại")


class PriceSimulationRequest(BaseModel):
    """Request model for price change simulation"""
    product_id: str = Field(..., description="ID của sản phẩm")
    new_price: float = Field(..., gt=0, description="Giá mới đề xuất")


class ElasticityResponse(BaseModel):
    """Response model cho elasticity data"""
    success: bool
    elasticity_data: Optional[dict] = None
    summary: Optional[dict] = None
    error: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Response model cho price recommendation"""
    success: bool
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    current_price: Optional[float] = None
    elasticity: Optional[float] = None
    sensitivity: Optional[str] = None
    max_safe_increase_pct: Optional[float] = None
    max_safe_price: Optional[float] = None
    recommendation: Optional[str] = None
    error: Optional[str] = None


class SimulationResponse(BaseModel):
    """Response model cho price simulation"""
    success: bool
    product_id: Optional[str] = None
    current_price: Optional[float] = None
    new_price: Optional[float] = None
    price_change_pct: Optional[float] = None
    estimated_quantity_change_pct: Optional[float] = None
    revenue_change: Optional[float] = None
    revenue_change_pct: Optional[float] = None
    is_safe_change: Optional[bool] = None
    recommendation: Optional[str] = None
    error: Optional[str] = None


# ==================== API Endpoints ====================

@router.post(
    "/calculate",
    response_model=ElasticityResponse,
    summary="Calculate price elasticity for all products"
)
async def calculate_elasticity(
    request: ElasticityCalculationRequest
):
    """
    Tính toán price elasticity cho tất cả sản phẩm
    
    ## Parameters:
    - **days**: Số ngày data để phân tích (30-365 days)
    - **min_samples**: Số samples tối thiểu để tính elasticity (5-100)
    - **force_recalculate**: Force tính lại ngay cả khi có cache
    
    ## Returns:
    - **elasticity_data**: Dict mapping product_id -> elasticity coefficient
    - **summary**: Thống kê tổng quan về elasticity
    
    ## Example Response:
    ```json
    {
        "success": true,
        "elasticity_data": {
            "product_123": -0.8,
            "product_456": -1.6
        },
        "summary": {
            "total_products": 50,
            "mean_elasticity": -1.2,
            "sensitivity_distribution": {
                "VERY_SENSITIVE": 10,
                "SENSITIVE": 15,
                "MODERATE": 20,
                "INSENSITIVE": 5
            }
        }
    }
    ```
    """
    try:
        logger.info(
            f"📊 Calculating price elasticity for {request.days} days, "
            f"min_samples={request.min_samples}"
        )
        
        # Get service instance
        db_access = MongoDBDataAccess(use_async=False)
        service = create_price_elasticity_service(db_access)
        
        # Calculate elasticity
        result = await service.calculate_all_elasticities(
            days=request.days,
            min_samples=request.min_samples,
            force_recalculate=request.force_recalculate
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Calculation failed')
            )
        
        return ElasticityResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in calculate_elasticity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/recommendation/{product_id}",
    response_model=RecommendationResponse,
    summary="Get price recommendation for a product"
)
async def get_product_recommendation(
    product_id: str
):
    """
    Lấy recommendation về thay đổi giá cho một sản phẩm
    
    ## Parameters:
    - **product_id**: ID của sản phẩm cần phân tích
    
    ## Returns:
    - **elasticity**: Hệ số elasticity
    - **sensitivity**: Độ nhạy cảm (VERY_SENSITIVE/SENSITIVE/MODERATE/INSENSITIVE)
    - **max_safe_increase_pct**: % tăng giá an toàn tối đa
    - **max_safe_price**: Giá an toàn tối đa
    - **recommendation**: Chi tiết khuyến nghị
    
    ## Example Response:
    ```json
    {
        "success": true,
        "product_id": "product_123",
        "product_name": "Bánh Su Kem",
        "current_price": 20000,
        "elasticity": -0.8,
        "sensitivity": "MODERATE",
        "max_safe_increase_pct": 10.0,
        "max_safe_price": 22000,
        "recommendation": "✅ ĐỘ NHẠY TRUNG BÌNH (E=-0.80)..."
    }
    ```
    """
    try:
        logger.info(f"🔍 Getting recommendation for product {product_id}")
        
        # Get service instance
        db_access = MongoDBDataAccess(use_async=False)
        service = create_price_elasticity_service(db_access)
        
        # Get recommendation
        result = await service.get_product_recommendation(product_id)
        
        if not result['success']:
            raise HTTPException(
                status_code=404,
                detail=result.get('error', 'Product not found')
            )
        
        return RecommendationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_product_recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/recommendations",
    summary="Get recommendations for all products"
)
async def get_all_recommendations():
    """
    Lấy recommendations cho tất cả sản phẩm
    
    ## Returns:
    - **recommendations**: List tất cả recommendations
    - **grouped_by_sensitivity**: Recommendations grouped theo sensitivity
    - **summary**: Thống kê tổng quan
    
    ## Example Response:
    ```json
    {
        "success": true,
        "total_products": 50,
        "recommendations": [...],
        "grouped_by_sensitivity": {
            "VERY_SENSITIVE": [...],
            "SENSITIVE": [...],
            "MODERATE": [...],
            "INSENSITIVE": [...]
        }
    }
    ```
    """
    try:
        logger.info("📊 Getting recommendations for all products")
        
        # Get service instance
        db_access = MongoDBDataAccess(use_async=False)
        service = create_price_elasticity_service(db_access)
        
        # Get all recommendations
        result = await service.get_all_recommendations()
        
        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to get recommendations')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_all_recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/report",
    summary="Get detailed elasticity report"
)
async def get_elasticity_report():
    """
    Lấy báo cáo chi tiết về price elasticity
    
    ## Returns:
    - **report**: Chi tiết elasticity cho từng sản phẩm
    - **summary**: Thống kê tổng quan
    - **quality_validation**: Đánh giá chất lượng của calculations
    
    ## Example Response:
    ```json
    {
        "success": true,
        "report": [
            {
                "product_id": "product_123",
                "elasticity": -0.8,
                "sensitivity": "MODERATE",
                "r_squared": 0.75,
                "sample_size": 45,
                "can_increase_price": true
            }
        ],
        "quality_validation": {
            "is_valid": true,
            "quality_rate": 85.5
        }
    }
    ```
    """
    try:
        logger.info("📊 Generating elasticity report")
        
        # Get service instance
        db_access = MongoDBDataAccess(use_async=False)
        service = create_price_elasticity_service(db_access)
        
        # Get report
        result = await service.get_elasticity_report()
        
        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to generate report')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_elasticity_report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/simulate",
    response_model=SimulationResponse,
    summary="Simulate price change impact"
)
async def simulate_price_change(
    request: PriceSimulationRequest
):
    """
    Simulate tác động của việc thay đổi giá
    
    ## Parameters:
    - **product_id**: ID của sản phẩm
    - **new_price**: Giá mới đề xuất
    
    ## Returns:
    - **estimated_quantity_change_pct**: % thay đổi số lượng dự kiến
    - **revenue_change**: Thay đổi doanh thu (VND)
    - **is_safe_change**: Có phải là thay đổi an toàn?
    - **recommendation**: Chi tiết khuyến nghị
    
    ## Example Request:
    ```json
    {
        "product_id": "product_123",
        "new_price": 22000
    }
    ```
    
    ## Example Response:
    ```json
    {
        "success": true,
        "product_id": "product_123",
        "current_price": 20000,
        "new_price": 22000,
        "price_change_pct": 10.0,
        "estimated_quantity_change_pct": -8.0,
        "revenue_change": 150000,
        "revenue_change_pct": 5.2,
        "is_safe_change": true
    }
    ```
    """
    try:
        logger.info(
            f"🎯 Simulating price change for {request.product_id}: "
            f"new_price={request.new_price}"
        )
        
        # Get service instance
        db_access = MongoDBDataAccess(use_async=False)
        service = create_price_elasticity_service(db_access)
        
        # Simulate price change
        result = await service.simulate_price_change(
            request.product_id,
            request.new_price
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=404,
                detail=result.get('error', 'Simulation failed')
            )
        
        return SimulationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in simulate_price_change: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Health check for price elasticity service"
)
async def health_check():
    """
    Kiểm tra tình trạng của Price Elasticity Service
    
    ## Returns:
    - **status**: Tình trạng service
    - **is_trained**: Calculator đã được train chưa
    - **last_training_time**: Thời gian train lần cuối
    """
    try:
        # Get service instance
        db_access = MongoDBDataAccess(use_async=False)
        service = create_price_elasticity_service(db_access)
        
        return {
            "status": "healthy",
            "service": "Price Elasticity Calculator",
            "is_trained": service.calculator.is_trained,
            "last_training_time": (
                service.last_training_time.isoformat() 
                if service.last_training_time 
                else None
            ),
            "total_products_analyzed": len(service.calculator.product_elasticity)
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
