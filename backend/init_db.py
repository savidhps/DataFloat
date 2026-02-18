"""
Database initialization script for LuckyVista.
Creates all tables and seeds initial data.
"""
import os
from app import create_app, db
from app.models import User, Feedback, AuditLog, PasswordResetToken

def init_database():
    """Initialize database with tables and seed data."""
    
    # Create application
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        # Drop all tables (use with caution in production)
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating tables...")
        db.create_all()
        
        # Seed super admin user
        print("Seeding super admin user...")
        from app.services.auth_service import AuthenticationService
        auth_service = AuthenticationService()
        auth_service.seed_admin_user()
        
        print("Database initialization complete!")


if __name__ == '__main__':
    init_database()
