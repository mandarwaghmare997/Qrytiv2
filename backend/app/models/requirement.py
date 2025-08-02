# ISO 42001 Requirements Data Model
# Comprehensive model for managing ISO 42001 requirements and assessments

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base

class RequirementCategory(enum.Enum):
    """ISO 42001 Requirement Categories"""
    CONTEXT_ORGANIZATION = "context_organization"  # Clause 4
    LEADERSHIP = "leadership"  # Clause 5
    PLANNING = "planning"  # Clause 6
    SUPPORT = "support"  # Clause 7
    OPERATION = "operation"  # Clause 8
    PERFORMANCE_EVALUATION = "performance_evaluation"  # Clause 9
    IMPROVEMENT = "improvement"  # Clause 10
    AI_MANAGEMENT_SYSTEM = "ai_management_system"  # AI-specific requirements

class RequirementType(enum.Enum):
    """Types of Requirements"""
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"
    GUIDANCE = "guidance"

class AssessmentStatus(enum.Enum):
    """Assessment Status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"

class ComplianceLevel(enum.Enum):
    """Compliance Assessment Levels"""
    FULLY_COMPLIANT = "fully_compliant"
    LARGELY_COMPLIANT = "largely_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"

class Requirement(Base):
    """ISO 42001 Requirements Master List"""
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    
    # Requirement Identification
    requirement_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "4.1", "5.2.1"
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # Classification
    category = Column(Enum(RequirementCategory), nullable=False)
    requirement_type = Column(Enum(RequirementType), nullable=False, default=RequirementType.MANDATORY)
    clause_reference = Column(String(20))  # ISO 42001 clause reference
    
    # Content
    objective = Column(Text)
    guidance = Column(Text)
    evidence_required = Column(Text)  # What evidence is needed for compliance
    
    # Metadata
    created_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    assessments = relationship("RequirementAssessment", back_populates="requirement")
    
    def __repr__(self):
        return f"<Requirement(id='{self.requirement_id}', title='{self.title[:50]}...')>"

class RequirementAssessment(Base):
    """Assessment of requirements against AI models/systems"""
    __tablename__ = "requirement_assessments"

    id = Column(Integer, primary_key=True, index=True)
    
    # References
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    ai_model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Assessment Details
    compliance_level = Column(Enum(ComplianceLevel), nullable=False, default=ComplianceLevel.NOT_APPLICABLE)
    compliance_score = Column(Float, default=0.0)  # 0-100 scale
    
    # Assessment Content
    current_state = Column(Text)  # Current implementation status
    gap_analysis = Column(Text)  # Identified gaps
    evidence_provided = Column(Text)  # Evidence of compliance
    recommendations = Column(Text)  # Recommendations for improvement
    
    # Risk Assessment
    risk_level = Column(String(20), default="medium")  # low, medium, high, critical
    risk_description = Column(Text)
    mitigation_plan = Column(Text)
    
    # Timeline
    assessment_date = Column(DateTime, default=datetime.utcnow)
    target_completion_date = Column(DateTime)
    actual_completion_date = Column(DateTime)
    next_review_date = Column(DateTime)
    
    # Status
    status = Column(Enum(AssessmentStatus), nullable=False, default=AssessmentStatus.NOT_STARTED)
    
    # Metadata
    assessed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    created_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requirement = relationship("Requirement", back_populates="assessments")
    ai_model = relationship("AIModel", back_populates="assessments")
    organization = relationship("Organization", back_populates="requirement_assessments")
    assessor = relationship("User", foreign_keys=[assessed_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<RequirementAssessment(req_id='{self.requirement_id}', model_id='{self.ai_model_id}', compliance='{self.compliance_level}')>"
    
    def to_dict(self):
        """Convert assessment to dictionary for API responses"""
        return {
            'id': self.id,
            'requirement_id': self.requirement_id,
            'ai_model_id': self.ai_model_id,
            'compliance_level': self.compliance_level.value if self.compliance_level else None,
            'compliance_score': self.compliance_score,
            'current_state': self.current_state,
            'gap_analysis': self.gap_analysis,
            'recommendations': self.recommendations,
            'risk_level': self.risk_level,
            'status': self.status.value if self.status else None,
            'assessment_date': self.assessment_date.isoformat() if self.assessment_date else None,
            'target_completion_date': self.target_completion_date.isoformat() if self.target_completion_date else None,
            'next_review_date': self.next_review_date.isoformat() if self.next_review_date else None
        }

class GapAnalysis(Base):
    """Gap Analysis Results"""
    __tablename__ = "gap_analyses"

    id = Column(Integer, primary_key=True, index=True)
    
    # References
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    ai_model_id = Column(Integer, ForeignKey("ai_models.id"))  # Optional - can be org-wide
    
    # Analysis Details
    analysis_name = Column(String(255), nullable=False)
    description = Column(Text)
    scope = Column(Text)  # What was included in the analysis
    
    # Results
    overall_compliance_score = Column(Float, default=0.0)  # 0-100 scale
    total_requirements = Column(Integer, default=0)
    compliant_requirements = Column(Integer, default=0)
    non_compliant_requirements = Column(Integer, default=0)
    partially_compliant_requirements = Column(Integer, default=0)
    
    # Gap Summary
    critical_gaps = Column(Text)  # JSON array of critical gaps
    high_priority_gaps = Column(Text)  # JSON array of high priority gaps
    medium_priority_gaps = Column(Text)  # JSON array of medium priority gaps
    low_priority_gaps = Column(Text)  # JSON array of low priority gaps
    
    # Recommendations
    immediate_actions = Column(Text)  # Actions needed immediately
    short_term_actions = Column(Text)  # Actions needed in 1-3 months
    long_term_actions = Column(Text)  # Actions needed in 3+ months
    
    # Timeline
    analysis_date = Column(DateTime, default=datetime.utcnow)
    target_completion_date = Column(DateTime)
    estimated_effort = Column(String(100))  # e.g., "6 months", "120 person-days"
    estimated_cost = Column(Float)  # Estimated cost for remediation
    
    # Metadata
    conducted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    created_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="gap_analyses")
    ai_model = relationship("AIModel")
    conductor = relationship("User", foreign_keys=[conducted_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<GapAnalysis(name='{self.analysis_name}', score='{self.overall_compliance_score}')>"

