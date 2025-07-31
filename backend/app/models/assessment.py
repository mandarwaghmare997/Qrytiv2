"""
Assessment Model
Represents ISO 42001 compliance assessments

Developed by: Qryti Dev Team
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.core.database import Base
from app.core.config import settings

class Assessment(Base):
    """
    Assessment model representing ISO 42001 compliance assessment instances
    Each assessment tracks an organization's compliance journey
    """
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Organization and lead information
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    assessment_lead_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Assessment identification
    assessment_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # Assessment status and scoring
    status = Column(String(50), default="in_progress", nullable=False)  # in_progress, completed, archived
    overall_score = Column(Numeric(5, 2), default=0.00, nullable=False)
    
    # Risk and compliance information
    risk_level = Column(String(50), nullable=True)  # low, medium, high, critical
    certification_eligible = Column(Boolean, default=False, nullable=False)
    
    # Validity and timing
    validity_period_months = Column(Integer, default=settings.DEFAULT_VALIDITY_PERIOD_MONTHS, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="assessments")
    assessment_lead = relationship("User", back_populates="led_assessments")
    assessment_stages = relationship("AssessmentStage", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, assessment_id='{self.assessment_id}', status='{self.status}')>"
    
    @property
    def is_completed(self):
        """Check if assessment is completed"""
        return self.status == "completed"
    
    @property
    def is_in_progress(self):
        """Check if assessment is in progress"""
        return self.status == "in_progress"
    
    @property
    def validity_end_date(self):
        """Calculate assessment validity end date"""
        if self.completed_at:
            return self.completed_at + timedelta(days=self.validity_period_months * 30)
        return None
    
    @property
    def is_valid(self):
        """Check if assessment is still valid"""
        if not self.completed_at:
            return False
        return datetime.now() <= self.validity_end_date
    
    @property
    def days_until_expiry(self):
        """Get days until assessment expires"""
        if not self.validity_end_date:
            return None
        delta = self.validity_end_date - datetime.now()
        return max(0, delta.days)
    
    @property
    def completion_percentage(self):
        """Calculate assessment completion percentage"""
        if not self.assessment_stages:
            return 0.0
        
        completed_stages = len([stage for stage in self.assessment_stages 
                              if stage.status == "completed"])
        total_stages = len(self.assessment_stages)
        
        return (completed_stages / total_stages) * 100 if total_stages > 0 else 0.0
    
    def update_overall_score(self):
        """Calculate and update overall assessment score"""
        if not self.assessment_stages:
            self.overall_score = 0.00
            return
        
        # Calculate weighted average of stage scores
        total_weight = 0
        weighted_score = 0
        
        for stage in self.assessment_stages:
            if stage.status == "completed" and not stage.is_skipped and not stage.is_not_applicable:
                weight = 1.0  # Equal weight for all stages for now
                total_weight += weight
                weighted_score += stage.score * weight
        
        if total_weight > 0:
            self.overall_score = round(weighted_score / total_weight, 2)
        else:
            self.overall_score = 0.00
        
        # Update certification eligibility
        self.certification_eligible = self.overall_score >= settings.CERTIFICATION_THRESHOLD_SCORE
    
    def generate_assessment_id(self):
        """Generate unique assessment ID in format: ORG-ISO42001-YYYY-QX-XXX"""
        if self.organization and self.started_at:
            org_prefix = self.organization.name[:3].upper().replace(" ", "")
            year = self.started_at.year
            quarter = f"Q{((self.started_at.month - 1) // 3) + 1}"
            
            # Get sequence number for this organization/year/quarter
            from sqlalchemy import func
            from app.core.database import SessionLocal
            
            db = SessionLocal()
            try:
                count = db.query(func.count(Assessment.id)).filter(
                    Assessment.organization_id == self.organization_id,
                    func.extract('year', Assessment.started_at) == year,
                    func.extract('quarter', Assessment.started_at) == ((self.started_at.month - 1) // 3) + 1
                ).scalar() or 0
                
                sequence = str(count + 1).zfill(3)
                self.assessment_id = f"{org_prefix}-ISO42001-{year}-{quarter}-{sequence}"
            finally:
                db.close()
    
    def to_dict(self, include_stages=False):
        """Convert assessment to dictionary for API responses"""
        data = {
            "id": self.id,
            "organization_id": self.organization_id,
            "assessment_lead_id": self.assessment_lead_id,
            "assessment_id": self.assessment_id,
            "status": self.status,
            "overall_score": float(self.overall_score),
            "risk_level": self.risk_level,
            "certification_eligible": self.certification_eligible,
            "validity_period_months": self.validity_period_months,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "validity_end_date": self.validity_end_date.isoformat() if self.validity_end_date else None,
            "is_valid": self.is_valid,
            "days_until_expiry": self.days_until_expiry,
            "completion_percentage": self.completion_percentage,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_stages:
            data["stages"] = [stage.to_dict() for stage in self.assessment_stages]
            
        return data

