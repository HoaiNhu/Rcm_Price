"""
MongoDB Setup Script
Hướng dẫn cài đặt và chạy MongoDB
"""
import subprocess
import os
import sys

def check_mongodb_installed():
    """Check if MongoDB is installed"""
    print("🔍 Checking MongoDB installation...")
    
    try:
        result = subprocess.run("mongod --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MongoDB is installed!")
            print(result.stdout)
            return True
        else:
            print("❌ MongoDB not found")
            return False
    except:
        print("❌ MongoDB not found")
        return False

def check_mongodb_running():
    """Check if MongoDB is running"""
    print("\n🔍 Checking if MongoDB is running...")
    
    try:
        result = subprocess.run("netstat -an | findstr :27017", shell=True, capture_output=True, text=True)
        if ":27017" in result.stdout:
            print("✅ MongoDB is running on port 27017")
            return True
        else:
            print("❌ MongoDB is not running")
            return False
    except:
        print("❌ Could not check MongoDB status")
        return False

def start_mongodb_service():
    """Start MongoDB service"""
    print("\n🚀 Starting MongoDB service...")
    
    try:
        # Try to start MongoDB service
        result = subprocess.run("net start MongoDB", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MongoDB service started successfully!")
            return True
        else:
            print(f"❌ Failed to start MongoDB service: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error starting MongoDB service: {e}")
        return False

def start_mongodb_manual():
    """Start MongoDB manually"""
    print("\n🚀 Starting MongoDB manually...")
    
    # Create data directory
    data_dir = "C:\\data\\db"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ Created data directory: {data_dir}")
    
    try:
        # Start MongoDB daemon
        print("Starting MongoDB daemon...")
        print("Note: This will run in the background. Press Ctrl+C to stop.")
        
        # Start mongod in background
        subprocess.Popen(["mongod", "--dbpath", data_dir], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        
        print("✅ MongoDB daemon started!")
        print("You can now test the connection.")
        return True
        
    except Exception as e:
        print(f"❌ Error starting MongoDB daemon: {e}")
        return False

def provide_installation_guide():
    """Provide MongoDB installation guide"""
    print("\n📚 MongoDB Installation Guide:")
    print("="*50)
    print("1. Download MongoDB Community Server:")
    print("   https://www.mongodb.com/try/download/community")
    print()
    print("2. Install MongoDB with default settings")
    print()
    print("3. Start MongoDB service:")
    print("   - Open Command Prompt as Administrator")
    print("   - Run: net start MongoDB")
    print()
    print("4. Or start manually:")
    print("   - Create folder: C:\\data\\db")
    print("   - Run: mongod --dbpath C:\\data\\db")
    print()
    print("5. Test connection:")
    print("   - Run: mongo")
    print("   - Or test with Python script")

def suggest_alternatives():
    """Suggest alternatives to local MongoDB"""
    print("\n🔄 Alternative Solutions:")
    print("="*50)
    print("1. Use MongoDB Atlas (Cloud - Free):")
    print("   - Go to: https://cloud.mongodb.com/")
    print("   - Create free account")
    print("   - Create cluster")
    print("   - Get connection string")
    print("   - Update .env file with Atlas URL")
    print()
    print("2. Use Docker MongoDB:")
    print("   - Install Docker Desktop")
    print("   - Run: docker run -d -p 27017:27017 --name mongodb mongo")
    print()
    print("3. Use Mock Data (No MongoDB needed):")
    print("   - API will work with mock endpoints")
    print("   - No real data, but good for testing")

def main():
    """Main setup function"""
    print("🍰 MongoDB Setup for AI Promotion System")
    print("="*50)
    
    # Check if MongoDB is installed
    if not check_mongodb_installed():
        provide_installation_guide()
        suggest_alternatives()
        return
    
    # Check if MongoDB is running
    if check_mongodb_running():
        print("\n🎉 MongoDB is already running!")
        print("You can now test the API connection.")
        return
    
    # Try to start MongoDB service
    if start_mongodb_service():
        print("\n🎉 MongoDB service started!")
        return
    
    # Try to start manually
    if start_mongodb_manual():
        print("\n🎉 MongoDB started manually!")
        return
    
    # If all else fails, suggest alternatives
    print("\n❌ Could not start MongoDB automatically.")
    suggest_alternatives()

if __name__ == "__main__":
    main()
