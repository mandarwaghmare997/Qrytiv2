"""
API Router
Main API router that includes all endpoint modules
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, organizations, ai_models, requirements, admin, evidence_review, certificates

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(ai_models.router, prefix="/ai-models", tags=["ai-models"])
api_router.include_router(requirements.router, prefix="/requirements", tags=["requirements"])

# Admin endpoints
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(evidence_review.router, prefix="/admin", tags=["evidence-review"])
api_router.include_router(certificates.router, prefix="/admin", tags=["certificates"])