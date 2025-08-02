"""
Admin API endpoints for user and project management
Handles admin operations for client management and compliance oversight
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models import User, UserRole, Project, Assessment, Score
from app.schemas.admin import (
    UserCreate, UserUpdate, UserResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    AdminDashboardResponse, ClientProgressResponse
)

router = APIRouter()

# User Management Endpoints
@router.post("/users", response_model=UserResponse)
def create_client_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new client user"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new client user
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        organization=user_data.organization,
        department=user_data.department,
        role=UserRole.CLIENT,
        is_active=True
    )
    new_user.set_password(user_data.password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user.to_dict()

@router.get("/users", response_model=List[UserResponse])
def list_client_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    organization: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """List all client users with optional filtering"""
    
    query = db.query(User).filter(User.role == UserRole.CLIENT)
    
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    if organization:
        query = query.filter(User.organization.ilike(f"%{organization}%"))
    
    users = query.offset(skip).limit(limit).all()
    return [user.to_dict() for user in users]

@router.get("/users/{user_id}", response_model=UserResponse)
def get_client_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get specific client user details"""
    
    user = db.query(User).filter(
        User.id == user_id,
        User.role == UserRole.CLIENT
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client user not found"
        )
    
    return user.to_dict()

@router.put("/users/{user_id}", response_model=UserResponse)
def update_client_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update client user information"""
    
    user = db.query(User).filter(
        User.id == user_id,
        User.role == UserRole.CLIENT
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client user not found"
        )
    
    # Update user fields
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.organization is not None:
        user.organization = user_data.organization
    if user_data.department is not None:
        user.department = user_data.department
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.password is not None:
        user.set_password(user_data.password)
    
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return user.to_dict()

@router.delete("/users/{user_id}")
def delete_client_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete client user (soft delete by deactivating)"""
    
    user = db.query(User).filter(
        User.id == user_id,
        User.role == UserRole.CLIENT
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client user not found"
        )
    
    # Soft delete by deactivating
    user.is_active = False
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Client user deactivated successfully"}

# Project Management Endpoints
@router.post("/projects", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new compliance project for a client"""
    
    # Verify client exists
    client = db.query(User).filter(
        User.id == project_data.client_id,
        User.role == UserRole.CLIENT,
        User.is_active == True
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found or inactive"
        )
    
    # Check if client already has an active project
    existing_project = db.query(Project).filter(
        Project.client_id == project_data.client_id,
        Project.status == 'active'
    ).first()
    
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client already has an active compliance project"
        )
    
    # Create new project
    new_project = Project(
        client_id=project_data.client_id,
        project_name=project_data.project_name,
        ai_system_name=project_data.ai_system_name,
        risk_template=project_data.risk_template,
        start_date=project_data.start_date or date.today(),
        target_completion_date=project_data.target_completion_date,
        description=project_data.description,
        created_by=current_admin.id,
        status='active'
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project.to_dict()

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    risk_template: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """List all compliance projects"""
    
    query = db.query(Project)
    
    if status:
        query = query.filter(Project.status == status)
    
    if risk_template:
        query = query.filter(Project.risk_template == risk_template)
    
    projects = query.offset(skip).limit(limit).all()
    return [project.to_dict() for project in projects]

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get specific project details"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project.to_dict()

@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update project information"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update project fields
    if project_data.project_name is not None:
        project.project_name = project_data.project_name
    if project_data.ai_system_name is not None:
        project.ai_system_name = project_data.ai_system_name
    if project_data.risk_template is not None:
        project.risk_template = project_data.risk_template
    if project_data.target_completion_date is not None:
        project.target_completion_date = project_data.target_completion_date
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.status is not None:
        project.status = project_data.status
    
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    
    return project.to_dict()

# Dashboard and Analytics Endpoints
@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get admin dashboard data with analytics"""
    
    # Get total counts
    total_clients = db.query(User).filter(User.role == UserRole.CLIENT).count()
    active_clients = db.query(User).filter(
        User.role == UserRole.CLIENT,
        User.is_active == True
    ).count()
    
    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == 'active').count()
    completed_projects = db.query(Project).filter(Project.status == 'completed').count()
    
    # Get recent projects
    recent_projects = db.query(Project).order_by(
        Project.created_at.desc()
    ).limit(5).all()
    
    # Get compliance statistics
    high_risk_projects = db.query(Project).filter(
        Project.risk_template == 'high'
    ).count()
    
    # Get projects needing attention (low compliance scores)
    projects_needing_attention = db.query(Project).join(Score).filter(
        Score.overall_compliance_score < 70
    ).count()
    
    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "high_risk_projects": high_risk_projects,
        "projects_needing_attention": projects_needing_attention,
        "recent_projects": [project.to_dict() for project in recent_projects]
    }

@router.get("/clients/progress", response_model=List[ClientProgressResponse])
def get_clients_progress(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get progress overview for all clients"""
    
    clients_with_projects = db.query(User).join(Project).filter(
        User.role == UserRole.CLIENT
    ).all()
    
    progress_data = []
    for client in clients_with_projects:
        for project in client.client_projects:
            progress_data.append({
                "client_id": client.id,
                "client_name": client.name,
                "client_email": client.email,
                "organization": client.organization,
                "project_id": project.id,
                "project_name": project.project_name,
                "risk_template": project.risk_template,
                "completion_percentage": project.completion_percentage,
                "compliance_score": project.compliance_score,
                "risk_score": project.risk_score,
                "status": project.status,
                "last_activity": project.updated_at.isoformat() if project.updated_at else None
            })
    
    return progress_data

