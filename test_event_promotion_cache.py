"""
Test script để verify cache hoạt động đúng
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_event_promotion_cache():
    """Test cache cho event promotion endpoint"""
    
    print("=" * 80)
    print("🧪 Testing Event Promotion Cache")
    print("=" * 80)
    
    endpoint = f"{BASE_URL}/api/event-promotions/generate-event-promotion"
    params = {"days_ahead": 4}
    
    # First request - should generate new data
    print("\n1️⃣ First Request (should MISS cache and generate new data)...")
    start = time.time()
    response1 = requests.post(endpoint, params=params)
    duration1 = time.time() - start
    
    print(f"   ⏱️  Duration: {duration1:.2f}s")
    print(f"   📊 Status Code: {response1.status_code}")
    
    if response1.status_code != 200:
        print(f"   ❌ ERROR: {response1.text}")
        return
    
    data1 = response1.json()
    print(f"   ✅ Received {len(data1)} promotions")
    
    if data1:
        first_promo = data1[0]
        print(f"   📝 First promotion: {first_promo.get('promotion_name', 'N/A')}")
        print(f"   💰 Discount: {first_promo.get('discount_value', 0)}%")
        print(f"   🎯 Products: {len(first_promo.get('target_products', []))}")
    
    # Second request - should hit cache
    print("\n2️⃣ Second Request (should HIT cache)...")
    time.sleep(1)  # Small delay
    start = time.time()
    response2 = requests.post(endpoint, params=params)
    duration2 = time.time() - start
    
    print(f"   ⏱️  Duration: {duration2:.2f}s")
    print(f"   📊 Status Code: {response2.status_code}")
    
    if response2.status_code != 200:
        print(f"   ❌ ERROR: {response2.text}")
        return
    
    data2 = response2.json()
    print(f"   ✅ Received {len(data2)} promotions")
    
    # Compare results
    print("\n3️⃣ Comparing Results...")
    print(f"   📊 Data identical: {data1 == data2}")
    print(f"   ⚡ Speed improvement: {duration1 / duration2:.1f}x faster")
    
    # Verify structure
    print("\n4️⃣ Verifying Response Structure...")
    if data2:
        first_promo = data2[0]
        required_fields = [
            'promotion_id', 'promotion_name', 'description', 'strategy',
            'target_products', 'discount_value', 'start_date', 'end_date'
        ]
        
        missing = [f for f in required_fields if f not in first_promo]
        
        if missing:
            print(f"   ❌ Missing fields: {missing}")
        else:
            print(f"   ✅ All required fields present")
            
            # Check if products are dicts (not strings)
            products = first_promo.get('target_products', [])
            if products:
                first_product = products[0]
                if isinstance(first_product, dict):
                    print(f"   ✅ Products are properly structured (dict)")
                    print(f"      Sample: {first_product.get('product_name', 'N/A')}")
                else:
                    print(f"   ❌ Products are NOT dicts: {type(first_product)}")
                    print(f"      Value: {str(first_product)[:100]}")
    
    print("\n" + "=" * 80)
    print("✅ Test completed!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_event_promotion_cache()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
