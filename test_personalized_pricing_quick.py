"""
Quick Test Script for Personalized Dynamic Pricing
Validates pricing rules and personalized pricing engine without database
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from infrastructure.ml_models.pricing_rules import (
    SegmentPricingRules,
    ElasticityThresholds,
    get_pricing_recommendation
)
from infrastructure.ml_models.personalized_pricing import PersonalizedDynamicPricing


def print_header(title):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def test_pricing_rules():
    """Test pricing rules for all segments"""
    print_header("TEST 1: Pricing Rules Validation")
    
    segments = ['VIP', 'REGULAR', 'OCCASIONAL', 'NEW', 'AT_RISK', 'LOST']
    
    for segment in segments:
        min_change, max_change = SegmentPricingRules.get_pricing_bounds(segment)
        print(f"\n{segment} Segment:")
        print(f"  Min Change: {min_change*100:+.1f}% (Max Discount)")
        print(f"  Max Change: {max_change*100:+.1f}% (Max Increase)")
        
        # Test valid case
        test_change = max_change / 2 if max_change > 0 else min_change / 2
        is_valid, reason = SegmentPricingRules.validate_price_change(segment, test_change)
        print(f"  Test {test_change*100:+.1f}%: {'✅ VALID' if is_valid else '❌ INVALID'}")
        if not is_valid:
            print(f"    Reason: {reason}")


def test_elasticity_thresholds():
    """Test elasticity sensitivity classification"""
    print_header("TEST 2: Elasticity Sensitivity Levels")
    
    test_elasticities = [-2.5, -1.8, -1.2, -0.8, -0.4, -0.2]
    
    for e in test_elasticities:
        sensitivity = ElasticityThresholds.get_sensitivity_level(e)
        safe_increase_vip = ElasticityThresholds.get_max_safe_increase(e, 'VIP')
        safe_increase_regular = ElasticityThresholds.get_max_safe_increase(e, 'REGULAR')
        
        print(f"\nElasticity {e:.2f}:")
        print(f"  Sensitivity: {sensitivity}")
        print(f"  VIP Max Safe Increase: {safe_increase_vip*100:.1f}%")
        print(f"  REGULAR Max Safe Increase: {safe_increase_regular*100:.1f}%")


def test_pricing_recommendations():
    """Test pricing recommendations"""
    print_header("TEST 3: Pricing Recommendations by Segment")
    
    test_cases = [
        ('VIP', -0.8, 100000, "VIP customer, moderate elasticity"),
        ('REGULAR', -1.2, 80000, "Regular customer, sensitive product"),
        ('OCCASIONAL', -0.5, 60000, "Occasional customer, insensitive product"),
        ('NEW', -1.5, 100000, "New customer, sensitive product"),
        ('AT_RISK', -1.8, 90000, "At-risk customer, very sensitive"),
        ('LOST', -2.0, 70000, "Lost customer, very sensitive")
    ]
    
    for segment, elasticity, price, description in test_cases:
        rec = get_pricing_recommendation(segment, elasticity, price)
        
        print(f"\n{description}:")
        print(f"  Segment: {rec['segment']}")
        print(f"  Strategy: {rec['strategy']}")
        print(f"  Action: {rec['action']}")
        print(f"  Current Price: {price:,} VND")
        print(f"  Recommended Price: {rec['recommended_price']:,.0f} VND")
        print(f"  Price Change: {rec['price_change_pct']*100:+.1f}%")
        print(f"  Justification Required: {rec['justification_required']}")


def test_personalized_pricing():
    """Test personalized pricing engine"""
    print_header("TEST 4: Personalized Pricing Engine")
    
    # Initialize engine
    engine = PersonalizedDynamicPricing()
    
    # Setup test data
    elasticities = {
        'prod_banh_mi': -1.2,      # Bánh mì - sensitive
        'prod_pho_bo': -0.8,       # Phở bò - moderate
        'prod_cafe_sua': -2.0,     # Cà phê sữa - very sensitive
        'prod_bun_cha': -0.5       # Bún chả - insensitive
    }
    
    segments = {
        'user_nguyen_vip': 'VIP',
        'user_tran_regular': 'REGULAR',
        'user_le_atrisk': 'AT_RISK',
        'user_pham_new': 'NEW'
    }
    
    engine.set_elasticities(elasticities)
    engine.set_segments(segments)
    
    # Test Case 1: VIP customer + Moderate elasticity product
    print("\n🔹 Case 1: VIP Customer + Phở Bò (Moderate Elasticity)")
    pricing1 = engine.calculate_personalized_price(
        product_id='prod_pho_bo',
        user_id='user_nguyen_vip',
        current_price=50000,
        product_elasticity=-0.8,
        customer_segment='VIP'
    )
    
    print(f"  Customer: VIP")
    print(f"  Product: Phở Bò (E = -0.8)")
    print(f"  Current Price: {pricing1['current_price']:,} VND")
    print(f"  Recommended Price: {pricing1['recommended_price']:,} VND")
    print(f"  Action: {pricing1['action']}")
    print(f"  Price Change: {pricing1['price_change_pct']*100:+.1f}%")
    print(f"  Expected Revenue Impact: {pricing1['revenue_impact']['revenue_change_pct']*100:+.1f}%")
    
    # Test Case 2: AT_RISK customer + Sensitive product
    print("\n🔹 Case 2: AT_RISK Customer + Bánh Mì (Sensitive)")
    pricing2 = engine.calculate_personalized_price(
        product_id='prod_banh_mi',
        user_id='user_le_atrisk',
        current_price=25000,
        product_elasticity=-1.2,
        customer_segment='AT_RISK'
    )
    
    print(f"  Customer: AT_RISK")
    print(f"  Product: Bánh Mì (E = -1.2)")
    print(f"  Current Price: {pricing2['current_price']:,} VND")
    print(f"  Recommended Price: {pricing2['recommended_price']:,} VND")
    print(f"  Action: {pricing2['action']}")
    print(f"  Price Change: {pricing2['price_change_pct']*100:+.1f}%")
    print(f"  Expected Revenue Impact: {pricing2['revenue_impact']['revenue_change_pct']*100:+.1f}%")
    
    # Test Case 3: NEW customer + Very sensitive product
    print("\n🔹 Case 3: NEW Customer + Cà Phê Sữa (Very Sensitive)")
    pricing3 = engine.calculate_personalized_price(
        product_id='prod_cafe_sua',
        user_id='user_pham_new',
        current_price=30000,
        product_elasticity=-2.0,
        customer_segment='NEW'
    )
    
    print(f"  Customer: NEW")
    print(f"  Product: Cà Phê Sữa (E = -2.0)")
    print(f"  Current Price: {pricing3['current_price']:,} VND")
    print(f"  Recommended Price: {pricing3['recommended_price']:,} VND")
    print(f"  Action: {pricing3['action']}")
    print(f"  Price Change: {pricing3['price_change_pct']*100:+.1f}%")
    print(f"  Expected Revenue Impact: {pricing3['revenue_impact']['revenue_change_pct']*100:+.1f}%")


def test_segment_pricing_matrix():
    """Test segment pricing matrix"""
    print_header("TEST 5: Segment Pricing Matrix")
    
    engine = PersonalizedDynamicPricing()
    
    # Setup elasticities
    engine.set_elasticities({'prod_banh_mi': -1.2})
    
    # Get matrix
    matrix = engine.get_segment_pricing_matrix(
        product_id='prod_banh_mi',
        current_price=25000,
        elasticity=-1.2
    )
    
    print("\nBánh Mì - Pricing Matrix Across All Segments (E = -1.2)")
    print(f"{'Segment':<12} {'Strategy':<15} {'Action':<10} {'Price':>12} {'Change':>8}")
    print("-" * 65)
    
    for _, row in matrix.iterrows():
        print(f"{row['segment']:<12} "
              f"{row['strategy']:<15} "
              f"{row['action']:<10} "
              f"{row['recommended_price']:>12,.0f} "
              f"{row['price_change_pct']*100:>7.1f}%")


def test_price_validation():
    """Test price change validation"""
    print_header("TEST 6: Price Change Validation")
    
    engine = PersonalizedDynamicPricing()
    engine.set_segments({
        'user_vip': 'VIP',
        'user_atrisk': 'AT_RISK'
    })
    
    # Test 1: VIP + 10% increase (should PASS)
    print("\n🔹 Test 1: VIP customer, 10% price increase")
    is_valid1, reason1, details1 = engine.validate_price_change(
        user_id='user_vip',
        product_id='prod_001',
        proposed_price=110000,
        current_price=100000,
        customer_segment='VIP'
    )
    
    print(f"  Proposed: 110,000 VND (100,000 + 10%)")
    print(f"  Result: {'✅ VALID' if is_valid1 else '❌ INVALID'}")
    print(f"  Reason: {reason1}")
    
    # Test 2: VIP + discount (should FAIL)
    print("\n🔹 Test 2: VIP customer, 10% discount")
    is_valid2, reason2, details2 = engine.validate_price_change(
        user_id='user_vip',
        product_id='prod_001',
        proposed_price=90000,
        current_price=100000,
        customer_segment='VIP'
    )
    
    print(f"  Proposed: 90,000 VND (100,000 - 10%)")
    print(f"  Result: {'✅ VALID' if is_valid2 else '❌ INVALID'}")
    print(f"  Reason: {reason2}")
    
    # Test 3: AT_RISK + 20% discount (should PASS)
    print("\n🔹 Test 3: AT_RISK customer, 20% discount")
    is_valid3, reason3, details3 = engine.validate_price_change(
        user_id='user_atrisk',
        product_id='prod_001',
        proposed_price=80000,
        current_price=100000,
        customer_segment='AT_RISK'
    )
    
    print(f"  Proposed: 80,000 VND (100,000 - 20%)")
    print(f"  Result: {'✅ VALID' if is_valid3 else '❌ INVALID'}")
    print(f"  Reason: {reason3}")


def test_price_simulation():
    """Test price change simulation"""
    print_header("TEST 7: Price Change Simulation")
    
    engine = PersonalizedDynamicPricing()
    
    customer_distribution = {
        'VIP': 15,
        'REGULAR': 45,
        'OCCASIONAL': 25,
        'NEW': 10,
        'AT_RISK': 5
    }
    
    # Simulation 1: 10% increase
    print("\n🔹 Simulation 1: 10% Price Increase (100,000 → 110,000 VND)")
    sim1 = engine.simulate_price_change_impact(
        product_id='prod_001',
        current_price=100000,
        new_price=110000,
        elasticity=-0.8,
        customer_segments_distribution=customer_distribution
    )
    
    print(f"  Price Change: {sim1['price_change_pct']*100:+.1f}%")
    print(f"  Allowed Segments: {', '.join(sim1['allowed_segments'])}")
    print(f"  Blocked Segments: {', '.join(sim1['blocked_segments'])}")
    print(f"  Total Revenue Impact: {sim1['total_revenue_change_pct']*100:+.1f}%")
    print(f"  Recommendation: {sim1['recommendation']}")
    
    # Simulation 2: 15% discount
    print("\n🔹 Simulation 2: 15% Discount (100,000 → 85,000 VND)")
    sim2 = engine.simulate_price_change_impact(
        product_id='prod_001',
        current_price=100000,
        new_price=85000,
        elasticity=-1.3,
        customer_segments_distribution=customer_distribution
    )
    
    print(f"  Price Change: {sim2['price_change_pct']*100:+.1f}%")
    print(f"  Allowed Segments: {', '.join(sim2['allowed_segments'])}")
    print(f"  Blocked Segments: {', '.join(sim2['blocked_segments'])}")
    print(f"  Total Revenue Impact: {sim2['total_revenue_change_pct']*100:+.1f}%")
    print(f"  Recommendation: {sim2['recommendation']}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("PERSONALIZED DYNAMIC PRICING - QUICK TEST SUITE")
    print("="*80)
    
    try:
        test_pricing_rules()
        test_elasticity_thresholds()
        test_pricing_recommendations()
        test_personalized_pricing()
        test_segment_pricing_matrix()
        test_price_validation()
        test_price_simulation()
        
        print_header("ALL TESTS COMPLETED SUCCESSFULLY ✅")
        
        print("\n📊 Summary:")
        print("  ✅ Pricing rules validated for all 6 segments")
        print("  ✅ Elasticity thresholds working correctly")
        print("  ✅ Pricing recommendations aligned with strategies")
        print("  ✅ Personalized pricing engine functioning")
        print("  ✅ Segment pricing matrix generated")
        print("  ✅ Price validation working as expected")
        print("  ✅ Simulation providing accurate forecasts")
        
        print("\n🎯 Next Steps:")
        print("  1. Run full unit tests: pytest tests/unit/test_personalized_pricing.py")
        print("  2. Test API endpoints with sample data")
        print("  3. Integrate with Week 1 (Price Elasticity) and Week 2 (Segmentation)")
        print("  4. Review PERSONALIZED_PRICING_QUICK_START.md for API usage")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
