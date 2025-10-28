# Price Elasticity Calculator - Quick Start Guide

## 📋 Tổng Quan

**Price Elasticity Calculator** là module tính toán độ nhạy cảm giá của sản phẩm, giúp đưa ra khuyến nghị về thay đổi giá an toàn mà không làm mất khách hàng trung thành.

### 🎯 Tính Năng Chính

✅ **Tính toán Price Elasticity** - Phân tích độ nhạy cảm giá của sản phẩm  
✅ **Phân loại Sensitivity** - 4 mức độ (VERY_SENSITIVE → INSENSITIVE)  
✅ **Khuyến nghị giá** - Đề xuất mức tăng giá an toàn  
✅ **Simulation** - Dự đoán tác động trước khi thay đổi giá  
✅ **Quality Metrics** - R², MSE, sample size validation

---

## 🏗️ Kiến Trúc Clean Architecture

```
RCM_PRICE/
├── infrastructure/ml_models/
│   └── price_elasticity.py         # ⚙️ Core calculation logic
├── application/services/
│   └── price_elasticity_service.py # 🔗 Business logic & orchestration
├── app/routers/
│   └── price_elasticity.py         # 🌐 REST API endpoints
└── tests/unit/
    └── test_price_elasticity.py    # 🧪 Unit tests
```

### Layers:

1. **Infrastructure Layer** (`price_elasticity.py`)

   - Core ML logic (LinearRegression)
   - Elasticity calculation
   - Data processing

2. **Application Layer** (`price_elasticity_service.py`)

   - MongoDB integration
   - Business rules
   - Orchestration

3. **Presentation Layer** (`routers/price_elasticity.py`)
   - REST API endpoints
   - Request validation
   - Response formatting

---

## 🚀 Quick Start

### 1. Cài Đặt Dependencies

```bash
# Đã có trong requirements.txt
pip install pandas numpy scikit-learn
```

### 2. Test Module

```bash
# Run unit tests
cd c:\Users\Lenovo\STUDY\RCM_PRICE
pytest tests/unit/test_price_elasticity.py -v
```

### 3. Start API Server

```bash
# Start FastAPI server
python app/main.py

# hoặc
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test API Endpoints

#### **A. Calculate Elasticity (Training)**

```bash
curl -X POST "http://localhost:8000/api/price-elasticity/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "days": 90,
    "min_samples": 10,
    "force_recalculate": false
  }'
```

**Response:**

```json
{
  "success": true,
  "elasticity_data": {
    "product_123": -0.8,
    "product_456": -1.6
  },
  "summary": {
    "total_products": 50,
    "mean_elasticity": -1.2,
    "sensitivity_distribution": {
      "VERY_SENSITIVE": 10,
      "SENSITIVE": 15,
      "MODERATE": 20,
      "INSENSITIVE": 5
    }
  }
}
```

#### **B. Get Recommendation for Product**

```bash
curl "http://localhost:8000/api/price-elasticity/recommendation/{product_id}"
```

**Response:**

```json
{
  "success": true,
  "product_id": "product_123",
  "product_name": "Bánh Su Kem",
  "current_price": 20000,
  "elasticity": -0.8,
  "sensitivity": "MODERATE",
  "max_safe_increase_pct": 10.0,
  "max_safe_price": 22000,
  "recommendation": "✅ ĐỘ NHẠY TRUNG BÌNH (E=-0.80)\n• Có thể tăng giá nhẹ\n• Tăng giá tối đa: 10%\n• Nên test A/B trước khi áp dụng rộng rãi"
}
```

#### **C. Get All Recommendations**

```bash
curl "http://localhost:8000/api/price-elasticity/recommendations"
```

#### **D. Simulate Price Change**

```bash
curl -X POST "http://localhost:8000/api/price-elasticity/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "product_123",
    "new_price": 22000
  }'
```

**Response:**

```json
{
  "success": true,
  "product_id": "product_123",
  "current_price": 20000,
  "new_price": 22000,
  "price_change_pct": 10.0,
  "estimated_quantity_change_pct": -8.0,
  "revenue_change": 150000,
  "revenue_change_pct": 5.2,
  "is_safe_change": true
}
```

#### **E. Get Detailed Report**

```bash
curl "http://localhost:8000/api/price-elasticity/report"
```

#### **F. Health Check**

```bash
curl "http://localhost:8000/api/price-elasticity/health"
```

---

## 📊 Hiểu Về Price Elasticity

### Formula:

```
Price Elasticity (E) = % Change in Quantity / % Change in Price
```

### Phân Loại:

| Elasticity Value    | Sensitivity    | Meaning                 | Max Safe Increase |
| ------------------- | -------------- | ----------------------- | ----------------- |
| **E < -1.5**        | VERY_SENSITIVE | Khách hàng rất nhạy giá | ≤ 2%              |
| **-1.5 ≤ E < -1.0** | SENSITIVE      | Khách hàng khá nhạy giá | ≤ 5%              |
| **-1.0 ≤ E < -0.5** | MODERATE       | Độ nhạy trung bình      | ≤ 10%             |
| **E ≥ -0.5**        | INSENSITIVE    | Premium, ít nhạy giá    | ≤ 15%             |

### Example:

**Bánh Su Kem: E = -0.8 (MODERATE)**

- Tăng giá 10% → Giảm demand ~8%
- Current: 100 cái/tháng × 20,000đ = 2,000,000đ
- New: 92 cái/tháng × 22,000đ = 2,024,000đ
- **Revenue tăng 1.2%** ✅

---

## 🧪 Metrics & Quality

### Model Metrics:

- **R² (R-squared)**: Độ chính xác của model (0-1)

  - R² > 0.7: Excellent
  - R² > 0.5: Good
  - R² > 0.3: Acceptable
  - R² < 0.3: Need more data

- **MSE (Mean Squared Error)**: Sai số trung bình

  - Lower is better

- **Sample Size**: Số lượng data points
  - Recommended: ≥ 10 samples

### Quality Validation:

```python
{
  "is_valid": true,
  "total_products": 50,
  "high_quality_products": 42,
  "quality_rate": 84.0,
  "recommendation": "✅ Good quality - 42/50 products have R² >= 0.3"
}
```

---

## 💡 Best Practices

### 1. Data Requirements

✅ **Minimum**: 30 days of order history  
✅ **Recommended**: 90 days for accuracy  
✅ **Ideal**: 180+ days for seasonal patterns

### 2. Recalculation Schedule

- **Daily**: For high-volume products
- **Weekly**: For normal products
- **Force recalculate**: After major price changes or events

### 3. Decision Making

**Before changing price:**

1. ✅ Calculate elasticity
2. ✅ Check sensitivity category
3. ✅ Run simulation
4. ✅ Verify is_safe_change = true
5. ✅ Test with small segment first
6. ✅ Monitor results for 2-4 weeks

**Warning Signs:**

⚠️ VERY_SENSITIVE products → Don't increase price  
⚠️ R² < 0.3 → Need more data  
⚠️ Sample size < 10 → Unreliable

---

## 🔧 Advanced Usage

### Python SDK:

```python
from infrastructure.ml_models.price_elasticity import create_price_elasticity_calculator
from infrastructure.db.mongodb_access import get_mongodb_access
import pandas as pd

# Initialize
calculator = create_price_elasticity_calculator()

# Load data
orders_df = pd.DataFrame(...)  # Your orders
products_df = pd.DataFrame(...)  # Your products

# Calculate
elasticity_results = calculator.calculate_elasticity(
    orders_df,
    products_df,
    min_samples=10
)

# Get recommendation
recommendation = calculator.recommend_price_change(
    product_id='product_123',
    current_price=20000
)

print(recommendation['recommendation'])
```

### Service Layer:

```python
from application.services.price_elasticity_service import create_price_elasticity_service

# Initialize
db_access = await get_mongodb_access()
service = create_price_elasticity_service(db_access)

# Calculate all
result = await service.calculate_all_elasticities(days=90)

# Simulate
simulation = await service.simulate_price_change(
    product_id='product_123',
    new_price=22000
)
```

---

## 📈 Integration with Dynamic Pricing

Price Elasticity Calculator là **foundation** cho Personalized Dynamic Pricing:

```
Price Elasticity → Customer Segmentation (RFM) → Personalized Pricing
```

**Next Steps:**

1. ✅ Week 1: Price Elasticity (DONE)
2. 🔜 Week 2: Customer Segmentation (RFM)
3. 🔜 Week 3: Personalized Dynamic Pricing
4. 🔜 Week 4: Simulation & Promotion Generator

---

## 🐛 Troubleshooting

### Issue: "No elasticity data available"

**Solution:**

- Check if orders exist in MongoDB
- Verify min_samples parameter (default: 10)
- Try reducing min_samples to 5

### Issue: "Low R² values"

**Solution:**

- Increase data period (90 → 180 days)
- Check for data quality (missing prices, quantities)
- Filter out outliers

### Issue: "Insufficient samples"

**Solution:**

- Reduce min_samples parameter
- Combine related products
- Wait for more sales data

---

## 📚 API Documentation

**Swagger UI**: http://localhost:8000/docs  
**ReDoc**: http://localhost:8000/redoc

**Base URL**: `/api/price-elasticity`

**Endpoints:**

- `POST /calculate` - Calculate elasticity
- `GET /recommendation/{product_id}` - Get recommendation
- `GET /recommendations` - Get all recommendations
- `GET /report` - Get detailed report
- `POST /simulate` - Simulate price change
- `GET /health` - Health check

---

## ✅ Testing Checklist

- [ ] Unit tests pass (`pytest`)
- [ ] API server starts successfully
- [ ] Calculate elasticity returns results
- [ ] Recommendations make sense
- [ ] Simulation predicts revenue correctly
- [ ] R² values > 0.3 for most products
- [ ] Integration with MongoDB works

---

## 📞 Support

**Documentation:**

- `EXECUTIVE_SUMMARY_PERSONALIZED_PRICING.md`
- `CUSTOMER_LOYALTY_PRICING_STRATEGY.md`
- `IMPLEMENTATION_PLAN_PERSONALIZED_PRICING.md`

**Contact:** RCM_PRICE Team  
**Date:** 2025-10-27  
**Version:** 1.0.0
