# 🎯 PHÂN TÍCH HỆ THỐNG KHUYẾN MÃI HIỆN TẠI

## 📊 TỔNG QUAN 2 API CHÍNH

### **1. `/api/event-promotions/generate-event-promotion`**

🎉 **Khuyến mãi dựa trên SỰ KIỆN**

### **2. `/api/event-promotions/generate-smart-promotion`**

🧠 **Khuyến mãi THÔNG MINH không phụ thuộc sự kiện**

---

## 🔍 CHI TIẾT API 1: GENERATE EVENT PROMOTION

### **📝 Mô tả**

Tự động tạo chương trình khuyến mãi dựa trên **sự kiện sắp tới** (Tết, Halloween, Valentine, v.v.)

### **⚙️ Quy trình hoạt động**

```
┌─────────────────────────────────────────────────────┐
│  INPUT: event_type (optional), days_ahead (60)      │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  STEP 1: EVENT DETECTION                            │
│  - Phát hiện sự kiện sắp tới (EventDetector)        │
│  - Halloween, Tết, Valentine, Christmas...          │
│  - Lọc theo event_type nếu có                       │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  STEP 2: PRODUCT PERFORMANCE ANALYSIS               │
│  - Phân tích 30 ngày gần nhất                       │
│  - Tính metrics cho mỗi sản phẩm:                   │
│    • avg_monthly_sales (doanh số trung bình/tháng)  │
│    • revenue_contribution (% đóng góp doanh thu)    │
│    • total_sold (tổng đã bán)                       │
│    • stock_level (tồn kho)                          │
│    • avg_rating (đánh giá)                          │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  STEP 3: PRODUCT CLASSIFICATION                     │
│  - Phân loại sản phẩm:                              │
│    • BEST_SELLER: total_sold > 20 + revenue > 5%    │
│      → Giảm 5% (nhẹ)                                │
│    • SLOW_MOVING: total_sold < 5 + stock > 10       │
│      → Giảm 20% (mạnh - thanh lý)                   │
│    • COMBO_POTENTIAL: rating >= 4.5 + sold < 10     │
│      → Giảm 10% (vừa - kích thích)                  │
│    • NORMAL: Còn lại                                │
│      → Giảm 10% (chuẩn)                             │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  STEP 4: COMBO DISCOVERY (Market Basket Analysis)   │
│  - Apriori Algorithm                                │
│  - Tìm sản phẩm thường mua cùng nhau                │
│  - min_support = 5%, min_confidence = 30%           │
│  - Đề xuất bundle discount 15%                      │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  STEP 5: STRATEGY SELECTION                         │
│  - Nếu nhiều SLOW_MOVING (>5):                      │
│    → Strategy: CLEARANCE (thanh lý)                 │
│    → Goal: CLEARANCE                                │
│  - Nếu sự kiện lớn (TET, CHRISTMAS):                │
│    → Strategy: EVENT_SPECIAL                        │
│    → Goal: REVENUE                                  │
│  - Còn lại:                                         │
│    → Strategy: BOOST_SALES                          │
│    → Goal: VOLUME                                   │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  STEP 6: DISCOUNT CALCULATION                       │
│  - Lấy discount range từ EventDetector:             │
│    • Halloween: 15-25%                              │
│    • Tết: 20-40%                                    │
│    • Black Friday: 30-50%                           │
│  - Tính average: (min + max) / 2                    │
│  - Apply theo product classification                │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  STEP 7: TIMING OPTIMIZATION                        │
│  - suggest_promotion_timing(event):                 │
│    • Pre-event promotion (7-14 ngày trước)          │
│    • During event (1-7 ngày)                        │
│    • Total duration: 8-21 ngày                      │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  STEP 8: REVENUE IMPACT ESTIMATION                  │
│  - Formula:                                         │
│    base_impact = (discount / 10) * 5                │
│    multiplier = event_multipliers[event_type]       │
│    coverage_factor = min(num_products / 10, 1.5)    │
│    estimated = base * multiplier * coverage         │
│    net_impact = estimated - (discount * 0.5)        │
│                                                     │
│  - Event Multipliers:                               │
│    • TET: 2.5x                                      │
│    • CHRISTMAS: 2.0x                                │
│    • BLACK_FRIDAY: 3.0x                             │
│    • VALENTINE: 1.5x                                │
│    • NORMAL: 1.0x                                   │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  OUTPUT: List[PromotionRecommendation]              │
│  - promotion_id                                     │
│  - promotion_name                                   │
│  - strategy (CLEARANCE/EVENT_SPECIAL/BOOST_SALES)   │
│  - target_products (top 10-15)                      │
│  - combo_suggestions (top 5)                        │
│  - discount_value (%)                               │
│  - start_date, end_date                             │
│  - estimated_revenue_impact (%)                     │
│  - risk_level (LOW/MEDIUM/HIGH)                     │
└─────────────────────────────────────────────────────┘
```

### **🔬 Phương pháp sử dụng**

#### **1. Statistical Analysis (Phân tích thống kê)**

```python
# Tính metrics
avg_monthly_sales = (total_sold / analysis_period_days) * 30
revenue_contribution = (total_revenue_product / total_revenue) * 100

# Phân loại rule-based
if total_sold > 20 and revenue_contribution > 5:
    status = BEST_SELLER
    discount = 5%
elif total_sold < 5 and stock > 10:
    status = SLOW_MOVING
    discount = 20%
```

#### **2. Market Basket Analysis (Apriori)**

```python
from mlxtend.frequent_patterns import apriori, association_rules

# Tìm frequent itemsets
frequent_itemsets = apriori(df_encoded, min_support=0.05)

# Tạo association rules
rules = association_rules(frequent_itemsets,
                          metric="confidence",
                          min_threshold=0.3)
```

#### **3. Rule-Based Strategy Selection**

```python
if len(slow_moving) > 5:
    strategy = CLEARANCE
elif event_type in [TET, CHRISTMAS]:
    strategy = EVENT_SPECIAL
else:
    strategy = BOOST_SALES
```

#### **4. Simple Revenue Estimation**

```python
base_impact = (discount / 10) * 5
multiplier = event_multipliers[event_type]
coverage_factor = min(num_products / 10, 1.5)
net_impact = base_impact * multiplier * coverage - (discount * 0.5)
```

### **📈 Ví dụ Response**

```json
{
  "promotion_id": "abc-123",
  "promotion_name": "Khuyến Mãi Halloween (31/10)",
  "description": "Chương trình đặc biệt nhân dịp Halloween. Giảm giá 15-25%...",
  "strategy": "BOOST_SALES",
  "event_info": {
    "event_type": "Halloween (31/10)",
    "event_date": "2025-10-31",
    "days_until_event": 1,
    "recommended_discount_range": "15-25",
    "target_categories": ["Bánh Kem Halloween", "Bánh Cookie", "Kẹo"]
  },
  "target_products": [
    {
      "product_id": "671eddc4e630c82794ed8c4c",
      "product_name": "Bánh Kem Halloween Bí Ngô",
      "current_price": 150000,
      "avg_monthly_sales": 12.5,
      "total_sold": 25,
      "revenue_contribution": 8.2,
      "stock_level": 30,
      "avg_rating": 4.5,
      "status": "BEST_SELLER",
      "recommended_discount": 5,
      "reason": "Sản phẩm bán chạy, chỉ cần khuyến mãi nhẹ..."
    }
  ],
  "combo_suggestions": [
    {
      "product_1_name": "Bánh Kem Halloween",
      "product_2_name": "Kẹo Halloween Mix",
      "frequency_together": 15,
      "confidence": 0.65,
      "recommended_bundle_discount": 15
    }
  ],
  "discount_value": 20,
  "start_date": "2025-10-24",
  "end_date": "2025-10-31",
  "duration_days": 8,
  "estimated_revenue_impact": 12.5,
  "risk_level": "MEDIUM"
}
```

---

## 🔍 CHI TIẾT API 2: GENERATE SMART PROMOTION

### **📝 Mô tả**

Tạo khuyến mãi thông minh **không phụ thuộc sự kiện**, dựa trên mục tiêu kinh doanh

### **⚙️ 3 Chiến lược**

#### **1. REVENUE Focus** (`focus=revenue`)

```python
# Mục tiêu: Tối đa hóa doanh thu
target_products = [p for p in all if p.revenue_contribution > 3]
discount = 15%  # Giảm vừa
goal = "REVENUE"
```

#### **2. CLEARANCE Focus** (`focus=clearance`)

```python
# Mục tiêu: Thanh lý tồn kho
target_products = [p for p in all if p.status == SLOW_MOVING]
discount = 20%  # Giảm mạnh
goal = "CLEARANCE"
```

#### **3. BALANCED** (`focus=balanced`)

```python
# Mục tiêu: Cân bằng
target_products = all_products[:15]  # Mix tất cả
discount = 12%  # Giảm vừa phải
goal = "VOLUME"
```

### **📈 Quy trình**

```
INPUT: focus (revenue/clearance/balanced)
  ↓
Product Analysis (giống API 1)
  ↓
Filter theo focus:
  - revenue: revenue_contribution > 3%
  - clearance: status = SLOW_MOVING
  - balanced: all products
  ↓
Set discount theo focus:
  - revenue: 15%
  - clearance: 20%
  - balanced: 12%
  ↓
Combo Discovery
  ↓
Revenue Estimation (đơn giản hơn - không có event multiplier)
  ↓
OUTPUT: PromotionRecommendation
```

---

## ⚠️ HẠN CHẾ HIỆN TẠI

### **1. ❌ Discount % là HARD-CODED (Rule-based)**

```python
# BEST_SELLER → 5%
# SLOW_MOVING → 20%
# NORMAL → 10%
```

**Vấn đề:**

- Không tối ưu doanh thu
- Không học từ kết quả thực tế
- Không cá nhân hóa theo từng sản phẩm

### **2. ❌ Revenue Estimation quá ĐƠN GIẢN**

```python
estimated_impact = (discount / 10) * 5 * multiplier * coverage - (discount * 0.5)
```

**Vấn đề:**

- Công thức linear đơn giản
- Không học từ historical data
- Không xem xét price elasticity thực tế

### **3. ❌ Không có LEARNING MECHANISM**

**Vấn đề:**

- Chạy promotion → Không ghi nhận kết quả
- Không cải thiện theo thời gian
- Mỗi lần chạy đều giống nhau

### **4. ❌ Strategy Selection là RULE-BASED**

```python
if len(slow_moving) > 5:
    strategy = CLEARANCE
elif event_type in [TET, CHRISTMAS]:
    strategy = EVENT_SPECIAL
```

**Vấn đề:**

- Không flexible
- Không học cái nào hiệu quả nhất

---

## 💡 ĐỀ XUẤT CÁI THIỆN

### **🎯 Mục tiêu: Tối ưu DOANH THU cho Event Promotion**

### **✅ Solution: HYBRID AI OPTIMIZER**

```
┌─────────────────────────────────────────────────────┐
│  CURRENT: generate-event-promotion                  │
│  - Event Detection ✅                               │
│  - Product Analysis ✅                              │
│  - Combo Discovery ✅                               │
│  - DISCOUNT = Rule-based ❌                         │
│  - Revenue Estimation = Simple formula ❌           │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  IMPROVED: AI-Powered Discount Optimization         │
│  - Keep: Event Detection, Product Analysis, Combo   │
│  - ADD: Thompson Sampling + Gemini API              │
│    • Thompson: Tự học discount tối ưu               │
│    • Gemini: Cold start khi chưa có data            │
│  - ADD: Real revenue prediction                     │
│  - ADD: Learning from results                       │
└─────────────────────────────────────────────────────┘
```

### **🔧 Implementation Plan**

#### **Phase 1: Thêm AI Optimizer vào Event Promotion** ⭐

```python
# File: application/services/event_promotion_service.py

from application.services.discount_optimizer import get_discount_optimizer

async def generate_event_promotion(self, event_type, days_ahead):
    # KEEP: Steps 1-4 (Event Detection, Product Analysis, Combo)
    events = self.event_detector.get_upcoming_events(...)
    products = await self.analyze_product_performance()
    combos = await self.discover_product_combos()

    # NEW: Optimize discount với AI
    optimizer = get_discount_optimizer()

    for product in products:
        # Thay vì hard-coded 5%, 10%, 20%
        # Dùng AI để tìm discount tối ưu
        result = optimizer.get_optimal_discount(
            product_id=product.product_id,
            product_name=product.product_name,
            base_price=product.current_price,
            event_type=event.event_type.name,
            current_stock=product.stock_level,
            avg_rating=product.avg_rating,
            days_to_event=event.days_until_event
        )

        # Update discount từ AI
        product.recommended_discount = result['discount_percent']
        product.reason = result['reason']

    # KEEP: Strategy selection, timing, output
    ...
```

#### **Phase 2: Track Results & Learn**

```python
# Thêm endpoint mới
@router.post("/track-promotion-result")
async def track_promotion_result(
    promotion_id: str,
    actual_revenue: float,
    target_revenue: float
):
    """Ghi nhận kết quả promotion để AI học"""
    optimizer = get_discount_optimizer()

    # Lấy thông tin promotion
    promotion = get_promotion_by_id(promotion_id)

    # Update Thompson Sampling với kết quả
    for product in promotion.target_products:
        optimizer.record_result(
            product_id=product.product_id,
            event_type=promotion.event_info.event_type.name,
            discount_used=product.recommended_discount,
            revenue=actual_revenue,
            target_revenue=target_revenue
        )
```

### **📊 So sánh BEFORE/AFTER**

| Tính năng                | CURRENT                   | WITH AI OPTIMIZER              |
| ------------------------ | ------------------------- | ------------------------------ |
| **Discount Selection**   | Rule-based (5%, 10%, 20%) | AI-optimized (học từ data)     |
| **Revenue Optimization** | Simple formula            | Price elasticity + Learning    |
| **Cold Start**           | Hard-coded rules          | Gemini API                     |
| **Learning**             | ❌ Không                  | ✅ Tự học từ kết quả           |
| **Personalization**      | ❌ Không                  | ✅ Mỗi product khác nhau       |
| **Confidence Score**     | ❌ Không                  | ✅ Có (0.0-1.0)                |
| **CPU Usage**            | Low                       | Low (Thompson < 1ms)           |
| **Deploy Render**        | ✅ OK                     | ✅ OK                          |
| **Need Training Data**   | ❌ Không                  | ❌ Không (cold start = Gemini) |

---

## 🚀 NEXT STEPS

### **Option 1: Giữ nguyên (không thay đổi)** ❌

- Pro: Không cần làm gì
- Con: Discount không tối ưu, không học được

### **Option 2: Implement AI Optimizer** ⭐ **RECOMMENDED**

- Pro:
  - Tối ưu doanh thu tự động
  - Tự học và cải thiện
  - Lightweight, deploy Render OK
  - Dùng Gemini API có sẵn
- Con:
  - Cần viết thêm code (~300 lines)
  - Cần test

### **Công việc cần làm:**

1. ✅ Tạo `application/services/discount_optimizer.py` (~300 lines)
2. ✅ Update `event_promotion_service.py` (~50 lines thay đổi)
3. ✅ Thêm 2 endpoints mới vào `event_promotions.py`
4. ✅ Test với Postman
5. ✅ Deploy lên Render

**Thời gian:** 2-3 giờ implementation + 1 giờ testing

---

## ❓ BẠN MUỐN GÌ?

1. **Giữ nguyên hệ thống hiện tại** (rule-based)?
2. **Implement AI Optimizer** vào `generate-event-promotion`?
3. **Tạo API mới** riêng cho AI optimization?

Bạn chọn cái nào? 🤔
