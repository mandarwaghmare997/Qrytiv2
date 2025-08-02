"""
Qrytiv2 FastAPI Application
Main application entry point with all routes and middleware

Developed by: Qryti Dev Team
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import time
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db, check_db_connection
from app.core.database_setup import setup_database
from app.api.api_v1.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ISO 42001 AI Governance Platform",
    openapi_url="/api/v1/openapi.json" if not settings.is_production else None,
    docs_url="/api/v1/docs" if not settings.is_production else None,
    redoc_url="/api/v1/redoc" if not settings.is_production else None,
)

# CORS Middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Trusted Host Middleware (only in production)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["app.qryti.com", "*.qryti.com"]
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for debugging and monitoring"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} - {process_time:.3f}s"
        )
        
        # Add process time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # Log errors
        process_time = time.time() - start_time
        logger.error(f"Request failed: {str(e)} - {process_time:.3f}s")
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )

# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": getattr(exc, 'error_code', None)
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    try:
        # Setup database
        logger.info("Setting up database...")
        if setup_database():
            logger.info("✅ Database setup completed successfully")
        else:
            logger.error("❌ Database setup failed")
            raise Exception("Database setup failed")
        
        # Check database connection
        if check_db_connection():
            logger.info("✅ Database connection verified")
        else:
            logger.error("❌ Database connection failed")
            raise Exception("Database connection failed")
        
        # Create necessary directories
        Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
        Path(settings.REPORTS_DIR).mkdir(exist_ok=True)
        Path(settings.CERTIFICATES_DIR).mkdir(exist_ok=True)
        Path("static").mkdir(exist_ok=True)
        
        logger.info("✅ Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down application...")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_healthy = check_db_connection()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "connected" if db_healthy else "disconnected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/api/v1/docs" if not settings.is_production else None,
        "health": "/health"
    }

# API routes
app.include_router(api_router, prefix="/api/v1")

# Static files (for uploaded files, reports, etc.)
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Development info endpoint
if not settings.is_production:
    @app.get("/api/v1/info")
    async def app_info():
        """Application information (development only)"""
        return {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
            "cors_origins": settings.ALLOWED_HOSTS,
            "features": {
                "authentication": True,
                "email_verification": bool(settings.SMTP_HOST),
                "file_upload": True,
                "s3_storage": bool(settings.S3_BUCKET),
                "slack_notifications": bool(settings.SLACK_WEBHOOK_URL)
            }
        }

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.is_production else "debug"
    )

