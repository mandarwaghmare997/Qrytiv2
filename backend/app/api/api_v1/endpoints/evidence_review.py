"""
Evidence Review API endpoints for admin users
Handles evidence approval and review workflows
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models import User, Evidence, Assessment, Project
from app.schemas.admin import EvidenceReviewRequest, EvidenceReviewResponse

router = APIRouter()

@router.get("/evidence/pending", response_model=List[EvidenceReviewResponse])
def get_pending_evidence_review(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    project_id: Optional[int] = None,
    control_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get list of evidence files pending review"""
    
    query = db.query(Evidence).join(Assessment).join(Project).filter(
        Evidence.is_validated == False,
        Evidence.is_active == True
    )
    
    if project_id:
        query = query.filter(Assessment.project_id == project_id)
    
    if control_id:
        query = query.filter(Assessment.control_id == control_id)
    
    evidence_list = query.offset(skip).limit(limit).all()
    
    result = []
    for evidence in evidence_list:
        assessment = evidence.assessment
        project = assessment.project
        client = project.client
        
        result.append({
            "evidence_id": evidence.id,
            "file_name": evidence.file_name,
            "assessment_id": assessment.id,
            "control_id": assessment.control_id,
            "client_name": client.name,
            "project_name": project.project_name,
            "uploaded_at": evidence.uploaded_at.isoformat(),
            "file_size": evidence.file_size,
            "file_type": evidence.file_type,
            "is_approved": None,
            "review_notes": None,
            "reviewed_by": None,
            "reviewed_at": None
        })
    
    return result

@router.post("/evidence/{evidence_id}/review")
def review_evidence(
    evidence_id: int,
    review_data: EvidenceReviewRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Review and approve/reject evidence"""
    
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    # Update evidence validation status
    evidence.is_validated = review_data.approved
    evidence.validation_notes = review_data.review_notes
    
    # You might want to add review tracking fields to Evidence model
    # evidence.reviewed_by = current_admin.id
    # evidence.reviewed_at = datetime.utcnow()
    
    # Update assessment evidence status
    assessment = evidence.assessment
    if review_data.approved:
        assessment.evidence_provided = True
    
    db.commit()
    
    return {
        "message": f"Evidence {'approved' if review_data.approved else 'rejected'} successfully",
        "evidence_id": evidence_id,
        "approved": review_data.approved
    }

@router.get("/evidence/{evidence_id}/download")
def download_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Download evidence file for review"""
    
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    # In a real implementation, you would return the file
    # For now, return file information
    return {
        "file_name": evidence.file_name,
        "file_path": evidence.file_path,
        "file_size": evidence.file_size,
        "file_type": evidence.file_type,
        "download_url": f"/files/evidence/{evidence.id}/{evidence.file_name}"
    }

@router.get("/evidence/statistics")
def get_evidence_statistics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get evidence review statistics"""
    
    total_evidence = db.query(Evidence).filter(Evidence.is_active == True).count()
    pending_review = db.query(Evidence).filter(
        Evidence.is_active == True,
        Evidence.is_validated == False
    ).count()
    approved_evidence = db.query(Evidence).filter(
        Evidence.is_active == True,
        Evidence.is_validated == True
    ).count()
    
    return {
        "total_evidence": total_evidence,
        "pending_review": pending_review,
        "approved_evidence": approved_evidence,
        "approval_rate": round((approved_evidence / total_evidence * 100), 2) if total_evidence > 0 else 0
    }

