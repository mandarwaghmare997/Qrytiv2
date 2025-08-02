"""
Certificate Management API endpoints
Handles certificate issuance, validation, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models import User, Project, Score
from app.schemas.admin import CertificateIssueRequest, CertificateResponse

router = APIRouter()

# For now, we'll store certificates in a simple model
# In production, you'd want a proper Certificate model
class Certificate:
    def __init__(self, project_id, certificate_type, validity_months, issued_by, notes=None):
        self.id = None  # Would be auto-generated in DB
        self.project_id = project_id
        self.certificate_number = f"QRYTI-{certificate_type.upper()}-{uuid.uuid4().hex[:8].upper()}"
        self.certificate_type = certificate_type
        self.issued_date = datetime.utcnow()
        self.expiry_date = self.issued_date + timedelta(days=validity_months * 30)
        self.status = "active"
        self.issued_by = issued_by
        self.notes = notes

@router.post("/certificates/issue", response_model=dict)
def issue_certificate(
    certificate_data: CertificateIssueRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Issue a compliance certificate for a project"""
    
    # Verify project exists and has sufficient compliance score
    project = db.query(Project).filter(Project.id == certificate_data.project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check compliance score
    latest_score = db.query(Score).filter(
        Score.project_id == certificate_data.project_id
    ).order_by(Score.calculated_at.desc()).first()
    
    if not latest_score or latest_score.overall_compliance_score < 80:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project does not meet minimum compliance score (80%) for certification"
        )
    
    # Create certificate (in production, save to database)
    certificate = Certificate(
        project_id=certificate_data.project_id,
        certificate_type=certificate_data.certificate_type,
        validity_months=certificate_data.validity_period_months,
        issued_by=current_admin.id,
        notes=certificate_data.notes
    )
    
    # In production, you would save to database here
    # db.add(certificate)
    # db.commit()
    
    return {
        "message": "Certificate issued successfully",
        "certificate_number": certificate.certificate_number,
        "project_id": certificate.project_id,
        "certificate_type": certificate.certificate_type,
        "issued_date": certificate.issued_date.isoformat(),
        "expiry_date": certificate.expiry_date.isoformat(),
        "status": certificate.status,
        "download_url": f"/api/certificates/{certificate.certificate_number}/download"
    }

@router.get("/certificates/eligible-projects")
def get_eligible_projects(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get projects eligible for certification"""
    
    # Projects with compliance score >= 80%
    eligible_projects = db.query(Project).join(Score).filter(
        Score.overall_compliance_score >= 80,
        Project.status == 'active'
    ).all()
    
    result = []
    for project in eligible_projects:
        latest_score = db.query(Score).filter(
            Score.project_id == project.id
        ).order_by(Score.calculated_at.desc()).first()
        
        result.append({
            "project_id": project.id,
            "project_name": project.project_name,
            "client_name": project.client.name,
            "client_organization": project.client.organization,
            "compliance_score": latest_score.overall_compliance_score,
            "completion_percentage": project.completion_percentage,
            "risk_template": project.risk_template
        })
    
    return result

@router.get("/certificates/project/{project_id}")
def get_project_certificates(
    project_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all certificates for a specific project"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # In production, query from certificates table
    # For now, return mock data
    return {
        "project_id": project_id,
        "project_name": project.project_name,
        "certificates": []  # Would contain actual certificates from DB
    }

@router.get("/certificates/{certificate_number}/download")
def download_certificate(
    certificate_number: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Download certificate PDF"""
    
    # In production, you would:
    # 1. Verify certificate exists
    # 2. Generate PDF certificate
    # 3. Return file response
    
    return {
        "message": "Certificate download functionality will be implemented",
        "certificate_number": certificate_number,
        "download_url": f"/files/certificates/{certificate_number}.pdf"
    }

@router.put("/certificates/{certificate_number}/revoke")
def revoke_certificate(
    certificate_number: str,
    reason: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Revoke a certificate"""
    
    # In production, update certificate status in database
    
    return {
        "message": "Certificate revoked successfully",
        "certificate_number": certificate_number,
        "revoked_by": current_admin.id,
        "revoked_at": datetime.utcnow().isoformat(),
        "reason": reason
    }

@router.get("/certificates/statistics")
def get_certificate_statistics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get certificate issuance statistics"""
    
    # In production, query from certificates table
    return {
        "total_certificates_issued": 0,
        "active_certificates": 0,
        "expired_certificates": 0,
        "revoked_certificates": 0,
        "certificates_this_month": 0,
        "eligible_projects": len(get_eligible_projects(db, current_admin))
    }

