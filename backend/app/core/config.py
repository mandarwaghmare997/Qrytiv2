"""
Qrytiv2 Configuration Settings
Handles environment variables and application configuration

Developed by: Qryti Dev Team
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Qrytiv2"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "qrytiv2-super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite:///./qrytiv2.db"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:5173", "https://qryti.com"]
    
    # File Storage
    STORAGE_TYPE: str = "local"  # local, s3
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "image/jpeg",
        "image/png",
        "image/gif",
        "text/plain",
        "text/csv"
    ]
    
    # AWS S3 (if using S3 storage)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: Optional[str] = None
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: str = "noreply@qryti.com"
    
    # Slack Notifications
    SLACK_WEBHOOK_URL: Optional[str] = None
    
    # Blocked Email Domains (personal email providers)
    BLOCKED_EMAIL_DOMAINS: List[str] = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
        "aol.com", "icloud.com", "protonmail.com", "mail.com",
        "yandex.com", "zoho.com", "tutanota.com"
    ]
    
    # ISO 42001 Configuration
    DEFAULT_VALIDITY_PERIOD_MONTHS: int = 12
    CERTIFICATION_THRESHOLD_SCORE: float = 80.0
    
    # Reporting
    REPORTS_DIR: str = "reports"
    CERTIFICATES_DIR: str = "certificates"
    
    # Audit Trail
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years for compliance
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create necessary directories
        Path(self.UPLOAD_DIR).mkdir(exist_ok=True)
        Path(self.REPORTS_DIR).mkdir(exist_ok=True)
        Path(self.CERTIFICATES_DIR).mkdir(exist_ok=True)
        Path("static").mkdir(exist_ok=True)
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for SQLAlchemy"""
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL
        elif self.DATABASE_URL.startswith("postgresql"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
        return self.DATABASE_URL
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"

# Global settings instance
settings = Settings()

