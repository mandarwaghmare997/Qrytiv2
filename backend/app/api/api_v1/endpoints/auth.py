"""
Authentication Endpoints
Handles user registration, login, and token management

Developed by: Qryti Dev Team
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    extract_domain_from_email
)
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.models.audit_log import AuditLog, AuditActions, AuditEntityTypes
from app.schemas.auth import (
    UserRegister, 
    UserLogin, 
    Token, 
    TokenRefresh, 
    PasswordChange,
    UserProfile
)

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user and organization
    Creates organization if it doesn't exist, or adds user to existing organization
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Extract domain from email
    domain = extract_domain_from_email(user_data.email)
    
    # Check if organization exists for this domain
    organization = db.query(Organization).filter(Organization.domain == domain).first()
    
    if not organization:
        # Create new organization
        organization = Organization(
            name=user_data.organization_name,
            domain=domain,
            industry=user_data.industry,
            size_category=user_data.size_category,
            geographic_scope=user_data.geographic_scope
        )
        db.add(organization)
        db.flush()  # Get the organization ID
        
        # First user in organization becomes admin
        user_role = "admin"
        
        # Log organization creation
        audit_log = AuditLog.create_log(
            organization_id=organization.id,
            action=AuditActions.ORGANIZATION_CREATED,
            entity_type=AuditEntityTypes.ORGANIZATION,
            entity_id=organization.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            description=f"Organization '{organization.name}' created during user registration"
        )
        db.add(audit_log)
    else:
        # Add user to existing organization
        user_role = "user"
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        position=user_data.position,
        role=user_role,
        organization_id=organization.id,
        is_email_verified=True  # Auto-verify for business emails
    )
    
    db.add(user)
    db.flush()  # Get the user ID
    
    # Log user creation
    audit_log = AuditLog.create_log(
        organization_id=organization.id,
        user_id=user.id,
        action=AuditActions.USER_CREATED,
        entity_type=AuditEntityTypes.USER,
        entity_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        description=f"User '{user.full_name}' registered with role '{user_role}'"
    )
    db.add(audit_log)
    
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        # Log failed login attempt
        if user:
            audit_log = AuditLog.create_log(
                organization_id=user.organization_id,
                user_id=user.id,
                action=AuditActions.LOGIN_FAILED,
                entity_type=AuditEntityTypes.USER,
                entity_id=user.id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                description="Failed login attempt - incorrect password",
                severity="warning"
            )
            db.add(audit_log)
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated"
        )
    
    # Update last login time
    user.last_login = func.now()
    
    # Log successful login
    audit_log = AuditLog.create_log(
        organization_id=user.organization_id,
        user_id=user.id,
        action=AuditActions.LOGIN,
        entity_type=AuditEntityTypes.USER,
        entity_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        description="Successful login"
    )
    db.add(audit_log)
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    payload = verify_token(token_data.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile information
    """
    return UserProfile(**current_user.to_dict())

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    
    # Log password change
    audit_log = AuditLog.create_log(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditActions.PASSWORD_CHANGED,
        entity_type=AuditEntityTypes.USER,
        entity_id=current_user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        description="Password changed successfully"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user (mainly for audit logging)
    """
    # Log logout
    audit_log = AuditLog.create_log(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditActions.LOGOUT,
        entity_type=AuditEntityTypes.USER,
        entity_id=current_user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        description="User logged out"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Logged out successfully"}

