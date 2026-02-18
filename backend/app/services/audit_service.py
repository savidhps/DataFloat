"""
Audit logging service for LuckyVista.
Provides immutable audit trail for security and compliance.
"""
import json
from datetime import datetime
from flask import request, session, current_app
from typing import Dict, Any, Optional
from app import db
from app.models import AuditLog


class AuditService:
    """Service for audit logging."""
    
    def log_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = 'INFO'
    ):
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            user_id: User ID (optional)
            tenant_id: Tenant ID (optional)
            details: Additional details (optional)
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
        """
        try:
            # Get request context
            ip_address = self._get_client_ip()
            user_agent = request.headers.get('User-Agent', '')
            
            # Use session data if not provided
            if user_id is None:
                user_id = session.get('user_id')
            if tenant_id is None:
                tenant_id = session.get('tenant_id')
            
            # Create audit log entry
            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                event_type=event_type,
                user_id=user_id,
                tenant=tenant_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=json.dumps(details) if details else None,
                severity=severity
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
        except Exception as e:
            # Graceful degradation - log error but don't fail the operation
            current_app.logger.error(f"Failed to write audit log: {str(e)}")
            try:
                db.session.rollback()
            except:
                pass
    
    def log_registration(self, user_id: int, tenant_id: str, success: bool):
        """
        Log user registration event.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            success: Whether registration was successful
        """
        event_type = 'user_registration_success' if success else 'user_registration_failure'
        severity = 'INFO' if success else 'WARNING'
        
        details = {
            'user_id': user_id,
            'tenant': tenant_id,
            'success': success
        }
        
        self.log_event(event_type, user_id, tenant_id, details, severity)
    
    def log_authentication(self, email: str, success: bool, user_id: Optional[int] = None, tenant_id: Optional[str] = None):
        """
        Log authentication attempt.
        
        Args:
            email: User email
            success: Whether authentication was successful
            user_id: User ID (if successful)
            tenant_id: Tenant ID (if successful)
        """
        event_type = 'user_signin_success' if success else 'user_signin_failure'
        severity = 'INFO' if success else 'WARNING'
        
        details = {
            'email': email,
            'success': success
        }
        
        self.log_event(event_type, user_id, tenant_id, details, severity)
    
    def log_feedback_submission(self, feedback_id: int, user_id: int, tenant_id: str):
        """
        Log feedback submission.
        
        Args:
            feedback_id: Feedback ID
            user_id: User ID
            tenant_id: Tenant ID
        """
        details = {
            'feedback_id': feedback_id
        }
        
        self.log_event('feedback_submission', user_id, tenant_id, details, 'INFO')
    
    def log_security_violation(self, violation_type: str, details: Optional[Dict[str, Any]] = None):
        """
        Log security violation.
        
        Args:
            violation_type: Type of violation
            details: Additional details
        """
        event_type = f'security_violation_{violation_type}'
        
        self.log_event(event_type, details=details, severity='CRITICAL')
    
    def log_admin_access(self, resource: str, action: str):
        """
        Log admin dashboard access.
        
        Args:
            resource: Resource accessed
            action: Action performed
        """
        details = {
            'resource': resource,
            'action': action
        }
        
        self.log_event('admin_access', details=details, severity='INFO')
    
    def log_data_export(self, user_id: int, tenant_id: str, record_count: int):
        """
        Log data export.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            record_count: Number of records exported
        """
        details = {
            'record_count': record_count
        }
        
        self.log_event('data_export', user_id, tenant_id, details, 'INFO')
    
    def log_password_reset_request(self, email: str, user_id: Optional[int] = None):
        """
        Log password reset request.
        
        Args:
            email: User email
            user_id: User ID (if found)
        """
        details = {
            'email': email
        }
        
        self.log_event('password_reset_request', user_id, details=details, severity='INFO')
    
    def log_password_reset_success(self, user_id: int, tenant_id: str):
        """
        Log successful password reset.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
        """
        self.log_event('password_reset_success', user_id, tenant_id, severity='INFO')
    
    def _get_client_ip(self) -> str:
        """
        Get client IP address from request.
        
        Returns:
            IP address
        """
        # Check for proxy headers
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or 'unknown'
    
    def query_logs(
        self,
        event_type: Optional[str] = None,
        user_id: Optional[int] = None,
        tenant_id: Optional[str] = None,
        severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ):
        """
        Query audit logs.
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            tenant_id: Filter by tenant ID
            severity: Filter by severity
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
        
        Returns:
            List of audit log entries
        """
        query = AuditLog.query
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        if user_id:
            query = query.filter_by(user_id=user_id)
        if tenant_id:
            query = query.filter_by(tenant=tenant_id)
        if severity:
            query = query.filter_by(severity=severity)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        query = query.order_by(AuditLog.timestamp.desc())
        query = query.limit(limit)
        
        return query.all()