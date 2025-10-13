# 🚀 API ENDPOINTS - QUICK REFERENCE

## 📋 TÓM TẮT NHANH

| Endpoint                                           | Method | Chức năng               | Khi nào dùng                   |
| -------------------------------------------------- | ------ | ----------------------- | ------------------------------ |
| `/`                                                | GET    | Thông tin hệ thống      | Kiểm tra API running           |
| `/health`                                          | GET    | Health check            | Monitoring, check MongoDB      |
| `/api/hybrid/initialize`                           | POST   | **Khởi tạo hệ thống**   | **BẮT BUỘC gọi đầu tiên**      |
| `/api/hybrid/user-recommendations/{user_id}`       | GET    | Gợi ý cho user          | Homepage "Gợi ý cho bạn"       |
| `/api/hybrid/product-recommendations/{product_id}` | GET    | Sản phẩm tương tự       | Trang sản phẩm "Similar items" |
| `/api/hybrid/promotion-strategy`                   | GET    | Chiến lược promotion    | Marketing planning             |
| `/api/huggingface/search-products`                 | GET    | Semantic search         | Search bar                     |
| `/api/pricing/optimize/{product_id}`               | GET    | Tối ưu giá 1 sản phẩm   | Pricing decision               |
| `/api/pricing/strategy`                            | GET    | Chiến lược giá tổng thể | Pricing planning               |
| `/api/analytics/business-health`                   | GET    | Tổng quan business      | Dashboard overview             |
| `/api/analytics/product-performance`               | GET    | Performance từng SP     | Product ranking                |
| `/api/analytics/customer-insights`                 | GET    | Phân tích khách hàng    | Customer segmentation          |
| `/api/analytics/trends`                            | GET    | Xu hướng thị trường     | Trend analysis                 |
| `/api/data/orders`                                 | GET    | Raw orders data         | Export data                    |
| `/api/data/products`                               | GET    | Danh sách sản phẩm      | Product catalog                |

---

## 🎯 USE CASES CHỦ YẾU

### 1️⃣ Setup lần đầu

```bash
POST /api/hybrid/initialize
# Đợi 10-30 giây
GET /health  # Check status: initialized
```

### 2️⃣ Homepage Website

```bash
# Gợi ý cá nhân hóa
GET /api/hybrid/user-recommendations/676eaf5cbf34ce78983409c3?top_k=6

# Top bán chạy
GET /api/analytics/product-performance
```

### 3️⃣ Trang sản phẩm

```bash
# Sản phẩm tương tự
GET /api/hybrid/product-recommendations/67643c2411d943b7bdecb7d3?top_k=4
```

### 4️⃣ Search

```bash
GET /api/huggingface/search-products?query=bánh+sinh+nhật&top_k=10
```

### 5️⃣ Admin Dashboard

```bash
GET /api/analytics/business-health      # Overview
GET /api/analytics/product-performance  # Products
GET /api/analytics/customer-insights    # Customers
GET /api/analytics/trends               # Trends
GET /api/pricing/strategy               # Pricing
```

### 6️⃣ Marketing Planning

```bash
POST /api/hybrid/generate-complete-strategy  # Comprehensive AI
GET /api/hybrid/promotion-strategy           # Promotions
```

---

## ⚡ RESPONSE TIMES

| Endpoint Type     | Thời gian | Notes              |
| ----------------- | --------- | ------------------ |
| Data access       | < 200ms   | Fast               |
| Analytics         | < 500ms   | Cached recommended |
| Recommendations   | < 1s      | After initialized  |
| Initialize        | 10-30s    | Background process |
| Complete strategy | 30-60s    | Calls Gemini LLM   |

---

## 🔑 KEY PARAMETERS

### Common Query Parameters

- `top_k`: Số lượng kết quả (1-50)
- `limit`: Giới hạn records (1-1000)
- `start_date`: Ngày bắt đầu (YYYY-MM-DD)
- `end_date`: Ngày kết thúc (YYYY-MM-DD)

### Common Path Parameters

- `{user_id}`: User ID (VD: `676eaf5cbf34ce78983409c3`)
- `{product_id}`: Product ID (VD: `67643c2411d943b7bdecb7d3`)

---

## 📊 RESPONSE FORMAT

Tất cả endpoints trả về JSON với structure:

```json
{
  "data_field": { ... },
  "count": 10,
  "timestamp": "2025-10-11T10:30:00"
}
```

Error format:

```json
{
  "detail": "Error message"
}
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

### ✅ BẮT BUỘC

1. **Gọi `/api/hybrid/initialize` TRƯỚC** khi dùng:

   - Recommendation endpoints
   - Pricing endpoints
   - ML model endpoints

2. **Kiểm tra `is_initialized`** status trước khi gọi recommendation APIs

### 💡 BEST PRACTICES

1. **Cache** analytics results (5-10 phút)
2. **Background jobs** cho initialize và complete strategy
3. **Retry logic** cho Gemini LLM calls
4. **Rate limiting** cho production

### 🚫 KHÔNG

1. Không gọi initialize liên tục (chỉ khi cần train lại)
2. Không gọi complete-strategy trong user flow (quá chậm)
3. Không query data endpoints quá thường xuyên (dùng cache)

---

## 🔗 FULL DOCUMENTATION

Chi tiết đầy đủ: [API_ENDPOINTS_GUIDE.md](./API_ENDPOINTS_GUIDE.md)

Interactive docs: http://localhost:8000/docs

---

**Version:** 2.0.0 | **Updated:** 2025-10-11
