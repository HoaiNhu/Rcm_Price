"""Test event promotion service directly"""
import asyncio
from application.services.event_promotion_service import get_event_promotion_service

async def test():
    service = get_event_promotion_service()
    
    print("1. Analyzing products...")
    products = await service.analyze_product_performance()
    print(f"   Found {len(products)} products")
    
    suitable = [p for p in products if p.avg_rating >= 3.5 and p.total_sold > 0]
    print(f"   Suitable products (rating >= 3.5, sold > 0): {len(suitable)}")
    
    if suitable:
        print("\n   Top 3 suitable products:")
        for i, p in enumerate(sorted(suitable, key=lambda x: x.revenue_contribution, reverse=True)[:3], 1):
            print(f"   {i}. {p.product_name}")
            print(f"      Rating: {p.avg_rating}, Sold: {p.total_sold}, Revenue: {p.revenue_contribution:.2f}%")
    
    print("\n2. Generating promotions...")
    promotions = await service.generate_event_promotion(days_ahead=60)
    print(f"   Generated {len(promotions)} promotions")
    
    if promotions:
        for i, promo in enumerate(promotions, 1):
            print(f"\n   Promotion #{i}:")
            print(f"   - Event: {promo.event_info.event_type.value if promo.event_info else 'N/A'}")
            print(f"   - Discount: {promo.discount_value}%")
            print(f"   - Products: {len(promo.target_products)}")
    else:
        print("   ❌ No promotions generated!")

asyncio.run(test())
