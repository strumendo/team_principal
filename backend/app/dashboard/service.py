"""
Dashboard business logic.
Logica de negocios do dashboard.
"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus, championship_entries
from app.races.models import Race, RaceStatus
from app.results.service import get_championship_standings


async def get_dashboard_summary(
    db: AsyncSession,
    next_races_limit: int = 5,
    standings_limit: int = 5,
) -> dict[str, Any]:
    """
    Aggregate dashboard data: active championships, next races, and partial standings.
    Agrega dados do dashboard: campeonatos ativos, proximas corridas e classificacoes parciais.
    """
    # Query 1: Active championships with race counts and team counts
    # Query 1: Campeonatos ativos com contagem de corridas e equipes
    total_races_sq = (
        select(func.count(Race.id))
        .where(Race.championship_id == Championship.id)
        .correlate(Championship)
        .scalar_subquery()
    )
    completed_races_sq = (
        select(func.count(Race.id))
        .where(Race.championship_id == Championship.id, Race.status == RaceStatus.finished)
        .correlate(Championship)
        .scalar_subquery()
    )
    team_count_sq = (
        select(func.count(championship_entries.c.team_id))
        .where(championship_entries.c.championship_id == Championship.id)
        .correlate(Championship)
        .scalar_subquery()
    )

    champ_stmt = (
        select(
            Championship,
            total_races_sq.label("total_races"),
            completed_races_sq.label("completed_races"),
            team_count_sq.label("team_count"),
        )
        .where(Championship.status == ChampionshipStatus.active)
        .order_by(Championship.season_year.desc(), Championship.name)
    )
    champ_result = await db.execute(champ_stmt)
    champ_rows = champ_result.all()

    active_championships = []
    championship_ids = []
    for row in champ_rows:
        champ = row[0]
        championship_ids.append(champ.id)
        active_championships.append(
            {
                "id": champ.id,
                "name": champ.name,
                "display_name": champ.display_name,
                "season_year": champ.season_year,
                "status": champ.status.value,
                "start_date": champ.start_date,
                "end_date": champ.end_date,
                "total_races": row[1] or 0,
                "completed_races": row[2] or 0,
                "team_count": row[3] or 0,
            }
        )

    # Query 2: Next scheduled races across all active championships
    # Query 2: Proximas corridas agendadas em todos os campeonatos ativos
    next_races: list[dict[str, Any]] = []
    if championship_ids:
        race_stmt = (
            select(Race, Championship.display_name.label("championship_display_name"))
            .join(Championship, Race.championship_id == Championship.id)
            .where(
                Race.championship_id.in_(championship_ids),
                Race.status == RaceStatus.scheduled,
                Race.scheduled_at.is_not(None),
            )
            .order_by(Race.scheduled_at.asc())
            .limit(next_races_limit)
        )
        race_result = await db.execute(race_stmt)
        race_rows = race_result.all()

        for row in race_rows:
            race = row[0]
            next_races.append(
                {
                    "id": race.id,
                    "name": race.name,
                    "display_name": race.display_name,
                    "championship_id": race.championship_id,
                    "championship_display_name": row[1],
                    "round_number": race.round_number,
                    "scheduled_at": race.scheduled_at,
                    "track_name": race.track_name,
                    "track_country": race.track_country,
                }
            )

    # Query 3: Top N standings per active championship (reuse existing service)
    # Query 3: Top N classificacao por campeonato ativo (reutiliza servico existente)
    championship_standings: list[dict[str, Any]] = []
    for champ_data in active_championships:
        standings = await get_championship_standings(db, champ_data["id"])
        if standings:
            championship_standings.append(
                {
                    "championship_id": champ_data["id"],
                    "championship_display_name": champ_data["display_name"],
                    "standings": standings[:standings_limit],
                }
            )

    return {
        "active_championships": active_championships,
        "next_races": next_races,
        "championship_standings": championship_standings,
    }
