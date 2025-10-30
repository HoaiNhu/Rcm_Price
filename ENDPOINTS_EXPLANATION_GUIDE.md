# 📚 GIẢI THÍCH CHI TIẾT CÁC ENDPOINTS - RCM PRICE API

## 🎯 Mục đích của Guide này

Giải thích **công dụng, khi nào dùng, và cách dùng** từng endpoint trong hệ thống AI Promotion.

---

## 📋 MỤC LỤC

1. [Basic & Health - Kiểm tra hệ thống](#1-basic--health)
2. [Data Access - Truy xuất dữ liệu](#2-data-access)
3. [Analytics - Phân tích kinh doanh](#3-analytics)
4. [Customer Segmentation - Phân khúc khách hàng](#4-customer-segmentation)
5. [Price Elasticity - Độ co giãn giá](#5-price-elasticity)
6. [Personalized Pricing - Định giá cá nhân hóa](#6-personalized-pricing)
7. [Pricing Simulator - Mô phỏng giá](#7-pricing-simulator)
8. [Smart Promotions - Khuyến mãi thông minh](#8-smart-promotions)
9. [Event Promotions - Khuyến mãi sự kiện](#9-event-promotions)
10. [Hybrid Recommender - Gợi ý sản phẩm](#10-hybrid-recommender)
11. [ML Models - Mô hình AI/ML](#11-ml-models)
12. [Legacy Endpoints - API cũ](#12-legacy-endpoints)
13. [Test Endpoints - Debug](#13-test-endpoints)

---

## 1. BASIC & HEALTH

### 1.1 Root - System Info

```
GET /
```

**Công dụng:**

- Hiển thị thông tin tổng quan về hệ thống
- Liệt kê các tính năng có sẵn
- Kiểm tra server có đang chạy không

**Khi nào dùng:**

- ✅ Lần đầu kết nối đến API
- ✅ Kiểm tra version API
- ✅ Xem danh sách features có sẵn

**Ví dụ thực tế:**

```javascript
// Response
{
  "message": "AI Promotion System API v2.0",
  "version": "2.0.0",
  "status": "running",
  "features": [
    "MongoDB Integration",
    "TensorFlow Recommenders",
    "Dynamic Pricing Models"
  ]
}
```

### 1.2 Health Check

```
GET /health
```

**Công dụng:**

- Kiểm tra tình trạng sức khỏe của toàn bộ hệ thống
- Xác nhận kết nối MongoDB
- Kiểm tra các services đã khởi động chưa

**Khi nào dùng:**

- ✅ Trước khi bắt đầu test các API khác
- ✅ Khi gặp lỗi không rõ nguyên nhân
- ✅ Monitoring tự động (mỗi 5 phút)
- ✅ Sau khi restart server

**Ví dụ thực tế:**

```javascript
// Scenario: Trước khi chạy chiến dịch marketing
// 1. Check health
// 2. Nếu "status": "healthy" → Tiếp tục
// 3. Nếu không → Fix lỗi trước
```

---

## 2. DATA ACCESS

### 2.1 Get Orders

```
GET /api/data/orders?limit=10
```

**Công dụng:**

- Lấy danh sách đơn hàng từ MongoDB
- Xem lịch sử mua hàng của khách
- Phân tích xu hướng mua sắm

**Khi nào dùng:**

- ✅ Cần xem orders gần nhất
- ✅ Phân tích doanh thu theo thời gian
- ✅ Tìm top khách hàng mua nhiều
- ✅ Debug data issues

**Parameters:**

- `limit`: Số lượng orders trả về (default: 100)
- `skip`: Bỏ qua n records đầu (pagination)

**Ví dụ thực tế:**

```javascript
// Scenario: Phân tích doanh thu tuần này
GET /api/data/orders?limit=1000

// Lọc orders có totalAmount > 500,000 VND
// Tính tổng revenue
// Xác định top products
```

### 2.2 Get Products

```
GET /api/data/products?limit=10
```

**Công dụng:**

- Lấy danh sách sản phẩm
- Xem thông tin giá, tên, mô tả
- Lấy product_id để dùng cho các API khác

**Khi nào dùng:**

- ✅ **QUAN TRỌNG**: Lấy product_id thực để test
- ✅ Xem catalog sản phẩm hiện có
- ✅ Kiểm tra giá hiện tại
- ✅ Setup data cho testing

**Ví dụ thực tế:**

```javascript
// Scenario: Chuẩn bị test pricing APIs
// 1. GET /api/data/products?limit=5
// 2. Copy một product_id từ response
// 3. Lưu vào Environment variable
// 4. Dùng {{product_id}} trong các requests sau
```

### 2.3 Get Users

```
GET /api/data/users?limit=10
```

**Công dụng:**

- Lấy danh sách khách hàng
- Xem thông tin user
- Lấy user_id cho personalized pricing

**Khi nào dùng:**

- ✅ **QUAN TRỌNG**: Lấy user_id thực để test
- ✅ Xem customer base
- ✅ Phân tích demographics
- ✅ Setup data cho segmentation

**Ví dụ thực tế:**

```javascript
// Scenario: Test personalized pricing
// 1. GET /api/data/users?limit=5
// 2. Copy một user_id
// 3. Lưu vào Environment
// 4. Test GET /api/personalized-pricing/catalog/{{user_id}}
```

### 2.4 Get Ratings

```
GET /api/data/ratings?limit=10
```

**Công dụng:**

- Lấy đánh giá của khách hàng
- Phân tích sentiment
- Tìm sản phẩm được yêu thích

**Khi nào dùng:**

- ✅ Cần feedback về sản phẩm
- ✅ Tìm sản phẩm rating cao để promote
- ✅ Phân tích chất lượng dịch vụ

### 2.5 Get Discounts

```
GET /api/data/discounts?limit=10
```

**Công dụng:**

- Xem các chương trình giảm giá đang chạy
- Kiểm tra discount history
- Phân tích hiệu quả campaigns

**Khi nào dùng:**

- ✅ Kiểm tra discount đã tạo
- ✅ Tránh duplicate campaigns
- ✅ Analyze ROI của promotions

### 2.6 Get Search Histories

```
GET /api/data/search-histories?limit=10
```

**Công dụng:**

- Xem lịch sử tìm kiếm của khách
- Phân tích search intent
- Tìm trending keywords

**Khi nào dùng:**

- ✅ Hiểu khách muốn tìm gì
- ✅ Optimize product catalog
- ✅ Plan marketing content

---

## 3. ANALYTICS

### 3.1 Business Health

```
GET /api/analytics/business-health
```

**Công dụng:**

- **DASHBOARD CHÍNH** của business
- Xem tổng quan: Revenue, Orders, AOV
- Customer retention rate
- Growth metrics

**Khi nào dùng:**

- ✅ **Daily**: Báo cáo hàng ngày cho management
- ✅ Meeting với stakeholders
- ✅ Đánh giá performance tổng thể
- ✅ So sánh với targets

**Metrics quan trọng:**

```javascript
{
  "total_revenue": 50000000,      // Tổng doanh thu
  "total_orders": 234,             // Số đơn hàng
  "average_order_value": 213675,   // Giá trị TB mỗi đơn
  "unique_customers": 156,         // Số khách unique
  "retention_rate": 0.45,          // 45% khách quay lại
  "revenue_growth": 0.15           // Tăng 15% so với kỳ trước
}
```

**Ví dụ thực tế:**

```javascript
// Scenario: Họp chiến lược hàng tuần
// 1. Chạy Business Health
// 2. Nếu revenue_growth < 0 → Cần action
// 3. Nếu retention_rate < 0.3 → Focus retention
// 4. Nếu AOV giảm → Upsell/Cross-sell
```

### 3.2 Product Performance

```
GET /api/analytics/product-performance?top_n=10
```

**Công dụng:**

- Xem top sản phẩm bán chạy
- Sản phẩm đóng góp revenue nhiều nhất
- Identify underperformers

**Khi nào dùng:**

- ✅ Quyết định sản phẩm nào nên promote
- ✅ Inventory planning
- ✅ Xóa sản phẩm ế
- ✅ Bundle hot products

**Ví dụ thực tế:**

```javascript
// Scenario: Plan Flash Sale
// 1. Get top 10 best sellers
// 2. Chọn 3-5 products có margin cao
// 3. Tạo bundle promotion
// 4. Set discount 15-20%
```

### 3.3 Customer Insights

```
GET /api/analytics/customer-insights
```

**Công dụng:**

- Phân tích hành vi khách hàng
- Lifetime value distribution
- Purchase frequency patterns

**Khi nào dùng:**

- ✅ Hiểu customer behavior
- ✅ Plan retention campaigns
- ✅ Identify VIP candidates

### 3.4 Trends Analysis

```
GET /api/analytics/trends
```

**Công dụng:**

- Phát hiện xu hướng mua sắm
- Seasonal patterns
- Product category trends

**Khi nào dùng:**

- ✅ Planning seasonal campaigns
- ✅ Inventory forecasting
- ✅ Product development

### 3.5 Enhanced Strategy

```
GET /api/analytics/enhanced-strategy
```

**Công dụng:**

- **AI-powered insights**
- Comprehensive business analysis
- Actionable recommendations

**Khi nào dùng:**

- ✅ Quarterly business review
- ✅ Strategic planning
- ✅ Need AI suggestions

---

## 4. CUSTOMER SEGMENTATION

### 4.1 Segment All Customers ⭐⭐⭐

```
POST /api/customer-segmentation/segment
```

**Công dụng:**

- **QUAN TRỌNG NHẤT** trong module này
- Phân loại TẤT CẢ khách hàng thành segments
- Dùng RFM analysis (Recency, Frequency, Monetary)
- Tự động gắn nhãn: VIP, REGULAR, OCCASIONAL, NEW, AT_RISK, LOST

**Khi nào dùng:**

- ✅ **BẮT BUỘC chạy trước** khi dùng các API khác
- ✅ Mỗi ngày/tuần để update segments
- ✅ Sau khi có orders mới
- ✅ Trước khi tạo campaigns

**Request Body:**

```json
{
  "min_orders_for_analysis": 1, // Tối thiểu bao nhiêu đơn mới phân tích
  "vip_threshold": 500000, // Chi >= 500k VND → VIP
  "regular_threshold": 100000, // Chi >= 100k → REGULAR
  "at_risk_days": 60, // Không mua >60 ngày → AT_RISK
  "lost_days": 90 // Không mua >90 ngày → LOST
}
```

**Response:**

```json
{
  "total_customers": 150,
  "segments": {
    "VIP": 15, // 10% - Chi nhiều, mua thường xuyên
    "REGULAR": 45, // 30% - Khách quen
    "OCCASIONAL": 30, // 20% - Mua thỉnh thoảng
    "NEW": 20, // 13% - Khách mới
    "AT_RISK": 25, // 17% - Sắp rời bỏ
    "LOST": 15 // 10% - Đã mất
  },
  "timestamp": "2024-12-27T10:00:00"
}
```

**Ví dụ thực tế:**

```javascript
// Scenario: Chiến dịch Marketing tháng 1
// 1. Segment all customers
// 2. VIP (15 người) → Tặng voucher 100k
// 3. REGULAR (45 người) → Discount 15%
// 4. NEW (20 người) → Welcome offer 20%
// 5. AT_RISK (25 người) → Winback campaign
// 6. LOST (15 người) → Special comeback offer
```

### 4.2 Get Customer Segment

```
GET /api/customer-segmentation/segment/{user_id}
```

**Công dụng:**

- Xem segment của 1 khách cụ thể
- Chi tiết metrics: RFM scores, LTV, churn risk

**Khi nào dùng:**

- ✅ Check segment trước khi offer
- ✅ Customer service cần info
- ✅ Personalized communication

**Response:**

```json
{
  "user_id": "674cfcb62b4c648fe8c2c7e3",
  "segment": "VIP",
  "rfm_scores": {
    "recency": 5, // Mua rất gần đây (1-5)
    "frequency": 5, // Mua rất thường xuyên
    "monetary": 5 // Chi tiêu rất nhiều
  },
  "lifetime_value": 1250000,
  "total_orders": 15,
  "avg_order_value": 83333,
  "days_since_last_order": 3,
  "churn_risk": "LOW"
}
```

### 4.3 Get Customers by Segment

```
GET /api/customer-segmentation/customers/VIP
```

**Công dụng:**

- Lấy list tất cả khách trong 1 segment
- Export để gửi email marketing
- Target specific group

**Khi nào dùng:**

- ✅ Tạo campaign cho segment cụ thể
- ✅ Export email list
- ✅ Analyze segment characteristics

**Segments có thể query:**

- `VIP` - Khách VIP
- `REGULAR` - Khách quen
- `OCCASIONAL` - Thỉnh thoảng
- `NEW` - Khách mới
- `AT_RISK` - Sắp mất
- `LOST` - Đã mất

### 4.4 Segmentation Report

```
GET /api/customer-segmentation/report
```

**Công dụng:**

- Báo cáo chi tiết từng segment
- Revenue contribution
- Growth/decline trends

**Khi nào dùng:**

- ✅ Weekly marketing review
- ✅ Identify opportunities
- ✅ Track segment health

### 4.5 Get VIP Customers

```
GET /api/customer-segmentation/vip-customers?min_ltv=500000
```

**Công dụng:**

- Lấy list khách VIP (chi nhiều nhất)
- Filter theo lifetime value

**Khi nào dùng:**

- ✅ **VIP program**: Tặng quà, ưu đãi đặc biệt
- ✅ Exclusive events
- ✅ Premium service
- ✅ Personal account manager

**Ví dụ thực tế:**

```javascript
// Scenario: VIP Year-End Party
// 1. Get VIP customers (LTV >= 1M VND)
// 2. Send personal invitations
// 3. Tặng voucher 200k
// 4. Giới thiệu sản phẩm mới
```

### 4.6 Get At-Risk Customers

```
GET /api/customer-segmentation/at-risk-customers?days_threshold=60
```

**Công dụng:**

- Tìm khách sắp rời bỏ (không mua >60 ngày)
- Churn prevention
- Retention campaigns

**Khi nào dùng:**

- ✅ **Retention campaigns** (quan trọng!)
- ✅ Win-back offers
- ✅ Survey để hiểu lý do
- ✅ Re-engagement emails

**Ví dụ thực tế:**

```javascript
// Scenario: Winback Campaign
// 1. Get at-risk customers (>60 days)
// 2. Segment thành:
//    - High value → Personal call + 30% discount
//    - Medium value → Email + 20% discount
//    - Low value → SMS + 15% discount
// 3. Track response rate
// 4. Follow up after 1 week
```

---

## 5. PRICE ELASTICITY

### 5.1 Analyze Price Elasticity ⭐⭐⭐

```
POST /api/price-elasticity/analyze
```

**Công dụng:**

- **QUAN TRỌNG**: Phân tích độ co giãn giá
- Hiểu khách sẽ phản ứng như thế nào khi tăng/giảm giá
- Tính elasticity coefficient cho từng sản phẩm

**Khi nào dùng:**

- ✅ **Trước khi thay đổi giá**
- ✅ Planning pricing strategy
- ✅ Maximize revenue
- ✅ Avoid pricing mistakes

**Request:**

```json
{
  "product_ids": [], // Empty = analyze all products
  "min_orders": 5, // Cần ít nhất 5 orders để accurate
  "price_range_pct": 0.3 // Test giá ±30%
}
```

**Response:**

```json
{
  "elasticity": {
    "prod_banh_mi": -0.8, // Elastic: Tăng giá 1% → Giảm demand 0.8%
    "prod_pho_bo": -1.5, // Very elastic: Nhạy cảm với giá
    "prod_cafe": -0.3 // Inelastic: Không nhạy cảm
  },
  "recommendations": {
    "prod_banh_mi": {
      "current_price": 25000,
      "optimal_price": 27000,
      "price_change_pct": 0.08,
      "expected_revenue_change": 0.024 // +2.4% revenue
    }
  }
}
```

**Hiểu Price Elasticity:**

- **|E| < 1**: Inelastic (không nhạy cảm) → **CÓ THỂ TĂNG GIÁ**
- **|E| = 1**: Unit elastic → Giữ nguyên
- **|E| > 1**: Elastic (nhạy cảm) → **KHÔNG NÊN TĂNG GIÁ**

**Ví dụ thực tế:**

```javascript
// Scenario: Muốn tăng giá Bánh Mì
// 1. Analyze elasticity
// 2. Result: E = -0.5 (inelastic)
// 3. → Khách không nhạy cảm với giá
// 4. Tăng giá 8%: 25k → 27k
// 5. Expected: Revenue +2.4%
```

### 5.2 Get Product Elasticity

```
GET /api/price-elasticity/product/{product_id}
```

**Công dụng:**

- Xem elasticity của 1 sản phẩm cụ thể
- Chi tiết sensitivity analysis

**Khi nào dùng:**

- ✅ Pricing decision cho 1 product
- ✅ Compare với competitors

### 5.3 Get Segment Elasticity

```
GET /api/price-elasticity/segment/VIP
```

**Công dụng:**

- Xem độ nhạy cảm giá theo từng segment
- VIP vs REGULAR vs NEW

**Khi nào dùng:**

- ✅ **Personalized pricing strategy**
- ✅ Segment-based discounts

**Insights:**

```javascript
// VIP: E = -0.3 (ít nhạy cảm) → Có thể giá cao hơn
// REGULAR: E = -0.8 → Giá standard
// NEW: E = -1.5 (rất nhạy cảm) → Cần giá thấp để attract
```

### 5.4 Predict Demand

```
POST /api/price-elasticity/predict
```

**Công dụng:**

- Dự đoán demand nếu thay đổi giá
- Forecast revenue impact

**Khi nào dùng:**

- ✅ "What-if" analysis
- ✅ Before price changes
- ✅ Revenue forecasting

**Request:**

```json
{
  "product_id": "prod_banh_mi",
  "new_price": 27000,
  "segment": "REGULAR"
}
```

**Response:**

```json
{
  "current_demand": 100, // orders/month hiện tại
  "predicted_demand": 92, // orders/month nếu tăng giá
  "demand_change_pct": -0.08,
  "current_revenue": 2500000,
  "predicted_revenue": 2484000,
  "revenue_change_pct": -0.006
}
```

---

## 6. PERSONALIZED PRICING

### 6.1 Get Personalized Price ⭐⭐⭐

```
GET /api/personalized-pricing/price/{product_id}/{user_id}
```

**Công dụng:**

- **DYNAMIC PRICING**: Giá khác nhau cho từng khách
- Dựa trên segment, purchase history, price sensitivity
- Maximize revenue và conversion

**Khi nào dùng:**

- ✅ **E-commerce website**: Hiển thị giá cho user
- ✅ Mobile app
- ✅ Chatbot commerce
- ✅ Email marketing với giá cá nhân

**Response:**

```json
{
  "product_id": "prod_banh_mi",
  "user_id": "user_123",
  "segment": "VIP",
  "current_price": 25000,
  "recommended_price": 27000, // Giá đề xuất cho user này
  "price_change_pct": 0.08, // +8%
  "strategy": "premium", // VIP → giá cao hơn
  "action": "INCREASE",
  "justification_required": true, // Cần giải thích tại sao
  "revenue_impact": {
    "revenue_change_pct": 0.05 // +5% revenue
  }
}
```

**Strategies:**

- **VIP**: Premium pricing (+5% đến +10%)
- **REGULAR**: Standard pricing (0%)
- **NEW**: Acquisition pricing (-10% đến -20%)
- **AT_RISK**: Retention pricing (-15% đến -25%)

**Ví dụ thực tế:**

```javascript
// Scenario: User login vào website
// 1. Detect user_id from session
// 2. GET personalized price for products
// 3. Display:
//    - VIP user: Bánh Mì 27,000 VND (giá cao)
//    - NEW user: Bánh Mì 22,000 VND (welcome discount)
//    - AT_RISK: Bánh Mì 20,000 VND (winback offer)
```

### 6.2 Get Personalized Catalog ⭐⭐

```
GET /api/personalized-pricing/catalog/{user_id}?limit=10
```

**Công dụng:**

- Lấy **toàn bộ catalog** với giá cá nhân hóa
- Mỗi sản phẩm có giá riêng cho user này

**Khi nào dùng:**

- ✅ **Homepage personalization**
- ✅ Product listing page
- ✅ Shopping cart
- ✅ Email campaigns

**Response:**

```json
{
  "user_id": "user_123",
  "segment": "REGULAR",
  "catalog": [
    {
      "product_id": "prod_banh_mi",
      "product_name": "Bánh Mì Thịt",
      "base_price": 25000,
      "personalized_price": 25000, // REGULAR → giữ nguyên
      "discount_pct": 0,
      "strategy": "standard"
    },
    {
      "product_id": "prod_pho_bo",
      "product_name": "Phở Bò",
      "base_price": 50000,
      "personalized_price": 50000,
      "discount_pct": 0,
      "strategy": "standard"
    }
  ]
}
```

### 6.3 Validate Price

```
POST /api/personalized-pricing/validate
```

**Công dụng:**

- Kiểm tra giá có hợp lệ không
- Đảm bảo trong min/max bounds
- Compliance check

**Khi nào dùng:**

- ✅ Before applying price
- ✅ Manual price override
- ✅ Regulatory compliance

### 6.4 Simulate Pricing Impact

```
POST /api/personalized-pricing/simulate
```

**Công dụng:**

- "What-if" analysis cho pricing strategy
- Forecast revenue với different pricing tiers

**Khi nào dùng:**

- ✅ **Strategic planning**
- ✅ A/B testing planning
- ✅ Board presentations

**Request:**

```json
{
  "product_id": "prod_banh_mi",
  "price_changes": {
    "VIP": 1.1, // +10% cho VIP
    "REGULAR": 1.0, // Giữ nguyên
    "NEW": 0.85 // -15% cho NEW
  },
  "expected_customer_counts": {
    "VIP": 20,
    "REGULAR": 50,
    "NEW": 30
  }
}
```

---

## 7. PRICING SIMULATOR (Monte Carlo)

### 7.1 Simulate Single Price ⭐⭐⭐

```
POST /api/pricing-simulator/simulate
```

**Công dụng:**

- **Monte Carlo simulation**: Chạy 1000+ iterations
- Predict revenue distribution với price mới
- Tính confidence intervals
- Risk assessment

**Khi nào dùng:**

- ✅ **Trước khi launch giá mới**
- ✅ Cần chắc chắn về revenue impact
- ✅ Present to management với confidence level
- ✅ High-stake pricing decisions

**Request:**

```json
{
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
```

**Response:**

```json
{
  "product_id": "prod_banh_mi",
  "current_price": 25000,
  "new_price": 27000,
  "simulation_results": {
    "mean_revenue": 2700000,
    "median_revenue": 2695000,
    "min_revenue": 2400000, // Worst case
    "max_revenue": 3100000, // Best case
    "confidence_interval_95": {
      "lower": 2550000, // 95% chắc >= 2.55M
      "upper": 2850000 // 95% chắc <= 2.85M
    },
    "probability_of_increase": 0.78, // 78% khả năng revenue tăng
    "risk_level": "LOW"
  },
  "recommendation": "APPROVE - Low risk, high probability of success"
}
```

**Ví dụ thực tế:**

```javascript
// Scenario: CEO hỏi "Nếu tăng giá 8%, revenue sẽ như thế nào?"
// 1. Run simulation 1000 iterations
// 2. Result:
//    - Mean revenue: +8.5%
//    - 95% confident: +5% to +12%
//    - Probability success: 78%
//    - Risk: LOW
// 3. Decision: APPROVE
```

### 7.2 Simulate Multiple Scenarios

```
POST /api/pricing-simulator/simulate-scenarios
```

**Công dụng:**

- Test nhiều mức giá cùng lúc
- So sánh scenarios
- Find sweet spot

**Khi nào dùng:**

- ✅ **A/B/C/D testing planning**
- ✅ Explore pricing range
- ✅ Find optimal zone

**Request:**

```json
{
  "product_id": "prod_banh_mi",
  "price_scenarios": [24000, 25000, 26000, 27000, 28000, 29000, 30000],
  "n_iterations": 1000
}
```

**Response:**

```json
{
  "scenarios": [
    {
      "price": 24000,
      "expected_revenue": 2400000,
      "risk": "LOW"
    },
    {
      "price": 27000,
      "expected_revenue": 2700000, // HIGHEST
      "risk": "LOW"
    },
    {
      "price": 30000,
      "expected_revenue": 2550000, // Too high → demand drop
      "risk": "HIGH"
    }
  ],
  "best_scenario": {
    "price": 27000,
    "reason": "Maximum revenue with low risk"
  }
}
```

### 7.3 Find Optimal Price ⭐⭐⭐

```
POST /api/pricing-simulator/find-optimal
```

**Công dụng:**

- **TỰ ĐỘNG tìm giá tối ưu**
- Test 20-50 price points
- Maximize revenue objective

**Khi nào dùng:**

- ✅ **Không biết nên set giá bao nhiêu**
- ✅ New product launch
- ✅ Market repositioning
- ✅ Quarterly pricing review

**Request:**

```json
{
  "product_id": "prod_banh_mi",
  "price_range": [20000, 32000], // Search từ 20k đến 32k
  "n_scenarios": 25, // Test 25 price points
  "n_iterations": 1000
}
```

**Response:**

```json
{
  "optimal_price": 27500,
  "expected_revenue": 2750000,
  "current_price": 25000,
  "current_revenue": 2500000,
  "improvement": {
    "revenue_increase": 250000, // +250k VND
    "revenue_increase_pct": 0.1, // +10%
    "price_increase_pct": 0.1 // Tăng giá 10%
  },
  "confidence": {
    "level": 0.95,
    "lower_bound": 2650000,
    "upper_bound": 2850000
  },
  "recommendation": "Set price to 27,500 VND for maximum revenue"
}
```

**Ví dụ thực tế:**

```javascript
// Scenario: Launch sản phẩm mới "Bánh Mì Đặc Biệt"
// Question: Nên định giá bao nhiêu?
//
// 1. Estimate range: 30k - 50k
// 2. POST /find-optimal với range [30000, 50000]
// 3. Algorithm test 25 price points
// 4. Result: Optimal = 42,000 VND
// 5. Expected revenue: 8.4M/month
// 6. Launch với giá 42k!
```

---

## 8. SMART PROMOTIONS

### 8.1 Generate Segment Promotion ⭐⭐⭐

```
POST /api/smart-promotions/generate-segment-promotion
```

**Công dụng:**

- **AI-powered promotion** cho từng segment
- Tự động tính discount % phù hợp
- Generate voucher codes
- Set validity period

**Khi nào dùng:**

- ✅ **Tạo campaign nhanh**
- ✅ Segment-targeted marketing
- ✅ Automated promotions
- ✅ Loyalty programs

**Request:**

```json
{
  "segment": "NEW",
  "goal": "ACQUISITION",
  "validity_days": 30
}
```

**Goals:**

- `ACQUISITION`: Thu hút khách mới
- `RETENTION`: Giữ chân khách cũ
- `WINBACK`: Gọi lại khách mất
- `REVENUE_MAX`: Maximize revenue

**Response:**

```json
{
  "promotion_id": "PROMO_NEW_ACQ_001",
  "segment": "NEW",
  "goal": "ACQUISITION",
  "type": "percentage_discount",
  "value": 0.2, // 20% discount
  "description": "Welcome Offer - 20% off for new customers",
  "voucher_code": "WELCOME20",
  "valid_from": "2024-12-27",
  "valid_until": "2025-01-26",
  "max_uses": 100,
  "discounted_catalog": {
    "prod_banh_mi": {
      "original_price": 25000,
      "discounted_price": 20000
    }
  }
}
```

**Strategies tự động:**

- **VIP**: No discount, bonus points, free shipping
- **REGULAR**: 5-10% discount
- **NEW**: 15-20% welcome discount
- **AT_RISK**: 20-25% retention discount
- **LOST**: 25-30% winback discount

**Ví dụ thực tế:**

```javascript
// Scenario: Chiến dịch thu hút khách mới
// 1. POST generate-segment-promotion
//    - segment: "NEW"
//    - goal: "ACQUISITION"
// 2. System tạo:
//    - Discount: 20%
//    - Code: WELCOME20
//    - Valid: 30 ngày
// 3. Share code qua:
//    - Facebook Ads
//    - Email signup
//    - SMS
```

### 8.2 Generate Price Increase Voucher

```
POST /api/smart-promotions/generate-price-increase-voucher
```

**Công dụng:**

- Khi TĂNG GIÁ, tạo voucher để giảm impact
- Customer satisfaction during price hike
- Smooth transition

**Khi nào dùng:**

- ✅ **Bắt buộc khi tăng giá**
- ✅ Inflation adjustment
- ✅ Cost increase

**Request:**

```json
{
  "product_id": "prod_banh_mi",
  "new_price": 28000, // Tăng từ 25k lên 28k
  "segment": "REGULAR",
  "validity_days": 30
}
```

**Response:**

```json
{
  "voucher_code": "PRICE28K_REG",
  "product_id": "prod_banh_mi",
  "old_price": 25000,
  "new_price": 28000,
  "price_increase": 3000, // +3k
  "price_increase_pct": 0.12, // +12%
  "voucher_value": 1800, // Voucher 60% of increase
  "final_price": 26200, // 28k - 1.8k
  "description": "Offset voucher for price increase",
  "strategy": "Offset 60% of price increase to maintain customer satisfaction"
}
```

**Logic:**

```javascript
// Khi tăng giá 12% (3000 VND)
// → Voucher = 60% x 3000 = 1800 VND
// → Final price = 26,200 (chỉ tăng 4.8% thay vì 12%)
// → Khách dễ chấp nhận hơn
```

### 8.3 Generate Winback Campaign ⭐⭐

```
POST /api/smart-promotions/generate-winback-campaign?validity_days=60
```

**Công dụng:**

- **Tự động tạo campaign** cho AT_RISK + LOST customers
- Mỗi customer 1 voucher code riêng
- Aggressive discount 25-30%

**Khi nào dùng:**

- ✅ **Hàng tháng/quý** để recover lost customers
- ✅ High churn rate
- ✅ Seasonal re-activation

**Response:**

```json
{
  "campaign_id": "WINBACK_DEC2024",
  "type": "winback",
  "target_segment": "AT_RISK,LOST",
  "n_customers": 40,
  "discount_pct": 0.25,
  "customer_vouchers": {
    "user_001": "COMEBACK_USER001",
    "user_002": "COMEBACK_USER002"
    // ... 40 unique codes
  },
  "discounted_catalog": {
    "prod_banh_mi": {
      "original_price": 25000,
      "discounted_price": 18750 // -25%
    }
  },
  "valid_from": "2024-12-27",
  "valid_until": "2025-02-26", // 60 days
  "description": "We miss you! 25% off on everything"
}
```

**Ví dụ thực tế:**

```javascript
// Scenario: 40 khách sắp mất/đã mất
// 1. Generate winback campaign
// 2. System tạo 40 unique voucher codes
// 3. Send personalized emails:
//    "Hi John, we miss you! Use code COMEBACK_JOHN
//     for 25% off. Valid 60 days."
// 4. Track:
//    - Open rate: 60%
//    - Redemption rate: 15%
//    - Recovered customers: 6
//    - ROI: 3.5x
```

### 8.4 Generate Bundle Promotion

```
POST /api/smart-promotions/generate-bundle-promotion
```

**Công dụng:**

- Combo/bundle promotions
- "Buy together, save more"
- Cross-sell strategy

**Khi nào dùng:**

- ✅ Increase basket size
- ✅ Move slow inventory
- ✅ Seasonal bundles

**Request:**

```json
{
  "product_bundles": [
    ["prod_banh_mi", "prod_cafe_sua"],
    ["prod_pho_bo", "prod_bun_cha"]
  ],
  "bundle_discount_pct": 0.15,
  "validity_days": 30
}
```

**Response:**

```json
{
  "promotion_id": "BUNDLE_COMBO_001",
  "bundles": [
    {
      "products": ["Bánh Mì", "Cà Phê Sữa"],
      "regular_total": 40000,
      "bundle_price": 34000, // Save 6k
      "savings": 6000,
      "savings_pct": 0.15
    }
  ],
  "voucher_code": "COMBO15",
  "total_savings": 12000
}
```

---

## 9. EVENT PROMOTIONS

### 9.1 Analyze Products for Event

```
GET /api/event-promotions/analyze-products?top_n=10
```

**Công dụng:**

- Phân tích sản phẩm phù hợp cho events
- Revenue potential
- Popularity scores

**Khi nào dùng:**

- ✅ **Event planning** (Tết, Valentine, etc.)
- ✅ Chọn sản phẩm để promote
- ✅ Seasonal campaigns

### 9.2 Discover Product Combos ⭐⭐

```
GET /api/event-promotions/discover-combos
```

**Công dụng:**

- **Market Basket Analysis**
- Tìm sản phẩm thường mua cùng nhau
- Association rules mining

**Khi nào dùng:**

- ✅ **Bundle planning**
- ✅ Cross-sell recommendations
- ✅ Store layout optimization

**Response:**

```json
{
  "combos": [
    {
      "product_1": "Bánh Mì",
      "product_2": "Cà Phê Sữa",
      "support": 0.15, // 15% orders có cả 2
      "confidence": 0.75, // 75% người mua Bánh Mì cũng mua Cà Phê
      "lift": 2.5, // Mua cùng nhiều gấp 2.5x random
      "recommendation": "STRONG - Excellent bundle opportunity"
    }
  ]
}
```

### 9.3 Get Upcoming Events

```
GET /api/event-promotions/upcoming-events?days_ahead=30
```

**Công dụng:**

- Lịch events/holidays sắp tới
- Planning timeline
- Preparation checklist

**Khi nào dùng:**

- ✅ **Marketing calendar**
- ✅ Campaign planning
- ✅ Inventory preparation

### 9.4 Generate Event Promotion ⭐⭐⭐

```
POST /api/event-promotions/generate-event-promotion
```

**Công dụng:**

- **Complete event campaign** tự động
- Product selection
- Combo suggestions
- Budget allocation
- Segment targeting

**Khi nào dùng:**

- ✅ **Major events**: Tết, Christmas, Valentine
- ✅ Flash sales
- ✅ Grand opening
- ✅ Anniversary sales

**Request:**

```json
{
  "event_name": "Tết Nguyên Đán 2025",
  "event_date": "2025-01-29",
  "target_segments": ["VIP", "REGULAR"],
  "budget": 10000000, // 10M VND budget
  "top_n_products": 5,
  "min_support": 0.01,
  "min_confidence": 0.3
}
```

**Response:**

```json
{
  "event_name": "Tết Nguyên Đán 2025",
  "event_date": "2025-01-29",
  "days_until_event": 33,
  "promotions": [
    {
      "type": "product_discount",
      "segment": "VIP",
      "products": ["Bánh Chưng", "Mứt Tết"],
      "discount_pct": 0.15,
      "budget_allocated": 3000000,
      "expected_orders": 60,
      "expected_revenue": 9000000
    },
    {
      "type": "bundle_offer",
      "segment": "REGULAR",
      "bundle": ["Bánh Chưng", "Giò Lụa", "Mứt"],
      "bundle_discount": 0.2,
      "bundle_price": 250000,
      "regular_price": 312500,
      "savings": 62500
    }
  ],
  "total_budget": 10000000,
  "expected_revenue": 25000000,
  "roi": 2.5,
  "recommendation": "Strong event opportunity with 2.5x ROI"
}
```

**Ví dụ thực tế:**

```javascript
// Scenario: Tết Nguyên Đán
// 1. Generate event promotion 30 ngày trước Tết
// 2. System suggest:
//    - Top products: Bánh Chưng, Mứt, Giò
//    - VIP: 15% off
//    - REGULAR: Bundle 20% off
//    - Budget: 10M
//    - Expected revenue: 25M
//    - ROI: 2.5x
// 3. Approve & launch campaign
// 4. Track performance
```

---

## 10. HYBRID RECOMMENDER

### 10.1 Initialize Hybrid System

```
POST /api/hybrid/initialize
```

**Công dụng:**

- Khởi tạo recommendation system
- Load models
- Train with latest data

**Khi nào dùng:**

- ✅ First time setup
- ✅ After major data update
- ✅ Model refresh

### 10.2 Get User Recommendations ⭐⭐⭐

```
GET /api/hybrid/user-recommendations/{user_id}?top_k=5
```

**Công dụng:**

- **"Customers who bought X also bought Y"**
- Personalized product recommendations
- Collaborative + content-based filtering

**Khi nào dùng:**

- ✅ **Homepage**: "Recommended for you"
- ✅ Product detail page: "You may also like"
- ✅ Email: "Based on your history"
- ✅ Mobile app recommendations

**Response:**

```json
{
  "user_id": "user_123",
  "recommendations": [
    {
      "product_id": "prod_pho_bo",
      "product_name": "Phở Bò",
      "score": 0.89, // 89% confidence
      "price": 50000,
      "reason": "Based on your purchase history",
      "recommendation_type": "collaborative_filtering"
    },
    {
      "product_id": "prod_bun_cha",
      "product_name": "Bún Chả",
      "score": 0.76,
      "price": 45000,
      "reason": "Similar to products you liked",
      "recommendation_type": "content_based"
    }
  ]
}
```

### 10.3 Get Product Recommendations

```
GET /api/hybrid/product-recommendations/{product_id}?top_k=5
```

**Công dụng:**

- "Similar products"
- "Customers also viewed"
- Content-based recommendations

**Khi nào dùng:**

- ✅ Product detail page
- ✅ Out of stock alternatives
- ✅ Upsell/cross-sell

---

## 11. ML MODELS

### 11.1 TensorFlow Recommender

```
GET /api/tf-recommenders/recommendations/{user_id}
```

**Công dụng:**

- Deep learning recommendations
- Neural collaborative filtering

### 11.2 HuggingFace - Similar Products

```
GET /api/huggingface/similar-products/{product_id}
```

**Công dụng:**

- NLP-based similarity
- Semantic search
- Content matching

### 11.3 HuggingFace - Search Products

```
GET /api/huggingface/search-products?query=bánh mì
```

**Công dụng:**

- Intelligent search
- Intent understanding
- Fuzzy matching

---

## 📊 WORKFLOW EXAMPLES

### Workflow 1: Launch New Product

```
1. GET /api/analytics/product-performance
   → Xem competitors' performance

2. POST /api/price-elasticity/analyze
   → Estimate price sensitivity

3. POST /api/pricing-simulator/find-optimal
   → Find optimal launch price

4. POST /api/smart-promotions/generate-segment-promotion
   → Create launch promotion for NEW segment

5. Launch product!
```

### Workflow 2: Monthly Marketing Campaign

```
1. POST /api/customer-segmentation/segment
   → Segment all customers

2. GET /api/customer-segmentation/at-risk-customers
   → Find at-risk customers

3. POST /api/smart-promotions/generate-winback-campaign
   → Create winback offers

4. GET /api/event-promotions/discover-combos
   → Find bundle opportunities

5. POST /api/event-promotions/generate-event-promotion
   → Plan event campaign
```

### Workflow 3: Optimize Pricing

```
1. POST /api/price-elasticity/analyze
   → Analyze all products

2. GET /api/price-elasticity/product/{product_id}
   → Deep dive on specific product

3. POST /api/pricing-simulator/simulate-scenarios
   → Test multiple price points

4. POST /api/pricing-simulator/find-optimal
   → Find best price

5. Implement new pricing!
```

---

## 🎯 QUICK REFERENCE

### Must-Use Daily

- `GET /health` - System check
- `GET /api/analytics/business-health` - Daily dashboard
- `POST /api/customer-segmentation/segment` - Update segments

### Must-Use Weekly

- `GET /api/analytics/product-performance` - Review top products
- `GET /api/customer-segmentation/at-risk-customers` - Retention
- `POST /api/smart-promotions/generate-winback-campaign` - Win back

### Must-Use Monthly

- `POST /api/price-elasticity/analyze` - Pricing review
- `POST /api/pricing-simulator/find-optimal` - Optimize prices
- `POST /api/event-promotions/generate-event-promotion` - Plan campaigns

---

**🎓 Pro Tips:**

1. **Luôn chạy Health Check trước**
2. **Segment customers trước khi tạo promotions**
3. **Test với simulator trước khi thay đổi giá thật**
4. **Dùng personalized pricing cho maximize revenue**
5. **Monitor analytics daily**

**Happy optimizing! 🚀**
