"""
🧪 AI Optimizer Test Script
============================

Test the AI-powered discount optimization system for event promotions.

Run this after starting the FastAPI server:
    python run.py

Then test with:
    python test_ai_optimizer.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_generate_halloween_promotion():
    """Test 1: Generate AI-optimized Halloween promotion"""
    print("\n" + "="*80)
    print("🎃 TEST 1: Generate Halloween Promotion (AI-Optimized)")
    print("="*80)
    
    url = f"{BASE_URL}/api/event-promotions/generate-event-promotion"
    params = {
        "event_type": "Halloween (31/10)",  # Exact value from EventType enum
        "days_ahead": 30
    }
    
    print(f"\n📤 Request: POST {url}")
    print(f"   Params: {params}")
    
    try:
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Status: {response.status_code}")
            print(f"\n📊 Results:")
            print(f"   - Found {len(data)} promotions")
            
            for idx, promo in enumerate(data, 1):
                # Debug: Check type
                if isinstance(promo, str):
                    print(f"\n   ⚠️ Promotion #{idx} is a string, not a dict!")
                    print(f"   Value: {promo[:200]}...")
                    continue
                
                print(f"\n   Promotion #{idx}:")
                print(f"   - Name: {promo.get('promotion_name', 'N/A')}")
                print(f"   - Avg Discount: {promo.get('discount_value', 'N/A')}%")
                print(f"   - Strategy: {promo.get('strategy', 'N/A')}")
                print(f"   - Revenue Impact: {promo.get('estimated_revenue_impact', 'N/A')}%")
                print(f"   - Duration: {promo.get('duration_days', 'N/A')} days")
                
                # Check products
                target_products = promo.get('target_products', [])
                print(f"   - Products: {len(target_products)} items")
                
                if target_products:
                    print(f"\n   📦 Sample Products (top 3):")
                    for i, product in enumerate(target_products[:3], 1):
                        product_name = product.get('product_name', 'N/A')
                        discount = product.get('recommended_discount', 'N/A')
                        reason = product.get('reason', 'N/A')
                        print(f"      {i}. {product_name}")
                        print(f"         Discount: {discount}%")
                        print(f"         Reason: {reason[:80]}...")
                
                print(f"\n   📝 Description Preview:")
                description = promo.get('description', 'N/A')
                print(f"      {description[:200]}...")
            
            return True
        else:
            print(f"\n❌ Failed! Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_generate_all_upcoming_events():
    """Test 2: Generate promotions for all upcoming events"""
    print("\n" + "="*80)
    print("🎉 TEST 2: Generate All Upcoming Event Promotions")
    print("="*80)
    
    url = f"{BASE_URL}/api/event-promotions/generate-event-promotion"
    params = {
        "days_ahead": 60  # No event_type → all events
    }
    
    print(f"\n📤 Request: POST {url}")
    print(f"   Params: {params}")
    
    try:
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Status: {response.status_code}")
            print(f"\n📊 Results:")
            print(f"   - Found {len(data)} upcoming event promotions")
            
            for idx, promo in enumerate(data, 1):
                event_info = promo.get('event_info', {})
                event_type = event_info.get('event_type', {}).get('value', 'N/A')
                event_date = event_info.get('event_date', 'N/A')
                discount_value = promo.get('discount_value', 'N/A')
                
                print(f"\n   {idx}. {event_type} ({event_date})")
                print(f"      - Avg Discount: {discount_value}%")
                print(f"      - Products: {len(promo.get('target_products', []))} items")
            
            return True
        else:
            print(f"\n❌ Failed! Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_optimizer_stats():
    """Test 3: Check optimizer statistics (if endpoint exists)"""
    print("\n" + "="*80)
    print("📊 TEST 3: Check AI Optimizer Learning Statistics")
    print("="*80)
    
    # This endpoint doesn't exist yet - TODO: implement
    print("\n⏳ Endpoint not yet implemented")
    print("   TODO: Add GET /api/event-promotions/learning-stats/{product_id}/{event_type}")
    print("   TODO: Add POST /api/event-promotions/record-promotion-result")
    return None


def check_server_health():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        return response.status_code == 200
    except:
        return False


def main():
    print("\n" + "="*80)
    print("🤖 AI Discount Optimizer - Test Suite")
    print("="*80)
    print(f"\n⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check server
    print("\n🔍 Checking server health...")
    if not check_server_health():
        print("\n❌ Server is not running!")
        print("   Please start the server first:")
        print("   $ python run.py")
        return
    
    print("✅ Server is running!")
    
    # Run tests
    results = []
    
    results.append(("Halloween Promotion", test_generate_halloween_promotion()))
    results.append(("All Upcoming Events", test_generate_all_upcoming_events()))
    results.append(("Optimizer Stats", test_optimizer_stats()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏳ PENDING"
        
        print(f"   {status} - {name}")
    
    passed = sum(1 for _, r in results if r is True)
    total = sum(1 for _, r in results if r is not None)
    
    print(f"\n   Total: {passed}/{total} tests passed")
    print(f"\n⏰ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


if __name__ == "__main__":
    main()
