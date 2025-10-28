"""
Unit Tests for Price Elasticity Calculator
Test coverage: Calculation logic, edge cases, validation

Author: RCM_PRICE Team
Date: 2025-10-27
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from infrastructure.ml_models.price_elasticity import (
    PriceElasticityCalculator,
    create_price_elasticity_calculator
)


class TestPriceElasticityCalculator:
    """Test suite for Price Elasticity Calculator"""
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance for testing"""
        return create_price_elasticity_calculator()
    
    @pytest.fixture
    def sample_products_df(self):
        """Create sample products data"""
        return pd.DataFrame({
            '_id': ['prod_001', 'prod_002', 'prod_003'],
            'name': ['Bánh Su Kem', 'Bánh Mì Hoa Cúc', 'Cookies'],
            'basePrice': [20000, 15000, 50000]
        })
    
    @pytest.fixture
    def sample_orders_df(self):
        """
        Create sample order data with realistic price variations
        Simulating 3 months of data
        """
        orders = []
        base_date = datetime(2024, 8, 1)
        
        # Product 1: VERY_SENSITIVE - price increase causes large demand drop
        for i in range(30):
            price = 20000 if i < 15 else 22000  # 10% price increase at day 15
            quantity = 100 if i < 15 else 70    # 30% demand drop
            
            orders.append({
                '_id': f'order_{i}_001',
                'createdAt': base_date + timedelta(days=i),
                'orderItems': [{
                    'product': 'prod_001',
                    'quantity': quantity + np.random.randint(-5, 5),
                    'total': (quantity + np.random.randint(-5, 5)) * price
                }]
            })
        
        # Product 2: MODERATE - price increase causes moderate demand change
        for i in range(30):
            price = 15000 if i < 15 else 16000  # ~6.7% price increase
            quantity = 80 if i < 15 else 70     # ~12.5% demand drop
            
            orders.append({
                '_id': f'order_{i}_002',
                'createdAt': base_date + timedelta(days=i),
                'orderItems': [{
                    'product': 'prod_002',
                    'quantity': quantity + np.random.randint(-3, 3),
                    'total': (quantity + np.random.randint(-3, 3)) * price
                }]
            })
        
        # Product 3: INSENSITIVE - price increase has little effect
        for i in range(30):
            price = 50000 if i < 15 else 55000  # 10% price increase
            quantity = 50 if i < 15 else 48     # Only 4% demand drop
            
            orders.append({
                '_id': f'order_{i}_003',
                'createdAt': base_date + timedelta(days=i),
                'orderItems': [{
                    'product': 'prod_003',
                    'quantity': quantity + np.random.randint(-2, 2),
                    'total': (quantity + np.random.randint(-2, 2)) * price
                }]
            })
        
        return pd.DataFrame(orders)
    
    def test_initialization(self, calculator):
        """Test calculator initialization"""
        assert calculator is not None
        assert calculator.is_trained == False
        assert len(calculator.product_elasticity) == 0
        assert len(calculator.elasticity_models) == 0
        assert isinstance(calculator.metrics, dict)
    
    def test_factory_function(self):
        """Test factory function creates correct instance"""
        calc = create_price_elasticity_calculator()
        assert isinstance(calc, PriceElasticityCalculator)
        assert calc.is_trained == False
    
    def test_calculate_elasticity_basic(
        self, 
        calculator, 
        sample_orders_df, 
        sample_products_df
    ):
        """Test basic elasticity calculation"""
        elasticity_results = calculator.calculate_elasticity(
            sample_orders_df,
            sample_products_df,
            min_samples=5
        )
        
        # Should calculate elasticity for all products
        assert len(elasticity_results) > 0
        assert calculator.is_trained == True
        
        # All elasticity values should be negative (law of demand)
        for elasticity in elasticity_results.values():
            assert elasticity < 0, "Elasticity should be negative"
    
    def test_calculate_elasticity_min_samples(
        self,
        calculator,
        sample_products_df
    ):
        """Test that products with insufficient samples are skipped"""
        # Create minimal order data
        minimal_orders = pd.DataFrame([{
            '_id': 'order_001',
            'createdAt': datetime.now(),
            'orderItems': [{
                'product': 'prod_001',
                'quantity': 10,
                'total': 200000
            }]
        }])
        
        elasticity_results = calculator.calculate_elasticity(
            minimal_orders,
            sample_products_df,
            min_samples=10  # Require 10 samples
        )
        
        # Should not calculate elasticity (insufficient samples)
        assert len(elasticity_results) == 0
    
    def test_get_sensitivity_category(self, calculator):
        """Test sensitivity categorization"""
        assert calculator.get_sensitivity_category(-1.8) == "VERY_SENSITIVE"
        assert calculator.get_sensitivity_category(-1.3) == "SENSITIVE"
        assert calculator.get_sensitivity_category(-0.8) == "MODERATE"
        assert calculator.get_sensitivity_category(-0.3) == "INSENSITIVE"
        assert calculator.get_sensitivity_category(-0.1) == "INSENSITIVE"
    
    def test_recommend_price_change_no_data(self, calculator):
        """Test recommendation when no elasticity data available"""
        recommendation = calculator.recommend_price_change('unknown_product', 20000)
        
        assert recommendation['can_increase'] == False
        assert 'Insufficient data' in recommendation['reason']
        assert recommendation['max_safe_price'] == 20000
    
    def test_recommend_price_change_with_data(
        self,
        calculator,
        sample_orders_df,
        sample_products_df
    ):
        """Test price recommendation with calculated elasticity"""
        # Calculate elasticity first
        calculator.calculate_elasticity(
            sample_orders_df,
            sample_products_df,
            min_samples=5
        )
        
        # Get recommendation for first product
        if len(calculator.product_elasticity) > 0:
            product_id = list(calculator.product_elasticity.keys())[0]
            recommendation = calculator.recommend_price_change(product_id, 20000)
            
            assert recommendation['can_increase'] == True
            assert recommendation['product_id'] == product_id
            assert recommendation['current_price'] == 20000
            assert recommendation['max_safe_price'] > 20000
            assert recommendation['sensitivity'] in [
                'VERY_SENSITIVE', 'SENSITIVE', 'MODERATE', 'INSENSITIVE'
            ]
            assert 0 < recommendation['max_safe_increase_pct'] <= 15
    
    def test_get_elasticity_report(
        self,
        calculator,
        sample_orders_df,
        sample_products_df
    ):
        """Test elasticity report generation"""
        # Calculate elasticity
        calculator.calculate_elasticity(
            sample_orders_df,
            sample_products_df,
            min_samples=5
        )
        
        # Generate report
        report = calculator.get_elasticity_report()
        
        assert isinstance(report, pd.DataFrame)
        assert len(report) > 0
        assert 'product_id' in report.columns
        assert 'elasticity' in report.columns
        assert 'sensitivity' in report.columns
        assert 'r_squared' in report.columns
        assert 'sample_size' in report.columns
        assert 'can_increase_price' in report.columns
    
    def test_get_elasticity_report_empty(self, calculator):
        """Test report generation with no data"""
        report = calculator.get_elasticity_report()
        
        assert isinstance(report, pd.DataFrame)
        assert len(report) == 0
    
    def test_get_summary_statistics(
        self,
        calculator,
        sample_orders_df,
        sample_products_df
    ):
        """Test summary statistics generation"""
        # Calculate elasticity
        calculator.calculate_elasticity(
            sample_orders_df,
            sample_products_df,
            min_samples=5
        )
        
        # Get summary
        summary = calculator.get_summary_statistics()
        
        assert 'total_products' in summary
        assert 'mean_elasticity' in summary
        assert 'median_elasticity' in summary
        assert 'sensitivity_distribution' in summary
        assert 'products_can_increase_price' in summary
        assert 'products_should_not_increase' in summary
        
        assert summary['total_products'] > 0
        assert summary['mean_elasticity'] < 0  # Should be negative
    
    def test_get_summary_statistics_empty(self, calculator):
        """Test summary with no data"""
        summary = calculator.get_summary_statistics()
        assert summary == {}
    
    def test_validate_elasticity_quality(
        self,
        calculator,
        sample_orders_df,
        sample_products_df
    ):
        """Test elasticity quality validation"""
        # Before training
        validation = calculator.validate_elasticity_quality()
        assert validation['is_valid'] == False
        
        # After training
        calculator.calculate_elasticity(
            sample_orders_df,
            sample_products_df,
            min_samples=5
        )
        
        validation = calculator.validate_elasticity_quality(min_r_squared=0.3)
        
        assert validation['is_valid'] == True
        assert 'total_products' in validation
        assert 'high_quality_products' in validation
        assert 'quality_rate' in validation
        assert validation['quality_rate'] >= 0
        assert validation['quality_rate'] <= 100
    
    def test_flatten_order_items(
        self,
        calculator,
        sample_orders_df
    ):
        """Test order items flattening"""
        flattened = calculator._flatten_order_items(sample_orders_df)
        
        assert isinstance(flattened, pd.DataFrame)
        assert len(flattened) > 0
        assert 'product_id' in flattened.columns
        assert 'quantity' in flattened.columns
        assert 'total' in flattened.columns
        assert 'date' in flattened.columns
    
    def test_flatten_order_items_empty(self, calculator):
        """Test flattening with empty data"""
        empty_df = pd.DataFrame()
        flattened = calculator._flatten_order_items(empty_df)
        
        assert isinstance(flattened, pd.DataFrame)
        assert len(flattened) == 0
    
    def test_flatten_order_items_invalid_structure(self, calculator):
        """Test flattening with invalid order structure"""
        invalid_orders = pd.DataFrame([{
            '_id': 'order_001',
            'createdAt': datetime.now(),
            'orderItems': 'invalid'  # Not a list
        }])
        
        flattened = calculator._flatten_order_items(invalid_orders)
        assert len(flattened) == 0
    
    def test_calculate_product_elasticity_edge_cases(self, calculator):
        """Test elasticity calculation edge cases"""
        # Empty dataframe
        empty_df = pd.DataFrame()
        elasticity, r2, mse = calculator._calculate_product_elasticity(
            empty_df, 
            'test_product'
        )
        assert elasticity is None
        
        # Single row (insufficient data)
        single_row = pd.DataFrame([{
            'order_id': 'order_001',
            'date': datetime.now().date(),
            'product_id': 'prod_001',
            'quantity': 10,
            'total': 200000
        }])
        
        elasticity, r2, mse = calculator._calculate_product_elasticity(
            single_row,
            'prod_001'
        )
        assert elasticity is None
    
    def test_recommendation_message_generation(self, calculator):
        """Test recommendation message generation for all sensitivity levels"""
        messages = []
        
        for sensitivity in ['VERY_SENSITIVE', 'SENSITIVE', 'MODERATE', 'INSENSITIVE']:
            if sensitivity == 'VERY_SENSITIVE':
                elasticity = -1.8
                max_inc = 0.02
            elif sensitivity == 'SENSITIVE':
                elasticity = -1.3
                max_inc = 0.05
            elif sensitivity == 'MODERATE':
                elasticity = -0.8
                max_inc = 0.10
            else:
                elasticity = -0.3
                max_inc = 0.15
            
            msg = calculator._generate_recommendation_message(
                sensitivity,
                elasticity,
                max_inc
            )
            
            assert isinstance(msg, str)
            assert len(msg) > 0
            messages.append(msg)
        
        # All messages should be different
        assert len(set(messages)) == 4
    
    def test_metrics_tracking(
        self,
        calculator,
        sample_orders_df,
        sample_products_df
    ):
        """Test that metrics are properly tracked during calculation"""
        calculator.calculate_elasticity(
            sample_orders_df,
            sample_products_df,
            min_samples=5
        )
        
        # Metrics should be populated
        assert len(calculator.metrics['r_squared']) > 0
        assert len(calculator.metrics['mse']) > 0
        assert len(calculator.metrics['sample_size']) > 0
        
        # All products should have metrics
        for product_id in calculator.product_elasticity.keys():
            assert product_id in calculator.metrics['r_squared']
            assert product_id in calculator.metrics['mse']
            assert product_id in calculator.metrics['sample_size']
            
            # R² should be between 0 and 1
            assert 0 <= calculator.metrics['r_squared'][product_id] <= 1
            
            # MSE should be non-negative
            assert calculator.metrics['mse'][product_id] >= 0
            
            # Sample size should be positive
            assert calculator.metrics['sample_size'][product_id] > 0


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios"""
    
    def test_realistic_bakery_scenario(self):
        """Test with realistic Vietnamese bakery data"""
        calculator = create_price_elasticity_calculator()
        
        # Realistic products
        products = pd.DataFrame({
            '_id': ['banh_su', 'banh_mi', 'cookies_premium'],
            'name': ['Bánh Su Kem', 'Bánh Mì Hoa Cúc', 'Cookies Cao Cấp'],
            'basePrice': [20000, 15000, 80000]
        })
        
        # Generate 2 months of realistic order data
        orders = []
        base_date = datetime(2024, 8, 1)
        
        for day in range(60):
            # Bánh Su: Popular, price-sensitive
            orders.append({
                '_id': f'order_day{day}_bs',
                'createdAt': base_date + timedelta(days=day),
                'orderItems': [{
                    'product': 'banh_su',
                    'quantity': 50 + np.random.randint(-10, 10),
                    'total': (50 + np.random.randint(-10, 10)) * 20000
                }]
            })
            
            # Bánh Mì: Daily staple, moderate sensitivity
            orders.append({
                '_id': f'order_day{day}_bm',
                'createdAt': base_date + timedelta(days=day),
                'orderItems': [{
                    'product': 'banh_mi',
                    'quantity': 100 + np.random.randint(-15, 15),
                    'total': (100 + np.random.randint(-15, 15)) * 15000
                }]
            })
            
            # Cookies Premium: Luxury, price-insensitive
            orders.append({
                '_id': f'order_day{day}_cp',
                'createdAt': base_date + timedelta(days=day),
                'orderItems': [{
                    'product': 'cookies_premium',
                    'quantity': 10 + np.random.randint(-2, 2),
                    'total': (10 + np.random.randint(-2, 2)) * 80000
                }]
            })
        
        orders_df = pd.DataFrame(orders)
        
        # Calculate elasticity
        results = calculator.calculate_elasticity(orders_df, products, min_samples=10)
        
        # Should have results for all products
        assert len(results) == 3
        
        # Get report
        report = calculator.get_elasticity_report()
        assert len(report) == 3
        
        # Get summary
        summary = calculator.get_summary_statistics()
        assert summary['total_products'] == 3
        
        # Validate quality
        validation = calculator.validate_elasticity_quality()
        assert validation['is_valid'] == True


if __name__ == '__main__':
    """Run tests with pytest"""
    pytest.main([__file__, '-v', '--tb=short'])
