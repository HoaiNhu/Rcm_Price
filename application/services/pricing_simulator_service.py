"""
Pricing Simulator Service
Business logic layer for Monte Carlo pricing simulation
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging

from infrastructure.ml_models.pricing_simulator import (
    PricingSimulator,
    SimulationConfig,
    create_pricing_simulator
)
from infrastructure.ml_models.personalized_pricing import PersonalizedDynamicPricing
from application.services.personalized_pricing_service import PersonalizedPricingService
from application.services.price_elasticity_service import PriceElasticityService

logger = logging.getLogger(__name__)


class PricingSimulatorService:
    """
    Service for Monte Carlo pricing simulation
    Integrates with Week 1-4 services
    """
    
    def __init__(
        self,
        pricing_service: Optional[PersonalizedPricingService] = None,
        elasticity_service: Optional[PriceElasticityService] = None
    ):
        """
        Initialize service
        
        Args:
            pricing_service: Personalized pricing service (Week 3-4)
            elasticity_service: Price elasticity service (Week 1)
        """
        self.pricing_service = pricing_service or PersonalizedPricingService()
        self.elasticity_service = elasticity_service or PriceElasticityService()
        
        # Create simulator
        pricing_engine = self.pricing_service.pricing_engine
        self.simulator = create_pricing_simulator(pricing_engine=pricing_engine)
        
        # Cache for simulation results
        self._simulation_cache: Dict = {}
        self._cache_duration = timedelta(hours=6)
        
        logger.info("✅ Pricing Simulator Service initialized")
    
    async def simulate_price_change(
        self,
        product_id: str,
        new_price: float,
        customer_segments_distribution: Optional[Dict[str, int]] = None,
        n_iterations: int = 1000,
        confidence_level: float = 0.95
    ) -> Dict:
        """
        Simulate price change with Monte Carlo
        
        Args:
            product_id: Product ID
            new_price: Proposed new price
            customer_segments_distribution: Optional segment distribution
            n_iterations: Number of simulation iterations
            confidence_level: Confidence level for intervals (default 95%)
            
        Returns:
            Dict with simulation results
        """
        logger.info(f"🎲 Simulating price change for {product_id} to {new_price:,.0f} VND")
        
        # Get current price and elasticity
        product_info = await self._get_product_info(product_id)
        current_price = product_info['current_price']
        elasticity = product_info['elasticity']
        current_demand = product_info.get('current_demand', 100)  # Default baseline
        
        # Get customer distribution
        if customer_segments_distribution is None:
            customer_segments_distribution = await self._get_default_segment_distribution()
        
        # Create config
        config = SimulationConfig(
            n_iterations=n_iterations,
            confidence_level=confidence_level
        )
        
        # Run simulation
        result = self.simulator.simulate_price_change(
            product_id=product_id,
            current_price=current_price,
            new_price=new_price,
            base_elasticity=elasticity,
            current_demand=current_demand,
            customer_segments_distribution=customer_segments_distribution,
            config=config
        )
        
        # Cache result
        cache_key = f"{product_id}_{new_price}_{n_iterations}"
        self._simulation_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        
        logger.info(
            f"✅ Simulation complete: "
            f"Risk={result['risk_metrics']['risk_level']}, "
            f"Recommendation={result['recommendation']}"
        )
        
        return result
    
    async def simulate_multiple_scenarios(
        self,
        product_id: str,
        price_scenarios: List[float],
        customer_segments_distribution: Optional[Dict[str, int]] = None,
        n_iterations: int = 1000
    ) -> pd.DataFrame:
        """
        Simulate multiple price scenarios
        
        Args:
            product_id: Product ID
            price_scenarios: List of prices to test
            customer_segments_distribution: Optional segment distribution
            n_iterations: Simulation iterations per scenario
            
        Returns:
            DataFrame comparing scenarios
        """
        logger.info(f"🎲 Simulating {len(price_scenarios)} scenarios for {product_id}")
        
        # Get product info
        product_info = await self._get_product_info(product_id)
        current_price = product_info['current_price']
        elasticity = product_info['elasticity']
        current_demand = product_info.get('current_demand', 100)
        
        # Get customer distribution
        if customer_segments_distribution is None:
            customer_segments_distribution = await self._get_default_segment_distribution()
        
        # Create config
        config = SimulationConfig(n_iterations=n_iterations)
        
        # Run multi-scenario simulation
        results_df = self.simulator.simulate_multiple_scenarios(
            product_id=product_id,
            current_price=current_price,
            price_scenarios=price_scenarios,
            base_elasticity=elasticity,
            current_demand=current_demand,
            customer_segments_distribution=customer_segments_distribution,
            config=config
        )
        
        logger.info(f"✅ Multi-scenario simulation complete")
        
        return results_df
    
    async def find_optimal_price(
        self,
        product_id: str,
        price_range: Optional[Tuple[float, float]] = None,
        n_scenarios: int = 20,
        n_iterations: int = 1000,
        customer_segments_distribution: Optional[Dict[str, int]] = None
    ) -> Dict:
        """
        Find optimal price using Monte Carlo optimization
        
        Args:
            product_id: Product ID
            price_range: (min, max) price range to search
            n_scenarios: Number of prices to test
            n_iterations: Simulation iterations per price
            customer_segments_distribution: Optional segment distribution
            
        Returns:
            Dict with optimal price and analysis
        """
        logger.info(f"🎯 Finding optimal price for {product_id}")
        
        # Get product info
        product_info = await self._get_product_info(product_id)
        current_price = product_info['current_price']
        elasticity = product_info['elasticity']
        current_demand = product_info.get('current_demand', 100)
        
        # Default price range: ±30% from current
        if price_range is None:
            min_price = current_price * 0.7
            max_price = current_price * 1.3
            price_range = (min_price, max_price)
        
        # Get customer distribution
        if customer_segments_distribution is None:
            customer_segments_distribution = await self._get_default_segment_distribution()
        
        # Create config
        config = SimulationConfig(n_iterations=n_iterations)
        
        # Find optimal
        result = self.simulator.find_optimal_price(
            product_id=product_id,
            current_price=current_price,
            base_elasticity=elasticity,
            current_demand=current_demand,
            customer_segments_distribution=customer_segments_distribution,
            price_range=price_range,
            n_scenarios=n_scenarios,
            config=config
        )
        
        logger.info(
            f"✅ Optimal price: {result['optimal_price']:,.0f} VND "
            f"({result['price_change_pct']*100:+.1f}%)"
        )
        
        return result
    
    async def get_simulation_summary(self) -> Dict:
        """
        Get summary of simulation service
        
        Returns:
            Dict with service statistics
        """
        return {
            'service': 'Pricing Simulator',
            'version': '1.0.0',
            'capabilities': [
                'Monte Carlo simulation',
                'Risk assessment',
                'Confidence intervals',
                'Multi-scenario comparison',
                'Optimal price finding'
            ],
            'cache_size': len(self._simulation_cache),
            'default_iterations': 1000,
            'default_confidence_level': 0.95,
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_all_scenarios(self) -> Dict[str, Any]:
        """
        Get all simulation scenarios for Phase 1 Enhanced LLM
        
        Returns:
            Dict with cached scenarios and summary
        """
        scenarios_list = []
        
        for cache_key, scenario_data in self._simulation_cache.items():
            scenarios_list.append({
                'cache_key': cache_key,
                'scenario': scenario_data,
                'cached_at': scenario_data.get('timestamp', 'unknown')
            })
        
        return {
            'scenarios': scenarios_list,
            'total_scenarios': len(scenarios_list),
            'cache_size': len(self._simulation_cache),
            'service_info': {
                'version': '1.0.0',
                'capabilities': ['Monte Carlo', 'Risk Assessment', 'Multi-scenario']
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def clear_cache(self):
        """Clear simulation cache"""
        cache_size = len(self._simulation_cache)
        self._simulation_cache.clear()
        logger.info(f"🗑️ Cleared {cache_size} cached simulations")
        
        return {
            'status': 'success',
            'cleared_items': cache_size
        }
    
    async def _get_product_info(self, product_id: str) -> Dict:
        """
        Get product information from database
        
        Returns:
            Dict with current_price, elasticity, current_demand
        """
        # Get elasticity from Week 1
        elasticity_data = await self.elasticity_service.get_elasticity(product_id)
        
        if not elasticity_data:
            raise ValueError(f"Product {product_id} not found or no elasticity data")
        
        return {
            'product_id': product_id,
            'current_price': elasticity_data.get('current_price', 100000),
            'elasticity': elasticity_data.get('elasticity', -1.0),
            'current_demand': elasticity_data.get('avg_quantity_sold', 100)
        }
    
    async def _get_default_segment_distribution(self) -> Dict[str, int]:
        """
        Get default customer segment distribution
        
        Returns:
            Dict mapping segment to customer count
        """
        # Default distribution based on typical Vietnamese bakery
        return {
            'VIP': 15,
            'REGULAR': 45,
            'OCCASIONAL': 25,
            'NEW': 10,
            'AT_RISK': 3,
            'LOST': 2
        }
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if 'timestamp' not in cache_entry:
            return False
        
        age = datetime.now() - cache_entry['timestamp']
        return age < self._cache_duration


# Singleton instance
_simulator_service_instance: Optional[PricingSimulatorService] = None


def get_simulator_service() -> PricingSimulatorService:
    """Get singleton instance of simulator service"""
    global _simulator_service_instance
    
    if _simulator_service_instance is None:
        # Import singleton getters for dependencies
        from application.services.personalized_pricing_service import get_pricing_service
        from application.services.price_elasticity_service import get_elasticity_service
        
        # Use singletons to avoid db_access issues
        pricing_service = get_pricing_service()
        elasticity_service = get_elasticity_service()
        
        _simulator_service_instance = PricingSimulatorService(
            pricing_service=pricing_service,
            elasticity_service=elasticity_service
        )
    
    return _simulator_service_instance

