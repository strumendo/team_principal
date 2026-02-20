"""
Dashboard API router.
Router da API do dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permissions
from app.dashboard.schemas import DashboardSummaryResponse
from app.dashboard.service import get_dashboard_summary
from app.db.session import get_db
from app.users.models import User

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def read_dashboard_summary(
    _current_user: User = Depends(require_permissions("championships:read", "results:read")),
    db: AsyncSession = Depends(get_db),
) -> DashboardSummaryResponse:
    """
    Get dashboard summary: active championships, upcoming races, and partial standings.
    Obtem resumo do dashboard: campeonatos ativos, proximas corridas e classificacoes parciais.
    """
    return await get_dashboard_summary(db)  # type: ignore[return-value]
