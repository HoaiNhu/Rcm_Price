"""
Data Access endpoints router
MongoDB data access for orders, products, users, ratings, discounts, search histories
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import logging
import pandas as pd

from infrastructure.db.mongodb_access import mongodb_data
from utils.numpy_serializer import convert_numpy_types

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/data/orders")
async def get_orders_data(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of records"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get orders data from MongoDB"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        orders_df = mongodb_data.get_orders_data(start_dt, end_dt, limit)
        
        if orders_df.empty:
            return {"orders": [], "count": 0}
        
        # Convert DataFrame to dict and sanitize all types (ObjectId, numpy, datetime)
        orders = orders_df.to_dict('records')
        orders = convert_numpy_types(orders)
        
        return {
            "orders": orders,
            "count": len(orders),
            "filters": {
                "limit": limit,
                "start_date": start_date,
                "end_date": end_date
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[ERROR] Error getting orders data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/data/products")
async def get_products_data():
    """Get products data from MongoDB"""
    try:
        products_df = mongodb_data.get_products_data()
        
        if products_df.empty:
            return {"products": [], "count": 0}
        
        # Convert DataFrame to dict and sanitize all types
        products = products_df.to_dict('records')
        products = convert_numpy_types(products)
        
        return {
            "products": products,
            "count": len(products),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[ERROR] Error getting products data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/data/users")
async def get_users_data():
    """Get users data from MongoDB"""
    try:
        users_df = mongodb_data.get_users_data()
        
        if users_df.empty:
            return {"users": [], "count": 0}
        
        # Convert DataFrame to dict and sanitize all types
        users = users_df.to_dict('records')
        users = convert_numpy_types(users)
        
        return {
            "users": users,
            "count": len(users),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[ERROR] Error getting users data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/data/ratings")
async def get_ratings_data():
    """Get ratings data from MongoDB"""
    try:
        ratings_df = mongodb_data.get_ratings_data()
        
        if ratings_df.empty:
            return {"ratings": [], "count": 0}
        
        # Convert DataFrame to dict and sanitize all types
        ratings = ratings_df.to_dict('records')
        ratings = convert_numpy_types(ratings)
        
        return {
            "ratings": ratings,
            "count": len(ratings),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[ERROR] Error getting ratings data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/data/discounts")
async def get_discounts_data():
    """Get discounts data from MongoDB"""
    try:
        discounts_df = mongodb_data.get_discounts_data()
        
        if discounts_df.empty:
            return {"discounts": [], "count": 0}
        
        # Convert DataFrame to dict and sanitize all types
        discounts = discounts_df.to_dict('records')
        discounts = convert_numpy_types(discounts)
        
        return {
            "discounts": discounts,
            "count": len(discounts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[ERROR] Error getting discounts data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/data/search-histories")
async def get_search_histories_data():
    """Get search histories data from MongoDB"""
    try:
        search_df = mongodb_data.get_search_histories_data()
        
        if search_df.empty:
            return {"search_histories": [], "count": 0}
        
        # Convert DataFrame to dict and sanitize all types
        search_histories = search_df.to_dict('records')
        search_histories = convert_numpy_types(search_histories)
        
        return {
            "search_histories": search_histories,
            "count": len(search_histories),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[ERROR] Error getting search histories data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
