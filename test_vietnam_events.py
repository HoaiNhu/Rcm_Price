"""
Test script để kiểm tra tất cả ngày lễ đã được thêm vào
"""

import sys
sys.path.append('.')

from datetime import datetime
from utils.event_detector import EventDetector
from domain.entities.event_promotion import EventType

def test_all_events():
    print("=" * 80)
    print("🎯 TEST DANH SÁCH ĐẦY ĐỦ NGÀY LỄ VIỆT NAM")
    print("=" * 80)
    
    # Test với reference date = hôm nay
    reference_date = datetime.now()
    print(f"\n📅 Ngày tham chiếu: {reference_date.strftime('%d/%m/%Y')}")
    
    # Lấy sự kiện sắp tới trong 365 ngày (cả năm)
    print(f"\n🔍 Tìm sự kiện trong 365 ngày tới...\n")
    events = EventDetector.get_upcoming_events(reference_date, days_ahead=365)
    
    print(f"✅ Tìm thấy {len(events)} sự kiện:\n")
    print("-" * 80)
    
    # Nhóm sự kiện theo tháng
    events_by_month = {}
    for event in events:
        month = event.event_date.month
        if month not in events_by_month:
            events_by_month[month] = []
        events_by_month[month].append(event)
    
    # In ra từng tháng
    months_vn = {
        1: "THÁNG 1", 2: "THÁNG 2", 3: "THÁNG 3", 4: "THÁNG 4",
        5: "THÁNG 5", 6: "THÁNG 6", 7: "THÁNG 7", 8: "THÁNG 8",
        9: "THÁNG 9", 10: "THÁNG 10", 11: "THÁNG 11", 12: "THÁNG 12"
    }
    
    total_events = 0
    for month in sorted(events_by_month.keys()):
        month_events = events_by_month[month]
        print(f"\n📆 {months_vn[month]} ({len(month_events)} sự kiện)")
        print("-" * 80)
        
        for event in sorted(month_events, key=lambda x: x.event_date):
            days_until = event.days_until_event
            status = "🔴 Đang diễn ra" if event.is_active else f"⏰ Còn {days_until} ngày"
            
            print(f"  • {event.event_date.strftime('%d/%m/%Y')} - {event.event_type.value}")
            print(f"    {status}")
            print(f"    Giảm giá: {event.recommended_discount_range}%")
            print(f"    Thời gian: {event.duration_days} ngày")
            print(f"    Sản phẩm: {', '.join(event.target_categories[:3])}")
            print()
            total_events += 1
    
    print("=" * 80)
    print(f"✨ TỔNG KẾT: {total_events} sự kiện trong năm")
    print("=" * 80)
    
    # Test các EventType mới
    print("\n\n" + "=" * 80)
    print("🎨 DANH SÁCH TẤT CẢ EVENT TYPES")
    print("=" * 80)
    
    event_types = list(EventType)
    print(f"\nTổng số: {len(event_types)} loại sự kiện\n")
    
    categories = {
        "Ngày Lễ Quốc Gia": [],
        "Ngày Lễ Truyền Thống": [],
        "Ngày Phụ Nữ & Gia Đình": [],
        "Ngày Lễ Tôn Giáo": [],
        "Ngày Nghề Nghiệp": [],
        "Sự Kiện Mua Sắm": [],
        "Sự Kiện Đặc Biệt": [],
        "Sự Kiện Shop": [],
        "Khác": []
    }
    
    # Phân loại
    national = ["TET", "HUNG_KING", "LIBERATION_DAY", "LABOR_DAY", "NATIONAL_DAY"]
    traditional = ["KITCHEN_GOD", "COLD_FOOD", "WANDERING_SOULS", "MID_AUTUMN"]
    women_family = ["INTERNATIONAL_WOMEN_DAY", "VIETNAM_WOMEN_DAY", "VALENTINE", 
                    "WHITE_DAY", "MOTHER_DAY", "FATHER_DAY", "FAMILY_DAY", 
                    "CHILDREN_DAY", "MID_AUTUMN_CHILDREN"]
    religion = ["CHRISTMAS", "CHRISTMAS_EVE", "NEW_YEAR", "NEW_YEAR_EVE"]
    profession = ["TEACHER_DAY", "DOCTOR_DAY", "PRESS_DAY"]
    shopping = ["BLACK_FRIDAY", "CYBER_MONDAY", "SINGLES_DAY", "DOUBLE_12", 
                "ONLINE_FRIDAY", "SUPER_SALE_1111"]
    special = ["FLASH_SALE", "WEEKEND", "PAYDAY", "MONTH_END_SALE", 
               "BACK_TO_SCHOOL", "GRADUATION_SEASON", "SUMMER_SALE", "YEAR_END_SALE"]
    shop = ["BIRTHDAY", "ANNIVERSARY", "GRAND_OPENING", "CUSTOMER_APPRECIATION"]
    
    for event_type in event_types:
        name = event_type.name
        if name in national:
            categories["Ngày Lễ Quốc Gia"].append(event_type)
        elif name in traditional:
            categories["Ngày Lễ Truyền Thống"].append(event_type)
        elif name in women_family:
            categories["Ngày Phụ Nữ & Gia Đình"].append(event_type)
        elif name in religion:
            categories["Ngày Lễ Tôn Giáo"].append(event_type)
        elif name in profession:
            categories["Ngày Nghề Nghiệp"].append(event_type)
        elif name in shopping:
            categories["Sự Kiện Mua Sắm"].append(event_type)
        elif name in special:
            categories["Sự Kiện Đặc Biệt"].append(event_type)
        elif name in shop:
            categories["Sự Kiện Shop"].append(event_type)
        else:
            categories["Khác"].append(event_type)
    
    for category, items in categories.items():
        if items:
            print(f"\n📌 {category} ({len(items)} sự kiện):")
            for item in items:
                discount = EventDetector.EVENT_DISCOUNT_RANGES.get(item, "0-10")
                print(f"  • {item.value} - Giảm giá: {discount}%")
    
    print("\n" + "=" * 80)
    print("✅ TEST HOÀN TẤT!")
    print("=" * 80)

if __name__ == "__main__":
    test_all_events()
