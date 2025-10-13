#!/usr/bin/env python3
"""
Production-ready script chạy AI Promotion System API
Không có cảnh báo, tối ưu cho deploy
"""
import sys
import os
import warnings
import logging
from pathlib import Path

# Suppress all warnings for production
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("tensorflow").setLevel(logging.ERROR)

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Change working directory to project root
os.chdir(project_root)

def main():
    try:
        print("[STARTING] AI Promotion System API (Production Mode)...")
        print(f"[INFO] Working directory: {os.getcwd()}")
        
        # Import and start server
        from app.main import app
        import uvicorn
        
        print("[SUCCESS] App imported successfully")
        
        # Start server with production settings
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            reload=False,  # Disable reload for production
            log_level="warning",  # Only show warnings and errors
            access_log=False  # Disable access logs for cleaner output
        )
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("[TIP] Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
