"""
LuckyVista Flask Application Factory.
"""
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import logging
import json
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def create_app(config_name='default'):
    """
    Application factory pattern.
    
    Args:
        config_name: Configuration to use (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    config[config_name].validate()
    
    # Ensure secret key is set for sessions
    if not app.config.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY must be set for sessions to work")
    
    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)
    
    # Configure CORS with credentials support
    CORS(app, 
         origins=app.config['CORS_ORIGINS'], 
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         expose_headers=['Content-Type'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    
    # Configure logging
    setup_logging(app)
    
    # Register blueprints
    from app.routes import auth, feedback, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(feedback.bp)
    app.register_blueprint(admin.bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add security headers middleware
    @app.after_request
    def add_security_headers(response):
        # Security headers
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CORS headers for credentials
        origin = request.headers.get('Origin')
        if origin in app.config['CORS_ORIGINS']:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Seed admin user if not exists
        from app.services.auth_service import AuthenticationService
        auth_service = AuthenticationService()
        auth_service.seed_admin_user()
    
    return app


def setup_logging(app):
    """Configure structured JSON logging."""
    if not app.debug:
        # Create logs directory if it doesn't exist
        import os
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler with JSON formatting
        file_handler = logging.FileHandler('logs/luckyvista.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('LuckyVista startup')


def register_error_handlers(app):
    """Register error handlers for consistent error responses."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {
            'success': False,
            'error': 'Bad request',
            'message': str(error)
        }, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {
            'success': False,
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            'success': False,
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }, 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return {
            'success': False,
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {str(error)}', exc_info=True)
        return {
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }, 500