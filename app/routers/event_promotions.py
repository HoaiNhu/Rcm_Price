"""
Event-Based Promotion Router
API endpoints cho hệ thống tạo khuyến mãi tự động dựa trên sự kiện
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import math

from application.services.event_promotion_service import get_event_promotion_service
from domain.entities.event_promotion import EventType
from utils.response_cache import get_response_cache
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Utility Functions
# ============================================================================

def sanitize_float(value: float, default: float = 0.0) -> float:
    """
    Sanitize float values to prevent NaN and Infinity in JSON response
    
    Args:
        value: Float value to sanitize
        default: Default value if input is NaN or Infinity
        
    Returns:
        Valid float value or default
    """
    if value is None or math.isnan(value) or math.isinf(value):
        return default
    return value


router = APIRouter(
    prefix="/api/event-promotions",
    tags=["event-promotions"]
)


# ============================================================================
# Pydantic Models for API
# ============================================================================

class ProductAnalysisResponse(BaseModel):
    """Response model for product analysis"""
    product_id: str
    product_name: str
    current_price: float
    avg_monthly_sales: float
    total_sold: int
    revenue_contribution: float
    stock_level: int
    avg_rating: float
    status: str
    recommended_discount: float
    reason: str


class ComboSuggestionResponse(BaseModel):
    """Response model for combo suggestion"""
    product_1_id: str
    product_1_name: str
    product_1_price: float
    product_2_id: str
    product_2_name: str
    product_2_price: float
    frequency_together: int
    confidence: float
    recommended_bundle_discount: float


class EventInfoResponse(BaseModel):
    """Response model for event info"""
    event_type: str
    event_date: str
    days_until_event: int
    is_active: bool
    duration_days: int
    recommended_discount_range: str
    target_categories: List[str]


class PromotionRecommendationResponse(BaseModel):
    """Response model for promotion recommendation"""
    promotion_id: str
    promotion_name: str
    description: str
    strategy: str
    event_info: Optional[EventInfoResponse]
    
    target_products: List[ProductAnalysisResponse]
    combo_suggestions: List[ComboSuggestionResponse]
    
    discount_type: str
    discount_value: float
    min_order_value: Optional[float]
    max_discount_amount: Optional[float]
    
    start_date: str
    end_date: str
    duration_days: int
    
    estimated_revenue_impact: float
    estimated_order_increase: int
    risk_level: str
    
    primary_goal: str
    target_customer_type: str
    created_at: str


class PromotionFocusEnum(str, Enum):
    """Promotion focus types"""
    REVENUE = "revenue"
    CLEARANCE = "clearance"
    BALANCED = "balanced"


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/analyze-products", response_model=List[ProductAnalysisResponse])
async def analyze_product_performance(
    analysis_period_days: int = Query(30, ge=7, le=90, description="Số ngày phân tích (7-90)")
):
    """
    Phân tích hiệu suất sản phẩm
    
    Trả về danh sách sản phẩm với:
    - Trạng thái: BEST_SELLER, SLOW_MOVING, NORMAL, etc.
    - Doanh số trung bình hàng tháng
    - % đóng góp vào doanh thu
    - Mức giảm giá đề xuất
    - Lý do đề xuất
    
    **Ví dụ:**
    ```
    GET /api/event-promotions/analyze-products?analysis_period_days=30
    ```
    
    **Use cases:**
    - Xác định sản phẩm nào cần đẩy mạnh doanh số
    - Sản phẩm nào đang bán chạy
    - Sản phẩm nào có tiềm năng combo
    """
    try:
        service = get_event_promotion_service()
        analyses = await service.analyze_product_performance(
            analysis_period_days=analysis_period_days
        )
        
        # Convert to response model
        response = []
        for analysis in analyses:
            response.append(ProductAnalysisResponse(
                product_id=analysis.product_id,
                product_name=analysis.product_name,
                current_price=sanitize_float(analysis.current_price),
                avg_monthly_sales=sanitize_float(analysis.avg_monthly_sales),
                total_sold=analysis.total_sold,
                revenue_contribution=sanitize_float(analysis.revenue_contribution),
                stock_level=analysis.stock_level,
                avg_rating=sanitize_float(analysis.avg_rating),
                status=analysis.status.value,
                recommended_discount=sanitize_float(analysis.recommended_discount),
                reason=analysis.reason
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing products: {str(e)}")


@router.get("/discover-combos", response_model=List[ComboSuggestionResponse])
async def discover_product_combos(
    min_support: float = Query(0.05, ge=0.01, le=0.5, description="Ngưỡng support tối thiểu"),
    min_confidence: float = Query(0.3, ge=0.1, le=0.9, description="Ngưỡng confidence tối thiểu")
):
    """
    Phát hiện combo sản phẩm tiềm năng
    
    Sử dụng Market Basket Analysis để tìm các sản phẩm thường được mua cùng nhau.
    
    **Ví dụ:**
    ```
    GET /api/event-promotions/discover-combos?min_support=0.05&min_confidence=0.3
    ```
    
    **Kết quả:**
    - Cặp sản phẩm A + B
    - Tần suất mua cùng nhau
    - Độ tin cậy
    - Mức giảm giá combo đề xuất
    
    **Use cases:**
    - Tạo combo deals
    - Cross-selling
    - Tăng giá trị đơn hàng trung bình
    """
    try:
        service = get_event_promotion_service()
        combos = await service.discover_product_combos(
            min_support=min_support,
            min_confidence=min_confidence
        )
        
        # Convert to response model
        response = []
        for combo in combos:
            response.append(ComboSuggestionResponse(
                product_1_id=combo.product_1_id,
                product_1_name=combo.product_1_name,
                product_1_price=sanitize_float(combo.product_1_price),
                product_2_id=combo.product_2_id,
                product_2_name=combo.product_2_name,
                product_2_price=sanitize_float(combo.product_2_price),
                frequency_together=combo.frequency_together,
                confidence=sanitize_float(combo.confidence),
                recommended_bundle_discount=sanitize_float(combo.recommended_bundle_discount)
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error discovering combos: {str(e)}")


@router.get("/upcoming-events", response_model=List[EventInfoResponse])
async def get_upcoming_events(
    days_ahead: int = Query(60, ge=7, le=365, description="Số ngày nhìn về tương lai")
):
    """
    Lấy danh sách sự kiện sắp tới
    
    **Sự kiện được phát hiện:**
    - Tết Nguyên Đán
    - Ngày Phụ Nữ (8/3, 20/10)
    - Valentine
    - Ngày của Mẹ/Bố
    - Trung Thu
    - Giáng Sinh
    - Năm Mới
    - Cuối tuần
    
    **Ví dụ:**
    ```
    GET /api/event-promotions/upcoming-events?days_ahead=60
    ```
    
    **Use cases:**
    - Lên kế hoạch khuyến mãi trước
    - Chuẩn bị hàng hóa cho sự kiện
    - Tối ưu thời gian chạy promotion
    """
    try:
        service = get_event_promotion_service()
        events = service.event_detector.get_upcoming_events(
            reference_date=datetime.now(),
            days_ahead=days_ahead
        )
        
        # Convert to response model
        response = []
        for event in events:
            response.append(EventInfoResponse(
                event_type=event.event_type.value,
                event_date=event.event_date.isoformat(),
                days_until_event=event.days_until_event,
                is_active=event.is_active,
                duration_days=event.duration_days,
                recommended_discount_range=event.recommended_discount_range,
                target_categories=event.target_categories
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting events: {str(e)}")


@router.post("/generate-event-promotion", response_model=List[PromotionRecommendationResponse])
async def generate_event_based_promotion(
    event_type: Optional[str] = Query(None, description="Loại sự kiện (để trống = tất cả)"),
    days_ahead: int = Query(30, ge=3, le=365, description="Số ngày nhìn về tương lai")
):
    """
    Tạo đề xuất khuyến mãi dựa trên sự kiện sắp tới
    
    **Quy trình tự động:**
    1. Phát hiện sự kiện sắp tới
    2. Phân tích sản phẩm (bán chạy/chậm)
    3. Tìm combo tiềm năng
    4. Tạo chương trình khuyến mãi phù hợp
    
    **Ví dụ:**
    ```
    POST /api/event-promotions/generate-event-promotion?days_ahead=60
    ```
    
    **Hoặc cho sự kiện cụ thể:**
    ```
    POST /api/event-promotions/generate-event-promotion?event_type=Tết Nguyên Đán
    ```
    
    **Kết quả bao gồm:**
    - Tên chương trình
    - Sản phẩm áp dụng
    - Mức giảm giá
    - Thời gian bắt đầu/kết thúc
    - Dự đoán tác động doanh thu
    - Mức độ rủi ro
    """
    try:
        # 🔥 CHECK CACHE FIRST
        response_cache = get_response_cache()
        cache_key_params = {"event_type": event_type or "ALL", "days_ahead": days_ahead}
        
        cached_response = await response_cache.get("event_promotion", **cache_key_params)
        if cached_response:
            logger.info(f"✅ [CACHE HIT] event_type={event_type}, days_ahead={days_ahead}")
            return cached_response
        
        logger.info(f"🔍 [CACHE MISS] Generating new promotion...")
        
        service = get_event_promotion_service()
        
        # Parse event type if provided
        event_type_enum = None
        if event_type:
            try:
                event_type_enum = EventType(event_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid event_type. Must be one of: {[e.value for e in EventType]}"
                )
        
        promotions = await service.generate_event_promotion(
            event_type=event_type_enum,
            days_ahead=days_ahead
        )
        
        # Convert to response model
        response = []
        for promo in promotions:
            # Convert event info
            event_info_resp = None
            if promo.event_info:
                event_info_resp = EventInfoResponse(
                    event_type=promo.event_info.event_type.value,
                    event_date=promo.event_info.event_date.isoformat(),
                    days_until_event=promo.event_info.days_until_event,
                    is_active=promo.event_info.is_active,
                    duration_days=promo.event_info.duration_days,
                    recommended_discount_range=promo.event_info.recommended_discount_range,
                    target_categories=promo.event_info.target_categories
                )
            
            # Convert products
            products_resp = [
                ProductAnalysisResponse(
                    product_id=p.product_id,
                    product_name=p.product_name,
                    current_price=sanitize_float(p.current_price),
                    avg_monthly_sales=sanitize_float(p.avg_monthly_sales),
                    total_sold=p.total_sold,
                    revenue_contribution=sanitize_float(p.revenue_contribution),
                    stock_level=p.stock_level,
                    avg_rating=sanitize_float(p.avg_rating),
                    status=p.status.value,
                    recommended_discount=sanitize_float(p.recommended_discount),
                    reason=p.reason
                )
                for p in promo.target_products
            ]
            
            # Convert combos
            combos_resp = [
                ComboSuggestionResponse(
                    product_1_id=c.product_1_id,
                    product_1_name=c.product_1_name,
                    product_1_price=sanitize_float(c.product_1_price),
                    product_2_id=c.product_2_id,
                    product_2_name=c.product_2_name,
                    product_2_price=sanitize_float(c.product_2_price),
                    frequency_together=c.frequency_together,
                    confidence=sanitize_float(c.confidence),
                    recommended_bundle_discount=sanitize_float(c.recommended_bundle_discount)
                )
                for c in promo.combo_suggestions
            ]
            
            response.append(PromotionRecommendationResponse(
                promotion_id=promo.promotion_id,
                promotion_name=promo.promotion_name,
                description=promo.description,
                strategy=promo.strategy.value,
                event_info=event_info_resp,
                target_products=products_resp,
                combo_suggestions=combos_resp,
                discount_type=promo.discount_type,
                discount_value=sanitize_float(promo.discount_value),
                min_order_value=sanitize_float(promo.min_order_value) if promo.min_order_value else None,
                max_discount_amount=sanitize_float(promo.max_discount_amount) if promo.max_discount_amount else None,
                start_date=promo.start_date.isoformat(),
                end_date=promo.end_date.isoformat(),
                duration_days=promo.duration_days,
                estimated_revenue_impact=sanitize_float(promo.estimated_revenue_impact),
                estimated_order_increase=promo.estimated_order_increase,
                risk_level=promo.risk_level,
                primary_goal=promo.primary_goal,
                target_customer_type=promo.target_customer_type,
                created_at=promo.created_at.isoformat()
            ))
        
        # Save to response cache
        await response_cache.set("event_promotion", response, expire=3600, **cache_key_params)
        logger.info(f"💾 [CACHE SAVED] Event promotion for {cache_key_params}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating promotion: {str(e)}")


@router.post("/generate-smart-promotion", response_model=PromotionRecommendationResponse)
async def generate_smart_promotion(
    focus: PromotionFocusEnum = Query(
        PromotionFocusEnum.BALANCED,
        description="Focus của promotion: revenue (tăng doanh thu), clearance (thanh lý), balanced (cân bằng)"
    )
):
    """
    Tạo khuyến mãi thông minh không phụ thuộc sự kiện
    
    **3 chiến lược:**
    
    1. **Revenue Focus** (`focus=revenue`):
       - Tập trung vào sản phẩm đóng góp doanh thu cao
       - Giảm giá vừa phải (15%)
       - Mục tiêu: Tối đa hóa doanh thu
    
    2. **Clearance Focus** (`focus=clearance`):
       - Tập trung vào sản phẩm bán chậm
       - Giảm giá mạnh (20%)
       - Mục tiêu: Thanh lý tồn kho
    
    3. **Balanced** (`focus=balanced`):
       - Mix sản phẩm bán chạy + bán chậm
       - Giảm giá cân bằng (12%)
       - Mục tiêu: Tăng số lượng đơn hàng
    
    **Ví dụ:**
    ```
    POST /api/event-promotions/generate-smart-promotion?focus=balanced
    ```
    
    **Use cases:**
    - Tạo khuyến mãi nhanh không cần chờ sự kiện
    - Điều chỉnh chiến lược theo mục tiêu kinh doanh
    - Phản ứng nhanh với tình hình thị trường
    """
    try:
        service = get_event_promotion_service()
        promo = await service.generate_smart_promotion(focus=focus.value)
        
        # Convert event info
        event_info_resp = None
        if promo.event_info:
            event_info_resp = EventInfoResponse(
                event_type=promo.event_info.event_type.value,
                event_date=promo.event_info.event_date.isoformat(),
                days_until_event=promo.event_info.days_until_event,
                is_active=promo.event_info.is_active,
                duration_days=promo.event_info.duration_days,
                recommended_discount_range=promo.event_info.recommended_discount_range,
                target_categories=promo.event_info.target_categories
            )
        
        # Convert products
        products_resp = [
            ProductAnalysisResponse(
                product_id=p.product_id,
                product_name=p.product_name,
                current_price=sanitize_float(p.current_price),
                avg_monthly_sales=sanitize_float(p.avg_monthly_sales),
                total_sold=p.total_sold,
                revenue_contribution=sanitize_float(p.revenue_contribution),
                stock_level=p.stock_level,
                avg_rating=sanitize_float(p.avg_rating),
                status=p.status.value,
                recommended_discount=sanitize_float(p.recommended_discount),
                reason=p.reason
            )
            for p in promo.target_products
        ]
        
        # Convert combos
        combos_resp = [
            ComboSuggestionResponse(
                product_1_id=c.product_1_id,
                product_1_name=c.product_1_name,
                product_1_price=sanitize_float(c.product_1_price),
                product_2_id=c.product_2_id,
                product_2_name=c.product_2_name,
                product_2_price=sanitize_float(c.product_2_price),
                frequency_together=c.frequency_together,
                confidence=sanitize_float(c.confidence),
                recommended_bundle_discount=sanitize_float(c.recommended_bundle_discount)
            )
            for c in promo.combo_suggestions
        ]
        
        return PromotionRecommendationResponse(
            promotion_id=promo.promotion_id,
            promotion_name=promo.promotion_name,
            description=promo.description,
            strategy=promo.strategy.value,
            event_info=event_info_resp,
            target_products=products_resp,
            combo_suggestions=combos_resp,
            discount_type=promo.discount_type,
            discount_value=sanitize_float(promo.discount_value),
            min_order_value=sanitize_float(promo.min_order_value) if promo.min_order_value else None,
            max_discount_amount=sanitize_float(promo.max_discount_amount) if promo.max_discount_amount else None,
            start_date=promo.start_date.isoformat(),
            end_date=promo.end_date.isoformat(),
            duration_days=promo.duration_days,
            estimated_revenue_impact=sanitize_float(promo.estimated_revenue_impact),
            estimated_order_increase=promo.estimated_order_increase,
            risk_level=promo.risk_level,
            primary_goal=promo.primary_goal,
            target_customer_type=promo.target_customer_type,
            created_at=promo.created_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating smart promotion: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    **Ví dụ:**
    ```
    GET /api/event-promotions/health
    ```
    """
    return {
        "status": "healthy",
        "service": "event-promotions",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Product Performance Analysis",
            "Combo Discovery",
            "Event Detection",
            "AI Promotion Generation"
        ]
    }
