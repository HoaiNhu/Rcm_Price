"""Test hybrid initialization after fixing dynamic pricing"""
import requests
import json
import time

print("\n" + "="*60)
print("🧪 TESTING HYBRID SYSTEM INITIALIZATION")
print("="*60)

try:
    # Call initialize endpoint
    print("\n📡 Calling POST /api/hybrid/initialize...")
    response = requests.post("http://localhost:8000/api/hybrid/initialize", timeout=30)
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        print("\n✅ Initialize request accepted!")
        print("⏳ Waiting 10 seconds for background initialization...")
        time.sleep(10)
        
        # Check logs for errors
        print("\n📊 Check server logs for:")
        print("   - ✅ HuggingFace embeddings created")
        print("   - ✅ Dynamic Pricing data prepared (should NOT show error)")
        print("   - ✅ Hybrid System initialized successfully")
        
    else:
        print(f"\n❌ Request failed with status {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to http://localhost:8000")
    print("⚠️  Make sure server is running!")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
