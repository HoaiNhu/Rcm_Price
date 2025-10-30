# 🤖 AI/ML OPTIMIZATION CHO % GIẢM GIÁ TỐI ƯU

## 🎯 MỤC TIÊU

Thay vì dùng **hard-coded discount ranges** (10-20%, 20-40%), sử dụng **AI/ML** để:

- 📊 **Dự đoán discount % tối ưu** cho từng sản phẩm
- 💰 **Tối đa hóa doanh thu** thay vì chỉ tăng số lượng bán
- 🎯 **Cá nhân hóa** discount cho từng khách hàng
- 📈 **Học từ dữ liệu lịch sử** để cải thiện liên tục

---

## 🧠 PHƯƠNG PHÁP AI/ML CÓ THỂ SỬ DỤNG

### **1️⃣ PRICE ELASTICITY OPTIMIZATION (Tối ưu độ co giãn giá)**

#### **📊 Mô tả**

Sử dụng **Linear Regression** hoặc **Polynomial Regression** để tìm mối quan hệ giữa:

- **Discount %** (biến độc lập)
- **Revenue** (biến phụ thuộc)

#### **🔬 Công thức**

```
Revenue = (Original_Price - Discount) × Quantity_Sold

Price Elasticity = % Change in Quantity / % Change in Price

Optimal_Discount = argmax(Revenue) where Revenue = f(discount%)
```

#### **💻 Implementation**

```python
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize_scalar
import numpy as np

class PriceElasticityOptimizer:
    """
    Tối ưu hóa discount % dựa trên độ co giãn giá
    """

    def __init__(self, historical_data):
        """
        historical_data: DataFrame với columns:
        - discount_percent: % giảm giá đã áp dụng
        - quantity_sold: Số lượng bán được
        - revenue: Doanh thu thực tế
        - product_id: ID sản phẩm
        - event_type: Loại sự kiện
        """
        self.data = historical_data
        self.models = {}

    def train_model(self, product_id, event_type):
        """
        Train model cho từng sản phẩm + sự kiện cụ thể
        """
        # Lọc dữ liệu
        subset = self.data[
            (self.data['product_id'] == product_id) &
            (self.data['event_type'] == event_type)
        ]

        if len(subset) < 3:
            return None  # Không đủ dữ liệu

        X = subset[['discount_percent']].values
        y = subset['revenue'].values

        # Train Polynomial Regression (bậc 2)
        from sklearn.preprocessing import PolynomialFeatures
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)

        model = LinearRegression()
        model.fit(X_poly, y)

        self.models[(product_id, event_type)] = {
            'model': model,
            'poly': poly,
            'base_price': subset['base_price'].iloc[0]
        }

        return model

    def predict_optimal_discount(self, product_id, event_type,
                                  min_discount=0, max_discount=50):
        """
        Tìm % giảm giá tối ưu cho doanh thu cao nhất
        """
        key = (product_id, event_type)
        if key not in self.models:
            return None

        model_info = self.models[key]
        model = model_info['model']
        poly = model_info['poly']

        # Hàm dự đoán revenue
        def revenue_function(discount):
            X = np.array([[discount]])
            X_poly = poly.transform(X)
            return -model.predict(X_poly)[0]  # Negative vì minimize

        # Tìm discount tối ưu
        result = minimize_scalar(
            revenue_function,
            bounds=(min_discount, max_discount),
            method='bounded'
        )

        optimal_discount = result.x
        max_revenue = -result.fun

        return {
            'optimal_discount': round(optimal_discount, 2),
            'predicted_revenue': round(max_revenue, 2),
            'confidence': self._calculate_confidence(key)
        }

    def _calculate_confidence(self, key):
        """Tính độ tin cậy dựa trên số lượng dữ liệu"""
        # Càng nhiều dữ liệu → confidence càng cao
        data_points = len(self.data[
            (self.data['product_id'] == key[0]) &
            (self.data['event_type'] == key[1])
        ])
        return min(data_points / 10, 1.0)  # Max 100%
```

#### **📈 Ví dụ sử dụng**

```python
# Load dữ liệu lịch sử
historical_data = pd.DataFrame({
    'product_id': [1, 1, 1, 1, 1],
    'event_type': ['VALENTINE', 'VALENTINE', 'VALENTINE', 'VALENTINE', 'VALENTINE'],
    'discount_percent': [0, 10, 20, 30, 40],
    'quantity_sold': [50, 80, 120, 100, 70],
    'base_price': [100000, 100000, 100000, 100000, 100000],
    'revenue': [5000000, 7200000, 9600000, 7000000, 4200000]
})

# Train model
optimizer = PriceElasticityOptimizer(historical_data)
optimizer.train_model(product_id=1, event_type='VALENTINE')

# Dự đoán discount tối ưu
result = optimizer.predict_optimal_discount(
    product_id=1,
    event_type='VALENTINE'
)

print(f"Optimal Discount: {result['optimal_discount']}%")
print(f"Predicted Revenue: {result['predicted_revenue']:,} VNĐ")
# Output: Optimal Discount: 22.5% → Revenue: 9,650,000 VNĐ
```

---

### **2️⃣ REINFORCEMENT LEARNING (Học tăng cường)**

#### **📊 Mô tả**

Sử dụng **Multi-Armed Bandit** hoặc **Q-Learning** để:

- Thử nghiệm các mức discount khác nhau
- Học từ kết quả thực tế (revenue)
- Tự động điều chỉnh discount % theo thời gian

#### **🔬 Thuật toán: Thompson Sampling**

```python
import numpy as np
from scipy.stats import beta

class ThompsonSamplingDiscountOptimizer:
    """
    Tối ưu hóa discount % bằng Thompson Sampling
    """

    def __init__(self, discount_options=[10, 15, 20, 25, 30, 35, 40]):
        """
        discount_options: Các mức discount có thể chọn
        """
        self.discount_options = discount_options

        # Beta distribution parameters cho mỗi discount level
        self.alpha = {d: 1 for d in discount_options}  # Success count
        self.beta_param = {d: 1 for d in discount_options}  # Failure count

    def select_discount(self):
        """
        Chọn discount % tốt nhất bằng Thompson Sampling
        """
        # Sample từ Beta distribution cho mỗi option
        sampled_theta = {
            d: np.random.beta(self.alpha[d], self.beta_param[d])
            for d in self.discount_options
        }

        # Chọn discount có theta cao nhất
        best_discount = max(sampled_theta, key=sampled_theta.get)
        return best_discount

    def update(self, discount, revenue, target_revenue=10000000):
        """
        Cập nhật model sau khi nhận kết quả

        revenue: Doanh thu thực tế
        target_revenue: Doanh thu mục tiêu
        """
        # Success nếu revenue >= target, failure nếu ngược lại
        if revenue >= target_revenue:
            self.alpha[discount] += 1  # Success
        else:
            self.beta_param[discount] += 1  # Failure

    def get_best_discount(self):
        """
        Lấy discount có xác suất thành công cao nhất
        """
        success_rates = {
            d: self.alpha[d] / (self.alpha[d] + self.beta_param[d])
            for d in self.discount_options
        }
        return max(success_rates, key=success_rates.get)
```

#### **📈 Ví dụ sử dụng**

```python
optimizer = ThompsonSamplingDiscountOptimizer()

# Simulation: 100 lần bán hàng
for i in range(100):
    # Chọn discount
    discount = optimizer.select_discount()

    # Giả lập bán hàng (trong thực tế sẽ lấy từ DB)
    revenue = simulate_sale(discount)

    # Cập nhật model
    optimizer.update(discount, revenue, target_revenue=8000000)

# Sau 100 lần học
best = optimizer.get_best_discount()
print(f"Best Discount: {best}%")
```

---

### **3️⃣ GRADIENT BOOSTING MACHINES (XGBoost/LightGBM)**

#### **📊 Mô tả**

Sử dụng **XGBoost** để dự đoán revenue dựa trên nhiều features:

#### **💻 Implementation**

```python
import xgboost as xgb
import pandas as pd
import numpy as np

class XGBoostDiscountOptimizer:
    """
    Tối ưu hóa discount % bằng XGBoost
    """

    def __init__(self):
        self.model = None

    def prepare_features(self, data):
        """
        Tạo features từ dữ liệu
        """
        features = pd.DataFrame({
            # Product features
            'product_price': data['base_price'],
            'product_category': data['category'].astype('category').cat.codes,
            'avg_rating': data['avg_rating'],
            'review_count': data['review_count'],

            # Event features
            'event_type': data['event_type'].astype('category').cat.codes,
            'days_to_event': data['days_to_event'],
            'event_importance': data['event_importance'],  # 1-5 scale

            # Discount feature
            'discount_percent': data['discount_percent'],

            # Time features
            'day_of_week': data['date'].dt.dayofweek,
            'month': data['date'].dt.month,
            'is_weekend': data['date'].dt.dayofweek.isin([5, 6]).astype(int),

            # Customer features
            'customer_segment': data['customer_segment'].astype('category').cat.codes,
            'purchase_history': data['purchase_count'],

            # Inventory features
            'stock_level': data['current_stock'],
            'days_until_expire': data['days_until_expire'],

            # Competition features
            'competitor_discount_avg': data['competitor_avg_discount'],
            'market_demand': data['market_demand_index'],
        })

        return features

    def train(self, historical_data):
        """
        Train XGBoost model
        """
        X = self.prepare_features(historical_data)
        y = historical_data['revenue']

        # XGBoost parameters
        params = {
            'objective': 'reg:squarederror',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
        }

        self.model = xgb.XGBRegressor(**params)
        self.model.fit(X, y)

        return self.model

    def find_optimal_discount(self, product_data, discount_range=(0, 50)):
        """
        Tìm discount tối ưu cho 1 sản phẩm
        """
        best_discount = None
        max_revenue = 0

        # Thử từng mức discount
        for discount in range(discount_range[0], discount_range[1] + 1):
            # Tạo features với discount này
            test_data = product_data.copy()
            test_data['discount_percent'] = discount

            X = self.prepare_features(test_data)
            predicted_revenue = self.model.predict(X)[0]

            if predicted_revenue > max_revenue:
                max_revenue = predicted_revenue
                best_discount = discount

        return {
            'optimal_discount': best_discount,
            'predicted_revenue': max_revenue,
            'feature_importance': self.get_feature_importance()
        }

    def get_feature_importance(self):
        """Xem features nào quan trọng nhất"""
        if self.model is None:
            return None

        importance = pd.DataFrame({
            'feature': self.model.feature_names_in_,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        return importance
```

#### **📈 Ví dụ sử dụng**

```python
# Load dữ liệu lịch sử
historical_data = load_historical_promotions()

# Train model
optimizer = XGBoostDiscountOptimizer()
optimizer.train(historical_data)

# Dự đoán cho sản phẩm mới
product_data = pd.DataFrame({
    'base_price': [150000],
    'category': ['Bánh Kem'],
    'avg_rating': [4.5],
    'event_type': ['HALLOWEEN'],
    'days_to_event': [1],
    # ... các features khác
})

result = optimizer.find_optimal_discount(product_data)
print(f"Optimal Discount: {result['optimal_discount']}%")
print(f"Predicted Revenue: {result['predicted_revenue']:,} VNĐ")
```

---

### **4️⃣ DEEP LEARNING (Neural Networks)**

#### **📊 Mô tả**

Sử dụng **Neural Network** để học mối quan hệ phức tạp:

```python
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

class DeepDiscountOptimizer:
    """
    Tối ưu hóa discount % bằng Deep Neural Network
    """

    def __init__(self, input_dim):
        self.model = self._build_model(input_dim)

    def _build_model(self, input_dim):
        """
        Xây dựng DNN model
        """
        model = keras.Sequential([
            # Input layer
            layers.Dense(128, activation='relu', input_dim=input_dim),
            layers.Dropout(0.2),

            # Hidden layers
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),

            layers.Dense(32, activation='relu'),
            layers.Dropout(0.1),

            # Output layer (predict revenue)
            layers.Dense(1, activation='linear')
        ])

        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )

        return model

    def train(self, X_train, y_train, epochs=100):
        """Train model"""
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=32,
            validation_split=0.2,
            verbose=1
        )
        return history

    def find_optimal_discount(self, features, discount_range=(0, 50)):
        """Tìm discount tối ưu"""
        best_discount = None
        max_revenue = 0

        for discount in np.arange(discount_range[0], discount_range[1], 0.5):
            # Update discount feature
            features_copy = features.copy()
            features_copy['discount_percent'] = discount

            # Predict revenue
            X = features_copy.values.reshape(1, -1)
            predicted_revenue = self.model.predict(X, verbose=0)[0][0]

            if predicted_revenue > max_revenue:
                max_revenue = predicted_revenue
                best_discount = discount

        return {
            'optimal_discount': round(best_discount, 2),
            'predicted_revenue': round(max_revenue, 2)
        }
```

---

### **5️⃣ TIME SERIES FORECASTING (LSTM/Prophet)**

#### **📊 Mô tả**

Sử dụng **LSTM** hoặc **Prophet** để dự đoán xu hướng theo thời gian:

```python
from prophet import Prophet
import pandas as pd

class ProphetDiscountOptimizer:
    """
    Dự đoán revenue theo thời gian với các mức discount khác nhau
    """

    def __init__(self):
        self.models = {}

    def train_for_discount(self, discount_percent, historical_data):
        """
        Train Prophet model cho mỗi mức discount
        """
        # Lọc data cho discount này
        data = historical_data[
            historical_data['discount_percent'] == discount_percent
        ][['date', 'revenue']].rename(columns={'date': 'ds', 'revenue': 'y'})

        # Train Prophet
        model = Prophet()
        model.fit(data)

        self.models[discount_percent] = model

    def predict_revenue(self, discount_percent, future_date):
        """
        Dự đoán revenue cho discount và ngày cụ thể
        """
        if discount_percent not in self.models:
            return None

        future = pd.DataFrame({'ds': [future_date]})
        forecast = self.models[discount_percent].predict(future)

        return forecast['yhat'].iloc[0]

    def find_optimal_discount_for_date(self, date, discount_options):
        """
        Tìm discount tốt nhất cho ngày cụ thể
        """
        predictions = {}

        for discount in discount_options:
            revenue = self.predict_revenue(discount, date)
            if revenue is not None:
                predictions[discount] = revenue

        optimal = max(predictions, key=predictions.get)

        return {
            'optimal_discount': optimal,
            'predicted_revenue': predictions[optimal],
            'all_predictions': predictions
        }
```

---

## 🚀 KIẾN TRÚC ĐỀ XUẤT CHO HỆ THỐNG

### **Hybrid Approach (Kết hợp nhiều phương pháp)**

```
┌─────────────────────────────────────────────────┐
│         INPUT: Product + Event + Context        │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
┌─────────────┐         ┌─────────────┐
│ RULE-BASED  │         │  ML MODELS  │
│ (Fallback)  │         │  (Primary)  │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │    ┌──────────────────┤
       │    │                  │
       │    ▼                  ▼
       │ ┌──────┐         ┌──────────┐
       │ │XGBoost│        │Thompson  │
       │ │Model │         │Sampling  │
       │ └───┬──┘         └────┬─────┘
       │     │                 │
       │     ▼                 ▼
       │ ┌────────────────────────┐
       │ │  ENSEMBLE PREDICTION   │
       │ │  (Weighted Average)    │
       │ └───────────┬────────────┘
       │             │
       └─────────────┼─────────────┐
                     │             │
                     ▼             ▼
              ┌─────────────────────────┐
              │  A/B TESTING LAYER      │
              │  - Test 2-3 discounts   │
              │  - Real-time feedback   │
              └────────────┬────────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  FINAL DISCOUNT %    │
                │  + Confidence Score  │
                └──────────────────────┘
```

---

## 📊 DỮ LIỆU CẦN THU THẬP

Để train ML models hiệu quả, cần thu thập:

### **1. Historical Sales Data**

```sql
CREATE TABLE promotion_history (
    id BIGINT PRIMARY KEY,
    product_id BIGINT,
    event_type VARCHAR(50),
    discount_percent DECIMAL(5,2),
    original_price DECIMAL(10,2),
    final_price DECIMAL(10,2),
    quantity_sold INT,
    revenue DECIMAL(12,2),
    date DATE,
    day_of_week INT,
    is_weekend BOOLEAN,
    customer_segment VARCHAR(20),
    created_at TIMESTAMP
);
```

### **2. Product Features**

- Base price
- Category
- Rating & reviews
- Stock level
- Days until expire (cho bánh)
- Historical sales velocity

### **3. Event Features**

- Event type
- Days to event
- Event importance (1-5)
- Historical event performance

### **4. Market Context**

- Competitor discounts
- Market demand index
- Seasonal factors
- Economic indicators

---

## 🎯 IMPLEMENTATION ROADMAP

### **Phase 1: MVP (2-3 tuần)**

✅ Implement Price Elasticity Optimizer (Linear Regression)
✅ Collect 3 months historical data
✅ A/B test với rule-based approach

### **Phase 2: ML Enhancement (1 tháng)**

✅ Train XGBoost model
✅ Add Thompson Sampling for exploration
✅ Build ensemble model

### **Phase 3: Advanced AI (2 tháng)**

✅ Deep Learning model (DNN)
✅ Time series forecasting (Prophet/LSTM)
✅ Real-time optimization

### **Phase 4: Production (ongoing)**

✅ Auto-retraining pipeline
✅ Monitoring & alerting
✅ Continuous A/B testing

---

## 📈 KẾT QUẢ KỲ VỌNG

| Metric                    | Current (Rule-based) | ML-optimized | Improvement |
| ------------------------- | -------------------- | ------------ | ----------- |
| **Revenue**               | Baseline             | +15-25%      | 🚀          |
| **Conversion Rate**       | Baseline             | +10-20%      | 📈          |
| **Profit Margin**         | Baseline             | +5-10%       | 💰          |
| **Customer Satisfaction** | Baseline             | +10-15%      | 😊          |

---

## 🔧 NEXT STEPS

1. **Tôi implement ML optimizer vào hệ thống không?**

   - Chọn phương pháp: XGBoost (recommended) hoặc Thompson Sampling
   - Tạo training pipeline
   - Integrate vào API

2. **Cần bổ sung data collection?**

   - Track promotion history
   - A/B testing framework

3. **Deploy & monitor?**
   - MLOps pipeline
   - Real-time retraining

Bạn muốn implement cái nào trước? 🚀
