"""
Debug script: Kiểm tra tại sao không có promotions
"""
from datetime import datetime
import asyncio
import sys
sys.path.insert(0, '.')

async def debug_event_promotions():
    print("="*80)
    print("🔍 DEBUG: Event Promotion Generation")
    print("="*80)
    
    # 1. Check EventDetector
    print("\n📅 Step 1: Kiểm tra EventDetector")
    print("-" * 80)
    try:
        from utils.event_detector import EventDetector
        
        detector = EventDetector()
        events = detector.get_upcoming_events(
            reference_date=datetime.now(),
            days_ahead=60
        )
        
        print(f"✅ Found {len(events)} upcoming events:")
        for event in events:
            print(f"   - {event.event_type.value}")
            print(f"     Date: {event.event_date}")
            print(f"     Days until: {event.days_until_event}")
            print(f"     Categories: {event.target_categories[:3]}...")
            print()
        
        if len(events) == 0:
            print("❌ PROBLEM: No upcoming events detected!")
            print("   Check utils/event_detector.py FIXED_EVENTS dict")
            return
            
    except Exception as e:
        print(f"❌ ERROR in EventDetector: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. Check Database Connection
    print("\n💾 Step 2: Kiểm tra Database Connection")
    print("-" * 80)
    try:
        from infrastructure.database import get_db
        
        db = next(get_db())
        
        # Count orders
        order_count = db['orders'].count_documents({})
        print(f"✅ Orders collection: {order_count} documents")
        
        # Count products
        product_count = db['products'].count_documents({})
        print(f"✅ Products collection: {product_count} documents")
        
        if order_count == 0:
            print("⚠️  WARNING: No orders in database!")
            print("   Product analysis cần orders để tính rating, sales, etc.")
        
        if product_count == 0:
            print("❌ PROBLEM: No products in database!")
            print("   Không có products → không thể tạo promotions")
            return
            
    except Exception as e:
        print(f"❌ ERROR connecting to database: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. Check Product Analysis
    print("\n📊 Step 3: Kiểm tra Product Analysis")
    print("-" * 80)
    try:
        from application.services.event_promotion_service import get_event_promotion_service
        
        service = get_event_promotion_service()
        
        # Analyze products
        product_analyses = await service.analyze_product_performance()
        
        print(f"✅ Analyzed {len(product_analyses)} products")
        
        if len(product_analyses) == 0:
            print("❌ PROBLEM: No product analyses returned!")
            print("   Check analyze_product_performance() logic")
            return
        
        # Check suitable products
        suitable_count = sum(1 for p in product_analyses if p.avg_rating >= 3.5 and p.total_sold > 0)
        print(f"✅ Suitable products (rating >= 3.5, sold > 0): {suitable_count}")
        
        if suitable_count == 0:
            print("❌ PROBLEM: No suitable products!")
            print("   All products have rating < 3.5 or total_sold = 0")
            print("\n   Sample products:")
            for i, p in enumerate(product_analyses[:5], 1):
                print(f"   {i}. {p.product_name}")
                print(f"      Rating: {p.avg_rating}, Sold: {p.total_sold}")
            return
        
        # Show top products
        print("\n   Top 5 products:")
        sorted_products = sorted(product_analyses, key=lambda x: x.revenue_contribution, reverse=True)
        for i, p in enumerate(sorted_products[:5], 1):
            print(f"   {i}. {p.product_name}")
            print(f"      Rating: {p.avg_rating}, Sold: {p.total_sold}, Revenue: {p.revenue_contribution}%")
            
    except Exception as e:
        print(f"❌ ERROR in product analysis: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. Test Full Generation
    print("\n🎯 Step 4: Test Full Promotion Generation")
    print("-" * 80)
    try:
        promotions = await service.generate_event_promotion(
            event_type=None,  # All events
            days_ahead=60
        )
        
        print(f"✅ Generated {len(promotions)} promotions")
        
        if len(promotions) == 0:
            print("❌ PROBLEM: No promotions generated!")
            print("   Cần check logic trong generate_event_promotion()")
            print("   Có thể bị filter hết ở đâu đó")
        else:
            for i, promo in enumerate(promotions, 1):
                print(f"\n   Promotion #{i}:")
                print(f"   - Name: {promo.promotion_name}")
                print(f"   - Event: {promo.event_info.event_type.value if promo.event_info else 'N/A'}")
                print(f"   - Discount: {promo.discount_value}%")
                print(f"   - Products: {len(promo.target_products)}")
                
    except Exception as e:
        print(f"❌ ERROR generating promotions: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*80)
    print("✅ DEBUG COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(debug_event_promotions())
