# 🎯 CHIẾN LƯỢC PRICING THÂN THIỆN VỚI KHÁCH HÀNG TRUNG THÀNH

## 📊 PHÂN TÍCH VẤN ĐỀ

### Vấn đề hiện tại

Bạn đã nêu đúng vấn đề: **Dynamic Pricing có thể làm mất khách hàng trung thành** nếu không được thực hiện cẩn thận.

**Ví dụ thực tế:**

- Bánh su 20k → 25-30k đột ngột = Khách quen cảm thấy bị "lừa"
- Khách mua thường xuyên cảm thấy không được trân trọng
- Loss aversion (tâm lý sợ mất) > Gain seeking

---

## ✅ ĐÁNH GIÁ FLOW GIẢI QUYẾT CỦA BẠN

### Flow 6 bước bạn đề xuất:

| Bước                             | Đánh giá                     | Khả thi       | Ưu tiên       |
| -------------------------------- | ---------------------------- | ------------- | ------------- |
| **1. Tính độ nhạy giá**          | ⭐⭐⭐⭐⭐ Cực kỳ quan trọng | ✅ Có thể làm | 🔥 Cao        |
| **2. Phân nhóm khách**           | ⭐⭐⭐⭐⭐ Thiết yếu         | ✅ Có thể làm | 🔥 Cao        |
| **3. Dynamic pricing phân tầng** | ⭐⭐⭐⭐⭐ Core feature      | ✅ Có thể làm | 🔥 Cao        |
| **4. Mô phỏng trước**            | ⭐⭐⭐⭐ Rất tốt             | ✅ Có thể làm | 🔶 Trung bình |
| **5. Khuyến mãi thông minh**     | ⭐⭐⭐⭐⭐ Cần thiết         | ✅ Có thể làm | 🔥 Cao        |
| **6. Học hành vi**               | ⭐⭐⭐⭐⭐ Long-term value   | ✅ Có thể làm | 🔶 Trung bình |

### 🎉 KẾT LUẬN: Flow của bạn **CỰC KỲ KHẢ THI** và **ĐÃ CÓ DỮ LIỆU PHÙ HỢP!**

---

## 🏗️ KIẾN TRÚC TECHNICAL CHI TIẾT

### 1️⃣ PRICE ELASTICITY (Độ nhạy giá)

**Mục tiêu:** Xác định sản phẩm nào có thể tăng giá mà không mất khách

```python
# File: infrastructure/ml_models/price_elasticity.py

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, List, Tuple

class PriceElasticityCalculator:
    """
    Tính độ nhạy cảm về giá của từng sản phẩm

    Price Elasticity = % Change in Quantity / % Change in Price

    - Elasticity < -1: Rất nhạy cảm (elastic) - Không nên tăng giá
    - -1 < Elasticity < 0: Ít nhạy cảm (inelastic) - Có thể tăng giá
    - Elasticity > 0: Giffen goods (rất hiếm)
    """

    def __init__(self):
        self.elasticity_models = {}
        self.product_elasticity = {}

    def calculate_elasticity(self,
                            orders_df: pd.DataFrame,
                            products_df: pd.DataFrame) -> Dict[str, float]:
        """
        Tính price elasticity cho từng sản phẩm

        Returns:
            {
                "product_id_1": -0.5,  # Inelastic - có thể tăng giá
                "product_id_2": -1.8,  # Elastic - nhạy cảm, không nên tăng
            }
        """
        elasticity_results = {}

        # Flatten orders
        flattened_orders = self._flatten_order_items(orders_df)

        for product_id in products_df['_id'].unique():
            product_orders = flattened_orders[
                flattened_orders['product_id'] == str(product_id)
            ]

            if len(product_orders) < 10:  # Cần ít nhất 10 đơn hàng
                continue

            # Prepare data
            product_orders['price'] = product_orders['total'] / product_orders['quantity']
            product_orders = product_orders.sort_values('date')

            # Calculate changes
            product_orders['price_change'] = product_orders['price'].pct_change()
            product_orders['quantity_change'] = product_orders['quantity'].pct_change()

            # Remove outliers and NaN
            clean_data = product_orders.dropna()
            clean_data = clean_data[
                (abs(clean_data['price_change']) < 0.5) &  # Remove extreme changes
                (abs(clean_data['quantity_change']) < 2.0)
            ]

            if len(clean_data) < 5:
                continue

            # Calculate elasticity using regression
            X = clean_data[['price_change']].values
            y = clean_data['quantity_change'].values

            model = LinearRegression()
            model.fit(X, y)

            elasticity = model.coef_[0]
            elasticity_results[product_id] = elasticity

            # Store model
            self.elasticity_models[product_id] = model

        self.product_elasticity = elasticity_results
        return elasticity_results

    def get_price_sensitivity_category(self, elasticity: float) -> str:
        """Phân loại độ nhạy giá"""
        if elasticity < -1.5:
            return "VERY_SENSITIVE"  # Rất nhạy cảm - KHÔNG tăng giá
        elif elasticity < -1.0:
            return "SENSITIVE"  # Nhạy cảm - Tăng giá cẩn thận
        elif elasticity < -0.5:
            return "MODERATE"  # Trung bình - Có thể tăng nhẹ
        else:
            return "INSENSITIVE"  # Không nhạy cảm - Có thể tăng giá

    def recommend_price_change(self,
                              product_id: str,
                              current_price: float) -> Dict:
        """
        Đề xuất thay đổi giá dựa trên elasticity
        """
        if product_id not in self.product_elasticity:
            return {
                "can_increase": False,
                "reason": "Insufficient data",
                "max_increase": 0
            }

        elasticity = self.product_elasticity[product_id]
        sensitivity = self.get_price_sensitivity_category(elasticity)

        # Safe price increase limits
        safe_increase = {
            "VERY_SENSITIVE": 0.02,   # Max 2% increase
            "SENSITIVE": 0.05,         # Max 5% increase
            "MODERATE": 0.10,          # Max 10% increase
            "INSENSITIVE": 0.15        # Max 15% increase
        }

        max_increase_pct = safe_increase[sensitivity]
        max_price = current_price * (1 + max_increase_pct)

        return {
            "product_id": product_id,
            "current_price": current_price,
            "elasticity": elasticity,
            "sensitivity": sensitivity,
            "can_increase": True,
            "max_safe_increase_pct": max_increase_pct * 100,
            "max_safe_price": max_price,
            "recommendation": self._get_recommendation(sensitivity)
        }

    def _get_recommendation(self, sensitivity: str) -> str:
        recommendations = {
            "VERY_SENSITIVE": "⚠️ SẢN PHẨM RẤT NHẠY GIÁ - Ưu tiên khuyến mãi thay vì tăng giá",
            "SENSITIVE": "⚠️ Nhạy cảm về giá - Nên kết hợp voucher khi tăng giá",
            "MODERATE": "✅ Có thể tăng giá nhẹ - Monitor phản hồi khách hàng",
            "INSENSITIVE": "✅ Sản phẩm premium - Có thể tăng giá thoải mái"
        }
        return recommendations[sensitivity]

    def _flatten_order_items(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Flatten nested order items"""
        flattened = []
        for _, order in orders_df.iterrows():
            if 'orderItems' in order and isinstance(order['orderItems'], list):
                for item in order['orderItems']:
                    if isinstance(item, dict):
                        flattened.append({
                            'order_id': order['_id'],
                            'date': order['createdAt'],
                            'product_id': str(item.get('product', '')),
                            'quantity': item.get('quantity', 0),
                            'total': item.get('total', 0),
                        })
        return pd.DataFrame(flattened)

```

---

### 2️⃣ CUSTOMER SEGMENTATION (Phân nhóm khách)

**Mục tiêu:** Phân khách thành các nhóm để áp dụng pricing khác nhau

```python
# File: infrastructure/ml_models/customer_segmentation.py

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, List
from datetime import datetime, timedelta

class CustomerSegmentation:
    """
    Phân khách hàng thành 4 nhóm:
    1. VIP/Loyal - Khách trung thành (protect at all cost)
    2. Regular - Khách thường xuyên
    3. Occasional - Khách thỉnh thoảng
    4. New/Trial - Khách mới
    """

    def __init__(self, n_clusters: int = 4):
        self.n_clusters = n_clusters
        self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        self.customer_segments = {}

    def segment_customers(self,
                         orders_df: pd.DataFrame,
                         users_df: pd.DataFrame) -> Dict[str, str]:
        """
        Phân khách hàng thành segments

        Returns:
            {
                "user_id_1": "VIP",
                "user_id_2": "REGULAR",
                ...
            }
        """
        # Calculate RFM metrics for each customer
        customer_metrics = self._calculate_rfm(orders_df, users_df)

        if customer_metrics.empty:
            return {}

        # Prepare features for clustering
        features = ['recency', 'frequency', 'monetary', 'avg_order_value']
        X = customer_metrics[features].fillna(0)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Perform clustering
        customer_metrics['cluster'] = self.kmeans_model.fit_predict(X_scaled)

        # Analyze clusters and assign meaningful labels
        cluster_analysis = self._analyze_clusters(customer_metrics)

        # Map clusters to segments
        customer_metrics['segment'] = customer_metrics['cluster'].map(
            cluster_analysis['cluster_to_segment']
        )

        # Create segment dictionary
        self.customer_segments = dict(
            zip(customer_metrics['user_id'], customer_metrics['segment'])
        )

        # Store detailed metrics for each customer
        self.customer_details = customer_metrics.set_index('user_id').to_dict('index')

        return self.customer_segments

    def _calculate_rfm(self,
                      orders_df: pd.DataFrame,
                      users_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RFM (Recency, Frequency, Monetary) + Additional metrics
        """
        current_date = datetime.now()

        # Flatten order items
        flattened_orders = []
        for _, order in orders_df.iterrows():
            order_total = 0
            if 'orderItems' in order and isinstance(order['orderItems'], list):
                for item in order['orderItems']:
                    if isinstance(item, dict):
                        order_total += item.get('total', 0)

            flattened_orders.append({
                'user_id': str(order['userId']),
                'order_date': pd.to_datetime(order['createdAt']),
                'order_total': order_total,
                'order_id': order['_id']
            })

        orders_flat = pd.DataFrame(flattened_orders)

        if orders_flat.empty:
            return pd.DataFrame()

        # Calculate RFM metrics
        rfm = orders_flat.groupby('user_id').agg({
            'order_date': lambda x: (current_date - x.max()).days,  # Recency
            'order_id': 'count',  # Frequency
            'order_total': ['sum', 'mean']  # Monetary
        }).reset_index()

        rfm.columns = ['user_id', 'recency', 'frequency', 'monetary', 'avg_order_value']

        # Additional metrics
        # Calculate customer lifetime (days since first order)
        first_order = orders_flat.groupby('user_id')['order_date'].min()
        rfm['lifetime_days'] = rfm['user_id'].map(
            lambda x: (current_date - first_order.get(x, current_date)).days
        )

        # Purchase frequency (orders per month)
        rfm['orders_per_month'] = rfm.apply(
            lambda row: row['frequency'] / max(row['lifetime_days'] / 30, 1),
            axis=1
        )

        # Customer Lifetime Value estimate
        rfm['estimated_clv'] = rfm['avg_order_value'] * rfm['orders_per_month'] * 12

        return rfm

    def _analyze_clusters(self, customer_metrics: pd.DataFrame) -> Dict:
        """
        Analyze clusters and assign meaningful segment names
        """
        cluster_stats = customer_metrics.groupby('cluster').agg({
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': 'mean',
            'avg_order_value': 'mean',
            'estimated_clv': 'mean'
        }).round(2)

        # Assign segment names based on characteristics
        cluster_to_segment = {}

        for cluster in range(self.n_clusters):
            stats = cluster_stats.loc[cluster]

            # Decision logic for segment assignment
            if stats['frequency'] >= 10 and stats['monetary'] >= 500000:
                segment = "VIP"  # High frequency, high value
            elif stats['frequency'] >= 5 and stats['recency'] <= 60:
                segment = "REGULAR"  # Regular buyers, recent
            elif stats['frequency'] >= 2:
                segment = "OCCASIONAL"  # Occasional buyers
            else:
                segment = "NEW"  # New or trial customers

            cluster_to_segment[cluster] = segment

        return {
            'cluster_stats': cluster_stats,
            'cluster_to_segment': cluster_to_segment
        }

    def get_customer_segment(self, user_id: str) -> str:
        """Get segment for a specific customer"""
        return self.customer_segments.get(user_id, "UNKNOWN")

    def get_customer_details(self, user_id: str) -> Dict:
        """Get detailed metrics for a customer"""
        return self.customer_details.get(user_id, {})

    def get_segment_statistics(self) -> Dict:
        """Get statistics for each segment"""
        segment_counts = {}
        for segment in self.customer_segments.values():
            segment_counts[segment] = segment_counts.get(segment, 0) + 1

        return {
            'segment_distribution': segment_counts,
            'total_customers': len(self.customer_segments)
        }

```

---

### 3️⃣ PERSONALIZED DYNAMIC PRICING (Giá động theo khách)

**Mục tiêu:** Áp dụng giá khác nhau cho từng segment khách hàng

```python
# File: infrastructure/ml_models/personalized_pricing.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PersonalizedDynamicPricing:
    """
    Dynamic Pricing thông minh - Bảo vệ khách trung thành

    Core Principle:
    - VIP customers: Best prices, exclusive early access
    - Regular customers: Loyalty discounts
    - Occasional customers: Targeted promotions
    - New customers: Trial offers
    """

    def __init__(self,
                 elasticity_calculator,
                 customer_segmentation):
        self.elasticity = elasticity_calculator
        self.segmentation = customer_segmentation

        # Pricing rules by segment
        self.segment_pricing_rules = {
            "VIP": {
                "max_increase": 0.00,  # NEVER increase for VIP
                "discount_range": (0.05, 0.15),  # 5-15% discount
                "price_lock": True,  # Lock price for loyalty
                "early_access": True,  # Early access to new products
                "priority": "HIGHEST"
            },
            "REGULAR": {
                "max_increase": 0.05,  # Max 5% increase
                "discount_range": (0.03, 0.10),  # 3-10% discount
                "price_lock": False,
                "early_access": True,
                "priority": "HIGH"
            },
            "OCCASIONAL": {
                "max_increase": 0.10,  # Max 10% increase
                "discount_range": (0.00, 0.05),  # 0-5% discount
                "price_lock": False,
                "early_access": False,
                "priority": "MEDIUM"
            },
            "NEW": {
                "max_increase": 0.15,  # Max 15% increase
                "discount_range": (0.10, 0.20),  # 10-20% first order discount
                "price_lock": False,
                "early_access": False,
                "priority": "LOW"
            }
        }

    def calculate_personalized_price(self,
                                    product_id: str,
                                    user_id: str,
                                    base_price: float,
                                    event_context: Optional[Dict] = None) -> Dict:
        """
        Tính giá cá nhân hóa cho khách hàng

        Args:
            product_id: ID sản phẩm
            user_id: ID khách hàng
            base_price: Giá gốc
            event_context: Context về sự kiện (Valentine, Christmas, etc.)

        Returns:
            {
                "user_id": "xxx",
                "product_id": "yyy",
                "base_price": 20000,
                "personalized_price": 18000,
                "discount_amount": 2000,
                "discount_percentage": 10,
                "segment": "VIP",
                "pricing_strategy": "loyalty_reward",
                "explanation": "Giá ưu đãi dành riêng cho khách hàng VIP"
            }
        """

        # Get customer segment
        segment = self.segmentation.get_customer_segment(user_id)
        if segment == "UNKNOWN":
            segment = "NEW"  # Default to NEW for unknown customers

        # Get pricing rules for this segment
        rules = self.segment_pricing_rules[segment]

        # Get product elasticity
        elasticity_info = self.elasticity.recommend_price_change(
            product_id, base_price
        )

        # Calculate optimal price based on segment and elasticity
        optimal_price = self._calculate_optimal_price(
            base_price=base_price,
            segment=segment,
            rules=rules,
            elasticity_info=elasticity_info,
            event_context=event_context
        )

        # Calculate discount
        discount_amount = base_price - optimal_price
        discount_pct = (discount_amount / base_price) * 100

        # Generate strategy explanation
        strategy, explanation = self._generate_strategy_explanation(
            segment=segment,
            discount_pct=discount_pct,
            elasticity_info=elasticity_info,
            event_context=event_context
        )

        return {
            "user_id": user_id,
            "product_id": product_id,
            "segment": segment,
            "base_price": base_price,
            "personalized_price": optimal_price,
            "discount_amount": discount_amount,
            "discount_percentage": round(discount_pct, 2),
            "pricing_strategy": strategy,
            "explanation": explanation,
            "price_locked": rules["price_lock"],
            "priority": rules["priority"],
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_optimal_price(self,
                                base_price: float,
                                segment: str,
                                rules: Dict,
                                elasticity_info: Dict,
                                event_context: Optional[Dict]) -> float:
        """Calculate optimal price based on all factors"""

        # Start with base price
        optimal_price = base_price

        # VIP: NEVER increase, always discount
        if segment == "VIP":
            discount_pct = np.random.uniform(*rules["discount_range"])
            optimal_price = base_price * (1 - discount_pct)
            return optimal_price

        # Regular: Small increases allowed, but prefer discounts
        if segment == "REGULAR":
            # Check if product is price sensitive
            if elasticity_info.get("sensitivity") in ["VERY_SENSITIVE", "SENSITIVE"]:
                # Give discount for sensitive products
                discount_pct = np.random.uniform(*rules["discount_range"])
                optimal_price = base_price * (1 - discount_pct)
            else:
                # Small increase possible for non-sensitive products
                # But still offer some discount to maintain loyalty
                discount_pct = np.random.uniform(0.02, 0.05)  # 2-5% discount
                optimal_price = base_price * (1 - discount_pct)
            return optimal_price

        # Occasional: Can increase for non-sensitive products
        if segment == "OCCASIONAL":
            if elasticity_info.get("sensitivity") == "INSENSITIVE":
                # Can increase price slightly
                increase_pct = np.random.uniform(0.00, rules["max_increase"])
                optimal_price = base_price * (1 + increase_pct)
            else:
                # Keep base price or small discount
                discount_pct = np.random.uniform(0.00, 0.03)
                optimal_price = base_price * (1 - discount_pct)
            return optimal_price

        # New: Aggressive discounts to acquire
        if segment == "NEW":
            discount_pct = np.random.uniform(*rules["discount_range"])
            optimal_price = base_price * (1 - discount_pct)
            return optimal_price

        return optimal_price

    def _generate_strategy_explanation(self,
                                      segment: str,
                                      discount_pct: float,
                                      elasticity_info: Dict,
                                      event_context: Optional[Dict]) -> tuple:
        """Generate human-readable strategy explanation"""

        if segment == "VIP":
            strategy = "loyalty_premium_protection"
            explanation = (
                f"🌟 Giá ưu đãi đặc biệt dành cho khách hàng VIP. "
                f"Giảm {abs(discount_pct):.0f}% - Cảm ơn sự ủng hộ của bạn!"
            )

        elif segment == "REGULAR":
            strategy = "loyalty_retention"
            if discount_pct > 0:
                explanation = (
                    f"💝 Ưu đãi khách hàng thân thiết - Giảm {discount_pct:.0f}%. "
                    f"Giá luôn tốt nhất dành cho bạn!"
                )
            else:
                explanation = (
                    f"✨ Giá đặc biệt cho khách quen. "
                    f"Chúng tôi cam kết giữ giá ổn định cho bạn!"
                )

        elif segment == "OCCASIONAL":
            strategy = "conversion_optimization"
            if discount_pct > 0:
                explanation = (
                    f"🎁 Ưu đãi đặc biệt hôm nay - Giảm {discount_pct:.0f}%. "
                    f"Đừng bỏ lỡ!"
                )
            elif discount_pct < -5:  # Price increase
                explanation = (
                    f"📈 Giá điều chỉnh theo thị trường. "
                    f"Đặt hàng ngay để nhận ưu đãi tốt nhất!"
                )
            else:
                explanation = "💰 Giá tốt nhất hiện tại!"

        else:  # NEW
            strategy = "customer_acquisition"
            explanation = (
                f"🎉 Chào mừng khách hàng mới! "
                f"Giảm {discount_pct:.0f}% cho đơn hàng đầu tiên. "
                f"Trải nghiệm ngay!"
            )

        return strategy, explanation

    def generate_pricing_strategy_for_event(self,
                                          event_name: str,
                                          products_df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive pricing strategy for an event

        Args:
            event_name: Valentine, Christmas, Tet, etc.
            products_df: DataFrame of products

        Returns:
            Pricing strategy for all segments
        """

        event_strategies = {
            "valentine": {
                "target_products": ["cake", "chocolate", "heart", "love"],
                "vip_discount": 0.10,  # 10% for VIP
                "regular_discount": 0.05,  # 5% for Regular
                "occasional_discount": 0.00,  # No discount, can increase
                "new_discount": 0.15  # 15% for new customers
            },
            "christmas": {
                "target_products": ["christmas", "xmas", "holiday", "cake"],
                "vip_discount": 0.12,
                "regular_discount": 0.08,
                "occasional_discount": 0.00,
                "new_discount": 0.20
            },
            "tet": {
                "target_products": ["tet", "banh", "traditional"],
                "vip_discount": 0.15,
                "regular_discount": 0.10,
                "occasional_discount": 0.05,
                "new_discount": 0.20
            }
        }

        event_config = event_strategies.get(event_name.lower(), {})

        if not event_config:
            logger.warning(f"No strategy defined for event: {event_name}")
            return {}

        # Generate strategy
        strategy = {
            "event_name": event_name,
            "event_date": datetime.now().isoformat(),
            "strategies_by_segment": {},
            "product_recommendations": []
        }

        # For each segment
        for segment in ["VIP", "REGULAR", "OCCASIONAL", "NEW"]:
            discount_key = f"{segment.lower()}_discount"
            discount = event_config.get(discount_key, 0)

            strategy["strategies_by_segment"][segment] = {
                "discount_percentage": discount * 100,
                "messaging": self._get_event_messaging(event_name, segment, discount),
                "priority": self.segment_pricing_rules[segment]["priority"]
            }

        # Identify target products
        target_keywords = event_config.get("target_products", [])
        for _, product in products_df.iterrows():
            product_name = product.get('productName', '').lower()

            if any(keyword in product_name for keyword in target_keywords):
                strategy["product_recommendations"].append({
                    "product_id": product['_id'],
                    "product_name": product.get('productName'),
                    "base_price": product.get('productPrice', 0),
                    "recommendation": "Featured product for event"
                })

        return strategy

    def _get_event_messaging(self, event_name: str, segment: str, discount: float) -> str:
        """Generate event-specific messaging"""

        messages = {
            "valentine": {
                "VIP": f"💕 Dành tặng khách VIP - Giảm {discount*100:.0f}% cho Valentine ngọt ngào",
                "REGULAR": f"💝 Ưu đãi Valentine cho khách quen - Giảm {discount*100:.0f}%",
                "OCCASIONAL": f"💖 Valentine Sale - Đặt ngay!",
                "NEW": f"🎁 Chào mừng! Giảm {discount*100:.0f}% mùa Valentine"
            },
            "christmas": {
                "VIP": f"🎄 Giảng sinh an lành - Ưu đãi VIP {discount*100:.0f}%",
                "REGULAR": f"🎅 Khách quen thân thiết - Giảm {discount*100:.0f}%",
                "OCCASIONAL": f"🎁 Christmas Sale đặc biệt!",
                "NEW": f"🌟 Chào mừng Giáng sinh - Giảm {discount*100:.0f}%"
            }
        }

        return messages.get(event_name.lower(), {}).get(segment, "")

```

---

### 4️⃣ SIMULATION & A/B TESTING (Mô phỏng)

```python
# File: infrastructure/ml_models/pricing_simulation.py

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class PricingSimulator:
    """
    Mô phỏng impact của pricing strategy trước khi apply

    Giúp trả lời:
    - Nếu tăng giá X%, doanh thu thay đổi thế nào?
    - Có bao nhiêu khách VIP bị ảnh hưởng?
    - ROI của chiến dịch khuyến mãi?
    """

    def __init__(self,
                 elasticity_calculator,
                 customer_segmentation):
        self.elasticity = elasticity_calculator
        self.segmentation = customer_segmentation

    def simulate_price_change(self,
                             product_id: str,
                             current_price: float,
                             new_price: float,
                             orders_df: pd.DataFrame) -> Dict:
        """
        Simulate impact of price change

        Returns:
            {
                "current_metrics": {
                    "avg_units_sold": 100,
                    "revenue": 2000000,
                    "customers_affected": 50
                },
                "predicted_metrics": {
                    "avg_units_sold": 85,  # -15% due to price increase
                    "revenue": 2125000,  # +6.25% despite lower volume
                    "customers_affected": 50,
                    "vip_customers_affected": 5
                },
                "impact": {
                    "revenue_change": 125000,
                    "revenue_change_pct": 6.25,
                    "volume_change": -15,
                    "volume_change_pct": -15.0,
                    "risk_level": "MEDIUM"
                },
                "recommendation": "Safe to proceed with caution"
            }
        """

        # Calculate price change percentage
        price_change_pct = ((new_price - current_price) / current_price) * 100

        # Get elasticity
        if product_id in self.elasticity.product_elasticity:
            elasticity = self.elasticity.product_elasticity[product_id]
        else:
            elasticity = -1.0  # Default moderate elasticity

        # Get current metrics
        current_metrics = self._get_current_metrics(product_id, orders_df)

        # Predict demand change using elasticity
        demand_change_pct = elasticity * price_change_pct
        predicted_units = current_metrics['avg_units_sold'] * (1 + demand_change_pct / 100)
        predicted_revenue = predicted_units * new_price

        # Analyze customer impact
        customer_impact = self._analyze_customer_impact(
            product_id, orders_df, price_change_pct
        )

        # Calculate overall impact
        revenue_change = predicted_revenue - current_metrics['revenue']
        revenue_change_pct = (revenue_change / current_metrics['revenue']) * 100
        volume_change = predicted_units - current_metrics['avg_units_sold']
        volume_change_pct = (volume_change / current_metrics['avg_units_sold']) * 100

        # Assess risk
        risk_level = self._assess_risk(
            price_change_pct=price_change_pct,
            elasticity=elasticity,
            vip_affected=customer_impact['vip_customers'],
            revenue_change_pct=revenue_change_pct
        )

        return {
            "product_id": product_id,
            "price_change_pct": round(price_change_pct, 2),
            "current_metrics": current_metrics,
            "predicted_metrics": {
                "avg_units_sold": round(predicted_units, 2),
                "revenue": round(predicted_revenue, 2),
                "customers_affected": customer_impact['total_customers'],
                "vip_customers_affected": customer_impact['vip_customers'],
                "regular_customers_affected": customer_impact['regular_customers']
            },
            "impact": {
                "revenue_change": round(revenue_change, 2),
                "revenue_change_pct": round(revenue_change_pct, 2),
                "volume_change": round(volume_change, 2),
                "volume_change_pct": round(volume_change_pct, 2),
                "elasticity": elasticity,
                "risk_level": risk_level
            },
            "customer_segments_impact": customer_impact,
            "recommendation": self._get_recommendation(risk_level, revenue_change_pct)
        }

    def _get_current_metrics(self, product_id: str, orders_df: pd.DataFrame) -> Dict:
        """Calculate current performance metrics"""

        # Flatten orders
        flattened = []
        for _, order in orders_df.iterrows():
            if 'orderItems' in order and isinstance(order['orderItems'], list):
                for item in order['orderItems']:
                    if isinstance(item, dict) and str(item.get('product', '')) == product_id:
                        flattened.append({
                            'user_id': str(order['userId']),
                            'quantity': item.get('quantity', 0),
                            'total': item.get('total', 0)
                        })

        if not flattened:
            return {
                'avg_units_sold': 0,
                'revenue': 0,
                'customers_affected': 0
            }

        df = pd.DataFrame(flattened)

        return {
            'avg_units_sold': df['quantity'].sum(),
            'revenue': df['total'].sum(),
            'customers_affected': df['user_id'].nunique()
        }

    def _analyze_customer_impact(self,
                                 product_id: str,
                                 orders_df: pd.DataFrame,
                                 price_change_pct: float) -> Dict:
        """Analyze which customer segments are affected"""

        # Get customers who bought this product
        affected_users = set()
        for _, order in orders_df.iterrows():
            if 'orderItems' in order and isinstance(order['orderItems'], list):
                for item in order['orderItems']:
                    if isinstance(item, dict) and str(item.get('product', '')) == product_id:
                        affected_users.add(str(order['userId']))

        # Count by segment
        segment_counts = {
            'VIP': 0,
            'REGULAR': 0,
            'OCCASIONAL': 0,
            'NEW': 0
        }

        for user_id in affected_users:
            segment = self.segmentation.get_customer_segment(user_id)
            if segment in segment_counts:
                segment_counts[segment] += 1

        return {
            'total_customers': len(affected_users),
            'vip_customers': segment_counts['VIP'],
            'regular_customers': segment_counts['REGULAR'],
            'occasional_customers': segment_counts['OCCASIONAL'],
            'new_customers': segment_counts['NEW'],
            'segment_breakdown': segment_counts
        }

    def _assess_risk(self,
                    price_change_pct: float,
                    elasticity: float,
                    vip_affected: int,
                    revenue_change_pct: float) -> str:
        """Assess risk level of pricing change"""

        # High risk conditions
        if vip_affected > 10 and price_change_pct > 10:
            return "HIGH"  # Too many VIPs affected by large increase

        if elasticity < -1.5 and price_change_pct > 5:
            return "HIGH"  # Very elastic product with price increase

        if revenue_change_pct < -5:
            return "HIGH"  # Significant revenue loss

        # Medium risk conditions
        if vip_affected > 5 and price_change_pct > 5:
            return "MEDIUM"

        if elasticity < -1.0 and price_change_pct > 10:
            return "MEDIUM"

        if revenue_change_pct < 0:
            return "MEDIUM"  # Any revenue loss

        # Low risk
        return "LOW"

    def _get_recommendation(self, risk_level: str, revenue_change_pct: float) -> str:
        """Generate recommendation based on simulation"""

        if risk_level == "HIGH":
            return (
                "⚠️ KHÔNG NÊN THỰC HIỆN - Rủi ro cao mất khách VIP hoặc giảm doanh thu. "
                "Cân nhắc giảm mức tăng giá hoặc kết hợp voucher cho khách quen."
            )

        if risk_level == "MEDIUM":
            return (
                "⚠️ CẨN THẬN - Có rủi ro vừa phải. "
                "Nên test A/B với một phần khách hàng trước. "
                "Chuẩn bị voucher bù đắp cho khách VIP/Regular."
            )

        return (
            f"✅ AN TOÀN - Dự kiến tăng doanh thu {revenue_change_pct:.1f}%. "
            f"Có thể thực hiện nhưng vẫn nên monitor phản hồi khách hàng."
        )

```

---

## 📈 IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1-2) ✅ CÓ THỂ BẮT ĐẦU NGAY

```python
# Đã có sẵn:
✅ MongoDB connection
✅ Orders, Products, Users data
✅ Dynamic Pricing Model (cơ bản)

# Cần bổ sung:
1. Price Elasticity Calculator
2. Customer Segmentation
3. Personalized Pricing Engine
```

### Phase 2: Core Features (Week 3-4)

```python
1. Implement Price Elasticity Calculator
2. Implement Customer Segmentation (RFM)
3. Integrate với existing Dynamic Pricing
4. Create API endpoints
```

### Phase 3: Advanced Features (Week 5-6)

```python
1. Pricing Simulation
2. A/B Testing framework
3. Event-based pricing strategies
4. Voucher generation system
```

### Phase 4: Monitoring & Learning (Week 7-8)

```python
1. Customer behavior tracking
2. Feedback loop for ML models
3. Dashboard & Analytics
4. Automated alerts
```

---

## 🎯 API ENDPOINTS ĐỀ XUẤT

```python
# File: app/routers/personalized_pricing.py

from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/personalized-pricing", tags=["Personalized Pricing"])

@router.post("/calculate-price")
async def calculate_personalized_price(
    product_id: str,
    user_id: str,
    event: Optional[str] = None
):
    """
    Tính giá cá nhân hóa cho một khách hàng

    Example:
    {
        "product_id": "product_123",
        "user_id": "user_456",
        "event": "valentine"
    }

    Response:
    {
        "user_id": "user_456",
        "segment": "VIP",
        "base_price": 20000,
        "personalized_price": 18000,
        "discount_percentage": 10,
        "explanation": "Giá ưu đãi dành riêng cho khách hàng VIP"
    }
    """
    pass

@router.get("/customer-segment/{user_id}")
async def get_customer_segment(user_id: str):
    """
    Lấy segment của khách hàng

    Response:
    {
        "user_id": "user_456",
        "segment": "VIP",
        "metrics": {
            "recency": 5,
            "frequency": 15,
            "monetary": 1500000,
            "avg_order_value": 100000,
            "estimated_clv": 1200000
        }
    }
    """
    pass

@router.post("/simulate-price-change")
async def simulate_price_change(
    product_id: str,
    current_price: float,
    new_price: float
):
    """
    Mô phỏng impact của thay đổi giá

    Response:
    {
        "price_change_pct": 10,
        "predicted_revenue_change": 125000,
        "customers_affected": {
            "vip": 5,
            "regular": 20,
            "occasional": 15
        },
        "risk_level": "MEDIUM",
        "recommendation": "Cẩn thận - Chuẩn bị voucher cho VIP"
    }
    """
    pass

@router.get("/event-strategy/{event_name}")
async def get_event_pricing_strategy(event_name: str):
    """
    Lấy chiến lược pricing cho sự kiện

    Example: /event-strategy/valentine

    Response:
    {
        "event_name": "valentine",
        "strategies_by_segment": {
            "VIP": {"discount": 10, "messaging": "..."},
            "REGULAR": {"discount": 5, "messaging": "..."}
        },
        "featured_products": [...]
    }
    """
    pass

@router.get("/price-elasticity/{product_id}")
async def get_price_elasticity(product_id: str):
    """
    Lấy độ nhạy giá của sản phẩm

    Response:
    {
        "product_id": "product_123",
        "elasticity": -1.2,
        "sensitivity": "SENSITIVE",
        "can_increase": false,
        "max_safe_increase": 5,
        "recommendation": "Không nên tăng giá - sản phẩm nhạy cảm"
    }
    """
    pass
```

---

## 💡 REAL-WORLD EXAMPLE

### Case Study: Bánh Su 20k

**Scenario hiện tại:**

- Bánh su giá: 20,000đ
- Khách quen A (VIP): Mua 2 tuần/lần, đã mua 20 lần
- Hệ thống dynamic pricing muốn tăng lên 25,000đ (25%)

**Without Personalized Pricing:**

```
❌ Khách A thấy giá: 25,000đ (+25%)
❌ Khách A cảm thấy: "Giá tăng quá cao!"
❌ Khách A không mua nữa
❌ Mất khách trung thành
```

**With Personalized Pricing:**

```
✅ System nhận diện: Khách A là VIP
✅ Khách A thấy giá: 18,000đ (-10% loyalty discount)
✅ Khách A cảm thấy: "Được trân trọng!"
✅ Khách A tiếp tục mua
✅ Khách occasional thấy giá: 25,000đ (họ chấp nhận được)
✅ Revenue optimization + Customer retention
```

---

## 🚀 NEXT STEPS

### 1. Tạo file structure mới

```
RCM_PRICE/
├── infrastructure/
│   └── ml_models/
│       ├── price_elasticity.py         # NEW
│       ├── customer_segmentation.py     # NEW
│       ├── personalized_pricing.py      # NEW
│       └── pricing_simulation.py        # NEW
├── app/
│   └── routers/
│       └── personalized_pricing.py      # NEW
```

### 2. Update existing services

```python
# application/services/hybrid_recommender.py
# Tích hợp personalized pricing vào hybrid system
```

### 3. Test với data thật

```python
# Chạy trên MongoDB data hiện tại
# Phân tích khách hàng thực tế
# Mô phỏng các scenarios
```

---

## ✨ TÓM TẮT

### ✅ Flow của bạn HOÀN TOÀN KHẢ THI vì:

1. **Có đủ data**: MongoDB đã có orders, users, products
2. **Có infrastructure**: Dynamic pricing đã có sẵn
3. **Có ML capability**: TF Recommenders, HuggingFace sẵn sàng
4. **Logic rõ ràng**: 6 bước của bạn là best practice

### 🎯 Key Success Factors:

1. **ALWAYS protect VIP customers** - Họ là 20% khách mang 80% revenue
2. **Gradual price changes** - Không tăng đột ngột
3. **Clear communication** - Giải thích rõ ràng về giá
4. **Voucher compensation** - Bù đắp cho khách bị ảnh hưởng
5. **Continuous monitoring** - Theo dõi phản hồi real-time

### 💪 Advantages của approach này:

- Khoa học (ML-based)
- Bảo vệ khách trung thành
- Tăng revenue sustainably
- Có thể scale
- Measurable impact

---

Bạn muốn tôi implement các module này luôn không? 🚀
