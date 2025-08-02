# AI Models API Endpoints
# RESTful API for managing AI models and inventory

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ....core.deps import get_current_user, get_db
from ....models.user import User
from ....models.ai_model import AIModel, ModelType, RiskLevel, ModelStatus, ComplianceStatus
from ....services.ai_inventory_service import AIInventoryService
from ....services.gap_analysis_service import GapAnalysisService

router = APIRouter()

# Pydantic models for request/response
class AIModelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    model_type: str
    framework: Optional[str] = None
    algorithm: Optional[str] = None
    input_data_types: List[str] = []
    output_data_types: List[str] = []
    status: str = "development"
    business_purpose: Optional[str] = None
    stakeholders: List[str] = []
    training_data_source: Optional[str] = None
    data_classification: str = "Internal"

class AIModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    model_type: Optional[str] = None
    framework: Optional[str] = None
    algorithm: Optional[str] = None
    input_data_types: Optional[List[str]] = None
    output_data_types: Optional[List[str]] = None
    status: Optional[str] = None
    business_purpose: Optional[str] = None
    stakeholders: Optional[List[str]] = None
    training_data_source: Optional[str] = None
    data_classification: Optional[str] = None

class AIModelResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    version: str
    model_type: str
    framework: Optional[str]
    algorithm: Optional[str]
    status: str
    risk_level: str
    risk_score: float
    compliance_status: str
    compliance_score: float
    created_date: str
    last_updated: str
    business_purpose: Optional[str]
    monitoring_enabled: bool
    organization_id: int
    created_by: int

    class Config:
        from_attributes = True

@router.post("/", response_model=AIModelResponse)
def create_ai_model(
    model_data: AIModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new AI model in the inventory"""
    try:
        service = AIInventoryService(db)
        ai_model = service.create_ai_model(model_data.dict(), current_user.id)
        return ai_model.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[AIModelResponse])
def get_ai_models(
    status: Optional[str] = Query(None, description="Filter by status"),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    compliance_status: Optional[str] = Query(None, description="Filter by compliance status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all AI models for the user's organization"""
    try:
        service = AIInventoryService(db)
        filters = {}
        if status:
            filters['status'] = status
        if model_type:
            filters['model_type'] = model_type
        if risk_level:
            filters['risk_level'] = risk_level
        if compliance_status:
            filters['compliance_status'] = compliance_status
        
        models = service.get_ai_models(current_user.organization_id, filters)
        return [model.to_dict() for model in models]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary")
def get_inventory_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI inventory summary statistics"""
    try:
        service = AIInventoryService(db)
        summary = service.get_inventory_summary(current_user.organization_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{model_id}", response_model=AIModelResponse)
def get_ai_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific AI model"""
    try:
        service = AIInventoryService(db)
        ai_model = service.get_ai_model(model_id, current_user.organization_id)
        if not ai_model:
            raise HTTPException(status_code=404, detail="AI model not found")
        return ai_model.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{model_id}", response_model=AIModelResponse)
def update_ai_model(
    model_id: int,
    model_data: AIModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an AI model"""
    try:
        service = AIInventoryService(db)
        # Filter out None values
        update_data = {k: v for k, v in model_data.dict().items() if v is not None}
        ai_model = service.update_ai_model(model_id, update_data, current_user.id)
        return ai_model.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{model_id}")
def delete_ai_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an AI model"""
    try:
        service = AIInventoryService(db)
        success = service.delete_ai_model(model_id, current_user.organization_id)
        if not success:
            raise HTTPException(status_code=404, detail="AI model not found")
        return {"message": "AI model deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{model_id}/compliance")
def get_model_compliance(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get compliance assessment for a specific AI model"""
    try:
        # Verify model exists and belongs to user's organization
        service = AIInventoryService(db)
        ai_model = service.get_ai_model(model_id, current_user.organization_id)
        if not ai_model:
            raise HTTPException(status_code=404, detail="AI model not found")
        
        # Get compliance score
        gap_service = GapAnalysisService(db)
        compliance_data = gap_service.calculate_compliance_score(
            current_user.organization_id, 
            model_id
        )
        
        return compliance_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{model_id}/compliance/update")
def update_model_compliance(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update AI model compliance status based on current assessments"""
    try:
        gap_service = GapAnalysisService(db)
        ai_model = gap_service.update_ai_model_compliance(model_id)
        return ai_model.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Model type and status enums for frontend
@router.get("/enums/model-types")
def get_model_types():
    """Get available model types"""
    return [{"value": item.value, "label": item.value.replace("_", " ").title()} 
            for item in ModelType]

@router.get("/enums/statuses")
def get_model_statuses():
    """Get available model statuses"""
    return [{"value": item.value, "label": item.value.replace("_", " ").title()} 
            for item in ModelStatus]

@router.get("/enums/risk-levels")
def get_risk_levels():
    """Get available risk levels"""
    return [{"value": item.value, "label": item.value.replace("_", " ").title()} 
            for item in RiskLevel]

@router.get("/enums/compliance-statuses")
def get_compliance_statuses():
    """Get available compliance statuses"""
    return [{"value": item.value, "label": item.value.replace("_", " ").title()} 
            for item in ComplianceStatus]

