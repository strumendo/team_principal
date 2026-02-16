"""
Health check endpoints.
Endpoints de verificacao de saude.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict[str, str]:
    """
    Basic health check / Verificacao basica de saude.
    """
    return {"status": "ok"}


@router.get("/db")
async def health_check_db(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """
    Database health check / Verificacao de saude do banco de dados.
    """
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
