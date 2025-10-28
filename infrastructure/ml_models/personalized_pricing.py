"""
Personalized Dynamic Pricing Engine
Combines Price Elasticity + Customer Segmentation for personalized pricing
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd

from infrastructure.ml_models.price_elasticity import PriceElasticityCalculator
from infrastructure.ml_models.customer_segmentation import CustomerSegmentation
from infrastructure.ml_models.pricing_rules import (
    SegmentPricingRules,
    ElasticityThresholds,
    get_pricing_recommendation
)

logger = logging.getLogger(__name__)


class PersonalizedDynamicPricing:
    """
    Engine để tính giá động cho từng khách hàng dựa trên:
    1. Price Elasticity của sản phẩm
    2. Customer Segment của khách hàng
    3. Pricing Rules cho từng segment
    
    Algorithm:
    1. Get product elasticity → Sensitivity level
    2. Get customer segment → Pricing constraints
    3. Apply segment-specific rules
    4. Generate personalized price
    """
    
    def __init__(self):
        """Initialize pricing engine"""
        self.elasticity_calculator = PriceElasticityCalculator()
        self.segmentation_model = CustomerSegmentation()
        
        # Cache
        self._product_elasticities: Dict = {}
        self._customer_segments: Dict = {}
        
        logger.info("✅ PersonalizedDynamicPricing engine initialized")
    
    def calculate_personalized_price(
        self,
        product_id: str,
        user_id: str,
        current_price: float,
        product_elasticity: Optional[float] = None,
        customer_segment: Optional[str] = None
    ) -> Dict:
        """
        Tính giá động cho 1 sản phẩm cho 1 khách hàng cụ thể
        
        Args:
            product_id: Product ID
            user_id: Customer ID
            current_price: Current product price
            product_elasticity: Pre-calculated elasticity (optional)
            customer_segment: Pre-calculated segment (optional)
            
        Returns:
            Dict with personalized pricing details
        """
        try:
            # Step 1: Get product elasticity
            if product_elasticity is None:
                product_elasticity = self._product_elasticities.get(product_id, -1.0)
                logger.info(f"📊 Product {product_id} elasticity: {product_elasticity:.3f}")
            
            # Step 2: Get customer segment
            if customer_segment is None:
                customer_segment = self._customer_segments.get(user_id, 'OCCASIONAL')
                logger.info(f"👤 Customer {user_id} segment: {customer_segment}")
            
            # Step 3: Get pricing recommendation
            recommendation = get_pricing_recommendation(
                segment=customer_segment,
                elasticity=product_elasticity,
                current_price=current_price
            )
            
            # Step 4: Add metadata
            recommendation['product_id'] = product_id
            recommendation['user_id'] = user_id
            recommendation['timestamp'] = datetime.now().isoformat()
            
            # Step 5: Calculate revenue impact
            revenue_impact = self._estimate_revenue_impact(
                current_price=current_price,
                new_price=recommendation['recommended_price'],
                elasticity=product_elasticity
            )
            
            recommendation['revenue_impact'] = revenue_impact
            
            logger.info(
                f"💰 {user_id} ({customer_segment}) - {product_id}: "
                f"{current_price:,.0f} → {recommendation['recommended_price']:,.0f} "
                f"({recommendation['action']})"
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"❌ Error calculating personalized price: {str(e)}")
            raise
    
    def calculate_batch_pricing(
        self,
        product_prices: Dict[str, float],
        user_segments: Dict[str, str],
        product_elasticities: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Tính giá động cho nhiều sản phẩm x nhiều khách hàng
        
        Args:
            product_prices: {product_id: current_price}
            user_segments: {user_id: segment}
            product_elasticities: {product_id: elasticity}
            
        Returns:
            DataFrame with pricing matrix
        """
        try:
            logger.info(
                f"🔄 Batch pricing: {len(product_prices)} products x {len(user_segments)} customers"
            )
            
            results = []
            
            for user_id, segment in user_segments.items():
                for product_id, current_price in product_prices.items():
                    elasticity = product_elasticities.get(product_id, -1.0)
                    
                    pricing = self.calculate_personalized_price(
                        product_id=product_id,
                        user_id=user_id,
                        current_price=current_price,
                        product_elasticity=elasticity,
                        customer_segment=segment
                    )
                    
                    results.append(pricing)
            
            df = pd.DataFrame(results)
            
            logger.info(f"✅ Generated {len(df)} personalized prices")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error in batch pricing: {str(e)}")
            raise
    
    def get_segment_pricing_matrix(
        self,
        product_id: str,
        current_price: float,
        elasticity: float
    ) -> pd.DataFrame:
        """
        Tạo pricing matrix cho 1 sản phẩm cho TẤT CẢ segments
        
        Args:
            product_id: Product ID
            current_price: Current price
            elasticity: Product elasticity
            
        Returns:
            DataFrame with pricing for each segment
        """
        segments = ['VIP', 'REGULAR', 'OCCASIONAL', 'NEW', 'AT_RISK', 'LOST']
        
        results = []
        
        for segment in segments:
            pricing = get_pricing_recommendation(
                segment=segment,
                elasticity=elasticity,
                current_price=current_price
            )
            
            pricing['product_id'] = product_id
            results.append(pricing)
        
        df = pd.DataFrame(results)
        
        # Sort by priority (VIP first)
        segment_priority = {s: i for i, s in enumerate(segments)}
        df['priority'] = df['segment'].map(segment_priority)
        df = df.sort_values('priority').drop('priority', axis=1)
        
        logger.info(f"📊 Pricing matrix for {product_id} across {len(segments)} segments")
        
        return df
    
    def validate_price_change(
        self,
        user_id: str,
        product_id: str,
        proposed_price: float,
        current_price: float,
        customer_segment: Optional[str] = None
    ) -> Tuple[bool, str, Dict]:
        """
        Validate if proposed price change is acceptable for customer
        
        Args:
            user_id: Customer ID
            product_id: Product ID
            proposed_price: Proposed new price
            current_price: Current price
            customer_segment: Customer segment (optional)
            
        Returns:
            (is_valid, reason, details)
        """
        try:
            # Get segment
            if customer_segment is None:
                customer_segment = self._customer_segments.get(user_id, 'OCCASIONAL')
            
            # Calculate price change percentage
            price_change_pct = (proposed_price - current_price) / current_price
            
            # Validate with segment rules
            is_valid, reason = SegmentPricingRules.validate_price_change(
                segment=customer_segment,
                price_change_pct=price_change_pct
            )
            
            details = {
                'user_id': user_id,
                'product_id': product_id,
                'segment': customer_segment,
                'current_price': current_price,
                'proposed_price': proposed_price,
                'price_change_pct': price_change_pct,
                'is_valid': is_valid,
                'reason': reason
            }
            
            if is_valid:
                logger.info(f"✅ Valid price change for {user_id}: {current_price:,.0f} → {proposed_price:,.0f}")
            else:
                logger.warning(f"⚠️ Invalid price change for {user_id}: {reason}")
            
            return is_valid, reason, details
            
        except Exception as e:
            logger.error(f"❌ Error validating price change: {str(e)}")
            return False, str(e), {}
    
    def simulate_price_change_impact(
        self,
        product_id: str,
        current_price: float,
        new_price: float,
        elasticity: float,
        customer_segments_distribution: Dict[str, int]
    ) -> Dict:
        """
        Simulate revenue impact khi thay đổi giá
        
        Args:
            product_id: Product ID
            current_price: Current price
            new_price: New price
            elasticity: Product elasticity
            customer_segments_distribution: {segment: customer_count}
            
        Returns:
            Dict with simulation results
        """
        try:
            price_change_pct = (new_price - current_price) / current_price
            
            # Calculate quantity change based on elasticity
            # Q_new = Q_old * (1 + elasticity * price_change_pct)
            quantity_change_pct = elasticity * price_change_pct
            
            total_customers = sum(customer_segments_distribution.values())
            
            # Simulate for each segment
            segment_impacts = []
            
            for segment, customer_count in customer_segments_distribution.items():
                # Check if price change is allowed for this segment
                is_valid, reason = SegmentPricingRules.validate_price_change(
                    segment=segment,
                    price_change_pct=price_change_pct
                )
                
                if is_valid:
                    # Calculate impact
                    old_revenue = current_price * customer_count
                    new_quantity = customer_count * (1 + quantity_change_pct)
                    new_revenue = new_price * new_quantity
                    revenue_change = new_revenue - old_revenue
                    
                    segment_impacts.append({
                        'segment': segment,
                        'customer_count': customer_count,
                        'is_allowed': True,
                        'old_revenue': old_revenue,
                        'new_revenue': new_revenue,
                        'revenue_change': revenue_change,
                        'revenue_change_pct': revenue_change / old_revenue if old_revenue > 0 else 0
                    })
                else:
                    # Price change not allowed for this segment
                    segment_impacts.append({
                        'segment': segment,
                        'customer_count': customer_count,
                        'is_allowed': False,
                        'reason': reason,
                        'old_revenue': current_price * customer_count,
                        'new_revenue': 0,  # No revenue if not allowed
                        'revenue_change': -current_price * customer_count,
                        'revenue_change_pct': -1.0
                    })
            
            # Aggregate results
            total_old_revenue = sum(s['old_revenue'] for s in segment_impacts)
            total_new_revenue = sum(s['new_revenue'] for s in segment_impacts)
            total_revenue_change = total_new_revenue - total_old_revenue
            
            allowed_segments = [s['segment'] for s in segment_impacts if s['is_allowed']]
            blocked_segments = [s['segment'] for s in segment_impacts if not s['is_allowed']]
            
            result = {
                'product_id': product_id,
                'current_price': current_price,
                'new_price': new_price,
                'price_change_pct': price_change_pct,
                'elasticity': elasticity,
                'quantity_change_pct': quantity_change_pct,
                'total_customers': total_customers,
                'total_old_revenue': total_old_revenue,
                'total_new_revenue': total_new_revenue,
                'total_revenue_change': total_revenue_change,
                'total_revenue_change_pct': total_revenue_change / total_old_revenue if total_old_revenue > 0 else 0,
                'allowed_segments': allowed_segments,
                'blocked_segments': blocked_segments,
                'segment_impacts': segment_impacts,
                'recommendation': 'PROCEED' if total_revenue_change > 0 else 'RECONSIDER'
            }
            
            logger.info(
                f"📊 Simulation for {product_id}: "
                f"Revenue change {total_revenue_change:,.0f} ({result['total_revenue_change_pct']*100:.1f}%)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in simulation: {str(e)}")
            raise
    
    def set_elasticities(self, elasticities: Dict[str, float]):
        """Set product elasticities cache"""
        self._product_elasticities = elasticities
        logger.info(f"📦 Cached {len(elasticities)} product elasticities")
    
    def set_segments(self, segments: Dict[str, str]):
        """Set customer segments cache"""
        self._customer_segments = segments
        logger.info(f"📦 Cached {len(segments)} customer segments")
    
    def _estimate_revenue_impact(
        self,
        current_price: float,
        new_price: float,
        elasticity: float
    ) -> Dict:
        """
        Estimate revenue impact from price change
        
        Args:
            current_price: Current price
            new_price: New price
            elasticity: Price elasticity
            
        Returns:
            Dict with revenue impact estimates
        """
        price_change_pct = (new_price - current_price) / current_price
        quantity_change_pct = elasticity * price_change_pct
        
        # Assume baseline quantity = 100
        old_quantity = 100
        new_quantity = old_quantity * (1 + quantity_change_pct)
        
        old_revenue = current_price * old_quantity
        new_revenue = new_price * new_quantity
        revenue_change = new_revenue - old_revenue
        
        return {
            'old_revenue': old_revenue,
            'new_revenue': new_revenue,
            'revenue_change': revenue_change,
            'revenue_change_pct': revenue_change / old_revenue if old_revenue > 0 else 0,
            'quantity_change_pct': quantity_change_pct,
            'is_beneficial': revenue_change > 0
        }


# Factory function
def create_personalized_pricing() -> PersonalizedDynamicPricing:
    """Factory function to create PersonalizedDynamicPricing instance"""
    return PersonalizedDynamicPricing()
