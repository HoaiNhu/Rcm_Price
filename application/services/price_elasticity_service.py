"""
Price Elasticity Service - Application Layer
Service để tính toán và quản lý price elasticity

Author: RCM_PRICE Team
Date: 2025-10-27
"""

import logging
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime, timedelta

from infrastructure.ml_models.price_elasticity import create_price_elasticity_calculator
from infrastructure.db.mongodb_access import MongoDBAccess

logger = logging.getLogger(__name__)


class PriceElasticityService:
    """
    Service layer cho Price Elasticity tính toán và quản lý
    
    Responsibilities:
    - Coordinate between database và ML calculator
    - Handle business logic for pricing recommendations
    - Provide API-friendly data structures
    """
    
    def __init__(self, db_access: MongoDBAccess):
        """
        Initialize Price Elasticity Service
        
        Args:
            db_access: MongoDB access instance
        """
        self.db = db_access
        self.calculator = create_price_elasticity_calculator()
        self.last_training_time: Optional[datetime] = None
        self.training_period_days = 90  # Use 90 days of data for training
        
        logger.info("✅ PriceElasticityService initialized")
    
    async def calculate_all_elasticities(
        self,
        days: int = 90,
        min_samples: int = 10,
        force_recalculate: bool = False
    ) -> Dict:
        """
        Tính toán elasticity cho tất cả sản phẩm
        
        Args:
            days: Số ngày data để phân tích
            min_samples: Số samples tối thiểu
            force_recalculate: Force tính lại dù đã có cache
            
        Returns:
            Dict chứa kết quả và metadata
        """
        try:
            logger.info(f"🔍 Starting elasticity calculation (last {days} days)...")
            
            # Check if we need to recalculate
            if not force_recalculate and self.calculator.is_trained:
                time_since_training = datetime.now() - self.last_training_time
                if time_since_training < timedelta(hours=24):
                    logger.info("✅ Using cached elasticity (< 24h old)")
                    return {
                        'success': True,
                        'cached': True,
                        'elasticity_data': self.calculator.product_elasticity,
                        'last_training_time': self.last_training_time.isoformat()
                    }
            
            # Fetch data from MongoDB
            orders_df = await self._fetch_orders_data(days)
            products_df = await self._fetch_products_data()
            
            if orders_df.empty:
                logger.warning("⚠️ No order data available")
                return {
                    'success': False,
                    'error': 'No order data available',
                    'products_count': len(products_df)
                }
            
            logger.info(
                f"📊 Data loaded: {len(orders_df)} orders, {len(products_df)} products"
            )
            
            # Calculate elasticity
            elasticity_results = self.calculator.calculate_elasticity(
                orders_df,
                products_df,
                min_samples=min_samples
            )
            
            self.last_training_time = datetime.now()
            
            # Get summary statistics
            summary = self.calculator.get_summary_statistics()
            
            logger.info(
                f"✅ Elasticity calculated for {len(elasticity_results)} products"
            )
            
            return {
                'success': True,
                'cached': False,
                'elasticity_data': elasticity_results,
                'summary': summary,
                'training_time': self.last_training_time.isoformat(),
                'data_period_days': days,
                'total_orders': len(orders_df),
                'total_products': len(products_df)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating elasticity: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_product_recommendation(
        self,
        product_id: str
    ) -> Dict:
        """
        Lấy recommendation cho một sản phẩm cụ thể
        
        Args:
            product_id: ID của sản phẩm
            
        Returns:
            Dict chứa recommendation details
        """
        try:
            # Ensure calculator is trained
            if not self.calculator.is_trained:
                logger.info("Calculator not trained, training now...")
                await self.calculate_all_elasticities()
            
            # Get product current price
            product = await self._fetch_product_by_id(product_id)
            
            if not product:
                return {
                    'success': False,
                    'error': f'Product {product_id} not found'
                }
            
            current_price = product.get('basePrice', 0)
            
            # Get recommendation
            recommendation = self.calculator.recommend_price_change(
                product_id,
                current_price
            )
            
            # Enrich with product information
            recommendation['product_name'] = product.get('name', 'Unknown')
            recommendation['category'] = product.get('category', 'Unknown')
            recommendation['success'] = True
            
            return recommendation
            
        except Exception as e:
            logger.error(f"❌ Error getting recommendation for {product_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'product_id': product_id
            }
    
    async def get_all_recommendations(self) -> Dict:
        """
        Lấy recommendations cho tất cả sản phẩm
        
        Returns:
            Dict chứa tất cả recommendations
        """
        try:
            # Ensure calculator is trained
            if not self.calculator.is_trained:
                logger.info("Calculator not trained, training now...")
                await self.calculate_all_elasticities()
            
            # Get all products
            products_df = await self._fetch_products_data()
            
            recommendations = []
            
            for _, product in products_df.iterrows():
                product_id = str(product['_id'])
                current_price = product.get('basePrice', 0)
                
                rec = self.calculator.recommend_price_change(
                    product_id,
                    current_price
                )
                
                # Enrich with product info
                rec['product_name'] = product.get('name', 'Unknown')
                rec['category'] = product.get('category', 'Unknown')
                
                recommendations.append(rec)
            
            # Group by sensitivity
            grouped = self._group_recommendations_by_sensitivity(recommendations)
            
            return {
                'success': True,
                'total_products': len(recommendations),
                'recommendations': recommendations,
                'grouped_by_sensitivity': grouped,
                'summary': self.calculator.get_summary_statistics()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting all recommendations: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_all_elasticities(self) -> Dict[str, Any]:
        """
        Get all elasticity data for all products (Phase 1 Enhanced LLM Integration)
        
        Returns:
            Dict with elasticity data for all products
        """
        try:
            logger.info("📊 Fetching all elasticity data for Phase 1...")
            
            # Ensure calculator is trained
            if not self.calculator.is_trained:
                logger.info("Calculator not trained, training now...")
                await self.calculate_all_elasticities()
            
            # Get all products
            products_df = await self._fetch_products_data()
            
            # Fetch orders with default parameters
            try:
                orders_df = await self._fetch_orders_data(days=90)
            except Exception as e:
                logger.warning(f"Could not fetch orders: {e}")
                orders_df = pd.DataFrame()
            
            results = []
            
            for _, product in products_df.iterrows():
                product_id = str(product['_id'])
                current_price = product.get('productPrice', 0)
                
                # Get elasticity from calculator
                try:
                    elasticity_value = self.calculator.elasticities.get(product_id, 0)
                except:
                    elasticity_value = 0
                
                # Get recommendation
                rec = self.calculator.recommend_price_change(product_id, current_price)
                
                results.append({
                    "product_id": product_id,
                    "product_name": product.get('productName', 'Unknown'),
                    "current_price": float(current_price) if current_price else 0,
                    "elasticity": float(elasticity_value) if elasticity_value else 0,
                    "sensitivity": rec.get('sensitivity', 'NO_DATA'),
                    "can_increase_price": rec.get('can_increase', False),
                    "recommended_action": rec.get('recommendation', 'No recommendation')
                })
            
            logger.info(f"✅ Fetched elasticity data for {len(results)} products")
            
            return {
                "products": results,
                "total_products": len(results),
                "summary": self.calculator.get_summary_statistics(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting all elasticities: {e}")
            return {
                "error": str(e),
                "products": [],
                "total_products": 0
            }
    
    async def get_elasticity_report(self) -> Dict:
        """
        Lấy báo cáo chi tiết về elasticity
        
        Returns:
            Dict chứa detailed report
        """
        try:
            # Ensure calculator is trained
            if not self.calculator.is_trained:
                logger.info("Calculator not trained, training now...")
                await self.calculate_all_elasticities()
            
            # Get report DataFrame
            report_df = self.calculator.get_elasticity_report()
            
            if report_df.empty:
                return {
                    'success': False,
                    'error': 'No elasticity data available'
                }
            
            # Convert to list of dicts for JSON serialization
            report_list = report_df.to_dict('records')
            
            # Get summary
            summary = self.calculator.get_summary_statistics()
            
            # Get quality validation
            quality = self.calculator.validate_elasticity_quality()
            
            return {
                'success': True,
                'report': report_list,
                'summary': summary,
                'quality_validation': quality,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def simulate_price_change(
        self,
        product_id: str,
        new_price: float
    ) -> Dict:
        """
        Simulate tác động của việc thay đổi giá
        
        Args:
            product_id: ID của sản phẩm
            new_price: Giá mới đề xuất
            
        Returns:
            Dict chứa simulation results
        """
        try:
            # Get product current price
            product = await self._fetch_product_by_id(product_id)
            
            if not product:
                return {
                    'success': False,
                    'error': f'Product {product_id} not found'
                }
            
            current_price = product.get('basePrice', 0)
            
            if current_price == 0:
                return {
                    'success': False,
                    'error': 'Invalid current price'
                }
            
            # Calculate price change percentage
            price_change_pct = (new_price - current_price) / current_price
            
            # Get elasticity
            if product_id not in self.calculator.product_elasticity:
                # Calculate if not available
                await self.calculate_all_elasticities()
            
            if product_id not in self.calculator.product_elasticity:
                return {
                    'success': False,
                    'error': 'Insufficient data to calculate elasticity'
                }
            
            elasticity = self.calculator.product_elasticity[product_id]
            
            # Estimate quantity change using elasticity formula
            # % Change in Quantity = Elasticity × % Change in Price
            estimated_qty_change_pct = elasticity * price_change_pct
            
            # Get current average monthly sales
            avg_monthly_qty = await self._get_avg_monthly_sales(product_id)
            
            # Estimate new quantity
            estimated_new_qty = avg_monthly_qty * (1 + estimated_qty_change_pct)
            
            # Calculate revenue impact
            current_revenue = avg_monthly_qty * current_price
            estimated_new_revenue = estimated_new_qty * new_price
            revenue_change = estimated_new_revenue - current_revenue
            revenue_change_pct = revenue_change / current_revenue if current_revenue > 0 else 0
            
            # Risk assessment
            sensitivity = self.calculator.get_sensitivity_category(elasticity)
            recommendation = self.calculator.recommend_price_change(product_id, current_price)
            
            is_safe = abs(price_change_pct) <= recommendation['max_safe_increase_pct'] / 100
            
            return {
                'success': True,
                'product_id': product_id,
                'product_name': product.get('name', 'Unknown'),
                'current_price': current_price,
                'new_price': new_price,
                'price_change_pct': round(price_change_pct * 100, 2),
                'elasticity': round(elasticity, 3),
                'sensitivity': sensitivity,
                'estimated_quantity_change_pct': round(estimated_qty_change_pct * 100, 2),
                'current_monthly_quantity': round(avg_monthly_qty, 0),
                'estimated_new_monthly_quantity': round(estimated_new_qty, 0),
                'current_monthly_revenue': round(current_revenue, 0),
                'estimated_new_monthly_revenue': round(estimated_new_revenue, 0),
                'revenue_change': round(revenue_change, 0),
                'revenue_change_pct': round(revenue_change_pct * 100, 2),
                'is_safe_change': is_safe,
                'max_safe_price': recommendation['max_safe_price'],
                'recommendation': recommendation['recommendation']
            }
            
        except Exception as e:
            logger.error(f"❌ Error simulating price change: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ==================== Private Helper Methods ====================
    
    async def _fetch_orders_data(self, days: int) -> pd.DataFrame:
        """Fetch orders from MongoDB (async wrapper for sync call)"""
        try:
            # Don't filter by date - use ALL orders since data is historical
            # Filtering by 90 days would exclude all data!
            orders_df = self.db.get_orders_data()
            
            logger.info(f"📦 Fetched {len(orders_df)} orders from MongoDB (all historical data)")
            
            return orders_df
            
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return pd.DataFrame()
    
    async def _fetch_products_data(self) -> pd.DataFrame:
        """Fetch products from MongoDB (async wrapper for sync call)"""
        try:
            # Use sync method from MongoDBDataAccess
            products_df = self.db.get_products_data()
            
            logger.info(f"📦 Fetched {len(products_df)} products from MongoDB")
            
            return products_df
            
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return pd.DataFrame()
    
    async def _fetch_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Fetch single product by ID (async wrapper for sync call)"""
        try:
            from bson.objectid import ObjectId
            
            # Use sync MongoDB access
            collection = self.db.db[self.db.config.COLLECTIONS['products']]
            product = collection.find_one({
                '_id': ObjectId(product_id)
            })
            
            if product:
                product['_id'] = str(product['_id'])
            
            return product
            
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None
    
    async def _get_avg_monthly_sales(self, product_id: str) -> float:
        """Calculate average monthly sales quantity for a product (async wrapper)"""
        try:
            # Get all orders (no date filter since data is historical)
            orders_df = self.db.get_orders_data()
            
            if orders_df.empty:
                return 0
            
            total_qty = 0
            
            for _, order in orders_df.iterrows():
                if 'orderItems' in order and isinstance(order['orderItems'], list):
                    for item in order['orderItems']:
                        if isinstance(item, dict) and str(item.get('product', '')) == product_id:
                            total_qty += item.get('quantity', 0)
            
            # Average per month (assuming 3 months of data)
            avg_monthly = total_qty / 3
            
            return avg_monthly
            
        except Exception as e:
            logger.error(f"Error calculating avg sales: {e}")
            return 0
    
    def _group_recommendations_by_sensitivity(
        self,
        recommendations: List[Dict]
    ) -> Dict:
        """Group recommendations by sensitivity category"""
        grouped = {
            'VERY_SENSITIVE': [],
            'SENSITIVE': [],
            'MODERATE': [],
            'INSENSITIVE': [],
            'NO_DATA': []
        }
        
        for rec in recommendations:
            sensitivity = rec.get('sensitivity', 'NO_DATA')
            if not rec.get('can_increase', False):
                sensitivity = 'NO_DATA'
            
            grouped[sensitivity].append(rec)
        
        return grouped


# Factory function
def create_price_elasticity_service(db_access: MongoDBAccess) -> PriceElasticityService:
    """
    Factory function to create PriceElasticityService
    
    Args:
        db_access: MongoDB access instance
        
    Returns:
        PriceElasticityService instance
    """
    return PriceElasticityService(db_access)

# Singleton instance
_elasticity_service_instance: 'PriceElasticityService | None' = None

def get_elasticity_service() -> PriceElasticityService:
    """
    Get or create singleton instance of PriceElasticityService
    
    Returns:
        PriceElasticityService instance
    """
    global _elasticity_service_instance
    
    if _elasticity_service_instance is None:
        from infrastructure.db.mongodb_access import MongoDBAccess
        db_access = MongoDBAccess(use_async=False)  # Use SYNC client
        _elasticity_service_instance = PriceElasticityService(db_access)
    
    return _elasticity_service_instance

