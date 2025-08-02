"""
User Model
Represents users of the Qrytiv2 platform

Developed by: Qryti Dev Team
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"

class User(Base):
    """
    User model representing individuals using the platform
    Users belong to organizations and have role-based access
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    position = Column(String(100), nullable=True)
    
    # Role-based access control
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    
    # Organization relationship
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Status and activity tracking
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    led_assessments = relationship("Assessment", back_populates="assessment_lead")
    uploaded_evidence = relationship("Evidence", back_populates="uploaded_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
    
    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN
    
    @property
    def domain(self):
        """Extract domain from user's email"""
        return self.email.split("@")[1] if "@" in self.email else None
    
    def can_access_organization(self, org_id: int) -> bool:
        """Check if user can access specific organization"""
        return self.organization_id == org_id
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.is_admin
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary for API responses"""
        data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "position": self.position,
            "role": self.role,
            "organization_id": self.organization_id,
            "is_active": self.is_active,
            "is_email_verified": self.is_email_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data["domain"] = self.domain
            
        return data

