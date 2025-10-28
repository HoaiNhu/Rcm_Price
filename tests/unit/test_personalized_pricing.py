"""
Unit Tests for Personalized Dynamic Pricing
Tests pricing rules, personalized pricing engine, and integration
"""

import pytest
from infrastructure.ml_models.pricing_rules import (
    SegmentPricingRules,
    ElasticityThresholds,
    get_pricing_recommendation
)
from infrastructure.ml_models.personalized_pricing import (
    PersonalizedDynamicPricing
)


class TestPricingRules:
    """Test pricing rules engine"""
    
    def test_vip_pricing_bounds(self):
        """VIP segment should allow 0-15% increase, no discount"""
        min_change, max_change = SegmentPricingRules.get_pricing_bounds('VIP')
        
        assert min_change == 0.0  # No discount allowed
        assert max_change == 0.15  # Max 15% increase
    
    def test_atrisk_pricing_bounds(self):
        """AT_RISK segment should require 15-25% discount"""
        min_change, max_change = SegmentPricingRules.get_pricing_bounds('AT_RISK')
        
        assert min_change == -0.25  # Max 25% discount
        assert max_change == 0.0  # No increase allowed
    
    def test_validate_vip_increase(self):
        """VIP segment should accept 10% increase"""
        is_valid, reason = SegmentPricingRules.validate_price_change(
            segment='VIP',
            price_change_pct=0.10  # 10% increase
        )
        
        assert is_valid is True
        assert "Valid" in reason
    
    def test_validate_vip_discount_rejected(self):
        """VIP segment should reject ANY discount"""
        is_valid, reason = SegmentPricingRules.validate_price_change(
            segment='VIP',
            price_change_pct=-0.05  # 5% discount
        )
        
        assert is_valid is False
        assert "exceeds max allowed" in reason
    
    def test_validate_new_increase_rejected(self):
        """NEW segment should reject price increases"""
        is_valid, reason = SegmentPricingRules.validate_price_change(
            segment='NEW',
            price_change_pct=0.05  # 5% increase
        )
        
        assert is_valid is False
        assert "should receive discounts" in reason
    
    def test_validate_atrisk_minimum_discount(self):
        """AT_RISK requires minimum 15% discount"""
        # Small discount should fail
        is_valid, _ = SegmentPricingRules.validate_price_change(
            segment='AT_RISK',
            price_change_pct=-0.10  # Only 10% discount
        )
        
        assert is_valid is False
        
        # Adequate discount should pass
        is_valid, _ = SegmentPricingRules.validate_price_change(
            segment='AT_RISK',
            price_change_pct=-0.20  # 20% discount
        )
        
        assert is_valid is True
    
    def test_get_recommended_discount_sensitive_product(self):
        """Very sensitive product should get higher discount"""
        segment = 'OCCASIONAL'
        elasticity = -2.0  # Very sensitive
        
        discount = SegmentPricingRules.get_recommended_discount(segment, elasticity)
        
        # Should be towards max discount for OCCASIONAL (15%)
        assert discount > 0.10  # More than base
        assert discount <= 0.15  # Within max
    
    def test_get_recommended_discount_insensitive_product(self):
        """Insensitive product should get lower discount"""
        segment = 'OCCASIONAL'
        elasticity = -0.3  # Insensitive
        
        discount = SegmentPricingRules.get_recommended_discount(segment, elasticity)
        
        # Should be towards min discount for OCCASIONAL (5%)
        assert discount >= 0.05  # Above min
        assert discount < 0.12  # Less than high sensitivity
    
    def test_elasticity_sensitivity_levels(self):
        """Test elasticity threshold classification"""
        assert ElasticityThresholds.get_sensitivity_level(-2.0) == "VERY_SENSITIVE"
        assert ElasticityThresholds.get_sensitivity_level(-1.2) == "SENSITIVE"
        assert ElasticityThresholds.get_sensitivity_level(-0.8) == "MODERATE"
        assert ElasticityThresholds.get_sensitivity_level(-0.3) == "INSENSITIVE"
    
    def test_max_safe_increase_vip_moderate(self):
        """VIP with moderate elasticity can increase up to 8%"""
        safe_increase = ElasticityThresholds.get_max_safe_increase(
            elasticity=-0.7,  # MODERATE
            segment='VIP'
        )
        
        assert safe_increase == 0.08  # Elasticity limit for MODERATE
    
    def test_max_safe_increase_regular_sensitive(self):
        """REGULAR with sensitive product limited to 5%"""
        safe_increase = ElasticityThresholds.get_max_safe_increase(
            elasticity=-1.3,  # SENSITIVE
            segment='REGULAR'
        )
        
        assert safe_increase == 0.05  # Elasticity limit for SENSITIVE
    
    def test_pricing_recommendation_vip(self):
        """VIP should get price increase recommendation"""
        recommendation = get_pricing_recommendation(
            segment='VIP',
            elasticity=-0.8,  # Moderate
            current_price=100000
        )
        
        assert recommendation['segment'] == 'VIP'
        assert recommendation['strategy'] == 'premium'
        assert recommendation['action'] in ['INCREASE', 'MAINTAIN']
        assert recommendation['recommended_price'] >= 100000
        assert recommendation['justification_required'] is True
    
    def test_pricing_recommendation_atrisk(self):
        """AT_RISK should get discount recommendation"""
        recommendation = get_pricing_recommendation(
            segment='AT_RISK',
            elasticity=-1.2,
            current_price=100000
        )
        
        assert recommendation['segment'] == 'AT_RISK'
        assert recommendation['strategy'] == 'winback'
        assert recommendation['action'] == 'DISCOUNT'
        assert recommendation['recommended_price'] < 100000
        assert recommendation['price_change_pct'] < 0
        # Should be between 15-25% discount
        assert -0.25 <= recommendation['price_change_pct'] <= -0.15


class TestPersonalizedPricing:
    """Test personalized pricing engine"""
    
    @pytest.fixture
    def pricing_engine(self):
        """Create pricing engine"""
        return PersonalizedDynamicPricing()
    
    @pytest.fixture
    def setup_data(self, pricing_engine):
        """Setup test data"""
        # Set elasticities
        elasticities = {
            'prod_001': -1.5,  # Sensitive
            'prod_002': -0.7,  # Moderate
            'prod_003': -2.2   # Very sensitive
        }
        
        # Set segments
        segments = {
            'user_vip': 'VIP',
            'user_regular': 'REGULAR',
            'user_atrisk': 'AT_RISK',
            'user_new': 'NEW'
        }
        
        pricing_engine.set_elasticities(elasticities)
        pricing_engine.set_segments(segments)
        
        return pricing_engine
    
    def test_calculate_personalized_price_vip(self, setup_data):
        """VIP customer should get price increase for moderate elasticity"""
        pricing = setup_data.calculate_personalized_price(
            product_id='prod_002',  # Moderate elasticity
            user_id='user_vip',
            current_price=100000,
            product_elasticity=-0.7,
            customer_segment='VIP'
        )
        
        assert pricing['product_id'] == 'prod_002'
        assert pricing['user_id'] == 'user_vip'
        assert pricing['segment'] == 'VIP'
        assert pricing['action'] in ['INCREASE', 'MAINTAIN']
        assert pricing['recommended_price'] >= 100000
    
    def test_calculate_personalized_price_atrisk(self, setup_data):
        """AT_RISK customer should get strong discount"""
        pricing = setup_data.calculate_personalized_price(
            product_id='prod_001',
            user_id='user_atrisk',
            current_price=100000,
            product_elasticity=-1.5,
            customer_segment='AT_RISK'
        )
        
        assert pricing['segment'] == 'AT_RISK'
        assert pricing['action'] == 'DISCOUNT'
        assert pricing['recommended_price'] < 100000
        # Should be 15-25% discount
        discount_pct = (100000 - pricing['recommended_price']) / 100000
        assert 0.15 <= discount_pct <= 0.25
    
    def test_validate_price_change_valid(self, setup_data):
        """Valid price change should pass"""
        is_valid, reason, details = setup_data.validate_price_change(
            user_id='user_vip',
            product_id='prod_002',
            proposed_price=108000,  # 8% increase
            current_price=100000,
            customer_segment='VIP'
        )
        
        assert is_valid is True
        assert details['is_valid'] is True
    
    def test_validate_price_change_invalid(self, setup_data):
        """Invalid price change should fail"""
        is_valid, reason, details = setup_data.validate_price_change(
            user_id='user_new',
            product_id='prod_001',
            proposed_price=110000,  # 10% increase - not allowed for NEW
            current_price=100000,
            customer_segment='NEW'
        )
        
        assert is_valid is False
        assert details['is_valid'] is False
        assert "discount" in reason.lower()
    
    def test_get_segment_pricing_matrix(self, setup_data):
        """Pricing matrix should show different prices for each segment"""
        matrix = setup_data.get_segment_pricing_matrix(
            product_id='prod_001',
            current_price=100000,
            elasticity=-1.2
        )
        
        assert len(matrix) == 6  # 6 segments
        assert 'VIP' in matrix['segment'].values
        assert 'AT_RISK' in matrix['segment'].values
        
        # VIP should have highest price
        vip_row = matrix[matrix['segment'] == 'VIP'].iloc[0]
        atrisk_row = matrix[matrix['segment'] == 'AT_RISK'].iloc[0]
        
        assert vip_row['recommended_price'] > atrisk_row['recommended_price']
    
    def test_simulate_price_increase_mixed_segments(self, setup_data):
        """Simulation with price increase should block some segments"""
        customer_distribution = {
            'VIP': 20,
            'REGULAR': 40,
            'OCCASIONAL': 25,
            'NEW': 10,
            'AT_RISK': 5
        }
        
        simulation = setup_data.simulate_price_change_impact(
            product_id='prod_002',
            current_price=100000,
            new_price=110000,  # 10% increase
            elasticity=-0.8,
            customer_segments_distribution=customer_distribution
        )
        
        # VIP and REGULAR should allow
        assert 'VIP' in simulation['allowed_segments']
        assert 'REGULAR' in simulation['allowed_segments']
        
        # NEW and AT_RISK should block
        assert 'NEW' in simulation['blocked_segments']
        assert 'AT_RISK' in simulation['blocked_segments']
        
        # Should have recommendation
        assert simulation['recommendation'] in ['PROCEED', 'RECONSIDER']
    
    def test_simulate_price_decrease_all_allowed(self, setup_data):
        """Price decrease should be allowed for all segments"""
        customer_distribution = {
            'VIP': 20,
            'REGULAR': 40,
            'AT_RISK': 10
        }
        
        simulation = setup_data.simulate_price_change_impact(
            product_id='prod_001',
            current_price=100000,
            new_price=85000,  # 15% discount
            elasticity=-1.3,
            customer_segments_distribution=customer_distribution
        )
        
        # All segments should allow discounts
        assert len(simulation['blocked_segments']) == 0
        assert len(simulation['allowed_segments']) > 0


class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_vip_product(self):
        """Test complete flow for VIP customer"""
        engine = PersonalizedDynamicPricing()
        
        # Set data
        engine.set_elasticities({'prod_001': -0.8})
        engine.set_segments({'user_001': 'VIP'})
        
        # Calculate price
        pricing = engine.calculate_personalized_price(
            product_id='prod_001',
            user_id='user_001',
            current_price=100000,
            product_elasticity=-0.8,
            customer_segment='VIP'
        )
        
        # Validate can increase
        is_valid, _, _ = engine.validate_price_change(
            user_id='user_001',
            product_id='prod_001',
            proposed_price=pricing['recommended_price'],
            current_price=100000,
            customer_segment='VIP'
        )
        
        assert is_valid is True
        assert pricing['recommended_price'] >= 100000
    
    def test_end_to_end_atrisk_product(self):
        """Test complete flow for AT_RISK customer"""
        engine = PersonalizedDynamicPricing()
        
        # Set data
        engine.set_elasticities({'prod_001': -1.5})
        engine.set_segments({'user_002': 'AT_RISK'})
        
        # Calculate price
        pricing = engine.calculate_personalized_price(
            product_id='prod_001',
            user_id='user_002',
            current_price=100000,
            product_elasticity=-1.5,
            customer_segment='AT_RISK'
        )
        
        # Should recommend discount
        assert pricing['action'] == 'DISCOUNT'
        assert pricing['recommended_price'] < 100000
        
        # Validate discount
        is_valid, _, _ = engine.validate_price_change(
            user_id='user_002',
            product_id='prod_001',
            proposed_price=pricing['recommended_price'],
            current_price=100000,
            customer_segment='AT_RISK'
        )
        
        assert is_valid is True
