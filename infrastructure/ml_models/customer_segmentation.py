"""
Customer Segmentation using RFM Analysis - Infrastructure Layer
Phân khúc khách hàng dựa trên Recency, Frequency, Monetary

RFM Metrics:
- Recency (R): Số ngày kể từ lần mua cuối
- Frequency (F): Số lần mua hàng
- Monetary (M): Tổng giá trị mua hàng

Segments:
- VIP: High F, High M, Low R (20% customers, 80% revenue)
- REGULAR: Medium F, Medium M, Medium R
- OCCASIONAL: Low F, Low M, High R
- NEW: First-time buyers
- AT_RISK: High F/M but High R (churn risk)
- LOST: Very High R (đã mất khách)

Author: RCM_PRICE Team
Date: 2025-10-27
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CustomerSegmentation:
    """
    Customer Segmentation using RFM Analysis + K-Means Clustering
    
    Attributes:
        rfm_data: DataFrame chứa RFM scores
        segments: Dict mapping customer_id -> segment
        segment_stats: Statistics cho từng segment
        kmeans_model: K-Means clustering model
        scaler: StandardScaler for normalization
        is_trained: Boolean indicating if segmentation has been performed
    """
    
    def __init__(self, n_clusters: int = 4):
        """
        Initialize Customer Segmentation
        
        Args:
            n_clusters: Số lượng segments (default: 4)
        """
        self.n_clusters = n_clusters
        self.rfm_data: Optional[pd.DataFrame] = None
        self.segments: Dict[str, str] = {}
        self.segment_stats: Dict[str, Dict] = {}
        self.kmeans_model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Segment definitions
        self.segment_definitions = {
            'VIP': {
                'description': 'Khách hàng VIP - Mua thường xuyên, chi tiêu cao',
                'recency_range': (0, 30),  # days
                'frequency_percentile': 75,
                'monetary_percentile': 75,
                'price_strategy': 'NEVER_INCREASE',  # Bảo vệ VIP
                'discount_eligibility': 'EXCLUSIVE'
            },
            'REGULAR': {
                'description': 'Khách hàng thường xuyên - Mua đều đặn',
                'recency_range': (0, 60),
                'frequency_percentile': 50,
                'monetary_percentile': 50,
                'price_strategy': 'CAREFUL_INCREASE',
                'discount_eligibility': 'STANDARD'
            },
            'OCCASIONAL': {
                'description': 'Khách hàng thỉnh thoảng - Mua ít',
                'recency_range': (60, 180),
                'frequency_percentile': 25,
                'monetary_percentile': 25,
                'price_strategy': 'CAN_INCREASE',
                'discount_eligibility': 'PROMOTIONAL'
            },
            'NEW': {
                'description': 'Khách hàng mới - Lần đầu mua',
                'recency_range': (0, 7),
                'frequency_percentile': 0,
                'monetary_percentile': 0,
                'price_strategy': 'CAREFUL_INCREASE',
                'discount_eligibility': 'WELCOME'
            },
            'AT_RISK': {
                'description': 'Khách hàng có nguy cơ mất - Từng mua nhiều nhưng lâu không mua',
                'recency_range': (90, 180),
                'frequency_percentile': 60,
                'monetary_percentile': 60,
                'price_strategy': 'NEVER_INCREASE',  # Win-back
                'discount_eligibility': 'WIN_BACK'
            },
            'LOST': {
                'description': 'Khách hàng đã mất - Rất lâu không mua',
                'recency_range': (180, 999999),
                'frequency_percentile': 0,
                'monetary_percentile': 0,
                'price_strategy': 'NEVER_INCREASE',
                'discount_eligibility': 'REACTIVATION'
            }
        }
        
        logger.info(f"✅ CustomerSegmentation initialized with {n_clusters} clusters")
    
    def segment_customers(
        self,
        orders_df: pd.DataFrame,
        users_df: pd.DataFrame,
        reference_date: Optional[datetime] = None
    ) -> Dict[str, str]:
        """
        Phân khúc khách hàng dựa trên RFM
        
        Args:
            orders_df: DataFrame chứa order history
            users_df: DataFrame chứa user information
            reference_date: Ngày tham chiếu để tính Recency (default: today)
            
        Returns:
            Dict mapping user_id -> segment name
        """
        logger.info(f"🔍 Segmenting {len(users_df)} customers...")
        
        if reference_date is None:
            reference_date = datetime.now()
        
        # Calculate RFM scores
        rfm_data = self._calculate_rfm(orders_df, users_df, reference_date)
        
        if rfm_data.empty:
            logger.warning("⚠️ No RFM data calculated")
            return {}
        
        # Perform K-Means clustering on RFM scores
        segments = self._perform_clustering(rfm_data)
        
        # Map clusters to business segments
        segments = self._map_to_business_segments(rfm_data, segments)
        
        # Store segments first (needed by _calculate_segment_statistics)
        self.segments = segments
        self.rfm_data = rfm_data
        
        # Calculate segment statistics
        self._calculate_segment_statistics(rfm_data)
        
        self.is_trained = True
        
        logger.info(f"✅ Segmented {len(segments)} customers into {len(self.segment_stats)} segments")
        
        return segments
    
    def _calculate_rfm(
        self,
        orders_df: pd.DataFrame,
        users_df: pd.DataFrame,
        reference_date: datetime
    ) -> pd.DataFrame:
        """
        Tính toán RFM scores cho từng khách hàng
        
        Args:
            orders_df: DataFrame chứa orders
            users_df: DataFrame chứa users
            reference_date: Ngày tham chiếu
            
        Returns:
            DataFrame với RFM scores
        """
        rfm_list = []
        
        for _, user in users_df.iterrows():
            user_id = str(user['_id'])
            
            # Get user's orders
            # Note: MongoDB uses 'userId' (ObjectId), need to convert for comparison
            user_orders = orders_df[orders_df['userId'].astype(str) == user_id]
            
            if len(user_orders) == 0:
                continue
            
            # Calculate Recency (days since last order)
            last_order_date = pd.to_datetime(user_orders['createdAt']).max()
            recency = (reference_date - last_order_date).days
            
            # Calculate Frequency (number of orders)
            frequency = len(user_orders)
            
            # Calculate Monetary (total spending)
            # Note: MongoDB uses 'totalPrice' not 'total_amount'
            monetary = user_orders['totalPrice'].sum()
            
            rfm_list.append({
                'user_id': user_id,
                'recency': recency,
                'frequency': frequency,
                'monetary': monetary,
                'last_order_date': last_order_date,
                'first_order_date': pd.to_datetime(user_orders['createdAt']).min(),
                'avg_order_value': monetary / frequency if frequency > 0 else 0
            })
        
        rfm_df = pd.DataFrame(rfm_list)
        
        if not rfm_df.empty:
            # Calculate RFM scores (1-5 scale)
            try:
                rfm_df['r_score'] = pd.qcut(
                    rfm_df['recency'], 
                    q=5, 
                    labels=[5, 4, 3, 2, 1],  # Lower recency = higher score
                    duplicates='drop'
                ).astype(int)
            except ValueError:
                # If not enough unique values, use simple ranking
                rfm_df['r_score'] = 6 - pd.cut(
                    rfm_df['recency'], 
                    bins=5, 
                    labels=[5, 4, 3, 2, 1],
                    duplicates='drop'
                ).astype(int)
            
            try:
                rfm_df['f_score'] = pd.qcut(
                    rfm_df['frequency'], 
                    q=5, 
                    labels=[1, 2, 3, 4, 5],  # Higher frequency = higher score
                    duplicates='drop'
                ).astype(int)
            except ValueError:
                rfm_df['f_score'] = pd.cut(
                    rfm_df['frequency'], 
                    bins=5, 
                    labels=[1, 2, 3, 4, 5],
                    duplicates='drop'
                ).astype(int)
            
            try:
                rfm_df['m_score'] = pd.qcut(
                    rfm_df['monetary'], 
                    q=5, 
                    labels=[1, 2, 3, 4, 5],  # Higher monetary = higher score
                    duplicates='drop'
                ).astype(int)
            except ValueError:
                rfm_df['m_score'] = pd.cut(
                    rfm_df['monetary'], 
                    bins=5, 
                    labels=[1, 2, 3, 4, 5],
                    duplicates='drop'
                ).astype(int)
            
            # Calculate combined RFM score
            rfm_df['rfm_score'] = rfm_df['r_score'] + rfm_df['f_score'] + rfm_df['m_score']
        
        logger.info(f"✅ Calculated RFM for {len(rfm_df)} customers")
        
        return rfm_df
    
    def _perform_clustering(self, rfm_data: pd.DataFrame) -> Dict[str, int]:
        """
        Perform K-Means clustering on RFM data
        
        Args:
            rfm_data: DataFrame with RFM scores
            
        Returns:
            Dict mapping user_id -> cluster_id
        """
        # Prepare features for clustering
        features = rfm_data[['recency', 'frequency', 'monetary']].values
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(features)
        
        # Perform clustering
        cluster_labels = self.kmeans_model.fit_predict(features_scaled)
        
        # Map user_id to cluster
        segments = {}
        for i, user_id in enumerate(rfm_data['user_id']):
            segments[user_id] = int(cluster_labels[i])
        
        logger.info(f"✅ K-Means clustering completed: {self.n_clusters} clusters")
        
        return segments
    
    def _map_to_business_segments(
        self,
        rfm_data: pd.DataFrame,
        clusters: Dict[str, int]
    ) -> Dict[str, str]:
        """
        Map K-Means clusters to business segments (VIP, REGULAR, etc.)
        
        Args:
            rfm_data: DataFrame with RFM data
            clusters: Dict mapping user_id -> cluster_id
            
        Returns:
            Dict mapping user_id -> segment_name
        """
        # Add cluster info to rfm_data
        rfm_data['cluster'] = rfm_data['user_id'].map(clusters)
        
        # Calculate cluster characteristics
        cluster_profiles = rfm_data.groupby('cluster').agg({
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': 'mean',
            'rfm_score': 'mean'
        }).reset_index()
        
        # Map clusters to business segments based on characteristics
        cluster_to_segment = {}
        
        for _, profile in cluster_profiles.iterrows():
            cluster_id = int(profile['cluster'])
            recency = profile['recency']
            frequency = profile['frequency']
            monetary = profile['monetary']
            
            # VIP: Low recency, high frequency, high monetary
            if recency < 30 and frequency >= rfm_data['frequency'].quantile(0.75):
                segment = 'VIP'
            
            # AT_RISK: High recency but historically good customer
            elif recency > 90 and frequency >= rfm_data['frequency'].quantile(0.6):
                segment = 'AT_RISK'
            
            # LOST: Very high recency
            elif recency > 180:
                segment = 'LOST'
            
            # NEW: Low frequency (1-2 orders)
            elif frequency <= 2:
                segment = 'NEW'
            
            # REGULAR: Medium metrics
            elif recency < 60 and frequency >= rfm_data['frequency'].quantile(0.4):
                segment = 'REGULAR'
            
            # OCCASIONAL: Everything else
            else:
                segment = 'OCCASIONAL'
            
            cluster_to_segment[cluster_id] = segment
        
        # Map users to segments
        business_segments = {}
        for user_id, cluster_id in clusters.items():
            business_segments[user_id] = cluster_to_segment[cluster_id]
        
        logger.info(f"✅ Mapped clusters to business segments:")
        for cluster_id, segment in cluster_to_segment.items():
            count = sum(1 for s in business_segments.values() if s == segment)
            logger.info(f"   • Cluster {cluster_id} → {segment}: {count} customers")
        
        return business_segments
    
    def _calculate_segment_statistics(self, rfm_data: pd.DataFrame):
        """Calculate statistics for each segment"""
        if 'segment' not in rfm_data.columns:
            rfm_data['segment'] = rfm_data['user_id'].map(self.segments)
        
        stats = {}
        
        for segment in rfm_data['segment'].unique():
            segment_data = rfm_data[rfm_data['segment'] == segment]
            
            stats[segment] = {
                'count': len(segment_data),
                'percentage': len(segment_data) / len(rfm_data) * 100,
                'avg_recency': segment_data['recency'].mean(),
                'avg_frequency': segment_data['frequency'].mean(),
                'avg_monetary': segment_data['monetary'].mean(),
                'total_revenue': segment_data['monetary'].sum(),
                'revenue_percentage': segment_data['monetary'].sum() / rfm_data['monetary'].sum() * 100,
                'avg_order_value': segment_data['avg_order_value'].mean(),
                'min_rfm_score': segment_data['rfm_score'].min(),
                'max_rfm_score': segment_data['rfm_score'].max(),
                'avg_rfm_score': segment_data['rfm_score'].mean()
            }
        
        self.segment_stats = stats
        logger.info(f"✅ Calculated statistics for {len(stats)} segments")
    
    def get_customer_segment(self, user_id: str) -> Optional[str]:
        """
        Lấy segment của một khách hàng
        
        Args:
            user_id: ID của khách hàng
            
        Returns:
            Segment name or None
        """
        return self.segments.get(user_id)
    
    def get_segment_customers(self, segment: str) -> List[str]:
        """
        Lấy danh sách khách hàng trong một segment
        
        Args:
            segment: Segment name
            
        Returns:
            List of user IDs
        """
        return [
            user_id for user_id, seg in self.segments.items() 
            if seg == segment
        ]
    
    def get_segment_report(self) -> pd.DataFrame:
        """
        Tạo báo cáo chi tiết về các segments
        
        Returns:
            DataFrame chứa segment report
        """
        if not self.segment_stats:
            logger.warning("No segment data available")
            return pd.DataFrame()
        
        report_data = []
        
        for segment, stats in self.segment_stats.items():
            definition = self.segment_definitions.get(segment, {})
            
            report_data.append({
                'segment': segment,
                'description': definition.get('description', 'N/A'),
                'customer_count': stats['count'],
                'customer_percentage': round(stats['percentage'], 2),
                'total_revenue': round(stats['total_revenue'], 0),
                'revenue_percentage': round(stats['revenue_percentage'], 2),
                'avg_recency_days': round(stats['avg_recency'], 1),
                'avg_frequency': round(stats['avg_frequency'], 1),
                'avg_monetary': round(stats['avg_monetary'], 0),
                'avg_order_value': round(stats['avg_order_value'], 0),
                'avg_rfm_score': round(stats['avg_rfm_score'], 1),
                'price_strategy': definition.get('price_strategy', 'N/A')
            })
        
        df = pd.DataFrame(report_data)
        
        # Sort by revenue_percentage descending
        df = df.sort_values('revenue_percentage', ascending=False)
        
        return df
    
    def get_summary_statistics(self) -> Dict:
        """
        Lấy thống kê tổng quan về segmentation
        
        Returns:
            Dict chứa summary statistics
        """
        if not self.segment_stats:
            return {}
        
        total_customers = sum(stats['count'] for stats in self.segment_stats.values())
        total_revenue = sum(stats['total_revenue'] for stats in self.segment_stats.values())
        
        # Find top segment by revenue
        top_segment = max(
            self.segment_stats.items(),
            key=lambda x: x[1]['revenue_percentage']
        )
        
        # Calculate 80/20 rule validation (VIP should contribute ~80% revenue)
        vip_revenue_pct = self.segment_stats.get('VIP', {}).get('revenue_percentage', 0)
        vip_customer_pct = self.segment_stats.get('VIP', {}).get('percentage', 0)
        
        return {
            'total_customers': total_customers,
            'total_revenue': round(total_revenue, 0),
            'total_segments': len(self.segment_stats),
            'top_segment_by_revenue': top_segment[0],
            'top_segment_revenue_pct': round(top_segment[1]['revenue_percentage'], 2),
            'vip_customers_pct': round(vip_customer_pct, 2),
            'vip_revenue_pct': round(vip_revenue_pct, 2),
            'pareto_principle_valid': vip_customer_pct <= 30 and vip_revenue_pct >= 60,
            'avg_customer_value': round(total_revenue / total_customers, 0) if total_customers > 0 else 0,
            'segment_distribution': {
                seg: stats['count'] 
                for seg, stats in self.segment_stats.items()
            }
        }
    
    def get_customer_details(self, user_id: str) -> Optional[Dict]:
        """
        Lấy chi tiết RFM và segment của một khách hàng
        
        Args:
            user_id: ID của khách hàng
            
        Returns:
            Dict chứa customer details
        """
        if self.rfm_data is None or user_id not in self.segments:
            return None
        
        customer_rfm = self.rfm_data[self.rfm_data['user_id'] == user_id]
        
        if customer_rfm.empty:
            return None
        
        row = customer_rfm.iloc[0]
        segment = self.segments[user_id]
        
        return {
            'user_id': user_id,
            'segment': segment,
            'segment_description': self.segment_definitions[segment]['description'],
            'recency_days': int(row['recency']),
            'frequency': int(row['frequency']),
            'monetary': float(row['monetary']),
            'avg_order_value': float(row['avg_order_value']),
            'r_score': int(row['r_score']),
            'f_score': int(row['f_score']),
            'm_score': int(row['m_score']),
            'rfm_score': int(row['rfm_score']),
            'last_order_date': row['last_order_date'].isoformat(),
            'first_order_date': row['first_order_date'].isoformat(),
            'price_strategy': self.segment_definitions[segment]['price_strategy'],
            'discount_eligibility': self.segment_definitions[segment]['discount_eligibility']
        }
    
    def recommend_actions(self, segment: str) -> Dict:
        """
        Đề xuất hành động cho một segment
        
        Args:
            segment: Segment name
            
        Returns:
            Dict chứa recommendations
        """
        actions = {
            'VIP': {
                'pricing': '🛡️ NEVER INCREASE - Bảo vệ VIP tuyệt đối',
                'promotion': 'Exclusive discounts, early access, VIP-only products',
                'communication': 'Personalized messages, birthday offers, loyalty rewards',
                'retention': 'Priority customer service, free shipping, special events',
                'goal': 'Maintain loyalty, increase lifetime value'
            },
            'REGULAR': {
                'pricing': '⚠️ CAREFUL INCREASE - Tối đa 5-8%',
                'promotion': 'Standard discounts, bundle offers, loyalty points',
                'communication': 'Regular newsletters, product recommendations',
                'retention': 'Encourage frequency increase, upgrade to VIP',
                'goal': 'Convert to VIP, maintain engagement'
            },
            'OCCASIONAL': {
                'pricing': '✅ CAN INCREASE - Tối đa 10-15%',
                'promotion': 'Aggressive promotions, flash sales, new customer offers',
                'communication': 'Re-engagement campaigns, personalized offers',
                'retention': 'Increase purchase frequency',
                'goal': 'Convert to REGULAR customers'
            },
            'NEW': {
                'pricing': '⚠️ CAREFUL - Tạo ấn tượng tốt',
                'promotion': 'Welcome discount 10-15%, first order incentives',
                'communication': 'Welcome series, product education',
                'retention': 'Encourage second purchase within 30 days',
                'goal': 'Convert to REGULAR customers quickly'
            },
            'AT_RISK': {
                'pricing': '🛡️ NEVER INCREASE - Win-back priority',
                'promotion': 'Win-back discounts 20-30%, exclusive offers',
                'communication': 'Re-engagement emails, "We miss you" campaigns',
                'retention': 'Address churn reasons, special incentives',
                'goal': 'Prevent churn, recover to REGULAR/VIP'
            },
            'LOST': {
                'pricing': '🛡️ NEVER INCREASE - Reactivation focus',
                'promotion': 'Reactivation offers 30-50%, apology discounts',
                'communication': 'Reactivation campaigns, survey for feedback',
                'retention': 'Major incentives to return',
                'goal': 'Reactivate if possible, learn from loss'
            }
        }
        
        return actions.get(segment, {
            'pricing': 'No specific strategy',
            'promotion': 'Standard approach',
            'communication': 'General messaging',
            'retention': 'Basic retention',
            'goal': 'Maintain customer base'
        })


# Factory function
def create_customer_segmentation(n_clusters: int = 4) -> CustomerSegmentation:
    """
    Factory function to create CustomerSegmentation instance
    
    Args:
        n_clusters: Number of clusters for K-Means
        
    Returns:
        CustomerSegmentation instance
    """
    return CustomerSegmentation(n_clusters=n_clusters)
