# 📚 RCM_PRICE API - COMPLETE DOCUMENTATION INDEX

## 🎯 Tài Liệu Theo Mục Đích

### 🚀 BẮT ĐẦU NHANH (Quick Start)

- **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)** - Bảng tóm tắt nhanh các endpoints
  - Use cases chính
  - Response times
  - Best practices

### 📖 TÀI LIỆU CHI TIẾT (Detailed Guide)

- **[API_ENDPOINTS_GUIDE.md](./API_ENDPOINTS_GUIDE.md)** - Hướng dẫn đầy đủ từng endpoint
  - Chức năng chi tiết
  - Parameters đầy vào
  - Response format
  - Use cases cụ thể
  - Code examples

### 🎨 SƠ ĐỒ KIẾN TRÚC (Architecture)

- **[API_ARCHITECTURE_DIAGRAM.md](./API_ARCHITECTURE_DIAGRAM.md)** - Sơ đồ trực quan
  - System architecture
  - Request flow diagrams
  - Data flow
  - Error handling flow

---

## 🔧 TÀI LIỆU KỸ THUẬT (Technical Docs)

### Bug Fixes & Troubleshooting

- **[TENSORFLOW_STUB_FIX.md](./TENSORFLOW_STUB_FIX.md)** - Fix TensorFlow optional dependencies
- **[DYNAMIC_PRICING_FIX.md](./DYNAMIC_PRICING_FIX.md)** - Fix MongoDB orderItems structure
- **[FIX_MONGODB_CONNECTION.md](./FIX_MONGODB_CONNECTION.md)** - Fix MongoDB connection issue

### Installation & Setup

- **[INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md)** - Hướng dẫn cài đặt
- **[requirements-minimal.txt](./requirements-minimal.txt)** - Dependencies tối thiểu (no TF)
- **[requirements-full.txt](./requirements-full.txt)** - Full dependencies (with TF)
- **[requirements.txt](./requirements.txt)** - Main requirements

---

## 🎓 HƯỚNG DẪN SỬ DỤNG THEO VAI TRÒ

### 👨‍💻 Frontend Developer

**Bạn cần:**

1. [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) - Xem nhanh endpoints
2. [API_ENDPOINTS_GUIDE.md](./API_ENDPOINTS_GUIDE.md) - Section 2, 3, 4, 5 (Endpoints cần gọi)

**Workflow:**

```javascript
// 1. Initialize system (lần đầu hoặc khi restart server)
POST /api/hybrid/initialize

// 2. Homepage - Recommendations
GET /api/hybrid/user-recommendations/{userId}?top_k=6

// 3. Product page - Similar products
GET /api/hybrid/product-recommendations/{productId}?top_k=4

// 4. Search bar
GET /api/huggingface/search-products?query={query}&top_k=10
```

### 👨‍💼 Business Analyst / Marketing

**Bạn cần:**

1. [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) - Use case #5, #6
2. [API_ENDPOINTS_GUIDE.md](./API_ENDPOINTS_GUIDE.md) - Section 4 (Analytics)

**Dashboard endpoints:**

```bash
GET /api/analytics/business-health      # Tổng quan
GET /api/analytics/product-performance  # SP bán chạy
GET /api/analytics/customer-insights    # Phân khúc KH
GET /api/analytics/trends               # Xu hướng
GET /api/pricing/strategy               # Chiến lược giá
```

### 🏗️ Backend Developer

**Bạn cần:**

1. [API_ARCHITECTURE_DIAGRAM.md](./API_ARCHITECTURE_DIAGRAM.md) - Hiểu architecture
2. [API_ENDPOINTS_GUIDE.md](./API_ENDPOINTS_GUIDE.md) - Full guide
3. Bug fix docs - Troubleshooting

**Key files:**

- `app/main.py` - FastAPI application
- `application/services/hybrid_recommender.py` - Core logic
- `infrastructure/ml_models/` - ML models
- `infrastructure/db/mongodb_access.py` - Data layer

### 🧪 QA / Tester

**Bạn cần:**

1. [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) - Test cases
2. [API_ENDPOINTS_GUIDE.md](./API_ENDPOINTS_GUIDE.md) - Expected responses

**Test checklist:**

- [ ] Health check returns "healthy"
- [ ] Initialize completes without errors
- [ ] User recommendations return top_k results
- [ ] Search returns relevant products
- [ ] Analytics show correct data
- [ ] Pricing optimization suggests reasonable prices

---

## 📋 DANH SÁCH ENDPOINTS ĐẦY ĐỦ

### 1. BASIC (2 endpoints)

| Endpoint  | Method | Chức năng    |
| --------- | ------ | ------------ |
| `/`       | GET    | System info  |
| `/health` | GET    | Health check |

### 2. HYBRID SYSTEM (5 endpoints)

| Endpoint                                           | Method | Chức năng               |
| -------------------------------------------------- | ------ | ----------------------- |
| `/api/hybrid/initialize`                           | POST   | Initialize system       |
| `/api/hybrid/user-recommendations/{user_id}`       | GET    | User recommendations    |
| `/api/hybrid/product-recommendations/{product_id}` | GET    | Product recommendations |
| `/api/hybrid/promotion-strategy`                   | GET    | Promotion strategy      |
| `/api/hybrid/generate-complete-strategy`           | POST   | Complete AI strategy    |

### 3. INDIVIDUAL MODELS (5 endpoints)

| Endpoint                                         | Method | Chức năng          |
| ------------------------------------------------ | ------ | ------------------ |
| `/api/tf-recommenders/recommendations/{user_id}` | GET    | TensorFlow recs    |
| `/api/huggingface/similar-products/{product_id}` | GET    | Similar products   |
| `/api/huggingface/search-products`               | GET    | Semantic search    |
| `/api/pricing/optimize/{product_id}`             | GET    | Price optimization |
| `/api/pricing/strategy`                          | GET    | Pricing strategy   |

### 4. ANALYTICS (4 endpoints)

| Endpoint                             | Method | Chức năng         |
| ------------------------------------ | ------ | ----------------- |
| `/api/analytics/business-health`     | GET    | Business overview |
| `/api/analytics/product-performance` | GET    | Product metrics   |
| `/api/analytics/customer-insights`   | GET    | Customer analysis |
| `/api/analytics/trends`              | GET    | Market trends     |

### 5. DATA ACCESS (6 endpoints)

| Endpoint                     | Method | Chức năng        |
| ---------------------------- | ------ | ---------------- |
| `/api/data/orders`           | GET    | Orders data      |
| `/api/data/products`         | GET    | Products data    |
| `/api/data/users`            | GET    | Users data       |
| `/api/data/ratings`          | GET    | Ratings data     |
| `/api/data/discounts`        | GET    | Discounts data   |
| `/api/data/search-histories` | GET    | Search histories |

### 6. LEGACY (4 endpoints)

Backward compatibility endpoints - documented in [API_ENDPOINTS_GUIDE.md](./API_ENDPOINTS_GUIDE.md)

**TỔNG CỘNG: 26+ endpoints**

---

## 🎯 USE CASES PHỔ BIẾN

### Use Case 1: Homepage Website

```
Mục đích: Hiển thị gợi ý cá nhân hóa và top sản phẩm

API calls:
1. GET /api/hybrid/user-recommendations/{userId}?top_k=6
   → Section "Gợi ý cho bạn"

2. GET /api/analytics/product-performance
   → Section "Bán chạy nhất"
```

### Use Case 2: Product Detail Page

```
Mục đích: Tăng cross-sell, up-sell

API calls:
1. GET /api/hybrid/product-recommendations/{productId}?top_k=4
   → Section "Sản phẩm tương tự"

2. GET /api/data/ratings
   → Section "Đánh giá khách hàng"
```

### Use Case 3: Search Feature

```
Mục đích: Semantic search thông minh

API call:
GET /api/huggingface/search-products?query={query}&top_k=10
   → Hiểu ngữ nghĩa: "bánh cho người ăn kiêng"
   → Tìm được "Bánh kem trái cây"
```

### Use Case 4: Admin Dashboard

```
Mục đích: Monitoring business metrics

API calls:
1. GET /api/analytics/business-health → Overview
2. GET /api/analytics/product-performance → Products
3. GET /api/analytics/customer-insights → Customers
4. GET /api/analytics/trends → Trends
5. GET /api/pricing/strategy → Pricing
```

### Use Case 5: Marketing Campaign Planning

```
Mục đích: Tạo chiến lược promotion

API calls:
1. POST /api/hybrid/generate-complete-strategy
   → Comprehensive AI analysis (30-60s)

2. GET /api/hybrid/promotion-strategy
   → Target products & customers

3. GET /api/pricing/strategy
   → Optimal pricing
```

---

## ⚡ QUICK START

### 1. Start Server

```bash
# Set PYTHONPATH
$env:PYTHONPATH="c:\Users\Lenovo\STUDY\RCM_PRICE"

# Start FastAPI
python app\main.py
```

### 2. Check Health

```bash
GET http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "services": {
    "mongodb": "connected",
    "hybrid_system": "initialized"
  }
}
```

### 3. Initialize System

```bash
POST http://localhost:8000/api/hybrid/initialize
```

Wait 10-30 seconds...

### 4. Test Recommendations

```bash
GET http://localhost:8000/api/hybrid/user-recommendations/676eaf5cbf34ce78983409c3?top_k=5
```

### 5. Access Interactive Docs

```
http://localhost:8000/docs       (Swagger UI)
http://localhost:8000/redoc      (ReDoc)
```

---

## 🔗 EXTERNAL LINKS

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **MongoDB Atlas:** Cloud database
- **Google Gemini AI:** LLM integration

---

## 📞 SUPPORT & TROUBLESHOOTING

### Common Issues

**Issue 1: MongoDB not connected**

- Check: [FIX_MONGODB_CONNECTION.md](./FIX_MONGODB_CONNECTION.md)
- Solution: Ensure .env file loaded

**Issue 2: TensorFlow errors**

- Check: [TENSORFLOW_STUB_FIX.md](./TENSORFLOW_STUB_FIX.md)
- Solution: TensorFlow is optional, stub works fine

**Issue 3: Dynamic pricing errors**

- Check: [DYNAMIC_PRICING_FIX.md](./DYNAMIC_PRICING_FIX.md)
- Solution: orderItems flattening implemented

**Issue 4: System not initialized**

- Error: "Hybrid system not initialized"
- Solution: Call `POST /api/hybrid/initialize` first

---

## 📝 VERSION HISTORY

| Version | Date       | Changes                    |
| ------- | ---------- | -------------------------- |
| 2.0.0   | 2025-10-11 | Complete API documentation |
| 1.5.0   | 2025-10-11 | Fixed Dynamic Pricing bug  |
| 1.4.0   | 2025-10-11 | Fixed TensorFlow stub      |
| 1.3.0   | 2025-10-10 | Fixed MongoDB connection   |
| 1.0.0   | 2025-09-01 | Initial release            |

---

## 🎓 RECOMMENDED READING ORDER

**Nếu bạn là người mới:**

1. README này (tổng quan)
2. [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) (hiểu nhanh)
3. [API_ARCHITECTURE_DIAGRAM.md](./API_ARCHITECTURE_DIAGRAM.md) (visualize)
4. [API_ENDPOINTS_GUIDE.md](./API_ENDPOINTS_GUIDE.md) (chi tiết)

**Nếu bạn đã biết rồi:**

- Vào thẳng [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)
- Hoặc http://localhost:8000/docs

---

**Last Updated:** 2025-10-11  
**API Version:** 2.0.0  
**Documentation Version:** 1.0.0
