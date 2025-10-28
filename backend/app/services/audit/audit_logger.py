"""
Audit Logging Service
監査ログサービス
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Audit action types"""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    
    # Investigation
    CREATE_INVESTIGATION = "create_investigation"
    VIEW_INVESTIGATION = "view_investigation"
    UPDATE_INVESTIGATION = "update_investigation"
    DELETE_INVESTIGATION = "delete_investigation"
    
    # Analysis
    RUN_PATTERN_ANALYSIS = "run_pattern_analysis"
    RUN_RISK_ANALYSIS = "run_risk_analysis"
    GENERATE_NARRATIVE = "generate_narrative"
    
    # Reports
    GENERATE_REPORT = "generate_report"
    EXPORT_REPORT = "export_report"
    VIEW_REPORT = "view_report"
    
    # Graph
    VIEW_GRAPH = "view_graph"
    EXPORT_GRAPH = "export_graph"
    
    # User management
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    VIEW_USER = "view_user"
    
    # System
    CHANGE_SETTINGS = "change_settings"
    VIEW_AUDIT_LOG = "view_audit_log"
    
    # Data access
    ACCESS_SENSITIVE_DATA = "access_sensitive_data"
    EXPORT_DATA = "export_data"


class AuditLevel(str, Enum):
    """Audit severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AuditLogger:
    """Audit logging service"""
    
    def __init__(self):
        """Initialize audit logger"""
        # In production, this should write to a dedicated audit log database
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
    
    def log_action(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        level: AuditLevel = AuditLevel.INFO,
        success: bool = True
    ):
        """
        Log an audit event
        
        Args:
            action: Type of action performed
            user_id: User ID who performed the action
            user_email: User email
            ip_address: IP address of the request
            resource_type: Type of resource affected
            resource_id: ID of the resource affected
            details: Additional details about the action
            level: Severity level
            success: Whether the action was successful
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action.value,
            "user_id": user_id,
            "user_email": user_email,
            "ip_address": ip_address,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "level": level.value,
            "success": success
        }
        
        # Log to file/database
        log_message = json.dumps(audit_entry, ensure_ascii=False)
        
        if level == AuditLevel.CRITICAL:
            self.logger.critical(log_message)
        elif level == AuditLevel.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # In production, also write to database for querying
        # await self._save_to_database(audit_entry)
    
    def log_authentication(
        self,
        action: AuditAction,
        user_email: str,
        ip_address: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log authentication events"""
        level = AuditLevel.WARNING if not success else AuditLevel.INFO
        
        self.log_action(
            action=action,
            user_email=user_email,
            ip_address=ip_address,
            details=details,
            level=level,
            success=success
        )
    
    def log_data_access(
        self,
        user_id: str,
        user_email: str,
        ip_address: str,
        resource_type: str,
        resource_id: str,
        action: AuditAction = AuditAction.ACCESS_SENSITIVE_DATA,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log sensitive data access"""
        self.log_action(
            action=action,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            level=AuditLevel.INFO
        )
    
    def log_report_generation(
        self,
        user_id: str,
        user_email: str,
        ip_address: str,
        investigation_id: str,
        report_format: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log report generation"""
        self.log_action(
            action=AuditAction.GENERATE_REPORT,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            resource_type="report",
            resource_id=investigation_id,
            details={
                "format": report_format,
                **(details or {})
            },
            level=AuditLevel.INFO
        )
    
    def log_analysis(
        self,
        user_id: str,
        user_email: str,
        ip_address: str,
        analysis_type: str,
        target_address: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log ML analysis execution"""
        action_map = {
            "pattern": AuditAction.RUN_PATTERN_ANALYSIS,
            "risk": AuditAction.RUN_RISK_ANALYSIS,
            "narrative": AuditAction.GENERATE_NARRATIVE
        }
        
        self.log_action(
            action=action_map.get(analysis_type, AuditAction.RUN_PATTERN_ANALYSIS),
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            resource_type="blockchain_address",
            resource_id=target_address,
            details=details,
            level=AuditLevel.INFO
        )
    
    def log_security_event(
        self,
        event_type: str,
        ip_address: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log security-related events"""
        self.log_action(
            action=AuditAction.ACCESS_SENSITIVE_DATA,  # Generic security action
            user_id=user_id,
            ip_address=ip_address,
            details={
                "event_type": event_type,
                **(details or {})
            },
            level=AuditLevel.WARNING
        )
    
    def log_user_management(
        self,
        action: AuditAction,
        admin_user_id: str,
        admin_email: str,
        ip_address: str,
        target_user_id: str,
        target_user_email: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log user management actions"""
        self.log_action(
            action=action,
            user_id=admin_user_id,
            user_email=admin_email,
            ip_address=ip_address,
            resource_type="user",
            resource_id=target_user_id,
            details={
                "target_user_email": target_user_email,
                **(details or {})
            },
            level=AuditLevel.INFO
        )


# Global audit logger instance
audit_logger = AuditLogger()
