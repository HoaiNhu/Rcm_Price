"""
Analytics & Reporting endpoints router
Business analytics, product performance, customer insights, market trends
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
import pandas as pd

from infrastructure.db.mongodb_access import mongodb_data
from utils.numpy_serializer import convert_numpy_types

logger = logging.getLogger(__name__)
router = APIRouter()

# Global services (will be injected from main.py)
promotion_service = None

def set_global_services(promo_service):
    """Set global services from main.py"""
    global promotion_service
    promotion_service = promo_service

@router.get("/api/analytics/business-health")
async def get_business_analytics():
    """Get comprehensive business analytics"""
    try:
        if not promotion_service:
            raise HTTPException(status_code=500, detail="Promotion service not initialized")
        
        analytics = promotion_service.analyze_business_health()
        
        # Clean analytics data for JSON serialization
        clean_analytics = convert_numpy_types(analytics)
        
        return {
            "analytics": clean_analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[ERROR] Error getting business analytics: {e}")
        import traceback
        logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/analytics/product-performance")
async def get_product_performance():
    """Get product performance analytics"""
    try:
        orders_df = mongodb_data.get_orders_data()
        products_df = mongodb_data.get_products_data()
        ratings_df = mongodb_data.get_ratings_data()
        
        if orders_df.empty or products_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Flatten orderItems (handle nested structure from MongoDB)
        flattened_orders = []
        for _, order in orders_df.iterrows():
            if 'orderItems' in order and isinstance(order['orderItems'], list):
                for item in order['orderItems']:
                    if isinstance(item, dict):
                        flattened_orders.append({
                            'order_id': order['_id'],
                            'product_id': str(item.get('product', '')),
                            'quantity': item.get('quantity', 0),
                            'total': item.get('total', 0)
                        })
        
        # Convert to DataFrame for easier processing
        flat_df = pd.DataFrame(flattened_orders) if flattened_orders else pd.DataFrame()
        
        # Calculate product performance
        product_performance = []
        
        for _, product in products_df.iterrows():
            product_id = str(product['_id'])
            
            # Get orders for this product from flattened data
            if not flat_df.empty:
                product_orders = flat_df[flat_df['product_id'] == product_id]
                orders_count = len(product_orders)
                total_revenue = product_orders['total'].sum() if 'total' in product_orders.columns else 0
            else:
                orders_count = 0
                total_revenue = 0
            
            # Get ratings
            product_ratings = ratings_df[ratings_df['productId'] == product['_id']] if not ratings_df.empty else pd.DataFrame()
            avg_rating = product_ratings['rating'].mean() if not product_ratings.empty else 0
            
            # Safe conversion with NaN handling
            price = product.get('productPrice', 0)
            price = float(price) if pd.notna(price) else 0.0
            
            revenue = float(total_revenue) if pd.notna(total_revenue) else 0.0
            rating = float(avg_rating) if pd.notna(avg_rating) else 0.0
            
            performance = {
                'product_id': product_id,
                'product_name': product.get('productName', ''),
                'price': price,
                'orders_count': int(orders_count),
                'total_revenue': revenue,
                'avg_rating': rating,
                'total_ratings': len(product_ratings),
                'popularity_score': float(orders_count * (rating / 5.0 if rating > 0 else 0))
            }
            
            product_performance.append(performance)
        
        # Sort by popularity score
        product_performance.sort(key=lambda x: x['popularity_score'], reverse=True)
        
        # Clean data for JSON serialization
        clean_performance = convert_numpy_types(product_performance)
        
        return {
            "product_performance": clean_performance,
            "total_products": len(product_performance),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting product performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/analytics/customer-insights")
async def get_customer_insights():
    """Get customer insights and segmentation"""
    try:
        orders_df = mongodb_data.get_orders_data()
        users_df = mongodb_data.get_users_data()
        
        if orders_df.empty or users_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Customer analysis
        customer_insights = {
            'total_customers': len(users_df),
            'active_customers': len(orders_df['userId'].unique()) if 'userId' in orders_df.columns else 0,
            'repeat_customers': len(orders_df[orders_df['userId'].duplicated()]['userId'].unique()) if 'userId' in orders_df.columns else 0,
            'avg_orders_per_customer': len(orders_df) / len(users_df) if len(users_df) > 0 else 0
        }
        
        # Top customers by order count
        if 'userId' in orders_df.columns:
            customer_orders = orders_df['userId'].value_counts().head(10)
            top_customers = []
            
            for user_id, order_count in customer_orders.items():
                user_info = users_df[users_df['_id'] == user_id]
                if not user_info.empty:
                    top_customers.append({
                        'user_id': user_id,
                        'user_name': user_info.iloc[0].get('userName', ''),
                        'order_count': order_count
                    })
            
            customer_insights['top_customers'] = top_customers
        
        return {
            "customer_insights": customer_insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting customer insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/analytics/trends")
async def get_market_trends():
    """Get market trends and patterns"""
    try:
        orders_df = mongodb_data.get_orders_data()
        search_histories_df = mongodb_data.get_search_histories_data()
        
        if orders_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Time-based trends
        orders_df['createdAt'] = pd.to_datetime(orders_df['createdAt'])
        orders_df['date'] = orders_df['createdAt'].dt.date
        orders_df['month'] = orders_df['createdAt'].dt.month
        orders_df['weekday'] = orders_df['createdAt'].dt.weekday
        
        # Daily trends
        daily_trends = orders_df.groupby('date').size().to_dict()
        daily_trends = {str(k): int(v) for k, v in daily_trends.items()}
        
        # Monthly trends
        monthly_trends = orders_df.groupby('month').size().to_dict()
        monthly_trends = {str(k): int(v) for k, v in monthly_trends.items()}
        
        # Weekday trends
        weekday_trends = orders_df.groupby('weekday').size().to_dict()
        weekday_trends = {str(k): int(v) for k, v in weekday_trends.items()}
        
        # Search trends
        search_trends = {}
        if not search_histories_df.empty:
            search_trends = search_histories_df['query'].value_counts().head(10).to_dict()
            search_trends = {str(k): int(v) for k, v in search_trends.items()}
        
        trends = {
            'daily_trends': daily_trends,
            'monthly_trends': monthly_trends,
            'weekday_trends': weekday_trends,
            'search_trends': search_trends
        }
        
        # Clean trends data for JSON serialization
        clean_trends = convert_numpy_types(trends)
        
        return {
            "trends": clean_trends,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

