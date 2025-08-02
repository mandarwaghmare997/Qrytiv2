"""
Authentication API endpoints
Handles user registration, login, token management, and profile operations

Developed by: Qryti Dev Team
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Any
import logging

from app.core.database import get_db
from app.core.security import (
    security_utils, get_current_user, get_current_active_user,
    create_tokens_for_user, security_middleware
)
from app.schemas.auth import (
    UserRegistration, UserLogin, TokenResponse, RefreshTokenRequest,
    PasswordReset, PasswordResetConfirm, PasswordChange, EmailVerification,
    AuthResponse, RegistrationResponse, MessageResponse, UserWithOrganization,
    InviteUserRequest, UpdateProfileRequest
)
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.services.email_service import send_verification_email, send_password_reset_email

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=RegistrationResponse)
async def register_user(
    user_data: UserRegistration,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user and organization
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Check if organization domain already exists
        if user_data.organization_domain:
            existing_org = db.query(Organization).filter(
                Organization.domain == user_data.organization_domain
            ).first()
            if existing_org:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization with this domain already exists"
                )
        
        # Create organization
        organization = Organization(
            name=user_data.organization_name,
            domain=user_data.organization_domain,
            description=f"Organization for {user_data.organization_name}",
            is_active=True
        )
        db.add(organization)
        db.flush()  # Get the organization ID
        
        # Create user
        hashed_password = security_utils.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,  # First user in organization is admin
            organization_id=organization.id,
            is_active=True,
            is_verified=False  # Require email verification
        )
        db.add(user)
        db.commit()
        
        # Send verification email
        background_tasks.add_task(send_verification_email, user.email, user.full_name)
        
        logger.info(f"User registered successfully: {user.email}")
        
        return RegistrationResponse(
            user=user,
            message="Registration successful. Please check your email for verification."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Authenticate user and return tokens
    """
    try:
        # Authenticate user
        user = security_utils.authenticate_user(
            db, user_credentials.email, user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required. Please check your email."
            )
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create tokens
        tokens = create_tokens_for_user(user)
        
        # Get user with organization
        user_with_org = db.query(User).filter(User.id == user.id).first()
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return AuthResponse(
            user=user_with_org,
            tokens=tokens,
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    try:
        # Verify refresh token
        payload = security_utils.verify_token(refresh_data.refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        tokens = create_tokens_for_user(user)
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify user email address
    """
    try:
        # Verify token (implement token verification logic)
        # For now, we'll use a simple approach
        payload = security_utils.verify_token(verification_data.token, "verification")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Get user
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify user
        user.is_verified = True
        db.commit()
        
        logger.info(f"Email verified for user: {user.email}")
        
        return MessageResponse(message="Email verified successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    reset_data: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Send password reset email
    """
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == reset_data.email).first()
        
        # Always return success to prevent email enumeration
        if user and user.is_active:
            # Send password reset email
            background_tasks.add_task(send_password_reset_email, user.email, user.full_name)
            logger.info(f"Password reset email sent to: {user.email}")
        
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> Any:
    """
    Reset password using reset token
    """
    try:
        # Verify reset token
        payload = security_utils.verify_token(reset_data.token, "reset")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get user
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user.hashed_password = security_utils.get_password_hash(reset_data.new_password)
        db.commit()
        
        logger.info(f"Password reset for user: {user.email}")
        
        return MessageResponse(message="Password reset successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change user password
    """
    try:
        # Verify current password
        if not security_utils.verify_password(
            password_data.current_password, current_user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = security_utils.get_password_hash(
            password_data.new_password
        )
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return MessageResponse(message="Password changed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.get("/profile", response_model=UserWithOrganization)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user profile
    """
    return current_user

@router.put("/profile", response_model=UserWithOrganization)
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user profile
    """
    try:
        # Update profile fields
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name
        
        db.commit()
        
        logger.info(f"Profile updated for user: {current_user.email}")
        
        return current_user
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Logout user (client should discard tokens)
    """
    logger.info(f"User logged out: {current_user.email}")
    
    return MessageResponse(message="Logout successful")

@router.get("/me", response_model=UserWithOrganization)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current authenticated user information
    """
    return current_user

