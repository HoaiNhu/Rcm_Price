# 🚀 AI PROMOTION SYSTEM API - COMPLETE DOCUMENTATION

## 📋 **API OVERVIEW**

Hệ thống AI Promotion System cung cấp các API endpoints để:

- **Hybrid Recommendation System** với TensorFlow Recommenders, HuggingFace Transformers, Dynamic Pricing
- **Business Analytics** và reporting
- **Data Access** từ MongoDB
- **Individual Model** endpoints

**Base URL**: `http://localhost:8000`
**API Version**: `2.0.0`
**Documentation**: `http://localhost:8000/docs`

---

## 🔧 **SETUP & INSTALLATION**

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy và chỉnh sửa .env file
cp env_example.txt .env

# Thêm các biến môi trường:
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=bakery_ai
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start Server

```bash
# Development mode
python app/main.py

# Hoặc với uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📊 **API ENDPOINTS**

### **🔍 BASIC ENDPOINTS**

#### `GET /`

**Root endpoint với thông tin hệ thống**

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
  "timestamp": "2024-01-01T00:00:00",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

#### `GET /health`

**Comprehensive health check**

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
    "products": 33,
    "orders": 113
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

---

### **🤖 HYBRID RECOMMENDATION SYSTEM**

#### `POST /api/hybrid/initialize`

**Initialize hybrid recommendation system**

```bash
curl -X POST "http://localhost:8000/api/hybrid/initialize"
```

**Response:**

```json
{
  "message": "Hybrid system initialization started",
  "status": "processing",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### `GET /api/hybrid/user-recommendations/{user_id}`

**Get comprehensive recommendations for a user**

```bash
curl "http://localhost:8000/api/hybrid/user-recommendations/676eaf5cbf34ce78983409c3?top_k=10"
```

**Response:**

```json
{
  "user_id": "676eaf5cbf34ce78983409c3",
  "collaborative_filtering": [
    {
      "product_id": "67643c2411d943b7bdecb7d3",
      "score": 0.85,
      "recommendation_type": "collaborative_filtering"
    }
  ],
  "content_based": [
    {
      "product_id": "67643c7b11d943b7bdecb7db",
      "name": "Bánh Corequette",
      "similarity_score": 0.92,
      "recommendation_type": "content_based"
    }
  ],
  "pricing_optimization": [
    {
      "product_id": "67643c2411d943b7bdecb7d3",
      "current_price": 260000,
      "optimal_price": 280000,
      "price_change_percentage": 7.69,
      "recommendation": "Tăng giá nhẹ - Cơ hội tăng doanh thu"
    }
  ],
  "combined_recommendations": [
    {
      "product_id": "67643c2411d943b7bdecb7d3",
      "collaborative_score": 0.85,
      "content_score": 0.78,
      "pricing_score": 0.38,
      "combined_score": 0.67
    }
  ],
  "generated_at": "2024-01-01T00:00:00"
}
```

#### `GET /api/hybrid/product-recommendations/{product_id}`

**Get comprehensive recommendations for a product**

```bash
curl "http://localhost:8000/api/hybrid/product-recommendations/67643c2411d943b7bdecb7d3?top_k=5"
```

#### `GET /api/hybrid/promotion-strategy`

**Get comprehensive promotion strategy**

```bash
curl "http://localhost:8000/api/hybrid/promotion-strategy"
```

#### `POST /api/hybrid/generate-complete-strategy`

**Generate complete AI strategy using all models**

```bash
curl -X POST "http://localhost:8000/api/hybrid/generate-complete-strategy"
```

---

### **🧠 INDIVIDUAL MODEL ENDPOINTS**

#### `GET /api/tf-recommenders/recommendations/{user_id}`

**TensorFlow Recommenders recommendations**

```bash
curl "http://localhost:8000/api/tf-recommenders/recommendations/676eaf5cbf34ce78983409c3?top_k=5"
```

#### `GET /api/huggingface/similar-products/{product_id}`

**HuggingFace similar products**

```bash
curl "http://localhost:8000/api/huggingface/similar-products/67643c2411d943b7bdecb7d3?top_k=5"
```

#### `GET /api/huggingface/search-products`

**Search products using semantic search**

```bash
curl "http://localhost:8000/api/huggingface/search-products?query=bánh sinh nhật&top_k=5"
```

#### `GET /api/pricing/optimize/{product_id}`

**Optimize price for a specific product**

```bash
curl "http://localhost:8000/api/pricing/optimize/67643c2411d943b7bdecb7d3?target_date=2024-02-14"
```

#### `GET /api/pricing/strategy`

**Get comprehensive pricing strategy**

```bash
curl "http://localhost:8000/api/pricing/strategy"
```

---

### **📈 ANALYTICS & REPORTING**

#### `GET /api/analytics/business-health`

**Get comprehensive business analytics**

```bash
curl "http://localhost:8000/api/analytics/business-health"
```

#### `GET /api/analytics/product-performance`

**Get product performance analytics**

```bash
curl "http://localhost:8000/api/analytics/product-performance"
```

#### `GET /api/analytics/customer-insights`

**Get customer insights and segmentation**

```bash
curl "http://localhost:8000/api/analytics/customer-insights"
```

#### `GET /api/analytics/trends`

**Get market trends and patterns**

```bash
curl "http://localhost:8000/api/analytics/trends"
```

---

### **💾 DATA ACCESS ENDPOINTS**

#### `GET /api/data/orders`

**Get orders data with filters**

```bash
curl "http://localhost:8000/api/data/orders?limit=50&start_date=2024-01-01&end_date=2024-01-31"
```

#### `GET /api/data/products`

**Get products data**

```bash
curl "http://localhost:8000/api/data/products"
```

#### `GET /api/data/users`

**Get users data**

```bash
curl "http://localhost:8000/api/data/users"
```

#### `GET /api/data/ratings`

**Get ratings data**

```bash
curl "http://localhost:8000/api/data/ratings"
```

#### `GET /api/data/discounts`

**Get discounts data**

```bash
curl "http://localhost:8000/api/data/discounts"
```

#### `GET /api/data/search-histories`

**Get search histories data**

```bash
curl "http://localhost:8000/api/data/search-histories"
```

---

## 🧪 **API TESTING**

### **Test Script**

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_api():
    """Test all API endpoints"""

    # 1. Health Check
    print("🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # 2. Initialize Hybrid System
    print("\n🤖 Initializing Hybrid System...")
    response = requests.post(f"{BASE_URL}/api/hybrid/initialize")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # 3. Get User Recommendations
    print("\n👤 Testing User Recommendations...")
    user_id = "676eaf5cbf34ce78983409c3"  # Replace with actual user ID
    response = requests.get(f"{BASE_URL}/api/hybrid/user-recommendations/{user_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Recommendations: {len(response.json().get('combined_recommendations', []))}")

    # 4. Get Product Recommendations
    print("\n🍰 Testing Product Recommendations...")
    product_id = "67643c2411d943b7bdecb7d3"  # Replace with actual product ID
    response = requests.get(f"{BASE_URL}/api/hybrid/product-recommendations/{product_id}")
    print(f"Status: {response.status_code}")

    # 5. Get Business Analytics
    print("\n📊 Testing Business Analytics...")
    response = requests.get(f"{BASE_URL}/api/analytics/business-health")
    print(f"Status: {response.status_code}")

    # 6. Get Product Performance
    print("\n📈 Testing Product Performance...")
    response = requests.get(f"{BASE_URL}/api/analytics/product-performance")
    print(f"Status: {response.status_code}")

    # 7. Search Products
    print("\n🔍 Testing Product Search...")
    response = requests.get(f"{BASE_URL}/api/huggingface/search-products?query=bánh sinh nhật")
    print(f"Status: {response.status_code}")

    # 8. Price Optimization
    print("\n💰 Testing Price Optimization...")
    response = requests.get(f"{BASE_URL}/api/pricing/optimize/{product_id}")
    print(f"Status: {response.status_code}")

if __name__ == "__main__":
    test_api()
```

### **Postman Collection**

```json
{
  "info": {
    "name": "AI Promotion System API",
    "description": "Complete API collection for AI Promotion System",
    "version": "2.0.0"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "Initialize Hybrid System",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/hybrid/initialize"
      }
    },
    {
      "name": "User Recommendations",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/hybrid/user-recommendations/{{user_id}}?top_k=10"
      }
    },
    {
      "name": "Product Recommendations",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/hybrid/product-recommendations/{{product_id}}?top_k=5"
      }
    },
    {
      "name": "Business Analytics",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/analytics/business-health"
      }
    },
    {
      "name": "Product Performance",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/analytics/product-performance"
      }
    },
    {
      "name": "Search Products",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/huggingface/search-products?query=bánh sinh nhật&top_k=5"
      }
    },
    {
      "name": "Price Optimization",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/pricing/optimize/{{product_id}}"
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "user_id",
      "value": "676eaf5cbf34ce78983409c3"
    },
    {
      "key": "product_id",
      "value": "67643c2411d943b7bdecb7d3"
    }
  ]
}
```

---

## 🚨 **ERROR HANDLING**

### **Common Error Codes**

- `400 Bad Request`: Invalid parameters or system not initialized
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### **Error Response Format**

```json
{
  "detail": "Error message description"
}
```

### **Troubleshooting**

1. **System not initialized**: Call `/api/hybrid/initialize` first
2. **MongoDB connection failed**: Check `MONGODB_URL` in `.env`
3. **Gemini API error**: Check `GEMINI_API_KEY` in `.env`
4. **No data found**: Ensure MongoDB has data

---

## 📚 **USAGE EXAMPLES**

### **1. Complete Workflow**

```python
import requests

# 1. Check system health
health = requests.get("http://localhost:8000/health").json()
print(f"System status: {health['status']}")

# 2. Initialize hybrid system
init_response = requests.post("http://localhost:8000/api/hybrid/initialize")
print(f"Initialization: {init_response.json()['status']}")

# 3. Get user recommendations
user_recs = requests.get("http://localhost:8000/api/hybrid/user-recommendations/USER_ID").json()
print(f"Found {len(user_recs['combined_recommendations'])} recommendations")

# 4. Get promotion strategy
strategy = requests.get("http://localhost:8000/api/hybrid/promotion-strategy").json()
print(f"Strategy generated: {strategy['current_season']}")
```

### **2. Frontend Integration**

```javascript
// React/Vue.js example
const API_BASE = "http://localhost:8000";

// Get user recommendations
const getUserRecommendations = async (userId) => {
  const response = await fetch(
    `${API_BASE}/api/hybrid/user-recommendations/${userId}`
  );
  return await response.json();
};

// Search products
const searchProducts = async (query) => {
  const response = await fetch(
    `${API_BASE}/api/huggingface/search-products?query=${query}`
  );
  return await response.json();
};

// Get business analytics
const getBusinessAnalytics = async () => {
  const response = await fetch(`${API_BASE}/api/analytics/business-health`);
  return await response.json();
};
```

---

## 🎯 **PERFORMANCE & SCALING**

### **Response Times**

- **Basic endpoints**: < 100ms
- **Analytics endpoints**: < 500ms
- **Hybrid recommendations**: < 2s
- **Complete strategy generation**: < 10s (background)

### **Rate Limits**

- **No rate limits** currently implemented
- **Background processing** for heavy operations
- **Caching** recommended for production

### **Production Deployment**

```bash
# Using Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker
docker build -t ai-promotion-api .
docker run -p 8000:8000 ai-promotion-api
```

---

## 📞 **SUPPORT**

- **API Documentation**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`
- **GitHub Issues**: Create issue for bugs/features
- **Email Support**: [Your email]

---

**🎉 Happy Coding với AI Promotion System API!**
