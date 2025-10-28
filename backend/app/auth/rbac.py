"""
Role-Based Access Control (RBAC)
ロールベースアクセス制御
"""

from enum import Enum
from typing import List, Optional, Set
from fastapi import HTTPException, status, Depends
from app.models.user import User
from app.auth.jwt import get_current_user


class Permission(str, Enum):
    """System permissions"""
    # Investigation permissions
    VIEW_INVESTIGATIONS = "view_investigations"
    CREATE_INVESTIGATIONS = "create_investigations"
    UPDATE_INVESTIGATIONS = "update_investigations"
    DELETE_INVESTIGATIONS = "delete_investigations"
    
    # Analysis permissions
    RUN_PATTERN_ANALYSIS = "run_pattern_analysis"
    RUN_RISK_ANALYSIS = "run_risk_analysis"
    GENERATE_NARRATIVE = "generate_narrative"
    
    # Report permissions
    VIEW_REPORTS = "view_reports"
    GENERATE_REPORTS = "generate_reports"
    EXPORT_REPORTS = "export_reports"
    
    # Graph permissions
    VIEW_GRAPH = "view_graph"
    EXPORT_GRAPH = "export_graph"
    
    # User management
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    UPDATE_USERS = "update_users"
    DELETE_USERS = "delete_users"
    
    # System administration
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_METRICS = "view_metrics"


class Role(str, Enum):
    """User roles"""
    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    VIEWER = "viewer"


# Role-Permission mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # All permissions
        Permission.VIEW_INVESTIGATIONS,
        Permission.CREATE_INVESTIGATIONS,
        Permission.UPDATE_INVESTIGATIONS,
        Permission.DELETE_INVESTIGATIONS,
        Permission.RUN_PATTERN_ANALYSIS,
        Permission.RUN_RISK_ANALYSIS,
        Permission.GENERATE_NARRATIVE,
        Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_GRAPH,
        Permission.EXPORT_GRAPH,
        Permission.VIEW_USERS,
        Permission.CREATE_USERS,
        Permission.UPDATE_USERS,
        Permission.DELETE_USERS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_METRICS,
    },
    Role.INVESTIGATOR: {
        # Full investigation and analysis capabilities
        Permission.VIEW_INVESTIGATIONS,
        Permission.CREATE_INVESTIGATIONS,
        Permission.UPDATE_INVESTIGATIONS,
        Permission.RUN_PATTERN_ANALYSIS,
        Permission.RUN_RISK_ANALYSIS,
        Permission.GENERATE_NARRATIVE,
        Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_GRAPH,
        Permission.EXPORT_GRAPH,
    },
    Role.ANALYST: {
        # Analysis and reporting only
        Permission.VIEW_INVESTIGATIONS,
        Permission.RUN_PATTERN_ANALYSIS,
        Permission.RUN_RISK_ANALYSIS,
        Permission.GENERATE_NARRATIVE,
        Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_GRAPH,
    },
    Role.VIEWER: {
        # Read-only access
        Permission.VIEW_INVESTIGATIONS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_GRAPH,
    },
}


class RBACService:
    """RBAC service for permission checking"""
    
    @staticmethod
    def get_role_permissions(role: Role) -> Set[Permission]:
        """Get all permissions for a role"""
        return ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    def has_permission(user: User, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        if not user.role:
            return False
        
        try:
            user_role = Role(user.role)
        except ValueError:
            return False
        
        role_permissions = ROLE_PERMISSIONS.get(user_role, set())
        return permission in role_permissions
    
    @staticmethod
    def has_any_permission(user: User, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions"""
        return any(RBACService.has_permission(user, perm) for perm in permissions)
    
    @staticmethod
    def has_all_permissions(user: User, permissions: List[Permission]) -> bool:
        """Check if user has all of the specified permissions"""
        return all(RBACService.has_permission(user, perm) for perm in permissions)
    
    @staticmethod
    def check_permission(user: User, permission: Permission):
        """Check permission and raise exception if not authorized"""
        if not RBACService.has_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value}"
            )


# Permission dependency decorators
def require_permission(permission: Permission):
    """Dependency to require specific permission"""
    def permission_checker(current_user: User = Depends(get_current_user)):
        RBACService.check_permission(current_user, permission)
        return current_user
    
    return permission_checker


def require_any_permission(*permissions: Permission):
    """Dependency to require any of the specified permissions"""
    def permission_checker(current_user: User = Depends(get_current_user)):
        if not RBACService.has_any_permission(current_user, list(permissions)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return permission_checker


def require_all_permissions(*permissions: Permission):
    """Dependency to require all of the specified permissions"""
    def permission_checker(current_user: User = Depends(get_current_user)):
        if not RBACService.has_all_permissions(current_user, list(permissions)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return permission_checker


def require_role(*roles: Role):
    """Dependency to require specific role"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned"
            )
        
        try:
            user_role = Role(current_user.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role"
            )
        
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user_role.value} is not authorized"
            )
        
        return current_user
    
    return role_checker
