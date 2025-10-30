# 🎯 Event-Based Smart Promotion System

## Tổng Quan

Flow mới này tạo ra một hệ thống **tự động phân tích và tạo khuyến mãi** dựa trên:

1. **📊 Phân tích sản phẩm**: Xác định sản phẩm bán chạy/chậm
2. **🎉 Phát hiện sự kiện**: Tự động nhận diện các ngày lễ, sự kiện đặc biệt
3. **🔗 Gợi ý combo**: Phát hiện sản phẩm nào thường được mua cùng nhau
4. **💡 Tạo khuyến mãi**: Tự động đề xuất chương trình khuyến mãi tối ưu

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────┐
│           Event-Based Promotion System                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌───────────────┐    ┌──────────┐│
│  │   MongoDB    │───>│  Service      │───>│  API     ││
│  │   Database   │    │  Layer        │    │  Router  ││
│  └──────────────┘    └───────────────┘    └──────────┘│
│        ▲                     │                   ▲      │
│        │              ┌──────┴──────┐           │      │
│        │              │             │           │      │
│  ┌─────┴──────┐ ┌────▼─────┐ ┌────▼────┐ ┌────┴────┐│
│  │  Products  │ │ Product  │ │ Event   │ │FastAPI  ││
│  │  Orders    │ │ Analyzer │ │Detector │ │Endpoints││
│  │  Users     │ └──────────┘ └─────────┘ └─────────┘│
│  └────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Cấu Trúc File

### 1. Domain Layer

**File**: `domain/entities/event_promotion.py`

Định nghĩa các entity cốt lõi:

- `EventType`: Loại sự kiện (Tết, Giáng Sinh, Valentine, v.v.)
- `ProductStatus`: Trạng thái sản phẩm (BEST_SELLER, SLOW_MOVING, v.v.)
- `PromotionStrategy`: Chiến lược khuyến mãi
- `ProductAnalysis`: Kết quả phân tích sản phẩm
- `ComboSuggestion`: Gợi ý combo
- `EventInfo`: Thông tin sự kiện
- `PromotionRecommendation`: Đề xuất khuyến mãi hoàn chỉnh

### 2. Utils Layer

**File**: `utils/event_detector.py`

Event Detector - Phát hiện sự kiện:

- Tự động phát hiện ngày lễ, sự kiện đặc biệt
- Hỗ trợ cả lịch Dương và lịch Âm
- Đề xuất thời gian bắt đầu khuyến mãi tối ưu
- Đề xuất mức giảm giá phù hợp với từng sự kiện

**Sự kiện được hỗ trợ:**

- Tết Nguyên Đán (lịch Âm)
- Ngày Phụ Nữ (8/3, 20/10)
- Valentine (14/2)
- Ngày của Mẹ/Bố
- Trung Thu (lịch Âm)
- Giáng Sinh (25/12)
- Năm Mới (1/1)
- Cuối tuần
- Black Friday (có thể thêm)

### 3. Service Layer

**File**: `application/services/event_promotion_service.py`

Core Service với các chức năng:

#### a) `analyze_product_performance()`

Phân tích hiệu suất sản phẩm trong khoảng thời gian cho trước:

- Tính doanh số trung bình hàng tháng
- % đóng góp vào tổng doanh thu
- Tồn kho hiện tại
- Phân loại: BEST_SELLER / SLOW_MOVING / NORMAL
- Đề xuất mức giảm giá phù hợp

**Logic phân loại:**

```
- Bán chạy (>20 đơn + revenue >5%): Giảm 5% (giữ momentum)
- Bán chậm + tồn kho cao: Giảm 20% (thanh lý)
- Bán chậm + tồn kho thấp: Giảm 15% (đẩy mạnh)
- Rating cao nhưng bán ít: Giảm 10% (tiềm năng combo)
- Bình thường: Giảm 10%
```

#### b) `discover_product_combos()`

Sử dụng **Market Basket Analysis** (Apriori Algorithm) để tìm combo:

- Phân tích lịch sử mua hàng
- Tìm sản phẩm thường được mua cùng nhau
- Tính độ tin cậy (confidence)
- Đề xuất mức giảm giá combo (10-20%)

#### c) `generate_event_promotion()`

Tạo khuyến mãi dựa trên sự kiện sắp tới:

- Phát hiện sự kiện trong N ngày tới
- Lọc sản phẩm phù hợp
- Tạo chiến lược khuyến mãi
- Dự đoán tác động doanh thu
- Đánh giá rủi ro

#### d) `generate_smart_promotion()`

Tạo khuyến mãi thông minh không phụ thuộc sự kiện:

- **Revenue Focus**: Tối đa hóa doanh thu
- **Clearance Focus**: Thanh lý tồn kho
- **Balanced**: Cân bằng cả hai

### 4. API Router

**File**: `app/routers/event_promotions.py`

RESTful API endpoints (xem chi tiết ở phần API Documentation)

---

## 🚀 Cách Sử Dụng

### 1. Khởi động server

```bash
cd c:\Users\Lenovo\STUDY\RCM_PRICE
python run_api.py
```

Server sẽ chạy tại: `http://localhost:8000`

### 2. Truy cập API Documentation

Mở trình duyệt: `http://localhost:8000/docs`

### 3. Các API Endpoints

#### 📊 Phân tích sản phẩm

```http
GET /api/event-promotions/analyze-products?analysis_period_days=30
```

**Kết quả:**

```json
[
  {
    "product_id": "67643c2411d943b7bdecb7d3",
    "product_name": "Bánh Kem Socola",
    "current_price": 250000,
    "avg_monthly_sales": 12.5,
    "total_sold": 15,
    "revenue_contribution": 8.2,
    "stock_level": 20,
    "avg_rating": 4.8,
    "status": "BEST_SELLER",
    "recommended_discount": 5.0,
    "reason": "Sản phẩm bán chạy, chỉ cần khuyến mãi nhẹ để duy trì momentum"
  }
]
```

#### 🔗 Phát hiện combo

```http
GET /api/event-promotions/discover-combos
```

**Kết quả:**

```json
[
  {
    "product_1_id": "abc123",
    "product_1_name": "Bánh Mì",
    "product_1_price": 25000,
    "product_2_id": "def456",
    "product_2_name": "Cà Phê Sữa",
    "product_2_price": 30000,
    "frequency_together": 45,
    "confidence": 0.67,
    "recommended_bundle_discount": 15.5
  }
]
```

#### 🎉 Xem sự kiện sắp tới

```http
GET /api/event-promotions/upcoming-events?days_ahead=60
```

**Kết quả:**

```json
[
  {
    "event_type": "Tết Nguyên Đán",
    "event_date": "2025-01-29T00:00:00",
    "days_until_event": 92,
    "is_active": false,
    "duration_days": 7,
    "recommended_discount_range": "15-30",
    "target_categories": ["Bánh Tết", "Bánh Kẹo", "Quà Tặng"]
  }
]
```

#### 💡 Tạo khuyến mãi cho sự kiện

```http
POST /api/event-promotions/generate-event-promotion?days_ahead=60
```

**Hoặc cho sự kiện cụ thể:**

```http
POST /api/event-promotions/generate-event-promotion?event_type=Giáng Sinh
```

**Kết quả:**

```json
[
  {
    "promotion_id": "uuid-xxx-xxx",
    "promotion_name": "Khuyến Mãi Giáng Sinh",
    "description": "Chương trình đặc biệt nhân dịp Giáng Sinh. Giảm giá 15-30% cho các sản phẩm được chọn.",
    "strategy": "EVENT_SPECIAL",
    "event_info": {...},
    "target_products": [...],
    "combo_suggestions": [...],
    "discount_type": "PERCENTAGE",
    "discount_value": 22.5,
    "start_date": "2025-12-15T00:00:00",
    "end_date": "2025-12-28T00:00:00",
    "duration_days": 13,
    "estimated_revenue_impact": 15.8,
    "estimated_order_increase": 37,
    "risk_level": "MEDIUM",
    "primary_goal": "REVENUE"
  }
]
```

#### 🧠 Tạo khuyến mãi thông minh

```http
POST /api/event-promotions/generate-smart-promotion?focus=balanced
```

**Tùy chọn focus:**

- `revenue`: Tối đa hóa doanh thu
- `clearance`: Thanh lý tồn kho
- `balanced`: Cân bằng

---

## 🎯 Use Cases

### Use Case 1: Chuẩn Bị Cho Tết

**Tình huống:** Tết còn 30 ngày, cần chuẩn bị khuyến mãi

**Bước thực hiện:**

1. Gọi API phát hiện sự kiện:

   ```
   GET /api/event-promotions/upcoming-events?days_ahead=60
   ```

2. Phân tích sản phẩm:

   ```
   GET /api/event-promotions/analyze-products?analysis_period_days=30
   ```

3. Tạo khuyến mãi Tết:
   ```
   POST /api/event-promotions/generate-event-promotion?event_type=Tết Nguyên Đán
   ```

**Kết quả:**

- Chương trình khuyến mãi đầy đủ
- Danh sách sản phẩm được chọn
- Mức giảm giá hợp lý (15-30%)
- Thời gian: Bắt đầu 14 ngày trước Tết
- Dự đoán tăng doanh thu 25-40%

### Use Case 2: Thanh Lý Hàng Tồn

**Tình huống:** Có nhiều sản phẩm bán chậm, cần thanh lý

**Bước thực hiện:**

1. Phân tích để tìm sản phẩm bán chậm:

   ```
   GET /api/event-promotions/analyze-products
   ```

2. Tạo promotion thanh lý:
   ```
   POST /api/event-promotions/generate-smart-promotion?focus=clearance
   ```

**Kết quả:**

- Tập trung vào sản phẩm SLOW_MOVING
- Giảm giá mạnh (20%)
- Không giới hạn giá trị đơn hàng
- Kéo dài 7 ngày

### Use Case 3: Tăng Doanh Thu Cuối Tuần

**Tình huống:** Muốn tăng doanh thu vào cuối tuần

**Bước thực hiện:**

1. Phát hiện combo tiềm năng:

   ```
   GET /api/event-promotions/discover-combos
   ```

2. Tạo promotion cuối tuần:
   ```
   POST /api/event-promotions/generate-event-promotion
   ```
   (Sẽ tự động phát hiện cuối tuần sắp tới)

**Kết quả:**

- Combo deals hấp dẫn
- Giảm 10-15% cho combo
- Thời gian: Thứ 6-7-CN
- Tăng giá trị đơn hàng trung bình

---

## 🧪 Testing

### Test với Postman

Import collection từ file: `AI_Promotion_API.postman_collection.json`

Hoặc test thủ công:

```bash
# 1. Kiểm tra health
curl http://localhost:8000/api/event-promotions/health

# 2. Phân tích sản phẩm
curl http://localhost:8000/api/event-promotions/analyze-products

# 3. Tìm combo
curl http://localhost:8000/api/event-promotions/discover-combos

# 4. Xem sự kiện
curl http://localhost:8000/api/event-promotions/upcoming-events

# 5. Tạo promotion
curl -X POST http://localhost:8000/api/event-promotions/generate-smart-promotion?focus=balanced
```

---

## 📊 Data Flow

```
1. MongoDB Orders/Products Data
         ↓
2. EventPromotionService.analyze_product_performance()
         ↓
3. Phân loại sản phẩm (BEST_SELLER, SLOW_MOVING, etc.)
         ↓
4. EventDetector.get_upcoming_events()
         ↓
5. Match sản phẩm với sự kiện
         ↓
6. discover_product_combos() (Market Basket Analysis)
         ↓
7. Tính toán discount tối ưu
         ↓
8. Dự đoán impact (revenue, orders)
         ↓
9. Return PromotionRecommendation
         ↓
10. API Response (JSON)
```

---

## 🔧 Tùy Chỉnh

### Thêm sự kiện mới

Chỉnh sửa `utils/event_detector.py`:

```python
FIXED_EVENTS = {
    EventType.YOUR_EVENT: {
        "month": 11,
        "day": 11,
        "duration": 3
    },
}

EVENT_DISCOUNT_RANGES = {
    EventType.YOUR_EVENT: "20-30",
}
```

### Điều chỉnh logic phân tích sản phẩm

Chỉnh sửa `application/services/event_promotion_service.py`:

```python
def _classify_product(self, ...):
    # Thay đổi ngưỡng theo nhu cầu
    if total_sold > 30:  # Thay vì 20
        return (ProductStatus.BEST_SELLER, 5.0, "...")
```

---

## 🎨 Tích Hợp Frontend

### React Example

```javascript
import axios from "axios";

// 1. Lấy phân tích sản phẩm
const analyzeProducts = async () => {
  const response = await axios.get(
    "http://localhost:8000/api/event-promotions/analyze-products"
  );
  return response.data;
};

// 2. Tạo khuyến mãi thông minh
const createPromotion = async (focus = "balanced") => {
  const response = await axios.post(
    `http://localhost:8000/api/event-promotions/generate-smart-promotion?focus=${focus}`
  );
  return response.data;
};

// 3. Hiển thị sự kiện sắp tới
const UpcomingEvents = () => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/event-promotions/upcoming-events")
      .then((res) => setEvents(res.data));
  }, []);

  return (
    <div>
      {events.map((event) => (
        <div key={event.event_type}>
          <h3>{event.event_type}</h3>
          <p>Còn {event.days_until_event} ngày</p>
          <p>Giảm giá đề xuất: {event.recommended_discount_range}%</p>
        </div>
      ))}
    </div>
  );
};
```

---

## 📈 Metrics & KPIs

Hệ thống đề xuất các metrics quan trọng:

1. **Product Performance**

   - Avg Monthly Sales
   - Revenue Contribution %
   - Stock Level

2. **Combo Analysis**

   - Confidence Score
   - Frequency Together
   - Bundle Discount

3. **Promotion Impact**
   - Estimated Revenue Impact %
   - Estimated Order Increase
   - Risk Level

---

## 🔐 Bảo Mật

- API không yêu cầu authentication (có thể thêm sau)
- CORS được enable cho development
- Data validation với Pydantic
- Error handling đầy đủ

---

## 🚧 Roadmap

### Phase 1 (Done)

- ✅ Product analysis
- ✅ Event detection
- ✅ Combo discovery
- ✅ Auto promotion generation

### Phase 2 (Future)

- [ ] Tích hợp với Gemini AI để tạo mô tả promotion
- [ ] A/B testing promotions
- [ ] Real-time promotion performance tracking
- [ ] Customer segment integration
- [ ] Email/notification automation
- [ ] Promotion calendar view

---

## 📚 Dependencies

```
pandas>=1.5.0
numpy>=1.24.0
mlxtend>=0.22.0  # Market Basket Analysis
fastapi>=0.104.0
pydantic>=2.0.0
```

---

## 🤝 Đóng Góp

Flow này được thiết kế để dễ mở rộng. Bạn có thể:

1. Thêm sự kiện mới
2. Tùy chỉnh logic phân tích
3. Thêm chiến lược khuyến mãi mới
4. Tích hợp AI models khác

---

## 📞 Support

Nếu có vấn đề, hãy kiểm tra:

1. Server đang chạy: `http://localhost:8000/docs`
2. MongoDB connection
3. Dependencies đã cài đủ
4. Log errors trong terminal

---

## 🎉 Kết Luận

Event-Based Smart Promotion System giúp:

✅ **Tự động hóa** việc tạo khuyến mãi  
✅ **Tối ưu** doanh thu và lợi nhuận  
✅ **Phát hiện** cơ hội kinh doanh  
✅ **Giảm thiểu** rủi ro  
✅ **Tiết kiệm** thời gian quản lý

**Perfect for:** Website bánh ngọt với 2 loại khách hàng (guest + registered users)
