"""
Quick Test Script for Price Elasticity Calculator
Test basic functionality without MongoDB

Author: RCM_PRICE Team
Date: 2025-10-27
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from infrastructure.ml_models.price_elasticity import create_price_elasticity_calculator


def generate_sample_data():
    """Generate sample bakery data for testing"""
    print("📊 Generating sample data...")
    
    # Create products
    products = pd.DataFrame({
        '_id': ['banh_su', 'banh_mi', 'cookies', 'mousse'],
        'name': ['Bánh Su Kem', 'Bánh Mì Hoa Cúc', 'Cookies Chocolate', 'Mousse Dâu'],
        'basePrice': [20000, 15000, 50000, 35000],
        'category': ['Bánh Ngọt', 'Bánh Mì', 'Bánh Cookies', 'Bánh Ngọt']
    })
    
    # Generate 90 days of order data
    orders = []
    base_date = datetime(2024, 8, 1)
    
    for day in range(90):
        current_date = base_date + timedelta(days=day)
        
        # Bánh Su: Price increases after day 45, demand drops significantly
        if day < 45:
            su_price = 20000
            su_qty = 80 + np.random.randint(-10, 10)
        else:
            su_price = 23000  # 15% increase
            su_qty = 55 + np.random.randint(-8, 8)  # 31% demand drop
        
        orders.append({
            '_id': f'order_{day}_su',
            'createdAt': current_date,
            'orderItems': [{
                'product': 'banh_su',
                'quantity': su_qty,
                'total': su_qty * su_price
            }]
        })
        
        # Bánh Mì: Moderate sensitivity
        if day < 45:
            bm_price = 15000
            bm_qty = 120 + np.random.randint(-15, 15)
        else:
            bm_price = 16000  # 6.7% increase
            bm_qty = 105 + np.random.randint(-12, 12)  # 12.5% demand drop
        
        orders.append({
            '_id': f'order_{day}_bm',
            'createdAt': current_date,
            'orderItems': [{
                'product': 'banh_mi',
                'quantity': bm_qty,
                'total': bm_qty * bm_price
            }]
        })
        
        # Cookies: Premium, insensitive
        if day < 45:
            ck_price = 50000
            ck_qty = 25 + np.random.randint(-3, 3)
        else:
            ck_price = 55000  # 10% increase
            ck_qty = 24 + np.random.randint(-2, 2)  # Only 4% demand drop
        
        orders.append({
            '_id': f'order_{day}_ck',
            'createdAt': current_date,
            'orderItems': [{
                'product': 'cookies',
                'quantity': ck_qty,
                'total': ck_qty * ck_price
            }]
        })
        
        # Mousse: Sensitive
        if day < 45:
            ms_price = 35000
            ms_qty = 40 + np.random.randint(-5, 5)
        else:
            ms_price = 38000  # 8.6% increase
            ms_qty = 30 + np.random.randint(-4, 4)  # 25% demand drop
        
        orders.append({
            '_id': f'order_{day}_ms',
            'createdAt': current_date,
            'orderItems': [{
                'product': 'mousse',
                'quantity': ms_qty,
                'total': ms_qty * ms_price
            }]
        })
    
    orders_df = pd.DataFrame(orders)
    
    print(f"✅ Generated {len(products)} products and {len(orders_df)} orders")
    return products, orders_df


def test_elasticity_calculation():
    """Test 1: Basic elasticity calculation"""
    print("\n" + "="*60)
    print("TEST 1: Price Elasticity Calculation")
    print("="*60)
    
    # Create calculator
    calculator = create_price_elasticity_calculator()
    
    # Generate data
    products_df, orders_df = generate_sample_data()
    
    # Calculate elasticity
    print("\n🔍 Calculating elasticity...")
    elasticity_results = calculator.calculate_elasticity(
        orders_df,
        products_df,
        min_samples=10
    )
    
    print(f"\n✅ Calculated elasticity for {len(elasticity_results)} products:")
    for product_id, elasticity in elasticity_results.items():
        sensitivity = calculator.get_sensitivity_category(elasticity)
        print(f"  • {product_id}: E={elasticity:.3f} ({sensitivity})")
    
    return calculator, products_df


def test_recommendations(calculator, products_df):
    """Test 2: Price recommendations"""
    print("\n" + "="*60)
    print("TEST 2: Price Recommendations")
    print("="*60)
    
    for _, product in products_df.iterrows():
        product_id = product['_id']
        current_price = product['basePrice']
        
        if product_id in calculator.product_elasticity:
            print(f"\n📋 Product: {product['name']} (ID: {product_id})")
            print(f"   Current Price: {current_price:,}đ")
            
            recommendation = calculator.recommend_price_change(
                product_id,
                current_price
            )
            
            print(f"   Elasticity: {recommendation['elasticity']}")
            print(f"   Sensitivity: {recommendation['sensitivity']}")
            print(f"   Max Safe Increase: {recommendation['max_safe_increase_pct']}%")
            print(f"   Max Safe Price: {recommendation['max_safe_price']:,}đ")
            print(f"   R²: {recommendation['r_squared']}")
            print(f"\n   💡 Recommendation:")
            for line in recommendation['recommendation'].split('\n'):
                print(f"      {line}")


def test_elasticity_report(calculator):
    """Test 3: Elasticity report"""
    print("\n" + "="*60)
    print("TEST 3: Elasticity Report")
    print("="*60)
    
    report_df = calculator.get_elasticity_report()
    
    if not report_df.empty:
        print("\n📊 Detailed Report:")
        print(report_df.to_string(index=False))
    else:
        print("⚠️ No report data available")


def test_summary_statistics(calculator):
    """Test 4: Summary statistics"""
    print("\n" + "="*60)
    print("TEST 4: Summary Statistics")
    print("="*60)
    
    summary = calculator.get_summary_statistics()
    
    if summary:
        print("\n📈 Summary Statistics:")
        print(f"  Total Products: {summary['total_products']}")
        print(f"  Mean Elasticity: {summary['mean_elasticity']}")
        print(f"  Median Elasticity: {summary['median_elasticity']}")
        print(f"  Std Elasticity: {summary['std_elasticity']}")
        print(f"  Min Elasticity: {summary['min_elasticity']}")
        print(f"  Max Elasticity: {summary['max_elasticity']}")
        
        print(f"\n  Sensitivity Distribution:")
        for sensitivity, count in summary['sensitivity_distribution'].items():
            print(f"    • {sensitivity}: {count} products")
        
        print(f"\n  Products can increase price: {summary['products_can_increase_price']}")
        print(f"  Products should NOT increase: {summary['products_should_not_increase']}")
        print(f"  Mean R²: {summary['mean_r_squared']}")
    else:
        print("⚠️ No summary data available")


def test_quality_validation(calculator):
    """Test 5: Quality validation"""
    print("\n" + "="*60)
    print("TEST 5: Quality Validation")
    print("="*60)
    
    validation = calculator.validate_elasticity_quality(min_r_squared=0.3)
    
    if validation['is_valid']:
        print(f"\n✅ Quality Validation:")
        print(f"  Total Products: {validation['total_products']}")
        print(f"  High Quality Products: {validation['high_quality_products']}")
        print(f"  Low Quality Products: {validation['low_quality_products']}")
        print(f"  Quality Rate: {validation['quality_rate']}%")
        print(f"\n  💡 {validation['recommendation']}")
        
        if validation['low_quality_details']:
            print(f"\n  ⚠️ Low Quality Products:")
            for detail in validation['low_quality_details']:
                print(f"    • {detail['product_id']}: R²={detail['r_squared']}, "
                      f"Samples={detail['sample_size']}")
    else:
        print(f"❌ Validation failed: {validation['reason']}")


def test_simulation_scenario():
    """Test 6: Price change simulation scenario"""
    print("\n" + "="*60)
    print("TEST 6: Price Change Simulation")
    print("="*60)
    
    # Create new calculator with sample data
    calculator = create_price_elasticity_calculator()
    products_df, orders_df = generate_sample_data()
    
    elasticity_results = calculator.calculate_elasticity(
        orders_df,
        products_df,
        min_samples=10
    )
    
    # Simulate price change for Bánh Su
    product_id = 'banh_su'
    current_price = 20000
    new_prices = [21000, 22000, 23000, 25000]
    
    print(f"\n🎯 Simulating price changes for Bánh Su Kem")
    print(f"   Current Price: {current_price:,}đ")
    
    if product_id in calculator.product_elasticity:
        elasticity = calculator.product_elasticity[product_id]
        print(f"   Elasticity: {elasticity:.3f}")
        
        print(f"\n   Price Change Scenarios:")
        print(f"   {'New Price':>12} {'Change %':>10} {'Est. Qty Δ':>12} {'Safe?':>8}")
        print(f"   {'-'*48}")
        
        for new_price in new_prices:
            price_change_pct = (new_price - current_price) / current_price * 100
            qty_change_pct = elasticity * (price_change_pct / 100) * 100
            
            recommendation = calculator.recommend_price_change(product_id, current_price)
            is_safe = new_price <= recommendation['max_safe_price']
            
            safe_indicator = "✅" if is_safe else "⚠️"
            
            print(f"   {new_price:>12,}đ {price_change_pct:>9.1f}% "
                  f"{qty_change_pct:>11.1f}% {safe_indicator:>8}")


def main():
    """Run all tests"""
    print("\n" + "🎯"*30)
    print("PRICE ELASTICITY CALCULATOR - QUICK TEST")
    print("🎯"*30)
    
    try:
        # Test 1: Calculate elasticity
        calculator, products_df = test_elasticity_calculation()
        
        # Test 2: Recommendations
        test_recommendations(calculator, products_df)
        
        # Test 3: Report
        test_elasticity_report(calculator)
        
        # Test 4: Summary
        test_summary_statistics(calculator)
        
        # Test 5: Quality validation
        test_quality_validation(calculator)
        
        # Test 6: Simulation
        test_simulation_scenario()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print("\n📚 Next Steps:")
        print("  1. ✅ Price Elasticity Calculator implemented")
        print("  2. 🔜 Test with real MongoDB data")
        print("  3. 🔜 Test API endpoints")
        print("  4. 🔜 Proceed to Week 2: Customer Segmentation (RFM)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
