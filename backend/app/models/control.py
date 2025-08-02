"""
Control Model
Represents specific controls within ISO 42001 compliance stages

Developed by: Qryti Dev Team
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Control(Base):
    """
    Control model representing specific control requirements within compliance stages
    Controls map to ISO 42001 requirements and provide granular assessment points
    """
    __tablename__ = "controls"

    id = Column(Integer, primary_key=True, index=True)
    
    # Stage relationship
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False)
    
    # Control identification
    control_code = Column(String(50), nullable=False, index=True)  # e.g., "4.1.1", "5.2.3"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Control properties
    is_required = Column(Boolean, default=True, nullable=False)
    weight = Column(Numeric(3, 2), default=1.00, nullable=False)  # Weight for scoring calculation
    
    # Implementation guidance
    implementation_guidance = Column(Text, nullable=True)
    evidence_requirements = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="controls")
    evidence = relationship("Evidence", back_populates="control")
    ai_model = relationship("AIModel", back_populates="controls")
    
    def __repr__(self):
        return f"<Control(id={self.id}, code='{self.control_code}', title='{self.title}')>"
    
    @property
    def full_code(self):
        """Get full control code including stage information"""
        if self.stage:
            return f"ISO42001-{self.stage.order_index}.{self.control_code}"
        return self.control_code
    
    def to_dict(self):
        """Convert control to dictionary for API responses"""
        return {
            "id": self.id,
            "stage_id": self.stage_id,
            "control_code": self.control_code,
            "full_code": self.full_code,
            "title": self.title,
            "description": self.description,
            "is_required": self.is_required,
            "weight": float(self.weight),
            "implementation_guidance": self.implementation_guidance,
            "evidence_requirements": self.evidence_requirements,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

