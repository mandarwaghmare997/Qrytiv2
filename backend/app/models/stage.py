"""
Stage and AssessmentStage Models
Represents ISO 42001 compliance stages and their progress

Developed by: Qryti Dev Team
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Stage(Base):
    """
    Stage model representing the fixed ISO 42001 compliance stages
    These are the standard stages that every assessment follows
    """
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, unique=True)
    is_required = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    controls = relationship("Control", back_populates="stage", cascade="all, delete-orphan")
    assessment_stages = relationship("AssessmentStage", back_populates="stage")
    
    def __repr__(self):
        return f"<Stage(id={self.id}, name='{self.name}', order={self.order_index})>"
    
    def to_dict(self):
        """Convert stage to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "order_index": self.order_index,
            "is_required": self.is_required,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class AssessmentStage(Base):
    """
    AssessmentStage model representing progress through stages for specific assessments
    Tracks completion status, scores, and justifications for each stage
    """
    __tablename__ = "assessment_stages"
    __table_args__ = (UniqueConstraint('assessment_id', 'stage_id', name='unique_assessment_stage'),)

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False)
    
    # Progress tracking
    status = Column(String(50), default="not_started", nullable=False)  # not_started, in_progress, completed
    score = Column(Numeric(5, 2), default=0.00, nullable=False)
    
    # Flexibility options
    is_skipped = Column(Boolean, default=False, nullable=False)
    skip_justification = Column(Text, nullable=True)
    is_not_applicable = Column(Boolean, default=False, nullable=False)
    na_justification = Column(Text, nullable=True)
    
    # Completion tracking
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Additional notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="assessment_stages")
    stage = relationship("Stage", back_populates="assessment_stages")
    evidence = relationship("Evidence", back_populates="assessment_stage", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AssessmentStage(assessment_id={self.assessment_id}, stage_id={self.stage_id}, status='{self.status}')>"
    
    @property
    def is_completed(self):
        """Check if stage is completed"""
        return self.status == "completed"
    
    @property
    def is_in_progress(self):
        """Check if stage is in progress"""
        return self.status == "in_progress"
    
    @property
    def is_not_started(self):
        """Check if stage is not started"""
        return self.status == "not_started"
    
    @property
    def evidence_count(self):
        """Get count of evidence items for this stage"""
        return len([e for e in self.evidence if e.is_active])
    
    @property
    def can_be_completed(self):
        """Check if stage can be marked as completed"""
        if self.is_skipped or self.is_not_applicable:
            return True
        
        # Check if required evidence is provided
        if self.stage.is_required and self.evidence_count == 0:
            return False
        
        return True
    
    def calculate_score(self):
        """Calculate stage score based on controls and evidence"""
        if self.is_skipped or self.is_not_applicable:
            self.score = 0.00
            return
        
        if not self.stage.controls:
            # If no controls defined, base score on completion status
            if self.is_completed:
                self.score = 100.00
            elif self.is_in_progress:
                self.score = 50.00
            else:
                self.score = 0.00
            return
        
        # Calculate score based on control completion and evidence quality
        total_controls = len(self.stage.controls)
        completed_controls = 0
        evidence_quality_bonus = 0
        
        for control in self.stage.controls:
            # Check if control has evidence
            control_evidence = [e for e in self.evidence if e.control_id == control.id and e.is_active]
            
            if control_evidence:
                completed_controls += 1
                
                # Add bonus for evidence quality
                for evidence in control_evidence:
                    if evidence.quality_rating == "comprehensive":
                        evidence_quality_bonus += 10
                    elif evidence.quality_rating == "adequate":
                        evidence_quality_bonus += 5
        
        # Base score from control completion
        base_score = (completed_controls / total_controls) * 80 if total_controls > 0 else 0
        
        # Add evidence quality bonus (max 20 points)
        quality_bonus = min(20, evidence_quality_bonus)
        
        self.score = min(100.00, base_score + quality_bonus)
    
    def mark_completed(self):
        """Mark stage as completed"""
        if self.can_be_completed:
            self.status = "completed"
            self.completed_at = func.now()
            self.calculate_score()
    
    def mark_skipped(self, justification: str):
        """Mark stage as skipped with justification"""
        if not justification or len(justification.strip()) < 10:
            raise ValueError("Skip justification must be at least 10 characters long")
        
        self.is_skipped = True
        self.skip_justification = justification
        self.status = "completed"  # Skipped stages are considered completed
        self.completed_at = func.now()
        self.score = 0.00
    
    def mark_not_applicable(self, justification: str):
        """Mark stage as not applicable with justification"""
        if not justification or len(justification.strip()) < 10:
            raise ValueError("Not applicable justification must be at least 10 characters long")
        
        self.is_not_applicable = True
        self.na_justification = justification
        self.status = "completed"  # NA stages are considered completed
        self.completed_at = func.now()
        self.score = 0.00
    
    def to_dict(self, include_evidence=False):
        """Convert assessment stage to dictionary for API responses"""
        data = {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "stage_id": self.stage_id,
            "stage_name": self.stage.name if self.stage else None,
            "stage_description": self.stage.description if self.stage else None,
            "stage_order": self.stage.order_index if self.stage else None,
            "status": self.status,
            "score": float(self.score),
            "is_skipped": self.is_skipped,
            "skip_justification": self.skip_justification,
            "is_not_applicable": self.is_not_applicable,
            "na_justification": self.na_justification,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
            "evidence_count": self.evidence_count,
            "can_be_completed": self.can_be_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_evidence:
            data["evidence"] = [e.to_dict() for e in self.evidence if e.is_active]
            
        return data

