"""
Customer Segmentation Service - Application Layer
Orchestrates RFM-based customer segmentation with MongoDB integration
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd

from infrastructure.db.mongodb_access import MongoDBAccess
from infrastructure.ml_models.customer_segmentation import CustomerSegmentation

logger = logging.getLogger(__name__)


class CustomerSegmentationService:
    """
    Service để phân khúc khách hàng dựa trên RFM analysis
    
    Features:
    - Tự động phân khúc tất cả khách hàng từ MongoDB
    - Caching kết quả segmentation (24h)
    - Tích hợp với orders và users collections
    - Lấy thông tin chi tiết về từng segment
    - Recommendations cho từng segment
    """
    
    def __init__(self, mongodb_access: Optional[MongoDBAccess] = None):
        """
        Initialize service
        
        Args:
            mongodb_access: MongoDB connection (optional, created if None with async support)
        """
        # Use async MongoDB by default since this service uses async methods
        self.db = mongodb_access or MongoDBAccess(use_async=True)
        self.segmentation_model = CustomerSegmentation()
        
        # Cache
        self._cache: Dict = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(hours=24)
        
        logger.info("✅ CustomerSegmentationService initialized")
    
    async def segment_all_customers(
        self,
        reference_date: Optional[datetime] = None,
        force_refresh: bool = False
    ) -> Dict[str, str]:
        """
        Phân khúc tất cả khách hàng từ database
        
        Args:
            reference_date: Ngày tham chiếu (default: today)
            force_refresh: Bắt buộc tính toán lại (ignore cache)
            
        Returns:
            Dict mapping user_id -> segment_name
        """
        try:
            # Check cache
            if not force_refresh and self._is_cache_valid():
                logger.info("📦 Using cached segmentation results")
                return self._cache.get('segments', {})
            
            logger.info("🔍 Fetching customer data from MongoDB...")
            
            # Fetch orders from MongoDB
            orders_data = await self._fetch_orders()
            if not orders_data:
                logger.warning("⚠️ No orders found in database")
                return {}
            
            orders_df = pd.DataFrame(orders_data)
            
            # Fetch users from MongoDB
            users_data = await self._fetch_users()
            if not users_data:
                logger.warning("⚠️ No users found in database")
                return {}
            
            users_df = pd.DataFrame(users_data)
            
            # Perform segmentation
            logger.info(f"🎯 Segmenting {len(users_df)} customers based on {len(orders_df)} orders...")
            
            segments = self.segmentation_model.segment_customers(
                orders_df=orders_df,
                users_df=users_df,
                reference_date=reference_date
            )
            
            # Update cache
            self._cache = {
                'segments': segments,
                'rfm_data': self.segmentation_model.rfm_data,
                'segment_stats': self.segmentation_model.segment_stats,
                'reference_date': reference_date or datetime.now()
            }
            self._cache_timestamp = datetime.now()
            
            logger.info(f"✅ Segmented {len(segments)} customers into {len(self.segmentation_model.segment_stats)} segments")
            
            return segments
            
        except Exception as e:
            logger.error(f"❌ Error in segment_all_customers: {str(e)}")
            raise
    
    async def get_customer_segment(
        self,
        user_id: str,
        auto_segment: bool = True
    ) -> Optional[str]:
        """
        Lấy segment của một khách hàng cụ thể
        
        Args:
            user_id: ID của khách hàng
            auto_segment: Tự động phân khúc nếu chưa có data
            
        Returns:
            Segment name hoặc None
        """
        try:
            # Check cache
            if not self._is_cache_valid() and auto_segment:
                await self.segment_all_customers()
            
            segment = self._cache.get('segments', {}).get(user_id)
            
            if segment:
                logger.info(f"👤 Customer {user_id}: {segment}")
            else:
                logger.warning(f"⚠️ Customer {user_id} not found in segmentation")
            
            return segment
            
        except Exception as e:
            logger.error(f"❌ Error getting customer segment: {str(e)}")
            return None
    
    async def get_segment_customers(
        self,
        segment: str,
        auto_segment: bool = True
    ) -> List[str]:
        """
        Lấy danh sách khách hàng trong một segment
        
        Args:
            segment: Segment name (VIP, REGULAR, etc.)
            auto_segment: Tự động phân khúc nếu chưa có data
            
        Returns:
            List of user IDs
        """
        try:
            # Check cache
            if not self._is_cache_valid() and auto_segment:
                await self.segment_all_customers()
            
            segments_dict = self._cache.get('segments', {})
            
            customers = [
                user_id for user_id, seg in segments_dict.items()
                if seg == segment
            ]
            
            logger.info(f"📊 Segment {segment}: {len(customers)} customers")
            
            return customers
            
        except Exception as e:
            logger.error(f"❌ Error getting segment customers: {str(e)}")
            return []
    
    async def get_segment_report(
        self,
        auto_segment: bool = True
    ) -> pd.DataFrame:
        """
        Tạo báo cáo chi tiết về các segments
        
        Args:
            auto_segment: Tự động phân khúc nếu chưa có data
            
        Returns:
            DataFrame chứa segment report
        """
        try:
            # Check cache
            if not self._is_cache_valid() and auto_segment:
                await self.segment_all_customers()
            
            if not self._cache.get('segment_stats'):
                logger.warning("⚠️ No segment statistics available")
                return pd.DataFrame()
            
            # Use cached model state to generate report
            self.segmentation_model.segment_stats = self._cache['segment_stats']
            
            report = self.segmentation_model.get_segment_report()
            
            logger.info(f"📊 Generated segment report with {len(report)} segments")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating segment report: {str(e)}")
            return pd.DataFrame()
    
    async def segment_customers(self) -> Dict[str, Any]:
        """
        Segment all customers using RFM + K-Means (Phase 1 Enhanced LLM Integration)
        
        Returns:
            Dict with customer segments and distribution
        """
        try:
            logger.info("👥 Segmenting customers for Phase 1...")
            
            # Get customer segments (returns Dict[user_id, segment_name])
            segments_mapping = await self.segment_all_customers()
            
            if not segments_mapping:
                return {
                    "error": "No segment data available",
                    "customers": [],
                    "total_customers": 0
                }
            
            # Convert mapping to customers list with enriched data
            customers = []
            segment_counts = {}
            
            # Get RFM data from cache for enrichment
            rfm_data = self._cache.get('rfm_data', {})
            
            for user_id, segment in segments_mapping.items():
                # Get RFM scores if available
                user_rfm = rfm_data.get(user_id, {})
                
                customer_data = {
                    "user_id": user_id,
                    "segment": segment,
                    "recency": user_rfm.get('recency', 0),
                    "frequency": user_rfm.get('frequency', 0),
                    "monetary": user_rfm.get('monetary', 0),
                    "rfm_score": user_rfm.get('rfm_score', 0)
                }
                customers.append(customer_data)
                
                # Count segments
                segment_counts[segment] = segment_counts.get(segment, 0) + 1
            
            logger.info(f"✅ Segmented {len(customers)} customers into {len(segment_counts)} segments")
            
            return {
                "customers": customers,
                "total_customers": len(customers),
                "segment_distribution": segment_counts,
                "segments_defined": list(segment_counts.keys()),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error segmenting customers: {e}")
            return {
                "error": str(e),
                "customers": [],
                "total_customers": 0
            }
    
    async def get_summary_statistics(
        self,
        auto_segment: bool = True
    ) -> Dict:
        """
        Lấy thống kê tổng quan về segmentation
        
        Args:
            auto_segment: Tự động phân khúc nếu chưa có data
            
        Returns:
            Dict chứa summary statistics
        """
        try:
            # Check cache
            if not self._is_cache_valid() and auto_segment:
                await self.segment_all_customers()
            
            if not self._cache.get('segment_stats'):
                logger.warning("⚠️ No segment statistics available")
                return {}
            
            # Use cached model state to get summary
            self.segmentation_model.segment_stats = self._cache['segment_stats']
            
            summary = self.segmentation_model.get_summary_statistics()
            
            logger.info(f"📊 Summary: {summary.get('total_customers', 0)} customers, "
                       f"{summary.get('total_segments', 0)} segments")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting summary statistics: {str(e)}")
            return {}
    
    async def get_customer_details(
        self,
        user_id: str,
        auto_segment: bool = True
    ) -> Dict:
        """
        Lấy thông tin chi tiết về một khách hàng
        
        Args:
            user_id: ID của khách hàng
            auto_segment: Tự động phân khúc nếu chưa có data
            
        Returns:
            Dict chứa customer details (RFM scores, segment, recommendations)
        """
        try:
            # Check cache
            if not self._is_cache_valid() and auto_segment:
                await self.segment_all_customers()
            
            segment = self._cache.get('segments', {}).get(user_id)
            
            if not segment:
                logger.warning(f"⚠️ Customer {user_id} not found")
                return {}
            
            # Get RFM data from cache
            rfm_data = self._cache.get('rfm_data')
            
            if rfm_data is None or rfm_data.empty:
                logger.warning("⚠️ No RFM data available")
                return {}
            
            # Find customer in RFM data
            customer_rfm = rfm_data[rfm_data['user_id'] == user_id]
            
            if customer_rfm.empty:
                logger.warning(f"⚠️ No RFM data for customer {user_id}")
                return {}
            
            # Use cached model state
            self.segmentation_model.segments = self._cache['segments']
            self.segmentation_model.segment_stats = self._cache['segment_stats']
            
            # Get details
            details = self.segmentation_model.get_customer_details(user_id)
            
            logger.info(f"👤 Retrieved details for customer {user_id} ({segment})")
            
            return details
            
        except Exception as e:
            logger.error(f"❌ Error getting customer details: {str(e)}")
            return {}
    
    async def recommend_actions(
        self,
        segment: str
    ) -> Dict:
        """
        Lấy khuyến nghị hành động cho một segment
        
        Args:
            segment: Segment name
            
        Returns:
            Dict chứa action recommendations
        """
        try:
            recommendations = self.segmentation_model.recommend_actions(segment)
            
            logger.info(f"💡 Generated recommendations for segment {segment}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {str(e)}")
            return {}
    
    async def get_vip_customers(
        self,
        auto_segment: bool = True
    ) -> List[Dict]:
        """
        Lấy danh sách khách hàng VIP với thông tin chi tiết
        
        Args:
            auto_segment: Tự động phân khúc nếu chưa có data
            
        Returns:
            List of customer details
        """
        try:
            # Get VIP customer IDs
            vip_ids = await self.get_segment_customers('VIP', auto_segment)
            
            if not vip_ids:
                logger.warning("⚠️ No VIP customers found")
                return []
            
            # Get details for each VIP
            vip_customers = []
            
            for user_id in vip_ids:
                details = await self.get_customer_details(user_id, auto_segment=False)
                if details:
                    vip_customers.append(details)
            
            # Sort by total_spent descending
            vip_customers.sort(key=lambda x: x.get('monetary', 0), reverse=True)
            
            logger.info(f"👑 Retrieved {len(vip_customers)} VIP customers")
            
            return vip_customers
            
        except Exception as e:
            logger.error(f"❌ Error getting VIP customers: {str(e)}")
            return []
    
    async def get_at_risk_customers(
        self,
        auto_segment: bool = True
    ) -> List[Dict]:
        """
        Lấy danh sách khách hàng AT_RISK với thông tin chi tiết
        
        Args:
            auto_segment: Tự động phân khúc nếu chưa có data
            
        Returns:
            List of customer details
        """
        try:
            # Get AT_RISK customer IDs
            at_risk_ids = await self.get_segment_customers('AT_RISK', auto_segment)
            
            if not at_risk_ids:
                logger.info("✅ No at-risk customers found")
                return []
            
            # Get details for each at-risk customer
            at_risk_customers = []
            
            for user_id in at_risk_ids:
                details = await self.get_customer_details(user_id, auto_segment=False)
                if details:
                    at_risk_customers.append(details)
            
            # Sort by recency descending (most urgent first)
            at_risk_customers.sort(key=lambda x: x.get('recency', 0), reverse=True)
            
            logger.info(f"⚠️ Retrieved {len(at_risk_customers)} at-risk customers")
            
            return at_risk_customers
            
        except Exception as e:
            logger.error(f"❌ Error getting at-risk customers: {str(e)}")
            return []
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self._cache_timestamp:
            return False
        
        age = datetime.now() - self._cache_timestamp
        return age < self._cache_duration
    
    async def _fetch_orders(self) -> List[Dict]:
        """
        Fetch orders from MongoDB (async wrapper for sync call)
        
        Returns:
            List of order documents
        """
        try:
            # Use sync MongoDB access
            # Note: MongoDB uses userId, totalPrice, createdAt, orderItems
            collection = self.db.db[self.db.config.COLLECTIONS['orders']]
            orders = list(collection.find({}))
            
            logger.info(f"📦 Fetched {len(orders)} orders from MongoDB")
            
            return orders
            
        except Exception as e:
            logger.error(f"❌ Error fetching orders: {str(e)}")
            return []
    
    async def _fetch_users(self) -> List[Dict]:
        """
        Fetch users from MongoDB (async wrapper for sync call)
        
        Returns:
            List of user documents
        """
        try:
            # Use sync MongoDB access
            # Note: MongoDB uses userName, userEmail, createdAt
            collection = self.db.db[self.db.config.COLLECTIONS['users']]
            users = list(collection.find({}))
            
            logger.info(f"👥 Fetched {len(users)} users from MongoDB")
            
            return users
            
        except Exception as e:
            logger.error(f"❌ Error fetching users: {str(e)}")
            return []
    
    def clear_cache(self):
        """Xóa cache để force refresh"""
        self._cache = {}
        self._cache_timestamp = None
        logger.info("🗑️ Cache cleared")


# Factory function for easy instantiation
def create_segmentation_service(
    mongodb_access: Optional[MongoDBAccess] = None
) -> CustomerSegmentationService:
    """
    Factory function to create CustomerSegmentationService instance
    
    Args:
        mongodb_access: MongoDB connection (optional)
        
    Returns:
        CustomerSegmentationService instance
    """
    return CustomerSegmentationService(mongodb_access)

# Singleton instance
_segmentation_service_instance: 'CustomerSegmentationService | None' = None

def get_segmentation_service() -> CustomerSegmentationService:
    """
    Get or create singleton instance of CustomerSegmentationService
    
    Returns:
        CustomerSegmentationService instance
    """
    global _segmentation_service_instance
    
    if _segmentation_service_instance is None:
        from infrastructure.db.mongodb_access import MongoDBAccess
        db_access = MongoDBAccess(use_async=False)  # Use SYNC client
        _segmentation_service_instance = CustomerSegmentationService(db_access)
    
    return _segmentation_service_instance

