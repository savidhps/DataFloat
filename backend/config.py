"""
Configuration module for LuckyVista application.
Loads configuration from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///luckyvista.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session Configuration
    SESSION_TYPE = 'null'  # Use Flask's default session handling
    SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'False').lower() == 'true'
    PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', '1800'))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None' if os.getenv('FLASK_ENV') == 'production' else 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_NAME = 'luckyvista_session'
    SESSION_COOKIE_PATH = '/'
    
    # Security Configuration
    BCRYPT_WORK_FACTOR = int(os.getenv('BCRYPT_WORK_FACTOR', '12'))
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # Admin Credentials
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Sentiment Analysis Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/sentiment_model.pkl')
    VECTORIZER_PATH = os.getenv('VECTORIZER_PATH', 'models/vectorizer.pkl')
    MIN_MODEL_ACCURACY = float(os.getenv('MIN_MODEL_ACCURACY', '0.70'))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    @staticmethod
    def validate():
        """Validate that required configuration is present."""
        required_vars = ['SECRET_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing and os.getenv('FLASK_ENV') == 'production':
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
