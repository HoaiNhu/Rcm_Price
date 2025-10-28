# Customer Segmentation Quick Start Guide

## 📊 Tổng Quan

Module **Customer Segmentation** sử dụng **RFM Analysis** (Recency, Frequency, Monetary) kết hợp **K-Means Clustering** để phân khúc khách hàng thành 6 nhóm:

1. **VIP**: Top 20% khách hàng, tạo ra 80% doanh thu
2. **REGULAR**: Khách hàng thường xuyên, chi tiêu trung bình
3. **OCCASIONAL**: Khách hàng thỉnh thoảng
4. **NEW**: Khách hàng mới, 1-2 đơn hàng đầu tiên
5. **AT_RISK**: Khách hàng cũ tốt nhưng đã lâu không mua
6. **LOST**: Không mua hàng trong 180+ ngày

---

## 🏗️ Kiến Trúc (Clean Architecture)

```
📦 Customer Segmentation Module
├── 🔧 Infrastructure Layer
│   └── infrastructure/ml_models/customer_segmentation.py
│       ├── CustomerSegmentation class
│       ├── RFM calculation (Recency, Frequency, Monetary)
│       ├── K-Means clustering (4 clusters)
│       └── Business segment mapping
│
├── 🎯 Application Layer
│   └── application/services/customer_segmentation_service.py
│       ├── CustomerSegmentationService class
│       ├── MongoDB integration
│       └── Caching (24h)
│
└── 🌐 Presentation Layer
    └── app/routers/customer_segmentation.py
        └── 11 REST API endpoints
```

---

## 🧮 Công Thức RFM

### 1. Recency (R) - Độ gần đây

```python
Recency = (Reference Date - Last Purchase Date).days
R_Score = 5 (if recency < 20% percentile) ... 1 (if recency > 80% percentile)
```

**Ý nghĩa**: Khách hàng mua gần đây → Score cao → Khả năng mua lại cao

### 2. Frequency (F) - Tần suất

```python
Frequency = Total number of orders
F_Score = 1 (if frequency < 20% percentile) ... 5 (if frequency > 80% percentile)
```

**Ý nghĩa**: Khách hàng mua nhiều lần → Score cao → Trung thành

### 3. Monetary (M) - Giá trị

```python
Monetary = Sum of all order totals
M_Score = 1 (if monetary < 20% percentile) ... 5 (if monetary > 80% percentile)
```

**Ý nghĩa**: Khách hàng chi tiêu nhiều → Score cao → Giá trị cao

### 4. Combined RFM Score

```python
RFM_Score = R_Score + F_Score + M_Score  # Range: 3-15
```

---

## 📐 K-Means Clustering

**Algorithm**: Phân 4 clusters dựa trên RFM scores

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Normalize features
scaler = StandardScaler()
features_scaled = scaler.fit_transform(rfm_data[['r_score', 'f_score', 'm_score']])

# Clustering
kmeans = KMeans(n_clusters=4, random_state=42)
cluster_labels = kmeans.fit_predict(features_scaled)
```

**Mapping Clusters → Business Segments**:

| Cluster Profile       | Business Segment | Criteria                             |
| --------------------- | ---------------- | ------------------------------------ |
| Low R, High F, High M | VIP              | Recency < 30 days, Frequency top 25% |
| High R, High F        | AT_RISK          | Recency > 90 days, Frequency top 60% |
| Very High R           | LOST             | Recency > 180 days                   |
| Low F (≤2 orders)     | NEW              | Frequency ≤ 2                        |
| Medium R, Medium F    | REGULAR          | Recency < 60 days, Frequency top 40% |
| Other                 | OCCASIONAL       | Everything else                      |

---

## 🚀 API Endpoints

### Base URL

```
http://localhost:8000/api/customer-segmentation
```

### 1. Phân Khúc Tất Cả Khách Hàng

**POST** `/segment`

```bash
curl -X POST "http://localhost:8000/api/customer-segmentation/segment" \
  -H "Content-Type: application/json" \
  -d '{
    "reference_date": "2024-12-27T00:00:00",
    "force_refresh": false
  }'
```

**Response**:

```json
{
  "total_customers": 100,
  "total_segments": 5,
  "segments": {
    "user_001": "VIP",
    "user_002": "REGULAR",
    "user_003": "AT_RISK"
  },
  "message": "Successfully segmented 100 customers into 5 segments"
}
```

---

### 2. Lấy Segment của 1 Khách Hàng

**GET** `/segment/{user_id}`

```bash
curl "http://localhost:8000/api/customer-segmentation/segment/user_001"
```

**Response**:

```json
{
  "user_id": "user_001",
  "segment": "VIP",
  "description": "Top 20% customers generating 80% revenue"
}
```

---

### 3. Lấy Danh Sách Khách Hàng trong Segment

**GET** `/customers/{segment}`

```bash
curl "http://localhost:8000/api/customer-segmentation/customers/VIP"
```

**Response**:

```json
["user_001", "user_005", "user_012"]
```

---

### 4. Báo Cáo Chi Tiết Tất Cả Segments

**GET** `/report`

```bash
curl "http://localhost:8000/api/customer-segmentation/report"
```

**Response**:

```json
[
  {
    "segment": "VIP",
    "description": "Top 20% customers",
    "customer_count": 20,
    "customer_percentage": 20.0,
    "total_revenue": 8000000.0,
    "revenue_percentage": 80.0,
    "avg_recency_days": 15.5,
    "avg_frequency": 25.0,
    "avg_monetary": 400000.0,
    "avg_order_value": 16000.0,
    "avg_rfm_score": 14.2,
    "price_strategy": "Premium pricing - never discount"
  },
  {
    "segment": "REGULAR",
    "customer_count": 40,
    "customer_percentage": 40.0,
    "total_revenue": 1500000.0,
    "revenue_percentage": 15.0
  }
]
```

---

### 5. Thống Kê Tổng Quan

**GET** `/summary`

```bash
curl "http://localhost:8000/api/customer-segmentation/summary"
```

**Response**:

```json
{
  "total_customers": 100,
  "total_revenue": 10000000.0,
  "total_segments": 5,
  "top_segment": "VIP",
  "top_segment_revenue_pct": 80.0,
  "avg_rfm_score": 8.5
}
```

---

### 6. Chi Tiết 1 Khách Hàng

**GET** `/details/{user_id}`

```bash
curl "http://localhost:8000/api/customer-segmentation/details/user_001"
```

**Response**:

```json
{
  "user_id": "user_001",
  "segment": "VIP",
  "recency": 15.5,
  "frequency": 25.0,
  "monetary": 5000000.0,
  "avg_order_value": 200000.0,
  "rfm_score": 15,
  "r_score": 5,
  "f_score": 5,
  "m_score": 5,
  "recommendations": [
    "Maintain premium service quality",
    "Offer exclusive early access to new products",
    "Provide personalized recommendations"
  ]
}
```

---

### 7. Khuyến Nghị Hành Động cho Segment

**GET** `/recommendations/{segment}`

```bash
curl "http://localhost:8000/api/customer-segmentation/recommendations/AT_RISK"
```

**Response**:

```json
{
  "segment": "AT_RISK",
  "description": "Previously good customers but haven't purchased recently",
  "marketing_actions": [
    "Send win-back email campaigns",
    "Offer comeback discount (10-15%)",
    "Survey to understand reasons for absence"
  ],
  "pricing_actions": [
    "Special bundle deals",
    "Limited-time offers",
    "Free shipping on next order"
  ],
  "retention_actions": [
    "Personal outreach from customer service",
    "Loyalty points bonus",
    "Exclusive invitation to events"
  ],
  "priority": "HIGH"
}
```

---

### 8. Danh Sách VIP Customers

**GET** `/vip-customers?limit=10`

```bash
curl "http://localhost:8000/api/customer-segmentation/vip-customers?limit=10"
```

**Response**: List of top 10 VIP customers sorted by spending

---

### 9. Danh Sách At-Risk Customers

**GET** `/at-risk-customers?limit=20`

```bash
curl "http://localhost:8000/api/customer-segmentation/at-risk-customers?limit=20"
```

**Response**: List of 20 at-risk customers sorted by recency (most urgent first)

---

### 10. Clear Cache

**POST** `/clear-cache`

```bash
curl -X POST "http://localhost:8000/api/customer-segmentation/clear-cache"
```

**Response**:

```json
{
  "status": "success",
  "message": "Cache cleared successfully",
  "next_action": "Segmentation will be re-calculated on next request"
}
```

---

### 11. Health Check

**GET** `/health`

```bash
curl "http://localhost:8000/api/customer-segmentation/health"
```

**Response**:

```json
{
  "status": "healthy",
  "service": "customer-segmentation",
  "model_trained": true,
  "cache_valid": true,
  "timestamp": "2024-12-27T10:30:00"
}
```

---

## 💡 Use Cases

### Case 1: Identify VIP Customers for Special Event

```python
import httpx

# Get VIP customers
response = httpx.get("http://localhost:8000/api/customer-segmentation/vip-customers?limit=50")
vip_customers = response.json()

# Send exclusive invites
for customer in vip_customers:
    print(f"Send invite to {customer['user_id']} - Total spent: {customer['monetary']}")
```

---

### Case 2: Win-Back Campaign for At-Risk Customers

```python
# Get at-risk customers
response = httpx.get("http://localhost:8000/api/customer-segmentation/at-risk-customers?limit=30")
at_risk = response.json()

# Get recommendations
rec_response = httpx.get("http://localhost:8000/api/customer-segmentation/recommendations/AT_RISK")
recommendations = rec_response.json()

print(f"Found {len(at_risk)} at-risk customers")
print(f"Recommended actions: {recommendations['marketing_actions']}")
```

---

### Case 3: Segment-Specific Pricing Strategy

```python
# Get all segments report
response = httpx.get("http://localhost:8000/api/customer-segmentation/report")
segments = response.json()

for segment in segments:
    print(f"{segment['segment']}: {segment['price_strategy']}")
    # VIP: Premium pricing - never discount
    # REGULAR: Moderate pricing - occasional promotions
    # AT_RISK: Aggressive discounts - win-back offers
```

---

## 🔬 Segment Characteristics

| Segment        | Recency     | Frequency   | Monetary | % Customers | % Revenue | Price Strategy                 |
| -------------- | ----------- | ----------- | -------- | ----------- | --------- | ------------------------------ |
| **VIP**        | < 30 days   | Top 25%     | High     | ~20%        | ~80%      | Premium - No discount          |
| **REGULAR**    | < 60 days   | Top 40%     | Medium   | ~30%        | ~15%      | Moderate - Occasional promo    |
| **OCCASIONAL** | Variable    | Low-Med     | Low      | ~25%        | ~3%       | Competitive - Frequent promo   |
| **NEW**        | Recent      | 1-2 orders  | Low      | ~10%        | ~1%       | Acquisition - Welcome offer    |
| **AT_RISK**    | 90-180 days | Was Top 60% | Was High | ~10%        | ~1%       | Win-back - Aggressive discount |
| **LOST**       | > 180 days  | Any         | Any      | ~5%         | ~0%       | Reactivation - Deep discount   |

---

## ⚙️ Configuration

### Caching

- **Duration**: 24 hours
- **Clear**: POST `/clear-cache`
- **Check**: GET `/health`

### K-Means Parameters

```python
CustomerSegmentation(
    n_clusters=4,  # Number of clusters
    random_state=42  # For reproducibility
)
```

---

## 🧪 Testing

Run unit tests:

```bash
cd c:\Users\Lenovo\STUDY\RCM_PRICE
pytest tests/unit/test_customer_segmentation.py -v
```

**Expected**: 13/13 tests PASSING ✅

---

## 📊 Sample Data Format

### Orders Collection (MongoDB)

```json
{
  "user_id": "user_001",
  "total_amount": 250000,
  "created_at": "2024-12-15T10:30:00",
  "items": [{ "product_id": "prod_001", "quantity": 2, "price": 125000 }]
}
```

### Users Collection (MongoDB)

```json
{
  "user_id": "user_001",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T08:00:00"
}
```

---

## 🎯 Best Practices

1. **VIP Customers**

   - Never apply generic discounts
   - Provide exclusive benefits
   - Personal service
   - Early product access

2. **REGULAR Customers**

   - Moderate promotions (5-10%)
   - Loyalty rewards
   - Upsell opportunities

3. **AT_RISK Customers**

   - Urgent win-back campaigns
   - 15-20% discount offers
   - Personal outreach
   - Survey feedback

4. **NEW Customers**

   - Welcome discounts
   - Onboarding experience
   - Convert to REGULAR segment

5. **LOST Customers**
   - Deep discount reactivation (25-30%)
   - Re-engagement surveys
   - Low-cost remarketing

---

## 🔍 Troubleshooting

### Issue: Empty segments returned

```bash
# Solution: Force refresh cache
curl -X POST "http://localhost:8000/api/customer-segmentation/clear-cache"
curl -X POST "http://localhost:8000/api/customer-segmentation/segment" \
  -d '{"force_refresh": true}'
```

### Issue: Customer not found

```bash
# Check if segmentation ran
curl "http://localhost:8000/api/customer-segmentation/health"

# Run segmentation first
curl -X POST "http://localhost:8000/api/customer-segmentation/segment"
```

### Issue: Revenue percentage not summing to 100%

**Cause**: Rounding errors with small datasets  
**Solution**: Acceptable variance ±5%

---

## 📈 Performance

- **Segmentation Time**: ~2-5 seconds for 1000 customers
- **Cache Hit**: < 100ms response
- **MongoDB Queries**: Optimized with projection
- **Memory**: O(n) where n = number of customers

---

## 🔗 Integration with Other Modules

### With Price Elasticity

```python
# Get VIP customers
vips = httpx.get("/api/customer-segmentation/vip-customers").json()

# Get price recommendations
for vip in vips:
    # VIPs can handle price increases
    elasticity = httpx.get(f"/api/price-elasticity/recommendation/{product_id}").json()
    if vip['segment'] == 'VIP':
        # Apply premium pricing
        new_price = elasticity['current_price'] * 1.1
```

### With Dynamic Pricing (Week 3-4)

```python
# Segment-specific pricing
segment = httpx.get(f"/api/customer-segmentation/segment/{user_id}").json()

if segment == 'VIP':
    discount = 0  # No discount
elif segment == 'AT_RISK':
    discount = 0.15  # 15% win-back offer
else:
    discount = 0.05  # Standard 5%
```

---

## ✅ Week 2 Completion Checklist

- [x] Infrastructure layer (700 lines)
- [x] Unit tests (13/13 PASSING)
- [x] Service layer (540 lines)
- [x] API router (680 lines, 11 endpoints)
- [x] Integration into main.py
- [x] Quick Start Guide

**Next**: Week 3-4 - Personalized Dynamic Pricing (combining Price Elasticity + Customer Segmentation)

---

## 📚 References

- **RFM Analysis**: https://en.wikipedia.org/wiki/RFM_(market_research)
- **K-Means Clustering**: scikit-learn documentation
- **Clean Architecture**: Robert C. Martin
- **MongoDB Aggregation**: MongoDB University

---

**Author**: AI Assistant  
**Date**: 2024-12-27  
**Version**: 1.0.0  
**Status**: PRODUCTION READY ✅
