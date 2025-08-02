"""
Organization management API endpoints
Handles organization CRUD operations and settings

Developed by: Qryti Dev Team
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.security import (
    get_current_user, get_current_admin_user,
    require_organization_access
)
from app.schemas.auth import OrganizationInfo, MessageResponse
from app.models.user import User, UserRole
from app.models.organization import Organization
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# Organization schemas
class OrganizationCreate(BaseModel):
    """Organization creation schema"""
    name: str = Field(..., min_length=2, max_length=100)
    domain: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class OrganizationUpdate(BaseModel):
    """Organization update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    domain: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(None)

class OrganizationStats(BaseModel):
    """Organization statistics schema"""
    id: int
    name: str
    total_users: int
    active_users: int
    verified_users: int
    admin_users: int
    created_at: str
    is_active: bool

@router.get("/", response_model=List[OrganizationInfo])
async def list_organizations(
    skip: int = Query(0, ge=0, description="Number of organizations to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of organizations to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List organizations (admin sees all, users see only their own)
    """
    try:
        if current_user.role == UserRole.ADMIN:
            # Admin can see all organizations
            organizations = db.query(Organization).offset(skip).limit(limit).all()
        else:
            # Regular users can only see their own organization
            organizations = db.query(Organization).filter(
                Organization.id == current_user.organization_id
            ).all()
        
        logger.info(f"Listed {len(organizations)} organizations for user {current_user.email}")
        return organizations
        
    except Exception as e:
        logger.error(f"Error listing organizations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list organizations"
        )

@router.get("/{organization_id}", response_model=OrganizationInfo)
async def get_organization(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get organization by ID
    """
    try:
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Check access permissions
        require_organization_access(current_user, organization_id)
        
        return organization
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization {organization_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get organization"
        )

@router.put("/{organization_id}", response_model=OrganizationInfo)
async def update_organization(
    organization_id: int,
    org_data: OrganizationUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update organization (admin only)
    """
    try:
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Check access permissions
        require_organization_access(current_user, organization_id)
        
        # Check if domain is already taken
        if org_data.domain and org_data.domain != organization.domain:
            existing_org = db.query(Organization).filter(
                Organization.domain == org_data.domain,
                Organization.id != organization_id
            ).first()
            if existing_org:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Domain is already taken by another organization"
                )
        
        # Update organization fields
        if org_data.name is not None:
            organization.name = org_data.name
        
        if org_data.domain is not None:
            organization.domain = org_data.domain
        
        if org_data.description is not None:
            organization.description = org_data.description
        
        if org_data.is_active is not None:
            organization.is_active = org_data.is_active
        
        db.commit()
        
        logger.info(f"Organization {organization_id} updated by {current_user.email}")
        return organization
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating organization {organization_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization"
        )

@router.delete("/{organization_id}", response_model=MessageResponse)
async def delete_organization(
    organization_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete organization (super admin only)
    """
    try:
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Only super admin can delete organizations
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin access required"
            )
        
        # Check if organization has users
        user_count = db.query(User).filter(User.organization_id == organization_id).count()
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete organization with {user_count} users. Please remove all users first."
            )
        
        # Soft delete (deactivate) instead of hard delete
        organization.is_active = False
        db.commit()
        
        logger.info(f"Organization {organization_id} deleted by {current_user.email}")
        
        return MessageResponse(message="Organization deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting organization {organization_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete organization"
        )

@router.get("/{organization_id}/stats", response_model=OrganizationStats)
async def get_organization_stats(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get organization statistics
    """
    try:
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Check access permissions
        require_organization_access(current_user, organization_id)
        
        # Get user statistics
        total_users = db.query(User).filter(User.organization_id == organization_id).count()
        active_users = db.query(User).filter(
            User.organization_id == organization_id,
            User.is_active == True
        ).count()
        verified_users = db.query(User).filter(
            User.organization_id == organization_id,
            User.is_verified == True
        ).count()
        admin_users = db.query(User).filter(
            User.organization_id == organization_id,
            User.role == UserRole.ADMIN
        ).count()
        
        return OrganizationStats(
            id=organization.id,
            name=organization.name,
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            admin_users=admin_users,
            created_at=organization.created_at.isoformat(),
            is_active=organization.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization stats {organization_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get organization statistics"
        )

@router.post("/", response_model=OrganizationInfo)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new organization (super admin only)
    """
    try:
        # Check if domain is already taken
        if org_data.domain:
            existing_org = db.query(Organization).filter(
                Organization.domain == org_data.domain
            ).first()
            if existing_org:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Domain is already taken"
                )
        
        # Create organization
        organization = Organization(
            name=org_data.name,
            domain=org_data.domain,
            description=org_data.description,
            is_active=True
        )
        
        db.add(organization)
        db.commit()
        
        logger.info(f"Organization created: {org_data.name} by {current_user.email}")
        
        return organization
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization"
        )

@router.get("/{organization_id}/users", response_model=List[dict])
async def get_organization_users(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all users in an organization
    """
    try:
        # Check access permissions
        require_organization_access(current_user, organization_id)
        
        users = db.query(User).filter(User.organization_id == organization_id).all()
        
        # Return simplified user data
        return [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            for user in users
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization users {organization_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get organization users"
        )

