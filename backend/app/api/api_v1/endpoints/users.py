"""
User management API endpoints
Handles user CRUD operations and user administration

Developed by: Qryti Dev Team
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.security import (
    get_current_user, get_current_admin_user,
    require_organization_access, security_utils
)
from app.schemas.auth import (
    UserWithOrganization, UpdateUserRequest, InviteUserRequest,
    MessageResponse, UserProfile
)
from app.models.user import User, UserRole
from app.services.email_service import send_verification_email

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[UserWithOrganization])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    organization_id: Optional[int] = Query(None, description="Filter by organization ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List users (admin can see all, users can see only their organization)
    """
    try:
        query = db.query(User)
        
        # Filter by organization access
        if current_user.role != UserRole.ADMIN:
            # Regular users can only see users from their organization
            query = query.filter(User.organization_id == current_user.organization_id)
        elif organization_id is not None:
            # Admin can filter by specific organization
            query = query.filter(User.organization_id == organization_id)
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        logger.info(f"Listed {len(users)} users for user {current_user.email}")
        return users
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )

@router.get("/{user_id}", response_model=UserWithOrganization)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check access permissions
        if current_user.role != UserRole.ADMIN:
            if user.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this user"
                )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )

@router.put("/{user_id}", response_model=UserWithOrganization)
async def update_user(
    user_id: int,
    user_data: UpdateUserRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update user (admin only)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check organization access
        require_organization_access(current_user, user.organization_id)
        
        # Update user fields
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.role is not None:
            user.role = user_data.role
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        db.commit()
        
        logger.info(f"User {user_id} updated by admin {current_user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete user (admin only)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check organization access
        require_organization_access(current_user, user.organization_id)
        
        # Prevent self-deletion
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Soft delete (deactivate) instead of hard delete
        user.is_active = False
        db.commit()
        
        logger.info(f"User {user_id} deleted by admin {current_user.email}")
        
        return MessageResponse(message="User deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.post("/invite", response_model=MessageResponse)
async def invite_user(
    invite_data: InviteUserRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Invite a new user to the organization (admin only)
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == invite_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        temp_password = "TempPass123!"  # User will need to reset this
        hashed_password = security_utils.get_password_hash(temp_password)
        
        new_user = User(
            email=invite_data.email,
            full_name=invite_data.full_name or invite_data.email.split("@")[0],
            hashed_password=hashed_password,
            role=invite_data.role,
            organization_id=current_user.organization_id,
            is_active=True,
            is_verified=False  # Require email verification
        )
        
        db.add(new_user)
        db.commit()
        
        # Send invitation email
        send_verification_email(new_user.email, new_user.full_name)
        
        logger.info(f"User invited: {invite_data.email} by {current_user.email}")
        
        return MessageResponse(
            message=f"Invitation sent to {invite_data.email}. They will receive an email with verification instructions."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inviting user {invite_data.email}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invite user"
        )

@router.post("/{user_id}/resend-verification", response_model=MessageResponse)
async def resend_verification(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Resend verification email for a user (admin only)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check organization access
        require_organization_access(current_user, user.organization_id)
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already verified"
            )
        
        # Send verification email
        send_verification_email(user.email, user.full_name)
        
        logger.info(f"Verification email resent for user {user_id} by {current_user.email}")
        
        return MessageResponse(
            message=f"Verification email sent to {user.email}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending verification for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification email"
        )

@router.get("/organization/{organization_id}/stats")
async def get_organization_user_stats(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user statistics for an organization
    """
    try:
        # Check organization access
        require_organization_access(current_user, organization_id)
        
        # Get user counts
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
        
        return {
            "organization_id": organization_id,
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "admin_users": admin_users,
            "pending_verification": total_users - verified_users
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user stats for organization {organization_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )

