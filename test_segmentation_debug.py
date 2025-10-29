"""
Debug Customer Segmentation
"""
import asyncio
from application.services.customer_segmentation_service import get_segmentation_service

async def test():
    print("="*70)
    print("🐛 DEBUGGING CUSTOMER SEGMENTATION")
    print("="*70)
    
    service = get_segmentation_service()
    
    print("\n1️⃣ Testing segment_all_customers()...")
    result = await service.segment_all_customers()
    print(f"   Type: {type(result)}")
    print(f"   Content: {result}")
    print(f"   Length: {len(result) if result else 0}")
    
    print("\n2️⃣ Testing segment_customers()...")
    result2 = await service.segment_customers()
    print(f"   Result: {result2}")
    
    print("\n" + "="*70)

asyncio.run(test())
