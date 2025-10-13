"""
Test Mock API - Không cần MongoDB
Test các endpoints với mock data
"""
import requests
import json
import time

def test_mock_api():
    """Test mock API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Mock API Endpoints...")
    print("="*50)
    
    # Test 1: Health Check
    print("\n1. 🔍 Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Mock Recommendations
    print("\n2. 👤 Mock User Recommendations")
    try:
        response = requests.get(f"{base_url}/api/mock/recommendations/user123?top_k=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data['recommendations'])} recommendations")
            print(f"First recommendation: {data['recommendations'][0]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Mock Promotion Strategy
    print("\n3. 🎯 Mock Promotion Strategy")
    try:
        response = requests.get(f"{base_url}/api/mock/promotion-strategy")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Strategy: {data['strategy']['current_season']}")
            print(f"Promotion products: {len(data['strategy']['promotion_products'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Business Analytics (sẽ trả về mock data)
    print("\n4. 📊 Business Analytics")
    try:
        response = requests.get(f"{base_url}/api/analytics/business-health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Analytics: {data['analytics']['message']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: API Documentation
    print("\n5. 📚 API Documentation")
    print(f"Swagger UI: {base_url}/docs")
    print(f"ReDoc: {base_url}/redoc")
    
    print("\n🎉 Mock API Testing Completed!")

if __name__ == "__main__":
    test_mock_api()

