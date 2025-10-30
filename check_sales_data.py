"""Check product sales data"""
import asyncio
from application.services.event_promotion_service import get_event_promotion_service

async def check():
    service = get_event_promotion_service()
    products = await service.analyze_product_performance()
    
    print(f"Total products: {len(products)}")
    print("\nAll products with their sales data:")
    for i, p in enumerate(products[:10], 1):
        print(f"{i}. {p.product_name}")
        print(f"   Rating: {p.avg_rating}")
        print(f"   Total Sold: {p.total_sold}")
        print(f"   Revenue Contribution: {p.revenue_contribution}%")
        print(f"   Status: {p.status}")
        print()

asyncio.run(check())
