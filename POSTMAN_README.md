# 📦 POSTMAN COLLECTION - RCM PRICE API

## 📋 Tổng quan

Complete Postman Collection để test **100% API endpoints** trong AI Promotion System.

### 🎯 Nội dung Collection

- **13 Modules** (Folders)
- **100+ Endpoints**
- **Full CRUD Operations**
- **Pre-configured Examples**
- **Environment Variables**

---

## 📁 Files trong Package

```
RCM_PRICE/
├── RCM_PRICE_Complete_API_Tests.postman_collection.json  # Main Collection
├── RCM_PRICE_Local.postman_environment.json              # Environment Variables
├── POSTMAN_QUICK_START.md                                # 5-min Quick Start
├── POSTMAN_TESTING_COMPLETE_GUIDE.md                     # Hướng dẫn chi tiết
└── POSTMAN_README.md                                     # File này
```

---

## 🚀 Quick Start (5 phút)

### 1. Import Collection & Environment

**Trong Postman:**

1. Click **Import**
2. Select files:
   - `RCM_PRICE_Complete_API_Tests.postman_collection.json`
   - `RCM_PRICE_Local.postman_environment.json`
3. Click **Import**

### 2. Select Environment

- Click dropdown ở góc trên phải
- Chọn **"RCM PRICE - Local Environment"**

### 3. Start Testing!

- Mở folder **"01. Basic & Health"**
- Click **"Health Check"**
- Click **Send** ✅

---

## 📚 13 Modules trong Collection

| #    | Module                    | Endpoints | Description                             |
| ---- | ------------------------- | --------- | --------------------------------------- |
| 1️⃣   | **Basic & Health**        | 2         | System info & health check              |
| 2️⃣   | **Data Access**           | 6         | Get products, users, orders, ratings    |
| 3️⃣   | **Analytics**             | 5         | Business metrics & insights             |
| 4️⃣   | **Customer Segmentation** | 11        | RFM segmentation, VIP/At-Risk customers |
| 5️⃣   | **Price Elasticity**      | 6         | Demand elasticity analysis              |
| 6️⃣   | **Personalized Pricing**  | 8         | Dynamic pricing per customer            |
| 7️⃣   | **Pricing Simulator**     | 6         | Monte Carlo simulations                 |
| 8️⃣   | **Smart Promotions**      | 8         | AI-powered vouchers & campaigns         |
| 9️⃣   | **Event Promotions**      | 6         | Event-based marketing                   |
| 🔟   | **Hybrid Recommender**    | 5         | ML-based recommendations                |
| 1️⃣1️⃣ | **ML Models**             | 5         | TensorFlow & HuggingFace APIs           |
| 1️⃣2️⃣ | **Legacy Endpoints**      | 5         | Backward compatibility                  |
| 1️⃣3️⃣ | **Test Endpoints**        | 4         | Debug & testing                         |

**Total: 77 endpoints** ✨

---

## 🎯 Most Important Endpoints

### 🔥 Top 5 Must-Try

1. **Customer Segmentation**

   ```
   POST /api/customer-segmentation/segment
   ```

   → Phân loại tất cả customers thành VIP, REGULAR, AT_RISK, etc.

2. **Find Optimal Price**

   ```
   POST /api/pricing-simulator/find-optimal
   ```

   → Tìm giá tối ưu bằng Monte Carlo simulation

3. **Personalized Catalog**

   ```
   GET /api/personalized-pricing/catalog/{user_id}
   ```

   → Xem giá cá nhân hóa cho từng customer

4. **Generate Smart Promotion**

   ```
   POST /api/smart-promotions/generate-segment-promotion
   ```

   → Tạo promotion tự động cho từng segment

5. **Business Health**
   ```
   GET /api/analytics/business-health
   ```
   → Dashboard overview toàn bộ business

---

## 📊 Test Flows

### Flow 1: Quick System Check (2 phút)

```
Health Check → Get Products → Get Users → Business Health
```

### Flow 2: Customer Analysis (5 phút)

```
Segment Customers → Get VIP List → Get At-Risk → Generate Winback Campaign
```

### Flow 3: Pricing Strategy (10 phút)

```
Analyze Elasticity → Get Personalized Prices → Simulate Scenarios → Find Optimal
```

### Flow 4: Campaign Creation (8 phút)

```
Discover Combos → Analyze Products → Generate Event Promotion → Generate Smart Promotion
```

---

## 🔧 Environment Variables

| Variable      | Default Value              | Usage                |
| ------------- | -------------------------- | -------------------- |
| `base_url`    | `http://localhost:8000`    | API base URL         |
| `product_id`  | `674cfc8e2b4c648fe8c2c7dd` | Sample product ID    |
| `user_id`     | `674cfcb62b4c648fe8c2c7e3` | Sample user ID       |
| `api_version` | `2.0.0`                    | API version          |
| `timeout`     | `5000`                     | Request timeout (ms) |

**💡 Tip:** Update `product_id` và `user_id` với ID thực từ database của bạn.

---

## 📖 Documentation Files

### 1. POSTMAN_QUICK_START.md

- 5-phút quick start guide
- 5 essential endpoints
- Top 10 most useful APIs
- Common issues & solutions

### 2. POSTMAN_TESTING_COMPLETE_GUIDE.md

- Chi tiết 100% endpoints
- Request/Response examples
- Test flows & scenarios
- Performance benchmarks
- Automated test scripts

---

## ✅ Pre-Test Checklist

- [ ] Server đang chạy (`python app/main.py`)
- [ ] MongoDB connected
- [ ] Import Collection vào Postman
- [ ] Import Environment vào Postman
- [ ] Select Environment từ dropdown
- [ ] Test Health Check thành công

---

## 🎓 Tips & Best Practices

### 1. Sử dụng Collection Runner

- Test hàng loạt endpoints
- Export test results
- Generate reports

### 2. Save Responses

```javascript
// Thêm vào Tests tab
pm.environment.set("product_id", pm.response.json().products[0]._id);
```

### 3. Organize Tests

- Group related requests vào folders
- Rename requests cho dễ hiểu
- Add descriptions

### 4. Monitor Performance

- Check Response Time
- Set timeout limits
- Track API health

---

## 🔍 Test Scripts Included

### Status Check

```javascript
pm.test("Status code is 200", function () {
  pm.response.to.have.status(200);
});
```

### Response Time

```javascript
pm.test("Response time < 5s", function () {
  pm.expect(pm.response.responseTime).to.be.below(5000);
});
```

### JSON Validation

```javascript
pm.test("Response is JSON", function () {
  pm.response.to.have.header("Content-Type", /application\/json/);
});
```

---

## 🐛 Troubleshooting

### Issue 1: Connection Error

**Error:** `Error: connect ECONNREFUSED`

**Fix:**

```powershell
# Kiểm tra server đang chạy
python app/main.py
```

### Issue 2: 404 Not Found

**Error:** `404 Not Found`

**Fix:**

- Kiểm tra URL path
- Đảm bảo `base_url` đúng
- Check API version

### Issue 3: Invalid ObjectID

**Error:** `Invalid ObjectId`

**Fix:**

- Lấy ID thực từ `/api/data/products`
- Update environment variables

### Issue 4: Timeout

**Error:** `Request timeout`

**Fix:**

- Tăng timeout trong Settings
- Check MongoDB connection
- Optimize query

---

## 📈 Expected Performance

| Operation            | Expected Time |
| -------------------- | ------------- |
| GET requests         | < 500ms       |
| Simple POST          | < 1000ms      |
| Analytics            | < 2000ms      |
| Segmentation         | < 3000ms      |
| Simulation (1K iter) | < 5000ms      |

---

## 🌐 Additional Resources

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Postman Learning**: https://learning.postman.com/
- **API Documentation**: Xem file `API_DOCUMENTATION.md`

---

## 🔄 Updates & Versions

### Version 2.0.0 (Current)

- ✅ 13 complete modules
- ✅ 77 endpoints
- ✅ Full CRUD operations
- ✅ Environment variables
- ✅ Test scripts
- ✅ Documentation

### Upcoming Features

- 🔜 Newman CLI integration
- 🔜 CI/CD automation
- 🔜 Mock servers
- 🔜 Performance monitoring

---

## 📞 Support

Nếu gặp vấn đề:

1. Check file `POSTMAN_TESTING_COMPLETE_GUIDE.md`
2. Xem API docs tại `/docs`
3. Review server logs
4. Test với simple endpoints trước

---

## 🎉 Happy Testing!

**Collection này cover:**

- ✅ 100% API endpoints
- ✅ All HTTP methods (GET, POST, PUT, DELETE)
- ✅ Example requests & responses
- ✅ Error handling
- ✅ Performance metrics

**Bắt đầu ngay:** Mở file `POSTMAN_QUICK_START.md` 🚀

---

**Last Updated:** December 27, 2024  
**Version:** 2.0.0  
**Author:** RCM PRICE Team
