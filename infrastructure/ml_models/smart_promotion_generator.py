"""
Week 6: Smart Promotion Generator
Generates vouchers and promotions based on pricing strategies and customer segments
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging
import random
import string

from infrastructure.ml_models.pricing_rules import SegmentPricingRules, PricingStrategy

logger = logging.getLogger(__name__)


class PromotionType(Enum):
    """Types of promotions"""
    DISCOUNT_PERCENTAGE = "DISCOUNT_PERCENTAGE"  # % off
    DISCOUNT_FIXED = "DISCOUNT_FIXED"  # Fixed amount off
    BUY_X_GET_Y = "BUY_X_GET_Y"  # Buy X get Y free
    BUNDLE = "BUNDLE"  # Bundle discount
    FREE_SHIPPING = "FREE_SHIPPING"  # Free delivery
    LOYALTY_BONUS = "LOYALTY_BONUS"  # Extra points


class PromotionGoal(Enum):
    """Goals for promotions"""
    ACQUISITION = "ACQUISITION"  # Attract new customers
    RETENTION = "RETENTION"  # Keep existing customers
    WINBACK = "WINBACK"  # Re-engage lost customers
    REVENUE_MAX = "REVENUE_MAX"  # Maximize revenue
    CLEAR_INVENTORY = "CLEAR_INVENTORY"  # Move slow products


@dataclass
class VoucherConfig:
    """Configuration for voucher generation"""
    prefix: str = "PROMO"  # Voucher code prefix
    code_length: int = 8  # Code length (excluding prefix)
    validity_days: int = 30  # Validity period
    max_uses: int = 1  # Max uses per voucher
    min_order_value: Optional[float] = None  # Minimum order value


class SmartPromotionGenerator:
    """
    Generates intelligent promotions based on:
    - Customer segments
    - Pricing elasticity
    - Business goals
    """
    
    def __init__(self):
        """Initialize generator"""
        self.pricing_rules = SegmentPricingRules()
        logger.info("✅ Smart Promotion Generator initialized")
    
    def generate_segment_promotion(
        self,
        segment: str,
        product_ids: List[str],
        product_prices: Dict[str, float],
        elasticities: Dict[str, float],
        goal: PromotionGoal = PromotionGoal.RETENTION,
        voucher_config: Optional[VoucherConfig] = None
    ) -> Dict:
        """
        Generate promotion for specific customer segment
        
        Args:
            segment: Customer segment (VIP, REGULAR, etc.)
            product_ids: List of products to include
            product_prices: {product_id: price}
            elasticities: {product_id: elasticity}
            goal: Promotion goal
            voucher_config: Voucher configuration
            
        Returns:
            Dict with promotion details
        """
        logger.info(f"🎁 Generating promotion for {segment} segment (Goal: {goal.value})")
        
        # Get segment pricing rules
        min_change, max_change = self.pricing_rules.get_pricing_bounds(segment)
        
        # Determine promotion type and discount based on segment + goal
        promo_details = self._design_promotion(
            segment=segment,
            goal=goal,
            min_change_pct=min_change,
            max_change_pct=max_change,
            elasticities=elasticities
        )
        
        # Generate voucher codes
        config = voucher_config or VoucherConfig()
        vouchers = self._generate_voucher_codes(
            n_vouchers=len(product_ids),
            config=config
        )
        
        # Calculate discounted prices
        discounted_prices = {}
        for product_id in product_ids:
            original_price = product_prices[product_id]
            
            if promo_details['type'] == PromotionType.DISCOUNT_PERCENTAGE:
                discount_pct = promo_details['value']
                discounted_price = original_price * (1 - discount_pct)
            elif promo_details['type'] == PromotionType.DISCOUNT_FIXED:
                discount_amount = promo_details['value']
                discounted_price = max(original_price - discount_amount, 0)
            else:
                discounted_price = original_price
            
            discounted_prices[product_id] = discounted_price
        
        # Create promotion
        promotion = {
            'promotion_id': f"PROMO_{segment}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'segment': segment,
            'goal': goal.value,
            'type': promo_details['type'].value,
            'value': promo_details['value'],
            'description': promo_details['description'],
            'product_ids': product_ids,
            'original_prices': product_prices,
            'discounted_prices': discounted_prices,
            'vouchers': vouchers,
            'valid_from': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=config.validity_days)).isoformat(),
            'max_uses': config.max_uses,
            'min_order_value': config.min_order_value,
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(
            f"✅ Promotion created: {promo_details['type'].value} - "
            f"{promo_details['description']}"
        )
        
        return promotion
    
    def generate_price_increase_voucher(
        self,
        product_id: str,
        old_price: float,
        new_price: float,
        segment: str,
        voucher_config: Optional[VoucherConfig] = None
    ) -> Dict:
        """
        Generate voucher to offset price increase
        
        Strategy: When raising prices for a segment, generate vouchers
        to maintain customer satisfaction
        
        Args:
            product_id: Product ID
            old_price: Old price
            new_price: New price (higher)
            segment: Target segment
            voucher_config: Voucher config
            
        Returns:
            Dict with voucher details
        """
        price_increase = new_price - old_price
        price_increase_pct = price_increase / old_price
        
        logger.info(
            f"🎫 Generating price increase voucher for {product_id}: "
            f"+{price_increase_pct*100:.1f}%"
        )
        
        # Determine voucher value (offset 50-80% of increase)
        offset_pct = 0.6  # Offset 60% of increase
        voucher_value = price_increase * offset_pct
        
        # Round to nearest 1000 VND
        voucher_value = round(voucher_value / 1000) * 1000
        
        config = voucher_config or VoucherConfig()
        voucher_code = self._generate_voucher_codes(n_vouchers=1, config=config)[0]
        
        voucher = {
            'voucher_code': voucher_code,
            'type': 'PRICE_INCREASE_OFFSET',
            'product_id': product_id,
            'segment': segment,
            'old_price': old_price,
            'new_price': new_price,
            'price_increase': price_increase,
            'price_increase_pct': price_increase_pct,
            'voucher_value': voucher_value,
            'final_price': new_price - voucher_value,
            'description': f"Voucher {voucher_value:,.0f} VND to offset price increase",
            'valid_from': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=config.validity_days)).isoformat(),
            'max_uses': config.max_uses,
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(
            f"✅ Voucher created: {voucher_value:,.0f} VND "
            f"(Final price: {voucher['final_price']:,.0f} VND)"
        )
        
        return voucher
    
    def generate_winback_campaign(
        self,
        lost_customers: List[str],
        product_catalog: Dict[str, Dict],  # {product_id: {price, elasticity}}
        voucher_config: Optional[VoucherConfig] = None
    ) -> Dict:
        """
        Generate win-back campaign for LOST/AT_RISK customers
        
        Args:
            lost_customers: List of customer IDs
            product_catalog: Product info
            voucher_config: Voucher config
            
        Returns:
            Dict with campaign details
        """
        logger.info(f"🎯 Generating win-back campaign for {len(lost_customers)} customers")
        
        # LOST/AT_RISK segments need aggressive discounts (20-30%)
        discount_pct = 0.25  # 25% off
        
        # Generate unique vouchers for each customer
        config = voucher_config or VoucherConfig(validity_days=60)  # Longer validity
        vouchers = self._generate_voucher_codes(
            n_vouchers=len(lost_customers),
            config=config
        )
        
        # Create customer-voucher mapping
        customer_vouchers = {}
        for customer_id, voucher_code in zip(lost_customers, vouchers):
            customer_vouchers[customer_id] = voucher_code
        
        # Calculate discounted prices for all products
        discounted_catalog = {}
        for product_id, info in product_catalog.items():
            original_price = info['price']
            discounted_price = original_price * (1 - discount_pct)
            
            discounted_catalog[product_id] = {
                'original_price': original_price,
                'discounted_price': discounted_price,
                'discount_pct': discount_pct,
                'savings': original_price - discounted_price
            }
        
        campaign = {
            'campaign_id': f"WINBACK_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'type': 'WINBACK',
            'target_segment': 'LOST/AT_RISK',
            'n_customers': len(lost_customers),
            'discount_pct': discount_pct,
            'customer_vouchers': customer_vouchers,
            'discounted_catalog': discounted_catalog,
            'description': f"Win-back campaign: {discount_pct*100:.0f}% off entire catalog",
            'valid_from': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=config.validity_days)).isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(
            f"✅ Win-back campaign created: {discount_pct*100:.0f}% off for "
            f"{len(lost_customers)} customers"
        )
        
        return campaign
    
    def generate_bundle_promotion(
        self,
        product_bundles: List[Tuple[str, str]],  # [(product1, product2), ...]
        product_prices: Dict[str, float],
        bundle_discount_pct: float = 0.15,  # 15% off bundle
        segment: Optional[str] = None,
        voucher_config: Optional[VoucherConfig] = None
    ) -> Dict:
        """
        Generate bundle promotion (Buy together, save more)
        
        Args:
            product_bundles: List of product pairs
            product_prices: Product prices
            bundle_discount_pct: Discount for bundle
            segment: Optional target segment
            voucher_config: Voucher config
            
        Returns:
            Dict with bundle promotion
        """
        logger.info(f"📦 Generating bundle promotion: {len(product_bundles)} bundles")
        
        bundles = []
        total_savings = 0
        
        for product1, product2 in product_bundles:
            price1 = product_prices.get(product1, 0)
            price2 = product_prices.get(product2, 0)
            
            regular_total = price1 + price2
            bundle_price = regular_total * (1 - bundle_discount_pct)
            savings = regular_total - bundle_price
            total_savings += savings
            
            bundles.append({
                'products': [product1, product2],
                'regular_prices': {product1: price1, product2: price2},
                'regular_total': regular_total,
                'bundle_price': bundle_price,
                'savings': savings,
                'discount_pct': bundle_discount_pct
            })
        
        config = voucher_config or VoucherConfig()
        voucher_code = self._generate_voucher_codes(n_vouchers=1, config=config)[0]
        
        promotion = {
            'promotion_id': f"BUNDLE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'type': 'BUNDLE',
            'segment': segment or 'ALL',
            'bundles': bundles,
            'bundle_discount_pct': bundle_discount_pct,
            'total_savings': total_savings,
            'voucher_code': voucher_code,
            'description': f"Bundle & Save: {bundle_discount_pct*100:.0f}% off when buying together",
            'valid_from': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=config.validity_days)).isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(
            f"✅ Bundle promotion created: {len(bundles)} bundles, "
            f"Total savings up to {total_savings:,.0f} VND"
        )
        
        return promotion
    
    def _design_promotion(
        self,
        segment: str,
        goal: PromotionGoal,
        min_change_pct: float,
        max_change_pct: float,
        elasticities: Dict[str, float]
    ) -> Dict:
        """
        Design promotion based on segment and goal
        
        Returns:
            Dict with type, value, description
        """
        # Segment-based promotion design
        if segment == 'VIP':
            if goal == PromotionGoal.RETENTION:
                return {
                    'type': PromotionType.LOYALTY_BONUS,
                    'value': 2.0,  # 2x points
                    'description': 'VIP Loyalty Bonus: 2x points on all purchases'
                }
            else:
                return {
                    'type': PromotionType.FREE_SHIPPING,
                    'value': 0,
                    'description': 'VIP Exclusive: Free shipping on all orders'
                }
        
        elif segment in ['AT_RISK', 'LOST']:
            # Aggressive discounts
            discount_pct = abs(min_change_pct) * 0.8  # 80% of max discount
            return {
                'type': PromotionType.DISCOUNT_PERCENTAGE,
                'value': discount_pct,
                'description': f'Win-back Special: {discount_pct*100:.0f}% off'
            }
        
        elif segment == 'NEW':
            # Welcome discount
            discount_pct = abs(min_change_pct) * 0.7  # 70% of max
            return {
                'type': PromotionType.DISCOUNT_PERCENTAGE,
                'value': discount_pct,
                'description': f'Welcome Offer: {discount_pct*100:.0f}% off first order'
            }
        
        else:  # REGULAR, OCCASIONAL
            if goal == PromotionGoal.REVENUE_MAX:
                # Moderate discount
                discount_pct = abs(min_change_pct) * 0.5
                return {
                    'type': PromotionType.DISCOUNT_PERCENTAGE,
                    'value': discount_pct,
                    'description': f'Special Offer: {discount_pct*100:.0f}% off'
                }
            else:
                # Buy X Get Y
                return {
                    'type': PromotionType.BUY_X_GET_Y,
                    'value': (2, 1),  # Buy 2 get 1 free
                    'description': 'Buy 2 Get 1 Free'
                }
    
    def _generate_voucher_codes(
        self,
        n_vouchers: int,
        config: VoucherConfig
    ) -> List[str]:
        """
        Generate unique voucher codes
        
        Args:
            n_vouchers: Number of codes to generate
            config: Voucher config
            
        Returns:
            List of unique voucher codes
        """
        codes = []
        
        for _ in range(n_vouchers):
            # Generate random code
            random_part = ''.join(
                random.choices(
                    string.ascii_uppercase + string.digits,
                    k=config.code_length
                )
            )
            
            code = f"{config.prefix}_{random_part}"
            codes.append(code)
        
        return codes


# Factory function
def create_promotion_generator() -> SmartPromotionGenerator:
    """Factory function to create SmartPromotionGenerator instance"""
    return SmartPromotionGenerator()
