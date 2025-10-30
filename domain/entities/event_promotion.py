"""
Domain Entities for Event-Based Promotion System
Định nghĩa các entity cho hệ thống khuyến mãi dựa trên sự kiện
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class EventType(Enum):
    """Loại sự kiện đặc biệt - Đầy đủ ngày lễ Việt Nam"""
    
    # ==== NGÀY LỄ QUỐC GIA VIỆT NAM ====
    TET = "Tết Nguyên Đán"
    HUNG_KING = "Giỗ Tổ Hùng Vương (10/3 Âm Lịch)"
    LIBERATION_DAY = "Ngày Giải Phóng Miền Nam (30/4)"
    LABOR_DAY = "Ngày Quốc Tế Lao Động (1/5)"
    NATIONAL_DAY = "Quốc Khánh (2/9)"
    
    # ==== NGÀY LỄ TRUYỀN THỐNG VIỆT NAM ====
    WANDERING_SOULS = "Tết Đoan Ngọ (5/5 Âm Lịch)"
    MID_AUTUMN = "Tết Trung Thu (15/8 Âm Lịch)"
    COLD_FOOD = "Tết Hàn Thực (3/3 Âm Lịch)"
    KITCHEN_GOD = "Ông Táo Chầu Trời (23/12 Âm Lịch)"
    
    # ==== NGÀY PHỤ NỮ ====
    INTERNATIONAL_WOMEN_DAY = "Ngày Quốc Tế Phụ Nữ (8/3)"
    VIETNAM_WOMEN_DAY = "Ngày Phụ Nữ Việt Nam (20/10)"
    
    # ==== NGÀY GIA ĐÌNH ====
    VALENTINE = "Ngày Lễ Tình Nhân (14/2)"
    WHITE_DAY = "Ngày Lễ Trắng (14/3)"
    MOTHER_DAY = "Ngày của Mẹ (Chủ Nhật thứ 2 tháng 5)"
    FATHER_DAY = "Ngày của Cha (Chủ Nhật thứ 3 tháng 6)"
    FAMILY_DAY = "Ngày Gia Đình Việt Nam (28/6)"
    CHILDREN_DAY = "Ngày Quốc Tế Thiếu Nhi (1/6)"
    MID_AUTUMN_CHILDREN = "Tết Trung Thu - Tết Thiếu Nhi"
    
    # ==== NGÀY LỄ TÔN GIÁO & QUỐC TẾ ====
    HALLOWEEN = "Halloween (31/10)"
    CHRISTMAS_EVE = "Đêm Giáng Sinh (24/12)"
    CHRISTMAS = "Lễ Giáng Sinh (25/12)"
    NEW_YEAR_EVE = "Đêm Giao Thừa Dương Lịch (31/12)"
    NEW_YEAR = "Tết Dương Lịch (1/1)"
    
    # ==== NGÀY LỄ NGHỀ NGHIỆP ====
    TEACHER_DAY = "Ngày Nhà Giáo Việt Nam (20/11)"
    DOCTOR_DAY = "Ngày Thầy Thuốc Việt Nam (27/2)"
    PRESS_DAY = "Ngày Báo Chí Việt Nam (21/6)"
    
    # ==== SỰ KIỆN MUA SẮM QUỐC TẾ ====
    BLACK_FRIDAY = "Black Friday"
    CYBER_MONDAY = "Cyber Monday"
    SINGLES_DAY = "Ngày Độc Thân (11/11)"
    DOUBLE_12 = "12/12 - Ngày Mua Sắm"
    
    # ==== SỰ KIỆN MUA SẮM VIỆT NAM ====
    ONLINE_FRIDAY = "Online Friday"
    SUPER_SALE_1111 = "Siêu Sale 11/11"
    HARUVEST = "Haruvest - Lễ Hội Mua Sắm"
    
    # ==== SỰ KIỆN ĐẶC BIỆT ====
    FLASH_SALE = "Flash Sale - Giờ Vàng"
    WEEKEND = "Cuối Tuần"
    PAYDAY = "Ngày Lương (27-30 hàng tháng)"
    MONTH_END_SALE = "Sale Cuối Tháng"
    BACK_TO_SCHOOL = "Khai Trường (Tháng 8-9)"
    GRADUATION_SEASON = "Mùa Tốt Nghiệp (Tháng 5-6)"
    SUMMER_SALE = "Sale Hè (Tháng 6-8)"
    YEAR_END_SALE = "Thanh Lý Cuối Năm"
    
    # ==== DỊP CỦA SHOP ====
    BIRTHDAY = "Sinh Nhật Shop"
    ANNIVERSARY = "Kỷ Niệm Thành Lập"
    GRAND_OPENING = "Khai Trương"
    CUSTOMER_APPRECIATION = "Tri Ân Khách Hàng"
    
    # ==== KHÁC ====
    NORMAL = "Ngày Thường"


class ProductStatus(Enum):
    """Trạng thái sản phẩm"""
    BEST_SELLER = "BEST_SELLER"  # Bán chạy
    SLOW_MOVING = "SLOW_MOVING"  # Bán chậm
    NEW_PRODUCT = "NEW_PRODUCT"  # Sản phẩm mới
    SEASONAL = "SEASONAL"  # Theo mùa
    COMBO_POTENTIAL = "COMBO_POTENTIAL"  # Tiềm năng combo
    NORMAL = "NORMAL"  # Bình thường


class PromotionStrategy(Enum):
    """Chiến lược khuyến mãi"""
    CLEARANCE = "CLEARANCE"  # Thanh lý hàng tồn
    BOOST_SALES = "BOOST_SALES"  # Đẩy doanh số
    COMBO_DEAL = "COMBO_DEAL"  # Combo ưu đãi
    EVENT_SPECIAL = "EVENT_SPECIAL"  # Đặc biệt sự kiện
    LOYALTY_REWARD = "LOYALTY_REWARD"  # Thưởng khách trung thành
    NEW_CUSTOMER = "NEW_CUSTOMER"  # Thu hút khách mới
    FLASH_DEAL = "FLASH_DEAL"  # Giảm giá nhanh


@dataclass
class ProductAnalysis:
    """Kết quả phân tích sản phẩm"""
    product_id: str
    product_name: str
    current_price: float
    avg_monthly_sales: float  # Doanh số trung bình/tháng
    total_sold: int  # Tổng số lượng bán
    revenue_contribution: float  # % đóng góp doanh thu
    stock_level: int  # Mức tồn kho
    avg_rating: float  # Đánh giá trung bình
    status: ProductStatus
    recommended_discount: float  # % khuyến mãi đề xuất
    reason: str  # Lý do đề xuất


@dataclass
class ComboSuggestion:
    """Gợi ý combo sản phẩm"""
    product_1_id: str
    product_1_name: str
    product_1_price: float
    product_2_id: str
    product_2_name: str
    product_2_price: float
    frequency_together: int  # Số lần mua cùng nhau
    confidence: float  # Độ tin cậy (0-1)
    recommended_bundle_discount: float  # % giảm giá combo


@dataclass
class EventInfo:
    """Thông tin sự kiện"""
    event_type: EventType
    event_date: datetime
    days_until_event: int
    is_active: bool  # Đang trong thời gian sự kiện
    duration_days: int  # Thời gian diễn ra sự kiện
    recommended_discount_range: str  # Format: "min%-max%" (e.g. "10-20")
    target_categories: List[str]  # Danh mục phù hợp


@dataclass
class PromotionRecommendation:
    """Đề xuất chương trình khuyến mãi"""
    promotion_id: str
    promotion_name: str
    description: str
    strategy: PromotionStrategy
    event_info: Optional[EventInfo]
    
    # Sản phẩm áp dụng
    target_products: List[ProductAnalysis]
    combo_suggestions: List[ComboSuggestion]
    
    # Chi tiết khuyến mãi
    discount_type: str  # "PERCENTAGE" | "FIXED_AMOUNT" | "BUNDLE"
    discount_value: float
    min_order_value: Optional[float]
    max_discount_amount: Optional[float]
    
    # Thời gian
    start_date: datetime
    end_date: datetime
    duration_days: int
    
    # Dự đoán hiệu quả
    estimated_revenue_impact: float  # Dự kiến tăng/giảm doanh thu (%)
    estimated_order_increase: int  # Dự kiến tăng đơn hàng
    risk_level: str  # "LOW" | "MEDIUM" | "HIGH"
    
    # Mục tiêu
    primary_goal: str  # "REVENUE" | "VOLUME" | "LOYALTY" | "CLEARANCE"
    target_customer_type: str  # "ALL" | "NEW" | "REGISTERED"
    
    created_at: datetime


@dataclass
class PromotionPerformance:
    """Đánh giá hiệu quả khuyến mãi"""
    promotion_id: str
    actual_revenue: float
    actual_orders: int
    actual_discount_given: float
    roi: float  # Return on Investment
    customer_satisfaction: float
    repeat_purchase_rate: float
