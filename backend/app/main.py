"""
FastAPI application factory.
Fabrica da aplicacao FastAPI.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth.router import router as auth_router
from app.championships.router import router as championships_router
from app.config import settings
from app.dashboard.router import router as dashboard_router
from app.drivers.router import router as drivers_router
from app.health.router import router as health_router
from app.notifications.router import router as notifications_router
from app.penalties.router import router as penalties_router
from app.races.router import router as races_router
from app.results.router import router as results_router
from app.roles.router import permissions_router, roles_router, user_roles_router
from app.teams.router import router as teams_router
from app.uploads.router import router as uploads_router
from app.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan: startup and shutdown events.
    Ciclo de vida da aplicacao: eventos de inicializacao e encerramento.
    """
    # Startup: create uploads directory / Inicializacao: criar diretorio de uploads
    Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
    yield
    # Shutdown / Encerramento


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Cria e configura a aplicacao FastAPI.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="E-Sports Racing Management Platform / Plataforma de Gerenciamento de E-Sports Racing",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(permissions_router)
    app.include_router(roles_router)
    app.include_router(user_roles_router)
    app.include_router(teams_router)
    app.include_router(championships_router)
    app.include_router(races_router)
    app.include_router(results_router)
    app.include_router(drivers_router)
    app.include_router(dashboard_router)
    app.include_router(notifications_router)
    app.include_router(uploads_router)
    app.include_router(penalties_router)

    # Static files: serve uploaded images / Arquivos estaticos: servir imagens enviadas
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=upload_path), name="uploads")

    return app


app = create_app()
