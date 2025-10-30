"""
Event Detector - Phát hiện sự kiện đặc biệt trong năm
Tự động xác định các ngày lễ, sự kiện đặc biệt để tạo khuyến mãi phù hợp
"""

from datetime import datetime, timedelta
from typing import List, Optional
from domain.entities.event_promotion import EventType, EventInfo
import calendar


class EventDetector:
    """Phát hiện và phân tích sự kiện đặc biệt - Đầy đủ ngày lễ Việt Nam"""
    
    # ========================================================================
    # NGÀY LỄ CỐ ĐỊNH THEO LỊCH DƯƠNG (FIXED SOLAR CALENDAR EVENTS)
    # ========================================================================
    FIXED_EVENTS = {
        # === Tháng 1 ===
        EventType.NEW_YEAR: {"month": 1, "day": 1, "duration": 3},
        
        # === Tháng 2 ===
        EventType.VALENTINE: {"month": 2, "day": 14, "duration": 1},
        EventType.DOCTOR_DAY: {"month": 2, "day": 27, "duration": 1},
        
        # === Tháng 3 ===
        EventType.INTERNATIONAL_WOMEN_DAY: {"month": 3, "day": 8, "duration": 1},
        EventType.WHITE_DAY: {"month": 3, "day": 14, "duration": 1},
        
        # === Tháng 4 ===
        EventType.LIBERATION_DAY: {"month": 4, "day": 30, "duration": 1},
        
        # === Tháng 5 ===
        EventType.LABOR_DAY: {"month": 5, "day": 1, "duration": 1},
        # MOTHER_DAY: Chủ nhật thứ 2 tháng 5 - tính động
        
        # === Tháng 6 ===
        EventType.CHILDREN_DAY: {"month": 6, "day": 1, "duration": 1},
        # FATHER_DAY: Chủ nhật thứ 3 tháng 6 - tính động
        EventType.PRESS_DAY: {"month": 6, "day": 21, "duration": 1},
        EventType.FAMILY_DAY: {"month": 6, "day": 28, "duration": 1},
        
        # === Tháng 9 ===
        EventType.NATIONAL_DAY: {"month": 9, "day": 2, "duration": 1},
        
        # === Tháng 10 ===
        EventType.VIETNAM_WOMEN_DAY: {"month": 10, "day": 20, "duration": 1},
        EventType.HALLOWEEN: {"month": 10, "day": 31, "duration": 1},
        
        # === Tháng 11 ===
        EventType.SINGLES_DAY: {"month": 11, "day": 11, "duration": 1},
        EventType.TEACHER_DAY: {"month": 11, "day": 20, "duration": 1},
        # BLACK_FRIDAY: Thứ 6 thứ 4 sau Lễ Tạ Ơn (tính động)
        # CYBER_MONDAY: Thứ 2 sau Black Friday (tính động)
        
        # === Tháng 12 ===
        EventType.DOUBLE_12: {"month": 12, "day": 12, "duration": 1},
        EventType.CHRISTMAS_EVE: {"month": 12, "day": 24, "duration": 1},
        EventType.CHRISTMAS: {"month": 12, "day": 25, "duration": 3},
        EventType.NEW_YEAR_EVE: {"month": 12, "day": 31, "duration": 1},
    }
    
    # ========================================================================
    # SỰ KIỆN THEO LỊCH ÂM (LUNAR CALENDAR EVENTS)
    # ========================================================================
    LUNAR_EVENTS = {
        # === TẾT NGUYÊN ĐÁN (1/1 Âm) ===
        EventType.TET: {
            2025: {"month": 1, "day": 29, "duration": 7},   # Tết Ất Tỵ 2025
            2026: {"month": 2, "day": 17, "duration": 7},   # Tết Bính Ngọ 2026
            2027: {"month": 2, "day": 6, "duration": 7},    # Tết Đinh Mùi 2027
            2028: {"month": 1, "day": 26, "duration": 7},   # Tết Mậu Thân 2028
        },
        
        # === ÔNG TÁO (23/12 Âm) ===
        EventType.KITCHEN_GOD: {
            2025: {"month": 1, "day": 22, "duration": 1},   # 23/12 Âm năm 2024
            2026: {"month": 2, "day": 10, "duration": 1},   # 23/12 Âm năm 2025
            2027: {"month": 1, "day": 30, "duration": 1},   # 23/12 Âm năm 2026
            2028: {"month": 1, "day": 19, "duration": 1},   # 23/12 Âm năm 2027
        },
        
        # === TẾT HÀN THỰC (3/3 Âm) ===
        EventType.COLD_FOOD: {
            2025: {"month": 3, "day": 31, "duration": 1},
            2026: {"month": 4, "day": 20, "duration": 1},
            2027: {"month": 4, "day": 9, "duration": 1},
            2028: {"month": 3, "day": 28, "duration": 1},
        },
        
        # === GIỖ TỔ HÙNG VƯƠNG (10/3 Âm) ===
        EventType.HUNG_KING: {
            2025: {"month": 4, "day": 7, "duration": 1},
            2026: {"month": 4, "day": 27, "duration": 1},
            2027: {"month": 4, "day": 16, "duration": 1},
            2028: {"month": 4, "day": 5, "duration": 1},
        },
        
        # === TẾT ĐOAN NGỌ (5/5 Âm) ===
        EventType.WANDERING_SOULS: {
            2025: {"month": 5, "day": 31, "duration": 1},
            2026: {"month": 6, "day": 19, "duration": 1},
            2027: {"month": 6, "day": 9, "duration": 1},
            2028: {"month": 5, "day": 29, "duration": 1},
        },
        
        # === TẾT TRUNG THU (15/8 Âm) ===
        EventType.MID_AUTUMN: {
            2025: {"month": 9, "day": 7, "duration": 3},
            2026: {"month": 9, "day": 27, "duration": 3},
            2027: {"month": 9, "day": 16, "duration": 3},
            2028: {"month": 10, "day": 4, "duration": 3},
        },
    }
    
    # ========================================================================
    # MỨC GIẢM GIÁ ĐỀ XUẤT (RECOMMENDED DISCOUNT RANGES)
    # ========================================================================
    EVENT_DISCOUNT_RANGES = {
        # === Ngày Lễ Lớn ===
        EventType.TET: "20-40",
        EventType.CHRISTMAS: "15-30",
        EventType.NEW_YEAR: "15-30",
        EventType.MID_AUTUMN: "15-30",
        
        # === Ngày Lễ Quốc Gia ===
        EventType.HUNG_KING: "10-20",
        EventType.LIBERATION_DAY: "10-25",
        EventType.LABOR_DAY: "10-20",
        EventType.NATIONAL_DAY: "10-25",
        
        # === Ngày Phụ Nữ & Gia Đình ===
        EventType.INTERNATIONAL_WOMEN_DAY: "10-25",
        EventType.VIETNAM_WOMEN_DAY: "10-25",
        EventType.VALENTINE: "10-20",
        EventType.WHITE_DAY: "5-15",
        EventType.MOTHER_DAY: "10-20",
        EventType.FATHER_DAY: "10-20",
        EventType.FAMILY_DAY: "10-20",
        EventType.CHILDREN_DAY: "10-20",
        
        # === Ngày Lễ Truyền Thống ===
        EventType.KITCHEN_GOD: "5-15",
        EventType.COLD_FOOD: "5-10",
        EventType.WANDERING_SOULS: "5-15",
        
        # === Ngày Nghề Nghiệp ===
        EventType.TEACHER_DAY: "10-20",
        EventType.DOCTOR_DAY: "5-15",
        EventType.PRESS_DAY: "5-10",
        
        # === Sự Kiện Mua Sắm Lớn ===
        EventType.BLACK_FRIDAY: "30-50",
        EventType.CYBER_MONDAY: "25-45",
        EventType.SINGLES_DAY: "20-40",
        EventType.DOUBLE_12: "20-35",
        EventType.ONLINE_FRIDAY: "20-35",
        EventType.SUPER_SALE_1111: "25-40",
        
        # === Sự Kiện Đặc Biệt ===
        EventType.FLASH_SALE: "20-40",
        EventType.PAYDAY: "10-25",
        EventType.MONTH_END_SALE: "15-30",
        EventType.BACK_TO_SCHOOL: "10-25",
        EventType.GRADUATION_SEASON: "10-20",
        EventType.SUMMER_SALE: "15-30",
        EventType.YEAR_END_SALE: "25-50",
        
        # === Sự Kiện Shop ===
        EventType.BIRTHDAY: "20-35",
        EventType.ANNIVERSARY: "20-35",
        EventType.GRAND_OPENING: "25-40",
        EventType.CUSTOMER_APPRECIATION: "15-30",
        
        # === Khác ===
        EventType.WEEKEND: "5-15",
        EventType.HALLOWEEN: "15-25",
        EventType.CHRISTMAS_EVE: "10-20",
        EventType.NEW_YEAR_EVE: "15-25",
        EventType.NORMAL: "0-10",
    }
    
    # ========================================================================
    # DANH MỤC SẢN PHẨM PHÙ HỢP (TARGET CATEGORIES)
    # ========================================================================
    EVENT_CATEGORIES = {
        # === Tết & Ngày Lễ Lớn ===
        EventType.TET: ["Bánh Tết", "Bánh Kẹo", "Mứt", "Bánh Truyền Thống", "Combo Tết", "Quà Tặng"],
        EventType.KITCHEN_GOD: ["Bánh Kẹo", "Mứt", "Hoa Quả", "Cúng Kiến"],
        EventType.HUNG_KING: ["Bánh Chưng", "Bánh Dày", "Bánh Giầy", "Cúng Tổ"],
        EventType.MID_AUTUMN: ["Bánh Trung Thu", "Bánh Nướng", "Bánh Dẻo", "Combo Trung Thu", "Đèn Lồng"],
        
        # === Ngày Phụ Nữ & Gia Đình ===
        EventType.INTERNATIONAL_WOMEN_DAY: ["Bánh Kem", "Bánh Ngọt", "Quà Tặng", "Chocolate"],
        EventType.VIETNAM_WOMEN_DAY: ["Bánh Kem", "Bánh Ngọt", "Quà Tặng"],
        EventType.VALENTINE: ["Bánh Kem Tim", "Chocolate", "Quà Tặng", "Combo Valentine"],
        EventType.WHITE_DAY: ["Bánh Ngọt", "Kẹo", "Quà Tặng"],
        EventType.MOTHER_DAY: ["Bánh Kem", "Bánh Sinh Nhật", "Quà Tặng", "Hoa"],
        EventType.FATHER_DAY: ["Bánh Kem", "Bánh Mặn", "Quà Tặng"],
        EventType.FAMILY_DAY: ["Combo Gia Đình", "Bánh Kem Lớn", "Set Quà"],
        EventType.CHILDREN_DAY: ["Bánh Ngọt", "Kẹo", "Bánh Kem Hoạt Hình"],
        
        # === Ngày Lễ Tôn Giáo ===
        EventType.HALLOWEEN: ["Bánh Kem Halloween", "Bánh Cookie", "Kẹo", "Quà Hóa Trang"],
        EventType.CHRISTMAS: ["Bánh Kem Giáng Sinh", "Bánh Cookie", "Quà Giáng Sinh"],
        EventType.CHRISTMAS_EVE: ["Bánh Kem", "Bánh Ngọt", "Tiệc Nhẹ"],
        EventType.NEW_YEAR: ["Bánh Kem", "Bánh Kẹo", "Quà Năm Mới"],
        EventType.NEW_YEAR_EVE: ["Bánh Tiệc", "Snack", "Party Food"],
        
        # === Ngày Nghề Nghiệp ===
        EventType.TEACHER_DAY: ["Bánh Kem", "Quà Tặng", "Bánh Ngọt", "Hoa"],
        EventType.DOCTOR_DAY: ["Bánh Kem", "Quà Tặng"],
        
        # === Ngày Lễ Quốc Gia ===
        EventType.LIBERATION_DAY: ["Tất cả"],
        EventType.LABOR_DAY: ["Tất cả"],
        EventType.NATIONAL_DAY: ["Bánh Kem", "Combo Quốc Khánh"],
        
        # === Sự Kiện Mua Sắm ===
        EventType.BLACK_FRIDAY: ["Tất cả"],
        EventType.CYBER_MONDAY: ["Tất cả"],
        EventType.SINGLES_DAY: ["Tất cả"],
        EventType.DOUBLE_12: ["Tất cả"],
        EventType.ONLINE_FRIDAY: ["Tất cả"],
        EventType.SUPER_SALE_1111: ["Tất cả"],
        
        # === Sự Kiện Theo Mùa ===
        EventType.BACK_TO_SCHOOL: ["Bánh Kem", "Snack", "Bánh Ngọt"],
        EventType.GRADUATION_SEASON: ["Bánh Kem Tốt Nghiệp", "Quà Tặng"],
        EventType.SUMMER_SALE: ["Tất cả"],
        EventType.YEAR_END_SALE: ["Tất cả"],
        
        # === Khác ===
        EventType.FLASH_SALE: ["Tất cả"],
        EventType.WEEKEND: ["Tất cả"],
        EventType.PAYDAY: ["Tất cả"],
        EventType.MONTH_END_SALE: ["Tất cả"],
        EventType.BIRTHDAY: ["Tất cả"],
        EventType.ANNIVERSARY: ["Tất cả"],
        EventType.GRAND_OPENING: ["Tất cả"],
        EventType.CUSTOMER_APPRECIATION: ["Tất cả"],
        EventType.NORMAL: ["Tất cả"],
    }
    
    @staticmethod
    def get_upcoming_events(
        reference_date: Optional[datetime] = None,
        days_ahead: int = 60
    ) -> List[EventInfo]:
        """
        Lấy danh sách sự kiện sắp tới
        
        Args:
            reference_date: Ngày tham chiếu (mặc định là hôm nay)
            days_ahead: Số ngày nhìn về tương lai
            
        Returns:
            Danh sách EventInfo
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        events = []
        year = reference_date.year
        
        # Kiểm tra các sự kiện cố định
        for event_type, event_data in EventDetector.FIXED_EVENTS.items():
            event_date = datetime(year, event_data["month"], event_data["day"])
            
            # Nếu sự kiện năm nay đã qua, xem sự kiện năm sau
            if event_date < reference_date:
                event_date = datetime(year + 1, event_data["month"], event_data["day"])
            
            days_until = (event_date - reference_date).days
            
            if 0 <= days_until <= days_ahead:
                event_info = EventDetector._create_event_info(
                    event_type, event_date, reference_date, event_data["duration"]
                )
                events.append(event_info)
        
        # === Thêm MOTHER_DAY (Chủ nhật thứ 2 tháng 5) ===
        mother_day = EventDetector._get_nth_sunday_of_month(year, 5, 2)
        if mother_day:
            if mother_day < reference_date:
                mother_day = EventDetector._get_nth_sunday_of_month(year + 1, 5, 2)
            if mother_day and 0 <= (mother_day - reference_date).days <= days_ahead:
                event_info = EventDetector._create_event_info(
                    EventType.MOTHER_DAY, mother_day, reference_date, 1
                )
                events.append(event_info)
        
        # === Thêm FATHER_DAY (Chủ nhật thứ 3 tháng 6) ===
        father_day = EventDetector._get_nth_sunday_of_month(year, 6, 3)
        if father_day:
            if father_day < reference_date:
                father_day = EventDetector._get_nth_sunday_of_month(year + 1, 6, 3)
            if father_day and 0 <= (father_day - reference_date).days <= days_ahead:
                event_info = EventDetector._create_event_info(
                    EventType.FATHER_DAY, father_day, reference_date, 1
                )
                events.append(event_info)
        
        # === Thêm BLACK_FRIDAY (Thứ 6 sau Lễ Tạ Ơn - Thứ 5 tuần 4 tháng 11) ===
        black_friday = EventDetector._get_black_friday(year)
        if black_friday:
            if black_friday < reference_date:
                black_friday = EventDetector._get_black_friday(year + 1)
            if black_friday and 0 <= (black_friday - reference_date).days <= days_ahead:
                event_info = EventDetector._create_event_info(
                    EventType.BLACK_FRIDAY, black_friday, reference_date, 1
                )
                events.append(event_info)
        
        # === Thêm CYBER_MONDAY (Thứ 2 sau Black Friday) ===
        if black_friday:
            cyber_monday = black_friday + timedelta(days=3)
            if 0 <= (cyber_monday - reference_date).days <= days_ahead:
                event_info = EventDetector._create_event_info(
                    EventType.CYBER_MONDAY, cyber_monday, reference_date, 1
                )
                events.append(event_info)
        
        # Kiểm tra sự kiện theo lịch Âm
        for event_type, years_data in EventDetector.LUNAR_EVENTS.items():
            if year in years_data:
                event_data = years_data[year]
                event_date = datetime(year, event_data["month"], event_data["day"])
                days_until = (event_date - reference_date).days
                
                if 0 <= days_until <= days_ahead:
                    duration = 7 if event_type == EventType.TET else 3
                    event_info = EventDetector._create_event_info(
                        event_type, event_date, reference_date, duration
                    )
                    events.append(event_info)
            
            # Kiểm tra năm sau
            if year + 1 in years_data:
                event_data = years_data[year + 1]
                event_date = datetime(year + 1, event_data["month"], event_data["day"])
                days_until = (event_date - reference_date).days
                
                if 0 <= days_until <= days_ahead:
                    duration = 7 if event_type == EventType.TET else 3
                    event_info = EventDetector._create_event_info(
                        event_type, event_date, reference_date, duration
                    )
                    events.append(event_info)
        
        # Kiểm tra cuối tuần gần nhất
        weekend_event = EventDetector._get_next_weekend(reference_date)
        if weekend_event:
            events.append(weekend_event)
        
        # Sắp xếp theo ngày
        events.sort(key=lambda x: x.days_until_event)
        
        return events
    
    @staticmethod
    def get_current_events(reference_date: Optional[datetime] = None) -> List[EventInfo]:
        """Lấy các sự kiện đang diễn ra"""
        if reference_date is None:
            reference_date = datetime.now()
        
        all_events = EventDetector.get_upcoming_events(reference_date, days_ahead=30)
        current_events = [e for e in all_events if e.is_active]
        
        return current_events
    
    @staticmethod
    def _create_event_info(
        event_type: EventType,
        event_date: datetime,
        reference_date: datetime,
        duration_days: int
    ) -> EventInfo:
        """Tạo EventInfo object"""
        days_until = (event_date - reference_date).days
        
        # Kiểm tra sự kiện có đang diễn ra không
        event_end = event_date + timedelta(days=duration_days)
        is_active = event_date <= reference_date <= event_end
        
        return EventInfo(
            event_type=event_type,
            event_date=event_date,
            days_until_event=days_until,
            is_active=is_active,
            duration_days=duration_days,
            recommended_discount_range=EventDetector.EVENT_DISCOUNT_RANGES.get(
                event_type, "5-15"
            ),
            target_categories=EventDetector.EVENT_CATEGORIES.get(
                event_type, ["Tất cả"]
            )
        )
    
    @staticmethod
    def _get_next_weekend(reference_date: datetime) -> Optional[EventInfo]:
        """Lấy thông tin cuối tuần tiếp theo"""
        days_ahead = (5 - reference_date.weekday()) % 7  # Tính đến thứ 6
        if days_ahead == 0 and reference_date.weekday() == 5:  # Đã là thứ 6
            days_ahead = 7
        
        next_friday = reference_date + timedelta(days=days_ahead)
        
        # Chỉ tạo event cuối tuần nếu còn xa hơn 2 ngày
        if days_ahead >= 2:
            return EventInfo(
                event_type=EventType.WEEKEND,
                event_date=next_friday,
                days_until_event=days_ahead,
                is_active=reference_date.weekday() in [4, 5, 6],  # Thứ 6, 7, CN
                duration_days=3,
                recommended_discount_range="5-15",
                target_categories=["Tất cả"]
            )
        
        return None
    
    @staticmethod
    def _get_nth_sunday_of_month(year: int, month: int, nth: int) -> Optional[datetime]:
        """
        Tìm Chủ nhật thứ N trong tháng
        
        Args:
            year: Năm
            month: Tháng
            nth: Thứ N (1 = Chủ nhật đầu tiên, 2 = thứ 2, ...)
            
        Returns:
            datetime object hoặc None
        """
        # Tìm ngày đầu tiên của tháng
        first_day = datetime(year, month, 1)
        
        # Tìm Chủ nhật đầu tiên (weekday 6 = Chủ nhật)
        days_until_sunday = (6 - first_day.weekday()) % 7
        first_sunday = first_day + timedelta(days=days_until_sunday)
        
        # Tính Chủ nhật thứ N
        target_sunday = first_sunday + timedelta(weeks=nth - 1)
        
        # Kiểm tra còn trong tháng không
        if target_sunday.month == month:
            return target_sunday
        return None
    
    @staticmethod
    def _get_black_friday(year: int) -> Optional[datetime]:
        """
        Tìm ngày Black Friday (Thứ 6 sau Lễ Tạ Ơn)
        Lễ Tạ Ơn = Thứ 5 tuần thứ 4 tháng 11 (US)
        
        Args:
            year: Năm
            
        Returns:
            datetime object hoặc None
        """
        # Tìm ngày đầu tiên tháng 11
        first_day = datetime(year, 11, 1)
        
        # Tìm Thứ 5 đầu tiên (weekday 3 = Thứ 5)
        days_until_thursday = (3 - first_day.weekday()) % 7
        first_thursday = first_day + timedelta(days=days_until_thursday)
        
        # Thứ 5 tuần thứ 4 = first_thursday + 3 weeks
        thanksgiving = first_thursday + timedelta(weeks=3)
        
        # Black Friday = ngày sau Thanksgiving (Thứ 6)
        black_friday = thanksgiving + timedelta(days=1)
        
        return black_friday
    
    @staticmethod
    def suggest_promotion_timing(event: EventInfo) -> dict:
        """
        Đề xuất thời gian bắt đầu khuyến mãi
        
        Args:
            event: Thông tin sự kiện
            
        Returns:
            Dictionary với thông tin về thời gian khuyến mãi
        """
        # Khuyến mãi nên bắt đầu trước sự kiện
        advance_days = {
            # Sự kiện lớn - cần chuẩn bị sớm
            EventType.TET: 14,  # 2 tuần trước Tết
            EventType.KITCHEN_GOD: 7,  # 1 tuần trước
            EventType.MID_AUTUMN: 10,  # 10 ngày trước Trung Thu
            EventType.CHRISTMAS: 10,  # 10 ngày trước Giáng Sinh
            EventType.NEW_YEAR: 7,  # 1 tuần trước
            
            # Ngày lễ gia đình
            EventType.VALENTINE: 5,  # 5 ngày trước
            EventType.INTERNATIONAL_WOMEN_DAY: 5,
            EventType.VIETNAM_WOMEN_DAY: 5,
            EventType.MOTHER_DAY: 7,
            EventType.FATHER_DAY: 7,
            EventType.TEACHER_DAY: 5,
            
            # Sự kiện mua sắm
            EventType.BLACK_FRIDAY: 3,
            EventType.CYBER_MONDAY: 1,
            EventType.SINGLES_DAY: 3,
            EventType.DOUBLE_12: 3,
            
            # Sự kiện ngắn
            EventType.WEEKEND: 2,
            EventType.FLASH_SALE: 1,
            EventType.PAYDAY: 2,
        }
        
        days_before = advance_days.get(event.event_type, 3)
        start_date = event.event_date - timedelta(days=days_before)
        end_date = event.event_date + timedelta(days=event.duration_days)
        
        return {
            "promotion_start": start_date,
            "promotion_end": end_date,
            "total_duration": (end_date - start_date).days,
            "pre_event_days": days_before,
            "event_days": event.duration_days,
            "recommendation": f"Bắt đầu khuyến mãi {days_before} ngày trước sự kiện để tối đa hóa hiệu quả"
        }
