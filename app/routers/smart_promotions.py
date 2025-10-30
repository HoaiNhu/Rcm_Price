"""
Smart Promotion Generator API Router
Week 6: Intelligent promotion and voucher generation
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from application.services.smart_promotion_service import (
    get_promotion_service,
    SmartPromotionService
)

router = APIRouter(
    prefix="/api/smart-promotions",
    tags=["smart-promotions"]
)


# ============================================================================
# Pydantic Models
# ============================================================================

class SegmentPromotionRequest(BaseModel):
    """Request to generate segment-based promotion"""
    segment: str = Field(..., description="Customer segment (VIP/REGULAR/OCCASIONAL/NEW/AT_RISK/LOST)")
    product_ids: Optional[List[str]] = Field(None, description="Product IDs (default: all products)")
    goal: str = Field("RETENTION", description="Promotion goal (ACQUISITION/RETENTION/WINBACK/REVENUE_MAX)")
    validity_days: int = Field(30, ge=1, le=365, description="Voucher validity days")
    
    class Config:
        json_schema_extra = {
            "example": {
                "segment": "NEW",
                "product_ids": ["prod_banh_mi", "prod_pho_bo"],
                "goal": "ACQUISITION",
                "validity_days": 30
            }
        }


class PriceIncreaseVoucherRequest(BaseModel):
    """Request to generate price increase voucher"""
    product_id: str = Field(..., description="Product ID")
    new_price: float = Field(..., gt=0, description="New (higher) price")
    segment: str = Field(..., description="Target segment")
    validity_days: int = Field(30, ge=1, le=365, description="Voucher validity days")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_banh_mi",
                "new_price": 28000,
                "segment": "REGULAR",
                "validity_days": 30
            }
        }


class BundlePromotionRequest(BaseModel):
    """Request to generate bundle promotion"""
    product_bundles: List[Tuple[str, str]] = Field(
        ...,
        min_length=1,
        description="List of product pairs for bundles"
    )
    bundle_discount_pct: float = Field(0.15, ge=0.05, le=0.5, description="Bundle discount (5-50%)")
    segment: Optional[str] = Field(None, description="Target segment (optional)")
    validity_days: int = Field(30, ge=1, le=365, description="Validity days")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_bundles": [
                    ["prod_banh_mi", "prod_cafe_sua"],
                    ["prod_pho_bo", "prod_bun_cha"]
                ],
                "bundle_discount_pct": 0.15,
                "validity_days": 30
            }
        }


class PromotionResponse(BaseModel):
    """Promotion response"""
    promotion_id: str
    segment: str
    goal: str
    type: str
    value: float
    description: str
    product_ids: List[str]
    original_prices: Dict[str, float]
    discounted_prices: Dict[str, float]
    vouchers: List[str]
    valid_from: str
    valid_until: str
    max_uses: int
    min_order_value: Optional[float]
    created_at: str


class VoucherResponse(BaseModel):
    """Voucher response"""
    voucher_code: str
    type: str
    product_id: str
    segment: str
    old_price: float
    new_price: float
    price_increase: float
    price_increase_pct: float
    voucher_value: float
    final_price: float
    description: str
    valid_from: str
    valid_until: str
    max_uses: int
    created_at: str


class CampaignResponse(BaseModel):
    """Campaign response"""
    campaign_id: str
    type: str
    target_segment: str
    n_customers: int
    discount_pct: float
    customer_vouchers: Dict[str, str]
    discounted_catalog: Dict[str, Dict]
    description: str
    valid_from: str
    valid_until: str
    created_at: str


class BundlePromotionResponse(BaseModel):
    """Bundle promotion response"""
    promotion_id: str
    type: str
    segment: str
    bundles: List[Dict]
    bundle_discount_pct: float
    total_savings: float
    voucher_code: str
    description: str
    valid_from: str
    valid_until: str
    created_at: str


class PromotionSummaryResponse(BaseModel):
    """Service summary"""
    service: str
    version: str
    capabilities: List[str]
    cached_promotions: int
    promotion_types: List[str]
    timestamp: str


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/generate-segment-promotion", response_model=PromotionResponse)
async def generate_segment_promotion(request: SegmentPromotionRequest):
    """
    Generate promotion for customer segment
    
    Creates segment-specific promotion with:
    - Automatic discount calculation based on segment rules
    - Voucher code generation
    - Discounted pricing for all products
    
    Segment Strategies:
    - VIP: Loyalty bonus, free shipping (no discounts)
    - REGULAR/OCCASIONAL: Moderate discounts (5-10%)
    - NEW: Welcome discount (10-20%)
    - AT_RISK/LOST: Win-back discount (20-30%)
    
    Example:
    ```
    POST /api/smart-promotions/generate-segment-promotion
    {
        "segment": "NEW",
        "goal": "ACQUISITION",
        "validity_days": 30
    }
    ```
    """
    try:
        service = get_promotion_service()
        
        promotion = await service.generate_segment_promotion(
            segment=request.segment,
            product_ids=request.product_ids,
            goal=request.goal,
            validity_days=request.validity_days
        )
        
        return PromotionResponse(**promotion)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Promotion generation error: {str(e)}")


@router.post("/generate-price-increase-voucher", response_model=VoucherResponse)
async def generate_price_increase_voucher(request: PriceIncreaseVoucherRequest):
    """
    Generate voucher to offset price increase
    
    Strategy: When increasing prices, generate vouchers to maintain
    customer satisfaction. Voucher offsets 60% of price increase.
    
    Use case:
    - Price increased from 25,000 to 27,000 VND (+2,000)
    - Voucher value: 1,200 VND (60% of increase)
    - Final price with voucher: 25,800 VND (small increase)
    
    Example:
    ```
    POST /api/smart-promotions/generate-price-increase-voucher
    {
        "product_id": "prod_banh_mi",
        "new_price": 27000,
        "segment": "REGULAR"
    }
    ```
    """
    try:
        service = get_promotion_service()
        
        voucher = await service.generate_price_increase_voucher(
            product_id=request.product_id,
            new_price=request.new_price,
            segment=request.segment,
            validity_days=request.validity_days
        )
        
        return VoucherResponse(**voucher)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voucher generation error: {str(e)}")


@router.post("/generate-winback-campaign", response_model=CampaignResponse)
async def generate_winback_campaign(
    validity_days: int = Query(default=60, ge=1, le=365, description="Campaign validity days")
):
    """
    Generate win-back campaign for AT_RISK/LOST customers
    
    Automatically:
    - Finds all AT_RISK and LOST customers
    - Generates unique voucher for each customer
    - Applies 25% discount on entire catalog
    - Extended validity (default 60 days)
    
    Returns:
    - Customer-to-voucher mapping
    - Discounted catalog
    - Campaign details
    
    Example:
    ```
    POST /api/smart-promotions/generate-winback-campaign?validity_days=60
    ```
    """
    try:
        service = get_promotion_service()
        
        campaign = await service.generate_winback_campaign(
            validity_days=validity_days
        )
        
        if campaign.get('status') == 'no_customers':
            return {
                "message": campaign.get('message'),
                "campaign_id": None,
                "n_customers": 0
            }
        
        return CampaignResponse(**campaign)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign generation error: {str(e)}")


@router.post("/generate-bundle-promotion", response_model=BundlePromotionResponse)
async def generate_bundle_promotion(request: BundlePromotionRequest):
    """
    Generate bundle promotion (Buy together, save more)
    
    Creates promotion for product bundles with discount when
    buying items together.
    
    Example bundles:
    - Bánh Mì + Cà Phê Sữa: Save 15%
    - Phở Bò + Bún Chả: Save 15%
    
    Calculation:
    - Regular total = Product1 + Product2
    - Bundle price = Regular total × (1 - discount%)
    
    Example:
    ```
    POST /api/smart-promotions/generate-bundle-promotion
    {
        "product_bundles": [
            ["prod_banh_mi", "prod_cafe_sua"],
            ["prod_pho_bo", "prod_bun_cha"]
        ],
        "bundle_discount_pct": 0.15
    }
    ```
    """
    try:
        service = get_promotion_service()
        
        promotion = await service.generate_bundle_promotion(
            product_bundles=request.product_bundles,
            bundle_discount_pct=request.bundle_discount_pct,
            segment=request.segment,
            validity_days=request.validity_days
        )
        
        return BundlePromotionResponse(**promotion)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bundle promotion error: {str(e)}")


@router.get("/all-promotions")
async def get_all_promotions():
    """
    Get all cached promotions
    
    Returns all promotions generated in current session.
    
    Example:
    ```
    GET /api/smart-promotions/all-promotions
    ```
    """
    try:
        service = get_promotion_service()
        promotions = await service.get_all_promotions()
        
        return {
            "count": len(promotions),
            "promotions": promotions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch error: {str(e)}")


@router.get("/summary", response_model=PromotionSummaryResponse)
async def get_promotion_summary():
    """
    Get promotion service summary
    
    Returns:
    - Service capabilities
    - Cached promotions count
    - Available promotion types
    
    Example:
    ```
    GET /api/smart-promotions/summary
    ```
    """
    try:
        service = get_promotion_service()
        summary = await service.get_promotion_summary()
        
        return PromotionSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")


@router.post("/clear-cache")
async def clear_cache():
    """
    Clear promotions cache
    
    Example:
    ```
    POST /api/smart-promotions/clear-cache
    ```
    """
    try:
        service = get_promotion_service()
        result = await service.clear_cache()
        
        return {
            "status": "success",
            "message": f"Cleared {result['cleared_items']} cached promotions",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Example:
    ```
    GET /api/smart-promotions/health
    ```
    """
    return {
        "status": "healthy",
        "service": "smart-promotions",
        "timestamp": datetime.now().isoformat()
    }
