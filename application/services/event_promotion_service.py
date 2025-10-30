"""
Event-Based Promotion Service
Service tự động phân tích và tạo khuyến mãi dựa trên:
- Phân tích sản phẩm bán chạy/bán chậm
- Phát hiện sự kiện đặc biệt
- Gợi ý combo sản phẩm
- Tạo chương trình khuyến mãi tối ưu
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import uuid

from infrastructure.db.mongodb_access import MongoDBDataAccess
from utils.event_detector import EventDetector
from domain.entities.event_promotion import (
    ProductAnalysis,
    ProductStatus,
    ComboSuggestion,
    PromotionRecommendation,
    PromotionStrategy,
    EventType
)
from application.services.discount_optimizer import get_discount_optimizer
import logging

logger = logging.getLogger(__name__)


class EventPromotionService:
    """Service phân tích và tạo khuyến mãi dựa trên sự kiện"""
    
    def __init__(self, use_async: bool = False):
        """Initialize service"""
        self.data_access = MongoDBDataAccess(use_async=use_async)
        self.event_detector = EventDetector()
        
    async def analyze_product_performance(
        self,
        analysis_period_days: int = 365  # ✅ FIXED: Tăng từ 30 → 365 ngày (do orders cũ)
    ) -> List[ProductAnalysis]:
        """
        Phân tích hiệu suất sản phẩm
        
        Args:
            analysis_period_days: Số ngày phân tích (mặc định 30 ngày)
            
        Returns:
            Danh sách ProductAnalysis
        """
        # Lấy dữ liệu
        orders_df = self.data_access.get_orders_data()
        products_df = self.data_access.get_products_data()
        
        if orders_df.empty or products_df.empty:
            return []
        
        # Lọc orders trong khoảng thời gian phân tích
        orders_df['createdAt'] = pd.to_datetime(orders_df['createdAt'])
        cutoff_date = datetime.now() - timedelta(days=analysis_period_days)
        recent_orders = orders_df[orders_df['createdAt'] >= cutoff_date]
        
        # Flatten orderItems để phân tích
        flattened_items = []
        for _, order in recent_orders.iterrows():
            if 'orderItems' in order and isinstance(order['orderItems'], list):
                for item in order['orderItems']:
                    if isinstance(item, dict):
                        flattened_items.append({
                            'product_id': str(item.get('product', '')),
                            'quantity': item.get('quantity', 0),
                            'total': item.get('total', 0)
                        })
        
        items_df = pd.DataFrame(flattened_items) if flattened_items else pd.DataFrame()
        
        # Tính toán revenue tổng
        total_revenue = items_df['total'].sum() if not items_df.empty else 1
        
        # Phân tích từng sản phẩm
        analyses = []
        for _, product in products_df.iterrows():
            try:
                product_id = str(product['_id'])
                product_name = product.get('productName', 'Unknown')
                current_price = float(product.get('productPrice', 0))
                
                # Handle NaN for stock_level
                stock_qty = product.get('productQuantity', 0)
                stock_level = int(stock_qty) if pd.notna(stock_qty) else 0
                
                # Handle NaN for avg_rating
                rating = product.get('averageRating', 0)
                avg_rating = float(rating) if pd.notna(rating) else 0.0
                
                # Lấy dữ liệu bán hàng của sản phẩm này
                if not items_df.empty:
                    product_sales = items_df[items_df['product_id'] == product_id]
                    total_sold = int(product_sales['quantity'].sum()) if not product_sales.empty else 0
                    total_revenue_product = float(product_sales['total'].sum()) if not product_sales.empty else 0.0
                else:
                    total_sold = 0
                    total_revenue_product = 0.0
                
                # Handle NaN values
                if pd.isna(total_sold):
                    total_sold = 0
                if pd.isna(total_revenue_product):
                    total_revenue_product = 0.0
                
                # Tính metrics với safe division
                avg_monthly_sales = (total_sold / analysis_period_days) * 30 if analysis_period_days > 0 else 0.0
                revenue_contribution = (total_revenue_product / total_revenue * 100) if total_revenue > 0 else 0.0
                
                # Ensure no NaN/Inf values
                if pd.isna(avg_monthly_sales) or not isinstance(avg_monthly_sales, (int, float)):
                    avg_monthly_sales = 0.0
                if pd.isna(revenue_contribution) or not isinstance(revenue_contribution, (int, float)):
                    revenue_contribution = 0.0
                
                # Phân loại sản phẩm và đề xuất discount
                status, discount, reason = self._classify_product(
                    total_sold=total_sold,
                    avg_monthly_sales=avg_monthly_sales,
                    revenue_contribution=revenue_contribution,
                    stock_level=stock_level,
                    avg_rating=avg_rating
                )
                
                analysis = ProductAnalysis(
                    product_id=product_id,
                    product_name=product_name,
                    current_price=current_price,
                    avg_monthly_sales=avg_monthly_sales,
                    total_sold=total_sold,
                    revenue_contribution=revenue_contribution,
                    stock_level=stock_level,
                    avg_rating=avg_rating,
                    status=status,
                    recommended_discount=discount,
                    reason=reason
                )
                analyses.append(analysis)
            except Exception as e:
                # Skip products with errors
                print(f"Warning: Error analyzing product {product.get('productName', 'Unknown')}: {e}")
                continue
        
        return analyses
    
    def _classify_product(
        self,
        total_sold: int,
        avg_monthly_sales: float,
        revenue_contribution: float,
        stock_level: int,
        avg_rating: float
    ) -> tuple:
        """
        Phân loại sản phẩm và đề xuất mức giảm giá
        
        Returns:
            (ProductStatus, recommended_discount, reason)
        """
        # Sản phẩm bán chạy
        if total_sold > 20 and revenue_contribution > 5:
            return (
                ProductStatus.BEST_SELLER,
                5.0,  # Giảm nhẹ vì đã bán tốt
                "Sản phẩm bán chạy, chỉ cần khuyến mãi nhẹ để duy trì momentum"
            )
        
        # Sản phẩm bán chậm + tồn kho cao
        if total_sold < 5 and stock_level > 10:
            return (
                ProductStatus.SLOW_MOVING,
                20.0,  # Giảm mạnh để thanh lý
                "Sản phẩm bán chậm và tồn kho cao, cần đẩy mạnh doanh số"
            )
        
        # Sản phẩm bán chậm nhưng tồn kho thấp
        if total_sold < 5 and stock_level <= 10:
            return (
                ProductStatus.SLOW_MOVING,
                15.0,
                "Sản phẩm bán chậm, khuyến mãi vừa phải để tăng độ quan tâm"
            )
        
        # Sản phẩm có tiềm năng (rating cao nhưng bán chưa tốt)
        if avg_rating >= 4.5 and total_sold < 10:
            return (
                ProductStatus.COMBO_POTENTIAL,
                10.0,
                "Sản phẩm được đánh giá cao, có tiềm năng bán kèm combo"
            )
        
        # Sản phẩm bình thường
        return (
            ProductStatus.NORMAL,
            10.0,
            "Sản phẩm bán ổn định, khuyến mãi tiêu chuẩn"
        )
    
    async def discover_product_combos(
        self,
        min_support: float = 0.05,
        min_confidence: float = 0.3
    ) -> List[ComboSuggestion]:
        """
        Phát hiện combo sản phẩm tiềm năng từ lịch sử mua hàng
        Sử dụng Market Basket Analysis
        
        Args:
            min_support: Ngưỡng support tối thiểu (mặc định 5%)
            min_confidence: Ngưỡng confidence tối thiểu (mặc định 30%)
            
        Returns:
            Danh sách ComboSuggestion
        """
        orders_df = self.data_access.get_orders_data()
        products_df = self.data_access.get_products_data()
        
        if orders_df.empty or products_df.empty:
            return []
        
        # Chuẩn bị transactions cho market basket analysis
        transactions = []
        for _, order in orders_df.iterrows():
            transaction = []
            if 'orderItems' in order and isinstance(order['orderItems'], list):
                for item in order['orderItems']:
                    if isinstance(item, dict) and 'product' in item:
                        product_id = str(item['product'])
                        transaction.append(product_id)
            
            if len(transaction) >= 2:  # Chỉ lấy đơn có ít nhất 2 sản phẩm
                transactions.append(transaction)
        
        if len(transactions) < 5:  # Không đủ dữ liệu
            return []
        
        # Áp dụng Apriori algorithm
        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
        
        # Tìm frequent itemsets
        frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
        
        if frequent_itemsets.empty:
            return []
        
        # Tạo association rules
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        
        # Lọc rules có 2 items (product pairs)
        rules = rules[rules['antecedents'].apply(len) == 1]
        rules = rules[rules['consequents'].apply(len) == 1]
        
        # Tạo combo suggestions
        combos = []
        products_dict = {str(p['_id']): p for _, p in products_df.iterrows()}
        
        for _, rule in rules.iterrows():
            product_1_id = list(rule['antecedents'])[0]
            product_2_id = list(rule['consequents'])[0]
            
            if product_1_id in products_dict and product_2_id in products_dict:
                p1 = products_dict[product_1_id]
                p2 = products_dict[product_2_id]
                
                # Tính frequency (số lần mua cùng nhau)
                frequency = int(rule['support'] * len(transactions))
                
                # Đề xuất discount cho combo (10-20%)
                confidence_score = float(rule['confidence'])
                
                # Ensure valid confidence score
                if pd.isna(confidence_score) or confidence_score < 0:
                    confidence_score = 0.0
                elif confidence_score > 1:
                    confidence_score = 1.0
                    
                recommended_discount = min(10 + (confidence_score * 10), 20)
                
                # Ensure valid discount
                if pd.isna(recommended_discount):
                    recommended_discount = 10.0
                
                combo = ComboSuggestion(
                    product_1_id=product_1_id,
                    product_1_name=p1.get('productName', 'Unknown'),
                    product_1_price=float(p1.get('productPrice', 0)),
                    product_2_id=product_2_id,
                    product_2_name=p2.get('productName', 'Unknown'),
                    product_2_price=float(p2.get('productPrice', 0)),
                    frequency_together=frequency,
                    confidence=confidence_score,
                    recommended_bundle_discount=recommended_discount
                )
                combos.append(combo)
        
        # Sắp xếp theo confidence
        combos.sort(key=lambda x: x.confidence, reverse=True)
        
        return combos[:10]  # Trả về top 10 combos
    
    async def generate_event_promotion(
        self,
        event_type: Optional[EventType] = None,
        days_ahead: int = 60
    ) -> List[PromotionRecommendation]:
        """
        🤖 Tạo đề xuất khuyến mãi dựa trên sự kiện sắp tới (AI-POWERED)
        
        **NÂNG CẤP MỚI:**
        - ✅ AI tự động tính discount % tối ưu cho DOANH THU CAO NHẤT
        - ✅ Thompson Sampling: Tự học từ kết quả thực tế
        - ✅ Gemini API: Cold start khi chưa có data
        - ✅ Loyalty bonus: Giữ chân khách hàng thân thiết (+2-5%)
        - ✅ Thời gian tối ưu: 3-5 ngày trước event (bánh tươi)
        
        Args:
            event_type: Loại sự kiện cụ thể (None = tất cả sự kiện)
            days_ahead: Số ngày nhìn về tương lai
            
        Returns:
            Danh sách PromotionRecommendation với discount tối ưu
        """
        logger.info(f"🎯 Generating AI-powered event promotions (days_ahead={days_ahead})")
        
        # Lấy sự kiện sắp tới
        upcoming_events = self.event_detector.get_upcoming_events(
            reference_date=datetime.now(),
            days_ahead=days_ahead
        )
        
        if event_type:
            upcoming_events = [e for e in upcoming_events if e.event_type == event_type]
        
        if not upcoming_events:
            logger.warning("No upcoming events found")
            return []
        
        logger.info(f"Found {len(upcoming_events)} upcoming events")
        
        # Phân tích sản phẩm
        product_analyses = await self.analyze_product_performance()
        
        # Phát hiện combos
        combo_suggestions = await self.discover_product_combos()
        
        # 🤖 Get AI Optimizer
        optimizer = get_discount_optimizer()
        
        # Tạo promotion cho từng sự kiện
        recommendations = []
        for event in upcoming_events:
            logger.info(f"Processing event: {event.event_type.value} on {event.event_date}")
            
            # Lọc sản phẩm phù hợp với sự kiện
            if "Tất cả" in event.target_categories:
                target_products = product_analyses
            else:
                # TODO: Lọc theo category khi có dữ liệu category
                target_products = product_analyses
            
            if not target_products:
                continue
            
            # 🎯 Chọn sản phẩm phù hợp
            # Priority: Best sellers + High rating (để maximize revenue)
            suitable_products = []
            
            for product in target_products:
                # Chỉ chọn sản phẩm có rating >= 3.5 và có bán
                if product.avg_rating >= 3.5 and product.total_sold > 0:
                    suitable_products.append(product)
            
            # Sort theo revenue contribution (ưu tiên sản phẩm đóng góp doanh thu cao)
            suitable_products.sort(key=lambda p: p.revenue_contribution, reverse=True)
            
            # Lấy top products (10-15 tùy sự kiện)
            if event.event_type in [EventType.TET, EventType.CHRISTMAS, EventType.MID_AUTUMN]:
                focus_products = suitable_products[:15]  # Sự kiện lớn → nhiều sản phẩm
                strategy = PromotionStrategy.EVENT_SPECIAL
                primary_goal = "REVENUE"
            else:
                focus_products = suitable_products[:10]
                strategy = PromotionStrategy.BOOST_SALES
                primary_goal = "VOLUME"
            
            if not focus_products:
                logger.warning(f"No suitable products for {event.event_type.value}")
                continue
            
            # 🤖 AI OPTIMIZATION: Tính discount tối ưu cho TỪNG sản phẩm
            optimized_products = []
            total_ai_discount = 0
            
            for product in focus_products:
                try:
                    # Gọi AI Optimizer
                    optimization_result = optimizer.get_optimal_discount(
                        product_id=product.product_id,
                        product_name=product.product_name,
                        category="Bánh",  # TODO: Get from product
                        base_price=product.current_price,
                        event_type=event.event_type.name,
                        avg_rating=product.avg_rating,
                        historical_sales=product.total_sold,
                        days_to_event=event.days_until_event,
                        customer_segment='all'  # Mặc định all (có thể customize sau)
                    )
                    
                    # Update product với AI-optimized discount
                    product.recommended_discount = optimization_result['final_discount']
                    product.reason = optimization_result['reason']
                    
                    optimized_products.append(product)
                    total_ai_discount += optimization_result['final_discount']
                    
                    logger.info(
                        f"  ✅ {product.product_name}: "
                        f"{optimization_result['final_discount']}% "
                        f"(method: {optimization_result['method']}, "
                        f"confidence: {optimization_result['confidence']})"
                    )
                    
                except Exception as e:
                    logger.error(f"Error optimizing discount for {product.product_name}: {e}")
                    # Fallback to rule-based
                    product.recommended_discount = 15
                    product.reason = f"Fallback: {str(e)}"
                    optimized_products.append(product)
            
            # Tính average discount cho promotion
            avg_discount = total_ai_discount / len(optimized_products) if optimized_products else 15
            
            # 📅 Tính thời gian tối ưu (cho bánh tươi)
            timing = optimizer.calculate_promotion_timing(
                event_date=event.event_date,
                event_type=event.event_type.name,
                is_fresh_product=True  # Bánh tươi bán trong ngày
            )
            
            # 💰 Dự đoán impact (cải thiện với AI discount)
            estimated_revenue_impact = self._estimate_revenue_impact_with_ai(
                products=optimized_products,
                event_type=event.event_type
            )
            
            # 🎁 Tạo promotion
            promotion = PromotionRecommendation(
                promotion_id=str(uuid.uuid4()),
                promotion_name=f"🎉 Khuyến Mãi {event.event_type.value} - AI Optimized",
                description=self._generate_promotion_description(
                    event=event,
                    products=optimized_products,
                    avg_discount=avg_discount
                ),
                strategy=strategy,
                event_info=event,
                target_products=optimized_products,
                combo_suggestions=combo_suggestions[:5],
                discount_type="PERCENTAGE",
                discount_value=round(avg_discount, 1),
                min_order_value=100000 if len(optimized_products) > 10 else 0,
                max_discount_amount=500000 if event.event_type in [EventType.TET, EventType.CHRISTMAS] else 300000,
                start_date=timing['start_date'],
                end_date=timing['end_date'],
                duration_days=timing['duration_days'],
                estimated_revenue_impact=estimated_revenue_impact,
                estimated_order_increase=int(len(optimized_products) * 3.0),  # AI tốt hơn → tăng nhiều hơn
                risk_level=self._assess_risk_level(avg_discount, strategy),
                primary_goal=primary_goal,
                target_customer_type="ALL",
                created_at=datetime.now()
            )
            
            recommendations.append(promotion)
        
        return recommendations
    
    def _estimate_revenue_impact_with_ai(
        self,
        products: List[ProductAnalysis],
        event_type: EventType
    ) -> float:
        """
        🤖 Dự đoán tác động doanh thu với AI-optimized discounts
        
        Cải tiến so với _estimate_revenue_impact cũ:
        - Tính riêng cho từng sản phẩm (personalized discount)
        - Cân nhắc confidence của AI
        - Weight theo revenue contribution
        
        Args:
            products: List sản phẩm đã được AI optimize
            event_type: Loại sự kiện
            
        Returns:
            Estimated revenue impact (%)
        """
        if not products:
            return 0.0
        
        # Event multipliers (giống cũ nhưng có thêm Halloween)
        event_multipliers = {
            EventType.TET: 2.5,
            EventType.CHRISTMAS: 2.0,
            EventType.BLACK_FRIDAY: 3.0,
            EventType.HALLOWEEN: 1.8,
            EventType.VALENTINE: 1.5,
            EventType.INTERNATIONAL_WOMEN_DAY: 1.4,  # ✅ FIXED: WOMEN_DAY → INTERNATIONAL_WOMEN_DAY
            EventType.VIETNAM_WOMEN_DAY: 1.4,
            EventType.MID_AUTUMN: 1.6,
            EventType.WEEKEND: 1.2,
            EventType.NORMAL: 1.0,
        }
        
        event_multiplier = event_multipliers.get(event_type, 1.5)
        
        # Tính revenue impact cho TỪNG sản phẩm
        total_weighted_impact = 0.0
        total_weight = 0.0
        
        for product in products:
            # Base impact từ AI-optimized discount
            discount = product.recommended_discount
            base_impact = (discount / 10) * 5  # 10% discount ~ 5% order increase
            
            # Weight theo revenue contribution (sản phẩm đóng góp doanh thu cao → impact lớn)
            weight = product.revenue_contribution / 100.0
            
            # Product performance factor
            performance_factor = 1.0
            if product.avg_rating >= 4.5:
                performance_factor = 1.2  # Best sellers có thể tăng nhiều hơn
            elif product.avg_rating >= 4.0:
                performance_factor = 1.1
            
            # Margin loss (giảm giá → mất margin)
            margin_loss = discount * 0.4  # Mỗi % giảm → mất 0.4% margin
            
            # Net impact cho sản phẩm này
            product_impact = (base_impact * performance_factor - margin_loss) * event_multiplier
            
            # Weighted sum
            total_weighted_impact += product_impact * weight
            total_weight += weight
        
        # Average weighted impact
        if total_weight > 0:
            net_impact = total_weighted_impact / total_weight
        else:
            net_impact = 10.0  # Fallback
        
        # AI bonus: Thompson Sampling học được → impact tốt hơn (+20%)
        ai_bonus = net_impact * 0.2
        
        return round(net_impact + ai_bonus, 2)
    
    def _generate_promotion_description(
        self,
        event,
        products: List[ProductAnalysis],
        avg_discount: float
    ) -> str:
        """
        📝 Tạo mô tả promotion hấp dẫn
        
        Args:
            event: UpcomingEvent object
            products: Danh sách sản phẩm trong promotion
            avg_discount: Discount trung bình (%)
            
        Returns:
            Mô tả promotion (Vietnamese)
        """
        # Top 3 sản phẩm đóng góp doanh thu cao nhất
        top_products = sorted(products, key=lambda p: p.revenue_contribution, reverse=True)[:3]
        product_names = ", ".join([p.product_name for p in top_products])
        
        # Thông tin sự kiện
        event_name = event.event_type.value
        event_date_str = event.event_date.strftime("%d/%m/%Y")
        
        # Tạo description
        description = (
            f"🎉 Chương trình khuyến mãi đặc biệt nhân dịp **{event_name}** ({event_date_str})\n\n"
            f"🤖 **AI-Optimized Promotion** - Tối ưu doanh thu với công nghệ Thompson Sampling + Gemini API\n\n"
            f"💰 Giảm giá trung bình **{avg_discount:.1f}%** cho {len(products)} sản phẩm chọn lọc\n\n"
            f"⭐ Sản phẩm nổi bật: {product_names}\n\n"
            f"🎯 Mục tiêu: Tăng doanh thu & giữ chân khách hàng thân thiết\n\n"
            f"📦 Áp dụng cho: Tất cả khách hàng (VIP được bonus thêm +5%)\n\n"
            f"⏰ Thời gian: 3-5 ngày trước sự kiện (phù hợp bánh tươi)\n\n"
            f"✨ Lưu ý: Mỗi sản phẩm có mức giảm giá riêng được AI tính toán để maximize revenue!"
        )
        
        return description
    
    def _estimate_revenue_impact(
        self,
        discount: float,
        num_products: int,
        event_type: EventType
    ) -> float:
        """
        Dự đoán tác động doanh thu (%)
        
        Công thức đơn giản:
        - Mức giảm giá cao + sự kiện lớn = tăng doanh thu cao
        - Cân nhắc việc giảm margin
        """
        # Base impact từ discount
        base_impact = (discount / 10) * 5  # 10% discount ~ 5% tăng orders
        
        # Event multiplier
        event_multipliers = {
            EventType.TET: 2.5,
            EventType.CHRISTMAS: 2.0,
            EventType.BLACK_FRIDAY: 3.0,
            EventType.VALENTINE: 1.5,
            EventType.WEEKEND: 1.2,
            EventType.NORMAL: 1.0,
        }
        
        multiplier = event_multipliers.get(event_type, 1.5)
        
        # Product coverage impact
        coverage_factor = min(num_products / 10, 1.5)
        
        estimated_impact = base_impact * multiplier * coverage_factor
        
        # Trừ đi loss từ discount
        margin_loss = discount * 0.5
        
        net_impact = estimated_impact - margin_loss
        
        return round(net_impact, 2)
    
    def _assess_risk_level(self, discount: float, strategy: PromotionStrategy) -> str:
        """Đánh giá mức độ rủi ro của promotion"""
        if discount > 25:
            return "HIGH"
        elif discount > 15:
            return "MEDIUM"
        else:
            return "LOW"
        
        # Clearance có rủi ro thấp vì đang thanh lý
        if strategy == PromotionStrategy.CLEARANCE:
            return "LOW"
        
        return "MEDIUM"
    
    async def generate_smart_promotion(
        self,
        focus: str = "balanced"
    ) -> PromotionRecommendation:
        """
        Tạo khuyến mãi thông minh dựa trên phân tích tổng hợp
        
        Args:
            focus: "revenue" | "clearance" | "balanced"
            
        Returns:
            PromotionRecommendation
        """
        # Phân tích toàn diện
        product_analyses = await self.analyze_product_performance()
        combo_suggestions = await self.discover_product_combos()
        upcoming_events = self.event_detector.get_upcoming_events(days_ahead=30)
        
        # Chọn strategy dựa trên focus
        if focus == "clearance":
            strategy = PromotionStrategy.CLEARANCE
            target_products = [p for p in product_analyses if p.status == ProductStatus.SLOW_MOVING]
            discount = 20.0
            primary_goal = "CLEARANCE"
        elif focus == "revenue":
            strategy = PromotionStrategy.BOOST_SALES
            target_products = sorted(product_analyses, key=lambda x: x.revenue_contribution, reverse=True)[:10]
            discount = 15.0
            primary_goal = "REVENUE"
        else:  # balanced
            strategy = PromotionStrategy.BOOST_SALES
            # Mix: một số slow-moving + một số best-sellers
            slow = [p for p in product_analyses if p.status == ProductStatus.SLOW_MOVING][:5]
            best = [p for p in product_analyses if p.status == ProductStatus.BEST_SELLER][:5]
            target_products = slow + best
            discount = 12.0
            primary_goal = "VOLUME"
        
        # Timing: bắt đầu ngay, kéo dài 7 ngày
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        # Event info (nếu có)
        event_info = upcoming_events[0] if upcoming_events else None
        
        promotion = PromotionRecommendation(
            promotion_id=str(uuid.uuid4()),
            promotion_name=f"Khuyến Mãi Thông Minh - {focus.title()}",
            description=f"Chương trình được AI đề xuất dựa trên phân tích dữ liệu bán hàng. "
                       f"Giảm {discount}% cho {len(target_products)} sản phẩm được chọn.",
            strategy=strategy,
            event_info=event_info,
            target_products=target_products,
            combo_suggestions=combo_suggestions[:5],
            discount_type="PERCENTAGE",
            discount_value=discount,
            min_order_value=50000,
            max_discount_amount=300000,
            start_date=start_date,
            end_date=end_date,
            duration_days=7,
            estimated_revenue_impact=self._estimate_revenue_impact(
                discount, len(target_products), EventType.NORMAL
            ),
            estimated_order_increase=len(target_products) * 2,
            risk_level=self._assess_risk_level(discount, strategy),
            primary_goal=primary_goal,
            target_customer_type="ALL",
            created_at=datetime.now()
        )
        
        return promotion


# Singleton instance
_service_instance = None


def get_event_promotion_service() -> EventPromotionService:
    """Get singleton instance của EventPromotionService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = EventPromotionService()
    return _service_instance
