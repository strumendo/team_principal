"""
Calendar business logic.
Logica de negocios do calendario.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship
from app.races.models import Race


async def list_calendar_races(
    db: AsyncSession,
    year: int,
    month: int,
    championship_id: uuid.UUID | None = None,
) -> list[dict[str, Any]]:
    """
    List races for a given year/month, ordered by scheduled_at.
    Optionally filter by championship_id.

    Lista corridas para um dado ano/mes, ordenadas por scheduled_at.
    Opcionalmente filtra por championship_id.
    """
    # Build date range for the month / Constroi intervalo de datas para o mes
    start_dt = datetime(year, month, 1, tzinfo=UTC)
    end_dt = datetime(year + 1, 1, 1, tzinfo=UTC) if month == 12 else datetime(year, month + 1, 1, tzinfo=UTC)

    champ_display = Championship.display_name.label("championship_display_name")
    champ_status = Championship.status.label("championship_status")

    stmt = (
        select(Race, champ_display, champ_status)
        .join(Championship, Race.championship_id == Championship.id)
        .where(
            Race.scheduled_at.is_not(None),
            Race.scheduled_at >= start_dt,
            Race.scheduled_at < end_dt,
        )
        .order_by(Race.scheduled_at.asc())
    )

    if championship_id is not None:
        stmt = stmt.where(Race.championship_id == championship_id)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "id": row[0].id,
            "display_name": row[0].display_name,
            "round_number": row[0].round_number,
            "status": row[0].status.value,
            "scheduled_at": row[0].scheduled_at,
            "track_name": row[0].track_name,
            "track_country": row[0].track_country,
            "championship_id": row[0].championship_id,
            "championship_display_name": row[1],
            "championship_status": row[2].value if hasattr(row[2], "value") else row[2],
        }
        for row in rows
    ]
