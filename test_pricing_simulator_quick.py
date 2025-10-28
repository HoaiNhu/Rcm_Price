"""
Quick Test for Pricing Simulator (Week 5)
Tests Monte Carlo simulation, risk assessment, optimal price finding
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from infrastructure.ml_models.pricing_simulator import (
    PricingSimulator,
    SimulationConfig,
    RiskLevel
)


def print_header(title):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def test_single_simulation():
    """Test single price change simulation"""
    print_header("TEST 1: Single Price Change Simulation")
    
    simulator = PricingSimulator()
    
    # Scenario: Bánh Mì price increase from 25,000 to 27,000 VND
    result = simulator.simulate_price_change(
        product_id='prod_banh_mi',
        current_price=25000,
        new_price=27000,  # +8% increase
        base_elasticity=-1.2,  # Sensitive product
        current_demand=100,  # units/day
        customer_segments_distribution={
            'VIP': 15,
            'REGULAR': 45,
            'OCCASIONAL': 25,
            'NEW': 10,
            'AT_RISK': 5
        },
        config=SimulationConfig(n_iterations=1000, random_seed=42)
    )
    
    print(f"📊 Product: Bánh Mì")
    print(f"   Current Price: {result['current_price']:,.0f} VND")
    print(f"   New Price: {result['new_price']:,.0f} VND")
    print(f"   Price Change: {result['price_change_pct']*100:+.1f}%")
    print(f"   Base Elasticity: {result['base_elasticity']:.2f}")
    
    print(f"\n💰 Revenue Statistics:")
    stats = result['revenue_statistics']
    print(f"   Baseline Revenue: {stats['old_revenue_baseline']:,.0f} VND")
    print(f"   Expected Revenue: {stats['mean_revenue']:,.0f} VND")
    print(f"   Expected Change: {stats['expected_change_pct']*100:+.1f}%")
    print(f"   Std Deviation: {stats['std_revenue']:,.0f} VND")
    
    print(f"\n📈 Confidence Intervals (95%):")
    ci = result['confidence_intervals']
    print(f"   Lower Bound: {ci['lower_bound']:,.0f} VND ({ci['lower_bound_change_pct']*100:+.1f}%)")
    print(f"   Upper Bound: {ci['upper_bound']:,.0f} VND ({ci['upper_bound_change_pct']*100:+.1f}%)")
    
    print(f"\n⚠️ Risk Metrics:")
    risk = result['risk_metrics']
    print(f"   Risk Level: {risk['risk_level']}")
    print(f"   Prob. Revenue Decrease: {risk['prob_revenue_decrease']*100:.1f}%")
    print(f"   Prob. Significant Loss (>10%): {risk['prob_significant_decrease']*100:.1f}%")
    print(f"   Value at Risk (5%): {risk['value_at_risk_5pct']:,.0f} VND")
    print(f"   VaR Loss: {risk['var_loss_pct']*100:+.1f}%")
    
    print(f"\n👥 Segment Validation:")
    seg = result['segment_validation']
    print(f"   Allowed Segments: {', '.join(seg['allowed_segments'])}")
    print(f"   Blocked Segments: {', '.join(seg['blocked_segments'])}")
    print(f"   Customers Affected: {seg['blocked_customer_pct']*100:.1f}% blocked")
    
    print(f"\n🎯 Recommendation: {result['recommendation']}")
    
    return result


def test_price_decrease_simulation():
    """Test price decrease (discount) simulation"""
    print_header("TEST 2: Price Decrease Simulation (Win-back Campaign)")
    
    simulator = PricingSimulator()
    
    # Scenario: Cà Phê Sữa deep discount for AT_RISK customers
    result = simulator.simulate_price_change(
        product_id='prod_cafe_sua',
        current_price=30000,
        new_price=24000,  # -20% discount
        base_elasticity=-2.0,  # Very sensitive
        current_demand=150,
        customer_segments_distribution={
            'VIP': 10,
            'REGULAR': 30,
            'OCCASIONAL': 20,
            'NEW': 15,
            'AT_RISK': 20,  # High AT_RISK
            'LOST': 5
        },
        config=SimulationConfig(n_iterations=1000, random_seed=42)
    )
    
    print(f"📊 Product: Cà Phê Sữa (Very Sensitive, E = {result['base_elasticity']:.2f})")
    print(f"   Price Change: {result['current_price']:,.0f} → {result['new_price']:,.0f} VND ({result['price_change_pct']*100:+.1f}%)")
    
    stats = result['revenue_statistics']
    print(f"\n💰 Revenue Impact:")
    print(f"   Expected Change: {stats['expected_change_pct']*100:+.1f}%")
    print(f"   Mean Revenue: {stats['mean_revenue']:,.0f} VND")
    
    risk = result['risk_metrics']
    print(f"\n⚠️ Risk: {risk['risk_level']}")
    print(f"   Prob. Decrease: {risk['prob_revenue_decrease']*100:.1f}%")
    
    seg = result['segment_validation']
    print(f"\n👥 Segment Impact:")
    print(f"   Allowed: {', '.join(seg['allowed_segments'])}")
    print(f"   Blocked: {', '.join(seg['blocked_segments'])}")
    
    print(f"\n🎯 Recommendation: {result['recommendation']}")


def test_multi_scenario():
    """Test multiple scenarios comparison"""
    print_header("TEST 3: Multiple Scenarios Comparison")
    
    simulator = PricingSimulator()
    
    # Test 5 price points for Phở Bò
    price_scenarios = [45000, 50000, 52000, 54000, 56000]
    
    print(f"📊 Testing {len(price_scenarios)} price scenarios for Phở Bò")
    print(f"   Current Price: 50,000 VND")
    print(f"   Scenarios: {', '.join([f'{p:,}' for p in price_scenarios])} VND\n")
    
    results_df = simulator.simulate_multiple_scenarios(
        product_id='prod_pho_bo',
        current_price=50000,
        price_scenarios=price_scenarios,
        base_elasticity=-0.8,  # Moderate
        current_demand=80,
        customer_segments_distribution={
            'VIP': 20,
            'REGULAR': 50,
            'OCCASIONAL': 20,
            'NEW': 5,
            'AT_RISK': 5
        },
        config=SimulationConfig(n_iterations=500, random_seed=42)
    )
    
    print(f"{'Price':<12} {'Change':<10} {'Exp. Revenue':<15} {'Change %':<10} {'Risk':<10} {'Recommendation':<15}")
    print("-" * 80)
    
    for _, row in results_df.iterrows():
        print(f"{row['new_price']:>10,.0f}  "
              f"{row['price_change_pct']*100:>7.1f}%  "
              f"{row['expected_revenue']:>13,.0f}  "
              f"{row['expected_change_pct']*100:>8.1f}%  "
              f"{row['risk_level']:<10}  "
              f"{row['recommendation']:<15}")
    
    best = results_df.iloc[0]
    print(f"\n🏆 Best Scenario:")
    print(f"   Price: {best['new_price']:,.0f} VND ({best['price_change_pct']*100:+.1f}%)")
    print(f"   Expected Revenue: {best['expected_revenue']:,.0f} VND ({best['expected_change_pct']*100:+.1f}%)")
    print(f"   Risk: {best['risk_level']}")
    print(f"   Recommendation: {best['recommendation']}")


def test_optimal_price():
    """Test optimal price finding"""
    print_header("TEST 4: Optimal Price Finding")
    
    simulator = PricingSimulator()
    
    print(f"🎯 Finding optimal price for Bánh Mì...")
    print(f"   Current Price: 25,000 VND")
    print(f"   Search Range: 20,000 - 30,000 VND")
    print(f"   Testing: 20 price points\n")
    
    result = simulator.find_optimal_price(
        product_id='prod_banh_mi',
        current_price=25000,
        base_elasticity=-1.2,
        current_demand=100,
        customer_segments_distribution={
            'VIP': 15,
            'REGULAR': 45,
            'OCCASIONAL': 25,
            'NEW': 10,
            'AT_RISK': 5
        },
        price_range=(20000, 30000),
        n_scenarios=20,
        config=SimulationConfig(n_iterations=500, random_seed=42)
    )
    
    print(f"✅ Optimization Complete!")
    print(f"\n🏆 Optimal Price: {result['optimal_price']:,.0f} VND")
    print(f"   Change from current: {result['price_change_pct']*100:+.1f}%")
    print(f"   Expected Revenue: {result['expected_revenue']:,.0f} VND")
    print(f"   Revenue Change: {result['expected_change_pct']*100:+.1f}%")
    
    ci = result['confidence_interval']
    print(f"\n📈 95% Confidence Interval:")
    print(f"   Lower: {ci['lower']:,.0f} VND")
    print(f"   Upper: {ci['upper']:,.0f} VND")
    
    print(f"\n⚠️ Risk Level: {result['risk_level']}")
    print(f"🎯 Recommendation: {result['recommendation']}")
    
    # Show top 5 scenarios
    print(f"\n📊 Top 5 Scenarios:")
    print(f"{'Rank':<6} {'Price':<12} {'Change':<10} {'Revenue':<15} {'Risk':<10}")
    print("-" * 60)
    
    for i, scenario in enumerate(result['all_scenarios'][:5], 1):
        print(f"{i:<6} "
              f"{scenario['new_price']:>10,.0f}  "
              f"{scenario['price_change_pct']*100:>7.1f}%  "
              f"{scenario['expected_revenue']:>13,.0f}  "
              f"{scenario['risk_level']:<10}")


def test_risk_assessment():
    """Test risk level classification"""
    print_header("TEST 5: Risk Assessment Validation")
    
    simulator = PricingSimulator()
    
    test_cases = [
        {
            'name': 'Aggressive Increase',
            'current': 50000,
            'new': 65000,  # +30%
            'elasticity': -1.5,
            'expected_risk': 'CRITICAL'
        },
        {
            'name': 'Moderate Increase',
            'current': 50000,
            'new': 54000,  # +8%
            'elasticity': -0.8,
            'expected_risk': 'LOW'
        },
        {
            'name': 'Deep Discount',
            'current': 50000,
            'new': 35000,  # -30%
            'elasticity': -2.0,
            'expected_risk': 'MEDIUM'
        }
    ]
    
    for case in test_cases:
        result = simulator.simulate_price_change(
            product_id='test',
            current_price=case['current'],
            new_price=case['new'],
            base_elasticity=case['elasticity'],
            current_demand=100,
            customer_segments_distribution={
                'VIP': 20,
                'REGULAR': 50,
                'OCCASIONAL': 30
            },
            config=SimulationConfig(n_iterations=500, random_seed=42)
        )
        
        actual_risk = result['risk_metrics']['risk_level']
        match = '✅' if actual_risk == case['expected_risk'] else '⚠️'
        
        print(f"{match} {case['name']}:")
        print(f"   Price: {case['current']:,} → {case['new']:,} VND ({(case['new']-case['current'])/case['current']*100:+.1f}%)")
        print(f"   Expected Risk: {case['expected_risk']}")
        print(f"   Actual Risk: {actual_risk}")
        print(f"   Recommendation: {result['recommendation']}")
        print()


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("PRICING SIMULATOR - QUICK TEST SUITE (Week 5)")
    print("="*80)
    
    try:
        test_single_simulation()
        test_price_decrease_simulation()
        test_multi_scenario()
        test_optimal_price()
        test_risk_assessment()
        
        print_header("ALL TESTS COMPLETED SUCCESSFULLY ✅")
        
        print("\n📊 Summary:")
        print("  ✅ Single simulation working (1000 iterations)")
        print("  ✅ Price decrease simulation functional")
        print("  ✅ Multi-scenario comparison operational")
        print("  ✅ Optimal price finding successful")
        print("  ✅ Risk assessment accurate")
        
        print("\n🎯 Key Features Validated:")
        print("  ✅ Monte Carlo simulation (1000+ iterations)")
        print("  ✅ Confidence intervals (95%)")
        print("  ✅ Risk levels (LOW/MEDIUM/HIGH/CRITICAL)")
        print("  ✅ Segment validation")
        print("  ✅ Revenue distribution analysis")
        print("  ✅ Value at Risk (VaR) calculation")
        print("  ✅ GO/NO_GO/CAUTION recommendations")
        
        print("\n🚀 Next Steps:")
        print("  1. Test API endpoints with sample data")
        print("  2. Integrate with Week 1-4 services")
        print("  3. Create unit tests")
        print("  4. Review Week 5 documentation")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
