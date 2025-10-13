# 🍰 AI PROMOTION SYSTEM - HƯỚNG DẪN SỬ DỤNG

## 🚀 Cài đặt và Chạy

### 1. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình Environment

```bash
# Copy file env_example.txt thành .env
cp env_example.txt .env

# Chỉnh sửa .env với thông tin thực tế:
# - MONGODB_URL: Đường dẫn MongoDB của bạn
# - GEMINI_API_KEY: API key từ Google AI Studio
```

### 3. Chạy Server

```bash
# Development mode
python app/main.py

# Hoặc với uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 API Endpoints

### Health Check

```bash
GET /health
```

### Business Analysis

```bash
GET /api/business-health
```

### Product Analysis

```bash
GET /api/product-combos
GET /api/recommendations
```

### Generate Complete Strategy

```bash
POST /api/generate-strategy
```

### Get Recent Strategies

```bash
GET /api/recent-strategies?limit=5
```

### Raw Data Access

```bash
GET /api/data/orders
GET /api/data/products
GET /api/data/users
GET /api/data/ratings
GET /api/data/discounts
```

## 🔧 Sử dụng trong Code

### 1. Import và Initialize - ENHANCED VERSION

```python
# Option 1: Hybrid System (Recommended)
from application.services.hybrid_recommender import create_hybrid_recommender

# Initialize hybrid system
hybrid_system = create_hybrid_recommender("your_gemini_api_key")
hybrid_system.initialize_system()

# Generate complete strategy
strategy = hybrid_system.generate_complete_ai_strategy()

# Option 2: Individual Models
from infrastructure.ml_models.tf_recommenders import create_tf_recommender
from infrastructure.ml_models.huggingface_filter import create_hf_content_filter
from infrastructure.ml_models.dynamic_pricing import create_dynamic_pricing_model

# Initialize individual models
tf_recommender = create_tf_recommender()
hf_filter = create_hf_content_filter()
pricing_model = create_dynamic_pricing_model()

# Option 3: Original Service
from application.services.ai_promotion_service import create_promotion_service
promotion_service = create_promotion_service("your_gemini_api_key")
```

### 2. Phân tích từng phần

```python
# Business health analysis
business_health = promotion_service.analyze_business_health()

# Product combo discovery
combos = promotion_service.discover_product_combos()

# Product recommendations
recommendations = promotion_service.generate_recommendations()
```

### 3. Truy cập MongoDB trực tiếp

```python
from infrastructure.db.mongodb_access import mongodb_data

# Get orders data
orders_df = mongodb_data.get_orders_data()

# Get products data
products_df = mongodb_data.get_products_data()

# Get all business data
all_data = mongodb_data.get_all_business_data()
```

## 📈 Output Examples

### Business Health Analysis

```json
{
  "total_orders": 113,
  "total_revenue": 25000000,
  "avg_order_value": 221238,
  "product_performance": {
    "67643c2411d943b7bdecb7d3": {
      "name": "Bánh hoa xuân",
      "price": 260000,
      "orders_count": 45,
      "total_revenue": 11700000,
      "avg_rating": 4.3
    }
  }
}
```

### Product Combos

```json
{
  "combos": [
    {
      "antecedents": ["67643c2411d943b7bdecb7d3"],
      "consequents": ["67643c7b11d943b7bdecb7db"],
      "support": 0.15,
      "confidence": 0.75,
      "lift": 2.1
    }
  ]
}
```

### LLM Insights

```json
{
  "llm_insights": {
    "promotion_products": [
      {
        "product_id": "67643c2411d943b7bdecb7d3",
        "name": "Bánh hoa xuân",
        "discount_percentage": 20,
        "reason": "Sản phẩm bán chạy nhất, có thể tăng doanh số"
      }
    ],
    "combo_suggestions": [
      {
        "combo": ["Bánh hoa xuân", "Bánh Corequette"],
        "price": 450000,
        "target": "Khách hàng VIP"
      }
    ]
  }
}
```

## 🎯 Lợi ích của việc sử dụng MongoDB

### ✅ So với CSV Files:

1. **Real-time Data**: Dữ liệu luôn cập nhật
2. **Scalability**: Xử lý được dataset lớn
3. **Flexibility**: Schema linh hoạt
4. **Performance**: Query nhanh hơn
5. **Integration**: Tích hợp trực tiếp với app

### ✅ Features:

- **Automatic Data Sync**: Không cần export/import
- **Real-time Analysis**: Phân tích dữ liệu mới nhất
- **Persistent Storage**: Lưu trữ kết quả AI
- **API Integration**: RESTful API endpoints
- **Background Processing**: Xử lý không đồng bộ

## 🔍 Monitoring và Debugging

### Logs

```bash
# Check logs
tail -f logs/ai_promotion.log
```

### MongoDB Queries

```javascript
// Check collections
db.orders.count();
db.products.count();
db.ai_insights.find().sort({ created_at: -1 }).limit(5);
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test business analysis
curl http://localhost:8000/api/business-health
```

## 🚨 Troubleshooting

### Common Issues:

1. **MongoDB Connection Failed**

   - Check MONGODB_URL in .env
   - Ensure MongoDB is running

2. **Gemini API Error**

   - Check GEMINI_API_KEY in .env
   - Verify API quota

3. **No Data Found**

   - Check if collections exist
   - Verify data format

4. **Performance Issues**
   - Add indexes to MongoDB
   - Use pagination for large datasets

## 📞 Support

Nếu gặp vấn đề:

1. Check logs trong `logs/ai_promotion.log`
2. Verify environment variables
3. Test MongoDB connection
4. Check API endpoints với curl/Postman
