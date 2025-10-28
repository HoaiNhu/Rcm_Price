"""
Personalized Dynamic Pricing API Router
Provides REST endpoints for personalized pricing
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from application.services.personalized_pricing_service import (
    PersonalizedPricingService,
    create_personalized_pricing_service
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/personalized-pricing",
    tags=["personalized-pricing"],
    responses={404: {"description": "Not found"}}
)


# ========================= Pydantic Models =========================

class PersonalizedPriceResponse(BaseModel):
    """Response for personalized price"""
    product_id: str
    user_id: str
    segment: str
    strategy: str
    action: str
    current_price: float
    recommended_price: float
    price_change_pct: float
    price_change_amount: float
    min_allowed_price: float
    max_allowed_price: float
    elasticity: float
    sensitivity: str
    justification_required: bool
    revenue_impact: dict
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_001",
                "user_id": "user_001",
                "segment": "VIP",
                "strategy": "premium",
                "action": "INCREASE",
                "current_price": 100000.0,
                "recommended_price": 110000.0,
                "price_change_pct": 0.1,
                "price_change_amount": 10000.0,
                "min_allowed_price": 100000.0,
                "max_allowed_price": 115000.0,
                "elasticity": -0.8,
                "sensitivity": "MODERATE",
                "justification_required": True,
                "revenue_impact": {
                    "revenue_change_pct": 0.12
                },
                "timestamp": "2024-12-27T10:00:00"
            }
        }


class CatalogItem(BaseModel):
    """Single item in personalized catalog"""
    product_id: str
    product_name: str
    segment: str
    base_price: float
    personalized_price: float
    discount_pct: float
    action: str
    strategy: str


class PricingMatrixRow(BaseModel):
    """Single row in pricing matrix"""
    product_id: str
    product_name: str
    segment: str
    strategy: str
    action: str
    current_price: float
    recommended_price: float
    price_change_pct: float
    elasticity: float
    sensitivity: str


class ValidationRequest(BaseModel):
    """Request for price validation"""
    user_id: str
    product_id: str
    proposed_price: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "product_id": "prod_001",
                "proposed_price": 110000.0
            }
        }


class ValidationResponse(BaseModel):
    """Response for price validation"""
    user_id: str
    product_id: str
    segment: str
    current_price: float
    proposed_price: float
    price_change_pct: float
    is_valid: bool
    reason: str


class SimulationRequest(BaseModel):
    """Request for price simulation"""
    product_id: str
    new_price: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_001",
                "new_price": 110000.0
            }
        }


class SimulationResponse(BaseModel):
    """Response for price simulation"""
    product_id: str
    current_price: float
    new_price: float
    price_change_pct: float
    elasticity: float
    quantity_change_pct: float
    total_customers: int
    total_old_revenue: float
    total_new_revenue: float
    total_revenue_change: float
    total_revenue_change_pct: float
    allowed_segments: List[str]
    blocked_segments: List[str]
    recommendation: str
    segment_impacts: List[dict]


class PricingSummaryResponse(BaseModel):
    """Summary of pricing system"""
    total_products: int
    total_customers: int
    total_possible_prices: int
    segment_distribution: dict
    cache_valid: bool
    last_updated: Optional[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    cache_valid: bool
    elasticity_service_available: bool
    segmentation_service_available: bool


# ========================= Dependency =========================

async def get_pricing_service() -> PersonalizedPricingService:
    """Dependency to get PersonalizedPricingService instance"""
    try:
        return create_personalized_pricing_service()
    except Exception as e:
        logger.error(f"❌ Failed to create pricing service: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize pricing service: {str(e)}"
        )


# ========================= Endpoints =========================

@router.get("/price/{product_id}/{user_id}", response_model=PersonalizedPriceResponse)
async def get_personalized_price(
    product_id: str,
    user_id: str,
    auto_calculate: bool = Query(True, description="Auto-calculate if no cached data"),
    service: PersonalizedPricingService = Depends(get_pricing_service)
):
    """
    Lấy giá cá nhân hóa cho 1 sản phẩm cho 1 khách hàng
    
    **Algorithm:**
    1. Get product price elasticity
    2. Get customer segment
    3. Apply segment-specific pricing rules
    4. Calculate personalized price
    5. Estimate revenue impact
    
    **Pricing Rules by Segment:**
    - **VIP**: Premium pricing, can increase 0-15%
    - **REGULAR**: Moderate pricing, discount 0-10% or increase 0-8%
    - **OCCASIONAL**: Aggressive discounts 5-15%
    - **NEW**: Welcome discount 10-20%
    - **AT_RISK**: Win-back discount 15-25%
    - **LOST**: Deep discount 20-30%
    
    **Parameters:**
    - **product_id**: Product ID
    - **user_id**: Customer ID
    - **auto_calculate**: Auto-run calculations if needed (default: true)
    """
    try:
        pricing = await service.get_personalized_price(
            product_id=product_id,
            user_id=user_id,
            auto_calculate=auto_calculate
        )
        
        return PersonalizedPriceResponse(**pricing)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Failed to get personalized price: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get personalized price: {str(e)}"
        )


@router.get("/catalog/{user_id}", response_model=List[CatalogItem])
async def get_customer_catalog(
    user_id: str,
    product_ids: Optional[str] = Query(None, description="Comma-separated product IDs"),
    auto_calculate: bool = Query(True, description="Auto-calculate if no cached data"),
    service: PersonalizedPricingService = Depends(get_pricing_service)
):
    """
    Lấy catalog với giá cá nhân hóa cho 1 khách hàng
    
    **Returns personalized catalog with:**
    - Base price vs personalized price
    - Discount percentage (if applicable)
    - Pricing action (INCREASE/DISCOUNT/MAINTAIN)
    - Pricing strategy
    
    **Use case:**
    - Display personalized prices to customer
    - E-commerce product listing
    - Shopping cart pricing
    
    **Parameters:**
    - **user_id**: Customer ID
    - **product_ids**: Optional comma-separated product IDs (all if omitted)
    - **auto_calculate**: Auto-run calculations if needed (default: true)
    """
    try:
        # Parse product IDs
        product_list = product_ids.split(',') if product_ids else None
        
        catalog_df = await service.get_customer_catalog(
            user_id=user_id,
            product_ids=product_list,
            auto_calculate=auto_calculate
        )
        
        if catalog_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No products found for user {user_id}"
            )
        
        # Convert to list of dicts
        catalog = catalog_df.to_dict(orient='records')
        
        return [CatalogItem(**item) for item in catalog]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get catalog: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get catalog: {str(e)}"
        )


@router.get("/matrix/{product_id}", response_model=List[PricingMatrixRow])
async def get_pricing_matrix(
    product_id: str,
    auto_calculate: bool = Query(True, description="Auto-calculate if no cached data"),
    service: PersonalizedPricingService = Depends(get_pricing_service)
):
    """
    Lấy pricing matrix cho 1 sản phẩm cho TẤT CẢ segments
    
    **Shows how the same product is priced differently for each segment:**
    - VIP: Premium pricing
    - REGULAR: Moderate pricing
    - OCCASIONAL: Discount pricing
    - NEW: Welcome discount
    - AT_RISK: Win-back discount
    - LOST: Deep discount
    
    **Use case:**
    - Analyze pricing strategy
    - Revenue optimization
    - Segment comparison
    
    **Parameters:**
    - **product_id**: Product ID
    - **auto_calculate**: Auto-run calculations if needed (default: true)
    """
    try:
        matrix_df = await service.get_product_pricing_matrix(
            product_id=product_id,
            auto_calculate=auto_calculate
        )
        
        if matrix_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found"
            )
        
        # Convert to list of dicts
        matrix = matrix_df.to_dict(orient='records')
        
        return [PricingMatrixRow(**row) for row in matrix]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get pricing matrix: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pricing matrix: {str(e)}"
        )


@router.post("/validate", response_model=ValidationResponse)
async def validate_price_change(
    request: ValidationRequest,
    auto_calculate: bool = Query(True, description="Auto-calculate if no cached data"),
    service: PersonalizedPricingService = Depends(get_pricing_service)
):
    """
    Validate if proposed price change is acceptable for customer
    
    **Validation checks:**
    - Segment-specific pricing constraints
    - Min/max discount limits
    - Price increase permissions
    - Required minimum discounts
    
    **Returns:**
    - is_valid: true/false
    - reason: Explanation if invalid
    
    **Use case:**
    - Before applying price changes
    - Admin price override validation
    - Dynamic pricing system checks
    """
    try:
        validation = await service.validate_price_change(
            user_id=request.user_id,
            product_id=request.product_id,
            proposed_price=request.proposed_price,
            auto_calculate=auto_calculate
        )
        
        return ValidationResponse(**validation)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Validation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_price_change(
    request: SimulationRequest,
    auto_calculate: bool = Query(True, description="Auto-calculate if no cached data"),
    service: PersonalizedPricingService = Depends(get_pricing_service)
):
    """
    Simulate revenue impact of price change across all segments
    
    **Simulation includes:**
    - Quantity change based on elasticity
    - Revenue impact per segment
    - Segments where price change is allowed/blocked
    - Total revenue change
    - Recommendation: PROCEED or RECONSIDER
    
    **Use case:**
    - Before implementing price changes
    - Revenue optimization analysis
    - What-if scenarios
    - Risk assessment
    
    **Example:**
    - Product current price: 100,000
    - New price: 110,000 (+10%)
    - Elasticity: -1.2
    - Expected quantity change: -12%
    - VIP segment: Allowed (premium pricing)
    - AT_RISK segment: Blocked (needs discount)
    """
    try:
        simulation = await service.simulate_price_change(
            product_id=request.product_id,
            new_price=request.new_price,
            auto_calculate=auto_calculate
        )
        
        return SimulationResponse(**simulation)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Simulation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )


@router.get("/summary", response_model=PricingSummaryResponse)
async def get_pricing_summary(
    auto_calculate: bool = Query(True, description="Auto-calculate if no cached data"),
    service: PersonalizedPricingService = Depends(get_pricing_service)
):
    """
    Get summary statistics about personalized pricing system
    
    **Returns:**
    - Total products
    - Total customers
    - Total possible price combinations
    - Customer distribution by segment
    - Cache status
    - Last update timestamp
    """
    try:
        summary = await service.get_pricing_summary(auto_calculate=auto_calculate)
        
        return PricingSummaryResponse(**summary)
        
    except Exception as e:
        logger.error(f"❌ Failed to get summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get summary: {str(e)}"
        )


@router.post("/clear-cache")
async def clear_cache(
    service: PersonalizedPricingService = Depends(get_pricing_service)
):
    """
    Clear cache to force refresh of pricing data
    
    **Use case:**
    - After bulk data updates
    - Manual refresh needed
    - Testing with new data
    
    **Next pricing call will re-calculate from database**
    """
    try:
        service.clear_cache()
        
        return {
            "status": "success",
            "message": "Pricing cache cleared successfully",
            "next_action": "Pricing will be re-calculated on next request"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to clear cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    service: PersonalizedPricingService = Depends(get_pricing_service)
):
    """
    Health check endpoint
    
    **Returns:**
    - Service status
    - Cache validity
    - Elasticity service availability
    - Segmentation service availability
    """
    try:
        return HealthResponse(
            status="healthy",
            service="personalized-pricing",
            cache_valid=service._is_cache_valid(),
            elasticity_service_available=service.elasticity_service is not None,
            segmentation_service_available=service.segmentation_service is not None
        )
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )
