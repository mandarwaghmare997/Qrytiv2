"""
Authentication schemas for request/response validation
Handles user registration, login, and token management

Developed by: Qryti Dev Team
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserRegistration(BaseModel):
    """User registration request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    organization_name: str = Field(..., min_length=2, max_length=100, description="Organization name")
    organization_domain: Optional[str] = Field(None, description="Organization domain")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v
    
    @validator('email')
    def validate_email_domain(cls, v):
        """Validate email domain"""
        from app.core.security import security_middleware
        
        if not security_middleware.validate_email_domain(v):
            raise ValueError('Personal email domains are not allowed. Please use a business email.')
        
        return v

class UserLogin(BaseModel):
    """User login request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="JWT refresh token")

class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="User email address")

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v

class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v

class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str = Field(..., description="Email verification token")

class UserProfile(BaseModel):
    """User profile response schema"""
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    organization_id: int
    
    class Config:
        from_attributes = True

class OrganizationInfo(BaseModel):
    """Organization information schema"""
    id: int
    name: str
    domain: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserWithOrganization(BaseModel):
    """User with organization information"""
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    organization: OrganizationInfo
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    """Authentication response schema"""
    user: UserWithOrganization
    tokens: TokenResponse
    message: str = "Authentication successful"

class RegistrationResponse(BaseModel):
    """Registration response schema"""
    user: UserProfile
    message: str = "Registration successful. Please check your email for verification."

class MessageResponse(BaseModel):
    """Generic message response schema"""
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    success: bool = False

# Request validation schemas
class InviteUserRequest(BaseModel):
    """Invite user request schema"""
    email: EmailStr = Field(..., description="User email to invite")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    full_name: Optional[str] = Field(None, description="User full name")

class UpdateUserRequest(BaseModel):
    """Update user request schema"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = Field(None)
    is_active: Optional[bool] = Field(None)

class UpdateProfileRequest(BaseModel):
    """Update profile request schema"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    
# Token payload schemas
class TokenPayload(BaseModel):
    """Token payload schema"""
    sub: str  # User ID
    email: str
    role: str
    exp: int
    type: str  # access or refresh

