"""
Feedback routes for LuckyVista.
"""
from flask import Blueprint, request, jsonify, session
from app import limiter
from app.services.feedback_service import FeedbackService
from app.services.auth_service import AuthenticationService
from app.services.audit_service import AuditService

bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

feedback_service = FeedbackService()
auth_service = AuthenticationService()
audit_service = AuditService()


def require_authentication():
    """Check if user is authenticated."""
    is_valid, user = auth_service.validate_session()
    if not is_valid:
        return jsonify({
            'success': False,
            'error': 'Authentication required'
        }), 401
    return None


@bp.route('', methods=['POST'])
@limiter.limit("10 per minute")
def submit_feedback():
    """
    Submit feedback endpoint.
    
    Request body:
        - overall_rating: Overall rating (1-5)
        - experience_rating: Experience rating (1-5)
        - comments: Feedback comments (minimum 10 characters)
        - feature_satisfaction: Optional feature satisfaction (1-5)
        - ui_rating: Optional UI rating (1-5)
        - recommendation_likelihood: Optional recommendation likelihood (1-10)
        - additional_suggestions: Optional additional suggestions
    
    Returns:
        JSON response with success status and feedback data or error
    """
    # Check authentication
    auth_error = require_authentication()
    if auth_error:
        return auth_error
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Extract required fields
        overall_rating = data.get('overall_rating')
        experience_rating = data.get('experience_rating')
        comments = data.get('comments')
        
        # Extract optional fields
        feature_satisfaction = data.get('feature_satisfaction')
        ui_rating = data.get('ui_rating')
        recommendation_likelihood = data.get('recommendation_likelihood')
        additional_suggestions = data.get('additional_suggestions')
        
        # Submit feedback
        success, feedback, error_msg, field = feedback_service.submit_feedback(
            overall_rating=overall_rating,
            experience_rating=experience_rating,
            comments=comments,
            feature_satisfaction=feature_satisfaction,
            ui_rating=ui_rating,
            recommendation_likelihood=recommendation_likelihood,
            additional_suggestions=additional_suggestions
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': error_msg,
                'field': field
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback': feedback.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Feedback submission failed'
        }), 500


@bp.route('/my-submissions', methods=['GET'])
@limiter.limit("30 per minute")
def get_my_submissions():
    """
    Get current user's feedback submissions.
    
    Returns:
        JSON response with list of user's feedback
    """
    # Check authentication
    auth_error = require_authentication()
    if auth_error:
        return auth_error
    
    try:
        feedback_list = feedback_service.get_user_feedback()
        
        return jsonify({
            'success': True,
            'feedback': [feedback.to_dict() for feedback in feedback_list],
            'count': len(feedback_list)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve feedback'
        }), 500


@bp.route('/<int:feedback_id>', methods=['GET'])
@limiter.limit("30 per minute")
def get_feedback(feedback_id):
    """
    Get specific feedback by ID.
    
    Args:
        feedback_id: Feedback ID
    
    Returns:
        JSON response with feedback data or error
    """
    # Check authentication
    auth_error = require_authentication()
    if auth_error:
        return auth_error
    
    try:
        feedback = feedback_service.get_feedback_by_id(feedback_id)
        
        if not feedback:
            return jsonify({
                'success': False,
                'error': 'Feedback not found or access denied'
            }), 404
        
        return jsonify({
            'success': True,
            'feedback': feedback.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve feedback'
        }), 500


@bp.route('/stats', methods=['GET'])
@limiter.limit("20 per minute")
def get_feedback_stats():
    """
    Get feedback statistics for current user's tenant.
    
    Returns:
        JSON response with feedback statistics
    """
    # Check authentication
    auth_error = require_authentication()
    if auth_error:
        return auth_error
    
    try:
        stats = feedback_service.get_feedback_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve feedback statistics'
        }), 500