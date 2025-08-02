"""
Admin API schemas for user and project management
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import date, datetime

# User Management Schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    organization: Optional[str] = None
    department: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    organization: Optional[str]
    department: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]
    last_login: Optional[str]
    project_count: int
    
    class Config:
        from_attributes = True

# Project Management Schemas
class ProjectCreate(BaseModel):
    client_id: int
    project_name: str
    ai_system_name: Optional[str] = None
    risk_template: str = "medium"  # 'high', 'medium', 'low'
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    description: Optional[str] = None
    
    @validator('risk_template')
    def validate_risk_template(cls, v):
        if v not in ['high', 'medium', 'low']:
            raise ValueError('Risk template must be high, medium, or low')
        return v

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    ai_system_name: Optional[str] = None
    risk_template: Optional[str] = None
    target_completion_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[str] = None
    
    @validator('risk_template')
    def validate_risk_template(cls, v):
        if v is not None and v not in ['high', 'medium', 'low']:
            raise ValueError('Risk template must be high, medium, or low')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in ['active', 'completed', 'on_hold', 'cancelled']:
            raise ValueError('Status must be active, completed, on_hold, or cancelled')
        return v

class ProjectResponse(BaseModel):
    id: int
    client_id: int
    project_name: str
    ai_system_name: Optional[str]
    risk_template: str
    start_date: Optional[str]
    target_completion_date: Optional[str]
    status: str
    description: Optional[str]
    created_by: int
    created_at: Optional[str]
    updated_at: Optional[str]
    client_name: Optional[str]
    client_email: Optional[str]
    client_organization: Optional[str]
    
    class Config:
        from_attributes = True

# Dashboard and Analytics Schemas
class AdminDashboardResponse(BaseModel):
    total_clients: int
    active_clients: int
    total_projects: int
    active_projects: int
    completed_projects: int
    high_risk_projects: int
    projects_needing_attention: int
    recent_projects: List[ProjectResponse]

class ClientProgressResponse(BaseModel):
    client_id: int
    client_name: str
    client_email: str
    organization: Optional[str]
    project_id: int
    project_name: str
    risk_template: str
    completion_percentage: float
    compliance_score: float
    risk_score: float
    status: str
    last_activity: Optional[str]

# Evidence Review Schemas
class EvidenceReviewRequest(BaseModel):
    evidence_id: int
    approved: bool
    review_notes: Optional[str] = None

class EvidenceReviewResponse(BaseModel):
    evidence_id: int
    file_name: str
    assessment_id: int
    control_id: str
    client_name: str
    project_name: str
    uploaded_at: str
    file_size: int
    file_type: str
    is_approved: Optional[bool]
    review_notes: Optional[str]
    reviewed_by: Optional[int]
    reviewed_at: Optional[str]

# Certificate Management Schemas
class CertificateIssueRequest(BaseModel):
    project_id: int
    certificate_type: str = "iso_42001_compliance"
    validity_period_months: int = 12
    notes: Optional[str] = None

class CertificateResponse(BaseModel):
    id: int
    project_id: int
    certificate_number: str
    certificate_type: str
    issued_date: str
    expiry_date: str
    status: str
    issued_by: int
    notes: Optional[str]
    
    class Config:
        from_attributes = True

# Report Management Schemas
class ReportValidationRequest(BaseModel):
    project_id: int
    report_type: str
    validation_status: str  # 'approved', 'rejected', 'needs_revision'
    validation_notes: Optional[str] = None

class ReportSigningRequest(BaseModel):
    project_id: int
    report_type: str
    digital_signature: str
    signing_notes: Optional[str] = None

