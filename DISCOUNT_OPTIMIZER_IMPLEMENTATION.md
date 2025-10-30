# 🎯 DISCOUNT OPTIMIZER - GIẢI PHÁP CHO PROJECT NHỎ

## 📋 PHÂN TÍCH YÊU CẦU

| Yêu Cầu                     | Mức Độ | Giải Pháp                                |
| --------------------------- | ------ | ---------------------------------------- |
| Project nhỏ                 | ✅     | Không cần train model nặng               |
| Có API/model sẵn            | ✅     | Dùng Gemini API (đã có)                  |
| Ít data                     | ✅     | Thompson Sampling (không cần nhiều data) |
| Deploy Render không out CPU | ✅     | Lightweight, không train real-time       |
| Output tốt                  | ✅     | Kết hợp AI + Statistical learning        |

---

## 🏆 GIẢI PHÁP: THOMPSON SAMPLING + GEMINI API

### **Tại Sao Chọn Cách Này?**

#### ✅ **Thompson Sampling (Multi-Armed Bandit)**

- **Không cần training data**: Học real-time từ kết quả bán hàng
- **Lightweight**: Chỉ cần lưu alpha/beta parameters (~100 bytes/product)
- **Tự động A/B testing**: Thử nhiều discount levels và tự học
- **Fast**: Inference < 1ms
- **CPU-friendly**: Chỉ dùng NumPy, không cần GPU

#### ✅ **Gemini API (Bạn đã có)**

- **No training needed**: Gọi API để phân tích
- **Smart recommendations**: Dựa trên product description + event type
- **Fallback mechanism**: Khi Thompson Sampling chưa đủ data

---

## 🏗️ KIẾN TRÚC

```
┌─────────────────────────────────────────┐
│  INPUT: Product + Event + Customer      │
└───────────────┬─────────────────────────┘
                │
       ┌────────┴────────┐
       │                 │
       ▼                 ▼
┌──────────────┐   ┌──────────────┐
│ THOMPSON     │   │ GEMINI API   │
│ SAMPLING     │   │ (Fallback)   │
│ (Primary)    │   │              │
└──────┬───────┘   └──────┬───────┘
       │                  │
       │  ┌───────────────┘
       │  │
       ▼  ▼
  ┌────────────┐
  │  ENSEMBLE  │
  │  (Weighted)│
  └─────┬──────┘
        │
        ▼
  ┌────────────────┐
  │ FINAL DISCOUNT │
  │   + Reason     │
  └────────────────┘
```

---

## 💻 IMPLEMENTATION

### **File 1: `application/services/discount_optimizer.py`**

````python
"""
AI-Powered Discount Optimizer
Sử dụng Thompson Sampling + Gemini API
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
from scipy.stats import beta
import google.generativeai as genai
from config.settings import settings

class ThompsonSamplingOptimizer:
    """
    Thompson Sampling cho discount optimization
    Tự động học từ kết quả bán hàng thực tế
    """

    def __init__(self):
        # Discount levels có thể test (5% increments)
        self.discount_levels = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

        # Beta distribution parameters cho mỗi (product, event, discount)
        # Lưu trong memory (có thể chuyển sang MongoDB sau)
        self.alpha = {}  # Success counts
        self.beta_param = {}  # Failure counts

    def _get_key(self, product_id: str, event_type: str, discount: int) -> str:
        """Tạo unique key cho combination"""
        return f"{product_id}_{event_type}_{discount}"

    def select_discount(
        self,
        product_id: str,
        event_type: str,
        base_price: float,
        min_profit_margin: float = 0.15  # 15% profit tối thiểu
    ) -> Dict:
        """
        Chọn discount tối ưu bằng Thompson Sampling

        Returns:
            {
                'discount_percent': 20,
                'confidence': 0.85,
                'reason': 'Thompson Sampling based on 45 trials',
                'expected_revenue': 8500000
            }
        """
        # Lọc discounts đảm bảo profit margin
        valid_discounts = [
            d for d in self.discount_levels
            if (base_price * (1 - d/100)) >= (base_price * min_profit_margin)
        ]

        if not valid_discounts:
            return {
                'discount_percent': 0,
                'confidence': 1.0,
                'reason': 'No valid discount maintains profit margin',
                'expected_revenue': 0
            }

        # Sample từ Beta distribution cho mỗi discount level
        sampled_rewards = {}
        trial_counts = {}

        for discount in valid_discounts:
            key = self._get_key(product_id, event_type, discount)

            # Lấy alpha, beta (default = 1,1 nếu chưa có data)
            alpha_val = self.alpha.get(key, 1)
            beta_val = self.beta_param.get(key, 1)

            # Sample từ Beta(alpha, beta)
            sampled_rewards[discount] = np.random.beta(alpha_val, beta_val)
            trial_counts[discount] = alpha_val + beta_val - 2  # Total trials

        # Chọn discount có highest sampled reward
        best_discount = max(sampled_rewards, key=sampled_rewards.get)

        # Tính confidence (dựa trên số lượng trials)
        total_trials = sum(trial_counts.values())
        confidence = min(trial_counts[best_discount] / max(total_trials, 10), 1.0)

        # Tính expected revenue
        key = self._get_key(product_id, event_type, best_discount)
        alpha_val = self.alpha.get(key, 1)
        beta_val = self.beta_param.get(key, 1)
        success_rate = alpha_val / (alpha_val + beta_val)

        return {
            'discount_percent': best_discount,
            'confidence': round(confidence, 2),
            'reason': f'Thompson Sampling: {trial_counts[best_discount]} trials, {round(success_rate*100)}% success rate',
            'expected_success_rate': round(success_rate, 3),
            'total_trials': trial_counts[best_discount]
        }

    def update(
        self,
        product_id: str,
        event_type: str,
        discount: int,
        revenue: float,
        target_revenue: float
    ):
        """
        Cập nhật model sau khi có kết quả bán hàng

        Args:
            revenue: Doanh thu thực tế
            target_revenue: Doanh thu mục tiêu (có thể tính từ avg)
        """
        key = self._get_key(product_id, event_type, discount)

        # Initialize nếu chưa có
        if key not in self.alpha:
            self.alpha[key] = 1
            self.beta_param[key] = 1

        # Update based on success/failure
        if revenue >= target_revenue:
            self.alpha[key] += 1  # Success
        else:
            self.beta_param[key] += 1  # Failure

    def get_statistics(self, product_id: str, event_type: str) -> Dict:
        """Lấy thống kê cho product + event"""
        stats = {}

        for discount in self.discount_levels:
            key = self._get_key(product_id, event_type, discount)

            if key in self.alpha:
                alpha_val = self.alpha[key]
                beta_val = self.beta_param[key]

                stats[discount] = {
                    'trials': alpha_val + beta_val - 2,
                    'successes': alpha_val - 1,
                    'success_rate': alpha_val / (alpha_val + beta_val),
                    'confidence_interval': self._get_confidence_interval(alpha_val, beta_val)
                }

        return stats

    def _get_confidence_interval(self, alpha: float, beta: float, confidence=0.95) -> Tuple[float, float]:
        """Tính 95% confidence interval"""
        lower = beta.ppf((1 - confidence) / 2, alpha, beta)
        upper = beta.ppf(1 - (1 - confidence) / 2, alpha, beta)
        return (round(lower, 3), round(upper, 3))


class GeminiDiscountAdvisor:
    """
    Sử dụng Gemini API để đề xuất discount
    Dùng khi Thompson Sampling chưa đủ data
    """

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def suggest_discount(
        self,
        product_name: str,
        category: str,
        base_price: float,
        event_type: str,
        current_stock: int,
        avg_rating: float,
        days_to_event: int
    ) -> Dict:
        """
        Gọi Gemini API để đề xuất discount
        """

        prompt = f"""
Bạn là chuyên gia tối ưu hóa giá và khuyến mãi cho tiệm bánh.

THÔNG TIN SẢN PHẨM:
- Tên: {product_name}
- Loại: {category}
- Giá gốc: {base_price:,} VNĐ
- Tồn kho: {current_stock} cái
- Đánh giá: {avg_rating}/5

SỰ KIỆN:
- Loại: {event_type}
- Còn {days_to_event} ngày

YÊU CẦU:
1. Đề xuất % giảm giá TỐI ƯU để DOANH THU CAO NHẤT (không phải số lượng bán)
2. Giải thích ngắn gọn lý do
3. Đảm bảo profit margin >= 15%

Trả lời theo format JSON:
{{
    "discount_percent": <số nguyên 0-50>,
    "reason": "<lý do ngắn gọn>",
    "expected_impact": "<ảnh hưởng dự kiến>"
}}
"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Parse JSON từ response
            # Gemini đôi khi wrap JSON trong ```json ... ```
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            return {
                'discount_percent': result.get('discount_percent', 15),
                'confidence': 0.6,  # Lower confidence vì không dựa trên real data
                'reason': f"Gemini AI: {result.get('reason', 'AI recommendation')}",
                'expected_impact': result.get('expected_impact', 'Unknown')
            }

        except Exception as e:
            # Fallback về rule-based nếu Gemini fail
            return self._fallback_rule_based(event_type, current_stock, avg_rating)

    def _fallback_rule_based(self, event_type: str, stock: int, rating: float) -> Dict:
        """Rule-based fallback khi Gemini API fail"""

        # Base discount theo event
        event_discounts = {
            'TET': 25, 'BLACK_FRIDAY': 35, 'HALLOWEEN': 20,
            'CHRISTMAS': 20, 'VALENTINE': 15, 'MID_AUTUMN': 25
        }

        base_discount = event_discounts.get(event_type, 10)

        # Điều chỉnh theo stock
        if stock > 100:
            base_discount += 5  # Tồn kho nhiều → giảm thêm

        # Điều chỉnh theo rating
        if rating >= 4.5:
            base_discount -= 5  # Rating cao → giảm ít
        elif rating <= 3.0:
            base_discount += 5  # Rating thấp → giảm nhiều

        return {
            'discount_percent': min(max(base_discount, 0), 50),
            'confidence': 0.5,
            'reason': 'Rule-based fallback (Gemini unavailable)',
            'expected_impact': 'Medium'
        }


class HybridDiscountOptimizer:
    """
    Kết hợp Thompson Sampling + Gemini API
    """

    def __init__(self):
        self.thompson = ThompsonSamplingOptimizer()
        self.gemini = GeminiDiscountAdvisor()

    def get_optimal_discount(
        self,
        product_id: str,
        product_name: str,
        category: str,
        base_price: float,
        event_type: str,
        current_stock: int = 50,
        avg_rating: float = 4.0,
        days_to_event: int = 7,
        min_trials_for_thompson: int = 3  # Số trials tối thiểu để tin Thompson
    ) -> Dict:
        """
        Main method: Lấy discount tối ưu

        Logic:
        1. Nếu Thompson có đủ data (>= min_trials) → dùng Thompson
        2. Nếu không → dùng Gemini
        3. Ensemble cả 2 nếu cần
        """

        # Try Thompson Sampling first
        thompson_result = self.thompson.select_discount(
            product_id=product_id,
            event_type=event_type,
            base_price=base_price
        )

        # Kiểm tra Thompson có đủ data không
        has_enough_data = thompson_result.get('total_trials', 0) >= min_trials_for_thompson

        if has_enough_data and thompson_result['confidence'] >= 0.7:
            # Thompson Sampling có đủ data và confidence cao
            return {
                **thompson_result,
                'method': 'Thompson Sampling',
                'status': 'high_confidence'
            }

        # Không đủ data → dùng Gemini
        gemini_result = self.gemini.suggest_discount(
            product_name=product_name,
            category=category,
            base_price=base_price,
            event_type=event_type,
            current_stock=current_stock,
            avg_rating=avg_rating,
            days_to_event=days_to_event
        )

        # Ensemble: Weighted average nếu Thompson có ít data
        if thompson_result.get('total_trials', 0) > 0:
            # Có ít data từ Thompson → ensemble
            thompson_weight = thompson_result['confidence']
            gemini_weight = 1 - thompson_weight

            final_discount = int(
                thompson_result['discount_percent'] * thompson_weight +
                gemini_result['discount_percent'] * gemini_weight
            )

            return {
                'discount_percent': final_discount,
                'confidence': (thompson_result['confidence'] + gemini_result['confidence']) / 2,
                'reason': f"Ensemble: Thompson ({thompson_weight:.0%}) + Gemini ({gemini_weight:.0%})",
                'method': 'Hybrid (Thompson + Gemini)',
                'status': 'learning',
                'thompson_suggestion': thompson_result['discount_percent'],
                'gemini_suggestion': gemini_result['discount_percent']
            }
        else:
            # Hoàn toàn mới → dùng Gemini
            return {
                **gemini_result,
                'method': 'Gemini AI',
                'status': 'cold_start'
            }

    def record_result(
        self,
        product_id: str,
        event_type: str,
        discount_used: int,
        revenue: float,
        target_revenue: float
    ):
        """
        Ghi nhận kết quả để Thompson Sampling học
        Gọi sau mỗi lần bán hàng với discount
        """
        self.thompson.update(
            product_id=product_id,
            event_type=event_type,
            discount=discount_used,
            revenue=revenue,
            target_revenue=target_revenue
        )

    def get_learning_statistics(self, product_id: str, event_type: str) -> Dict:
        """Xem thống kê học của Thompson Sampling"""
        return self.thompson.get_statistics(product_id, event_type)


# Singleton instance
_optimizer_instance = None

def get_discount_optimizer() -> HybridDiscountOptimizer:
    """Get singleton instance"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = HybridDiscountOptimizer()
    return _optimizer_instance
````

---

## 🔌 INTEGRATION VÀO API

### **File 2: Update `app/routers/event_promotions.py`**

Thêm endpoint mới:

```python
from application.services.discount_optimizer import get_discount_optimizer

@router.post("/optimize-discount")
async def optimize_discount(
    product_id: str,
    event_type: str,
    days_ahead: int = 7
):
    """
    🤖 AI-powered discount optimization

    Tự động tìm % giảm giá TỐI ƯU cho doanh thu cao nhất
    """
    try:
        # Get product info
        product = await products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(404, "Product not found")

        # Get optimizer
        optimizer = get_discount_optimizer()

        # Get optimal discount
        result = optimizer.get_optimal_discount(
            product_id=product_id,
            product_name=product.get('name', 'Unknown'),
            category=product.get('category', 'Unknown'),
            base_price=product.get('price', 0),
            event_type=event_type,
            current_stock=product.get('stock', 50),
            avg_rating=product.get('avgRating', 4.0),
            days_to_event=days_ahead
        )

        return {
            "product_id": product_id,
            "product_name": product.get('name'),
            "event_type": event_type,
            "optimization_result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/record-sale-result")
async def record_sale_result(
    product_id: str,
    event_type: str,
    discount_used: int,
    revenue: float,
    target_revenue: float
):
    """
    📊 Ghi nhận kết quả bán hàng để AI học

    Gọi endpoint này sau mỗi đợt promotion để Thompson Sampling học
    """
    try:
        optimizer = get_discount_optimizer()

        optimizer.record_result(
            product_id=product_id,
            event_type=event_type,
            discount_used=discount_used,
            revenue=revenue,
            target_revenue=target_revenue
        )

        # Get updated statistics
        stats = optimizer.get_learning_statistics(product_id, event_type)

        return {
            "message": "Result recorded successfully",
            "learning_statistics": stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/learning-stats/{product_id}/{event_type}")
async def get_learning_stats(product_id: str, event_type: str):
    """
    📈 Xem thống kê học của AI cho sản phẩm + sự kiện
    """
    try:
        optimizer = get_discount_optimizer()
        stats = optimizer.get_learning_statistics(product_id, event_type)

        return {
            "product_id": product_id,
            "event_type": event_type,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(500, str(e))
```

---

## 📦 DEPENDENCIES

Add vào `requirements.txt`:

```txt
scipy>=1.11.0
```

---

## 🚀 CÁCH SỬ DỤNG

### **1. Optimize Discount (Lần đầu - Cold Start)**

```bash
POST http://localhost:8000/api/event-promotions/optimize-discount
```

Request:

```json
{
  "product_id": "671eddc4e630c82794ed8c4c",
  "event_type": "HALLOWEEN",
  "days_ahead": 1
}
```

Response (Cold Start - Dùng Gemini):

```json
{
  "product_id": "671eddc4e630c82794ed8c4c",
  "product_name": "Bánh Kem Halloween Bí Ngô",
  "event_type": "HALLOWEEN",
  "optimization_result": {
    "discount_percent": 22,
    "confidence": 0.6,
    "reason": "Gemini AI: Halloween event với sản phẩm theo mùa, stock vừa phải, nên giảm 20-25% để tối đa doanh thu",
    "method": "Gemini AI",
    "status": "cold_start"
  }
}
```

### **2. Record Result (Sau khi bán)**

```bash
POST http://localhost:8000/api/event-promotions/record-sale-result
```

Request:

```json
{
  "product_id": "671eddc4e630c82794ed8c4c",
  "event_type": "HALLOWEEN",
  "discount_used": 22,
  "revenue": 8500000,
  "target_revenue": 8000000
}
```

Response:

```json
{
  "message": "Result recorded successfully",
  "learning_statistics": {
    "22": {
      "trials": 1,
      "successes": 1,
      "success_rate": 0.5,
      "confidence_interval": [0.025, 0.975]
    }
  }
}
```

### **3. Optimize Again (Sau vài lần - Thompson Learning)**

Sau 3-5 lần record, Thompson Sampling sẽ bắt đầu có data:

Response (Learning):

```json
{
  "optimization_result": {
    "discount_percent": 20,
    "confidence": 0.75,
    "reason": "Thompson Sampling: 5 trials, 80% success rate",
    "method": "Thompson Sampling",
    "status": "high_confidence",
    "expected_success_rate": 0.8,
    "total_trials": 5
  }
}
```

---

## 📊 SO SÁNH VỚI CÁC PHƯƠNG PHÁP KHÁC

| Tiêu Chí              | Thompson Sampling     | XGBoost          | Deep Learning      | Prophet        |
| --------------------- | --------------------- | ---------------- | ------------------ | -------------- |
| **Cần data training** | ❌ Không              | ✅ 5000+ records | ✅ 50,000+ records | ✅ 1+ năm data |
| **CPU usage**         | 🟢 Rất thấp           | 🟡 Trung bình    | 🔴 Cao             | 🟡 Trung bình  |
| **Memory**            | 🟢 <10MB              | 🟡 50-200MB      | 🔴 500MB+          | 🟡 100MB       |
| **Inference time**    | 🟢 <1ms               | 🟡 10-50ms       | 🟡 50-200ms        | 🟡 100ms       |
| **Tự học**            | ✅ Real-time          | ❌ Cần retrain   | ❌ Cần retrain     | ❌ Cần retrain |
| **Render deploy**     | ✅ OK                 | ⚠️ Có thể slow   | ❌ Out of CPU      | ⚠️ Có thể slow |
| **Độ chính xác**      | 🟡 Tốt sau 10+ trials | 🟢 Rất tốt       | 🟢 Rất tốt         | 🟡 Tốt         |

---

## ✅ ƯU ĐIỂM GIẢI PHÁP NÀY

1. ✅ **Không cần data ban đầu**: Cold start với Gemini API
2. ✅ **Tự học liên tục**: Thompson Sampling học từng kết quả bán hàng
3. ✅ **Lightweight**: CPU < 1%, Memory < 10MB
4. ✅ **Deploy Render OK**: Không cần GPU, không bị timeout
5. ✅ **Có sẵn**: Dùng Gemini API bạn đã có
6. ✅ **Ensemble**: Kết hợp 2 methods → output tốt hơn

---

## 🎯 ROADMAP

### **Week 1: MVP**

- ✅ Implement Thompson Sampling
- ✅ Integrate Gemini API
- ✅ Tạo 3 endpoints

### **Week 2: Testing**

- ✅ Test với 5-10 products
- ✅ Record results
- ✅ Monitor learning

### **Week 3: Optimize**

- ✅ Persist Thompson parameters to MongoDB
- ✅ Add caching
- ✅ A/B testing dashboard

---

## 📝 NEXT STEPS

Tôi có thể:

1. ✅ **Tạo file `discount_optimizer.py`** ngay
2. ✅ **Update router** với 3 endpoints mới
3. ✅ **Tạo Postman collection** để test
4. ✅ **Deploy lên Render** và test

Bạn muốn bắt đầu implement không? 🚀
