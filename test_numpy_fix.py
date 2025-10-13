"""
Quick test script for numpy serialization fix
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_product_recommendations():
    """Test product recommendations endpoint"""
    product_id = "67643c2411d943b7bdecb7d3"
    url = f"{BASE_URL}/api/hybrid/product-recommendations/{product_id}?top_k=5"
    
    print(f"Testing: {url}")
    print("-" * 80)
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Response received:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Check if pricing_optimization exists and has data
            if 'pricing_optimization' in data:
                pricing = data['pricing_optimization']
                print("\n✅ Pricing Optimization Data:")
                print(f"  - Current Price: {pricing.get('current_price')} (type: {type(pricing.get('current_price'))})")
                print(f"  - Optimal Price: {pricing.get('optimal_price')} (type: {type(pricing.get('optimal_price'))})")
                print(f"  - Predicted Revenue: {pricing.get('predicted_revenue')} (type: {type(pricing.get('predicted_revenue'))})")
                
                # Verify all are Python native types, not numpy types
                assert isinstance(pricing.get('current_price'), (int, float)), "current_price should be Python int/float"
                assert isinstance(pricing.get('optimal_price'), (int, float)), "optimal_price should be Python int/float"
                assert isinstance(pricing.get('predicted_revenue'), (int, float)), "predicted_revenue should be Python int/float"
                print("\n✅ All types are Python native (not numpy)!")
            
        else:
            print(f"❌ FAILED with status code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_complete_strategy():
    """Test complete strategy endpoint"""
    url = f"{BASE_URL}/api/hybrid/generate-complete-strategy"
    
    print(f"\nTesting: {url}")
    print("-" * 80)
    
    try:
        response = requests.post(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Response received:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ FAILED with status code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("=" * 80)
    print("NUMPY SERIALIZATION FIX - TEST SCRIPT")
    print("=" * 80)
    
    test_product_recommendations()
    test_complete_strategy()
    
    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)
