# 📊 GIẢI THÍCH CÁCH TÍNH % GIẢM GIÁ CHO SỰ KIỆN

## 🎯 Tổng Quan

Hệ thống tự động đề xuất **mức giảm giá phù hợp** cho từng sự kiện dựa trên:

1. **Tầm quan trọng** của sự kiện
2. **Hành vi mua sắm** của khách hàng
3. **Khả năng sinh lời** của shop
4. **Mùa vụ** và xu hướng thị trường

---

## 📈 CÁCH TÍNH DISCOUNT %

### 1️⃣ **Discount Range Cơ Bản (Base Range)**

Mỗi sự kiện có một **discount range được định sẵn** trong file `utils/event_detector.py`:

```python
EVENT_DISCOUNT_RANGES = {
    EventType.TET: "20-40",              # Tết → giảm 20-40%
    EventType.BLACK_FRIDAY: "30-50",     # Black Friday → giảm 30-50%
    EventType.VALENTINE: "10-20",        # Valentine → giảm 10-20%
    EventType.HALLOWEEN: "15-25",        # Halloween → giảm 15-25%
    # ... các sự kiện khác
}
```

### 2️⃣ **Phân Loại Theo Mức Độ Quan Trọng**

| Mức Giảm Giá | Loại Sự Kiện                                            | Ví Dụ                                            |
| ------------ | ------------------------------------------------------- | ------------------------------------------------ |
| **30-50%**   | 🔥 **Mega Sale** - Sự kiện mua sắm lớn nhất năm         | Black Friday, Cyber Monday, Thanh Lý Cuối Năm    |
| **20-40%**   | 🎊 **Sự kiện lớn** - Ngày lễ quan trọng, shopping event | Tết, Trung Thu, Singles Day (11/11), Khai Trương |
| **15-30%**   | 🎉 **Sự kiện vừa** - Ngày lễ phổ biến                   | Giáng Sinh, Tết Dương Lịch, Halloween, Sale Hè   |
| **10-25%**   | 🎈 **Sự kiện nhỏ** - Ngày lễ thông thường               | 8/3, 20/10, Valentine, Khai Trường, Quốc Khánh   |
| **5-15%**    | 📅 **Sự kiện đặc biệt** - Ngày lễ truyền thống nhỏ      | Ông Táo, White Day, Cuối Tuần, Nghề Nghiệp       |
| **0-10%**    | ⚪ **Ngày thường**                                      | Không có sự kiện đặc biệt                        |

---

## 🧮 CHI TIẾT CÁCH TÍNH

### **A. Dựa Trên Tầm Quan Trọng Sự Kiện**

#### 🔥 **Mega Sale Events (30-50%)**

- **Black Friday**: 30-50% - Sự kiện mua sắm lớn nhất thế giới
- **Cyber Monday**: 25-45% - Tiếp nối Black Friday
- **Thanh Lý Cuối Năm**: 25-50% - Giải phóng hàng tồn kho

**Lý do**:

- Khách hàng **kỳ vọng giảm giá sâu**
- Cạnh tranh gay gắt với các shop khác
- Cơ hội đẩy hàng tồn kho

---

#### 🎊 **Major Events (20-40%)**

- **Tết Nguyên Đán**: 20-40% - Sự kiện lớn nhất Việt Nam
- **Singles Day (11/11)**: 20-40% - Ngày độc thân mua sắm
- **Super Sale 11/11**: 25-40% - Sale online lớn
- **Double 12**: 20-35% - Sale cuối năm
- **Khai Trương Shop**: 25-40% - Thu hút khách hàng mới

**Lý do**:

- Sự kiện có **sức mua cao**
- Khách hàng sẵn sàng chi tiêu nhiều
- Thúc đẩy doanh số mạnh mẽ

---

#### 🎉 **Medium Events (15-30%)**

- **Giáng Sinh**: 15-30% - Mùa lễ hội cuối năm
- **Tết Dương Lịch**: 15-30% - Đón năm mới
- **Halloween**: 15-25% - 🎃 Sự kiện quốc tế vui nhộn
- **Trung Thu**: 15-30% - Tết thiếu nhi
- **Sale Hè**: 15-30% - Mùa du lịch
- **Sale Cuối Tháng**: 15-30% - Kích cầu mua sắm

**Lý do**:

- Sự kiện **phổ biến** nhưng không quá lớn
- Khách hàng kỳ vọng khuyến mãi **vừa phải**
- Cân bằng giữa lợi nhuận và doanh số

---

#### 🎈 **Regular Events (10-25%)**

- **Ngày Quốc Tế Phụ Nữ (8/3)**: 10-25%
- **Ngày Phụ Nữ Việt Nam (20/10)**: 10-25%
- **Valentine**: 10-20% - Ngày lễ tình nhân
- **Ngày của Mẹ**: 10-20% - Tri ân mẹ
- **Ngày của Cha**: 10-20% - Tri ân bố
- **Quốc Khánh (2/9)**: 10-25%
- **30/4**: 10-25% - Giải phóng
- **1/5**: 10-20% - Lao động
- **Khai Trường**: 10-25% - Mùa tựu trường
- **Sinh Nhật Shop**: 20-35% - Kỷ niệm đặc biệt

**Lý do**:

- Sự kiện **hàng năm** nhưng tập trung vào **nhóm khách cụ thể**
- Giảm giá vừa đủ để **kích thích mua sắm**
- Bảo vệ lợi nhuận

---

#### 📅 **Minor Events (5-15%)**

- **Ông Táo (23/12 Âm)**: 5-15% - Cúng ông Táo
- **White Day (14/3)**: 5-15% - Ngày đáp lễ Valentine
- **Hàn Thực (3/3 Âm)**: 5-10% - Tết truyền thống nhỏ
- **Đoan Ngọ (5/5 Âm)**: 5-15% - Tết truyền thống
- **Cuối Tuần**: 5-15% - Khuyến mãi thường xuyên
- **Ngày Nhà Giáo (20/11)**: 10-20%
- **Ngày Báo Chí (21/6)**: 5-10%
- **Ngày Thầy Thuốc (27/2)**: 5-15%

**Lý do**:

- Sự kiện **nhỏ**, ít sức mua
- Giảm giá nhẹ để **tạo sự khác biệt**
- Không ảnh hưởng nhiều đến lợi nhuận

---

### **B. Dựa Trên Loại Sản Phẩm**

AI sẽ tính **discount % cụ thể** cho từng sản phẩm dựa trên:

#### 1. **Sản Phẩm Bán Chạy (Best Seller)**

```
Discount = Base Min + 0-5%
```

- Ví dụ: Valentine (10-20%) → Sản phẩm best seller: **10-15%**
- **Lý do**: Sản phẩm đã bán tốt, không cần giảm giá sâu

#### 2. **Sản Phẩm Bán Chậm (Slow Moving)**

```
Discount = Base Max + 0-10%
```

- Ví dụ: Valentine (10-20%) → Sản phẩm bán chậm: **20-30%**
- **Lý do**: Cần đẩy hàng tồn kho, giảm giá sâu hơn

#### 3. **Sản Phẩm Mới (New Product)**

```
Discount = Base Min + 5-10%
```

- Ví dụ: Valentine (10-20%) → Sản phẩm mới: **15-20%**
- **Lý do**: Cần thu hút khách thử sản phẩm mới

#### 4. **Sản Phẩm Theo Mùa (Seasonal)**

```
Discount = Base Max
```

- Ví dụ: Trung Thu (15-30%) → Bánh Trung Thu: **25-30%**
- **Lý do**: Sản phẩm chỉ bán trong mùa, cần giảm giá mạnh

---

### **C. Dựa Trên Phân Tích Dữ Liệu (AI/ML)**

Hệ thống phân tích **dữ liệu lịch sử** để điều chỉnh discount:

#### **1. Phân Tích Doanh Số (Sales Analysis)**

```python
if avg_monthly_sales > median:
    # Sản phẩm bán tốt → giảm ít
    discount = min_discount + (max_discount - min_discount) * 0.3
else:
    # Sản phẩm bán kém → giảm nhiều
    discount = min_discount + (max_discount - min_discount) * 0.8
```

**Ví dụ**: Valentine (10-20%)

- Sản phẩm A: Bán 100 cái/tháng (trung bình 50) → Discount = 10 + (20-10) \* 0.3 = **13%**
- Sản phẩm B: Bán 20 cái/tháng (dưới trung bình) → Discount = 10 + (20-10) \* 0.8 = **18%**

---

#### **2. Phân Tích Đánh Giá (Rating Analysis)**

```python
if avg_rating >= 4.5:
    # Sản phẩm được yêu thích → giảm ít
    discount_adjustment = -2%
elif avg_rating <= 3.0:
    # Sản phẩm kém → giảm nhiều để thanh lý
    discount_adjustment = +5%
```

**Ví dụ**: Halloween (15-25%)

- Bánh Kem A: Rating 4.8/5 → Discount = 15% - 2% = **13%**
- Bánh Kem B: Rating 2.5/5 → Discount = 25% + 5% = **30%**

---

#### **3. Phân Tích Tồn Kho (Inventory Analysis)**

```python
if stock_level > safe_stock * 2:
    # Hàng tồn kho nhiều → giảm mạnh
    discount = max_discount
elif stock_level < safe_stock:
    # Hàng sắp hết → giảm ít
    discount = min_discount
```

**Ví dụ**: Giáng Sinh (15-30%)

- Bánh A: Tồn kho 500 cái (cần thanh lý) → **30%**
- Bánh B: Tồn kho 20 cái (sắp hết) → **15%**

---

#### **4. Market Basket Analysis (Combo Suggestion)**

```python
if product in frequent_combos:
    # Sản phẩm thường mua kèm → giảm vừa để kích combo
    combo_discount = base_discount + 5-10%
```

**Ví dụ**: Tết (20-40%)

- Bánh Chưng + Mứt thường được mua cùng → Combo discount: **35%** (thay vì 25% mỗi món)

---

## 🎯 VÍ DỤ CỤ THỂ: HALLOWEEN (31/10)

### **Base Range**: 15-25%

### **Phân Tích Theo Sản Phẩm**:

| Sản Phẩm                   | Trạng Thái  | Doanh Số | Rating  | Tồn Kho | Discount Đề Xuất | Lý Do                               |
| -------------------------- | ----------- | -------- | ------- | ------- | ---------------- | ----------------------------------- |
| **Bánh Kem Halloween 3D**  | Best Seller | 80/tháng | 4.8/5   | 50 cái  | **18%**          | Bán tốt, rating cao → giảm ít       |
| **Bánh Cookie Ma**         | New Product | 10/tháng | Chưa có | 100 cái | **22%**          | Sản phẩm mới → giảm vừa để thu hút  |
| **Bánh Bí Ngô**            | Seasonal    | 30/tháng | 4.0/5   | 200 cái | **25%**          | Seasonal + tồn kho nhiều → giảm max |
| **Kẹo Halloween Mix**      | Slow Moving | 5/tháng  | 3.5/5   | 300 cái | **25%**          | Bán chậm + rating thấp → giảm mạnh  |
| **Combo Halloween Family** | Combo       | -        | 4.5/5   | -       | **30%**          | Combo ưu đãi để đẩy doanh số        |

---

## 📊 BẢNG TÓM TẮT DISCOUNT % THEO SỰ KIỆN

### **🇻🇳 NGÀY LỄ VIỆT NAM**

| Sự Kiện                    | Ngày     | Discount % | Mức Độ      |
| -------------------------- | -------- | ---------- | ----------- |
| **Tết Nguyên Đán**         | 1/1 Âm   | 20-40%     | 🔥 Cao nhất |
| **Giỗ Tổ Hùng Vương**      | 10/3 Âm  | 10-20%     | 🎈 Vừa      |
| **30/4 - Giải Phóng**      | 30/4     | 10-25%     | 🎈 Vừa      |
| **1/5 - Quốc Tế Lao Động** | 1/5      | 10-20%     | 🎈 Vừa      |
| **2/9 - Quốc Khánh**       | 2/9      | 10-25%     | 🎈 Vừa      |
| **Ông Táo**                | 23/12 Âm | 5-15%      | 📅 Nhỏ      |
| **Hàn Thực**               | 3/3 Âm   | 5-10%      | 📅 Nhỏ      |
| **Đoan Ngọ**               | 5/5 Âm   | 5-15%      | 📅 Nhỏ      |
| **Trung Thu**              | 15/8 Âm  | 15-30%     | 🎉 Lớn      |

### **👨‍👩‍👧 NGÀY GIA ĐÌNH**

| Sự Kiện                    | Ngày       | Discount % | Mức Độ |
| -------------------------- | ---------- | ---------- | ------ |
| **Valentine**              | 14/2       | 10-20%     | 🎈 Vừa |
| **White Day**              | 14/3       | 5-15%      | 📅 Nhỏ |
| **8/3 - Quốc Tế Phụ Nữ**   | 8/3        | 10-25%     | 🎈 Vừa |
| **Ngày của Mẹ**            | CN thứ 2/5 | 10-20%     | 🎈 Vừa |
| **Ngày Quốc Tế Thiếu Nhi** | 1/6        | 10-20%     | 🎈 Vừa |
| **Ngày của Cha**           | CN thứ 3/6 | 10-20%     | 🎈 Vừa |
| **Ngày Gia Đình VN**       | 28/6       | 10-20%     | 🎈 Vừa |
| **20/10 - Phụ Nữ VN**      | 20/10      | 10-25%     | 🎈 Vừa |

### **🎃 NGÀY LỄ QUỐC TẾ**

| Sự Kiện                 | Ngày          | Discount % | Mức Độ      |
| ----------------------- | ------------- | ---------- | ----------- |
| **Halloween** 🎃        | 31/10         | 15-25%     | 🎉 Lớn      |
| **Black Friday**        | Thứ 6 cuối/11 | 30-50%     | 🔥 Cao nhất |
| **Cyber Monday**        | Thứ 2 sau BF  | 25-45%     | 🔥 Cao nhất |
| **Singles Day (11/11)** | 11/11         | 20-40%     | 🎊 Lớn      |
| **Double 12**           | 12/12         | 20-35%     | 🎊 Lớn      |
| **Đêm Giáng Sinh**      | 24/12         | 10-20%     | 🎈 Vừa      |
| **Giáng Sinh**          | 25/12         | 15-30%     | 🎉 Lớn      |
| **Đêm Giao Thừa**       | 31/12         | 15-25%     | 🎉 Lớn      |
| **Tết Dương Lịch**      | 1/1           | 15-30%     | 🎉 Lớn      |

### **👨‍🏫 NGÀY NGHỀ NGHIỆP**

| Sự Kiện                | Ngày  | Discount % | Mức Độ |
| ---------------------- | ----- | ---------- | ------ |
| **Ngày Thầy Thuốc VN** | 27/2  | 5-15%      | 📅 Nhỏ |
| **Ngày Báo Chí VN**    | 21/6  | 5-10%      | 📅 Nhỏ |
| **Ngày Nhà Giáo VN**   | 20/11 | 10-20%     | 🎈 Vừa |

### **🛒 SỰ KIỆN MUA SẮM**

| Sự Kiện               | Thời Gian        | Discount % | Mức Độ      |
| --------------------- | ---------------- | ---------- | ----------- |
| **Flash Sale**        | Bất kỳ           | 20-40%     | 🎊 Lớn      |
| **Cuối Tuần**         | T7-CN            | 5-15%      | 📅 Nhỏ      |
| **Ngày Lương**        | 27-30 hàng tháng | 10-25%     | 🎈 Vừa      |
| **Sale Cuối Tháng**   | Cuối tháng       | 15-30%     | 🎉 Lớn      |
| **Khai Trường**       | Tháng 8-9        | 10-25%     | 🎈 Vừa      |
| **Mùa Tốt Nghiệp**    | Tháng 5-6        | 10-20%     | 🎈 Vừa      |
| **Sale Hè**           | Tháng 6-8        | 15-30%     | 🎉 Lớn      |
| **Thanh Lý Cuối Năm** | Tháng 12         | 25-50%     | 🔥 Cao nhất |

### **🏪 SỰ KIỆN SHOP**

| Sự Kiện               | Thời Gian | Discount % | Mức Độ |
| --------------------- | --------- | ---------- | ------ |
| **Sinh Nhật Shop**    | Tùy shop  | 20-35%     | 🎊 Lớn |
| **Kỷ Niệm Thành Lập** | Tùy shop  | 20-35%     | 🎊 Lớn |
| **Khai Trương**       | Lần đầu   | 25-40%     | 🎊 Lớn |
| **Tri Ân Khách Hàng** | Tùy shop  | 15-30%     | 🎉 Lớn |

---

## 🚀 TÓM TẮT

### **Discount % được tính dựa trên**:

1. ✅ **Base Range** (Event Type) - 50%
   - Tầm quan trọng của sự kiện
   - Hành vi mua sắm khách hàng
2. ✅ **Product Performance** (AI Analysis) - 30%
   - Doanh số bán hàng
   - Đánh giá của khách
   - Tồn kho
3. ✅ **Market Basket Analysis** (Combo) - 10%
   - Sản phẩm thường mua kèm
   - Tối ưu hóa combo
4. ✅ **Strategy & Risk** (Business Logic) - 10%
   - Mục tiêu kinh doanh
   - Quản lý rủi ro
   - Cạnh tranh thị trường

### **Công Thức Tổng Quát**:

```python
Final_Discount = Base_Discount
                 + Product_Performance_Adjustment (-5% đến +10%)
                 + Combo_Bonus (0-10%)
                 + Strategy_Factor (-3% đến +5%)
```

**Ví dụ**: Halloween - Bánh Kem Halloween 3D

```
Base: 15-25% → Chọn 20%
Performance: Bán tốt, rating cao → -2%
Combo: Không có combo → 0%
Strategy: Sản phẩm mới muốn quảng bá → 0%
→ Final Discount = 20% - 2% = 18%
```

---

## 📞 LƯU Ý

1. **Discount range chỉ là gợi ý** - Shop có thể điều chỉnh dựa trên chiến lược kinh doanh
2. **AI sẽ tính toán cụ thể** cho từng sản phẩm dựa trên dữ liệu thực tế
3. **Không nhất thiết phải giảm giá** - Có thể dùng chiến lược khác (tặng quà, combo, tích điểm)
4. **Theo dõi kết quả** - Điều chỉnh discount % dựa trên hiệu quả thực tế

---

**🎯 KẾT LUẬN**: Hệ thống kết hợp **quy luật kinh doanh** (event importance) + **AI/ML** (data analysis) để đề xuất discount % **tối ưu** cho từng sản phẩm, đảm bảo **tăng doanh số** mà vẫn **bảo toàn lợi nhuận**! 🚀
