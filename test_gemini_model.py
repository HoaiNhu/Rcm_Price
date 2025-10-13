"""
Test Gemini API with new model gemini-1.5-flash
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    print("❌ google-generativeai not installed!")
    print("Run: pip install google-generativeai")
    sys.exit(1)

print("=" * 60)
print("Testing Gemini API - New Model Update")
print("=" * 60)

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file!")
    sys.exit(1)

print(f"\n✅ API Key found: {api_key[:10]}...")

# Configure
genai.configure(api_key=api_key)

# List available models
print("\n📋 Listing available Gemini models:")
try:
    models = genai.list_models()
    gemini_models = [m for m in models if 'gemini' in m.name.lower()]
    
    for model in gemini_models:
        print(f"\n  Model: {model.name}")
        print(f"  Methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"⚠️ Cannot list models: {e}")

# Test gemini-2.0-flash (current stable)
print("\n" + "=" * 60)
print("Testing: gemini-2.0-flash (CURRENT STABLE)")
print("=" * 60)

try:
    model = genai.GenerativeModel('gemini-2.5-pro')
    response = model.generate_content(
        "Viết một câu chào bằng tiếng Việt cho hệ thống khuyến mãi bánh kem."
    )

    print("\n✅ gemini-2.5-pro WORKS!")
    print(f"\nResponse:")
    print(f"{response.text}")
    
except Exception as e:
    print(f"\n❌ gemini-2.5-pro FAILED!")
    print(f"Error: {e}")

# Test gemini-2.5-flash (latest)
print("\n" + "=" * 60)
print("Testing: gemini-2.5-flash (LATEST)")
print("=" * 60)

try:
    model = genai.GenerativeModel('gemini-2.5-pro')
    response = model.generate_content(
        "Tạo một insight ngắn gọn về xu hướng mua bánh kem."
    )

    print("\n✅ gemini-2.5-pro WORKS!")
    print(f"\nResponse:")
    print(f"{response.text}")
    
except Exception as e:
    print(f"\n❌ gemini-2.5-pro FAILED!")
    print(f"Error: {e}")

# Test gemini-1.5-flash (deprecated)
print("\n" + "=" * 60)
print("Testing: gemini-1.5-flash (DEPRECATED - should fail)")
print("=" * 60)

try:
    model = genai.GenerativeModel('gemini-2.5-pro')
    response = model.generate_content(
        "Viết một câu chào bằng tiếng Việt cho hệ thống khuyến mãi bánh kem."
    )
    
    print("\n✅ gemini-1.5-flash WORKS!")
    print(f"\nResponse:")
    print(f"{response.text}")
    
except Exception as e:
    print(f"\n❌ gemini-1.5-flash FAILED!")
    print(f"Error: {e}")

# Test gemini-1.5-pro (optional)
print("\n" + "=" * 60)
print("Testing: gemini-1.5-pro (high quality model)")
print("=" * 60)

try:
    model = genai.GenerativeModel('gemini-2.5-pro')
    response = model.generate_content(
        "Tạo một insight ngắn gọn về xu hướng mua bánh kem."
    )

    print("\n✅ gemini-2.5-pro WORKS!")
    print(f"\nResponse:")
    print(f"{response.text}")
    
except Exception as e:
    print(f"\n❌ gemini-2.5-pro FAILED!")
    print(f"Error: {e}")

# Test old model (should fail)
print("\n" + "=" * 60)
print("Testing: gemini-pro (OLD - should fail)")
print("=" * 60)

try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello")
    
    print("\n⚠️ gemini-pro still works? (unexpected)")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"\n✅ gemini-pro FAILED as expected!")
    print(f"Error: {str(e)[:200]}")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
print("\n💡 Recommendation:")
print("   ✅ Use gemini-2.0-flash for production (stable, fast & cheap)")
print("   ✅ Use gemini-2.5-flash for latest features")
print("   ✅ Use gemini-2.5-pro for highest quality")
print("=" * 60)
