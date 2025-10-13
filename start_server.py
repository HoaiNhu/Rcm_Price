#!/usr/bin/env python3
"""
Script khởi động AI Promotion System API
Chạy từ thư mục gốc để tránh lỗi import module
"""
import sys
import os
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Change working directory to project root
os.chdir(project_root)

if __name__ == "__main__":
    print("🚀 Starting AI Promotion System API...")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    # Import app from the correct location
    from app.main import app
    
    # Start server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
