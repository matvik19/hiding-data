from fastapi import APIRouter
from app.api.api_v1.endpoints import healthcheck, permissions

api_router = APIRouter()

api_router.include_router(healthcheck.router)
api_router.include_router(permissions.router, prefix="/api", tags=["permissions"])
