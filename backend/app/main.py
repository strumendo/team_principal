"""
FastAPI application factory.
Fabrica da aplicacao FastAPI.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.health.router import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan: startup and shutdown events.
    Ciclo de vida da aplicacao: eventos de inicializacao e encerramento.
    """
    # Startup / Inicializacao
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

    return app


app = create_app()
