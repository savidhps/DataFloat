"""
Tenant isolation service for LuckyVista.
Enforces strict tenant-level data isolation.
"""
from flask import session, current_app
from typing import Optional
from sqlalchemy.orm import Query


class TenantIsolationService:
    """Service for enforcing tenant isolation."""
    
    def get_tenant_from_session(self) -> Optional[str]:
        """
        Get tenant ID from current session.
        
        Returns:
            Tenant ID or None
        """
        return session.get('tenant_id')
    
    def get_user_role_from_session(self) -> Optional[str]:
        """
        Get user role from current session.
        
        Returns:
            User role or None
        """
        return session.get('role')
    
    def is_admin(self) -> bool:
        """
        Check if current user is admin.
        
        Returns:
            True if admin, False otherwise
        """
        return self.get_user_role_from_session() == 'super_admin'
    
    def filter_query_by_tenant(self, query: Query, tenant_field: str = 'tenant') -> Query:
        """
        Filter query by tenant ID from session.
        
        Args:
            query: SQLAlchemy query
            tenant_field: Name of tenant field in model
        
        Returns:
            Filtered query
        """
        # Admin can see all data
        if self.is_admin():
            return query
        
        tenant_id = self.get_tenant_from_session()
        
        if not tenant_id:
            # No tenant in session, return empty query
            return query.filter(False)
        
        # Filter by tenant
        return query.filter_by(**{tenant_field: tenant_id})
    
    def validate_tenant_access(self, resource_tenant_id: str) -> bool:
        """
        Validate that current user can access resource from given tenant.
        
        Args:
            resource_tenant_id: Tenant ID of the resource
        
        Returns:
            True if access allowed, False otherwise
        """
        # Admin can access all tenants
        if self.is_admin():
            return True
        
        user_tenant_id = self.get_tenant_from_session()
        
        if not user_tenant_id:
            return False
        
        return user_tenant_id == resource_tenant_id
    
    def apply_tenant_filter(self, data: list, tenant_field: str = 'tenant') -> list:
        """
        Filter list of dictionaries by tenant.
        
        Args:
            data: List of dictionaries
            tenant_field: Name of tenant field
        
        Returns:
            Filtered list
        """
        # Admin can see all data
        if self.is_admin():
            return data
        
        tenant_id = self.get_tenant_from_session()
        
        if not tenant_id:
            return []
        
        return [item for item in data if item.get(tenant_field) == tenant_id]
    
    def log_unauthorized_access(self, resource_type: str, resource_id: int, resource_tenant: str):
        """
        Log unauthorized access attempt.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            resource_tenant: Resource tenant ID
        """
        from app.services.audit_service import AuditService
        
        audit_service = AuditService()
        user_tenant = self.get_tenant_from_session()
        
        details = {
            'resource_type': resource_type,
            'resource_id': resource_id,
            'resource_tenant': resource_tenant,
            'user_tenant': user_tenant
        }
        
        audit_service.log_security_violation(
            'unauthorized_access_attempt',
            details
        )