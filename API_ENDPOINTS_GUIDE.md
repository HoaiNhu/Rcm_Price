# 📚 HƯỚNG DẪN SỬ DỤNG API ENDPOINTS - RCM_PRICE

## 🎯 Tổng Quan

API cung cấp hệ thống AI recommendation và pricing cho cửa hàng bánh ngọt, bao gồm:

- Recommendation System (TensorFlow, HuggingFace)
- Dynamic Pricing
- Business Analytics
- Data Management

---

## 📋 1. BASIC ENDPOINTS

### GET `/`

**Chức năng:** Root endpoint - Thông tin tổng quan về hệ thống

**Response:**

```json
{
  "message": "AI Promotion System API v2.0",
  "version": "2.0.0",
  "status": "running",
  "features": [
    "MongoDB Integration",
    "TensorFlow Recommenders",
    "HuggingFace Transformers",
    "Dynamic Pricing Models",
    "Hybrid Recommendation System",
    "Gemini LLM Integration"
  ],
  "timestamp": "2025-10-11T10:30:00",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

**Khi nào dùng:** Kiểm tra xem API có đang chạy không, xem danh sách features

---

### GET `/health`

**Chức năng:** Health check - Kiểm tra trạng thái hệ thống

**Response:**

```json
{
  "status": "healthy",
  "services": {
    "mongodb": "connected",
    "promotion_service": "initialized",
    "hybrid_system": "initialized",
    "gemini": "configured"
  },
  "data_availability": {
    "products": 31,
    "orders": 111
  },
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Monitoring hệ thống
- Kiểm tra kết nối MongoDB
- Xem số lượng data có sẵn

---

## 🤖 2. HYBRID RECOMMENDATION SYSTEM

### POST `/api/hybrid/initialize`

**Chức năng:** Khởi tạo Hybrid Recommendation System (chạy background)

**Quy trình:**

1. Load data từ MongoDB (orders, products, users, ratings)
2. Prepare data cho TensorFlow Recommenders
3. Build & train TensorFlow models
4. Tạo embeddings cho HuggingFace
5. Prepare pricing data
6. Train pricing models

**Response:**

```json
{
  "message": "Hybrid system initialization started",
  "status": "processing",
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Lần đầu khởi động hệ thống
- Khi có data mới cần train lại models
- **BẮT BUỘC** phải gọi trước khi dùng các endpoints khác

**Lưu ý:** Quá trình có thể mất 10-30 giây

---

### GET `/api/hybrid/user-recommendations/{user_id}?top_k=10`

**Chức năng:** Gợi ý sản phẩm cho user cụ thể (hybrid của nhiều models)

**Parameters:**

- `user_id` (path): ID của user (VD: `676eaf5cbf34ce78983409c3`)
- `top_k` (query): Số lượng recommendations (1-50, default: 10)

**Response:**

```json
{
  "user_id": "676eaf5cbf34ce78983409c3",
  "recommendations": [
    {
      "product_id": "67643c2411d943b7bdecb7d3",
      "product_name": "Bánh Tiramisu",
      "score": 0.85,
      "recommendation_type": "collaborative_filtering",
      "price": 250000,
      "estimated_interest": "high"
    }
  ],
  "sources": {
    "tensorflow": 5,
    "huggingface": 3,
    "gemini": 2
  },
  "timestamp": "2025-10-11T10:30:00"
}
```

**Algorithms sử dụng:**

- Collaborative Filtering (TensorFlow) - dựa vào lịch sử mua hàng
- Content-based (HuggingFace) - dựa vào mô tả sản phẩm
- LLM insights (Gemini) - phân tích sở thích user

**Khi nào dùng:**

- Trang "Gợi ý cho bạn" trên homepage
- Email marketing cá nhân hóa
- Popup "Bạn có thể thích"

---

### GET `/api/hybrid/product-recommendations/{product_id}?top_k=10`

**Chức năng:** Gợi ý sản phẩm tương tự (cross-sell, up-sell)

**Parameters:**

- `product_id` (path): ID của sản phẩm
- `top_k` (query): Số lượng recommendations (1-50, default: 10)

**Response:**

```json
{
  "product_id": "67643c2411d943b7bdecb7d3",
  "product_name": "Bánh Tiramisu",
  "similar_products": [
    {
      "product_id": "67643c2411d943b7bdecb7d4",
      "product_name": "Bánh Mousse",
      "similarity_score": 0.92,
      "reason": "Cùng loại bánh kem, hương vị tương tự"
    }
  ],
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Trang chi tiết sản phẩm: "Sản phẩm tương tự"
- Giỏ hàng: "Thêm món này nhé"
- After checkout: "Mua thêm"

---

### GET `/api/hybrid/promotion-strategy`

**Chức năng:** Chiến lược promotion tổng thể cho toàn cửa hàng

**Response:**

```json
{
  "promotion_strategy": {
    "target_products": [
      {
        "product_id": "67643c2411d943b7bdecb7d3",
        "product_name": "Bánh Tiramisu",
        "current_price": 250000,
        "suggested_discount": 15,
        "reason": "Doanh số giảm 20% tuần trước",
        "expected_revenue_increase": "30%"
      }
    ],
    "target_customers": [
      {
        "segment": "VIP customers",
        "size": 50,
        "suggested_offer": "Free shipping + 10% discount"
      }
    ],
    "best_time": "Weekend (Sat-Sun)",
    "total_expected_revenue": 50000000
  },
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Planning marketing campaign
- Weekly/Monthly promotion planning
- Dashboard cho manager

---

### POST `/api/hybrid/generate-complete-strategy`

**Chức năng:** Tạo chiến lược AI toàn diện (chạy background, rất mạnh)

**Quy trình:**

1. Phân tích business health
2. Tìm product combos (bundle)
3. Pricing optimization
4. Customer segmentation
5. LLM insights từ Gemini
6. Tạo báo cáo hoàn chỉnh

**Response:**

```json
{
  "message": "Complete AI strategy generation started",
  "status": "processing",
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Cuối tuần/tháng để planning
- Khi cần insights sâu về business
- Quarterly review

**Lưu ý:** Có thể mất 30-60 giây vì gọi Gemini LLM

---

## 🧠 3. INDIVIDUAL MODEL ENDPOINTS

### GET `/api/tf-recommenders/recommendations/{user_id}?top_k=5`

**Chức năng:** Recommendations từ TensorFlow Recommenders (collaborative filtering)

**Algorithm:** Matrix Factorization - dựa vào lịch sử mua hàng của user và users tương tự

**Response:**

```json
{
  "user_id": "676eaf5cbf34ce78983409c3",
  "recommendations": [
    {
      "product_id": "67643c2411d943b7bdecb7d3",
      "score": 0.85,
      "recommendation_type": "collaborative_filtering"
    }
  ],
  "model": "TensorFlow Recommenders",
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Khi chỉ cần collaborative filtering
- A/B testing so sánh models
- Research/Development

**Lưu ý:** Nếu TensorFlow chưa cài, trả về empty array

---

### GET `/api/huggingface/similar-products/{product_id}?top_k=5`

**Chức năng:** Tìm sản phẩm tương tự bằng HuggingFace embeddings

**Algorithm:** Sentence Transformers - so sánh semantic similarity của product descriptions

**Response:**

```json
{
  "product_id": "67643c2411d943b7bdecb7d3",
  "similar_products": [
    {
      "product_id": "67643c2411d943b7bdecb7d4",
      "product_name": "Bánh Mousse Chocolate",
      "similarity_score": 0.92,
      "description": "Bánh mousse chocolate cao cấp"
    }
  ],
  "model": "HuggingFace Transformers",
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Content-based recommendation
- Tìm sản phẩm thay thế khi hết hàng
- Product discovery

---

### GET `/api/huggingface/search-products?query=bánh sinh nhật&top_k=5`

**Chức năng:** Semantic search - tìm sản phẩm theo ý nghĩa, không chỉ keyword

**Parameters:**

- `query` (required): Search query (VD: "bánh sinh nhật", "món ngọt cho người ăn kiêng")
- `top_k` (optional): Số kết quả (1-20, default: 5)

**Response:**

```json
{
  "query": "bánh sinh nhật",
  "results": [
    {
      "product_id": "67643c2411d943b7bdecb7d3",
      "product_name": "Bánh Tiramisu Size L",
      "similarity_score": 0.88,
      "price": 350000,
      "description": "Phù hợp cho sinh nhật 10-15 người"
    }
  ],
  "model": "HuggingFace Transformers",
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Search bar trên website
- Chatbot: "Tìm bánh cho sinh nhật"
- Voice search

**Ưu điểm:** Hiểu được ngữ nghĩa, VD: "món ngọt ít calo" sẽ tìm được "Bánh kem trái cây"

---

### GET `/api/pricing/optimize/{product_id}?target_date=2025-10-15`

**Chức năng:** Tối ưu giá cho sản phẩm cụ thể

**Parameters:**

- `product_id` (path): ID sản phẩm
- `target_date` (query, optional): Ngày mục tiêu (YYYY-MM-DD), default: hôm nay

**Response:**

```json
{
  "product_id": "67643c2411d943b7bdecb7d3",
  "product_name": "Bánh Tiramisu",
  "optimization": {
    "current_price": 250000,
    "optimal_price": 230000,
    "price_change_percentage": -8,
    "predicted_demand": 45,
    "predicted_revenue": 10350000,
    "price_elasticity": -0.5,
    "recommendation": "Giảm giá nhẹ - Cạnh tranh giá",
    "price_analysis": [
      {
        "price": 200000,
        "predicted_demand": 50,
        "predicted_revenue": 10000000
      },
      {
        "price": 230000,
        "predicted_demand": 45,
        "predicted_revenue": 10350000
      },
      {
        "price": 250000,
        "predicted_demand": 40,
        "predicted_revenue": 10000000
      }
    ]
  },
  "model": "Dynamic Pricing",
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Planning giá cho promotion
- Seasonal pricing (Giáng Sinh, Tết)
- Flash sale pricing

**Factors được xét:**

- Lịch sử mua hàng
- Weekday/Weekend
- Holidays (Valentine, Christmas...)
- Product rating
- Price elasticity

---

### GET `/api/pricing/strategy`

**Chức năng:** Chiến lược giá tổng thể cho tất cả sản phẩm

**Response:**

```json
{
  "pricing_strategy": {
    "increase_price": [
      {
        "product_id": "67643c2411d943b7bdecb7d3",
        "product_name": "Bánh Tiramisu",
        "current_price": 250000,
        "optimal_price": 280000,
        "price_change_percentage": 12,
        "predicted_revenue": 15000000,
        "recommendation": "Tăng giá mạnh - Sản phẩm có thể chịu được giá cao hơn"
      }
    ],
    "decrease_price": [
      {
        "product_id": "67643c2411d943b7bdecb7d4",
        "product_name": "Bánh Mousse",
        "current_price": 200000,
        "optimal_price": 170000,
        "price_change_percentage": -15,
        "predicted_revenue": 8500000,
        "recommendation": "Giảm giá mạnh - Cần khuyến mãi để tăng doanh số"
      }
    ],
    "keep_price": [
      {
        "product_id": "67643c2411d943b7bdecb7d5",
        "product_name": "Bánh Flan",
        "current_price": 150000,
        "optimal_price": 152000,
        "price_change_percentage": 1.3,
        "recommendation": "Giữ nguyên giá - Giá hiện tại đã tối ưu"
      }
    ],
    "promotion_candidates": [
      // Danh sách sản phẩm nên làm promotion
    ]
  },
  "model": "Dynamic Pricing",
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Weekly pricing review
- Dashboard cho manager
- Pricing planning meeting

---

## 📊 4. ANALYTICS & REPORTING

### GET `/api/analytics/business-health`

**Chức năng:** Phân tích tổng quan sức khỏe kinh doanh

**Response:**

```json
{
  "analytics": {
    "overall_health": "good",
    "health_score": 75,
    "metrics": {
      "total_revenue": 85000000,
      "total_orders": 111,
      "average_order_value": 765765,
      "total_products": 31,
      "total_customers": 22,
      "repeat_customer_rate": 45,
      "top_selling_products": [
        {
          "product_id": "67643c2411d943b7bdecb7d3",
          "product_name": "Bánh Tiramisu",
          "units_sold": 45,
          "revenue": 11250000
        }
      ],
      "revenue_trend": "increasing",
      "customer_satisfaction": 4.5
    },
    "insights": [
      "Doanh thu tăng 15% so với tuần trước",
      "Tỷ lệ khách quay lại cao (45%)",
      "Top 3 sản phẩm chiếm 60% doanh thu"
    ],
    "recommendations": [
      "Tăng marketing cho sản phẩm bán chậm",
      "Tạo combo bundle từ top products",
      "Focus vào retention customers"
    ]
  },
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Dashboard tổng quan
- Weekly/Monthly reports
- Meeting với stakeholders

---

### GET `/api/analytics/product-performance`

**Chức năng:** Phân tích hiệu suất từng sản phẩm

**Response:**

```json
{
  "product_performance": [
    {
      "product_id": "67643c2411d943b7bdecb7d3",
      "product_name": "Bánh Tiramisu",
      "price": 250000,
      "orders_count": 45,
      "total_revenue": 11250000,
      "avg_rating": 4.8,
      "total_ratings": 12,
      "popularity_score": 43.2
    }
  ],
  "total_products": 31,
  "timestamp": "2025-10-11T10:30:00"
}
```

**Metrics:**

- `orders_count`: Số lần được mua
- `total_revenue`: Tổng doanh thu
- `avg_rating`: Rating trung bình (1-5)
- `popularity_score`: orders_count × (avg_rating/5)

**Khi nào dùng:**

- Product ranking
- Quyết định ngừng/tiếp tục sản phẩm
- Inventory planning

---

### GET `/api/analytics/customer-insights`

**Chức năng:** Phân tích hành vi khách hàng

**Response:**

```json
{
  "customer_insights": {
    "total_customers": 22,
    "active_customers": 15,
    "repeat_customers": 8,
    "avg_orders_per_customer": 5.05,
    "top_customers": [
      {
        "user_id": "676eaf5cbf34ce78983409c3",
        "user_name": "Nguyễn Văn A",
        "order_count": 12
      }
    ],
    "customer_segments": {
      "vip": 5,
      "regular": 10,
      "new": 7
    }
  },
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Customer segmentation
- Loyalty program planning
- Personalized marketing

---

### GET `/api/analytics/trends`

**Chức năng:** Phân tích xu hướng thị trường

**Response:**

```json
{
  "trends": {
    "daily_trends": {
      "2025-10-01": 5,
      "2025-10-02": 8,
      "2025-10-03": 12
    },
    "monthly_trends": {
      "1": 20,
      "2": 25,
      "3": 18
    },
    "weekday_trends": {
      "0": 15, // Monday
      "5": 25, // Saturday
      "6": 30 // Sunday
    },
    "search_trends": {
      "bánh sinh nhật": 15,
      "bánh kem": 12,
      "tiramisu": 8
    }
  },
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Staffing planning (Weekend vs Weekday)
- Inventory planning
- Marketing timing

---

## 💾 5. DATA ACCESS ENDPOINTS

### GET `/api/data/orders?limit=100&start_date=2025-01-01&end_date=2025-10-11`

**Chức năng:** Lấy raw data đơn hàng

**Parameters:**

- `limit` (optional): Giới hạn số records (1-1000)
- `start_date` (optional): Ngày bắt đầu (YYYY-MM-DD)
- `end_date` (optional): Ngày kết thúc (YYYY-MM-DD)

**Response:**

```json
{
  "orders": [
    {
      "_id": "676d7cce4d065cdde8cce2c6",
      "orderCode": "ORD-1735228622685",
      "orderItems": [
        {
          "product": "67643c2411d943b7bdecb7d3",
          "quantity": 3,
          "total": 750000
        }
      ],
      "userId": "6756e4441df899603742e267",
      "totalPrice": 780000,
      "createdAt": "2024-12-26 15:57:02.710000"
    }
  ],
  "count": 111,
  "filters": {
    "limit": 100,
    "start_date": "2025-01-01",
    "end_date": "2025-10-11"
  },
  "timestamp": "2025-10-11T10:30:00"
}
```

**Khi nào dùng:**

- Export data
- Custom analytics
- Data integration với hệ thống khác

---

### GET `/api/data/products`

**Chức năng:** Lấy danh sách tất cả sản phẩm

**Response:**

```json
{
  "products": [
    {
      "_id": "67643c2411d943b7bdecb7d3",
      "productName": "Bánh Tiramisu",
      "productPrice": 250000,
      "productDescription": "Bánh Tiramisu cao cấp từ Ý",
      "averageRating": 4.8,
      "categoryId": "67643c2411d943b7bdecb7d1"
    }
  ],
  "count": 31,
  "timestamp": "2025-10-11T10:30:00"
}
```

---

### GET `/api/data/users`

**Chức năng:** Lấy danh sách users

**Response:**

```json
{
  "users": [
    {
      "_id": "676eaf5cbf34ce78983409c3",
      "userName": "Nguyễn Văn A",
      "userEmail": "nguyenvana@gmail.com",
      "userPhone": "0123456789"
    }
  ],
  "count": 22,
  "timestamp": "2025-10-11T10:30:00"
}
```

---

### GET `/api/data/ratings`

**Chức năng:** Lấy ratings/reviews của sản phẩm

**Response:**

```json
{
  "ratings": [
    {
      "_id": "676eaf5cbf34ce78983409c4",
      "productId": "67643c2411d943b7bdecb7d3",
      "userId": "676eaf5cbf34ce78983409c3",
      "rating": 5,
      "comment": "Bánh rất ngon!"
    }
  ],
  "count": 26,
  "timestamp": "2025-10-11T10:30:00"
}
```

---

### GET `/api/data/discounts`

**Chức năng:** Lấy danh sách mã giảm giá

**Response:**

```json
{
  "discounts": [
    {
      "_id": "676eaf5cbf34ce78983409c5",
      "discountCode": "SUMMER2025",
      "discountValue": 15,
      "validFrom": "2025-06-01",
      "validTo": "2025-08-31"
    }
  ],
  "count": 3,
  "timestamp": "2025-10-11T10:30:00"
}
```

---

### GET `/api/data/search-histories`

**Chức năng:** Lấy lịch sử search của users

**Response:**

```json
{
  "search_histories": [
    {
      "_id": "676eaf5cbf34ce78983409c6",
      "userId": "676eaf5cbf34ce78983409c3",
      "query": "bánh sinh nhật",
      "timestamp": "2025-10-10 14:30:00"
    }
  ],
  "count": 0,
  "timestamp": "2025-10-11T10:30:00"
}
```

---

## 🔄 WORKFLOW ĐIỂN HÌNH

### Scenario 1: Setup hệ thống lần đầu

```
1. GET /health → Kiểm tra MongoDB connected
2. POST /api/hybrid/initialize → Initialize toàn bộ system (đợi 10-30s)
3. GET /api/analytics/business-health → Xem tổng quan business
```

### Scenario 2: Trang chủ website

```
1. GET /api/hybrid/user-recommendations/{user_id}?top_k=6
   → Hiển thị "Gợi ý cho bạn"

2. GET /api/analytics/product-performance
   → Hiển thị "Bán chạy nhất"
```

### Scenario 3: Trang chi tiết sản phẩm

```
1. GET /api/data/products → Lấy thông tin sản phẩm

2. GET /api/hybrid/product-recommendations/{product_id}?top_k=4
   → Hiển thị "Sản phẩm tương tự"

3. GET /api/data/ratings → Hiển thị reviews
```

### Scenario 4: Search bar

```
1. GET /api/huggingface/search-products?query=bánh+sinh+nhật&top_k=10
   → Semantic search
```

### Scenario 5: Admin Dashboard

```
1. GET /api/analytics/business-health
   → Overview metrics

2. GET /api/analytics/product-performance
   → Product rankings

3. GET /api/analytics/customer-insights
   → Customer segmentation

4. GET /api/analytics/trends
   → Market trends

5. GET /api/pricing/strategy
   → Pricing recommendations
```

### Scenario 6: Weekly Marketing Planning

```
1. POST /api/hybrid/generate-complete-strategy
   → Generate comprehensive strategy (đợi 30-60s)

2. GET /api/hybrid/promotion-strategy
   → Get promotion recommendations

3. GET /api/pricing/strategy
   → Get pricing strategy
```

---

## ⚙️ TECHNICAL NOTES

### Required: Initialize trước khi dùng

Các endpoints sau **BẮT BUỘC** phải gọi `/api/hybrid/initialize` trước:

- `/api/hybrid/user-recommendations/*`
- `/api/hybrid/product-recommendations/*`
- `/api/hybrid/promotion-strategy`
- `/api/tf-recommenders/*`
- `/api/huggingface/*`
- `/api/pricing/*`

### Background Processing

Các endpoints chạy background (không đợi kết quả ngay):

- `POST /api/hybrid/initialize`
- `POST /api/hybrid/generate-complete-strategy`
- `POST /api/generate-strategy` (legacy)

### Rate Limiting Suggestions

- Analytics endpoints: 10 requests/minute
- Data endpoints: 100 requests/minute
- Recommendation endpoints: 50 requests/minute

### Caching Recommendations

- Business health: Cache 5 minutes
- Product performance: Cache 10 minutes
- User recommendations: Cache 1 hour (hoặc invalidate khi user mua hàng)
- Pricing strategy: Cache 1 day

---

## 🔗 SWAGGER DOCUMENTATION

Xem full interactive docs tại:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

**Last Updated:** 2025-10-11  
**API Version:** 2.0.0
