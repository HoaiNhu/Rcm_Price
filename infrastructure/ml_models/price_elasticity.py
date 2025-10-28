"""
Price Elasticity Calculator - Infrastructure Layer
Tính toán độ nhạy cảm giá của sản phẩm

Price Elasticity = % Change in Quantity Demanded / % Change in Price

Classification:
- E < -1.5: VERY_SENSITIVE (elastic) - Không nên tăng giá
- -1.5 <= E < -1.0: SENSITIVE - Tăng giá cẩn thận
- -1.0 <= E < -0.5: MODERATE - Có thể tăng giá nhẹ
- E >= -0.5: INSENSITIVE (inelastic) - Có thể tăng giá

Author: RCM_PRICE Team
Date: 2025-10-27
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class PriceElasticityCalculator:
    """
    Calculator cho Price Elasticity of Demand
    
    Attributes:
        elasticity_models: Dict mapping product_id -> LinearRegression model
        product_elasticity: Dict mapping product_id -> elasticity coefficient
        scaler: StandardScaler for feature normalization
        is_trained: Boolean indicating if calculator has been trained
    """
    
    def __init__(self):
        """Initialize Price Elasticity Calculator"""
        self.elasticity_models: Dict[str, LinearRegression] = {}
        self.product_elasticity: Dict[str, float] = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Metrics for evaluation
        self.metrics = {
            'r_squared': {},
            'mse': {},
            'sample_size': {}
        }
        
        logger.info("✅ PriceElasticityCalculator initialized")
    
    def calculate_elasticity(
        self,
        orders_df: pd.DataFrame,
        products_df: pd.DataFrame,
        min_samples: int = 10
    ) -> Dict[str, float]:
        """
        Tính price elasticity cho tất cả sản phẩm
        
        Args:
            orders_df: DataFrame chứa order history
            products_df: DataFrame chứa product information
            min_samples: Số lượng samples tối thiểu để tính elasticity
            
        Returns:
            Dict mapping product_id -> elasticity coefficient
            
        Example:
            {
                "product_123": -0.8,  # MODERATE
                "product_456": -1.6,  # VERY_SENSITIVE
            }
        """
        logger.info(f"🔍 Calculating price elasticity for {len(products_df)} products...")
        
        elasticity_results = {}
        
        # Flatten order items to get price and quantity data
        flattened_orders = self._flatten_order_items(orders_df)
        
        if flattened_orders.empty:
            logger.warning("⚠️ No order data available for elasticity calculation")
            return elasticity_results
        
        # Calculate elasticity for each product
        for product_id in products_df['_id'].unique():
            try:
                product_orders = flattened_orders[
                    flattened_orders['product_id'] == str(product_id)
                ]
                
                if len(product_orders) < min_samples:
                    logger.debug(
                        f"Skipping {product_id}: insufficient samples "
                        f"({len(product_orders)} < {min_samples})"
                    )
                    continue
                
                # Calculate elasticity for this product
                elasticity, r_squared, mse = self._calculate_product_elasticity(
                    product_orders,
                    product_id
                )
                
                if elasticity is not None:
                    elasticity_results[product_id] = elasticity
                    self.metrics['r_squared'][product_id] = r_squared
                    self.metrics['mse'][product_id] = mse
                    self.metrics['sample_size'][product_id] = len(product_orders)
                    
                    sensitivity = self.get_sensitivity_category(elasticity)
                    logger.info(
                        f"✅ {product_id}: E={elasticity:.3f}, "
                        f"Sensitivity={sensitivity}, "
                        f"R²={r_squared:.3f}, "
                        f"Samples={len(product_orders)}"
                    )
                    
            except Exception as e:
                logger.error(f"❌ Error calculating elasticity for {product_id}: {e}")
                continue
        
        self.product_elasticity = elasticity_results
        self.is_trained = True
        
        logger.info(
            f"✅ Calculated elasticity for {len(elasticity_results)}/{len(products_df)} products"
        )
        
        return elasticity_results
    
    def _calculate_product_elasticity(
        self,
        product_orders: pd.DataFrame,
        product_id: str
    ) -> Tuple[Optional[float], float, float]:
        """
        Tính elasticity cho một sản phẩm cụ thể
        
        Args:
            product_orders: DataFrame chứa orders của sản phẩm
            product_id: ID của sản phẩm
            
        Returns:
            Tuple of (elasticity, r_squared, mse)
        """
        try:
            # Calculate unit price
            product_orders = product_orders.copy()
            product_orders['price'] = product_orders['total'] / product_orders['quantity']
            
            # Sort by date
            product_orders = product_orders.sort_values('date')
            
            # Calculate percentage changes
            product_orders['price_change'] = product_orders['price'].pct_change()
            product_orders['quantity_change'] = product_orders['quantity'].pct_change()
            
            # Remove NaN and infinite values
            clean_data = product_orders.replace([np.inf, -np.inf], np.nan).dropna()
            
            # Filter outliers (extreme price/quantity changes)
            clean_data = clean_data[
                (abs(clean_data['price_change']) < 0.5) &  # Max 50% price change
                (abs(clean_data['quantity_change']) < 2.0)  # Max 200% quantity change
            ]
            
            if len(clean_data) < 5:
                logger.debug(f"Insufficient clean data for {product_id}")
                return None, 0.0, 0.0
            
            # Prepare features for regression
            X = clean_data[['price_change']].values
            y = clean_data['quantity_change'].values
            
            # Train linear regression model
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate metrics
            y_pred = model.predict(X)
            mse = np.mean((y - y_pred) ** 2)
            
            # R-squared
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
            
            # Elasticity is the coefficient (slope)
            elasticity = model.coef_[0]
            
            # Store model
            self.elasticity_models[product_id] = model
            
            return elasticity, r_squared, mse
            
        except Exception as e:
            logger.error(f"Error in _calculate_product_elasticity: {e}")
            return None, 0.0, 0.0
    
    def get_sensitivity_category(self, elasticity: float) -> str:
        """
        Phân loại độ nhạy cảm giá
        
        Args:
            elasticity: Elasticity coefficient
            
        Returns:
            Sensitivity category string
        """
        if elasticity < -1.5:
            return "VERY_SENSITIVE"
        elif elasticity < -1.0:
            return "SENSITIVE"
        elif elasticity < -0.5:
            return "MODERATE"
        else:
            return "INSENSITIVE"
    
    def recommend_price_change(
        self,
        product_id: str,
        current_price: float
    ) -> Dict:
        """
        Đề xuất thay đổi giá an toàn cho sản phẩm
        
        Args:
            product_id: ID của sản phẩm
            current_price: Giá hiện tại
            
        Returns:
            Dict chứa recommendations
        """
        if product_id not in self.product_elasticity:
            return {
                "product_id": product_id,
                "can_increase": False,
                "reason": "Insufficient data - no elasticity calculated",
                "max_safe_increase_pct": 0,
                "max_safe_price": current_price,
                "recommendation": "⚠️ Cần thêm dữ liệu để phân tích"
            }
        
        elasticity = self.product_elasticity[product_id]
        sensitivity = self.get_sensitivity_category(elasticity)
        
        # Safe price increase limits by sensitivity
        safe_increase_pct = {
            "VERY_SENSITIVE": 0.02,   # Max 2% increase
            "SENSITIVE": 0.05,         # Max 5% increase
            "MODERATE": 0.10,          # Max 10% increase
            "INSENSITIVE": 0.15        # Max 15% increase
        }
        
        max_increase_pct = safe_increase_pct[sensitivity]
        max_safe_price = current_price * (1 + max_increase_pct)
        
        # Generate recommendation message
        recommendation_msg = self._generate_recommendation_message(
            sensitivity, 
            elasticity,
            max_increase_pct
        )
        
        return {
            "product_id": product_id,
            "current_price": current_price,
            "elasticity": round(elasticity, 3),
            "sensitivity": sensitivity,
            "can_increase": True,
            "max_safe_increase_pct": round(max_increase_pct * 100, 1),
            "max_safe_price": round(max_safe_price, 0),
            "recommendation": recommendation_msg,
            "r_squared": round(self.metrics['r_squared'].get(product_id, 0), 3),
            "sample_size": self.metrics['sample_size'].get(product_id, 0)
        }
    
    def _generate_recommendation_message(
        self,
        sensitivity: str,
        elasticity: float,
        max_increase_pct: float
    ) -> str:
        """Generate human-readable recommendation message"""
        
        messages = {
            "VERY_SENSITIVE": (
                f"⚠️ SẢN PHẨM RẤT NHẠY GIÁ (E={elasticity:.2f})\n"
                f"• Khách hàng rất nhạy cảm với thay đổi giá\n"
                f"• Tăng giá có thể dẫn đến mất khách\n"
                f"• Đề xuất: Ưu tiên khuyến mãi thay vì tăng giá\n"
                f"• Nếu bắt buộc tăng: Tối đa {max_increase_pct*100:.0f}% và kèm voucher bù đắp"
            ),
            "SENSITIVE": (
                f"⚠️ SẢN PHẨM NHẠY GIÁ (E={elasticity:.2f})\n"
                f"• Khách hàng khá nhạy cảm về giá\n"
                f"• Nên kết hợp voucher khi tăng giá\n"
                f"• Tăng giá tối đa: {max_increase_pct*100:.0f}%\n"
                f"• Monitor phản hồi khách hàng sau khi tăng"
            ),
            "MODERATE": (
                f"✅ ĐỘ NHẠY TRUNG BÌNH (E={elasticity:.2f})\n"
                f"• Có thể tăng giá nhẹ\n"
                f"• Tăng giá tối đa: {max_increase_pct*100:.0f}%\n"
                f"• Nên test A/B trước khi áp dụng rộng rãi\n"
                f"• Monitor doanh số trong 2-4 tuần đầu"
            ),
            "INSENSITIVE": (
                f"✅ SẢN PHẨM PREMIUM/ÍT NHẠY GIÁ (E={elasticity:.2f})\n"
                f"• Khách hàng ít quan tâm đến giá\n"
                f"• Có thể tăng giá thoải mái: tối đa {max_increase_pct*100:.0f}%\n"
                f"• Focus vào value proposition thay vì giá\n"
                f"• Cơ hội tăng profit margin"
            )
        }
        
        return messages.get(sensitivity, "No recommendation available")
    
    def get_elasticity_report(self) -> pd.DataFrame:
        """
        Tạo báo cáo chi tiết về elasticity của tất cả sản phẩm
        
        Returns:
            DataFrame chứa elasticity report
        """
        if not self.product_elasticity:
            logger.warning("No elasticity data available")
            return pd.DataFrame()
        
        report_data = []
        
        for product_id, elasticity in self.product_elasticity.items():
            sensitivity = self.get_sensitivity_category(elasticity)
            
            report_data.append({
                'product_id': product_id,
                'elasticity': round(elasticity, 3),
                'sensitivity': sensitivity,
                'r_squared': round(self.metrics['r_squared'].get(product_id, 0), 3),
                'mse': round(self.metrics['mse'].get(product_id, 0), 4),
                'sample_size': self.metrics['sample_size'].get(product_id, 0),
                'can_increase_price': sensitivity in ['MODERATE', 'INSENSITIVE']
            })
        
        df = pd.DataFrame(report_data)
        df = df.sort_values('elasticity')  # Sort by elasticity (most sensitive first)
        
        return df
    
    def get_summary_statistics(self) -> Dict:
        """
        Lấy thống kê tổng quan về elasticity
        
        Returns:
            Dict chứa summary statistics
        """
        if not self.product_elasticity:
            return {}
        
        elasticities = list(self.product_elasticity.values())
        
        # Count by sensitivity category
        sensitivity_counts = {}
        for elasticity in elasticities:
            category = self.get_sensitivity_category(elasticity)
            sensitivity_counts[category] = sensitivity_counts.get(category, 0) + 1
        
        # Calculate statistics
        summary = {
            'total_products': len(elasticities),
            'mean_elasticity': round(np.mean(elasticities), 3),
            'median_elasticity': round(np.median(elasticities), 3),
            'std_elasticity': round(np.std(elasticities), 3),
            'min_elasticity': round(np.min(elasticities), 3),
            'max_elasticity': round(np.max(elasticities), 3),
            'sensitivity_distribution': sensitivity_counts,
            'products_can_increase_price': sensitivity_counts.get('MODERATE', 0) + 
                                          sensitivity_counts.get('INSENSITIVE', 0),
            'products_should_not_increase': sensitivity_counts.get('VERY_SENSITIVE', 0) + 
                                           sensitivity_counts.get('SENSITIVE', 0),
            'mean_r_squared': round(
                np.mean(list(self.metrics['r_squared'].values())), 3
            ) if self.metrics['r_squared'] else 0
        }
        
        return summary
    
    def _flatten_order_items(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Flatten nested order items structure
        
        Args:
            orders_df: DataFrame with nested orderItems
            
        Returns:
            Flattened DataFrame with one row per order item
        """
        flattened = []
        
        for _, order in orders_df.iterrows():
            if 'orderItems' not in order or not isinstance(order['orderItems'], list):
                continue
            
            for item in order['orderItems']:
                if not isinstance(item, dict):
                    continue
                
                product_id = item.get('product', '')
                quantity = item.get('quantity', 0)
                total = item.get('total', 0)
                
                if quantity > 0 and total > 0:
                    flattened.append({
                        'order_id': str(order['_id']),  # Convert ObjectId to string
                        'date': pd.to_datetime(order['createdAt']).date(),
                        'product_id': str(product_id),  # Convert ObjectId to string
                        'quantity': quantity,
                        'total': total,
                    })
        
        return pd.DataFrame(flattened)
    
    def validate_elasticity_quality(self, min_r_squared: float = 0.3) -> Dict:
        """
        Đánh giá chất lượng của elasticity calculations
        
        Args:
            min_r_squared: Minimum acceptable R² value
            
        Returns:
            Validation report
        """
        if not self.is_trained:
            return {
                'is_valid': False,
                'reason': 'Calculator has not been trained'
            }
        
        low_quality_products = []
        
        for product_id, r_squared in self.metrics['r_squared'].items():
            if r_squared < min_r_squared:
                low_quality_products.append({
                    'product_id': product_id,
                    'r_squared': round(r_squared, 3),
                    'sample_size': self.metrics['sample_size'].get(product_id, 0)
                })
        
        total_products = len(self.product_elasticity)
        high_quality_count = total_products - len(low_quality_products)
        
        return {
            'is_valid': True,
            'total_products': total_products,
            'high_quality_products': high_quality_count,
            'low_quality_products': len(low_quality_products),
            'quality_rate': round(high_quality_count / total_products * 100, 1) if total_products > 0 else 0,
            'low_quality_details': low_quality_products,
            'recommendation': (
                f"✅ Good quality - {high_quality_count}/{total_products} products have R² >= {min_r_squared}"
                if len(low_quality_products) < total_products * 0.3
                else f"⚠️ Need more data - {len(low_quality_products)}/{total_products} products have low R²"
            )
        }


# Factory function
def create_price_elasticity_calculator() -> PriceElasticityCalculator:
    """
    Factory function to create PriceElasticityCalculator instance
    
    Returns:
        PriceElasticityCalculator instance
    """
    return PriceElasticityCalculator()
