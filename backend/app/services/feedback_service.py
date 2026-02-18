"""
Feedback management service for LuckyVista.
Handles feedback submission, validation, and retrieval with tenant isolation.
"""
from flask import session, current_app
from typing import Tuple, Optional, List, Dict, Any
from app import db
from app.models import Feedback, User
from app.services.validation_service import ValidationService
from app.services.tenant_service import TenantIsolationService
from app.services.audit_service import AuditService
from datetime import datetime


class FeedbackService:
    """Service for managing feedback submissions and retrieval."""
    
    def __init__(self):
        self.validation_service = ValidationService()
        self.tenant_service = TenantIsolationService()
        self.audit_service = AuditService()
    
    def submit_feedback(
        self,
        overall_rating: int,
        experience_rating: int,
        comments: str,
        feature_satisfaction: Optional[int] = None,
        ui_rating: Optional[int] = None,
        recommendation_likelihood: Optional[int] = None,
        additional_suggestions: Optional[str] = None
    ) -> Tuple[bool, Optional[Feedback], Optional[str], Optional[str]]:
        """
        Submit feedback with validation and tenant association.
        
        Args:
            overall_rating: Overall rating (1-5)
            experience_rating: Experience rating (1-5)
            comments: Feedback comments (minimum 10 characters)
            feature_satisfaction: Optional feature satisfaction rating (1-5)
            ui_rating: Optional UI rating (1-5)
            recommendation_likelihood: Optional recommendation likelihood (1-10)
            additional_suggestions: Optional additional suggestions text
        
        Returns:
            Tuple of (success, feedback_object, error_message, field_name)
        """
        try:
            # Get user and tenant from session
            user_id = session.get('user_id')
            tenant_id = session.get('tenant_id')
            
            if not user_id or not tenant_id:
                return False, None, 'User not authenticated', None
            
            # Validate required fields
            validation_result = self._validate_feedback_data(
                overall_rating, experience_rating, comments,
                feature_satisfaction, ui_rating, recommendation_likelihood,
                additional_suggestions
            )
            
            if not validation_result[0]:
                return validation_result
            
            # Create feedback record
            feedback = Feedback(
                user_id=user_id,
                tenant=tenant_id,
                overall_rating=overall_rating,
                experience_rating=experience_rating,
                comments=comments.strip(),
                feature_satisfaction=feature_satisfaction,
                ui_rating=ui_rating,
                recommendation_likelihood=recommendation_likelihood,
                additional_suggestions=additional_suggestions.strip() if additional_suggestions else None,
                sentiment_label='Unclassified',  # Will be updated by sentiment analysis
                created_at=datetime.utcnow()
            )
            
            # Save to database
            db.session.add(feedback)
            db.session.commit()
            
            # Log feedback submission
            self.audit_service.log_feedback_submission(feedback.id, user_id, tenant_id)
            
            # Trigger sentiment analysis (will be implemented later)
            self._trigger_sentiment_analysis(feedback)
            
            return True, feedback, None, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Feedback submission failed: {str(e)}")
            return False, None, 'Feedback submission failed', None
    
    def get_user_feedback(self, user_id: Optional[int] = None) -> List[Feedback]:
        """
        Get feedback submissions for a specific user with tenant filtering.
        
        Args:
            user_id: User ID (uses session user if not provided)
        
        Returns:
            List of feedback objects
        """
        try:
            # Use session user if not provided
            if user_id is None:
                user_id = session.get('user_id')
            
            if not user_id:
                return []
            
            # Get tenant from session for filtering
            tenant_id = session.get('tenant_id')
            
            # Build query with tenant filtering
            query = Feedback.query.filter_by(user_id=user_id)
            
            # Apply tenant filtering (admin can see all)
            if not self.tenant_service.is_admin():
                if not tenant_id:
                    return []
                query = query.filter_by(tenant=tenant_id)
            
            # Order by creation date (newest first)
            feedback_list = query.order_by(Feedback.created_at.desc()).all()
            
            return feedback_list
            
        except Exception as e:
            current_app.logger.error(f"Failed to retrieve user feedback: {str(e)}")
            return []
    
    def get_feedback_by_id(self, feedback_id: int) -> Optional[Feedback]:
        """
        Get specific feedback by ID with tenant access validation.
        
        Args:
            feedback_id: Feedback ID
        
        Returns:
            Feedback object or None
        """
        try:
            feedback = Feedback.query.get(feedback_id)
            
            if not feedback:
                return None
            
            # Validate tenant access
            if not self.tenant_service.validate_tenant_access(feedback.tenant):
                # Log unauthorized access attempt
                self.tenant_service.log_unauthorized_access(
                    'feedback', feedback_id, feedback.tenant
                )
                return None
            
            return feedback
            
        except Exception as e:
            current_app.logger.error(f"Failed to retrieve feedback {feedback_id}: {str(e)}")
            return None
    
    def get_all_feedback(self, filters: Optional[Dict[str, Any]] = None) -> List[Feedback]:
        """
        Get all feedback with optional filtering (admin only).
        
        Args:
            filters: Optional filters (sentiment, rating, date_from, date_to, tenant)
        
        Returns:
            List of feedback objects
        """
        try:
            # Only admin can access all feedback
            if not self.tenant_service.is_admin():
                return []
            
            query = Feedback.query
            
            # Apply filters if provided
            if filters:
                if filters.get('sentiment'):
                    query = query.filter_by(sentiment_label=filters['sentiment'])
                
                if filters.get('overall_rating'):
                    query = query.filter_by(overall_rating=filters['overall_rating'])
                
                if filters.get('tenant'):
                    query = query.filter_by(tenant=filters['tenant'])
                
                if filters.get('date_from'):
                    query = query.filter(Feedback.created_at >= filters['date_from'])
                
                if filters.get('date_to'):
                    query = query.filter(Feedback.created_at <= filters['date_to'])
            
            # Order by creation date (newest first)
            feedback_list = query.order_by(Feedback.created_at.desc()).all()
            
            return feedback_list
            
        except Exception as e:
            current_app.logger.error(f"Failed to retrieve all feedback: {str(e)}")
            return []
    
    def update_sentiment(self, feedback_id: int, sentiment_label: str, confidence: Optional[float] = None) -> bool:
        """
        Update sentiment analysis results for feedback.
        
        Args:
            feedback_id: Feedback ID
            sentiment_label: Sentiment label (Positive, Negative, Neutral)
            confidence: Optional confidence score
        
        Returns:
            Success status
        """
        try:
            feedback = Feedback.query.get(feedback_id)
            
            if not feedback:
                return False
            
            # Validate sentiment label
            valid_sentiments = ['Positive', 'Negative', 'Neutral', 'Unclassified']
            if sentiment_label not in valid_sentiments:
                return False
            
            # Update sentiment
            feedback.sentiment_label = sentiment_label
            feedback.sentiment_confidence = confidence
            
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to update sentiment for feedback {feedback_id}: {str(e)}")
            return False
    
    def _validate_feedback_data(
        self,
        overall_rating: int,
        experience_rating: int,
        comments: str,
        feature_satisfaction: Optional[int],
        ui_rating: Optional[int],
        recommendation_likelihood: Optional[int],
        additional_suggestions: Optional[str]
    ) -> Tuple[bool, Optional[Feedback], Optional[str], Optional[str]]:
        """
        Validate feedback submission data.
        
        Returns:
            Tuple of (success, None, error_message, field_name)
        """
        # Validate overall rating
        if not isinstance(overall_rating, int) or overall_rating < 1 or overall_rating > 5:
            return False, None, 'Overall rating must be between 1 and 5', 'overall_rating'
        
        # Validate experience rating
        if not isinstance(experience_rating, int) or experience_rating < 1 or experience_rating > 5:
            return False, None, 'Experience rating must be between 1 and 5', 'experience_rating'
        
        # Validate comments
        if not comments or not isinstance(comments, str):
            return False, None, 'Comments are required', 'comments'
        
        comments = comments.strip()
        if len(comments) < 10:
            return False, None, 'Comments must be at least 10 characters long', 'comments'
        
        if len(comments) > 2000:
            return False, None, 'Comments must be less than 2000 characters', 'comments'
        
        # Check for injection patterns
        if self.validation_service.contains_injection_patterns(comments):
            return False, None, 'Comments contain invalid content', 'comments'
        
        # Validate optional fields
        if feature_satisfaction is not None:
            if not isinstance(feature_satisfaction, int) or feature_satisfaction < 1 or feature_satisfaction > 5:
                return False, None, 'Feature satisfaction must be between 1 and 5', 'feature_satisfaction'
        
        if ui_rating is not None:
            if not isinstance(ui_rating, int) or ui_rating < 1 or ui_rating > 5:
                return False, None, 'UI rating must be between 1 and 5', 'ui_rating'
        
        if recommendation_likelihood is not None:
            if not isinstance(recommendation_likelihood, int) or recommendation_likelihood < 1 or recommendation_likelihood > 10:
                return False, None, 'Recommendation likelihood must be between 1 and 10', 'recommendation_likelihood'
        
        # Validate additional suggestions
        if additional_suggestions is not None:
            if not isinstance(additional_suggestions, str):
                return False, None, 'Additional suggestions must be text', 'additional_suggestions'
            
            additional_suggestions = additional_suggestions.strip()
            if len(additional_suggestions) > 1000:
                return False, None, 'Additional suggestions must be less than 1000 characters', 'additional_suggestions'
            
            if self.validation_service.contains_injection_patterns(additional_suggestions):
                return False, None, 'Additional suggestions contain invalid content', 'additional_suggestions'
        
        return True, None, None, None
    
    def _trigger_sentiment_analysis(self, feedback: Feedback):
        """
        Trigger sentiment analysis for feedback.
        
        Args:
            feedback: Feedback object to analyze
        """
        try:
            from app.services.sentiment_service import SentimentAnalysisService
            
            sentiment_service = SentimentAnalysisService()
            sentiment_label, confidence = sentiment_service.classify_sentiment(feedback.comments)
            
            # Update feedback with sentiment results
            self.update_sentiment(feedback.id, sentiment_label, confidence)
            
            current_app.logger.info(f"Sentiment analysis completed for feedback {feedback.id}: {sentiment_label} ({confidence:.2f})")
            
        except Exception as e:
            current_app.logger.error(f"Sentiment analysis failed for feedback {feedback.id}: {str(e)}")
            # Leave sentiment as 'Unclassified' on failure
    
    def get_feedback_stats(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get feedback statistics for analytics.
        
        Args:
            tenant_id: Optional tenant filter (admin can specify, users get their tenant)
        
        Returns:
            Dictionary with feedback statistics
        """
        try:
            # Determine tenant filter
            if not self.tenant_service.is_admin():
                tenant_id = session.get('tenant_id')
            
            query = Feedback.query
            
            if tenant_id:
                query = query.filter_by(tenant=tenant_id)
            
            feedback_list = query.all()
            
            if not feedback_list:
                return {
                    'total_feedback': 0,
                    'average_overall_rating': 0,
                    'average_experience_rating': 0,
                    'sentiment_distribution': {},
                    'rating_distribution': {}
                }
            
            # Calculate statistics
            total_feedback = len(feedback_list)
            
            overall_ratings = [f.overall_rating for f in feedback_list]
            experience_ratings = [f.experience_rating for f in feedback_list]
            
            avg_overall = sum(overall_ratings) / len(overall_ratings)
            avg_experience = sum(experience_ratings) / len(experience_ratings)
            
            # Sentiment distribution
            sentiment_counts = {}
            for feedback in feedback_list:
                sentiment = feedback.sentiment_label
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            # Rating distribution
            rating_counts = {}
            for rating in overall_ratings:
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
            
            return {
                'total_feedback': total_feedback,
                'average_overall_rating': round(avg_overall, 2),
                'average_experience_rating': round(avg_experience, 2),
                'sentiment_distribution': sentiment_counts,
                'rating_distribution': rating_counts
            }
            
        except Exception as e:
            current_app.logger.error(f"Failed to get feedback stats: {str(e)}")
            return {
                'total_feedback': 0,
                'average_overall_rating': 0,
                'average_experience_rating': 0,
                'sentiment_distribution': {},
                'rating_distribution': {}
            }