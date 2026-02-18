"""
Database models for LuckyVista application.
"""
from app import db
from datetime import datetime
from sqlalchemy import Index


class User(db.Model):
    """User model for authentication and tenant association."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    tenant = db.Column(db.String(100), nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='tenant_user')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feedback = db.relationship('Feedback', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'super_admin'
    
    def to_dict(self):
        """Convert user to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'tenant': self.tenant,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class Feedback(db.Model):
    """Feedback model for user submissions."""
    
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    tenant = db.Column(db.String(100), nullable=False, index=True)
    overall_rating = db.Column(db.Integer, nullable=False)
    experience_rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=False)
    feature_satisfaction = db.Column(db.Integer, nullable=True)
    ui_rating = db.Column(db.Integer, nullable=True)
    recommendation_likelihood = db.Column(db.Integer, nullable=True)
    additional_suggestions = db.Column(db.Text, nullable=True)
    sentiment_label = db.Column(db.String(20), default='Unclassified', index=True)
    sentiment_confidence = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Check constraints
    __table_args__ = (
        db.CheckConstraint('overall_rating >= 1 AND overall_rating <= 5', name='check_overall_rating'),
        db.CheckConstraint('experience_rating >= 1 AND experience_rating <= 5', name='check_experience_rating'),
        db.CheckConstraint('feature_satisfaction IS NULL OR (feature_satisfaction >= 1 AND feature_satisfaction <= 5)', name='check_feature_satisfaction'),
        db.CheckConstraint('ui_rating IS NULL OR (ui_rating >= 1 AND ui_rating <= 5)', name='check_ui_rating'),
        db.CheckConstraint('recommendation_likelihood IS NULL OR (recommendation_likelihood >= 1 AND recommendation_likelihood <= 10)', name='check_recommendation_likelihood'),
    )
    
    def to_dict(self):
        """Convert feedback to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tenant': self.tenant,
            'overall_rating': self.overall_rating,
            'experience_rating': self.experience_rating,
            'comments': self.comments,
            'feature_satisfaction': self.feature_satisfaction,
            'ui_rating': self.ui_rating,
            'recommendation_likelihood': self.recommendation_likelihood,
            'additional_suggestions': self.additional_suggestions,
            'sentiment_label': self.sentiment_label,
            'sentiment_confidence': self.sentiment_confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Feedback {self.id} by User {self.user_id}>'


class AuditLog(db.Model):
    """Audit log model for security and compliance tracking."""
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=True, index=True)
    tenant = db.Column(db.String(100), nullable=True, index=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text, nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON string
    severity = db.Column(db.String(20), nullable=False)
    
    def to_dict(self):
        """Convert audit log to dictionary representation."""
        import json
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'tenant': self.tenant,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'details': json.loads(self.details) if self.details else None,
            'severity': self.severity
        }
    
    def __repr__(self):
        return f'<AuditLog {self.event_type} at {self.timestamp}>'


class PasswordResetToken(db.Model):
    """Password reset token model."""
    
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False, nullable=False)
    
    def is_expired(self):
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)."""
        return not self.used and not self.is_expired()
    
    def __repr__(self):
        return f'<PasswordResetToken for User {self.user_id}>'