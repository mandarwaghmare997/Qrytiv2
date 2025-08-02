"""
Assessment model for gap assessment responses
Handles client responses to ISO 42001 control questions
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Assessment(Base):
    __tablename__ = 'assessments'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    control_id = Column(String(10), ForeignKey('controls.control_id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    response = Column(String(20))  # 'yes', 'no', 'na'
    justification = Column(Text)
    evidence_provided = Column(Boolean, default=False)
    assessed_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    assessed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="assessments")
    control = relationship("Control")
    question = relationship("Question")
    assessor = relationship("User")
    evidence_files = relationship("Evidence", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, project_id={self.project_id}, control_id='{self.control_id}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'control_id': self.control_id,
            'question_id': self.question_id,
            'response': self.response,
            'justification': self.justification,
            'evidence_provided': self.evidence_provided,
            'assessed_by': self.assessed_by,
            'assessed_at': self.assessed_at.isoformat() if self.assessed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'control_name': self.control.control_name if self.control else None,
            'question_text': self.question.question_text if self.question else None,
            'evidence_count': len(self.evidence_files) if self.evidence_files else 0
        }
    
    @property
    def score(self):
        """Calculate score for this assessment based on response and evidence"""
        if self.response == 'na':
            return None  # N/A responses are excluded from scoring
        elif self.response == 'yes':
            return 100 if self.evidence_provided else 50
        elif self.response == 'no':
            return 0
        else:
            return None  # No response yet


class Question(Base):
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String(10), ForeignKey('controls.control_id'), nullable=False)
    question_text = Column(Text, nullable=False)
    response_type = Column(String(20), default='yes_no_na')
    weight = Column(Numeric(3, 2), default=1.0)
    order_index = Column(Integer, default=0)
    
    # Relationships
    control = relationship("Control", back_populates="questions")
    
    def __repr__(self):
        return f"<Question(id={self.id}, control_id='{self.control_id}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'control_id': self.control_id,
            'question_text': self.question_text,
            'response_type': self.response_type,
            'weight': float(self.weight) if self.weight else 1.0,
            'order_index': self.order_index
        }


class Evidence(Base):
    __tablename__ = 'evidence'
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    version = Column(Integer, default=1)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_current_version = Column(Boolean, default=True)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="evidence_files")
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<Evidence(id={self.id}, file_name='{self.file_name}', version={self.version})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'version': self.version,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'is_current_version': self.is_current_version,
            'uploader_name': self.uploader.name if self.uploader else None
        }


class Score(Base):
    __tablename__ = 'scores'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    control_id = Column(String(10), ForeignKey('controls.control_id'))
    control_score = Column(Numeric(5, 2))
    category_score = Column(Numeric(5, 2))
    overall_compliance_score = Column(Numeric(5, 2))
    risk_score = Column(Numeric(5, 2))
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="scores")
    control = relationship("Control")
    
    def __repr__(self):
        return f"<Score(id={self.id}, project_id={self.project_id}, overall_score={self.overall_compliance_score})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'control_id': self.control_id,
            'control_score': float(self.control_score) if self.control_score else None,
            'category_score': float(self.category_score) if self.category_score else None,
            'overall_compliance_score': float(self.overall_compliance_score) if self.overall_compliance_score else None,
            'risk_score': float(self.risk_score) if self.risk_score else None,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }

