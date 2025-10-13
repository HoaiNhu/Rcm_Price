#!/usr/bin/env python3
"""
Script chạy API với error handling tốt hơn
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Change working directory to project root
os.chdir(project_root)

def main():
    try:
        print("[STARTING] AI Promotion System API...")
        print(f"[INFO] Working directory: {os.getcwd()}")
        print(f"[INFO] Python path includes: {sys.path[0]}")
        
        # Import and start server
        from app.main import app
        import uvicorn
        
        print("[SUCCESS] App imported successfully")
        
        # Start server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            reload=False,  # Disable reload to avoid import issues
            log_level="info"
        )
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("[TIP] Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
