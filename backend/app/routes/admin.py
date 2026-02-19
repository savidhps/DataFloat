"""
Admin routes for LuckyVista.
"""
from flask import Blueprint, request, jsonify, session
from app import limiter
from app.models import User, Feedback
from app.services.analytics_service import AnalyticsService
from app.services.feedback_service import FeedbackService
from app.services.auth_service import AuthenticationService
from app.services.tenant_service import TenantIsolationService
from app.services.audit_service import AuditService
from datetime import datetime
import csv
import io

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

analytics_service = AnalyticsService()
feedback_service = FeedbackService()
auth_service = AuthenticationService()
tenant_service = TenantIsolationService()
audit_service = AuditService()


def require_admin():
    """Check if user is authenticated and has admin role using JWT token."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({
            'success': False,
            'error': 'Authentication required'
        }), 401
    
    token = auth_header.split(' ')[1]
    is_valid, payload = auth_service.verify_token(token)
    
    if not is_valid:
        return jsonify({
            'success': False,
            'error': 'Invalid or expired token'
        }), 401
    
    # Get user from database
    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 401
    
    if not user.is_admin():
        return jsonify({
            'success': False,
            'error': 'Admin access required'
        }), 403
    
    # Store user in request context
    request.current_user = user
    
    # Temporarily set session for legacy service methods
    session['user_id'] = user.id
    session['tenant_id'] = user.tenant
    session['role'] = user.role
    
    return None


@bp.route('/metrics', methods=['GET'])
@limiter.limit("20 per minute")
def get_platform_metrics():
    """
    Get platform-wide metrics.
    
    Query parameters:
        - tenant: Optional tenant filter
    
    Returns:
        JSON response with platform metrics
    """
    # Check admin access
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        tenant_filter = request.args.get('tenant')
        metrics = analytics_service.get_platform_metrics(tenant_filter)
        
        # Log admin access
        audit_service.log_admin_access('metrics', 'view')
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve metrics'
        }), 500


@bp.route('/sentiment-distribution', methods=['GET'])
@limiter.limit("20 per minute")
def get_sentiment_distribution():
    """
    Get sentiment distribution data for charts.
    
    Query parameters:
        - tenant: Optional tenant filter
    
    Returns:
        JSON response with sentiment distribution
    """
    # Check admin access
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        tenant_filter = request.args.get('tenant')
        distribution = analytics_service.get_sentiment_distribution(tenant_filter)
        
        # Log admin access
        audit_service.log_admin_access('sentiment_distribution', 'view')
        
        return jsonify({
            'success': True,
            'distribution': distribution
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve sentiment distribution'
        }), 500


@bp.route('/rating-breakdown', methods=['GET'])
@limiter.limit("20 per minute")
def get_rating_breakdown():
    """
    Get rating breakdown data for charts.
    
    Query parameters:
        - tenant: Optional tenant filter
    
    Returns:
        JSON response with rating breakdown
    """
    # Check admin access
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        tenant_filter = request.args.get('tenant')
        breakdown = analytics_service.get_rating_breakdown(tenant_filter)
        
        # Log admin access
        audit_service.log_admin_access('rating_breakdown', 'view')
        
        return jsonify({
            'success': True,
            'breakdown': breakdown
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve rating breakdown'
        }), 500


@bp.route('/trends', methods=['GET'])
@limiter.limit("20 per minute")
def get_feedback_trends():
    """
    Get feedback trends over time.
    
    Query parameters:
        - days: Number of days to look back (default: 30)
        - granularity: Time granularity ('day', 'week', 'month', default: 'day')
        - tenant: Optional tenant filter
    
    Returns:
        JSON response with trend data
    """
    # Check admin access
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        days = int(request.args.get('days', 30))
        granularity = request.args.get('granularity', 'day')
        tenant_filter = request.args.get('tenant')
        
        # Validate parameters
        if days < 1 or days > 365:
            return jsonify({
                'success': False,
                'error': 'Days must be between 1 and 365'
            }), 400
        
        if granularity not in ['day', 'week', 'month']:
            return jsonify({
                'success': False,
                'error': 'Granularity must be day, week, or month'
            }), 400
        
        trends = analytics_service.get_feedback_trends(days, granularity, tenant_filter)
        
        # Log admin access
        audit_service.log_admin_access('trends', 'view')
        
        return jsonify({
            'success': True,
            'trends': trends
        }), 200
    
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid days parameter'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve trends'
        }), 500


@bp.route('/feedback', methods=['GET'])
@limiter.limit("20 per minute")
def get_all_feedback():
    """
    Get all feedback with optional filtering.
    
    Query parameters:
        - sentiment: Filter by sentiment
        - rating: Filter by overall rating
        - tenant: Filter by tenant
        - date_from: Filter by start date (YYYY-MM-DD)
        - date_to: Filter by end date (YYYY-MM-DD)
        - limit: Number of results (default: 50, max: 200)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON response with filtered feedback
    """
    # Check admin access
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        # Parse filters
        filters = {}
        
        if request.args.get('sentiment'):
            filters['sentiment'] = request.args.get('sentiment')
        
        if request.args.get('rating'):
            try:
                filters['overall_rating'] = int(request.args.get('rating'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid rating parameter'
                }), 400
        
        if request.args.get('tenant'):
            filters['tenant'] = request.args.get('tenant')
        
        if request.args.get('date_from'):
            try:
                filters['date_from'] = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid date_from format (use YYYY-MM-DD)'
                }), 400
        
        if request.args.get('date_to'):
            try:
                filters['date_to'] = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid date_to format (use YYYY-MM-DD)'
                }), 400
        
        # Parse pagination
        limit = min(int(request.args.get('limit', 50)), 200)
        offset = int(request.args.get('offset', 0))
        
        # Get feedback
        feedback_list = feedback_service.get_all_feedback(filters)
        
        # Apply pagination
        total_count = len(feedback_list)
        paginated_feedback = feedback_list[offset:offset + limit]
        
        # Log admin access
        audit_service.log_admin_access('feedback', 'view')
        
        return jsonify({
            'success': True,
            'feedback': [fb.to_dict() for fb in paginated_feedback],
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve feedback'
        }), 500


@bp.route('/users', methods=['GET'])
@limiter.limit("20 per minute")
def get_all_users():
    """
    Get all users with optional filtering.
    
    Query parameters:
        - tenant: Filter by tenant
        - limit: Number of results (default: 50, max: 200)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON response with user list
    """
    # Check admin access
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        # Parse parameters
        tenant_filter = request.args.get('tenant')
        limit = min(int(request.args.get('limit', 50)), 200)
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = User.query
        
        if tenant_filter:
            query = query.filter_by(tenant=tenant_filter)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
        
        # Log admin access
        audit_service.log_admin_access('users', 'view')
        
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users],
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve users'
        }), 500


@bp.route('/tenant-comparison', methods=['GET'])
@limiter.limit("10 per minute")
def get_tenant_comparison():
    """
    Get comparison metrics across tenants.
    
    Returns:
        JSON response with tenant comparison data
    """
    # Check admin access
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        comparison = analytics_service.get_tenant_comparison()
        
        # Log admin access
        audit_service.log_admin_access('tenant_comparison', 'view')
        
        return jsonify({
            'success': True,
            'comparison': comparison
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve tenant comparison'
        }), 500


@bp.route('/engagement', methods=['GET'])
@limiter.limit("20 per minute")
def get_engagement_metrics():
    """
    Get user engagement metrics.
    
    Query parameters:
        - tenant: Optional tenant filter
    
    Returns:
        JSON response with engagement metrics
    """
    # Check admin access
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        tenant_filter = request.args.get('tenant')
        metrics = analytics_service.get_user_engagement_metrics(tenant_filter)
        
        # Log admin access
        audit_service.log_admin_access('engagement', 'view')
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve engagement metrics'
        }), 500


@bp.route('/recent-activity', methods=['GET'])
@limiter.limit("30 per minute")
def get_recent_activity():
    """
    Get recent feedback activity.
    
    Query parameters:
        - limit: Number of items to return (default: 10, max: 50)
        - tenant: Optional tenant filter
    
    Returns:
        JSON response with recent activity
    """
    # Check admin access
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        tenant_filter = request.args.get('tenant')
        
        activity = analytics_service.get_recent_activity(limit, tenant_filter)
        
        # Log admin access
        audit_service.log_admin_access('recent_activity', 'view')
        
        return jsonify({
            'success': True,
            'activity': activity
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve recent activity'
        }), 500


@bp.route('/export', methods=['POST'])
@limiter.limit("5 per hour")
def export_data():
    """
    Export feedback data to CSV.
    
    Request body:
        - format: Export format ('csv')
        - filters: Optional filters (same as feedback endpoint)
    
    Returns:
        CSV file download
    """
    # Check admin access
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    try:
        data = request.get_json() or {}
        export_format = data.get('format', 'csv')
        
        if export_format != 'csv':
            return jsonify({
                'success': False,
                'error': 'Only CSV format is supported'
            }), 400
        
        # Get filters
        filters = data.get('filters', {})
        
        # Get all feedback with filters
        feedback_list = feedback_service.get_all_feedback(filters)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'User ID', 'Tenant', 'Overall Rating', 'Experience Rating',
            'Comments', 'Feature Satisfaction', 'UI Rating', 'Recommendation Likelihood',
            'Additional Suggestions', 'Sentiment Label', 'Sentiment Confidence',
            'Created At'
        ])
        
        # Write data
        for feedback in feedback_list:
            writer.writerow([
                feedback.id,
                feedback.user_id,
                feedback.tenant,
                feedback.overall_rating,
                feedback.experience_rating,
                feedback.comments,
                feedback.feature_satisfaction,
                feedback.ui_rating,
                feedback.recommendation_likelihood,
                feedback.additional_suggestions,
                feedback.sentiment_label,
                feedback.sentiment_confidence,
                feedback.created_at.isoformat() if feedback.created_at else ''
            ])
        
        # Log export
        audit_service.log_data_export(
            session.get('user_id'),
            session.get('tenant_id'),
            len(feedback_list)
        )
        
        # Return CSV content
        csv_content = output.getvalue()
        output.close()
        
        return jsonify({
            'success': True,
            'csv_content': csv_content,
            'record_count': len(feedback_list)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to export data'
        }), 500