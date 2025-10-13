"""
Dynamic Pricing Models Integration
Tích hợp các models từ GitHub cho dynamic pricing
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from utils.numpy_serializer import convert_numpy_types
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class DynamicPricingModel:
    """Dynamic Pricing Model dựa trên các algorithms từ GitHub"""
    
    def __init__(self):
        self.demand_model = None
        self.price_elasticity_model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        logger.info("✅ Dynamic Pricing Model initialized")
    
    def prepare_pricing_data(self, orders_df: pd.DataFrame, products_df: pd.DataFrame, 
                            competitor_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Chuẩn bị dữ liệu cho dynamic pricing"""
        try:
            pricing_data = []
            
            # Convert dates
            orders_df['createdAt'] = pd.to_datetime(orders_df['createdAt'])
            orders_df['date'] = orders_df['createdAt'].dt.date
            
            # Flatten orderItems (handle nested structure from MongoDB)
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
            
            if not flattened_orders:
                logger.warning("No flattened order items found")
                return pd.DataFrame()
            
            flat_df = pd.DataFrame(flattened_orders)
            
            # Group by product and date
            for product_id in products_df['_id'].unique():
                product_info = products_df[products_df['_id'] == product_id].iloc[0]
                product_orders = flat_df[flat_df['product_id'] == str(product_id)]
                
                if product_orders.empty:
                    continue
                
                # Daily aggregation
                daily_stats = product_orders.groupby('date').agg({
                    'quantity': 'sum',
                    'total': 'sum'
                }).reset_index()
                
                for _, day_data in daily_stats.iterrows():
                    # Extract features
                    date = day_data['date']
                    quantity = day_data['quantity']
                    total_revenue = day_data['total']
                    avg_price = total_revenue / quantity if quantity > 0 else 0
                    
                    # Time features
                    weekday = date.weekday()
                    is_weekend = weekday >= 5
                    month = date.month
                    day_of_month = date.day
                    
                    # Seasonal features
                    is_holiday = self._is_holiday(date)
                    is_valentine = month == 2 and day_of_month in [14, 15]
                    is_christmas = month == 12 and day_of_month in range(20, 32)
                    
                    pricing_data.append({
                        'product_id': product_id,
                        'product_name': product_info.get('productName', ''),
                        'date': date,
                        'quantity': quantity,
                        'price': avg_price,
                        'revenue': total_revenue,
                        'weekday': weekday,
                        'is_weekend': is_weekend,
                        'month': month,
                        'day_of_month': day_of_month,
                        'is_holiday': is_holiday,
                        'is_valentine': is_valentine,
                        'is_christmas': is_christmas,
                        'product_price': product_info.get('productPrice', 0),
                        'product_rating': product_info.get('averageRating', 0)
                    })
            
            pricing_df = pd.DataFrame(pricing_data)
            
            if not pricing_df.empty:
                # Add lag features
                pricing_df = self._add_lag_features(pricing_df)
                
                # Add moving averages
                pricing_df = self._add_moving_averages(pricing_df)
            
            logger.info(f"✅ Prepared pricing data: {len(pricing_df)} records")
            return pricing_df
            
        except Exception as e:
            logger.error(f"❌ Error preparing pricing data: {e}")
            return pd.DataFrame()
    
    def _is_holiday(self, date) -> bool:
        """Check if date is a holiday"""
        holidays = [
            (1, 1),   # New Year
            (2, 14),  # Valentine
            (3, 8),   # Women's Day
            (4, 30),  # Liberation Day
            (5, 1),   # Labor Day
            (6, 1),   # Children's Day
            (9, 2),   # National Day
            (12, 25)  # Christmas
        ]
        
        return (date.month, date.day) in holidays
    
    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lag features for time series analysis"""
        try:
            df = df.sort_values(['product_id', 'date'])
            
            # Add lag features
            for lag in [1, 2, 3, 7]:
                df[f'quantity_lag_{lag}'] = df.groupby('product_id')['quantity'].shift(lag)
                df[f'price_lag_{lag}'] = df.groupby('product_id')['price'].shift(lag)
            
            # Fill NaN values
            df = df.fillna(method='bfill').fillna(method='ffill')
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error adding lag features: {e}")
            return df
    
    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add moving averages"""
        try:
            df = df.sort_values(['product_id', 'date'])
            
            # Moving averages
            for window in [3, 7, 14]:
                df[f'quantity_ma_{window}'] = df.groupby('product_id')['quantity'].rolling(window=window).mean().reset_index(0, drop=True)
                df[f'price_ma_{window}'] = df.groupby('product_id')['price'].rolling(window=window).mean().reset_index(0, drop=True)
            
            # Fill NaN values
            df = df.fillna(method='bfill').fillna(method='ffill')
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error adding moving averages: {e}")
            return df
    
    def train_demand_model(self, pricing_df: pd.DataFrame):
        """Train demand prediction model"""
        try:
            if pricing_df.empty:
                logger.error("No pricing data available")
                return False
            
            # Prepare features
            feature_columns = [
                'price', 'weekday', 'is_weekend', 'month', 'day_of_month',
                'is_holiday', 'is_valentine', 'is_christmas', 'product_price', 'product_rating'
            ]
            
            # Add lag features
            lag_columns = [col for col in pricing_df.columns if 'lag_' in col]
            feature_columns.extend(lag_columns)
            
            # Add moving average features
            ma_columns = [col for col in pricing_df.columns if 'ma_' in col]
            feature_columns.extend(ma_columns)
            
            # Filter available features
            available_features = [col for col in feature_columns if col in pricing_df.columns]
            
            X = pricing_df[available_features].fillna(0)
            y = pricing_df['quantity']
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.demand_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.demand_model.fit(X_scaled, y)
            
            logger.info(f"✅ Demand model trained with {len(available_features)} features")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error training demand model: {e}")
            return False
    
    def train_price_elasticity_model(self, pricing_df: pd.DataFrame):
        """Train price elasticity model"""
        try:
            if pricing_df.empty:
                logger.error("No pricing data available")
                return False
            
            # Calculate price elasticity
            pricing_df['price_change'] = pricing_df.groupby('product_id')['price'].pct_change()
            pricing_df['quantity_change'] = pricing_df.groupby('product_id')['quantity'].pct_change()
            
            # Remove infinite and NaN values
            pricing_df = pricing_df.replace([np.inf, -np.inf], np.nan).dropna()
            
            if pricing_df.empty:
                logger.error("No valid elasticity data")
                return False
            
            # Features for elasticity
            feature_columns = [
                'price', 'weekday', 'is_weekend', 'month', 'is_holiday',
                'product_price', 'product_rating'
            ]
            
            available_features = [col for col in feature_columns if col in pricing_df.columns]
            
            X = pricing_df[available_features].fillna(0)
            y = pricing_df['quantity_change']
            
            # Train model
            self.price_elasticity_model = LinearRegression()
            self.price_elasticity_model.fit(X, y)
            
            logger.info(f"✅ Price elasticity model trained")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error training price elasticity model: {e}")
            return False
    
    def optimize_price(self, product_id: str, current_price: float, 
                      target_date: datetime, pricing_df: pd.DataFrame) -> Dict[str, Any]:
        """Optimize price for a specific product"""
        try:
            if not self.is_trained:
                logger.error("Models not trained yet")
                return {}
            
            # Get product data
            product_data = pricing_df[pricing_df['product_id'] == product_id]
            if product_data.empty:
                logger.warning(f"No data for product {product_id}")
                return {}
            
            # Prepare features for target date
            features = {
                'price': current_price,
                'weekday': target_date.weekday(),
                'is_weekend': target_date.weekday() >= 5,
                'month': target_date.month,
                'day_of_month': target_date.day,
                'is_holiday': self._is_holiday(target_date.date()),
                'is_valentine': target_date.month == 2 and target_date.day in [14, 15],
                'is_christmas': target_date.month == 12 and target_date.day in range(20, 32)
            }
            
            # Add product features
            product_info = product_data.iloc[0]
            features.update({
                'product_price': product_info.get('product_price', 0),
                'product_rating': product_info.get('product_rating', 0)
            })
            
            # Add lag features (use recent data)
            recent_data = product_data.tail(7)
            if not recent_data.empty:
                # Lag features for 1, 2, 3, 7 days
                for lag in [1, 2, 3, 7]:
                    idx = min(lag, len(recent_data)) - 1
                    features[f'quantity_lag_{lag}'] = recent_data['quantity'].iloc[-idx-1] if idx < len(recent_data) else 0
                    features[f'price_lag_{lag}'] = recent_data['price'].iloc[-idx-1] if idx < len(recent_data) else 0
                
                # Moving averages for 3, 7, 14 days
                for window in [3, 7, 14]:
                    if len(recent_data) >= window:
                        features[f'quantity_ma_{window}'] = recent_data['quantity'].tail(window).mean()
                        features[f'price_ma_{window}'] = recent_data['price'].tail(window).mean()
                    else:
                        features[f'quantity_ma_{window}'] = recent_data['quantity'].mean()
                        features[f'price_ma_{window}'] = recent_data['price'].mean()
            else:
                # No recent data - use zeros for all lag/MA features
                for lag in [1, 2, 3, 7]:
                    features[f'quantity_lag_{lag}'] = 0
                    features[f'price_lag_{lag}'] = 0
                for window in [3, 7, 14]:
                    features[f'quantity_ma_{window}'] = 0
                    features[f'price_ma_{window}'] = 0
            
            # Fill missing features
            for key, value in features.items():
                if pd.isna(value):
                    features[key] = 0
            
            # Test different prices
            price_range = np.linspace(current_price * 0.8, current_price * 1.2, 20)
            best_price = current_price
            best_revenue = 0
            price_analysis = []
            
            for test_price in price_range:
                features['price'] = test_price
                
                # Predict demand
                X_test = np.array([list(features.values())])
                X_scaled = self.scaler.transform(X_test)
                
                predicted_demand = self.demand_model.predict(X_scaled)[0]
                predicted_revenue = test_price * predicted_demand
                
                price_analysis.append({
                    'price': test_price,
                    'predicted_demand': predicted_demand,
                    'predicted_revenue': predicted_revenue
                })
                
                if predicted_revenue > best_revenue:
                    best_revenue = predicted_revenue
                    best_price = test_price
            
            # Calculate price elasticity
            elasticity = self._calculate_price_elasticity(current_price, best_price, pricing_df, product_id)
            
            result = {
                'product_id': product_id,
                'current_price': current_price,
                'optimal_price': best_price,
                'price_change_percentage': ((best_price - current_price) / current_price) * 100,
                'predicted_demand': self.demand_model.predict(self.scaler.transform([list(features.values())]))[0],
                'predicted_revenue': best_revenue,
                'price_elasticity': elasticity,
                'price_analysis': price_analysis,
                'recommendation': self._get_price_recommendation(best_price, current_price, elasticity)
            }
            
            # Convert numpy types to Python native types
            result = convert_numpy_types(result)
            
            logger.info(f"✅ Price optimization completed for product {product_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error optimizing price: {e}")
            return {}
    
    def _calculate_price_elasticity(self, current_price: float, new_price: float, 
                                  pricing_df: pd.DataFrame, product_id: str) -> float:
        """Calculate price elasticity"""
        try:
            product_data = pricing_df[pricing_df['product_id'] == product_id]
            if product_data.empty:
                return 0
            
            # Calculate average quantity at current price
            avg_quantity = product_data['quantity'].mean()
            
            # Estimate quantity change based on price change
            price_change_pct = (new_price - current_price) / current_price
            
            # Simple elasticity calculation
            elasticity = -price_change_pct * 0.5  # Assume moderate elasticity
            
            return elasticity
            
        except Exception as e:
            logger.error(f"❌ Error calculating price elasticity: {e}")
            return 0
    
    def _get_price_recommendation(self, optimal_price: float, current_price: float, 
                                elasticity: float) -> str:
        """Get price recommendation based on analysis"""
        price_change_pct = ((optimal_price - current_price) / current_price) * 100
        
        if price_change_pct > 10:
            return "Tăng giá mạnh - Sản phẩm có thể chịu được giá cao hơn"
        elif price_change_pct > 5:
            return "Tăng giá nhẹ - Cơ hội tăng doanh thu"
        elif price_change_pct < -10:
            return "Giảm giá mạnh - Cần khuyến mãi để tăng doanh số"
        elif price_change_pct < -5:
            return "Giảm giá nhẹ - Cạnh tranh giá"
        else:
            return "Giữ nguyên giá - Giá hiện tại đã tối ưu"
    
    def train_models(self, pricing_df: pd.DataFrame):
        """Train both demand and elasticity models"""
        try:
            success1 = self.train_demand_model(pricing_df)
            success2 = self.train_price_elasticity_model(pricing_df)
            
            self.is_trained = success1 and success2
            
            if self.is_trained:
                logger.info("✅ Both pricing models trained successfully")
            else:
                logger.error("❌ Failed to train pricing models")
            
            return self.is_trained
            
        except Exception as e:
            logger.error(f"❌ Error training pricing models: {e}")
            return False
    
    def get_promotion_strategy(self, products_df: pd.DataFrame, pricing_df: pd.DataFrame) -> Dict[str, Any]:
        """Get promotion strategy for all products"""
        try:
            if not self.is_trained:
                logger.error("Models not trained yet")
                return {}
            
            promotion_strategy = {
                'increase_price': [],
                'decrease_price': [],
                'keep_price': [],
                'promotion_candidates': []
            }
            
            for _, product in products_df.iterrows():
                product_id = product['_id']
                current_price = product.get('productPrice', 0)
                
                if current_price == 0:
                    continue
                
                # Optimize price for next week
                target_date = datetime.now() + timedelta(days=7)
                optimization_result = self.optimize_price(product_id, current_price, target_date, pricing_df)
                
                if not optimization_result:
                    continue
                
                price_change_pct = optimization_result['price_change_percentage']
                
                product_info = {
                    'product_id': product_id,
                    'product_name': product.get('productName', ''),
                    'current_price': current_price,
                    'optimal_price': optimization_result['optimal_price'],
                    'price_change_percentage': price_change_pct,
                    'predicted_revenue': optimization_result['predicted_revenue'],
                    'recommendation': optimization_result['recommendation']
                }
                
                # Categorize by price change
                if price_change_pct > 5:
                    promotion_strategy['increase_price'].append(product_info)
                elif price_change_pct < -5:
                    promotion_strategy['decrease_price'].append(product_info)
                    promotion_strategy['promotion_candidates'].append(product_info)
                else:
                    promotion_strategy['keep_price'].append(product_info)
            
            # Convert numpy types to Python native types
            promotion_strategy = convert_numpy_types(promotion_strategy)
            
            logger.info("✅ Promotion strategy generated")
            return promotion_strategy
            
        except Exception as e:
            logger.error(f"❌ Error generating promotion strategy: {e}")
            return {}

# Factory function
def create_dynamic_pricing_model() -> DynamicPricingModel:
    """Create Dynamic Pricing Model instance"""
    return DynamicPricingModel()
