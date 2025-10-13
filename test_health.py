"""Quick test script to check API health endpoint"""
import requests
import json

try:
    response = requests.get("http://localhost:8000/health")
    data = response.json()
    
    print("\n" + "="*50)
    print("🏥 HEALTH ENDPOINT RESULTS")
    print("="*50)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("="*50)
    
    # Check MongoDB status
    mongodb_status = data.get("mongodb", {}).get("status", "unknown")
    if mongodb_status == "connected":
        print("\n✅ MongoDB: CONNECTED")
        print(f"   📦 Products: {data.get('mongodb', {}).get('products', 0)}")
        print(f"   🛒 Orders: {data.get('mongodb', {}).get('orders', 0)}")
        print(f"   👥 Users: {data.get('mongodb', {}).get('users', 0)}")
        print("\n🎉 API IS WORKING CORRECTLY! 🎉\n")
    else:
        print(f"\n❌ MongoDB: {mongodb_status.upper()}")
        print("⚠️  Connection issue detected\n")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to http://localhost:8000")
    print("⚠️  Make sure server is running!\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")
