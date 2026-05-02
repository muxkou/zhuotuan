from fastapi import APIRouter

from backend.app.api.routers import health, v1

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(v1.router)
