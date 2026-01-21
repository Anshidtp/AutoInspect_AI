from fastapi import APIRouter
from backend.api.endpoints import detection, estimation

# Create v1 API router
api_router = APIRouter(prefix="/api/v1")

# Include endpoint routers
api_router.include_router(detection.router)
api_router.include_router(estimation.router)