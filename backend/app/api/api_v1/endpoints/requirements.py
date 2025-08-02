# Requirements API Endpoints
# RESTful API for managing ISO 42001 requirements and assessments

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from ....core.deps import get_current_user, get_db
from ....models.user import User
from ....models.requirement import (
    Requirement, RequirementAssessment, GapAnalysis,
    RequirementCategory, ComplianceLevel, AssessmentStatus
)
from ....services.requirement_service import RequirementService
from ....services.gap_analysis_service import GapAnalysisService

router = APIRouter()

# Pydantic models for request/response
class RequirementResponse(BaseModel):
    id: int
    requirement_id: str
    title: str
    description: str
    category: str
    requirement_type: str
    clause_reference: Optional[str]
    objective: Optional[str]
    guidance: Optional[str]
    evidence_required: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class RequirementAssessmentCreate(BaseModel):
    requirement_id: int
    ai_model_id: int
    compliance_level: str = "not_applicable"
    compliance_score: float = 0.0
    current_state: Optional[str] = None
    gap_analysis: Optional[str] = None
    evidence_provided: Optional[str] = None
    recommendations: Optional[str] = None
    risk_level: str = "medium"
    risk_description: Optional[str] = None
    mitigation_plan: Optional[str] = None
    target_completion_date: Optional[str] = None

class RequirementAssessmentUpdate(BaseModel):
    compliance_level: Optional[str] = None
    compliance_score: Optional[float] = None
    current_state: Optional[str] = None
    gap_analysis: Optional[str] = None
    evidence_provided: Optional[str] = None
    recommendations: Optional[str] = None
    risk_level: Optional[str] = None
    risk_description: Optional[str] = None
    mitigation_plan: Optional[str] = None
    target_completion_date: Optional[str] = None
    status: Optional[str] = None

class RequirementAssessmentResponse(BaseModel):
    id: int
    requirement_id: int
    ai_model_id: int
    compliance_level: str
    compliance_score: float
    current_state: Optional[str]
    gap_analysis: Optional[str]
    recommendations: Optional[str]
    risk_level: str
    status: str
    assessment_date: str
    target_completion_date: Optional[str]
    next_review_date: Optional[str]

    class Config:
        from_attributes = True

class GapAnalysisResponse(BaseModel):
    id: int
    analysis_name: str
    description: Optional[str]
    overall_compliance_score: float
    total_requirements: int
    compliant_requirements: int
    non_compliant_requirements: int
    partially_compliant_requirements: int
    analysis_date: str
    estimated_effort: Optional[str]
    estimated_cost: Optional[float]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[RequirementResponse])
def get_requirements(
    category: Optional[str] = Query(None, description="Filter by category"),
    requirement_type: Optional[str] = Query(None, description="Filter by requirement type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all ISO 42001 requirements"""
    try:
        service = RequirementService(db)
        filters = {}
        if category:
            filters['category'] = category
        if requirement_type:
            filters['requirement_type'] = requirement_type
        
        requirements = service.get_requirements(filters)
        return requirements
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/initialize")
def initialize_requirements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initialize ISO 42001 requirements (admin only)"""
    try:
        # Check if user is admin
        if current_user.role.value != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = RequirementService(db)
        requirements = service.initialize_iso42001_requirements()
        return {"message": f"Initialized {len(requirements)} requirements"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/assessments", response_model=RequirementAssessmentResponse)
def create_assessment(
    assessment_data: RequirementAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new requirement assessment"""
    try:
        service = RequirementService(db)
        assessment = service.create_requirement_assessment(
            assessment_data.dict(), 
            current_user.id
        )
        return assessment.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assessments/model/{model_id}", response_model=List[RequirementAssessmentResponse])
def get_assessments_for_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all assessments for a specific AI model"""
    try:
        service = RequirementService(db)
        assessments = service.get_assessments_for_model(
            model_id, 
            current_user.organization_id
        )
        return [assessment.to_dict() for assessment in assessments]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/assessments/{assessment_id}", response_model=RequirementAssessmentResponse)
def update_assessment(
    assessment_id: int,
    assessment_data: RequirementAssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a requirement assessment"""
    try:
        service = RequirementService(db)
        # Filter out None values
        update_data = {k: v for k, v in assessment_data.dict().items() if v is not None}
        assessment = service.update_assessment(
            assessment_id, 
            update_data, 
            current_user.id
        )
        return assessment.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/compliance/summary")
def get_compliance_summary(
    model_id: Optional[int] = Query(None, description="Filter by AI model ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get compliance summary for organization or specific model"""
    try:
        service = RequirementService(db)
        summary = service.get_compliance_summary(
            current_user.organization_id, 
            model_id
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/gap-analysis")
def conduct_gap_analysis(
    model_id: Optional[int] = Query(None, description="AI model ID for model-specific analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Conduct automated gap analysis"""
    try:
        service = GapAnalysisService(db)
        gap_analysis = service.conduct_gap_analysis(
            current_user.organization_id,
            model_id,
            current_user.id
        )
        
        return {
            "id": gap_analysis.id,
            "analysis_name": gap_analysis.analysis_name,
            "overall_compliance_score": gap_analysis.overall_compliance_score,
            "total_requirements": gap_analysis.total_requirements,
            "compliant_requirements": gap_analysis.compliant_requirements,
            "non_compliant_requirements": gap_analysis.non_compliant_requirements,
            "partially_compliant_requirements": gap_analysis.partially_compliant_requirements,
            "estimated_effort": gap_analysis.estimated_effort,
            "estimated_cost": gap_analysis.estimated_cost,
            "analysis_date": gap_analysis.analysis_date.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/compliance/score")
def calculate_compliance_score(
    model_id: Optional[int] = Query(None, description="AI model ID for model-specific score"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate detailed compliance score"""
    try:
        service = GapAnalysisService(db)
        score_data = service.calculate_compliance_score(
            current_user.organization_id,
            model_id
        )
        return score_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Enum endpoints for frontend
@router.get("/enums/categories")
def get_requirement_categories():
    """Get available requirement categories"""
    return [{"value": item.value, "label": item.value.replace("_", " ").title()} 
            for item in RequirementCategory]

@router.get("/enums/compliance-levels")
def get_compliance_levels():
    """Get available compliance levels"""
    return [{"value": item.value, "label": item.value.replace("_", " ").title()} 
            for item in ComplianceLevel]

@router.get("/enums/assessment-statuses")
def get_assessment_statuses():
    """Get available assessment statuses"""
    return [{"value": item.value, "label": item.value.replace("_", " ").title()} 
            for item in AssessmentStatus]

