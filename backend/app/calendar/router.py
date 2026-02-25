"""
Calendar API router.
Router da API do calendario.
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.calendar.schemas import CalendarRaceResponse
from app.calendar.service import list_calendar_races
from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.users.models import User

router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])


def _current_year() -> int:
    return datetime.now(UTC).year


def _current_month() -> int:
    return datetime.now(UTC).month


@router.get("/races", response_model=list[CalendarRaceResponse])
async def read_calendar_races(
    year: int = Query(
        default_factory=_current_year,
        description="Year to query / Ano a consultar",
    ),
    month: int = Query(
        default_factory=_current_month,
        description="Month to query (1-12) / Mes a consultar (1-12)",
    ),
    championship_id: uuid.UUID | None = Query(
        default=None,
        description="Filter by championship / Filtrar por campeonato",
    ),
    _current_user: User = Depends(require_permissions("races:read")),
    db: AsyncSession = Depends(get_db),
) -> list[CalendarRaceResponse]:
    """
    List races for a given year/month across all or filtered championships.
    Returns races ordered by scheduled_at.

    Lista corridas para um dado ano/mes em todos ou campeonatos filtrados.
    Retorna corridas ordenadas por scheduled_at.
    """
    return await list_calendar_races(db, year, month, championship_id)  # type: ignore[return-value]
