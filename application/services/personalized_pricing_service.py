"""
Personalized Dynamic Pricing Service
Orchestrates personalized pricing with MongoDB integration
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd

from infrastructure.ml_models.personalized_pricing import PersonalizedDynamicPricing
from application.services.price_elasticity_service import PriceElasticityService
from application.services.customer_segmentation_service import CustomerSegmentationService

logger = logging.getLogger(__name__)


class PersonalizedPricingService:
    """
    Service để tính giá động cá nhân hóa
    
    Features:
    - Kết hợp Price Elasticity + Customer Segmentation
    - Tự động fetch data từ MongoDB
    - Caching results
    - Batch processing
    - Validation và simulation
    """
    
    def __init__(
        self,
        elasticity_service: Optional[PriceElasticityService] = None,
        segmentation_service: Optional[CustomerSegmentationService] = None
    ):
        """
        Initialize service
        
        Args:
            elasticity_service: Price elasticity service (optional)
            segmentation_service: Customer segmentation service (optional)
        """
        self.pricing_engine = PersonalizedDynamicPricing()
        
        # Services
        self.elasticity_service = elasticity_service or PriceElasticityService()
        self.segmentation_service = segmentation_service or CustomerSegmentationService()
        
        # Cache
        self._cache: Dict = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(hours=12)
        
        logger.info("✅ PersonalizedPricingService initialized")
    
    async def get_personalized_price(
        self,
        product_id: str,
        user_id: str,
        auto_calculate: bool = True
    ) -> Dict:
        """
        Lấy giá cá nhân hóa cho 1 sản phẩm cho 1 khách hàng
        
        Args:
            product_id: Product ID
            user_id: Customer ID
            auto_calculate: Auto-run calculations if no cached data
            
        Returns:
            Dict with personalized price
        """
        try:
            # Check cache
            cache_key = f"{product_id}_{user_id}"
            
            if self._is_cache_valid() and cache_key in self._cache:
                logger.info(f"📦 Using cached price for {cache_key}")
                return self._cache[cache_key]
            
            if auto_calculate:
                await self._ensure_data_loaded()
            
            # Get product info
            product_data = self._cache.get('product_data', {}).get(product_id)
            
            if not product_data:
                raise ValueError(f"Product {product_id} not found")
            
            # Get elasticity
            elasticity = self._cache.get('elasticities', {}).get(product_id, -1.0)
            
            # Get segment
            segment = self._cache.get('segments', {}).get(user_id, 'OCCASIONAL')
            
            # Calculate personalized price
            pricing = self.pricing_engine.calculate_personalized_price(
                product_id=product_id,
                user_id=user_id,
                current_price=product_data['current_price'],
                product_elasticity=elasticity,
                customer_segment=segment
            )
            
            # Cache result
            self._cache[cache_key] = pricing
            
            logger.info(f"💰 Personalized price for {user_id} - {product_id}: {pricing['recommended_price']:,.0f}")
            
            return pricing
            
        except Exception as e:
            logger.error(f"❌ Error getting personalized price: {str(e)}")
            raise
    
    async def get_customer_catalog(
        self,
        user_id: str,
        product_ids: Optional[List[str]] = None,
        auto_calculate: bool = True
    ) -> pd.DataFrame:
        """
        Lấy catalog với giá cá nhân hóa cho 1 khách hàng
        
        Args:
            user_id: Customer ID
            product_ids: List of product IDs (optional, all if None)
            auto_calculate: Auto-run calculations if no cached data
            
        Returns:
            DataFrame with personalized catalog
        """
        try:
            logger.info(f"📋 Building personalized catalog for {user_id}")
            
            if auto_calculate:
                await self._ensure_data_loaded()
            
            # Get products
            product_data = self._cache.get('product_data', {})
            
            if product_ids:
                products = {pid: data for pid, data in product_data.items() if pid in product_ids}
            else:
                products = product_data
            
            if not products:
                logger.warning(f"⚠️ No products found")
                return pd.DataFrame()
            
            # Get prices for all products
            catalog = []
            
            for product_id, data in products.items():
                pricing = await self.get_personalized_price(
                    product_id=product_id,
                    user_id=user_id,
                    auto_calculate=False
                )
                
                catalog.append({
                    'product_id': product_id,
                    'product_name': data.get('name', 'Unknown'),
                    'segment': pricing['segment'],
                    'base_price': pricing['current_price'],
                    'personalized_price': pricing['recommended_price'],
                    'discount_pct': -pricing['price_change_pct'] * 100 if pricing['price_change_pct'] < 0 else 0,
                    'action': pricing['action'],
                    'strategy': pricing['strategy']
                })
            
            df = pd.DataFrame(catalog)
            
            logger.info(f"✅ Generated catalog with {len(df)} products for {user_id}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error building catalog: {str(e)}")
            raise
    
    async def get_pricing_summary(self) -> Dict[str, Any]:
        """
        Get personalized pricing summary for all segments (Phase 1 Enhanced LLM Integration)
        
        Returns:
            Dict with pricing matrix and rules
        """
        try:
            logger.info("💰 Getting pricing summary for Phase 1...")
            
            # Get pricing matrix
            pricing_matrix = await self.get_pricing_matrix()
            
            if not pricing_matrix or 'pricing_rules' not in pricing_matrix:
                return {
                    "error": "No pricing data available",
                    "pricing_rules": {},
                    "total_products": 0
                }
            
            logger.info(f"✅ Retrieved pricing summary for {len(pricing_matrix.get('products', []))} products")
            
            return {
                "pricing_rules": pricing_matrix.get('pricing_rules', {}),
                "segment_pricing": pricing_matrix.get('segment_pricing', {}),
                "products": pricing_matrix.get('products', []),
                "total_products": len(pricing_matrix.get('products', [])),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting pricing summary: {e}")
            return {
                "error": str(e),
                "pricing_rules": {},
                "total_products": 0
            }
    
    async def get_product_pricing_matrix(
        self,
        product_id: str,
        auto_calculate: bool = True
    ) -> pd.DataFrame:
        """
        Lấy pricing matrix cho 1 sản phẩm cho TẤT CẢ segments
        
        Args:
            product_id: Product ID
            auto_calculate: Auto-run calculations if no cached data
            
        Returns:
            DataFrame with pricing for each segment
        """
        try:
            if auto_calculate:
                await self._ensure_data_loaded()
            
            # Get product info
            product_data = self._cache.get('product_data', {}).get(product_id)
            
            if not product_data:
                raise ValueError(f"Product {product_id} not found")
            
            # Get elasticity
            elasticity = self._cache.get('elasticities', {}).get(product_id, -1.0)
            
            # Generate matrix
            matrix = self.pricing_engine.get_segment_pricing_matrix(
                product_id=product_id,
                current_price=product_data['current_price'],
                elasticity=elasticity
            )
            
            # Add product name
            matrix['product_name'] = product_data.get('name', 'Unknown')
            
            logger.info(f"📊 Pricing matrix for {product_id}")
            
            return matrix
            
        except Exception as e:
            logger.error(f"❌ Error getting pricing matrix: {str(e)}")
            raise
    
    async def validate_price_change(
        self,
        user_id: str,
        product_id: str,
        proposed_price: float,
        auto_calculate: bool = True
    ) -> Dict:
        """
        Validate if price change is acceptable for customer
        
        Args:
            user_id: Customer ID
            product_id: Product ID
            proposed_price: Proposed new price
            auto_calculate: Auto-run calculations if no cached data
            
        Returns:
            Dict with validation results
        """
        try:
            if auto_calculate:
                await self._ensure_data_loaded()
            
            # Get product info
            product_data = self._cache.get('product_data', {}).get(product_id)
            
            if not product_data:
                raise ValueError(f"Product {product_id} not found")
            
            # Get segment
            segment = self._cache.get('segments', {}).get(user_id)
            
            # Validate
            is_valid, reason, details = self.pricing_engine.validate_price_change(
                user_id=user_id,
                product_id=product_id,
                proposed_price=proposed_price,
                current_price=product_data['current_price'],
                customer_segment=segment
            )
            
            logger.info(f"{'✅' if is_valid else '⚠️'} Validation: {reason}")
            
            return details
            
        except Exception as e:
            logger.error(f"❌ Error validating price: {str(e)}")
            raise
    
    async def simulate_price_change(
        self,
        product_id: str,
        new_price: float,
        auto_calculate: bool = True
    ) -> Dict:
        """
        Simulate revenue impact of price change across all segments
        
        Args:
            product_id: Product ID
            new_price: Proposed new price
            auto_calculate: Auto-run calculations if no cached data
            
        Returns:
            Dict with simulation results
        """
        try:
            if auto_calculate:
                await self._ensure_data_loaded()
            
            # Get product info
            product_data = self._cache.get('product_data', {}).get(product_id)
            
            if not product_data:
                raise ValueError(f"Product {product_id} not found")
            
            # Get elasticity
            elasticity = self._cache.get('elasticities', {}).get(product_id, -1.0)
            
            # Get segment distribution
            segment_distribution = self._cache.get('segment_distribution', {})
            
            # Run simulation
            simulation = self.pricing_engine.simulate_price_change_impact(
                product_id=product_id,
                current_price=product_data['current_price'],
                new_price=new_price,
                elasticity=elasticity,
                customer_segments_distribution=segment_distribution
            )
            
            logger.info(f"📊 Simulation complete: {simulation['recommendation']}")
            
            return simulation
            
        except Exception as e:
            logger.error(f"❌ Error in simulation: {str(e)}")
            raise
    
    async def get_pricing_summary(
        self,
        auto_calculate: bool = True
    ) -> Dict:
        """
        Get summary statistics about personalized pricing
        
        Args:
            auto_calculate: Auto-run calculations if no cached data
            
        Returns:
            Dict with summary statistics
        """
        try:
            if auto_calculate:
                await self._ensure_data_loaded()
            
            product_count = len(self._cache.get('product_data', {}))
            customer_count = len(self._cache.get('segments', {}))
            segment_distribution = self._cache.get('segment_distribution', {})
            
            summary = {
                'total_products': product_count,
                'total_customers': customer_count,
                'total_possible_prices': product_count * customer_count,
                'segment_distribution': segment_distribution,
                'cache_valid': self._is_cache_valid(),
                'last_updated': self._cache_timestamp.isoformat() if self._cache_timestamp else None
            }
            
            logger.info(f"📊 Pricing summary: {product_count} products x {customer_count} customers")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting summary: {str(e)}")
            raise
    
    async def _ensure_data_loaded(self):
        """Ensure all required data is loaded"""
        if not self._is_cache_valid():
            logger.info("🔄 Loading pricing data...")
            
            # Load elasticities
            elasticities_result = await self.elasticity_service.calculate_all_elasticities()
            
            if 'results' in elasticities_result:
                elasticities = {
                    r['product_id']: r['elasticity']
                    for r in elasticities_result['results']
                }
            else:
                elasticities = {}
            
            # Load segments
            segments = await self.segmentation_service.segment_all_customers()
            
            # Get segment distribution
            segment_distribution = {}
            for segment in segments.values():
                segment_distribution[segment] = segment_distribution.get(segment, 0) + 1
            
            # Load product data (simplified - in real app, fetch from MongoDB)
            # For now, extract from elasticity results
            product_data = {}
            
            if 'results' in elasticities_result:
                for result in elasticities_result['results']:
                    product_data[result['product_id']] = {
                        'product_id': result['product_id'],
                        'name': result.get('product_name', result['product_id']),
                        'current_price': result.get('current_price', 0)
                    }
            
            # Update engine caches
            self.pricing_engine.set_elasticities(elasticities)
            self.pricing_engine.set_segments(segments)
            
            # Update service cache
            self._cache = {
                'elasticities': elasticities,
                'segments': segments,
                'segment_distribution': segment_distribution,
                'product_data': product_data
            }
            self._cache_timestamp = datetime.now()
            
            logger.info(
                f"✅ Loaded {len(elasticities)} elasticities, "
                f"{len(segments)} segments, "
                f"{len(product_data)} products"
            )
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self._cache_timestamp:
            return False
        
        age = datetime.now() - self._cache_timestamp
        return age < self._cache_duration
    
    def clear_cache(self):
        """Clear cache to force refresh"""
        self._cache = {}
        self._cache_timestamp = None
        logger.info("🗑️ Cache cleared")


# Factory function
def create_personalized_pricing_service(
    elasticity_service: Optional[PriceElasticityService] = None,
    segmentation_service: Optional[CustomerSegmentationService] = None
) -> PersonalizedPricingService:
    """
    Factory function to create PersonalizedPricingService instance
    
    Args:
        elasticity_service: Price elasticity service (optional)
        segmentation_service: Customer segmentation service (optional)
        
    Returns:
        PersonalizedPricingService instance
    """
    return PersonalizedPricingService(elasticity_service, segmentation_service)

# Singleton instance
_pricing_service_instance: 'PersonalizedPricingService | None' = None

def get_pricing_service() -> PersonalizedPricingService:
    """
    Get or create singleton instance of PersonalizedPricingService
    
    Returns:
        PersonalizedPricingService instance
    """
    global _pricing_service_instance
    
    if _pricing_service_instance is None:
        # Import singleton getters for dependencies
        from application.services.price_elasticity_service import get_elasticity_service
        from application.services.customer_segmentation_service import get_segmentation_service
        
        # Use singletons to avoid db_access issues
        elasticity_service = get_elasticity_service()
        segmentation_service = get_segmentation_service()
        
        _pricing_service_instance = PersonalizedPricingService(
            elasticity_service=elasticity_service,
            segmentation_service=segmentation_service
        )
    
    return _pricing_service_instance

