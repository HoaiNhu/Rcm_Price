"""
Test Redis Cache cho Event Promotion
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.utils.promotion_cache import PromotionCache

async def test_cache():
    """Test Redis cache functionality"""
    print("🧪 Testing Redis Cache...")
    
    cache = PromotionCache()
    
    # Test 1: Set cache
    print("\n1️⃣ Testing cache SET...")
    test_data = {
        "event": "Halloween",
        "discount": 25,
        "products": ["Product A", "Product B"]
    }
    await cache.set("HALLOWEEN", 7, test_data)
    print("   ✅ Cache SET successful")
    
    # Test 2: Get cache
    print("\n2️⃣ Testing cache GET...")
    cached_data = await cache.get("HALLOWEEN", 7)
    if cached_data:
        print(f"   ✅ Cache GET successful: {cached_data}")
    else:
        print("   ❌ Cache GET failed: No data found")
    
    # Test 3: Get non-existent key
    print("\n3️⃣ Testing cache MISS...")
    missing = await cache.get("NONEXISTENT", 999)
    if missing is None:
        print("   ✅ Cache MISS handled correctly (returned None)")
    else:
        print(f"   ❌ Unexpected data: {missing}")
    
    print("\n✨ Cache test completed!")

if __name__ == "__main__":
    asyncio.run(test_cache())
