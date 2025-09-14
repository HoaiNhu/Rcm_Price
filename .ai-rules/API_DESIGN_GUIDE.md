# API DESIGN GUIDELINES

## API Endpoint Patterns

- Use RESTful conventions
- Consistent URL structure: `/api/v1/{resource}`
- Use HTTP methods correctly (GET, POST, PUT, DELETE)
- Return appropriate HTTP status codes

## Pricing API Endpoints

### 1. Price Optimization

```
POST /api/v1/pricing/optimize
Request Body:
{
    "product_id": int,
    "target_metric": "revenue" | "profit" | "market_share",
    "constraints": {
        "min_price": float,
        "max_price": float,
        "competitor_price_limit": float
    }
}

Response:
{
    "optimized_price": float,
    "expected_demand": int,
    "expected_revenue": float,
    "confidence_score": float
}
```

### 2. Demand Forecasting

```
POST /api/v1/pricing/forecast-demand
Request Body:
{
    "product_id": int,
    "price_point": float,
    "forecast_days": int,
    "external_factors": {
        "season": str,
        "events": List[str],
        "weather": str
    }
}

Response:
{
    "forecasted_demand": List[int],
    "dates": List[str],
    "confidence_intervals": List[dict]
}
```

### 3. Dynamic Pricing

```
GET /api/v1/pricing/dynamic/{product_id}
Response:
{
    "product_id": int,
    "current_price": float,
    "recommended_price": float,
    "price_change_reason": str,
    "effective_date": str,
    "expires_at": str
}
```

### 4. Bulk Price Update

```
POST /api/v1/pricing/bulk-update
Request Body:
{
    "products": [
        {
            "product_id": int,
            "new_price": float,
            "effective_date": str
        }
    ],
    "update_reason": str
}
```

## Response Format Standards

```python
# Success response
{
    "status": "success",
    "data": {...},
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid"
}

# Error response
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid product ID",
        "details": {...}
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid"
}
```

## Validation Rules

- All prices must be positive numbers
- Product IDs must exist in database
- Date formats must be ISO 8601
- Percentage discounts: 0-100%
- Required fields must be present
