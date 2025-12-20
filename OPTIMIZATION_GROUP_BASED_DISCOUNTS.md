# 🚀 Tối Ưu API Event Promotions - Group-Based Discounts

## 📊 Vấn Đề Trước Đây

### ❌ Chậm và Không Hiệu Quả

```python
# Vòng lặp chậm - mỗi sản phẩm = 1 request Gemini AI
for product in focus_products:  # 15 sản phẩm
    optimization_result = optimizer.get_optimal_discount(
        product_id=product.product_id,
        product_name=product.product_name,
        ...  # Gọi Gemini API
    )
    # 2-3 giây/request × 15 = 30-45 giây!
```

### 🐌 Hậu Quả

- **Thời gian xử lý**: 30-45 giây cho 15 sản phẩm
- **Chi phí API**: 15 requests × $0.001 = tốn kém
- **Khó quản lý**: Admin phải theo dõi 15 mức giảm giá khác nhau
- **Không thực tế**: Tiệm bánh thường có discount chung cho nhóm SP

---

## ✅ Giải Pháp Mới - Group-Based Optimization

### 🎯 Chiến Lược Nhóm Sản Phẩm

```
🏆 Nhóm 1: BEST_SELLER (Bán Chạy)
   ├─ Discount: 10-15%
   ├─ Mục tiêu: Tăng traffic, giữ momentum
   └─ VD: Bánh kem dâu, Bánh flan

🐌 Nhóm 2: SLOW_MOVING (Bán Chậm)
   ├─ Discount: 20-30%
   ├─ Mục tiêu: Thanh lý, tăng doanh số
   └─ VD: Bánh tart, Bánh quy

⭐ Nhóm 3: COMBO_POTENTIAL (Tiềm Năng)
   ├─ Discount: 15-20%
   ├─ Mục tiêu: Cross-sell, tăng giá trị đơn
   └─ VD: Bánh mì, Sữa chua

📦 Nhóm 4: NORMAL (Bình Thường)
   ├─ Discount: 15%
   ├─ Mục tiêu: Duy trì ổn định
   └─ VD: Các sản phẩm khác
```

### 🚀 Cải Thiện Hiệu Suất

| Metric        | Trước       | Sau          | Cải thiện  |
| ------------- | ----------- | ------------ | ---------- |
| **API Calls** | 15 lần      | 3-4 lần      | **-75%**   |
| **Thời gian** | 30-45s      | 6-12s        | **-75%**   |
| **Chi phí**   | 15 requests | 3-4 requests | **-75%**   |
| **Quản lý**   | 15 mức giá  | 3-4 mức giá  | **Dễ hơn** |

---

## 🔧 Implementation Details

### Thay Đổi Trong Code

**File**: `application/services/event_promotion_service.py`

```python
# 🚀 OPTIMIZED: Nhóm sản phẩm theo ProductStatus
product_groups = {
    ProductStatus.BEST_SELLER: [],
    ProductStatus.SLOW_MOVING: [],
    ProductStatus.NORMAL: [],
    ProductStatus.COMBO_POTENTIAL: []
}

# Phân nhóm
for product in focus_products:
    product_groups[product.status].append(product)

# Gọi AI cho từng NHÓM thay vì từng SẢN PHẨM
for status, products_in_group in product_groups.items():
    if not products_in_group:
        continue

    # Lấy sản phẩm đại diện
    representative = max(products_in_group, key=lambda p: p.revenue_contribution)

    # Gọi AI cho cả nhóm
    optimization_result = optimizer.get_optimal_discount(
        product_id=f"GROUP_{status.value}",  # Group ID
        product_name=f"Nhóm {status.value}",
        base_price=representative.current_price,
        historical_sales=sum(p.total_sold for p in products_in_group),
        ...
    )

    # Áp dụng cho tất cả sản phẩm trong nhóm
    for product in products_in_group:
        product.recommended_discount = group_discount
```

---

## 📝 API Response Example

### Trước (Mỗi Sản Phẩm 1 Discount)

```json
{
  "promotion_name": "Khuyến Mãi Tết",
  "target_products": [
    { "product_name": "Bánh kem dâu", "recommended_discount": 12.3 },
    { "product_name": "Bánh flan", "recommended_discount": 11.7 },
    { "product_name": "Bánh tart", "recommended_discount": 23.8 },
    { "product_name": "Bánh quy", "recommended_discount": 25.1 }
    // ... 11 sản phẩm nữa với 11 mức giảm giá khác nhau
  ]
}
```

### Sau (Nhóm Sản Phẩm)

```json
{
  "promotion_name": "Khuyến Mãi Tết - AI Optimized",
  "description": "💰 Chiết khấu theo nhóm:\n   • 10%: 5 sản phẩm bán chạy\n   • 25%: 4 sản phẩm bán chậm\n   • 15%: 6 sản phẩm tiềm năng",
  "target_products": [
    {
      "product_name": "Bánh kem dâu",
      "recommended_discount": 10,
      "reason": "Nhóm BEST_SELLER: 10%"
    },
    {
      "product_name": "Bánh flan",
      "recommended_discount": 10,
      "reason": "Nhóm BEST_SELLER: 10%"
    },
    {
      "product_name": "Bánh tart",
      "recommended_discount": 25,
      "reason": "Nhóm SLOW_MOVING: 25%"
    },
    {
      "product_name": "Bánh quy",
      "recommended_discount": 25,
      "reason": "Nhóm SLOW_MOVING: 25%"
    }
    // ... sản phẩm khác với 3-4 mức giảm giá rõ ràng
  ]
}
```

---

## 🧪 Testing

### Test Nhanh

```bash
# 1. Test import
python -c "from application.services.event_promotion_service import get_event_promotion_service; print('✅ OK')"

# 2. Test API
curl "http://localhost:8000/api/event-promotions/generate-event-promotion?days_ahead=30"
```

### Kiểm Tra Log

```
🎯 Grouping 15 products by status for batch AI optimization
  📊 BEST_SELLER: 5 products → 10% (method: thompson_sampling, confidence: 0.85)
  📊 SLOW_MOVING: 4 products → 25% (method: gemini_ai, confidence: 0.65)
  📊 COMBO_POTENTIAL: 6 products → 15% (method: hybrid, confidence: 0.75)
  🎁 Average discount: 15.7% across 3 groups, 15 products
```

---

## 📈 Benefits

### Cho Developer

- ✅ Code đơn giản hơn, dễ maintain
- ✅ Giảm số lần gọi API (tiết kiệm chi phí)
- ✅ Tăng tốc độ xử lý (user experience tốt hơn)

### Cho Business

- ✅ Dễ quản lý: Chỉ 3-4 mức giảm giá
- ✅ Thực tế hơn: Tiệm bánh thường có discount theo nhóm
- ✅ Linh hoạt: Có thể adjust mỗi nhóm độc lập

### Cho User

- ✅ Phản hồi nhanh (6-12s thay vì 30-45s)
- ✅ Dễ hiểu: "Bánh bán chạy giảm 10%, bánh bán chậm giảm 25%"

---

## 🔮 Future Improvements

1. **Cache Group Discounts**: Cache kết quả AI cho từng nhóm
2. **Dynamic Groups**: Cho phép admin tự định nghĩa nhóm
3. **A/B Testing**: Test nhiều mức discount cho cùng 1 nhóm
4. **Seasonal Adjustment**: Điều chỉnh nhóm theo mùa

---

## 📞 Contact

Có câu hỏi? Liên hệ team development!

---

**Last Updated**: December 20, 2025  
**Version**: 2.0 - Group-Based Optimization
