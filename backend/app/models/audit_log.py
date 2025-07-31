"""
Audit Log Model
Represents audit trail for compliance and security purposes

Developed by: Qryti Dev Team
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    """
    Audit Log model for tracking all user actions and system events
    Provides comprehensive audit trail for compliance purposes
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # User and organization context
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for system events
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # e.g., "CREATE", "UPDATE", "DELETE", "LOGIN"
    entity_type = Column(String(50), nullable=False, index=True)  # e.g., "assessment", "evidence", "user"
    entity_id = Column(Integer, nullable=True)  # ID of the affected entity
    
    # Change tracking
    old_values = Column(JSON, nullable=True)  # Previous values before change
    new_values = Column(JSON, nullable=True)  # New values after change
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(36), nullable=True)  # UUID for request tracking
    
    # Additional context
    description = Column(Text, nullable=True)  # Human-readable description
    severity = Column(String(20), default="info", nullable=False)  # info, warning, error, critical
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    organization = relationship("Organization", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', entity='{self.entity_type}')>"
    
    @classmethod
    def create_log(cls, 
                   organization_id: int,
                   action: str,
                   entity_type: str,
                   user_id: int = None,
                   entity_id: int = None,
                   old_values: dict = None,
                   new_values: dict = None,
                   ip_address: str = None,
                   user_agent: str = None,
                   request_id: str = None,
                   description: str = None,
                   severity: str = "info"):
        """Create a new audit log entry"""
        return cls(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            description=description,
            severity=severity
        )
    
    @property
    def is_user_action(self):
        """Check if this is a user-initiated action"""
        return self.user_id is not None
    
    @property
    def is_system_action(self):
        """Check if this is a system-initiated action"""
        return self.user_id is None
    
    @property
    def has_changes(self):
        """Check if this log entry contains data changes"""
        return self.old_values is not None or self.new_values is not None
    
    def to_dict(self, include_sensitive=False):
        """Convert audit log to dictionary for API responses"""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "description": self.description,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_user_action": self.is_user_action,
            "is_system_action": self.is_system_action,
            "has_changes": self.has_changes
        }
        
        if include_sensitive:
            data.update({
                "old_values": self.old_values,
                "new_values": self.new_values,
                "ip_address": self.ip_address,
                "user_agent": self.user_agent,
                "request_id": self.request_id
            })
            
        return data

# Common audit log actions
class AuditActions:
    """Constants for common audit log actions"""
    
    # Authentication
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    
    # User management
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_ACTIVATED = "USER_ACTIVATED"
    USER_DEACTIVATED = "USER_DEACTIVATED"
    
    # Organization management
    ORGANIZATION_CREATED = "ORGANIZATION_CREATED"
    ORGANIZATION_UPDATED = "ORGANIZATION_UPDATED"
    
    # Assessment management
    ASSESSMENT_CREATED = "ASSESSMENT_CREATED"
    ASSESSMENT_UPDATED = "ASSESSMENT_UPDATED"
    ASSESSMENT_COMPLETED = "ASSESSMENT_COMPLETED"
    ASSESSMENT_ARCHIVED = "ASSESSMENT_ARCHIVED"
    
    # Stage management
    STAGE_STARTED = "STAGE_STARTED"
    STAGE_COMPLETED = "STAGE_COMPLETED"
    STAGE_SKIPPED = "STAGE_SKIPPED"
    STAGE_MARKED_NA = "STAGE_MARKED_NA"
    
    # Evidence management
    EVIDENCE_UPLOADED = "EVIDENCE_UPLOADED"
    EVIDENCE_UPDATED = "EVIDENCE_UPDATED"
    EVIDENCE_DELETED = "EVIDENCE_DELETED"
    EVIDENCE_DOWNLOADED = "EVIDENCE_DOWNLOADED"
    EVIDENCE_VALIDATED = "EVIDENCE_VALIDATED"
    
    # Report generation
    REPORT_GENERATED = "REPORT_GENERATED"
    CERTIFICATE_GENERATED = "CERTIFICATE_GENERATED"
    DATA_EXPORTED = "DATA_EXPORTED"
    
    # System events
    SYSTEM_BACKUP = "SYSTEM_BACKUP"
    SYSTEM_RESTORE = "SYSTEM_RESTORE"
    SYSTEM_ERROR = "SYSTEM_ERROR"

# Entity types for audit logging
class AuditEntityTypes:
    """Constants for audit log entity types"""
    
    USER = "user"
    ORGANIZATION = "organization"
    ASSESSMENT = "assessment"
    STAGE = "stage"
    ASSESSMENT_STAGE = "assessment_stage"
    CONTROL = "control"
    EVIDENCE = "evidence"
    REPORT = "report"
    CERTIFICATE = "certificate"
    SYSTEM = "system"

