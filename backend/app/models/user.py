"""
User Model
Represents users of the Qrytiv2 platform

Developed by: Qryti Dev Team
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from app.core.database import Base
import enum

class UserRole(enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    CLIENT = "client"

class User(Base):
    """
    User model representing individuals using the platform
    Supports admin users and client users with project management
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(200), nullable=False)
    organization = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    
    # Role-based access control
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    
    # Status and activity tracking
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client_projects = relationship("Project", foreign_keys="Project.client_id", back_populates="client")
    created_models = relationship("AIModel", back_populates="creator")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
    
    def set_password(self, password):
        """Set password hash"""
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.hashed_password, password)
    
    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_client(self):
        """Check if user has client role"""
        return self.role == UserRole.CLIENT
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary for API responses"""
        data = {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "organization": self.organization,
            "department": self.department,
            "role": self.role.value,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "project_count": len(self.client_projects) if self.client_projects else 0
        }
        
        return data

