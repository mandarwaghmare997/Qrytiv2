"""
Organization Model
Represents organizations using the Qrytiv2 platform

Developed by: Qryti Dev Team
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Organization(Base):
    """
    Organization model representing companies/entities using the platform
    Each organization represents a distinct tenant in the system
    """
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    industry = Column(String(100), nullable=True)
    size_category = Column(String(50), nullable=True)  # small, medium, large, enterprise
    geographic_scope = Column(Text, nullable=True)
    primary_ai_systems = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', domain='{self.domain}')>"
    
    @property
    def active_users_count(self):
        """Get count of active users in this organization"""
        return len([user for user in self.users if user.is_active])
    
    @property
    def active_assessments_count(self):
        """Get count of active assessments for this organization"""
        return len([assessment for assessment in self.assessments if assessment.status != 'archived'])
    
    def to_dict(self):
        """Convert organization to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "industry": self.industry,
            "size_category": self.size_category,
            "geographic_scope": self.geographic_scope,
            "primary_ai_systems": self.primary_ai_systems,
            "logo_url": self.logo_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "active_users_count": self.active_users_count,
            "active_assessments_count": self.active_assessments_count
        }

