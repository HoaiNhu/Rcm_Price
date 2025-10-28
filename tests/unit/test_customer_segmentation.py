"""
Unit Tests for Customer Segmentation (RFM)
Test coverage: RFM calculation, clustering, segment mapping

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

from infrastructure.ml_models.customer_segmentation import (
    CustomerSegmentation,
    create_customer_segmentation
)


class TestCustomerSegmentation:
    """Test suite for Customer Segmentation"""
    
    @pytest.fixture
    def segmentation(self):
        """Create segmentation instance for testing"""
        return create_customer_segmentation(n_clusters=4)
    
    @pytest.fixture
    def sample_users_df(self):
        """Create sample users data"""
        return pd.DataFrame({
            '_id': [f'user_{i:03d}' for i in range(1, 21)],
            'name': [f'Customer {i}' for i in range(1, 21)],
            'email': [f'customer{i}@example.com' for i in range(1, 21)]
        })
    
    @pytest.fixture
    def sample_orders_df(self):
        """
        Create sample order data simulating different customer behaviors
        - VIP customers: Frequent, high value, recent
        - Regular: Medium frequency, medium value
        - Occasional: Low frequency
        - At Risk: High frequency in past, not recent
        """
        orders = []
        base_date = datetime(2024, 10, 1)
        order_id = 1
        
        # VIP Customers (user_001 to user_004)
        for user_idx in range(1, 5):
            user_id = f'user_{user_idx:03d}'
            # 15-20 orders in last 3 months, high value
            for i in range(np.random.randint(15, 21)):
                order_date = base_date + timedelta(days=np.random.randint(0, 90))
                orders.append({
                    '_id': f'order_{order_id:06d}',
                    'user': user_id,
                    'createdAt': order_date,
                    'totalPrice': np.random.randint(200000, 500000),
                    'status': 'Delivered'
                })
                order_id += 1
        
        # Regular Customers (user_005 to user_010)
        for user_idx in range(5, 11):
            user_id = f'user_{user_idx:03d}'
            # 5-10 orders, medium value
            for i in range(np.random.randint(5, 11)):
                order_date = base_date + timedelta(days=np.random.randint(0, 60))
                orders.append({
                    '_id': f'order_{order_id:06d}',
                    'user': user_id,
                    'createdAt': order_date,
                    'totalPrice': np.random.randint(100000, 250000),
                    'status': 'Delivered'
                })
                order_id += 1
        
        # Occasional Customers (user_011 to user_015)
        for user_idx in range(11, 16):
            user_id = f'user_{user_idx:03d}'
            # 1-3 orders, low value
            for i in range(np.random.randint(1, 4)):
                order_date = base_date + timedelta(days=np.random.randint(30, 120))
                orders.append({
                    '_id': f'order_{order_id:06d}',
                    'user': user_id,
                    'createdAt': order_date,
                    'totalPrice': np.random.randint(50000, 150000),
                    'status': 'Delivered'
                })
                order_id += 1
        
        # At Risk Customers (user_016 to user_018)
        for user_idx in range(16, 19):
            user_id = f'user_{user_idx:03d}'
            # Many orders but 100+ days ago
            for i in range(np.random.randint(10, 15)):
                order_date = base_date - timedelta(days=np.random.randint(100, 200))
                orders.append({
                    '_id': f'order_{order_id:06d}',
                    'user': user_id,
                    'createdAt': order_date,
                    'totalPrice': np.random.randint(150000, 350000),
                    'status': 'Delivered'
                })
                order_id += 1
        
        # New Customers (user_019 to user_020)
        for user_idx in range(19, 21):
            user_id = f'user_{user_idx:03d}'
            # 1-2 orders, very recent
            for i in range(np.random.randint(1, 3)):
                order_date = base_date + timedelta(days=np.random.randint(0, 7))
                orders.append({
                    '_id': f'order_{order_id:06d}',
                    'user': user_id,
                    'createdAt': order_date,
                    'totalPrice': np.random.randint(80000, 200000),
                    'status': 'Delivered'
                })
                order_id += 1
        
        return pd.DataFrame(orders)
    
    def test_initialization(self, segmentation):
        """Test segmentation initialization"""
        assert segmentation is not None
        assert segmentation.n_clusters == 4
        assert segmentation.is_trained == False
        assert len(segmentation.segments) == 0
        assert len(segmentation.segment_stats) == 0
    
    def test_factory_function(self):
        """Test factory function creates correct instance"""
        seg = create_customer_segmentation(n_clusters=5)
        assert isinstance(seg, CustomerSegmentation)
        assert seg.n_clusters == 5
    
    def test_segment_customers(
        self,
        segmentation,
        sample_orders_df,
        sample_users_df
    ):
        """Test basic customer segmentation"""
        segments = segmentation.segment_customers(
            sample_orders_df,
            sample_users_df
        )
        
        assert len(segments) > 0
        assert segmentation.is_trained == True
        
        # All users with orders should be segmented
        users_with_orders = sample_orders_df['user'].unique()
        for user_id in users_with_orders:
            assert user_id in segments
    
    def test_rfm_calculation(
        self,
        segmentation,
        sample_orders_df,
        sample_users_df
    ):
        """Test RFM calculation logic"""
        reference_date = datetime.now()  # Use current date for recency calculation
        
        rfm_data = segmentation._calculate_rfm(
            sample_orders_df,
            sample_users_df,
            reference_date
        )
        
        assert not rfm_data.empty
        assert 'recency' in rfm_data.columns
        assert 'frequency' in rfm_data.columns
        assert 'monetary' in rfm_data.columns
        assert 'r_score' in rfm_data.columns
        assert 'f_score' in rfm_data.columns
        assert 'm_score' in rfm_data.columns
        assert 'rfm_score' in rfm_data.columns
        
        # Recency should be non-negative
        assert (rfm_data['recency'] >= 0).all()
        
        # Frequency should be positive
        assert (rfm_data['frequency'] > 0).all()
        
        # Monetary should be positive
        assert (rfm_data['monetary'] > 0).all()
        
        # RFM scores should be 1-5
        assert (rfm_data['r_score'].between(1, 5)).all()
        assert (rfm_data['f_score'].between(1, 5)).all()
        assert (rfm_data['m_score'].between(1, 5)).all()
    
    def test_get_customer_segment(
        self,
        segmentation,
        sample_orders_df,
        sample_users_df
    ):
        """Test getting segment for a customer"""
        segmentation.segment_customers(
            sample_orders_df,
            sample_users_df
        )
        
        # Get segment for first customer
        user_id = 'user_001'
        segment = segmentation.get_customer_segment(user_id)
        
        assert segment is not None
        assert segment in ['VIP', 'REGULAR', 'OCCASIONAL', 'NEW', 'AT_RISK', 'LOST']
    
    def test_get_segment_customers(
        self,
        segmentation,
        sample_orders_df,
        sample_users_df
    ):
        """Test getting customers in a segment"""
        segmentation.segment_customers(
            sample_orders_df,
            sample_users_df
        )
        
        # Get all segments
        all_segments = set(segmentation.segments.values())
        
        for segment in all_segments:
            customers = segmentation.get_segment_customers(segment)
            assert isinstance(customers, list)
            assert len(customers) > 0
            
            # Verify all returned customers belong to this segment
            for customer_id in customers:
                assert segmentation.segments[customer_id] == segment
    
    def test_get_segment_report(
        self,
        segmentation,
        sample_orders_df,
        sample_users_df
    ):
        """Test segment report generation"""
        segmentation.segment_customers(
            sample_orders_df,
            sample_users_df
        )
        
        report = segmentation.get_segment_report()
        
        assert isinstance(report, pd.DataFrame)
        assert not report.empty
        assert 'segment' in report.columns
        assert 'customer_count' in report.columns
        assert 'total_revenue' in report.columns
        assert 'revenue_percentage' in report.columns
        assert 'price_strategy' in report.columns
        
        # Revenue percentages should sum to ~100%
        assert 95 <= report['revenue_percentage'].sum() <= 105
    
    def test_get_summary_statistics(
        self,
        segmentation,
        sample_orders_df,
        sample_users_df
    ):
        """Test summary statistics"""
        segmentation.segment_customers(
            sample_orders_df,
            sample_users_df
        )
        
        summary = segmentation.get_summary_statistics()
        
        assert 'total_customers' in summary
        assert 'total_revenue' in summary
        assert 'total_segments' in summary
        assert 'top_segment_by_revenue' in summary
        assert 'vip_customers_pct' in summary
        assert 'vip_revenue_pct' in summary
        assert 'pareto_principle_valid' in summary
        assert 'segment_distribution' in summary
        
        assert summary['total_customers'] > 0
        assert summary['total_revenue'] > 0
    
    def test_get_customer_details(
        self,
        segmentation,
        sample_orders_df,
        sample_users_df
    ):
        """Test getting customer details"""
        segmentation.segment_customers(
            sample_orders_df,
            sample_users_df
        )
        
        user_id = 'user_001'
        details = segmentation.get_customer_details(user_id)
        
        assert details is not None
        assert details['user_id'] == user_id
        assert 'segment' in details
        assert 'recency_days' in details
        assert 'frequency' in details
        assert 'monetary' in details
        assert 'rfm_score' in details
        assert 'price_strategy' in details
    
    def test_recommend_actions(self, segmentation):
        """Test action recommendations for segments"""
        for segment in ['VIP', 'REGULAR', 'OCCASIONAL', 'NEW', 'AT_RISK', 'LOST']:
            actions = segmentation.recommend_actions(segment)
            
            assert 'pricing' in actions
            assert 'promotion' in actions
            assert 'communication' in actions
            assert 'retention' in actions
            assert 'goal' in actions
            
            assert isinstance(actions['pricing'], str)
            assert len(actions['pricing']) > 0
    
    def test_segment_definitions(self, segmentation):
        """Test segment definitions are properly defined"""
        required_segments = ['VIP', 'REGULAR', 'OCCASIONAL', 'NEW', 'AT_RISK', 'LOST']
        
        for segment in required_segments:
            assert segment in segmentation.segment_definitions
            definition = segmentation.segment_definitions[segment]
            
            assert 'description' in definition
            assert 'price_strategy' in definition
            assert 'discount_eligibility' in definition
    
    def test_vip_customers_identification(
        self,
        segmentation,
        sample_orders_df,
        sample_users_df
    ):
        """Test that VIP customers are correctly identified"""
        segmentation.segment_customers(
            sample_orders_df,
            sample_users_df
        )
        
        vip_customers = segmentation.get_segment_customers('VIP')
        
        # Should have some VIP customers
        if len(vip_customers) > 0:
            # Check VIP characteristics
            for user_id in vip_customers:
                details = segmentation.get_customer_details(user_id)
                
                # VIP should have low recency, high frequency, or high monetary
                assert details['recency_days'] < 60 or details['frequency'] >= 10


class TestRFMScoring:
    """Test RFM scoring logic"""
    
    def test_recency_scoring(self):
        """Test that recency scoring is inverted (lower is better)"""
        seg = create_customer_segmentation()
        
        # Create simple data
        users_df = pd.DataFrame({
            '_id': ['user_a', 'user_b'],
            'name': ['A', 'B']
        })
        
        orders_df = pd.DataFrame([
            {
                '_id': 'order_1',
                'user': 'user_a',
                'createdAt': datetime(2024, 10, 25),  # 2 days ago
                'totalPrice': 100000,
                'status': 'Delivered'
            },
            {
                '_id': 'order_2',
                'user': 'user_b',
                'createdAt': datetime(2024, 8, 1),  # 87 days ago
                'totalPrice': 100000,
                'status': 'Delivered'
            }
        ])
        
        rfm = seg._calculate_rfm(orders_df, users_df, datetime(2024, 10, 27))
        
        # User A (recent) should have higher R score than User B
        user_a_r = rfm[rfm['user_id'] == 'user_a']['r_score'].values[0]
        user_b_r = rfm[rfm['user_id'] == 'user_b']['r_score'].values[0]
        
        assert user_a_r > user_b_r


if __name__ == '__main__':
    """Run tests with pytest"""
    pytest.main([__file__, '-v', '--tb=short'])
