#!/usr/bin/env python3
"""
Script sửa lỗi hybrid recommender initialization
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
from application.services.hybrid_recommender import HybridRecommendationSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hybrid_init():
    """Test hybrid system initialization"""
    try:
        print("🧪 Testing Hybrid System Initialization...")
        
        # Create hybrid system
        gemini_api_key = os.getenv("GEMINI_API_KEY", "test-key")
        hybrid_system = HybridRecommendationSystem(gemini_api_key)
        
        print(f"✅ Hybrid system created successfully")
        print(f"📊 TF Recommender type: {type(hybrid_system.tf_recommender)}")
        print(f"📊 HF Filter type: {type(hybrid_system.hf_filter)}")
        print(f"📊 Pricing Model type: {type(hybrid_system.pricing_model)}")
        
        # Test initialization
        print("\n🔄 Testing system initialization...")
        result = hybrid_system.initialize_system()
        
        if result:
            print("✅ Hybrid system initialized successfully!")
        else:
            print("❌ Hybrid system initialization failed")
            
        return result
        
    except Exception as e:
        print(f"❌ Error testing hybrid system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_hybrid_init()
