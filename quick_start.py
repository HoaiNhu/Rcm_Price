"""
Quick Start Script cho AI Promotion System
Khởi động nhanh hệ thống và test các API
"""
import subprocess
import time
import requests
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "pymongo", "pandas", "numpy",
        "scikit-learn", "tensorflow", "transformers", "google-generativeai"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Run: cp env_example.txt .env")
        print("Then edit .env with your MongoDB URL and Gemini API key")
        return False
    
    print("✅ .env file found")
    
    # Check if MongoDB is running (optional)
    try:
        response = requests.get("http://localhost:27017", timeout=2)
        print("✅ MongoDB appears to be running")
    except:
        print("⚠️ MongoDB connection not detected (may still work)")
    
    return True

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting AI Promotion System API server...")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                print("🌐 API available at: http://localhost:8000")
                print("📚 Documentation: http://localhost:8000/docs")
                return process
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("❌ Server not responding")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def run_quick_test():
    """Run a quick API test"""
    print("\n🧪 Running quick API test...")
    
    try:
        # Test basic endpoints
        endpoints = [
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/api/data/products"),
            ("GET", "/api/data/users"),
        ]
        
        for method, endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint}")
                else:
                    print(f"⚠️ {endpoint} - Status: {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"❌ {endpoint} - Connection failed")
        
        print("\n🎉 Quick test completed!")
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")

def show_usage_examples():
    """Show usage examples"""
    print("\n📚 Usage Examples:")
    print("="*50)
    
    examples = [
        ("Health Check", "curl http://localhost:8000/health"),
        ("Get Products", "curl http://localhost:8000/api/data/products"),
        ("Initialize Hybrid System", "curl -X POST http://localhost:8000/api/hybrid/initialize"),
        ("Get User Recommendations", "curl http://localhost:8000/api/hybrid/user-recommendations/USER_ID"),
        ("Search Products", "curl 'http://localhost:8000/api/huggingface/search-products?query=bánh sinh nhật'"),
        ("Business Analytics", "curl http://localhost:8000/api/analytics/business-health"),
    ]
    
    for name, command in examples:
        print(f"\n{name}:")
        print(f"  {command}")
    
    print(f"\n📖 Full Documentation: http://localhost:8000/docs")
    print(f"🔧 API Testing: python test_api.py")

def main():
    """Main function"""
    print("🍰 AI Promotion System - Quick Start")
    print("="*50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment
    if not check_environment():
        return
    
    # Start server
    server_process = start_server()
    if not server_process:
        return
    
    try:
        # Run quick test
        run_quick_test()
        
        # Show usage examples
        show_usage_examples()
        
        print("\n🎉 AI Promotion System is ready!")
        print("\nPress Ctrl+C to stop the server")
        
        # Keep server running
        server_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        server_process.terminate()
        print("✅ Server stopped")

if __name__ == "__main__":
    main()
