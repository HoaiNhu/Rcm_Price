# 📋 POSTMAN TESTING COMPLETE GUIDE - RCM PRICE API

## 🎯 Tổng quan

Hướng dẫn đầy đủ để test tất cả API endpoints trong AI Promotion System bằng Postman Collection.

## 📦 Import Postman Collection

### Bước 1: Mở Postman

1. Khởi động Postman Desktop hoặc Postman Web
2. Click vào `Import` ở góc trên bên trái

### Bước 2: Import Collection

1. Chọn tab `File`
2. Click `Choose Files`
3. Chọn file: `RCM_PRICE_Complete_API_Tests.postman_collection.json`
4. Click `Import`

### Bước 3: Kiểm tra Collection

- Collection sẽ xuất hiện trong sidebar với tên **"RCM PRICE - Complete API Tests"**
- Có 13 folders chứa 100+ endpoints

---

## 🔧 Cấu hình Environment Variables

### Tạo Environment mới:

1. Click vào icon ⚙️ (Settings) ở góc trên phải
2. Click `Environments` → `Create Environment`
3. Đặt tên: `RCM PRICE - Local`

### Thêm Variables:

| Variable Name | Initial Value              | Current Value           |
| ------------- | -------------------------- | ----------------------- |
| `base_url`    | `http://localhost:8000`    | `http://localhost:8000` |
| `product_id`  | `674cfc8e2b4c648fe8c2c7dd` | _(sẽ update sau)_       |
| `user_id`     | `674cfcb62b4c648fe8c2c7e3` | _(sẽ update sau)_       |

4. Click `Save`
5. Chọn environment này từ dropdown ở góc trên phải

---

## 🚀 Hướng dẫn Test theo từng Module

### 📍 Module 1: Basic & Health (Bắt đầu ở đây)

#### 1.1 Test Root Endpoint

```
GET http://localhost:8000/
```

**Expected Response:**

```json
{
  "message": "AI Promotion System API v2.0",
  "version": "2.0.0",
  "status": "running",
  "features": [...],
  "timestamp": "2024-12-27T10:00:00"
}
```

#### 1.2 Test Health Check

```
GET http://localhost:8000/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "services": {
    "mongodb": "connected",
    "promotion_service": "initialized",
    "hybrid_system": "initialized",
    "gemini": "configured"
  }
}
```

---

### 📍 Module 2: Data Access

#### 2.1 Get Products (Lấy product_id thực tế)

```
GET http://localhost:8000/api/data/products?limit=5
```

**Hành động:**

1. Copy một `_id` từ response
2. Update environment variable `product_id`

#### 2.2 Get Users (Lấy user_id thực tế)

```
GET http://localhost:8000/api/data/users?limit=5
```

**Hành động:**

1. Copy một `_id` từ response
2. Update environment variable `user_id`

#### 2.3 Test các endpoints khác:

- ✅ Get Orders
- ✅ Get Ratings
- ✅ Get Discounts
- ✅ Get Search Histories

---

### 📍 Module 3: Analytics

#### 3.1 Business Health Analysis

```
GET http://localhost:8000/api/analytics/business-health
```

**Metrics:**

- Total revenue
- Total orders
- Average order value
- Customer retention rate

#### 3.2 Product Performance

```
GET http://localhost:8000/api/analytics/product-performance?top_n=10
```

**Metrics:**

- Top selling products
- Revenue contribution
- Order frequency

#### 3.3 Customer Insights

```
GET http://localhost:8000/api/analytics/customer-insights
```

#### 3.4 Trends Analysis

```
GET http://localhost:8000/api/analytics/trends
```

---

### 📍 Module 4: Customer Segmentation

#### 4.1 Segment All Customers (QUAN TRỌNG - Chạy đầu tiên)

```
POST http://localhost:8000/api/customer-segmentation/segment
Body:
{
  "min_orders_for_analysis": 1,
  "vip_threshold": 500000,
  "regular_threshold": 100000,
  "at_risk_days": 60,
  "lost_days": 90
}
```

**Expected Response:**

```json
{
  "total_customers": 50,
  "segments": {
    "VIP": 10,
    "REGULAR": 20,
    "OCCASIONAL": 10,
    "NEW": 5,
    "AT_RISK": 3,
    "LOST": 2
  }
}
```

#### 4.2 Get Customer Segment

```
GET http://localhost:8000/api/customer-segmentation/segment/{{user_id}}
```

#### 4.3 Get Customers by Segment

```
GET http://localhost:8000/api/customer-segmentation/customers/VIP
```

Thử với các segments: `VIP`, `REGULAR`, `OCCASIONAL`, `NEW`, `AT_RISK`, `LOST`

#### 4.4 Segmentation Report

```
GET http://localhost:8000/api/customer-segmentation/report
```

#### 4.5 Get VIP Customers

```
GET http://localhost:8000/api/customer-segmentation/vip-customers?min_ltv=500000
```

#### 4.6 Get At-Risk Customers

```
GET http://localhost:8000/api/customer-segmentation/at-risk-customers?days_threshold=60
```

---

### 📍 Module 5: Price Elasticity

#### 5.1 Analyze Price Elasticity (Chạy đầu tiên)

```
POST http://localhost:8000/api/price-elasticity/analyze
Body:
{
  "product_ids": [],
  "min_orders": 5,
  "price_range_pct": 0.3
}
```

#### 5.2 Get Product Elasticity

```
GET http://localhost:8000/api/price-elasticity/product/{{product_id}}
```

#### 5.3 Get Segment Elasticity

```
GET http://localhost:8000/api/price-elasticity/segment/VIP
```

#### 5.4 Predict Demand

```
POST http://localhost:8000/api/price-elasticity/predict
Body:
{
  "product_id": "{{product_id}}",
  "new_price": 30000,
  "segment": "REGULAR"
}
```

---

### 📍 Module 6: Personalized Pricing

#### 6.1 Get Personalized Price

```
GET http://localhost:8000/api/personalized-pricing/price/{{product_id}}/{{user_id}}
```

#### 6.2 Get Personalized Catalog

```
GET http://localhost:8000/api/personalized-pricing/catalog/{{user_id}}?limit=10
```

#### 6.3 Get Pricing Matrix

```
GET http://localhost:8000/api/personalized-pricing/matrix/{{product_id}}
```

#### 6.4 Validate Price

```
POST http://localhost:8000/api/personalized-pricing/validate
Body:
{
  "user_id": "{{user_id}}",
  "product_id": "{{product_id}}",
  "proposed_price": 28000
}
```

#### 6.5 Simulate Pricing Impact

```
POST http://localhost:8000/api/personalized-pricing/simulate
Body:
{
  "product_id": "{{product_id}}",
  "price_changes": {
    "VIP": 1.05,
    "REGULAR": 1.0,
    "OCCASIONAL": 0.95,
    "NEW": 0.9
  },
  "expected_customer_counts": {
    "VIP": 20,
    "REGULAR": 50,
    "OCCASIONAL": 30,
    "NEW": 15
  }
}
```

---

### 📍 Module 7: Pricing Simulator (Monte Carlo)

#### 7.1 Simulate Single Price

```
POST http://localhost:8000/api/pricing-simulator/simulate
Body:
{
  "product_id": "{{product_id}}",
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
```

#### 7.2 Simulate Multiple Scenarios

```
POST http://localhost:8000/api/pricing-simulator/simulate-scenarios
Body:
{
  "product_id": "{{product_id}}",
  "price_scenarios": [24000, 25000, 26000, 27000, 28000, 29000, 30000],
  "n_iterations": 1000
}
```

#### 7.3 Find Optimal Price

```
POST http://localhost:8000/api/pricing-simulator/find-optimal
Body:
{
  "product_id": "{{product_id}}",
  "price_range": [20000, 32000],
  "n_scenarios": 25,
  "n_iterations": 1000
}
```

---

### 📍 Module 8: Smart Promotions

#### 8.1 Generate Segment Promotion

```
POST http://localhost:8000/api/smart-promotions/generate-segment-promotion
Body:
{
  "segment": "NEW",
  "goal": "ACQUISITION",
  "validity_days": 30
}
```

Thử với các segments và goals khác nhau:

- Segments: `VIP`, `REGULAR`, `OCCASIONAL`, `NEW`, `AT_RISK`, `LOST`
- Goals: `ACQUISITION`, `RETENTION`, `WINBACK`, `REVENUE_MAX`

#### 8.2 Generate Price Increase Voucher

```
POST http://localhost:8000/api/smart-promotions/generate-price-increase-voucher
Body:
{
  "product_id": "{{product_id}}",
  "new_price": 28000,
  "segment": "REGULAR",
  "validity_days": 30
}
```

#### 8.3 Generate Winback Campaign

```
POST http://localhost:8000/api/smart-promotions/generate-winback-campaign?validity_days=60
```

#### 8.4 Generate Bundle Promotion

```
POST http://localhost:8000/api/smart-promotions/generate-bundle-promotion
Body:
{
  "product_bundles": [
    ["product_id_1", "product_id_2"],
    ["product_id_3", "product_id_4"]
  ],
  "bundle_discount_pct": 0.15,
  "validity_days": 30
}
```

_(Cần thay thế product_id thực tế)_

#### 8.5 Get All Promotions

```
GET http://localhost:8000/api/smart-promotions/all-promotions
```

---

### 📍 Module 9: Event Promotions

#### 9.1 Analyze Products for Event

```
GET http://localhost:8000/api/event-promotions/analyze-products?top_n=10
```

#### 9.2 Discover Product Combos

```
GET http://localhost:8000/api/event-promotions/discover-combos?min_support=0.01&min_confidence=0.3&top_n=10
```

#### 9.3 Get Upcoming Events

```
GET http://localhost:8000/api/event-promotions/upcoming-events?days_ahead=30
```

#### 9.4 Generate Event Promotion

```
POST http://localhost:8000/api/event-promotions/generate-event-promotion
Body:
{
  "event_name": "Tết 2025",
  "event_date": "2025-01-29",
  "target_segments": ["VIP", "REGULAR"],
  "budget": 10000000,
  "top_n_products": 5,
  "min_support": 0.01,
  "min_confidence": 0.3
}
```

#### 9.5 Generate Smart Promotion

```
POST http://localhost:8000/api/event-promotions/generate-smart-promotion
Body:
{
  "event_name": "Flash Sale Weekend",
  "event_date": "2025-02-15",
  "target_segments": ["REGULAR", "OCCASIONAL"],
  "budget": 5000000,
  "strategy": "AGGRESSIVE",
  "promotion_type": "DISCOUNT",
  "top_n_products": 8
}
```

---

### 📍 Module 10: Hybrid Recommender

#### 10.1 Initialize Hybrid System (Chạy đầu tiên)

```
POST http://localhost:8000/api/hybrid/initialize
```

#### 10.2 Get User Recommendations

```
GET http://localhost:8000/api/hybrid/user-recommendations/{{user_id}}?top_k=5
```

#### 10.3 Get Product Recommendations

```
GET http://localhost:8000/api/hybrid/product-recommendations/{{product_id}}?top_k=5
```

#### 10.4 Get Promotion Strategy

```
GET http://localhost:8000/api/hybrid/promotion-strategy?top_products=5
```

#### 10.5 Generate Complete Strategy

```
POST http://localhost:8000/api/hybrid/generate-complete-strategy
Body:
{
  "include_gemini_insights": true,
  "top_products": 5,
  "promotion_budget": 5000000
}
```

---

### 📍 Module 11: ML Models

#### 11.1 TensorFlow Recommender

```
GET http://localhost:8000/api/tf-recommenders/recommendations/{{user_id}}?top_k=5
```

#### 11.2 HuggingFace - Similar Products

```
GET http://localhost:8000/api/huggingface/similar-products/{{product_id}}?top_k=5
```

#### 11.3 HuggingFace - Search Products

```
GET http://localhost:8000/api/huggingface/search-products?query=bánh mì&top_k=5
```

#### 11.4 Dynamic Pricing - Optimize

```
GET http://localhost:8000/api/pricing/optimize/{{product_id}}?target_revenue_increase=0.1
```

#### 11.5 Dynamic Pricing - Strategy

```
GET http://localhost:8000/api/pricing/strategy
```

---

## 📊 Test Flow Recommendations

### 🎯 Flow 1: Complete System Test (15-20 phút)

```
1. Basic & Health
   ├── Root
   └── Health Check

2. Data Access
   ├── Get Products (lưu product_id)
   ├── Get Users (lưu user_id)
   └── Get Orders

3. Customer Segmentation
   ├── Segment All Customers
   ├── Get Customer Segment
   └── Segmentation Report

4. Price Elasticity
   ├── Analyze Price Elasticity
   └── Get Product Elasticity

5. Personalized Pricing
   ├── Get Personalized Price
   └── Get Personalized Catalog

6. Smart Promotions
   ├── Generate Segment Promotion
   └── Get All Promotions

7. Analytics
   ├── Business Health
   └── Enhanced Strategy
```

### 🎯 Flow 2: Advanced Pricing Test (10-15 phút)

```
1. Price Elasticity Module
   └── Analyze All → Get by Product → Get by Segment

2. Personalized Pricing Module
   └── Get Price → Validate → Simulate

3. Pricing Simulator Module
   └── Single Simulation → Multiple Scenarios → Find Optimal

4. Compare Results
```

### 🎯 Flow 3: Promotion Campaign Test (10 phút)

```
1. Customer Segmentation
   └── Segment All → Get VIP → Get At-Risk

2. Smart Promotions
   ├── Generate Segment Promotion (VIP)
   ├── Generate Segment Promotion (NEW)
   ├── Generate Winback Campaign
   └── Get All Promotions

3. Event Promotions
   ├── Analyze Products
   ├── Discover Combos
   └── Generate Event Promotion
```

---

## 🔍 Test Scripts (Tự động hóa)

### Thêm vào Collection Tests:

```javascript
// Test 1: Status Code Check
pm.test("Status code is 200", function () {
  pm.response.to.have.status(200);
});

// Test 2: Response Time
pm.test("Response time is less than 5000ms", function () {
  pm.expect(pm.response.responseTime).to.be.below(5000);
});

// Test 3: Content Type
pm.test("Content-Type is JSON", function () {
  pm.response.to.have.header("Content-Type", /application\/json/);
});

// Test 4: Save Variables (cho GET Products)
if (pm.response.code === 200) {
  var jsonData = pm.response.json();
  if (jsonData.products && jsonData.products.length > 0) {
    pm.environment.set("product_id", jsonData.products[0]._id);
  }
}

// Test 5: Validate Response Structure
pm.test("Response has required fields", function () {
  var jsonData = pm.response.json();
  pm.expect(jsonData).to.have.property("status");
});
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Connection Refused

```
Error: connect ECONNREFUSED 127.0.0.1:8000
```

**Solution:**

- Kiểm tra server đang chạy: `python app/main.py`
- Kiểm tra port 8000 không bị chiếm

### Issue 2: 404 Not Found

```
Status: 404 Not Found
```

**Solution:**

- Kiểm tra lại endpoint URL
- Đảm bảo base_url = `http://localhost:8000`

### Issue 3: 500 Internal Server Error

```
Status: 500 Internal Server Error
```

**Solution:**

- Kiểm tra MongoDB connection
- Kiểm tra logs server
- Đảm bảo data đã được load

### Issue 4: Invalid product_id/user_id

```
Error: Product not found
```

**Solution:**

- Lấy ID thực tế từ `/api/data/products` và `/api/data/users`
- Update environment variables

---

## 📈 Expected Performance

| Endpoint Type               | Expected Response Time |
| --------------------------- | ---------------------- |
| Health Check                | < 100ms                |
| Data Access                 | < 500ms                |
| Analytics                   | < 2000ms               |
| Segmentation                | < 3000ms               |
| Price Elasticity            | < 2000ms               |
| Personalized Pricing        | < 1000ms               |
| Simulator (1000 iterations) | < 5000ms               |
| Smart Promotions            | < 2000ms               |
| Event Promotions            | < 3000ms               |
| ML Models                   | < 2000ms               |

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GitHub Repo**: [Link to your repo]
- **Postman Documentation**: https://learning.postman.com/

---

## ✅ Checklist trước khi Test

- [ ] Server đang chạy (`python app/main.py`)
- [ ] MongoDB connection thành công
- [ ] Import Postman Collection
- [ ] Tạo Environment với `base_url`
- [ ] Lấy `product_id` và `user_id` thực tế
- [ ] Test Health Check trước

---

## 🎓 Tips & Best Practices

1. **Luôn test Health Check trước**
2. **Lưu response variables** để dùng cho requests sau
3. **Test theo thứ tự** từ đơn giản đến phức tạp
4. **Kiểm tra logs** nếu có lỗi
5. **Sử dụng Collection Runner** để test hàng loạt
6. **Export results** để documentation
7. **Tạo nhiều environments** (Local, Dev, Prod)

---

## 📝 Notes

- Collection này cover 100% endpoints trong project
- Tất cả requests đều có example data
- Response models đã được validate
- Có thể chạy automated tests với Newman CLI

---

**Happy Testing! 🚀**
