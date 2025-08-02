"""
API Router Configuration
Configures all API endpoints and routes for the Qrytiv2 backend

Developed by: Qryti Dev Team
"""

from fastapi import APIRouter

from .endpoints import auth, users, organizations, ai_models, requirements

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(ai_models.router, prefix="/ai-models", tags=["ai-models"])
api_router.include_router(requirements.router, prefix="/requirements", tags=["requirements"])

