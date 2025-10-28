"""
Pricing Simulator API Router
Week 5: Monte Carlo simulation endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from application.services.pricing_simulator_service import (
    get_simulator_service,
    PricingSimulatorService
)

router = APIRouter(
    prefix="/api/pricing-simulator",
    tags=["pricing-simulator"]
)


# ============================================================================
# Pydantic Models
# ============================================================================

class SimulationRequest(BaseModel):
    """Request to simulate price change"""
    product_id: str = Field(..., description="Product ID")
    new_price: float = Field(..., gt=0, description="Proposed new price (VND)")
    customer_segments_distribution: Optional[Dict[str, int]] = Field(
        None,
        description="Customer segment distribution {segment: count}"
    )
    n_iterations: int = Field(1000, ge=100, le=10000, description="Simulation iterations")
    confidence_level: float = Field(0.95, ge=0.9, le=0.99, description="Confidence level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_banh_mi",
                "new_price": 27000,
                "customer_segments_distribution": {
                    "VIP": 15,
                    "REGULAR": 45,
                    "OCCASIONAL": 25,
                    "NEW": 10,
                    "AT_RISK": 5
                },
                "n_iterations": 1000,
                "confidence_level": 0.95
            }
        }


class MultiScenarioRequest(BaseModel):
    """Request to simulate multiple price scenarios"""
    product_id: str = Field(..., description="Product ID")
    price_scenarios: List[float] = Field(..., min_length=2, description="List of prices to test")
    customer_segments_distribution: Optional[Dict[str, int]] = Field(
        None,
        description="Customer segment distribution"
    )
    n_iterations: int = Field(1000, ge=100, le=10000, description="Iterations per scenario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_pho_bo",
                "price_scenarios": [45000, 50000, 52000, 54000, 56000],
                "n_iterations": 1000
            }
        }


class OptimalPriceRequest(BaseModel):
    """Request to find optimal price"""
    product_id: str = Field(..., description="Product ID")
    price_range: Optional[Tuple[float, float]] = Field(
        None,
        description="(min_price, max_price) to search. Default: ±30% from current"
    )
    n_scenarios: int = Field(20, ge=5, le=50, description="Number of prices to test")
    n_iterations: int = Field(1000, ge=100, le=10000, description="Iterations per price")
    customer_segments_distribution: Optional[Dict[str, int]] = Field(
        None,
        description="Customer segment distribution"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_banh_mi",
                "price_range": [20000, 30000],
                "n_scenarios": 20,
                "n_iterations": 1000
            }
        }


class SimulationResponse(BaseModel):
    """Simulation result"""
    product_id: str
    current_price: float
    new_price: float
    price_change_pct: float
    base_elasticity: float
    current_demand: float
    simulation_config: Dict
    revenue_statistics: Dict
    confidence_intervals: Dict
    risk_metrics: Dict
    segment_validation: Dict
    recommendation: str
    distribution_percentiles: Dict
    timestamp: str


class ScenarioComparisonRow(BaseModel):
    """Single row in scenario comparison"""
    new_price: float
    price_change_pct: float
    expected_revenue: float
    expected_change_pct: float
    ci_lower: float
    ci_upper: float
    risk_level: str
    prob_decrease: float
    var_5pct: float
    recommendation: str
    blocked_customers_pct: float


class OptimalPriceResponse(BaseModel):
    """Optimal price finding result"""
    product_id: str
    current_price: float
    optimal_price: float
    price_change_pct: float
    expected_revenue: float
    expected_change_pct: float
    confidence_interval: Dict
    risk_level: str
    recommendation: str
    all_scenarios: List[Dict]
    timestamp: str


class SimulatorSummaryResponse(BaseModel):
    """Simulator service summary"""
    service: str
    version: str
    capabilities: List[str]
    cache_size: int
    default_iterations: int
    default_confidence_level: float
    timestamp: str


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/simulate", response_model=SimulationResponse)
async def simulate_price_change(request: SimulationRequest):
    """
    Run Monte Carlo simulation for price change
    
    Simulates revenue impact with uncertainty modeling:
    - Elasticity variance (±10%)
    - Demand variance (±15%)
    - Segment rule validation
    - Risk assessment (LOW/MEDIUM/HIGH/CRITICAL)
    - Confidence intervals (default 95%)
    
    Returns:
    - Expected revenue with confidence intervals
    - Risk metrics (probability of loss, VaR)
    - Recommendation (GO/NO_GO/CAUTION)
    - Distribution percentiles (p5, p25, p50, p75, p95)
    
    Example:
    ```
    POST /api/pricing-simulator/simulate
    {
        "product_id": "prod_banh_mi",
        "new_price": 27000,
        "n_iterations": 1000
    }
    ```
    """
    try:
        service = get_simulator_service()
        
        result = await service.simulate_price_change(
            product_id=request.product_id,
            new_price=request.new_price,
            customer_segments_distribution=request.customer_segments_distribution,
            n_iterations=request.n_iterations,
            confidence_level=request.confidence_level
        )
        
        return SimulationResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.post("/simulate-scenarios")
async def simulate_multiple_scenarios(request: MultiScenarioRequest):
    """
    Simulate multiple price scenarios and compare
    
    Runs Monte Carlo simulation for each price in the list and returns
    comparison table sorted by expected revenue.
    
    Useful for:
    - Finding best price among several options
    - Understanding revenue curve
    - Risk comparison across scenarios
    
    Returns:
    - DataFrame (as list of dicts) comparing all scenarios
    - Sorted by expected revenue (descending)
    - Includes risk metrics and recommendations
    
    Example:
    ```
    POST /api/pricing-simulator/simulate-scenarios
    {
        "product_id": "prod_pho_bo",
        "price_scenarios": [45000, 50000, 52000, 54000, 56000]
    }
    ```
    """
    try:
        service = get_simulator_service()
        
        results_df = await service.simulate_multiple_scenarios(
            product_id=request.product_id,
            price_scenarios=request.price_scenarios,
            customer_segments_distribution=request.customer_segments_distribution,
            n_iterations=request.n_iterations
        )
        
        # Convert DataFrame to list of dicts
        scenarios = results_df.to_dict('records')
        
        return {
            "product_id": request.product_id,
            "n_scenarios": len(scenarios),
            "scenarios": scenarios,
            "best_scenario": scenarios[0] if scenarios else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-scenario simulation error: {str(e)}")


@router.post("/find-optimal", response_model=OptimalPriceResponse)
async def find_optimal_price(request: OptimalPriceRequest):
    """
    Find optimal price using Monte Carlo optimization
    
    Searches price range to find price that maximizes expected revenue
    while maintaining acceptable risk (LOW or MEDIUM only).
    
    Algorithm:
    1. Generate N price scenarios in range
    2. Simulate each price
    3. Filter to LOW/MEDIUM risk only
    4. Return price with highest expected revenue
    
    Returns:
    - Optimal price and expected revenue
    - Confidence intervals
    - Risk assessment
    - All scenarios for comparison
    
    Example:
    ```
    POST /api/pricing-simulator/find-optimal
    {
        "product_id": "prod_banh_mi",
        "price_range": [20000, 30000],
        "n_scenarios": 20
    }
    ```
    """
    try:
        service = get_simulator_service()
        
        result = await service.find_optimal_price(
            product_id=request.product_id,
            price_range=request.price_range,
            n_scenarios=request.n_scenarios,
            n_iterations=request.n_iterations,
            customer_segments_distribution=request.customer_segments_distribution
        )
        
        return OptimalPriceResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimal price finding error: {str(e)}")


@router.get("/summary", response_model=SimulatorSummaryResponse)
async def get_simulator_summary():
    """
    Get pricing simulator service summary
    
    Returns:
    - Service capabilities
    - Cache statistics
    - Default configuration
    
    Example:
    ```
    GET /api/pricing-simulator/summary
    ```
    """
    try:
        service = get_simulator_service()
        summary = await service.get_simulation_summary()
        
        return SimulatorSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")


@router.post("/clear-cache")
async def clear_cache():
    """
    Clear simulation cache
    
    Forces re-computation on next simulation request.
    
    Example:
    ```
    POST /api/pricing-simulator/clear-cache
    ```
    """
    try:
        service = get_simulator_service()
        result = await service.clear_cache()
        
        return {
            "status": "success",
            "message": f"Cleared {result['cleared_items']} cached simulations",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Example:
    ```
    GET /api/pricing-simulator/health
    ```
    """
    return {
        "status": "healthy",
        "service": "pricing-simulator",
        "timestamp": datetime.now().isoformat()
    }
