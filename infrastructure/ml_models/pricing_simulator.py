"""
Week 5: Pricing Simulator with Monte Carlo Simulation
Simulates revenue impact với uncertainty và risk assessment
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from infrastructure.ml_models.personalized_pricing import PersonalizedDynamicPricing
from infrastructure.ml_models.pricing_rules import SegmentPricingRules

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for pricing decisions"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class SimulationConfig:
    """Configuration for Monte Carlo simulation"""
    n_iterations: int = 1000  # Number of simulation runs
    confidence_level: float = 0.95  # For confidence intervals
    elasticity_variance: float = 0.1  # Elasticity uncertainty (±10%)
    demand_variance: float = 0.15  # Demand uncertainty (±15%)
    random_seed: Optional[int] = None  # For reproducibility


class PricingSimulator:
    """
    Monte Carlo simulator for pricing decisions
    Estimates revenue distribution, risk, and confidence intervals
    """
    
    def __init__(
        self,
        pricing_engine: Optional[PersonalizedDynamicPricing] = None,
        config: Optional[SimulationConfig] = None
    ):
        """
        Initialize simulator
        
        Args:
            pricing_engine: Personalized pricing engine
            config: Simulation configuration
        """
        self.pricing_engine = pricing_engine or PersonalizedDynamicPricing()
        self.config = config or SimulationConfig()
        
        if self.config.random_seed:
            np.random.seed(self.config.random_seed)
        
        logger.info(f"🎲 Pricing Simulator initialized with {self.config.n_iterations} iterations")
    
    def simulate_price_change(
        self,
        product_id: str,
        current_price: float,
        new_price: float,
        base_elasticity: float,
        current_demand: float,
        customer_segments_distribution: Dict[str, int],
        config: Optional[SimulationConfig] = None
    ) -> Dict:
        """
        Run Monte Carlo simulation for price change
        
        Args:
            product_id: Product ID
            current_price: Current price
            new_price: New price
            base_elasticity: Base elasticity estimate
            current_demand: Current demand (units/day)
            customer_segments_distribution: {segment: customer_count}
            config: Override default config
            
        Returns:
            Dict with simulation results including:
            - revenue_distribution: Array of possible revenues
            - confidence_intervals: 95% CI for revenue
            - risk_metrics: Risk assessment
            - recommendation: GO/NO_GO/CAUTION
        """
        cfg = config or self.config
        
        logger.info(
            f"🎲 Simulating price change for {product_id}: "
            f"{current_price:,.0f} → {new_price:,.0f} VND"
        )
        
        # Calculate price change percentage
        price_change_pct = (new_price - current_price) / current_price
        
        # Validate against segment rules
        total_customers = sum(customer_segments_distribution.values())
        segment_validation = self._validate_segments(
            price_change_pct,
            customer_segments_distribution
        )
        
        # Run Monte Carlo simulation
        revenue_samples = []
        demand_samples = []
        elasticity_samples = []
        
        for i in range(cfg.n_iterations):
            # Sample elasticity with uncertainty
            sampled_elasticity = np.random.normal(
                base_elasticity,
                abs(base_elasticity) * cfg.elasticity_variance
            )
            # Keep elasticity negative
            sampled_elasticity = min(sampled_elasticity, -0.1)
            
            # Sample demand with uncertainty
            sampled_demand = np.random.normal(
                current_demand,
                current_demand * cfg.demand_variance
            )
            # Keep demand positive
            sampled_demand = max(sampled_demand, 1)
            
            # Calculate new demand based on elasticity
            demand_change_pct = sampled_elasticity * price_change_pct
            new_demand = sampled_demand * (1 + demand_change_pct)
            new_demand = max(new_demand, 0)  # Can't be negative
            
            # Calculate revenues
            old_revenue = current_price * sampled_demand
            new_revenue = new_price * new_demand
            
            # Apply segment blocking (customers who can't get new price)
            blocked_pct = segment_validation['blocked_customer_pct']
            # Blocked customers continue at old price with old demand
            blocked_revenue = current_price * sampled_demand * blocked_pct
            # Allowed customers get new price
            allowed_revenue = new_revenue * (1 - blocked_pct)
            
            total_new_revenue = blocked_revenue + allowed_revenue
            
            revenue_samples.append(total_new_revenue)
            demand_samples.append(new_demand)
            elasticity_samples.append(sampled_elasticity)
        
        revenue_samples = np.array(revenue_samples)
        old_revenue_baseline = current_price * current_demand
        
        # Calculate statistics
        mean_revenue = np.mean(revenue_samples)
        median_revenue = np.median(revenue_samples)
        std_revenue = np.std(revenue_samples)
        
        # Confidence intervals
        alpha = 1 - cfg.confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        ci_lower = np.percentile(revenue_samples, lower_percentile)
        ci_upper = np.percentile(revenue_samples, upper_percentile)
        
        # Risk metrics
        prob_revenue_decrease = np.mean(revenue_samples < old_revenue_baseline)
        prob_significant_decrease = np.mean(revenue_samples < old_revenue_baseline * 0.9)  # >10% loss
        
        # Value at Risk (VaR): worst-case at 5% probability
        var_5pct = np.percentile(revenue_samples, 5)
        
        # Expected revenue change
        expected_revenue_change = mean_revenue - old_revenue_baseline
        expected_revenue_change_pct = expected_revenue_change / old_revenue_baseline
        
        # Risk assessment
        risk_level = self._assess_risk(
            prob_revenue_decrease,
            prob_significant_decrease,
            expected_revenue_change_pct,
            segment_validation['blocked_customer_pct']
        )
        
        # Recommendation
        recommendation = self._get_recommendation(
            risk_level,
            expected_revenue_change_pct,
            prob_revenue_decrease
        )
        
        result = {
            'product_id': product_id,
            'current_price': current_price,
            'new_price': new_price,
            'price_change_pct': price_change_pct,
            'base_elasticity': base_elasticity,
            'current_demand': current_demand,
            'simulation_config': {
                'n_iterations': cfg.n_iterations,
                'confidence_level': cfg.confidence_level,
                'elasticity_variance': cfg.elasticity_variance,
                'demand_variance': cfg.demand_variance
            },
            'revenue_statistics': {
                'old_revenue_baseline': old_revenue_baseline,
                'mean_revenue': mean_revenue,
                'median_revenue': median_revenue,
                'std_revenue': std_revenue,
                'min_revenue': np.min(revenue_samples),
                'max_revenue': np.max(revenue_samples),
                'expected_change': expected_revenue_change,
                'expected_change_pct': expected_revenue_change_pct
            },
            'confidence_intervals': {
                'confidence_level': cfg.confidence_level,
                'lower_bound': ci_lower,
                'upper_bound': ci_upper,
                'lower_bound_change_pct': (ci_lower - old_revenue_baseline) / old_revenue_baseline,
                'upper_bound_change_pct': (ci_upper - old_revenue_baseline) / old_revenue_baseline
            },
            'risk_metrics': {
                'risk_level': risk_level.value,
                'prob_revenue_decrease': prob_revenue_decrease,
                'prob_significant_decrease': prob_significant_decrease,
                'value_at_risk_5pct': var_5pct,
                'var_loss_pct': (var_5pct - old_revenue_baseline) / old_revenue_baseline
            },
            'segment_validation': segment_validation,
            'recommendation': recommendation,
            'distribution_percentiles': {
                'p5': np.percentile(revenue_samples, 5),
                'p25': np.percentile(revenue_samples, 25),
                'p50': np.percentile(revenue_samples, 50),
                'p75': np.percentile(revenue_samples, 75),
                'p95': np.percentile(revenue_samples, 95)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(
            f"✅ Simulation complete: "
            f"Expected revenue change {expected_revenue_change_pct*100:+.1f}%, "
            f"Risk: {risk_level.value}, "
            f"Recommendation: {recommendation}"
        )
        
        return result
    
    def simulate_multiple_scenarios(
        self,
        product_id: str,
        current_price: float,
        price_scenarios: List[float],
        base_elasticity: float,
        current_demand: float,
        customer_segments_distribution: Dict[str, int],
        config: Optional[SimulationConfig] = None
    ) -> pd.DataFrame:
        """
        Simulate multiple price scenarios and compare
        
        Args:
            product_id: Product ID
            current_price: Current price
            price_scenarios: List of prices to simulate
            base_elasticity: Base elasticity
            current_demand: Current demand
            customer_segments_distribution: Segment distribution
            config: Simulation config
            
        Returns:
            DataFrame comparing all scenarios
        """
        logger.info(f"🎲 Simulating {len(price_scenarios)} scenarios for {product_id}")
        
        results = []
        
        for new_price in price_scenarios:
            sim_result = self.simulate_price_change(
                product_id=product_id,
                current_price=current_price,
                new_price=new_price,
                base_elasticity=base_elasticity,
                current_demand=current_demand,
                customer_segments_distribution=customer_segments_distribution,
                config=config
            )
            
            results.append({
                'new_price': new_price,
                'price_change_pct': sim_result['price_change_pct'],
                'expected_revenue': sim_result['revenue_statistics']['mean_revenue'],
                'expected_change_pct': sim_result['revenue_statistics']['expected_change_pct'],
                'ci_lower': sim_result['confidence_intervals']['lower_bound'],
                'ci_upper': sim_result['confidence_intervals']['upper_bound'],
                'risk_level': sim_result['risk_metrics']['risk_level'],
                'prob_decrease': sim_result['risk_metrics']['prob_revenue_decrease'],
                'var_5pct': sim_result['risk_metrics']['value_at_risk_5pct'],
                'recommendation': sim_result['recommendation'],
                'blocked_customers_pct': sim_result['segment_validation']['blocked_customer_pct']
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('expected_revenue', ascending=False)
        
        logger.info(f"✅ Multi-scenario simulation complete: {len(df)} scenarios")
        
        return df
    
    def find_optimal_price(
        self,
        product_id: str,
        current_price: float,
        base_elasticity: float,
        current_demand: float,
        customer_segments_distribution: Dict[str, int],
        price_range: Tuple[float, float],
        n_scenarios: int = 20,
        config: Optional[SimulationConfig] = None
    ) -> Dict:
        """
        Find optimal price that maximizes expected revenue
        
        Args:
            product_id: Product ID
            current_price: Current price
            base_elasticity: Base elasticity
            current_demand: Current demand
            customer_segments_distribution: Segment distribution
            price_range: (min_price, max_price) to search
            n_scenarios: Number of prices to test
            config: Simulation config
            
        Returns:
            Dict with optimal price and analysis
        """
        logger.info(f"🎯 Finding optimal price for {product_id}")
        
        # Generate price scenarios
        min_price, max_price = price_range
        price_scenarios = np.linspace(min_price, max_price, n_scenarios)
        
        # Simulate all scenarios
        scenarios_df = self.simulate_multiple_scenarios(
            product_id=product_id,
            current_price=current_price,
            price_scenarios=price_scenarios.tolist(),
            base_elasticity=base_elasticity,
            current_demand=current_demand,
            customer_segments_distribution=customer_segments_distribution,
            config=config
        )
        
        # Find optimal (max expected revenue with acceptable risk)
        # Filter to LOW or MEDIUM risk only
        safe_scenarios = scenarios_df[
            scenarios_df['risk_level'].isin(['LOW', 'MEDIUM'])
        ]
        
        if len(safe_scenarios) == 0:
            # No safe scenarios, use all
            safe_scenarios = scenarios_df
            logger.warning("⚠️ No LOW/MEDIUM risk scenarios found, using all")
        
        optimal_row = safe_scenarios.iloc[0]  # Already sorted by expected_revenue
        
        result = {
            'product_id': product_id,
            'current_price': current_price,
            'optimal_price': optimal_row['new_price'],
            'price_change_pct': optimal_row['price_change_pct'],
            'expected_revenue': optimal_row['expected_revenue'],
            'expected_change_pct': optimal_row['expected_change_pct'],
            'confidence_interval': {
                'lower': optimal_row['ci_lower'],
                'upper': optimal_row['ci_upper']
            },
            'risk_level': optimal_row['risk_level'],
            'recommendation': optimal_row['recommendation'],
            'all_scenarios': scenarios_df.to_dict('records'),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(
            f"✅ Optimal price found: {optimal_row['new_price']:,.0f} VND "
            f"({optimal_row['price_change_pct']*100:+.1f}%), "
            f"Expected revenue change: {optimal_row['expected_change_pct']*100:+.1f}%"
        )
        
        return result
    
    def _validate_segments(
        self,
        price_change_pct: float,
        customer_segments_distribution: Dict[str, int]
    ) -> Dict:
        """
        Validate price change against segment rules
        
        Returns:
            Dict with validation results
        """
        total_customers = sum(customer_segments_distribution.values())
        
        allowed_segments = []
        blocked_segments = []
        allowed_customers = 0
        blocked_customers = 0
        
        for segment, count in customer_segments_distribution.items():
            is_valid, reason = SegmentPricingRules.validate_price_change(
                segment=segment,
                price_change_pct=price_change_pct
            )
            
            if is_valid:
                allowed_segments.append(segment)
                allowed_customers += count
            else:
                blocked_segments.append(segment)
                blocked_customers += count
        
        return {
            'allowed_segments': allowed_segments,
            'blocked_segments': blocked_segments,
            'allowed_customer_count': allowed_customers,
            'blocked_customer_count': blocked_customers,
            'allowed_customer_pct': allowed_customers / total_customers if total_customers > 0 else 0,
            'blocked_customer_pct': blocked_customers / total_customers if total_customers > 0 else 0
        }
    
    def _assess_risk(
        self,
        prob_decrease: float,
        prob_significant_decrease: float,
        expected_change_pct: float,
        blocked_customer_pct: float
    ) -> RiskLevel:
        """
        Assess risk level based on simulation results
        
        Args:
            prob_decrease: Probability of revenue decrease
            prob_significant_decrease: Probability of >10% decrease
            expected_change_pct: Expected revenue change %
            blocked_customer_pct: % of customers blocked by segment rules
            
        Returns:
            RiskLevel enum
        """
        # CRITICAL: High chance of significant loss or most customers blocked
        if prob_significant_decrease > 0.3 or blocked_customer_pct > 0.8:
            return RiskLevel.CRITICAL
        
        # HIGH: Likely revenue decrease or many customers blocked
        if prob_decrease > 0.6 or blocked_customer_pct > 0.5:
            return RiskLevel.HIGH
        
        # MEDIUM: Some risk but acceptable
        if prob_decrease > 0.3 or expected_change_pct < 0:
            return RiskLevel.MEDIUM
        
        # LOW: Low risk, positive expected return
        return RiskLevel.LOW
    
    def _get_recommendation(
        self,
        risk_level: RiskLevel,
        expected_change_pct: float,
        prob_decrease: float
    ) -> str:
        """
        Get recommendation based on risk and expected return
        
        Returns:
            'GO' | 'NO_GO' | 'CAUTION'
        """
        if risk_level == RiskLevel.CRITICAL:
            return 'NO_GO'
        
        if risk_level == RiskLevel.HIGH:
            if expected_change_pct > 0.05:  # >5% expected gain
                return 'CAUTION'
            else:
                return 'NO_GO'
        
        if risk_level == RiskLevel.MEDIUM:
            if expected_change_pct > 0:
                return 'CAUTION'
            else:
                return 'NO_GO'
        
        # LOW risk
        if expected_change_pct > 0:
            return 'GO'
        else:
            return 'CAUTION'


# Factory function
def create_pricing_simulator(
    pricing_engine: Optional[PersonalizedDynamicPricing] = None,
    config: Optional[SimulationConfig] = None
) -> PricingSimulator:
    """Factory function to create PricingSimulator instance"""
    return PricingSimulator(pricing_engine=pricing_engine, config=config)
