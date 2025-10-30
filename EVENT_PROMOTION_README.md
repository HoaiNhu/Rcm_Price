# 🎯 Event-Based Smart Promotion System - Quick Start

## Tính Năng Mới

Hệ thống **tự động phân tích và tạo khuyến mãi** cho website bánh ngọt dựa trên:

✅ **Phân tích sản phẩm**: Tự động xác định sản phẩm bán chạy/chậm  
✅ **Phát hiện sự kiện**: Nhận diện Tết, Giáng Sinh, Valentine, v.v.  
✅ **Gợi ý combo**: AI tìm sản phẩm thường mua cùng nhau  
✅ **Tạo khuyến mãi**: Tự động đề xuất chương trình phù hợp

---

## 🚀 Khởi Động Nhanh

### 1. Cài đặt dependencies

```bash
pip install mlxtend pandas numpy
```

### 2. Khởi động server

```bash
cd RCM_PRICE
python run_api.py
```

### 3. Test thử

```bash
python test_event_promotions.py
```

### 4. Xem API docs

Mở trình duyệt: `http://localhost:8000/docs`

---

## 📡 API Endpoints

### 1. Phân tích sản phẩm

```http
GET /api/event-promotions/analyze-products?analysis_period_days=30
```

**Kết quả**: Danh sách sản phẩm với trạng thái (BEST_SELLER/SLOW_MOVING) và mức giảm giá đề xuất

### 2. Phát hiện combo

```http
GET /api/event-promotions/discover-combos
```

**Kết quả**: Các cặp sản phẩm thường được mua cùng nhau + discount đề xuất

### 3. Xem sự kiện sắp tới

```http
GET /api/event-promotions/upcoming-events?days_ahead=60
```

**Kết quả**: Danh sách sự kiện (Tết, Giáng Sinh, v.v.) và thông tin chi tiết

### 4. Tạo khuyến mãi cho sự kiện

```http
POST /api/event-promotions/generate-event-promotion?days_ahead=60
```

**Kết quả**: Chương trình khuyến mãi hoàn chỉnh với:

- Sản phẩm được chọn
- Mức giảm giá tối ưu
- Thời gian bắt đầu/kết thúc
- Dự đoán tác động doanh thu

### 5. Tạo khuyến mãi thông minh

```http
POST /api/event-promotions/generate-smart-promotion?focus=balanced
```

**Focus options:**

- `revenue`: Tối đa hóa doanh thu
- `clearance`: Thanh lý tồn kho
- `balanced`: Cân bằng

---

## 💡 Ví Dụ Sử Dụng

### Scenario 1: Chuẩn bị Tết

```bash
# 1. Xem Tết còn bao nhiêu ngày
curl http://localhost:8000/api/event-promotions/upcoming-events

# 2. Tạo chương trình khuyến mãi Tết
curl -X POST "http://localhost:8000/api/event-promotions/generate-event-promotion?event_type=Tết Nguyên Đán"
```

### Scenario 2: Thanh lý hàng tồn

```bash
# 1. Phân tích sản phẩm bán chậm
curl http://localhost:8000/api/event-promotions/analyze-products

# 2. Tạo promotion thanh lý
curl -X POST "http://localhost:8000/api/event-promotions/generate-smart-promotion?focus=clearance"
```

### Scenario 3: Tăng doanh thu cuối tuần

```bash
# 1. Tìm combo tiềm năng
curl http://localhost:8000/api/event-promotions/discover-combos

# 2. Tạo promotion cuối tuần
curl -X POST http://localhost:8000/api/event-promotions/generate-event-promotion
```

---

## 📁 Files Mới

```
RCM_PRICE/
├── domain/
│   └── entities/
│       └── event_promotion.py          # Domain entities
├── utils/
│   └── event_detector.py               # Event detection
├── application/
│   └── services/
│       └── event_promotion_service.py  # Core service
├── app/
│   └── routers/
│       └── event_promotions.py         # API router
├── test_event_promotions.py            # Test suite
└── EVENT_PROMOTION_GUIDE.md            # Chi tiết đầy đủ
```

---

## 🎨 Tích Hợp Frontend

### React Example

```javascript
import axios from "axios";

// Lấy khuyến mãi thông minh
const createPromotion = async () => {
  const response = await axios.post(
    "http://localhost:8000/api/event-promotions/generate-smart-promotion?focus=balanced"
  );

  const promo = response.data;
  console.log(`Khuyến mãi: ${promo.promotion_name}`);
  console.log(`Giảm giá: ${promo.discount_value}%`);
  console.log(`Sản phẩm: ${promo.target_products.length}`);
};
```

---

## 🧪 Testing

Chạy test suite:

```bash
python test_event_promotions.py
```

Test sẽ kiểm tra:

- ✅ Phân tích sản phẩm
- ✅ Phát hiện combo
- ✅ Phát hiện sự kiện
- ✅ Tạo khuyến mãi sự kiện
- ✅ Tạo khuyến mãi thông minh

---

## 📖 Documentation

Chi tiết đầy đủ: [EVENT_PROMOTION_GUIDE.md](./EVENT_PROMOTION_GUIDE.md)

Bao gồm:

- Architecture
- Data flow
- API documentation
- Use cases
- Customization guide
- Frontend integration

---

## 🎯 Lợi Ích

### So với cách thủ công:

❌ **Trước:** Tạo khuyến mãi thủ công, không biết sản phẩm nào cần đẩy  
✅ **Bây giờ:** AI tự động phân tích và đề xuất

❌ **Trước:** Đoán mức giảm giá, có thể lỗ hoặc không hiệu quả  
✅ **Bây giờ:** AI tính toán mức giảm giá tối ưu, dự đoán impact

❌ **Trước:** Quên các sự kiện quan trọng  
✅ **Bây giờ:** Hệ thống tự động nhắc và tạo promotion trước sự kiện

❌ **Trước:** Không biết sản phẩm nào đi combo với nhau  
✅ **Bây giờ:** AI phân tích lịch sử mua hàng và gợi ý combo

---

## 🔧 Tùy Chỉnh

### Thêm sự kiện mới

Chỉnh sửa `utils/event_detector.py`:

```python
FIXED_EVENTS = {
    EventType.YOUR_EVENT: {"month": 11, "day": 11, "duration": 3},
}
```

### Điều chỉnh mức giảm giá

Chỉnh sửa `application/services/event_promotion_service.py`:

```python
def _classify_product(self, ...):
    if total_sold > 20:
        return (ProductStatus.BEST_SELLER, 5.0, "...")  # Thay đổi 5.0
```

---

## 🤝 Support

**API Docs:** `http://localhost:8000/docs`  
**Full Guide:** [EVENT_PROMOTION_GUIDE.md](./EVENT_PROMOTION_GUIDE.md)  
**Test:** `python test_event_promotions.py`

---

## ✨ Tóm Tắt

Flow mới này giúp:

1. **Tự động** phân tích sản phẩm bán chạy/chậm
2. **Phát hiện** sự kiện đặc biệt sắp tới
3. **Gợi ý** combo sản phẩm dựa trên AI
4. **Tạo** chương trình khuyến mãi tối ưu
5. **Dự đoán** tác động doanh thu

**Perfect for:** Website chỉ có 2 loại khách (guest + registered)  
**No need for:** Phân khúc khách hàng phức tạp  
**AI-powered:** Market Basket Analysis + Event Detection + Smart Recommendations
