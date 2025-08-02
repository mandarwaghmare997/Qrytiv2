"""
Project model for client project management
Handles compliance projects assigned to clients
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, date
from .base import Base

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_name = Column(String(255), nullable=False)
    ai_system_name = Column(String(255))
    risk_template = Column(String(50), default='medium')  # 'high', 'medium', 'low'
    start_date = Column(Date, default=date.today)
    target_completion_date = Column(Date)
    status = Column(String(50), default='active')  # 'active', 'completed', 'on_hold', 'cancelled'
    description = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("User", foreign_keys=[client_id], back_populates="client_projects")
    creator = relationship("User", foreign_keys=[created_by])
    assessments = relationship("Assessment", back_populates="project", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.project_name}', client_id={self.client_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'project_name': self.project_name,
            'ai_system_name': self.ai_system_name,
            'risk_template': self.risk_template,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_completion_date': self.target_completion_date.isoformat() if self.target_completion_date else None,
            'status': self.status,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'client_name': self.client.name if self.client else None,
            'client_email': self.client.email if self.client else None,
            'client_organization': self.client.organization if self.client else None
        }
    
    @property
    def completion_percentage(self):
        """Calculate project completion percentage based on assessments"""
        if not self.assessments:
            return 0
        
        total_assessments = len(self.assessments)
        completed_assessments = len([a for a in self.assessments if a.response is not None])
        
        return round((completed_assessments / total_assessments) * 100, 2) if total_assessments > 0 else 0
    
    @property
    def compliance_score(self):
        """Get latest overall compliance score"""
        if not self.scores:
            return 0
        
        latest_score = max(self.scores, key=lambda s: s.calculated_at)
        return latest_score.overall_compliance_score if latest_score else 0
    
    @property
    def risk_score(self):
        """Get latest risk score"""
        if not self.scores:
            return 0
        
        latest_score = max(self.scores, key=lambda s: s.calculated_at)
        return latest_score.risk_score if latest_score else 0

