"""
Fix Installation Script với Python 3.11
Sử dụng Python 3.11 để tránh compatibility issues
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e.stderr}")
        return False

def check_python_versions():
    """Check available Python versions"""
    print("🐍 Checking Python versions...")
    
    # Check Python 3.11
    try:
        result = subprocess.run("python3.11 --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python 3.11 found: {result.stdout.strip()}")
            return "python3.11"
    except:
        pass
    
    # Check py -3.11
    try:
        result = subprocess.run("py -3.11 --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python 3.11 found: {result.stdout.strip()}")
            return "py -3.11"
    except:
        pass
    
    # Check python311
    try:
        result = subprocess.run("python311 --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python 3.11 found: {result.stdout.strip()}")
            return "python311"
    except:
        pass
    
    print("❌ Python 3.11 not found!")
    print("Please install Python 3.11 or check your PATH")
    return None

def install_with_python311():
    """Install packages with Python 3.11"""
    python_cmd = check_python_versions()
    if not python_cmd:
        return False
    
    print(f"\n🚀 Installing packages with {python_cmd}...")
    
    # Upgrade pip first
    run_command(f"{python_cmd} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install packages that work well with Python 3.11
    packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0", 
        "python-dotenv==1.0.0",
        "pymongo==4.6.0",
        "motor==3.3.2",
        "pandas==2.1.3",
        "numpy==1.24.3",
        "scikit-learn==1.3.2",
        "xgboost==2.0.2",
        "surprise==1.1.3",
        "mlxtend==0.22.0",
        "google-generativeai==0.3.2",
        "langchain==0.0.350",
        "streamlit==1.28.1",
        "plotly==5.17.0",
        "python-multipart==0.0.6",
        "pydantic==2.5.0",
        "httpx==0.25.2"
    ]
    
    success_count = 0
    for package in packages:
        if run_command(f"{python_cmd} -m pip install {package}", f"Installing {package}"):
            success_count += 1
        else:
            print(f"⚠️ Skipping {package} due to installation error")
    
    print(f"\n✅ Installed {success_count}/{len(packages)} packages successfully!")
    return success_count > len(packages) // 2

def create_env_file():
    """Create .env file"""
    print("📝 Creating .env file...")
    
    env_content = """# Environment Variables cho AI Promotion System
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=bakery_ai

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/ai_promotion.log

# AI Model Configuration
MIN_SUPPORT_THRESHOLD=0.1
MIN_CONFIDENCE_THRESHOLD=0.5
MAX_RECOMMENDATIONS=10
MAX_COMBOS=5

# Business Rules
MIN_ORDER_COUNT_FOR_ANALYSIS=5
MIN_RATING_FOR_PROMOTION=3.0
MAX_DISCOUNT_PERCENTAGE=50
"""
    
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_installation():
    """Test if installation works"""
    print("🧪 Testing installation...")
    
    python_cmd = check_python_versions()
    if not python_cmd:
        return False
    
    try:
        # Test basic imports
        test_script = """
import fastapi
import pandas
import numpy
import sklearn
print("✅ Basic packages working!")

# Test API import
try:
    from app.main import app
    print("✅ FastAPI app can be imported!")
except ImportError as e:
    print(f"⚠️ FastAPI app import failed: {e}")
    print("This is expected if some dependencies are missing")
"""
        
        result = subprocess.run(f"{python_cmd} -c \"{test_script}\"", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def create_run_script():
    """Create run script for Python 3.11"""
    print("📝 Creating run script...")
    
    python_cmd = check_python_versions()
    if not python_cmd:
        return False
    
    run_script = f"""@echo off
echo 🚀 Starting AI Promotion System with Python 3.11...
echo.

REM Check if .env exists
if not exist ".env" (
    echo ❌ .env file not found!
    echo Please create .env file with your MongoDB URL and Gemini API key
    pause
    exit /b 1
)

REM Start the server
echo 🌐 Starting server at http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

{python_cmd} app/main_minimal.py

pause
"""
    
    try:
        with open("run_server.bat", "w", encoding="utf-8") as f:
            f.write(run_script)
        print("✅ run_server.bat created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating run script: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 AI Promotion System - Python 3.11 Fix")
    print("="*50)
    
    # Check Python 3.11
    python_cmd = check_python_versions()
    if not python_cmd:
        print("\n❌ Python 3.11 not found!")
        print("Please install Python 3.11 or check your PATH")
        return
    
    # Install packages
    if not install_with_python311():
        print("❌ Failed to install packages!")
        return
    
    # Create .env file
    create_env_file()
    
    # Create run script
    create_run_script()
    
    # Test installation
    if test_installation():
        print("\n🎉 Installation completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your MongoDB URL and Gemini API key")
        print("2. Run: run_server.bat")
        print("3. Or run: python3.11 app/main_minimal.py")
        print("4. Visit: http://localhost:8000/docs")
    else:
        print("\n⚠️ Installation completed with some issues")
        print("You can still run the basic API")

if __name__ == "__main__":
    main()
