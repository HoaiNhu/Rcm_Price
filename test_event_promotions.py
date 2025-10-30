"""
Test Event-Based Promotion System
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from application.services.event_promotion_service import get_event_promotion_service
from utils.event_detector import EventDetector
from datetime import datetime


async def test_product_analysis():
    """Test 1: Phân tích sản phẩm"""
    print("\n" + "="*70)
    print("TEST 1: PHÂN TÍCH SẢN PHẨM")
    print("="*70)
    
    service = get_event_promotion_service()
    
    try:
        analyses = await service.analyze_product_performance(analysis_period_days=30)
        
        print(f"\n✅ Đã phân tích {len(analyses)} sản phẩm\n")
        
        # Hiển thị top 5 sản phẩm bán chạy
        best_sellers = [p for p in analyses if p.status.value == "BEST_SELLER"]
        print(f"🏆 Top {len(best_sellers)} sản phẩm bán chạy:")
        for p in best_sellers[:5]:
            print(f"  - {p.product_name}: {p.total_sold} đơn, {p.revenue_contribution:.1f}% doanh thu")
        
        # Hiển thị sản phẩm bán chậm
        slow_moving = [p for p in analyses if p.status.value == "SLOW_MOVING"]
        print(f"\n⚠️ {len(slow_moving)} sản phẩm bán chậm:")
        for p in slow_moving[:5]:
            print(f"  - {p.product_name}: {p.total_sold} đơn, tồn kho {p.stock_level}")
            print(f"    → Đề xuất giảm {p.recommended_discount}%: {p.reason}")
        
        # Stats
        print(f"\n📊 Thống kê:")
        print(f"  - Bán chạy: {len(best_sellers)} sản phẩm")
        print(f"  - Bán chậm: {len(slow_moving)} sản phẩm")
        print(f"  - Bình thường: {len(analyses) - len(best_sellers) - len(slow_moving)} sản phẩm")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")


async def test_combo_discovery():
    """Test 2: Phát hiện combo"""
    print("\n" + "="*70)
    print("TEST 2: PHÁT HIỆN COMBO SẢN PHẨM")
    print("="*70)
    
    service = get_event_promotion_service()
    
    try:
        combos = await service.discover_product_combos(
            min_support=0.05,
            min_confidence=0.3
        )
        
        print(f"\n✅ Tìm thấy {len(combos)} combo tiềm năng\n")
        
        if combos:
            print("🔗 Top 5 combo:")
            for i, combo in enumerate(combos[:5], 1):
                total_price = combo.product_1_price + combo.product_2_price
                discount_amount = total_price * (combo.recommended_bundle_discount / 100)
                final_price = total_price - discount_amount
                
                print(f"\n{i}. {combo.product_1_name} + {combo.product_2_name}")
                print(f"   Giá gốc: {total_price:,.0f} VND")
                print(f"   Giảm {combo.recommended_bundle_discount:.1f}%: {final_price:,.0f} VND")
                print(f"   Confidence: {combo.confidence:.2f} ({combo.frequency_together} lần mua cùng)")
        else:
            print("⚠️ Không đủ dữ liệu để tìm combo (cần ít nhất 5 đơn hàng có 2+ sản phẩm)")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")


def test_event_detection():
    """Test 3: Phát hiện sự kiện"""
    print("\n" + "="*70)
    print("TEST 3: PHÁT HIỆN SỰ KIỆN SẮP TỚI")
    print("="*70)
    
    detector = EventDetector()
    
    try:
        events = detector.get_upcoming_events(
            reference_date=datetime.now(),
            days_ahead=90
        )
        
        print(f"\n✅ Tìm thấy {len(events)} sự kiện trong 90 ngày tới\n")
        
        for event in events:
            status = "🔴 ĐANG DIỄN RA" if event.is_active else f"📅 Còn {event.days_until_event} ngày"
            print(f"\n{status}")
            print(f"  Sự kiện: {event.event_type.value}")
            print(f"  Ngày: {event.event_date.strftime('%d/%m/%Y')}")
            print(f"  Thời gian: {event.duration_days} ngày")
            print(f"  Giảm giá đề xuất: {event.recommended_discount_range}%")
            print(f"  Danh mục: {', '.join(event.target_categories)}")
            
            # Đề xuất thời gian promotion
            timing = detector.suggest_promotion_timing(event)
            print(f"  💡 Khuyến mãi nên bắt đầu: {timing['promotion_start'].strftime('%d/%m/%Y')}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")


async def test_event_promotion():
    """Test 4: Tạo khuyến mãi cho sự kiện"""
    print("\n" + "="*70)
    print("TEST 4: TẠO KHUYẾN MÃI DỰA TRÊN SỰ KIỆN")
    print("="*70)
    
    service = get_event_promotion_service()
    
    try:
        promotions = await service.generate_event_promotion(
            event_type=None,  # Tất cả sự kiện
            days_ahead=60
        )
        
        print(f"\n✅ Tạo được {len(promotions)} chương trình khuyến mãi\n")
        
        for promo in promotions:
            print(f"\n{'='*60}")
            print(f"🎉 {promo.promotion_name}")
            print(f"{'='*60}")
            print(f"Mô tả: {promo.description}")
            
            if promo.event_info:
                print(f"\nSự kiện: {promo.event_info.event_type.value}")
                print(f"Còn: {promo.event_info.days_until_event} ngày")
            
            print(f"\nChiến lược: {promo.strategy.value}")
            print(f"Mục tiêu: {promo.primary_goal}")
            print(f"Giảm giá: {promo.discount_value}%")
            print(f"Thời gian: {promo.start_date.strftime('%d/%m/%Y')} → {promo.end_date.strftime('%d/%m/%Y')} ({promo.duration_days} ngày)")
            
            print(f"\nSản phẩm áp dụng: {len(promo.target_products)} sản phẩm")
            for p in promo.target_products[:3]:
                print(f"  - {p.product_name} ({p.status.value})")
            
            print(f"\nCombo đề xuất: {len(promo.combo_suggestions)} combo")
            
            print(f"\n📊 Dự đoán:")
            print(f"  - Tác động doanh thu: {promo.estimated_revenue_impact:+.1f}%")
            print(f"  - Tăng đơn hàng: +{promo.estimated_order_increase} đơn")
            print(f"  - Mức rủi ro: {promo.risk_level}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")


async def test_smart_promotion():
    """Test 5: Tạo khuyến mãi thông minh"""
    print("\n" + "="*70)
    print("TEST 5: TẠO KHUYẾN MÃI THÔNG MINH")
    print("="*70)
    
    service = get_event_promotion_service()
    
    focuses = ["revenue", "clearance", "balanced"]
    
    for focus in focuses:
        print(f"\n{'─'*60}")
        print(f"Focus: {focus.upper()}")
        print(f"{'─'*60}")
        
        try:
            promo = await service.generate_smart_promotion(focus=focus)
            
            print(f"\n🎯 {promo.promotion_name}")
            print(f"Mô tả: {promo.description}")
            print(f"Chiến lược: {promo.strategy.value}")
            print(f"Giảm giá: {promo.discount_value}%")
            print(f"Sản phẩm: {len(promo.target_products)} sản phẩm")
            print(f"Dự đoán doanh thu: {promo.estimated_revenue_impact:+.1f}%")
            print(f"Rủi ro: {promo.risk_level}")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")


async def main():
    """Chạy tất cả tests"""
    print("\n" + "🧪" * 35)
    print("EVENT-BASED PROMOTION SYSTEM - TEST SUITE")
    print("🧪" * 35)
    
    # Test 1: Product Analysis
    await test_product_analysis()
    
    # Test 2: Combo Discovery
    await test_combo_discovery()
    
    # Test 3: Event Detection
    test_event_detection()
    
    # Test 4: Event Promotion
    await test_event_promotion()
    
    # Test 5: Smart Promotion
    await test_smart_promotion()
    
    print("\n" + "="*70)
    print("✅ TẤT CẢ TESTS HOÀN THÀNH")
    print("="*70)
    print("\n💡 Mở http://localhost:8000/docs để xem API documentation")
    print("📖 Xem EVENT_PROMOTION_GUIDE.md để biết chi tiết\n")


if __name__ == "__main__":
    asyncio.run(main())
