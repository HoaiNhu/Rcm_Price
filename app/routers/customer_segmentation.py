"""
Customer Segmentation API Router
Provides REST endpoints for RFM-based customer segmentation
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from application.services.customer_segmentation_service import (
    CustomerSegmentationService,
    create_segmentation_service
)
from infrastructure.db.mongodb_access import MongoDBDataAccess

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/customer-segmentation",
    tags=["customer-segmentation"],
    responses={404: {"description": "Not found"}}
)


# ========================= Pydantic Models =========================

class SegmentationRequest(BaseModel):
    """Request body for segmentation endpoint"""
    reference_date: Optional[datetime] = Field(
        default=None,
        description="Reference date for recency calculation (default: today)"
    )
    force_refresh: bool = Field(
        default=False,
        description="Force refresh cached results"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "reference_date": "2024-12-27T00:00:00",
                "force_refresh": False
            }
        }


class SegmentationResponse(BaseModel):
    """Response for segmentation endpoint"""
    total_customers: int
    total_segments: int
    segments: dict
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_customers": 100,
                "total_segments": 5,
                "segments": {
                    "user_001": "VIP",
                    "user_002": "REGULAR"
                },
                "message": "Successfully segmented 100 customers"
            }
        }


class CustomerSegmentResponse(BaseModel):
    """Response for single customer segment"""
    user_id: str
    segment: str
    description: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "segment": "VIP",
                "description": "Top 20% customers generating 80% revenue"
            }
        }


class CustomerDetailsResponse(BaseModel):
    """Detailed customer information"""
    user_id: str
    segment: str
    recency: float = Field(description="Days since last purchase")
    frequency: float = Field(description="Number of purchases")
    monetary: float = Field(description="Total spending")
    avg_order_value: float
    rfm_score: int
    r_score: int
    f_score: int
    m_score: int
    recommendations: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "segment": "VIP",
                "recency": 15.5,
                "frequency": 25.0,
                "monetary": 5000000.0,
                "avg_order_value": 200000.0,
                "rfm_score": 15,
                "r_score": 5,
                "f_score": 5,
                "m_score": 5,
                "recommendations": [
                    "Maintain premium service quality",
                    "Offer exclusive early access to new products"
                ]
            }
        }


class SegmentReportRow(BaseModel):
    """Single row in segment report"""
    segment: str
    description: str
    customer_count: int
    customer_percentage: float
    total_revenue: float
    revenue_percentage: float
    avg_recency_days: float
    avg_frequency: float
    avg_monetary: float
    avg_order_value: float
    avg_rfm_score: float
    price_strategy: str


class SummaryStatistics(BaseModel):
    """Summary statistics for all segments"""
    total_customers: int
    total_revenue: float
    total_segments: int
    top_segment: str
    top_segment_revenue_pct: float
    avg_rfm_score: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_customers": 100,
                "total_revenue": 10000000.0,
                "total_segments": 5,
                "top_segment": "VIP",
                "top_segment_revenue_pct": 75.5,
                "avg_rfm_score": 8.5
            }
        }


class ActionRecommendations(BaseModel):
    """Action recommendations for a segment"""
    segment: str
    description: str
    marketing_actions: List[str]
    pricing_actions: List[str]
    retention_actions: List[str]
    priority: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "segment": "VIP",
                "description": "Top customers",
                "marketing_actions": ["Exclusive previews", "VIP events"],
                "pricing_actions": ["Premium pricing", "Bundle deals"],
                "retention_actions": ["Loyalty rewards", "Personal service"],
                "priority": "HIGH"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    model_trained: bool
    cache_valid: bool
    timestamp: datetime


# ========================= Dependency =========================

async def get_segmentation_service() -> CustomerSegmentationService:
    """Dependency to get CustomerSegmentationService instance"""
    try:
        mongodb_access = MongoDBDataAccess(use_async=False)
        return create_segmentation_service(mongodb_access)
    except Exception as e:
        logger.error(f"❌ Failed to create segmentation service: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize segmentation service: {str(e)}"
        )


# ========================= Endpoints =========================

@router.post("/segment", response_model=SegmentationResponse)
async def segment_customers(
    request: SegmentationRequest,
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Phân khúc tất cả khách hàng dựa trên RFM analysis
    
    **Algorithm:**
    1. Fetch all orders and users from MongoDB
    2. Calculate RFM scores (Recency, Frequency, Monetary)
    3. Perform K-Means clustering (4 clusters)
    4. Map clusters to business segments (VIP, REGULAR, etc.)
    5. Cache results for 24h
    
    **Segments:**
    - **VIP**: Top 20% customers, 80% revenue
    - **REGULAR**: Frequent buyers, medium spend
    - **OCCASIONAL**: Infrequent buyers
    - **NEW**: Recent first-time buyers
    - **AT_RISK**: Previously good customers, high recency
    - **LOST**: No purchases in 180+ days
    
    **Returns:**
    - Dictionary mapping user_id → segment_name
    - Total customer and segment counts
    """
    try:
        logger.info(f"📊 Segmentation request: force_refresh={request.force_refresh}")
        
        segments = await service.segment_all_customers(
            reference_date=request.reference_date,
            force_refresh=request.force_refresh
        )
        
        if not segments:
            raise HTTPException(
                status_code=404,
                detail="No customers found for segmentation"
            )
        
        # Get unique segments
        unique_segments = set(segments.values())
        
        return SegmentationResponse(
            total_customers=len(segments),
            total_segments=len(unique_segments),
            segments=segments,
            message=f"Successfully segmented {len(segments)} customers into {len(unique_segments)} segments"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Segmentation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Segmentation failed: {str(e)}"
        )


@router.get("/segment/{user_id}", response_model=CustomerSegmentResponse)
async def get_customer_segment(
    user_id: str,
    auto_segment: bool = Query(True, description="Auto-segment if no cached data"),
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Lấy segment của một khách hàng cụ thể
    
    **Parameters:**
    - **user_id**: Customer ID
    - **auto_segment**: Auto-run segmentation if no cached data (default: true)
    
    **Returns:**
    - Customer's segment name
    - Segment description
    """
    try:
        segment = await service.get_customer_segment(user_id, auto_segment)
        
        if not segment:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {user_id} not found in segmentation"
            )
        
        # Get segment definition
        segment_def = service.segmentation_model.segment_definitions.get(
            segment,
            {"description": "Unknown segment"}
        )
        
        return CustomerSegmentResponse(
            user_id=user_id,
            segment=segment,
            description=segment_def.get('description', 'N/A')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get customer segment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer segment: {str(e)}"
        )


@router.get("/customers/{segment}", response_model=List[str])
async def get_segment_customers(
    segment: str,
    auto_segment: bool = Query(True, description="Auto-segment if no cached data"),
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Lấy danh sách khách hàng trong một segment
    
    **Parameters:**
    - **segment**: Segment name (VIP, REGULAR, OCCASIONAL, NEW, AT_RISK, LOST)
    - **auto_segment**: Auto-run segmentation if no cached data (default: true)
    
    **Returns:**
    - List of customer IDs in the segment
    """
    try:
        # Validate segment name
        valid_segments = ['VIP', 'REGULAR', 'OCCASIONAL', 'NEW', 'AT_RISK', 'LOST']
        if segment not in valid_segments:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid segment. Must be one of: {', '.join(valid_segments)}"
            )
        
        customers = await service.get_segment_customers(segment, auto_segment)
        
        if not customers:
            logger.warning(f"⚠️ No customers found in segment {segment}")
            return []
        
        return customers
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get segment customers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get segment customers: {str(e)}"
        )


@router.get("/report", response_model=List[SegmentReportRow])
async def get_segment_report(
    auto_segment: bool = Query(True, description="Auto-segment if no cached data"),
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Tạo báo cáo chi tiết về tất cả các segments
    
    **Returns comprehensive report including:**
    - Customer count and percentage per segment
    - Revenue breakdown per segment
    - Average RFM metrics per segment
    - Pricing strategy per segment
    
    **Sorted by revenue percentage (highest first)**
    """
    try:
        report_df = await service.get_segment_report(auto_segment)
        
        if report_df.empty:
            raise HTTPException(
                status_code=404,
                detail="No segment data available for reporting"
            )
        
        # Convert DataFrame to list of dicts
        report_data = report_df.to_dict(orient='records')
        
        return [SegmentReportRow(**row) for row in report_data]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate segment report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate segment report: {str(e)}"
        )


@router.get("/summary", response_model=SummaryStatistics)
async def get_summary_statistics(
    auto_segment: bool = Query(True, description="Auto-segment if no cached data"),
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Lấy thống kê tổng quan về segmentation
    
    **Returns:**
    - Total customer count
    - Total revenue across all segments
    - Number of segments
    - Top segment by revenue
    - Average RFM score
    """
    try:
        summary = await service.get_summary_statistics(auto_segment)
        
        if not summary:
            raise HTTPException(
                status_code=404,
                detail="No summary statistics available"
            )
        
        return SummaryStatistics(**summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get summary statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get summary statistics: {str(e)}"
        )


@router.get("/details/{user_id}", response_model=CustomerDetailsResponse)
async def get_customer_details(
    user_id: str,
    auto_segment: bool = Query(True, description="Auto-segment if no cached data"),
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Lấy thông tin chi tiết về một khách hàng
    
    **Includes:**
    - Complete RFM scores (Recency, Frequency, Monetary)
    - Individual R, F, M component scores (1-5 scale)
    - Combined RFM score (3-15 scale)
    - Segment assignment
    - Personalized recommendations
    
    **Parameters:**
    - **user_id**: Customer ID
    - **auto_segment**: Auto-run segmentation if no cached data (default: true)
    """
    try:
        details = await service.get_customer_details(user_id, auto_segment)
        
        if not details:
            raise HTTPException(
                status_code=404,
                detail=f"No details found for customer {user_id}"
            )
        
        return CustomerDetailsResponse(**details)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get customer details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer details: {str(e)}"
        )


@router.get("/recommendations/{segment}", response_model=ActionRecommendations)
async def get_segment_recommendations(
    segment: str,
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Lấy khuyến nghị hành động cho một segment
    
    **Provides actionable recommendations for:**
    - Marketing campaigns
    - Pricing strategies
    - Retention programs
    
    **Parameters:**
    - **segment**: Segment name (VIP, REGULAR, OCCASIONAL, NEW, AT_RISK, LOST)
    """
    try:
        # Validate segment name
        valid_segments = ['VIP', 'REGULAR', 'OCCASIONAL', 'NEW', 'AT_RISK', 'LOST']
        if segment not in valid_segments:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid segment. Must be one of: {', '.join(valid_segments)}"
            )
        
        recommendations = await service.recommend_actions(segment)
        
        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail=f"No recommendations available for segment {segment}"
            )
        
        return ActionRecommendations(**recommendations)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/vip-customers", response_model=List[CustomerDetailsResponse])
async def get_vip_customers(
    auto_segment: bool = Query(True, description="Auto-segment if no cached data"),
    limit: int = Query(50, description="Maximum number of VIP customers to return"),
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Lấy danh sách khách hàng VIP với thông tin chi tiết
    
    **VIP Criteria:**
    - Low recency (< 30 days)
    - High frequency (top 25% percentile)
    - High monetary value
    - Consistent purchasing behavior
    
    **Returns:**
    - List sorted by total spending (highest first)
    - Limited to specified number of customers
    """
    try:
        vip_customers = await service.get_vip_customers(auto_segment)
        
        if not vip_customers:
            logger.info("✅ No VIP customers found")
            return []
        
        # Limit results
        vip_customers = vip_customers[:limit]
        
        return [CustomerDetailsResponse(**customer) for customer in vip_customers]
        
    except Exception as e:
        logger.error(f"❌ Failed to get VIP customers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get VIP customers: {str(e)}"
        )


@router.get("/at-risk-customers", response_model=List[CustomerDetailsResponse])
async def get_at_risk_customers(
    auto_segment: bool = Query(True, description="Auto-segment if no cached data"),
    limit: int = Query(50, description="Maximum number of at-risk customers to return"),
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Lấy danh sách khách hàng AT_RISK với thông tin chi tiết
    
    **AT_RISK Criteria:**
    - High recency (> 90 days but < 180 days)
    - Previously good frequency (top 60% percentile)
    - Risk of churning to LOST segment
    
    **Returns:**
    - List sorted by recency (most urgent first)
    - Limited to specified number of customers
    
    **Use case:**
    - Target for win-back campaigns
    - Offer special promotions
    - Re-engagement emails
    """
    try:
        at_risk_customers = await service.get_at_risk_customers(auto_segment)
        
        if not at_risk_customers:
            logger.info("✅ No at-risk customers found")
            return []
        
        # Limit results
        at_risk_customers = at_risk_customers[:limit]
        
        return [CustomerDetailsResponse(**customer) for customer in at_risk_customers]
        
    except Exception as e:
        logger.error(f"❌ Failed to get at-risk customers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get at-risk customers: {str(e)}"
        )


@router.post("/clear-cache")
async def clear_cache(
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Xóa cache để force refresh segmentation
    
    **Use case:**
    - After bulk data updates
    - Testing with new data
    - Manual refresh needed
    
    **Next segmentation call will re-calculate from database**
    """
    try:
        service.clear_cache()
        
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "next_action": "Segmentation will be re-calculated on next request"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to clear cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    service: CustomerSegmentationService = Depends(get_segmentation_service)
):
    """
    Health check endpoint
    
    **Returns:**
    - Service status
    - Model training status
    - Cache validity
    - Current timestamp
    """
    try:
        return HealthResponse(
            status="healthy",
            service="customer-segmentation",
            model_trained=service.segmentation_model.is_trained,
            cache_valid=service._is_cache_valid(),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )
