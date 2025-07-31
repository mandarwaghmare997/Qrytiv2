"""
Evidence Model
Represents evidence files uploaded for compliance controls

Developed by: Qryti Dev Team
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Evidence(Base):
    """
    Evidence model representing files uploaded as evidence for compliance controls
    Supports file metadata, quality ratings, and audit trail
    """
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    assessment_stage_id = Column(Integer, ForeignKey("assessment_stages.id"), nullable=False)
    control_id = Column(Integer, ForeignKey("controls.id"), nullable=True)  # Can be general stage evidence
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File information
    file_name = Column(String(255), nullable=False)
    original_file_name = Column(String(255), nullable=False)  # Original name before sanitization
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(100), nullable=False)  # MIME type
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash for integrity
    
    # Evidence metadata
    description = Column(Text, nullable=True)
    quality_rating = Column(String(50), nullable=True)  # comprehensive, adequate, limited
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Status and validation
    is_active = Column(Boolean, default=True, nullable=False)
    is_validated = Column(Boolean, default=False, nullable=False)
    validation_notes = Column(Text, nullable=True)
    
    # Timestamps
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Additional metadata (JSON field for extensibility)
    file_metadata = Column(JSON, nullable=True)
    
    # Relationships
    assessment_stage = relationship("AssessmentStage", back_populates="evidence")
    control = relationship("Control", back_populates="evidence")
    uploaded_by_user = relationship("User", back_populates="uploaded_evidence")
    
    def __repr__(self):
        return f"<Evidence(id={self.id}, file_name='{self.file_name}', quality='{self.quality_rating}')>"
    
    @property
    def file_size_mb(self):
        """Get file size in megabytes"""
        return round(self.file_size / (1024 * 1024), 2) if self.file_size else 0
    
    @property
    def file_extension(self):
        """Get file extension"""
        return self.file_name.split('.')[-1].lower() if '.' in self.file_name else ''
    
    @property
    def is_image(self):
        """Check if file is an image"""
        image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        return self.file_type in image_types
    
    @property
    def is_document(self):
        """Check if file is a document"""
        doc_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'text/csv'
        ]
        return self.file_type in doc_types
    
    @property
    def download_url(self):
        """Get download URL for the evidence file"""
        return f"/api/v1/evidence/{self.id}/download"
    
    @property
    def preview_url(self):
        """Get preview URL for the evidence file (if applicable)"""
        if self.is_image:
            return f"/api/v1/evidence/{self.id}/preview"
        return None
    
    def get_tags_list(self):
        """Get tags as a list"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def set_tags_list(self, tags_list):
        """Set tags from a list"""
        if tags_list:
            self.tags = ', '.join([tag.strip() for tag in tags_list if tag.strip()])
        else:
            self.tags = None
    
    def validate_evidence(self, notes=None):
        """Mark evidence as validated"""
        self.is_validated = True
        if notes:
            self.validation_notes = notes
    
    def to_dict(self, include_metadata=False):
        """Convert evidence to dictionary for API responses"""
        data = {
            "id": self.id,
            "assessment_stage_id": self.assessment_stage_id,
            "control_id": self.control_id,
            "uploaded_by": self.uploaded_by,
            "file_name": self.file_name,
            "original_file_name": self.original_file_name,
            "file_size": self.file_size,
            "file_size_mb": self.file_size_mb,
            "file_type": self.file_type,
            "file_extension": self.file_extension,
            "description": self.description,
            "quality_rating": self.quality_rating,
            "tags": self.get_tags_list(),
            "is_active": self.is_active,
            "is_validated": self.is_validated,
            "validation_notes": self.validation_notes,
            "is_image": self.is_image,
            "is_document": self.is_document,
            "download_url": self.download_url,
            "preview_url": self.preview_url,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_metadata and self.file_metadata:
            data["file_metadata"] = self.file_metadata
            
        return data

