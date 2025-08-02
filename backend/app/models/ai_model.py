# AI Model Registry Data Model
# Comprehensive model for managing AI models in the organization

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from .base import Base

class ModelType(enum.Enum):
    """AI Model Types"""
    MACHINE_LEARNING = "machine_learning"
    DEEP_LEARNING = "deep_learning"
    NATURAL_LANGUAGE = "natural_language"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    GENERATIVE_AI = "generative_ai"
    DECISION_SUPPORT = "decision_support"
    OTHER = "other"

class RiskLevel(enum.Enum):
    """Risk Assessment Levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

class ModelStatus(enum.Enum):
    """Model Lifecycle Status"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    RETIRED = "retired"

class ComplianceStatus(enum.Enum):
    """ISO 42001 Compliance Status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    NOT_ASSESSED = "not_assessed"

class AIModel(Base):
    """AI Model Registry - Core model for AI inventory management"""
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    version = Column(String(50), nullable=False)
    model_type = Column(Enum(ModelType), nullable=False)
    
    # Technical Details
    framework = Column(String(100))  # TensorFlow, PyTorch, Scikit-learn, etc.
    algorithm = Column(String(100))  # Random Forest, Neural Network, etc.
    input_data_types = Column(Text)  # JSON array of data types
    output_data_types = Column(Text)  # JSON array of output types
    
    # Lifecycle Management
    status = Column(Enum(ModelStatus), nullable=False, default=ModelStatus.DEVELOPMENT)
    created_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deployment_date = Column(DateTime)
    retirement_date = Column(DateTime)
    
    # Risk Assessment
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.MEDIUM)
    risk_score = Column(Float, default=0.0)  # 0-100 scale
    bias_risk = Column(Float, default=0.0)   # Bias assessment score
    privacy_risk = Column(Float, default=0.0)  # Privacy impact score
    security_risk = Column(Float, default=0.0)  # Security vulnerability score
    
    # Compliance
    compliance_status = Column(Enum(ComplianceStatus), nullable=False, default=ComplianceStatus.NOT_ASSESSED)
    compliance_score = Column(Float, default=0.0)  # ISO 42001 compliance score
    last_audit_date = Column(DateTime)
    next_audit_date = Column(DateTime)
    
    # Business Context
    business_purpose = Column(Text)
    stakeholders = Column(Text)  # JSON array of stakeholder information
    impact_assessment = Column(Text)
    
    # Data Management
    training_data_source = Column(Text)
    data_retention_period = Column(Integer)  # Days
    data_classification = Column(String(50))  # Public, Internal, Confidential, Restricted
    
    # Performance Metrics
    accuracy = Column(Float)
    precision_score = Column(Float)
    recall_score = Column(Float)
    f1_score = Column(Float)
    
    # Monitoring
    monitoring_enabled = Column(Boolean, default=False)
    alert_threshold = Column(Float, default=0.8)
    performance_degradation_threshold = Column(Float, default=0.1)
    
    # Relationships
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="ai_models")
    creator = relationship("User", back_populates="created_models")
    assessments = relationship("RequirementAssessment", back_populates="ai_model")
    controls = relationship("Control", back_populates="ai_model")
    
    def __repr__(self):
        return f"<AIModel(name='{self.name}', version='{self.version}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'model_type': self.model_type.value if self.model_type else None,
            'framework': self.framework,
            'algorithm': self.algorithm,
            'status': self.status.value if self.status else None,
            'risk_level': self.risk_level.value if self.risk_level else None,
            'risk_score': self.risk_score,
            'compliance_status': self.compliance_status.value if self.compliance_status else None,
            'compliance_score': self.compliance_score,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'business_purpose': self.business_purpose,
            'monitoring_enabled': self.monitoring_enabled,
            'organization_id': self.organization_id,
            'created_by': self.created_by
        }

