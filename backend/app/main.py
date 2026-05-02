from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.config import get_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app


app = create_app()
