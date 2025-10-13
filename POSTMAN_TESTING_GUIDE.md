# 🚀 POSTMAN TESTING GUIDE - AI PROMOTION SYSTEM API

## 📋 **CÁCH SỬ DỤNG POSTMAN COLLECTION**

### **1. Import Collection vào Postman**

1. **Mở Postman**
2. **Click "Import"** (góc trái trên)
3. **Chọn file**: `AI_Promotion_API.postman_collection.json`
4. **Click "Import"**

### **2. Setup Environment Variables**

1. **Click "Environments"** (sidebar trái)
2. **Click "Create Environment"**
3. **Tên**: `AI Promotion API`
4. **Thêm variables**:
   - `base_url`: `http://localhost:8000`
   - `user_id`: `676eaf5cbf34ce78983409c3`
   - `product_id`: `67643c2411d943b7bdecb7d3`
5. **Click "Save"**

### **3. Chọn Environment**

1. **Click dropdown "No Environment"** (góc phải trên)
2. **Chọn "AI Promotion API"**

---

## 🧪 **TESTING WORKFLOW**

### **Bước 1: Start API Server**

```bash
py -3.11 app/main_minimal.py
```

### **Bước 2: Test Basic Endpoints**

#### **🔍 Health Check**

1. **Chọn**: `🔍 Basic Endpoints > Health Check`
2. **Click "Send"**
3. **Expected Response**:

```json
{
  "status": "healthy",
  "services": {
    "mongodb": "connected/not_connected",
    "promotion_service": "initialized/not_initialized",
    "gemini": "configured/not_configured"
  },
  "data_availability": {
    "products": 0,
    "orders": 0
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

#### **📊 Root Endpoint**

1. **Chọn**: `🔍 Basic Endpoints > Root Endpoint`
2. **Click "Send"**
3. **Expected Response**: System information

### **Bước 3: Test Mock Endpoints (Không cần MongoDB)**

#### **🎭 Mock User Recommendations**

1. **Chọn**: `🎭 Mock Endpoints > Mock User Recommendations`
2. **Click "Send"**
3. **Expected Response**:

```json
{
  "user_id": "user123",
  "recommendations": [
    {
      "product_id": "product_1",
      "product_name": "Bánh Mock 1",
      "score": 0.9,
      "recommendation_type": "mock"
    }
  ],
  "model": "Mock Recommendation System",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### **🎯 Mock Promotion Strategy**

1. **Chọn**: `🎭 Mock Endpoints > Mock Promotion Strategy`
2. **Click "Send"**
3. **Expected Response**:

```json
{
  "strategy": {
    "current_season": "Spring 2024",
    "promotion_products": [
      {
        "product_id": "product_1",
        "product_name": "Bánh Mock 1",
        "discount_percentage": 20,
        "reason": "Sản phẩm bán chạy nhất"
      }
    ],
    "combo_suggestions": [
      {
        "combo": ["Bánh Mock 1", "Bánh Mock 2"],
        "price": 450000,
        "target": "Khách hàng VIP"
      }
    ],
    "promotion_schedule": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "discount_code": "SPRING2024"
    }
  },
  "model": "Mock Promotion Strategy",
  "timestamp": "2024-01-01T00:00:00"
}
```

### **Bước 4: Test Analytics Endpoints**

#### **📊 Business Health**

1. **Chọn**: `📊 Analytics & Reporting > Business Health`
2. **Click "Send"**
3. **Expected Response**: Business analytics (mock data nếu không có MongoDB)

#### **📈 Product Performance**

1. **Chọn**: `📊 Analytics & Reporting > Product Performance`
2. **Click "Send"**
3. **Expected Response**: Product performance data

### **Bước 5: Test Data Access Endpoints**

#### **💾 Get Products**

1. **Chọn**: `💾 Data Access > Get Products`
2. **Click "Send"**
3. **Expected Response**: Products data từ MongoDB hoặc empty array

#### **📦 Get Orders**

1. **Chọn**: `💾 Data Access > Get Orders`
2. **Click "Send"**
3. **Expected Response**: Orders data với filters

---

## 🎯 **TESTING SCENARIOS**

### **Scenario 1: Basic API Test (No MongoDB)**

1. ✅ Health Check
2. ✅ Root Endpoint
3. ✅ Mock User Recommendations
4. ✅ Mock Promotion Strategy
5. ✅ Business Health (mock data)

### **Scenario 2: Full API Test (With MongoDB)**

1. ✅ Health Check (MongoDB connected)
2. ✅ Initialize Hybrid System
3. ✅ User Recommendations
4. ✅ Product Recommendations
5. ✅ Promotion Strategy
6. ✅ All Analytics Endpoints
7. ✅ All Data Access Endpoints

### **Scenario 3: Individual Model Test**

1. ✅ TensorFlow Recommenders
2. ✅ HuggingFace Similar Products
3. ✅ HuggingFace Search Products
4. ✅ Price Optimization
5. ✅ Pricing Strategy

---

## 🚨 **TROUBLESHOOTING**

### **Error: Connection Refused**

- **Cause**: API server chưa chạy
- **Solution**: Chạy `py -3.11 app/main_minimal.py`

### **Error: MongoDB not connected**

- **Cause**: MongoDB chưa chạy
- **Solution**:
  - Start MongoDB: `net start MongoDB`
  - Hoặc dùng Mock endpoints

### **Error: 404 Not Found**

- **Cause**: Endpoint không tồn tại
- **Solution**: Kiểm tra URL và method

### **Error: 500 Internal Server Error**

- **Cause**: Server error
- **Solution**: Check server logs

---

## 📊 **EXPECTED RESPONSES**

### **Success Response Format**

```json
{
  "data": "...",
  "timestamp": "2024-01-01T00:00:00",
  "status": "success"
}
```

### **Error Response Format**

```json
{
  "detail": "Error message description"
}
```

---

## 🎉 **QUICK TEST COMMANDS**

### **Curl Commands (Alternative to Postman)**

```bash
# Health Check
curl http://localhost:8000/health

# Mock Recommendations
curl http://localhost:8000/api/mock/recommendations/user123

# Mock Strategy
curl http://localhost:8000/api/mock/promotion-strategy

# Business Health
curl http://localhost:8000/api/analytics/business-health

# Get Products
curl http://localhost:8000/api/data/products
```

### **Browser Testing**

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📚 **COLLECTION STRUCTURE**

```
AI Promotion System API
├── 🔍 Basic Endpoints
│   ├── Root Endpoint
│   └── Health Check
├── 🤖 Hybrid Recommendation System
│   ├── Initialize Hybrid System
│   ├── User Recommendations
│   ├── Product Recommendations
│   ├── Promotion Strategy
│   └── Generate Complete Strategy
├── 🧠 Individual Model Endpoints
│   ├── TensorFlow Recommenders
│   ├── HuggingFace Similar Products
│   ├── HuggingFace Search Products
│   ├── Price Optimization
│   └── Pricing Strategy
├── 📊 Analytics & Reporting
│   ├── Business Health
│   ├── Product Performance
│   ├── Customer Insights
│   └── Market Trends
├── 💾 Data Access
│   ├── Get Products
│   ├── Get Orders
│   ├── Get Users
│   ├── Get Ratings
│   ├── Get Discounts
│   └── Get Search Histories
├── 🎭 Mock Endpoints
│   ├── Mock User Recommendations
│   └── Mock Promotion Strategy
└── 🔄 Legacy Endpoints
    ├── Legacy Business Health
    ├── Legacy Product Combos
    ├── Legacy Recommendations
    ├── Legacy Generate Strategy
    └── Legacy Recent Strategies
```

---

**🎉 Happy Testing với AI Promotion System API!**
