"""
Analytics service for LuckyVista.
Provides platform-wide metrics, trends, and data analysis.
"""
from flask import session, current_app
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app import db
from app.models import User, Feedback
from app.services.tenant_service import TenantIsolationService


class AnalyticsService:
    """Service for analytics and metrics calculation."""
    
    def __init__(self):
        self.tenant_service = TenantIsolationService()
    
    def get_platform_metrics(self, tenant_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate platform-wide metrics.
        
        Args:
            tenant_filter: Optional tenant filter (admin can specify, users get their tenant)
        
        Returns:
            Dictionary with platform metrics
        """
        try:
            # Determine tenant filter
            if not self.tenant_service.is_admin():
                tenant_filter = session.get('tenant_id')
            
            # Base queries
            user_query = User.query
            feedback_query = Feedback.query
            
            # Apply tenant filter if specified
            if tenant_filter:
                user_query = user_query.filter_by(tenant=tenant_filter)
                feedback_query = feedback_query.filter_by(tenant=tenant_filter)
            
            # Calculate basic counts
            total_users = user_query.count()
            total_feedback = feedback_query.count()
            
            if total_feedback == 0:
                return {
                    'total_users': total_users,
                    'total_feedback': 0,
                    'average_overall_rating': 0,
                    'average_experience_rating': 0,
                    'positive_feedback_count': 0,
                    'negative_feedback_count': 0,
                    'neutral_feedback_count': 0,
                    'positive_to_negative_ratio': 0,
                    'most_common_sentiment': 'None'
                }
            
            # Calculate rating averages
            rating_stats = db.session.query(
                func.avg(Feedback.overall_rating).label('avg_overall'),
                func.avg(Feedback.experience_rating).label('avg_experience')
            )
            
            if tenant_filter:
                rating_stats = rating_stats.filter_by(tenant=tenant_filter)
            
            rating_result = rating_stats.first()
            avg_overall = float(rating_result.avg_overall) if rating_result.avg_overall else 0
            avg_experience = float(rating_result.avg_experience) if rating_result.avg_experience else 0
            
            # Calculate sentiment distribution
            sentiment_query = db.session.query(
                Feedback.sentiment_label,
                func.count(Feedback.id).label('count')
            )
            
            if tenant_filter:
                sentiment_query = sentiment_query.filter_by(tenant=tenant_filter)
            
            sentiment_counts = sentiment_query.group_by(Feedback.sentiment_label).all()
            
            # Process sentiment counts
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            sentiment_dict = {}
            
            for sentiment, count in sentiment_counts:
                sentiment_dict[sentiment] = count
                if sentiment.lower() == 'positive':
                    positive_count = count
                elif sentiment.lower() == 'negative':
                    negative_count = count
                elif sentiment.lower() == 'neutral':
                    neutral_count = count
            
            # Calculate positive to negative ratio
            if negative_count > 0:
                pos_neg_ratio = round(positive_count / negative_count, 2)
            else:
                pos_neg_ratio = positive_count if positive_count > 0 else 0
            
            # Find most common sentiment
            most_common_sentiment = 'None'
            if sentiment_dict:
                most_common_sentiment = max(sentiment_dict.items(), key=lambda x: x[1])[0]
            
            return {
                'total_users': total_users,
                'total_feedback': total_feedback,
                'average_overall_rating': round(avg_overall, 2),
                'average_experience_rating': round(avg_experience, 2),
                'positive_feedback_count': positive_count,
                'negative_feedback_count': negative_count,
                'neutral_feedback_count': neutral_count,
                'positive_to_negative_ratio': pos_neg_ratio,
                'most_common_sentiment': most_common_sentiment
            }
            
        except Exception as e:
            current_app.logger.error(f"Failed to calculate platform metrics: {str(e)}")
            return {
                'total_users': 0,
                'total_feedback': 0,
                'average_overall_rating': 0,
                'average_experience_rating': 0,
                'positive_feedback_count': 0,
                'negative_feedback_count': 0,
                'neutral_feedback_count': 0,
                'positive_to_negative_ratio': 0,
                'most_common_sentiment': 'Error'
            }
    
    def get_sentiment_distribution(self, tenant_filter: Optional[str] = None) -> Dict[str, int]:
        """
        Get sentiment distribution data for charts.
        
        Args:
            tenant_filter: Optional tenant filter
        
        Returns:
            Dictionary with sentiment counts
        """
        try:
            # Determine tenant filter
            if not self.tenant_service.is_admin():
                tenant_filter = session.get('tenant_id')
            
            query = db.session.query(
                Feedback.sentiment_label,
                func.count(Feedback.id).label('count')
            )
            
            if tenant_filter:
                query = query.filter_by(tenant=tenant_filter)
            
            results = query.group_by(Feedback.sentiment_label).all()
            
            # Convert to dictionary
            distribution = {}
            for sentiment, count in results:
                distribution[sentiment] = count
            
            # Ensure all sentiment types are present
            for sentiment in ['Positive', 'Negative', 'Neutral', 'Unclassified']:
                if sentiment not in distribution:
                    distribution[sentiment] = 0
            
            return distribution
            
        except Exception as e:
            current_app.logger.error(f"Failed to get sentiment distribution: {str(e)}")
            return {'Positive': 0, 'Negative': 0, 'Neutral': 0, 'Unclassified': 0}
    
    def get_rating_breakdown(self, tenant_filter: Optional[str] = None) -> Dict[str, int]:
        """
        Get rating breakdown data for charts.
        
        Args:
            tenant_filter: Optional tenant filter
        
        Returns:
            Dictionary with rating counts
        """
        try:
            # Determine tenant filter
            if not self.tenant_service.is_admin():
                tenant_filter = session.get('tenant_id')
            
            query = db.session.query(
                Feedback.overall_rating,
                func.count(Feedback.id).label('count')
            )
            
            if tenant_filter:
                query = query.filter_by(tenant=tenant_filter)
            
            results = query.group_by(Feedback.overall_rating).all()
            
            # Convert to dictionary with string keys for consistency
            breakdown = {}
            for rating, count in results:
                breakdown[f"{rating} Stars"] = count
            
            # Ensure all ratings are present
            for rating in range(1, 6):
                key = f"{rating} Stars"
                if key not in breakdown:
                    breakdown[key] = 0
            
            return breakdown
            
        except Exception as e:
            current_app.logger.error(f"Failed to get rating breakdown: {str(e)}")
            return {f"{i} Stars": 0 for i in range(1, 6)}
    
    def get_feedback_trends(
        self, 
        days: int = 30, 
        granularity: str = 'day',
        tenant_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get feedback trends over time.
        
        Args:
            days: Number of days to look back
            granularity: Time granularity ('day', 'week', 'month')
            tenant_filter: Optional tenant filter
        
        Returns:
            List of trend data points
        """
        try:
            # Determine tenant filter
            if not self.tenant_service.is_admin():
                tenant_filter = session.get('tenant_id')
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Build base query
            query = db.session.query(
                func.date(Feedback.created_at).label('date'),
                func.count(Feedback.id).label('count'),
                func.avg(Feedback.overall_rating).label('avg_rating')
            )
            
            if tenant_filter:
                query = query.filter_by(tenant=tenant_filter)
            
            query = query.filter(
                and_(
                    Feedback.created_at >= start_date,
                    Feedback.created_at <= end_date
                )
            )
            
            # Group by date
            if granularity == 'week':
                query = query.group_by(func.date_trunc('week', Feedback.created_at))
            elif granularity == 'month':
                query = query.group_by(func.date_trunc('month', Feedback.created_at))
            else:  # day
                query = query.group_by(func.date(Feedback.created_at))
            
            query = query.order_by('date')
            
            results = query.all()
            
            # Convert to list of dictionaries
            trends = []
            for date, count, avg_rating in results:
                trends.append({
                    'date': date.isoformat() if date else None,
                    'feedback_count': count,
                    'average_rating': round(float(avg_rating), 2) if avg_rating else 0
                })
            
            return trends
            
        except Exception as e:
            current_app.logger.error(f"Failed to get feedback trends: {str(e)}")
            return []
    
    def get_tenant_comparison(self) -> List[Dict[str, Any]]:
        """
        Get comparison metrics across tenants (admin only).
        
        Returns:
            List of tenant metrics
        """
        try:
            # Only admin can access cross-tenant data
            if not self.tenant_service.is_admin():
                return []
            
            # Get tenant metrics
            tenant_stats = db.session.query(
                Feedback.tenant,
                func.count(Feedback.id).label('feedback_count'),
                func.avg(Feedback.overall_rating).label('avg_rating'),
                func.count(func.distinct(Feedback.user_id)).label('active_users')
            ).group_by(Feedback.tenant).all()
            
            # Get sentiment breakdown per tenant
            sentiment_stats = db.session.query(
                Feedback.tenant,
                Feedback.sentiment_label,
                func.count(Feedback.id).label('count')
            ).group_by(Feedback.tenant, Feedback.sentiment_label).all()
            
            # Organize sentiment data by tenant
            tenant_sentiments = {}
            for tenant, sentiment, count in sentiment_stats:
                if tenant not in tenant_sentiments:
                    tenant_sentiments[tenant] = {}
                tenant_sentiments[tenant][sentiment] = count
            
            # Combine data
            comparison = []
            for tenant, feedback_count, avg_rating, active_users in tenant_stats:
                sentiments = tenant_sentiments.get(tenant, {})
                
                comparison.append({
                    'tenant': tenant,
                    'feedback_count': feedback_count,
                    'average_rating': round(float(avg_rating), 2) if avg_rating else 0,
                    'active_users': active_users,
                    'positive_count': sentiments.get('Positive', 0),
                    'negative_count': sentiments.get('Negative', 0),
                    'neutral_count': sentiments.get('Neutral', 0)
                })
            
            # Sort by feedback count descending
            comparison.sort(key=lambda x: x['feedback_count'], reverse=True)
            
            return comparison
            
        except Exception as e:
            current_app.logger.error(f"Failed to get tenant comparison: {str(e)}")
            return []
    
    def get_user_engagement_metrics(self, tenant_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user engagement metrics.
        
        Args:
            tenant_filter: Optional tenant filter
        
        Returns:
            Dictionary with engagement metrics
        """
        try:
            # Determine tenant filter
            if not self.tenant_service.is_admin():
                tenant_filter = session.get('tenant_id')
            
            # Base queries
            user_query = User.query
            feedback_query = Feedback.query
            
            if tenant_filter:
                user_query = user_query.filter_by(tenant=tenant_filter)
                feedback_query = feedback_query.filter_by(tenant=tenant_filter)
            
            # Calculate metrics
            total_users = user_query.count()
            active_users = db.session.query(func.count(func.distinct(Feedback.user_id)))
            
            if tenant_filter:
                active_users = active_users.filter_by(tenant=tenant_filter)
            
            active_users_count = active_users.scalar() or 0
            
            # Calculate engagement rate
            engagement_rate = 0
            if total_users > 0:
                engagement_rate = round((active_users_count / total_users) * 100, 2)
            
            # Get feedback per user statistics
            feedback_per_user = db.session.query(
                Feedback.user_id,
                func.count(Feedback.id).label('feedback_count')
            )
            
            if tenant_filter:
                feedback_per_user = feedback_per_user.filter_by(tenant=tenant_filter)
            
            feedback_per_user = feedback_per_user.group_by(Feedback.user_id).all()
            
            # Calculate average feedback per active user
            avg_feedback_per_user = 0
            if feedback_per_user:
                total_feedback_count = sum(count for _, count in feedback_per_user)
                avg_feedback_per_user = round(total_feedback_count / len(feedback_per_user), 2)
            
            return {
                'total_users': total_users,
                'active_users': active_users_count,
                'engagement_rate': engagement_rate,
                'average_feedback_per_user': avg_feedback_per_user
            }
            
        except Exception as e:
            current_app.logger.error(f"Failed to get user engagement metrics: {str(e)}")
            return {
                'total_users': 0,
                'active_users': 0,
                'engagement_rate': 0,
                'average_feedback_per_user': 0
            }
    
    def get_recent_activity(self, limit: int = 10, tenant_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent feedback activity.
        
        Args:
            limit: Number of recent items to return
            tenant_filter: Optional tenant filter
        
        Returns:
            List of recent feedback items
        """
        try:
            # Determine tenant filter
            if not self.tenant_service.is_admin():
                tenant_filter = session.get('tenant_id')
            
            query = db.session.query(
                Feedback.id,
                Feedback.overall_rating,
                Feedback.sentiment_label,
                Feedback.created_at,
                Feedback.tenant,
                User.name.label('user_name')
            ).join(User, Feedback.user_id == User.id)
            
            if tenant_filter:
                query = query.filter(Feedback.tenant == tenant_filter)
            
            recent_feedback = query.order_by(Feedback.created_at.desc()).limit(limit).all()
            
            activity = []
            for feedback_id, rating, sentiment, created_at, tenant, user_name in recent_feedback:
                activity.append({
                    'id': feedback_id,
                    'user_name': user_name,
                    'rating': rating,
                    'sentiment': sentiment,
                    'tenant': tenant,
                    'created_at': created_at.isoformat() if created_at else None
                })
            
            return activity
            
        except Exception as e:
            current_app.logger.error(f"Failed to get recent activity: {str(e)}")
            return []