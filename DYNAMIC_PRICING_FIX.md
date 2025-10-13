# Fix: Dynamic Pricing Model - OrderItems Structure Error

## Vấn Đề (Problem)

Khi khởi tạo Hybrid Recommendation System, Dynamic Pricing Model báo lỗi:

```
ERROR:infrastructure.ml_models.dynamic_pricing:❌ Error preparing pricing data: 'orderItems[0].product'
```

Điều này khiến pricing data không được chuẩn bị đúng cách.

## Nguyên Nhân (Root Cause)

Code trong `dynamic_pricing.py` giả định rằng MongoDB trả về dữ liệu đã được **flatten** với columns như:

- `orderItems[0].product`
- `orderItems[0].quantity`
- `orderItems[0].total`

Nhưng thực tế, MongoDB trả về **nested structure** (array of objects):

```python
{
  "_id": "676d7cce4d065cdde8cce2c6",
  "orderItems": [
    {
      "product": ObjectId("67643c2411d943b7bdecb7d3"),
      "quantity": 3,
      "total": 750000,
      "_id": ObjectId("676d7cce4d065cdde8cce2c7")
    }
  ],
  "totalPrice": 780000,
  ...
}
```

Column `orderItems` là một **list**, không phải flat columns.

## Giải Pháp (Solution)

Thêm logic **flatten orderItems** trước khi xử lý:

### Code Cũ (Lỗi):

```python
# Truy cập trực tiếp column không tồn tại
product_orders = orders_df[orders_df['orderItems[0].product'] == product_id]

daily_stats = product_orders.groupby('date').agg({
    'orderItems[0].quantity': 'sum',
    'orderItems[0].total': 'mean',
    'totalPrice': 'sum'
})
```

### Code Mới (Fix):

```python
# Flatten orderItems array thành flat DataFrame
flattened_orders = []
for _, order in orders_df.iterrows():
    if 'orderItems' in order and isinstance(order['orderItems'], list):
        for item in order['orderItems']:
            if isinstance(item, dict):
                flattened_orders.append({
                    'order_id': order['_id'],
                    'date': order['date'],
                    'product_id': str(item.get('product', '')),
                    'quantity': item.get('quantity', 0),
                    'total': item.get('total', 0),
                    'createdAt': order['createdAt']
                })

flat_df = pd.DataFrame(flattened_orders)

# Giờ có thể truy cập dễ dàng
product_orders = flat_df[flat_df['product_id'] == str(product_id)]

daily_stats = product_orders.groupby('date').agg({
    'quantity': 'sum',
    'total': 'sum'
})
```

### Chi Tiết Thay Đổi:

1. **Flatten nested orderItems**:

   - Loop qua từng order
   - Loop qua từng item trong `orderItems` array
   - Tạo flat record với các fields: product_id, quantity, total, date

2. **Sửa tên columns**:

   - `orderItems[0].quantity` → `quantity`
   - `orderItems[0].total` → `total` (tổng tiền của item)
   - Tính `avg_price = total / quantity`

3. **Sửa revenue calculation**:
   - Code cũ: `revenue = day_data['totalPrice']` (lỗi vì totalPrice là tổng đơn hàng, không phải tổng của 1 product)
   - Code mới: `revenue = total_revenue` (tổng từ aggregation của item.total)

## File Đã Sửa (Modified Files)

- `infrastructure/ml_models/dynamic_pricing.py`
  - Method: `prepare_pricing_data()`

## Kết Quả (Result)

✅ Server khởi động thành công:

```
INFO:infrastructure.ml_models.dynamic_pricing:✅ Dynamic Pricing Model initialized
INFO:application.services.hybrid_recommender:✅ Hybrid Recommendation System initialized
INFO:__main__:✅ All AI services initialized successfully
```

✅ Không còn lỗi `'orderItems[0].product'`

✅ Hybrid system có thể initialize và prepare pricing data đúng cách

## Cách Test (How to Test)

1. **Start server:**

   ```powershell
   $env:PYTHONPATH="c:\Users\Lenovo\STUDY\RCM_PRICE"
   python app\main.py
   ```

2. **Initialize hybrid system:**

   ```
   POST http://localhost:8000/api/hybrid/initialize
   ```

3. **Check logs - Nên thấy:**

   ```
   ✅ Retrieved 111 orders from MongoDB
   ✅ Retrieved 31 products from MongoDB
   ✅ HuggingFace model loaded successfully
   ✅ Created embeddings for 31 products
   ✅ Prepared pricing data: X records  <-- KHÔNG CÒN LỖI
   ✅ Hybrid Recommendation System initialized successfully
   ```

4. **Test pricing endpoints:**
   ```
   GET http://localhost:8000/api/pricing/strategy
   GET http://localhost:8000/api/pricing/optimize/{product_id}
   ```

## MongoDB Data Structure Reference

### Orders Collection Structure:

```json
{
  "_id": "676d7cce4d065cdde8cce2c6",
  "orderCode": "ORD-1735228622685",
  "orderItems": [              // 📌 Array, not flat columns!
    {
      "product": ObjectId("67643c2411d943b7bdecb7d3"),
      "quantity": 3,
      "total": 750000,
      "_id": ObjectId("676d7cce4d065cdde8cce2c7")
    }
  ],
  "userId": "6756e4441df899603742e267",
  "totalItemPrice": 750000,
  "totalPrice": 780000,
  "createdAt": "2024-12-26 15:57:02.710000",
  ...
}
```

### Flattened Structure (After Fix):

```python
{
  'order_id': '676d7cce4d065cdde8cce2c6',
  'date': datetime.date(2024, 12, 26),
  'product_id': '67643c2411d943b7bdecb7d3',
  'quantity': 3,
  'total': 750000,
  'createdAt': Timestamp('2024-12-26 15:57:02.710000')
}
```

## Lưu Ý (Notes)

1. **Multiple items per order**: Một order có thể có nhiều items, code flatten sẽ tạo nhiều records
2. **ObjectId conversion**: Phải convert `item.get('product')` thành `str()` để match với products_df['_id']
3. **Empty check**: Phải check `if not flattened_orders:` trước khi create DataFrame
4. **Daily aggregation**: Group by date và product_id, sum quantity và total

## Tài Liệu Liên Quan (Related Documentation)

- `TENSORFLOW_STUB_FIX.md` - Fix TensorFlow stub missing methods
- `FIX_MONGODB_CONNECTION.md` - Fix MongoDB connection issue
- `debug_orders_structure.py` - Script để debug MongoDB data structure

---

**Ngày sửa:** 11/10/2025  
**Status:** ✅ RESOLVED
