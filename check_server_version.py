"""
Quick test to check if server has latest EventType with Halloween
"""
import requests

BASE_URL = "http://localhost:8000"

def check_server_version():
    """Try to generate promotion with Halloween"""
    print("🔍 Checking if server has Halloween event type...")
    
    url = f"{BASE_URL}/api/event-promotions/generate-event-promotion"
    
    # Try with Halloween
    params_halloween = {
        "event_type": "Halloween (31/10)",
        "days_ahead": 30
    }
    
    print(f"\n📤 Testing POST {url}")
    print(f"   Params: {params_halloween}")
    
    try:
        response = requests.post(url, params=params_halloween)
        
        if response.status_code == 400:
            error_detail = response.json().get('detail', '')
            if 'Invalid event_type' in error_detail:
                print(f"\n❌ Server is running OLD code (no Halloween)")
                print(f"   Valid events from server: {error_detail}")
                print("\n⚠️ ACTION REQUIRED:")
                print("   1. Stop the server (Ctrl+C)")
                print("   2. Restart: python app/main.py")
                return False
            else:
                print(f"\n❌ Other 400 error: {error_detail}")
                return False
        
        elif response.status_code == 200:
            print(f"\n✅ Server has Halloween! Code is up-to-date!")
            data = response.json()
            print(f"   Found {len(data)} promotions")
            return True
        
        else:
            print(f"\n⚠️ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Server is NOT running!")
        print("   Start server: python app/main.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_server_version()
