"""
AI-Powered Discount Optimizer
Tối ưu hóa % giảm giá để DOANH THU CAO NHẤT

Phương pháp:
1. Thompson Sampling: Tự học từ kết quả thực tế
2. Gemini API: Cold start khi chưa có data
3. Price Elasticity: Tính toán dựa trên hành vi khách hàng

Đặc thù: Bánh ngọt bán trong ngày, không tồn kho
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from scipy.stats import beta as beta_dist
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)


class ThompsonSamplingOptimizer:
    """
    Thompson Sampling cho discount optimization
    Tự động học discount % tối ưu từ kết quả bán hàng thực tế
    
    Ưu điểm:
    - Không cần training data ban đầu
    - Tự động A/B testing
    - Học real-time
    - Lightweight (< 1ms inference)
    """
    
    def __init__(self):
        # Discount levels để test (tăng dần 5%)
        self.discount_levels = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        
        # Beta distribution parameters: {key: (alpha, beta)}
        # alpha = success count, beta = failure count
        self.params = {}
        
    def _get_key(self, product_id: str, event_type: str, discount: int) -> str:
        """Tạo unique key cho combination"""
        return f"{product_id}_{event_type}_{discount}"
    
    def select_discount(
        self, 
        product_id: str, 
        event_type: str,
        base_price: float,
        avg_rating: float = 4.0,
        historical_sales: int = 0,
        min_profit_margin: float = 0.20  # 20% profit tối thiểu cho bánh
    ) -> Dict:
        """
        Chọn discount tối ưu bằng Thompson Sampling
        
        Args:
            product_id: ID sản phẩm
            event_type: Loại sự kiện
            base_price: Giá gốc
            avg_rating: Đánh giá trung bình
            historical_sales: Số lượng đã bán (dùng cho prior)
            min_profit_margin: Profit margin tối thiểu
            
        Returns:
            {
                'discount_percent': 20,
                'confidence': 0.85,
                'reason': 'Thompson Sampling: 45 trials, 80% success',
                'method': 'thompson_sampling'
            }
        """
        # Lọc discounts đảm bảo profit margin
        valid_discounts = [
            d for d in self.discount_levels 
            if (100 - d) >= (min_profit_margin * 100)
        ]
        
        if not valid_discounts:
            return {
                'discount_percent': 0,
                'confidence': 1.0,
                'reason': 'Không có discount nào đảm bảo profit margin',
                'method': 'fallback'
            }
        
        # Sample từ Beta distribution cho mỗi discount level
        sampled_rewards = {}
        trial_counts = {}
        success_rates = {}
        
        for discount in valid_discounts:
            key = self._get_key(product_id, event_type, discount)
            
            # Lấy parameters (default = informed prior)
            if key in self.params:
                alpha, beta = self.params[key]
            else:
                # Informed prior dựa trên rating và historical sales
                # Rating cao + sales cao = tin tưởng giảm ít
                # Rating thấp + sales thấp = thử giảm nhiều
                prior_success = max(1, int(avg_rating * historical_sales / 10))
                prior_failure = max(1, int((5 - avg_rating) * 2))
                alpha, beta = prior_success, prior_failure
            
            # Sample từ Beta(alpha, beta)
            sampled_rewards[discount] = np.random.beta(alpha, beta)
            trial_counts[discount] = alpha + beta - 2
            success_rates[discount] = alpha / (alpha + beta)
        
        # Chọn discount có highest sampled reward
        best_discount = max(sampled_rewards, key=sampled_rewards.get)
        
        # Tính confidence
        total_trials = sum(trial_counts.values())
        confidence = min(trial_counts[best_discount] / max(total_trials, 10), 1.0) if total_trials > 0 else 0.3
        
        return {
            'discount_percent': best_discount,
            'confidence': round(confidence, 2),
            'reason': f'Thompson Sampling: {trial_counts[best_discount]} trials, {round(success_rates[best_discount]*100)}% success rate',
            'expected_success_rate': round(success_rates[best_discount], 3),
            'total_trials': trial_counts[best_discount],
            'method': 'thompson_sampling'
        }
    
    def update(
        self, 
        product_id: str, 
        event_type: str, 
        discount: int,
        actual_revenue: float,
        expected_revenue: float
    ):
        """
        Cập nhật model sau khi có kết quả bán hàng
        
        Args:
            actual_revenue: Doanh thu thực tế
            expected_revenue: Doanh thu kỳ vọng
        """
        key = self._get_key(product_id, event_type, discount)
        
        # Initialize nếu chưa có
        if key not in self.params:
            self.params[key] = (1, 1)
        
        alpha, beta = self.params[key]
        
        # Update: Success nếu revenue >= expected
        if actual_revenue >= expected_revenue:
            alpha += 1  # Success
        else:
            beta += 1  # Failure
        
        self.params[key] = (alpha, beta)
        
        logger.info(f"Updated {key}: alpha={alpha}, beta={beta}, success_rate={alpha/(alpha+beta):.2%}")


class GeminiDiscountAdvisor:
    """
    Sử dụng Gemini API để đề xuất discount
    Dùng khi Thompson Sampling chưa đủ data (cold start)
    """
    
    def __init__(self):
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')  # ✅ FIXED: gemini-pro không tồn tại
            self.available = True
        except Exception as e:
            logger.warning(f"Gemini API không khả dụng: {e}")
            self.available = False
    
    def suggest_discount(
        self,
        product_name: str,
        category: str,
        base_price: float,
        event_type: str,
        avg_rating: float,
        days_to_event: int,
        is_fresh_product: bool = True  # Bánh tươi bán trong ngày
    ) -> Dict:
        """
        Gọi Gemini API để đề xuất discount tối ưu
        """
        
        if not self.available:
            return self._fallback_rule_based(event_type, avg_rating)
        
        prompt = f"""
Bạn là chuyên gia tối ưu hóa giá và khuyến mãi cho tiệm bánh cao cấp.

THÔNG TIN SẢN PHẨM:
- Tên: {product_name}
- Loại: {category}
- Giá gốc: {base_price:,} VNĐ
- Đánh giá: {avg_rating}/5
- ĐẶC ĐIỂM: Bánh tươi, bán trong ngày, KHÔNG TỒN KHO

SỰ KIỆN:
- Loại: {event_type}
- Còn {days_to_event} ngày

MỤC TIÊU:
Đề xuất % giảm giá TỐI ƯU để:
1. DOANH THU CAO NHẤT (không phải số lượng bán)
2. Thu hút khách hàng mới
3. Giữ chân khách hàng thân thiết
4. Đảm bảo profit margin >= 20%

LƯU Ý:
- Bánh bán trong ngày nên ưu tiên bán nhanh
- Khách hàng thân thiết quan trọng (repeat purchase)
- Sự kiện lớn = cơ hội tăng doanh thu

Trả lời theo format JSON:
{{
    "discount_percent": <số nguyên 0-40>,
    "reason": "<lý do ngắn gọn về tâm lý khách hàng và tối ưu doanh thu>",
    "target_customer": "<new/loyal/all>",
    "expected_impact": "<mô tả ảnh hưởng dự kiến>"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            return {
                'discount_percent': min(result.get('discount_percent', 15), 40),  # Cap at 40%
                'confidence': 0.65,  # Moderate confidence cho AI
                'reason': f"Gemini AI: {result.get('reason', 'AI recommendation')}",
                'target_customer': result.get('target_customer', 'all'),
                'expected_impact': result.get('expected_impact', 'Unknown'),
                'method': 'gemini_ai'
            }
            
        except Exception as e:
            logger.warning(f"Gemini API error: {e}")
            return self._fallback_rule_based(event_type, avg_rating)
    
    def _fallback_rule_based(self, event_type: str, rating: float) -> Dict:
        """Rule-based fallback khi Gemini fail"""
        
        # Event-based discounts (conservative cho bánh tươi)
        event_discounts = {
            'HALLOWEEN': 20, 'TET': 25, 'CHRISTMAS': 20,
            'VALENTINE': 15, 'MID_AUTUMN': 25, 'BLACK_FRIDAY': 30,
            'MOTHER_DAY': 15, 'FATHER_DAY': 15, 'WOMEN_DAY': 15
        }
        
        base_discount = event_discounts.get(event_type.upper().replace(' ', '_'), 12)
        
        # Điều chỉnh theo rating
        if rating >= 4.5:
            base_discount -= 3  # Sản phẩm tốt → giảm ít
        elif rating <= 3.5:
            base_discount += 5  # Sản phẩm kém → giảm nhiều để test
        
        return {
            'discount_percent': min(max(base_discount, 5), 35),
            'confidence': 0.5,
            'reason': 'Rule-based: Dựa trên loại sự kiện và rating sản phẩm',
            'target_customer': 'all',
            'method': 'rule_based'
        }


class HybridDiscountOptimizer:
    """
    Kết hợp Thompson Sampling + Gemini API + Business Rules
    Tối ưu cho tiệm bánh (không tồn kho, bán trong ngày)
    """
    
    def __init__(self):
        self.thompson = ThompsonSamplingOptimizer()
        self.gemini = GeminiDiscountAdvisor()
        
        # Loyalty boost cho khách hàng thân thiết
        self.loyalty_boost = {
            'new': 0,      # Khách mới không giảm thêm
            'regular': 2,  # Khách quen +2%
            'vip': 5       # VIP +5%
        }
        
    def get_optimal_discount(
        self,
        product_id: str,
        product_name: str,
        category: str,
        base_price: float,
        event_type: str,
        avg_rating: float = 4.0,
        historical_sales: int = 0,
        days_to_event: int = 7,
        customer_segment: str = 'all',  # new/regular/vip/all
        min_trials_threshold: int = 5   # Số trials tối thiểu để tin Thompson
    ) -> Dict:
        """
        Lấy discount tối ưu kết hợp nhiều phương pháp
        
        Returns:
            {
                'discount_percent': 20,
                'confidence': 0.85,
                'reason': '...',
                'method': 'thompson_sampling/gemini_ai/hybrid',
                'loyalty_discount': 2,  # Discount thêm cho khách thân thiết
                'final_discount': 22,   # Tổng discount
                'target_customer': 'all'
            }
        """
        
        # Try Thompson Sampling
        thompson_result = self.thompson.select_discount(
            product_id=product_id,
            event_type=event_type,
            base_price=base_price,
            avg_rating=avg_rating,
            historical_sales=historical_sales
        )
        
        # Kiểm tra Thompson có đủ data không
        has_enough_data = thompson_result.get('total_trials', 0) >= min_trials_threshold
        high_confidence = thompson_result['confidence'] >= 0.7
        
        # Decision logic
        if has_enough_data and high_confidence:
            # Thompson có đủ data → tin tưởng hoàn toàn
            base_result = thompson_result
            base_result['status'] = 'confident'
            
        elif thompson_result.get('total_trials', 0) > 0:
            # Có ít data → ensemble Thompson + Gemini
            gemini_result = self.gemini.suggest_discount(
                product_name=product_name,
                category=category,
                base_price=base_price,
                event_type=event_type,
                avg_rating=avg_rating,
                days_to_event=days_to_event
            )
            
            # Weighted average
            thompson_weight = thompson_result['confidence']
            gemini_weight = 1 - thompson_weight
            
            ensemble_discount = int(
                thompson_result['discount_percent'] * thompson_weight +
                gemini_result['discount_percent'] * gemini_weight
            )
            
            base_result = {
                'discount_percent': ensemble_discount,
                'confidence': (thompson_result['confidence'] + gemini_result['confidence']) / 2,
                'reason': f"Hybrid: Thompson ({thompson_weight:.0%}) + Gemini ({gemini_weight:.0%})",
                'method': 'hybrid',
                'status': 'learning',
                'thompson_suggestion': thompson_result['discount_percent'],
                'gemini_suggestion': gemini_result['discount_percent']
            }
            
        else:
            # Cold start → dùng Gemini hoàn toàn
            base_result = self.gemini.suggest_discount(
                product_name=product_name,
                category=category,
                base_price=base_price,
                event_type=event_type,
                avg_rating=avg_rating,
                days_to_event=days_to_event
            )
            base_result['status'] = 'cold_start'
        
        # Apply loyalty bonus
        loyalty_discount = self._calculate_loyalty_discount(
            base_discount=base_result['discount_percent'],
            customer_segment=customer_segment
        )
        
        # ✅ FIXED: Round về các mức chuẩn (5%, 10%, 15%, 20%, 25%, 30%, 35%, 40%)
        raw_final_discount = base_result['discount_percent'] + loyalty_discount
        final_discount = self._round_to_standard_tiers(raw_final_discount)
        final_discount = min(final_discount, 50)  # Cap at 50%
        
        return {
            **base_result,
            'loyalty_discount': loyalty_discount,
            'final_discount': final_discount,
            'target_customer': customer_segment,
            'base_discount': base_result['discount_percent']
        }
    
    def _calculate_loyalty_discount(self, base_discount: float, customer_segment: str) -> int:
        """
        Tính discount thêm cho khách hàng thân thiết
        
        Logic:
        - VIP: +5% (để giữ chân)
        - Regular: +2% (khuyến khích quay lại)
        - New: 0% (đã có event discount)
        - All: +1% (trung bình)
        """
        if customer_segment == 'vip':
            return 5
        elif customer_segment == 'regular':
            return 2
        elif customer_segment == 'all':
            return 1
        else:
            return 0
    
    def _round_to_standard_tiers(self, discount: float) -> int:
        """
        ✅ Làm tròn discount về các mức chuẩn dễ quản lý
        
        Standard tiers: 5%, 10%, 15%, 20%, 25%, 30%, 35%, 40%
        
        Logic:
        - 0-7%  → 5%
        - 8-12% → 10%
        - 13-17% → 15%
        - 18-22% → 20%
        - 23-27% → 25%
        - 28-32% → 30%
        - 33-37% → 35%
        - 38+    → 40%
        
        Examples:
        - 26% → 25%
        - 31% → 30%
        - 41% → 40%
        """
        tiers = [5, 10, 15, 20, 25, 30, 35, 40]
        
        # Tìm tier gần nhất
        closest_tier = min(tiers, key=lambda x: abs(x - discount))
        
        return closest_tier
    
    def calculate_promotion_timing(
        self,
        event_date: datetime,
        event_type: str,
        is_fresh_product: bool = True
    ) -> Dict:
        """
        Tính thời gian khuyến mãi tối ưu
        
        Đặc thù bánh tươi:
        - Không nên chạy quá sớm (bánh bị hỏng)
        - Tập trung vào 3-5 ngày trước event
        - Kết thúc đúng ngày event
        """
        
        if is_fresh_product:
            # Bánh tươi: Chỉ 3-5 ngày trước event
            if event_type in ['TET', 'CHRISTMAS', 'MID_AUTUMN']:
                # Sự kiện lớn: 5 ngày
                pre_days = 5
            else:
                # Sự kiện nhỏ: 3 ngày
                pre_days = 3
            
            start_date = event_date - timedelta(days=pre_days)
            end_date = event_date
            
        else:
            # Sản phẩm lâu hơn: 7-14 ngày
            pre_days = 7 if event_type not in ['TET', 'CHRISTMAS'] else 14
            start_date = event_date - timedelta(days=pre_days)
            end_date = event_date + timedelta(days=1)
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'duration_days': (end_date - start_date).days,
            'pre_event_days': pre_days,
            'reasoning': 'Tối ưu cho bánh tươi: tập trung vào vài ngày trước event' if is_fresh_product else 'Thời gian chuẩn'
        }
    
    def record_result(
        self,
        product_id: str,
        event_type: str,
        discount_used: int,
        actual_revenue: float,
        expected_revenue: float
    ):
        """
        Ghi nhận kết quả để Thompson Sampling học
        Gọi sau mỗi đợt promotion
        """
        self.thompson.update(
            product_id=product_id,
            event_type=event_type,
            discount=discount_used,
            actual_revenue=actual_revenue,
            expected_revenue=expected_revenue
        )
    
    def get_learning_statistics(self, product_id: str, event_type: str) -> Dict:
        """Xem thống kê học của Thompson Sampling"""
        stats = {}
        
        for discount in self.thompson.discount_levels:
            key = self.thompson._get_key(product_id, event_type, discount)
            
            if key in self.thompson.params:
                alpha, beta = self.thompson.params[key]
                
                stats[discount] = {
                    'trials': alpha + beta - 2,
                    'successes': alpha - 1,
                    'failures': beta - 1,
                    'success_rate': round(alpha / (alpha + beta), 3),
                    'confidence_interval': self._get_confidence_interval(alpha, beta)
                }
        
        return stats
    
    def _get_confidence_interval(self, alpha: float, beta: float, confidence: float = 0.95) -> Tuple[float, float]:
        """Tính 95% confidence interval cho success rate"""
        lower = beta_dist.ppf((1 - confidence) / 2, alpha, beta)
        upper = beta_dist.ppf(1 - (1 - confidence) / 2, alpha, beta)
        return (round(lower, 3), round(upper, 3))


# Singleton instance
_optimizer_instance = None

def get_discount_optimizer() -> HybridDiscountOptimizer:
    """Get singleton instance của optimizer"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = HybridDiscountOptimizer()
        logger.info("✅ Discount Optimizer initialized")
    return _optimizer_instance
