# 🚀 QUICK START - Test API trong 5 phút

## Bước 1: Khởi động Server (30 giây)

```powershell
cd C:\Users\Lenovo\STUDY\RCM_PRICE
python .\app\main.py
```

**Chờ đến khi thấy:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Bước 2: Import Postman Collection (1 phút)

1. Mở **Postman**
2. Click **Import** (góc trên trái)
3. Chọn file: `RCM_PRICE_Complete_API_Tests.postman_collection.json`
4. Click **Import**

✅ Bạn sẽ thấy collection "RCM PRICE - Complete API Tests" với 13 folders

---

## Bước 3: Test ngay 5 endpoints cơ bản (3 phút)

### Test 1: Health Check ✅

```
Method: GET
URL: http://localhost:8000/health
```

**Click "Send"** → Expect: `"status": "healthy"`

### Test 2: Lấy danh sách Products 📦

```
Method: GET
URL: http://localhost:8000/api/data/products?limit=5
```

**Click "Send"** → Copy một `_id` từ response

### Test 3: Lấy danh sách Users 👥

```
Method: GET
URL: http://localhost:8000/api/data/users?limit=5
```

**Click "Send"** → Copy một `_id` từ response

### Test 4: Customer Segmentation 🎯

```
Method: POST
URL: http://localhost:8000/api/customer-segmentation/segment
Body (raw JSON):
{
  "min_orders_for_analysis": 1,
  "vip_threshold": 500000
}
```

**Click "Send"** → Expect: Phân loại customers thành VIP, REGULAR, etc.

### Test 5: Business Analytics 📊

```
Method: GET
URL: http://localhost:8000/api/analytics/business-health
```

**Click "Send"** → Expect: Revenue, orders, metrics

---

## 🎉 Hoàn thành!

Bạn đã test thành công 5 endpoints cơ bản. Giờ có thể:

### 📚 Tiếp tục khám phá:

- **Folder 01-04**: Basic APIs
- **Folder 05-07**: Advanced Pricing
- **Folder 08-09**: Smart Promotions
- **Folder 10-11**: ML & AI Features

### 📖 Đọc hướng dẫn chi tiết:

- File: `POSTMAN_TESTING_COMPLETE_GUIDE.md`
- Hoặc truy cập: http://localhost:8000/docs (Swagger UI)

---

## 🔥 Top 10 Most Useful Endpoints

| Rank | Endpoint                                                | What it does             |
| ---- | ------------------------------------------------------- | ------------------------ |
| 1️⃣   | `GET /api/analytics/business-health`                    | Tổng quan business       |
| 2️⃣   | `POST /api/customer-segmentation/segment`               | Phân loại khách hàng     |
| 3️⃣   | `GET /api/personalized-pricing/catalog/{user_id}`       | Giá cá nhân hóa          |
| 4️⃣   | `POST /api/pricing-simulator/find-optimal`              | Tìm giá tối ưu           |
| 5️⃣   | `POST /api/smart-promotions/generate-segment-promotion` | Tạo promotion            |
| 6️⃣   | `GET /api/event-promotions/discover-combos`             | Tìm combo sản phẩm       |
| 7️⃣   | `POST /api/price-elasticity/analyze`                    | Phân tích độ co giãn giá |
| 8️⃣   | `GET /api/hybrid/user-recommendations/{user_id}`        | Gợi ý sản phẩm           |
| 9️⃣   | `POST /api/event-promotions/generate-event-promotion`   | Promotion cho sự kiện    |
| 🔟   | `GET /api/analytics/enhanced-strategy`                  | Chiến lược tổng thể      |

---

## 💡 Pro Tips

1. **Dùng Variables**: Lưu `product_id` và `user_id` để tái sử dụng
2. **Check Response Time**: Nên < 5 giây
3. **Xem Docs**: http://localhost:8000/docs để test trực tiếp
4. **Save Collection**: Để backup configs

---

## ❓ Gặp vấn đề?

**Server không chạy?**

```powershell
# Check lại MongoDB connection
python test_connection.py
```

**Port 8000 bị chiếm?**

```powershell
# Change port trong main.py
uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Lỗi 500?**

- Check server logs
- Đảm bảo MongoDB đang chạy
- Kiểm tra GEMINI_API_KEY trong .env

---

**Ready to test! 🎯**
