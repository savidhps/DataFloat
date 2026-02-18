"""
Authentication service for LuckyVista.
Handles user registration, authentication, session management, and password operations.
"""
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from flask import current_app, session
from app import db
from app.models import User, PasswordResetToken
from app.services.validation_service import ValidationService


class AuthenticationService:
    """Service for authentication operations."""
    
    def __init__(self):
        self.validation_service = ValidationService()
    
    def register_user(self, name: str, email: str, phone: str, tenant: str, password: str) -> Tuple[bool, Optional[User], Optional[str], Optional[str]]:
        """
        Register a new user.
        
        Args:
            name: User's full name
            email: User's email address
            phone: User's phone number
            tenant: Tenant/organization identifier
            password: User's password
        
        Returns:
            Tuple of (success, user, error_message, field_name)
        """
        # Validate registration data
        data = {
            'name': name,
            'email': email,
            'phone': phone,
            'tenant': tenant,
            'password': password
        }
        
        is_valid, error_msg, field = self.validation_service.validate_registration(data)
        if not is_valid:
            return False, None, error_msg, field
        
        # Validate password strength
        is_valid, error_msg = self.validation_service.validate_password_strength(password)
        if not is_valid:
            return False, None, error_msg, 'password'
        
        # Check email uniqueness
        if self.check_email_exists(email):
            return False, None, "Email already exists", 'email'
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user
        try:
            user = User(
                name=name,
                email=email,
                phone=phone,
                tenant=tenant,
                password_hash=password_hash,
                role='tenant_user'
            )
            
            db.session.add(user)
            db.session.commit()
            
            return True, user, None, None
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {str(e)}")
            return False, None, "Registration failed", None
    
    def authenticate(self, email: str, password: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Authenticate user credentials.
        
        Args:
            email: User's email
            password: User's password
        
        Returns:
            Tuple of (success, user, error_message)
        """
        # Validate sign-in data
        data = {'email': email, 'password': password}
        is_valid, error_msg, field = self.validation_service.validate_signin(data)
        if not is_valid:
            return False, None, "Invalid credentials"
        
        # Get user by email
        user = User.query.filter_by(email=email).first()
        
        # Return generic error if user not found
        if not user:
            return False, None, "Invalid credentials"
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            return False, None, "Invalid credentials"
        
        return True, user, None
    
    def create_session(self, user: User) -> str:
        """
        Create a session for authenticated user.
        
        Args:
            user: Authenticated user
        
        Returns:
            Session identifier
        """
        # Generate cryptographically random session ID
        session_id = secrets.token_hex(32)
        
        # Store user data in session
        session['user_id'] = user.id
        session['tenant_id'] = user.tenant
        session['role'] = user.role
        session['session_id'] = session_id
        session.permanent = False
        
        return session_id
    
    def validate_session(self) -> Tuple[bool, Optional[User]]:
        """
        Validate current session.
        
        Returns:
            Tuple of (is_valid, user)
        """
        user_id = session.get('user_id')
        
        if not user_id:
            return False, None
        
        user = User.query.get(user_id)
        
        if not user:
            return False, None
        
        return True, user
    
    def invalidate_session(self):
        """Invalidate current session."""
        session.clear()
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        work_factor = current_app.config.get('BCRYPT_WORK_FACTOR', 12)
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=work_factor)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            password_hash: Hashed password
        
        Returns:
            True if password matches, False otherwise
        """
        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception as e:
            current_app.logger.error(f"Error verifying password: {str(e)}")
            return False
    
    def check_email_exists(self, email: str) -> bool:
        """
        Check if email already exists.
        
        Args:
            email: Email to check
        
        Returns:
            True if email exists, False otherwise
        """
        return User.query.filter_by(email=email).first() is not None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User's email
        
        Returns:
            User or None
        """
        return User.query.filter_by(email=email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User's ID
        
        Returns:
            User or None
        """
        return User.query.get(user_id)
    
    def generate_reset_token(self, user_id: int) -> str:
        """
        Generate password reset token.
        
        Args:
            user_id: User's ID
        
        Returns:
            Reset token
        """
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(reset_token)
        db.session.commit()
        
        return token
    
    def validate_reset_token(self, token: str) -> Tuple[bool, Optional[PasswordResetToken]]:
        """
        Validate password reset token.
        
        Args:
            token: Reset token
        
        Returns:
            Tuple of (is_valid, token_object)
        """
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        
        if not reset_token:
            return False, None
        
        if not reset_token.is_valid():
            return False, None
        
        return True, reset_token
    
    def reset_password(self, token: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Reset user password with token.
        
        Args:
            token: Reset token
            new_password: New password
        
        Returns:
            Tuple of (success, error_message)
        """
        # Validate token
        is_valid, reset_token = self.validate_reset_token(token)
        if not is_valid:
            return False, "Invalid or expired reset token"
        
        # Validate password strength
        is_valid, error_msg = self.validation_service.validate_password_strength(new_password)
        if not is_valid:
            return False, error_msg
        
        # Get user
        user = User.query.get(reset_token.user_id)
        if not user:
            return False, "User not found"
        
        # Update password
        user.password_hash = self.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        # Mark token as used
        reset_token.used = True
        
        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error resetting password: {str(e)}")
            return False, "Password reset failed"
    
    def seed_admin_user(self):
        """Seed super admin user if not exists."""
        admin_email = "admin@gmail.com"
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            admin_password = current_app.config.get('ADMIN_PASSWORD', 'admin123')
            password_hash = self.hash_password(admin_password)
            
            admin = User(
                name="Super Admin",
                email=admin_email,
                phone="+1234567890",
                tenant="platform",
                password_hash=password_hash,
                role='super_admin'
            )
            
            db.session.add(admin)
            db.session.commit()
            current_app.logger.info("Super admin user created")