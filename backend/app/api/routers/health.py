from fastapi import APIRouter

from backend.app.config import get_settings

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str | bool]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "debug": settings.app_debug,
    }
