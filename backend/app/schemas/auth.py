"""
Authentication Schemas
Pydantic models for authentication requests and responses

Developed by: Qryti Dev Team
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from app.core.security import validate_business_email, validate_password_strength

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    organization_name: str
    position: Optional[str] = None
    industry: Optional[str] = None
    size_category: Optional[str] = None
    geographic_scope: Optional[str] = None
    
    @validator('email')
    def validate_email_domain(cls, v):
        if not validate_business_email(v):
            raise ValueError('Personal email addresses are not allowed. Please use your business email.')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip().title()
    
    @validator('organization_name')
    def validate_organization_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Organization name must be at least 2 characters long')
        return v.strip()

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    
    @validator('email')
    def validate_email_format(cls, v):
        return v.lower()

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefresh(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str

class PasswordChange(BaseModel):
    """Schema for password change request"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v

class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr
    
    @validator('email')
    def validate_email_format(cls, v):
        return v.lower()

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v

class UserProfile(BaseModel):
    """Schema for user profile response"""
    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    position: Optional[str]
    role: str
    organization_id: int
    is_active: bool
    is_email_verified: bool
    last_login: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True

