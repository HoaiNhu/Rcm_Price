"""
Pricing Rules Engine
Defines segment-specific pricing strategies and constraints
"""

from typing import Dict, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PricingStrategy(Enum):
    """Pricing strategies for different segments"""
    PREMIUM = "premium"  # VIP - never discount
    MODERATE = "moderate"  # REGULAR - occasional promotions
    AGGRESSIVE = "aggressive"  # OCCASIONAL - frequent promotions
    ACQUISITION = "acquisition"  # NEW - welcome offers
    WINBACK = "winback"  # AT_RISK - win-back discounts
    REACTIVATION = "reactivation"  # LOST - deep discounts


class SegmentPricingRules:
    """
    Định nghĩa pricing rules cho từng segment
    
    Rules:
    - VIP: Premium pricing, NEVER discount, có thể tăng giá
    - REGULAR: Moderate pricing, giảm giá nhỏ (0-10%)
    - OCCASIONAL: Competitive pricing, giảm giá trung bình (5-15%)
    - NEW: Acquisition pricing, welcome discount (10-20%)
    - AT_RISK: Win-back pricing, aggressive discount (15-25%)
    - LOST: Reactivation pricing, deep discount (20-30%)
    """
    
    # Segment-specific pricing constraints
    SEGMENT_RULES = {
        'VIP': {
            'strategy': PricingStrategy.PREMIUM,
            'min_discount': 0.0,  # NEVER discount for VIP
            'max_discount': 0.0,
            'min_increase': 0.0,
            'max_increase': 0.15,  # Can increase up to 15%
            'can_increase_price': True,
            'requires_justification': True,  # Must justify increases
            'priority': 1
        },
        'REGULAR': {
            'strategy': PricingStrategy.MODERATE,
            'min_discount': 0.0,
            'max_discount': 0.10,  # Max 10% discount
            'min_increase': 0.0,
            'max_increase': 0.08,  # Max 8% increase
            'can_increase_price': True,
            'requires_justification': True,
            'priority': 2
        },
        'OCCASIONAL': {
            'strategy': PricingStrategy.AGGRESSIVE,
            'min_discount': 0.05,  # Always at least 5% discount
            'max_discount': 0.15,
            'min_increase': 0.0,
            'max_increase': 0.05,  # Max 5% increase
            'can_increase_price': False,  # Better to discount
            'requires_justification': False,
            'priority': 3
        },
        'NEW': {
            'strategy': PricingStrategy.ACQUISITION,
            'min_discount': 0.10,  # Always at least 10% welcome discount
            'max_discount': 0.20,
            'min_increase': 0.0,
            'max_increase': 0.0,  # NEVER increase for new customers
            'can_increase_price': False,
            'requires_justification': False,
            'priority': 4
        },
        'AT_RISK': {
            'strategy': PricingStrategy.WINBACK,
            'min_discount': 0.15,  # Strong win-back offer
            'max_discount': 0.25,
            'min_increase': 0.0,
            'max_increase': 0.0,  # NEVER increase for at-risk
            'can_increase_price': False,
            'requires_justification': False,
            'priority': 5
        },
        'LOST': {
            'strategy': PricingStrategy.REACTIVATION,
            'min_discount': 0.20,  # Deep discount to reactivate
            'max_discount': 0.30,
            'min_increase': 0.0,
            'max_increase': 0.0,  # NEVER increase for lost customers
            'can_increase_price': False,
            'requires_justification': False,
            'priority': 6
        }
    }
    
    @classmethod
    def get_pricing_bounds(cls, segment: str) -> Tuple[float, float]:
        """
        Lấy min/max discount/increase cho segment
        
        Args:
            segment: Segment name
            
        Returns:
            (min_change, max_change) where negative = discount, positive = increase
        """
        rules = cls.SEGMENT_RULES.get(segment, cls.SEGMENT_RULES['OCCASIONAL'])
        
        if rules['can_increase_price']:
            # Can both increase and discount
            min_change = -rules['max_discount']
            max_change = rules['max_increase']
        else:
            # Can only discount
            min_change = -rules['max_discount']
            max_change = 0.0
        
        logger.info(f"📊 {segment} pricing bounds: [{min_change*100:.1f}%, {max_change*100:.1f}%]")
        
        return min_change, max_change
    
    @classmethod
    def validate_price_change(
        cls,
        segment: str,
        price_change_pct: float
    ) -> Tuple[bool, str]:
        """
        Validate if price change is allowed for segment
        
        Args:
            segment: Segment name
            price_change_pct: Proposed price change (e.g., 0.1 = 10% increase)
            
        Returns:
            (is_valid, reason)
        """
        rules = cls.SEGMENT_RULES.get(segment, cls.SEGMENT_RULES['OCCASIONAL'])
        
        # Check if increase is allowed
        if price_change_pct > 0 and not rules['can_increase_price']:
            return False, f"{segment} customers should receive discounts, not price increases"
        
        # Check bounds
        min_change, max_change = cls.get_pricing_bounds(segment)
        
        if price_change_pct < min_change:
            return False, f"Discount {price_change_pct*100:.1f}% exceeds max allowed {abs(min_change)*100:.1f}%"
        
        if price_change_pct > max_change:
            return False, f"Increase {price_change_pct*100:.1f}% exceeds max allowed {max_change*100:.1f}%"
        
        # Check minimum discount requirement
        if price_change_pct > -rules['min_discount'] and rules['min_discount'] > 0:
            return False, f"{segment} requires minimum {rules['min_discount']*100:.1f}% discount"
        
        return True, "Valid price change"
    
    @classmethod
    def get_recommended_discount(cls, segment: str, elasticity: float) -> float:
        """
        Tính discount phù hợp dựa trên segment và elasticity
        
        Args:
            segment: Segment name
            elasticity: Price elasticity value (negative)
            
        Returns:
            Recommended discount percentage (0.0 to 1.0)
        """
        rules = cls.SEGMENT_RULES.get(segment, cls.SEGMENT_RULES['OCCASIONAL'])
        
        # Base discount from segment rules
        base_discount = (rules['min_discount'] + rules['max_discount']) / 2
        
        # Adjust based on elasticity
        if elasticity < -1.5:  # Very sensitive
            # Increase discount towards max
            adjustment_factor = 0.8
            recommended = base_discount + (rules['max_discount'] - base_discount) * adjustment_factor
        elif elasticity < -1.0:  # Sensitive
            adjustment_factor = 0.5
            recommended = base_discount + (rules['max_discount'] - base_discount) * adjustment_factor
        elif elasticity < -0.5:  # Moderate
            recommended = base_discount
        else:  # Insensitive
            # Can reduce discount towards min
            adjustment_factor = 0.5
            recommended = base_discount - (base_discount - rules['min_discount']) * adjustment_factor
        
        # Ensure within bounds
        recommended = max(rules['min_discount'], min(rules['max_discount'], recommended))
        
        logger.info(f"💡 {segment} recommended discount: {recommended*100:.1f}% (elasticity: {elasticity:.2f})")
        
        return recommended
    
    @classmethod
    def get_strategy_description(cls, segment: str) -> Dict:
        """
        Get detailed description of pricing strategy for segment
        
        Args:
            segment: Segment name
            
        Returns:
            Dict with strategy details
        """
        rules = cls.SEGMENT_RULES.get(segment, cls.SEGMENT_RULES['OCCASIONAL'])
        
        return {
            'segment': segment,
            'strategy': rules['strategy'].value,
            'can_increase_price': rules['can_increase_price'],
            'discount_range': f"{rules['min_discount']*100:.0f}%-{rules['max_discount']*100:.0f}%",
            'increase_range': f"0%-{rules['max_increase']*100:.0f}%" if rules['can_increase_price'] else "N/A",
            'priority': rules['priority'],
            'requires_justification': rules['requires_justification']
        }


class ElasticityThresholds:
    """
    Định nghĩa thresholds cho price elasticity
    
    Elasticity interpretation:
    - E < -1.5: Very sensitive (VERY_SENSITIVE)
    - -1.5 ≤ E < -1.0: Sensitive (SENSITIVE)
    - -1.0 ≤ E < -0.5: Moderate (MODERATE)
    - E ≥ -0.5: Insensitive (INSENSITIVE)
    """
    
    VERY_SENSITIVE = -1.5
    SENSITIVE = -1.0
    MODERATE = -0.5
    
    @classmethod
    def get_sensitivity_level(cls, elasticity: float) -> str:
        """Get sensitivity level from elasticity value"""
        if elasticity < cls.VERY_SENSITIVE:
            return "VERY_SENSITIVE"
        elif elasticity < cls.SENSITIVE:
            return "SENSITIVE"
        elif elasticity < cls.MODERATE:
            return "MODERATE"
        else:
            return "INSENSITIVE"
    
    @classmethod
    def get_max_safe_increase(cls, elasticity: float, segment: str) -> float:
        """
        Tính mức tăng giá an toàn dựa trên elasticity và segment
        
        Args:
            elasticity: Price elasticity
            segment: Customer segment
            
        Returns:
            Max safe price increase percentage
        """
        # Get segment constraints
        _, max_increase = SegmentPricingRules.get_pricing_bounds(segment)
        
        # Calculate elasticity-based limit
        sensitivity = cls.get_sensitivity_level(elasticity)
        
        if sensitivity == "VERY_SENSITIVE":
            elasticity_limit = 0.02  # Max 2% increase
        elif sensitivity == "SENSITIVE":
            elasticity_limit = 0.05  # Max 5% increase
        elif sensitivity == "MODERATE":
            elasticity_limit = 0.08  # Max 8% increase
        else:
            elasticity_limit = 0.15  # Max 15% increase
        
        # Return the more conservative limit
        safe_increase = min(max_increase, elasticity_limit)
        
        logger.info(f"🔒 Safe increase for {segment} ({sensitivity}): {safe_increase*100:.1f}%")
        
        return safe_increase


def get_pricing_recommendation(
    segment: str,
    elasticity: float,
    current_price: float
) -> Dict:
    """
    Tổng hợp recommendation cho pricing
    
    Args:
        segment: Customer segment
        elasticity: Price elasticity
        current_price: Current product price
        
    Returns:
        Dict with pricing recommendation
    """
    rules = SegmentPricingRules.SEGMENT_RULES.get(segment)
    
    if not rules:
        logger.warning(f"⚠️ Unknown segment: {segment}, using OCCASIONAL rules")
        rules = SegmentPricingRules.SEGMENT_RULES['OCCASIONAL']
    
    # Get bounds
    min_change, max_change = SegmentPricingRules.get_pricing_bounds(segment)
    
    # Determine recommended action
    if rules['can_increase_price']:
        # Can increase - check if safe
        max_safe_increase = ElasticityThresholds.get_max_safe_increase(elasticity, segment)
        recommended_change = max_safe_increase
        action = "INCREASE" if max_safe_increase > 0 else "MAINTAIN"
    else:
        # Should discount
        recommended_discount = SegmentPricingRules.get_recommended_discount(segment, elasticity)
        recommended_change = -recommended_discount
        action = "DISCOUNT"
    
    # Calculate new price
    new_price = current_price * (1 + recommended_change)
    
    return {
        'segment': segment,
        'strategy': rules['strategy'].value,
        'action': action,
        'current_price': current_price,
        'recommended_price': round(new_price, -3),  # Round to nearest 1000
        'price_change_pct': recommended_change,
        'price_change_amount': new_price - current_price,
        'min_allowed_price': current_price * (1 + min_change),
        'max_allowed_price': current_price * (1 + max_change),
        'elasticity': elasticity,
        'sensitivity': ElasticityThresholds.get_sensitivity_level(elasticity),
        'justification_required': rules['requires_justification']
    }
