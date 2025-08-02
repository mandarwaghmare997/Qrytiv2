from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base

class ControlCategory(str, enum.Enum):
    CONTEXT_ORGANIZATION = "context_organization"
    LEADERSHIP = "leadership"
    PLANNING = "planning"
    SUPPORT = "support"
    OPERATION = "operation"
    PERFORMANCE_EVALUATION = "performance_evaluation"
    IMPROVEMENT = "improvement"
    AI_SYSTEM_IMPACT_ASSESSMENT = "ai_system_impact_assessment"
    AI_SYSTEM_LIFECYCLE = "ai_system_lifecycle"

class NISTFunction(str, enum.Enum):
    GOVERN = "govern"
    MAP = "map"
    MEASURE = "measure"
    MANAGE = "manage"

class RiskLevel(str, enum.Enum):
    MINIMAL = "minimal"
    LIMITED = "limited"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class RiskTemplate(str, enum.Enum):
    LOW = "low"      # 16 controls
    MEDIUM = "medium"  # 24 controls
    HIGH = "high"    # 32 controls

class ISOControl(Base):
    __tablename__ = "iso_controls"

    id = Column(Integer, primary_key=True, index=True)
    control_number = Column(String(20), unique=True, nullable=False, index=True)  # e.g., "4.1", "5.2.1"
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(ControlCategory), nullable=False)
    nist_function = Column(Enum(NISTFunction), nullable=False)
    weight = Column(Float, default=1.0)  # Scoring weight for this control
    is_mandatory = Column(Boolean, default=True)  # Required for all risk templates
    min_risk_template = Column(Enum(RiskTemplate), default=RiskTemplate.LOW)  # Minimum risk level that includes this control
    
    # Relationships
    questions = relationship("ControlQuestion", back_populates="control", cascade="all, delete-orphan")
    assessments = relationship("AssessmentResponse", back_populates="control")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ControlQuestion(Base):
    __tablename__ = "control_questions"

    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(Integer, ForeignKey("iso_controls.id"), nullable=False)
    question_number = Column(String(10), nullable=False)  # e.g., "1", "2a", "2b"
    question_text = Column(Text, nullable=False)
    guidance = Column(Text)  # Additional guidance for answering the question
    weight = Column(Float, default=1.0)  # Weight of this question within the control
    requires_evidence = Column(Boolean, default=True)  # Whether evidence is required for this question
    evidence_description = Column(Text)  # Description of what evidence is expected
    
    # Relationships
    control = relationship("ISOControl", back_populates="questions")
    responses = relationship("QuestionResponse", back_populates="question")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ResponseValue(str, enum.Enum):
    YES = "yes"
    NO = "no"
    NOT_APPLICABLE = "not_applicable"
    PARTIAL = "partial"

class QuestionResponse(Base):
    __tablename__ = "question_responses"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("control_questions.id"), nullable=False)
    response_value = Column(Enum(ResponseValue), nullable=False)
    comments = Column(Text)  # Additional comments from the user
    confidence_level = Column(Integer, default=5)  # 1-10 scale of confidence in the response
    
    # Relationships
    assessment = relationship("Assessment", back_populates="question_responses")
    question = relationship("ControlQuestion", back_populates="responses")
    evidence_files = relationship("EvidenceFile", back_populates="question_response")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EvidenceFile(Base):
    __tablename__ = "evidence_files"

    id = Column(Integer, primary_key=True, index=True)
    question_response_id = Column(Integer, ForeignKey("question_responses.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(50), nullable=False)  # MIME type
    version = Column(Integer, default=1)
    is_current_version = Column(Boolean, default=True)
    upload_status = Column(String(20), default="uploaded")  # uploaded, processing, approved, rejected
    admin_review_status = Column(String(20), default="pending")  # pending, approved, rejected
    admin_comments = Column(Text)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Relationships
    question_response = relationship("QuestionResponse", back_populates="evidence_files")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    control_id = Column(Integer, ForeignKey("iso_controls.id"), nullable=False)
    completion_percentage = Column(Float, default=0.0)  # Percentage of questions answered for this control
    compliance_score = Column(Float, default=0.0)  # Calculated compliance score for this control
    risk_score = Column(Float, default=0.0)  # Risk score based on NIST framework
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed, reviewed
    
    # Relationships
    assessment = relationship("Assessment", back_populates="control_responses")
    control = relationship("ISOControl", back_populates="assessments")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

