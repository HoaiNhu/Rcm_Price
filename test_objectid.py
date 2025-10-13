#!/usr/bin/env python3
"""
Test ObjectId conversion
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_objectid_conversion():
    """Test ObjectId conversion"""
    try:
        print("[TEST] Testing ObjectId conversion...")
        
        from infrastructure.db.mongodb_access import mongodb_data
        
        # Get products data
        products_df = mongodb_data.get_products_data()
        print(f"[INFO] Products DataFrame shape: {products_df.shape}")
        print(f"[INFO] Products columns: {list(products_df.columns)}")
        
        # Check _id column
        if '_id' in products_df.columns:
            print(f"[INFO] _id column type: {type(products_df['_id'].iloc[0])}")
            print(f"[INFO] First _id value: {products_df['_id'].iloc[0]}")
        
        # Try to convert to dict
        try:
            products_dict = products_df.to_dict('records')
            print(f"[SUCCESS] Converted to dict: {len(products_dict)} records")
            
            # Check first record
            if products_dict:
                first_record = products_dict[0]
                print(f"[INFO] First record keys: {list(first_record.keys())}")
                if '_id' in first_record:
                    print(f"[INFO] First _id type: {type(first_record['_id'])}")
                    print(f"[INFO] First _id value: {first_record['_id']}")
                    
                    # Try to convert to string
                    try:
                        str_id = str(first_record['_id'])
                        print(f"[SUCCESS] Converted to string: {str_id}")
                    except Exception as e:
                        print(f"[ERROR] String conversion failed: {e}")
                        
        except Exception as e:
            print(f"[ERROR] Dict conversion failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_objectid_conversion()
