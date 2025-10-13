#!/usr/bin/env python3
"""
Test script để debug router issues
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test imports"""
    try:
        print("[TEST] Testing imports...")
        
        # Test basic imports
        from application.services.ai_promotion_service import create_promotion_service
        print("[SUCCESS] AI promotion service imported")
        
        from application.services.hybrid_recommender import create_hybrid_recommender
        print("[SUCCESS] Hybrid recommender imported")
        
        # Test router imports
        from app.routers import basic, hybrid, models, analytics, data, legacy
        print("[SUCCESS] All routers imported")
        
        # Test router functionality
        print("[TEST] Testing router functionality...")
        
        # Test basic router
        print(f"[INFO] Basic router: {basic.router}")
        print(f"[INFO] Data router: {data.router}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_access():
    """Test data access"""
    try:
        print("[TEST] Testing data access...")
        
        from infrastructure.db.mongodb_access import mongodb_data
        
        # Test products
        products = mongodb_data.get_products_data()
        print(f"[SUCCESS] Products data: {len(products)} records")
        
        # Test orders
        orders = mongodb_data.get_orders_data()
        print(f"[SUCCESS] Orders data: {len(orders)} records")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Data access failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("[START] Testing router system...")
    
    # Test imports
    import_success = test_imports()
    
    # Test data access
    data_success = test_data_access()
    
    if import_success and data_success:
        print("[SUCCESS] All tests passed!")
    else:
        print("[FAILED] Some tests failed!")
