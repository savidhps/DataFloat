"""
Authentication routes for LuckyVista.
"""
from flask import Blueprint, request, jsonify, session, current_app
from app import limiter
from app.models import User
from app.services.auth_service import AuthenticationService
from app.services.audit_service import AuditService

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

auth_service = AuthenticationService()
audit_service = AuditService()


@bp.route('/signup', methods=['POST'])
@limiter.limit("3 per hour")
def signup():
    """
    User registration endpoint.
    
    Request body:
        - name: Full name
        - email: Email address
        - phone: Phone number
        - tenant: Organization/tenant identifier
        - password: Password
    
    Returns:
        JSON response with success status and user data or error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Extract fields
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        tenant = data.get('tenant')
        password = data.get('password')
        
        # Register user
        success, user, error_msg, field = auth_service.register_user(
            name, email, phone, tenant, password
        )
        
        if not success:
            # Log failed registration
            audit_service.log_registration(None, tenant, False)
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'field': field
            }), 400
        
        # Log successful registration
        audit_service.log_registration(user.id, user.tenant, True)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500


@bp.route('/signin', methods=['POST'])
@limiter.limit("20 per 15 minutes")
def signin():
    """
    User sign-in endpoint.
    
    Request body:
        - email: Email address
        - password: Password
    
    Returns:
        JSON response with success status and redirect URL or error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        # Authenticate user
        success, user, error_msg = auth_service.authenticate(email, password)
        
        if not success:
            # Log failed authentication
            audit_service.log_authentication(email, False)
            
            return jsonify({
                'success': False,
                'error': error_msg or 'Authentication failed'
            }), 401
        
        # Generate JWT token
        token = auth_service.generate_token(user)
        
        # Log successful authentication
        audit_service.log_authentication(email, True, user.id, user.tenant)
        
        # Determine redirect based on role
        redirect_url = '/admin/dashboard' if user.is_admin() else '/feedback'
        
        return jsonify({
            'success': True,
            'message': 'Sign-in successful',
            'token': token,
            'user': user.to_dict(),
            'redirect': redirect_url
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Signin error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Sign-in failed'
        }), 500


@bp.route('/signout', methods=['POST'])
def signout():
    """
    User sign-out endpoint.
    
    Returns:
        JSON response with success status
    """
    try:
        # Invalidate session
        auth_service.invalidate_session()
        
        return jsonify({
            'success': True,
            'message': 'Sign-out successful'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Sign-out failed'
        }), 500


@bp.route('/password-reset-request', methods=['POST'])
@limiter.limit("3 per hour")
def password_reset_request():
    """
    Request password reset token.
    
    Request body:
        - email: Email address
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        # Get user by email
        user = auth_service.get_user_by_email(email)
        
        if user:
            # Generate reset token
            token = auth_service.generate_reset_token(user.id)
            
            # Log password reset request
            audit_service.log_password_reset_request(email, user.id)
            
            # In production, send email with token
            # For now, return token in response (development only)
            return jsonify({
                'success': True,
                'message': 'Password reset token generated',
                'token': token  # Remove in production
            }), 200
        else:
            # Log password reset request for non-existent user
            audit_service.log_password_reset_request(email, None)
            
            # Return success even if user not found (security best practice)
            return jsonify({
                'success': True,
                'message': 'If the email exists, a reset link will be sent'
            }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Password reset request failed'
        }), 500


@bp.route('/password-reset', methods=['POST'])
def password_reset():
    """
    Reset password with token.
    
    Request body:
        - token: Reset token
        - password: New password
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({
                'success': False,
                'error': 'Token and password are required'
            }), 400
        
        # Reset password
        success, error_msg = auth_service.reset_password(token, new_password)
        
        if not success:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Get user from token to log event
        is_valid, reset_token = auth_service.validate_reset_token(token)
        if is_valid:
            user = auth_service.get_user_by_id(reset_token.user_id)
            if user:
                audit_service.log_password_reset_success(user.id, user.tenant)
        
        return jsonify({
            'success': True,
            'message': 'Password reset successful'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Password reset failed'
        }), 500


@bp.route('/session', methods=['GET'])
def check_session():
    """
    Check current session status using JWT token.
    
    Returns:
        JSON response with session status and user data
    """
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'authenticated': False
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        is_valid, payload = auth_service.verify_token(token)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'authenticated': False
            }), 401
        
        # Get user from database
        user = User.query.get(payload['user_id'])
        
        if not user:
            return jsonify({
                'success': False,
                'authenticated': False
            }), 401
        
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Session check error: {str(e)}")
        return jsonify({
            'success': False,
            'authenticated': False
        }), 401