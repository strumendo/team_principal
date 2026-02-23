"""
Race results business logic.
Logica de negocios de resultados de corrida.
"""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship
from app.core.exceptions import ConflictException, NotFoundException
from app.drivers.models import Driver
from app.races.models import Race, RaceStatus, race_entries
from app.results.models import RaceResult
from app.teams.models import Team


async def list_race_results(db: AsyncSession, race_id: uuid.UUID) -> list[RaceResult]:
    """
    List all results for a race, ordered by position.
    Lista todos os resultados de uma corrida, ordenados por posicao.
    """
    race_query = await db.execute(select(Race).where(Race.id == race_id))
    if race_query.scalar_one_or_none() is None:
        raise NotFoundException("Race not found")

    stmt = select(RaceResult).where(RaceResult.race_id == race_id).order_by(RaceResult.position)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_result_by_id(db: AsyncSession, result_id: uuid.UUID) -> RaceResult:
    """
    Get a race result by ID. Raises NotFoundException if not found.
    Busca um resultado de corrida por ID. Lanca NotFoundException se nao encontrado.
    """
    stmt = select(RaceResult).where(RaceResult.id == result_id)
    row = await db.execute(stmt)
    race_result = row.scalar_one_or_none()
    if race_result is None:
        raise NotFoundException("Race result not found")
    return race_result


async def create_result(
    db: AsyncSession,
    race_id: uuid.UUID,
    team_id: uuid.UUID,
    position: int,
    points: float = 0.0,
    laps_completed: int | None = None,
    fastest_lap: bool = False,
    dnf: bool = False,
    dsq: bool = False,
    notes: str | None = None,
    driver_id: uuid.UUID | None = None,
) -> RaceResult:
    """
    Create a race result. Validates race is finished, team is enrolled, no duplicate, position unique among non-DSQ.
    Cria um resultado de corrida. Valida que corrida esta finalizada, equipe inscrita, sem duplicata, posicao unica
    entre nao-DSQ.
    """
    # Validate race exists and is finished / Valida que a corrida existe e esta finalizada
    race_query = await db.execute(select(Race).where(Race.id == race_id))
    race = race_query.scalar_one_or_none()
    if race is None:
        raise NotFoundException("Race not found")
    if race.status != RaceStatus.finished:
        raise ConflictException("Race is not finished")

    # Validate team exists / Valida que a equipe existe
    team_query = await db.execute(select(Team).where(Team.id == team_id))
    if team_query.scalar_one_or_none() is None:
        raise NotFoundException("Team not found")

    # Validate team is enrolled in the race / Valida que a equipe esta inscrita na corrida
    entry_query = await db.execute(
        select(race_entries).where(
            race_entries.c.race_id == race_id,
            race_entries.c.team_id == team_id,
        )
    )
    if entry_query.first() is None:
        raise ConflictException("Team is not enrolled in this race")

    # Check duplicate team result / Verifica resultado duplicado para equipe
    dup_query = await db.execute(select(RaceResult).where(RaceResult.race_id == race_id, RaceResult.team_id == team_id))
    if dup_query.scalar_one_or_none() is not None:
        raise ConflictException("Result already exists for this team in this race")

    # Validate driver if provided / Valida piloto se fornecido
    if driver_id is not None:
        driver_query = await db.execute(select(Driver).where(Driver.id == driver_id))
        driver = driver_query.scalar_one_or_none()
        if driver is None:
            raise NotFoundException("Driver not found")
        if driver.team_id != team_id:
            raise ConflictException("Driver does not belong to the specified team")

    # Check position uniqueness among non-DSQ results / Verifica unicidade de posicao entre nao-DSQ
    if not dsq:
        pos_query = await db.execute(
            select(RaceResult).where(
                RaceResult.race_id == race_id,
                RaceResult.position == position,
                RaceResult.dsq == False,  # noqa: E712
            )
        )
        if pos_query.scalar_one_or_none() is not None:
            raise ConflictException("Position already taken by a non-DSQ result")

    race_result = RaceResult(
        race_id=race_id,
        team_id=team_id,
        driver_id=driver_id,
        position=position,
        points=points,
        laps_completed=laps_completed,
        fastest_lap=fastest_lap,
        dnf=dnf,
        dsq=dsq,
        notes=notes,
    )
    db.add(race_result)
    await db.commit()
    await db.refresh(race_result)
    return race_result


async def update_result(
    db: AsyncSession,
    race_result: RaceResult,
    position: int | None = None,
    points: float | None = None,
    laps_completed: int | None = None,
    fastest_lap: bool | None = None,
    dnf: bool | None = None,
    dsq: bool | None = None,
    notes: str | None = None,
    driver_id: uuid.UUID | None = None,
) -> RaceResult:
    """
    Update race result fields.
    Atualiza campos do resultado de corrida.
    """
    # Validate driver if provided / Valida piloto se fornecido
    if driver_id is not None:
        driver_query = await db.execute(select(Driver).where(Driver.id == driver_id))
        driver = driver_query.scalar_one_or_none()
        if driver is None:
            raise NotFoundException("Driver not found")
        if driver.team_id != race_result.team_id:
            raise ConflictException("Driver does not belong to the result's team")

    # Determine effective DSQ for position check / Determina DSQ efetivo para verificacao de posicao
    effective_dsq = dsq if dsq is not None else race_result.dsq
    effective_position = position if position is not None else race_result.position

    # Check position uniqueness among non-DSQ if position changed / Verifica unicidade se posicao mudou
    if position is not None and not effective_dsq:
        pos_query = await db.execute(
            select(RaceResult).where(
                RaceResult.race_id == race_result.race_id,
                RaceResult.position == effective_position,
                RaceResult.dsq == False,  # noqa: E712
                RaceResult.id != race_result.id,
            )
        )
        if pos_query.scalar_one_or_none() is not None:
            raise ConflictException("Position already taken by a non-DSQ result")

    if driver_id is not None:
        race_result.driver_id = driver_id
    if position is not None:
        race_result.position = position
    if points is not None:
        race_result.points = points
    if laps_completed is not None:
        race_result.laps_completed = laps_completed
    if fastest_lap is not None:
        race_result.fastest_lap = fastest_lap
    if dnf is not None:
        race_result.dnf = dnf
    if dsq is not None:
        race_result.dsq = dsq
    if notes is not None:
        race_result.notes = notes

    await db.commit()
    await db.refresh(race_result)
    return race_result


async def delete_result(db: AsyncSession, race_result: RaceResult) -> None:
    """
    Delete a race result.
    Exclui um resultado de corrida.
    """
    await db.delete(race_result)
    await db.commit()


async def get_championship_standings(db: AsyncSession, championship_id: uuid.UUID) -> list[dict[str, Any]]:
    """
    Compute championship standings by aggregating race results.
    Excludes DSQ results. Wins counted via separate query for SQLite compatibility.

    Calcula classificacao do campeonato agregando resultados de corrida.
    Exclui resultados DSQ. Vitorias contadas via query separada para compatibilidade com SQLite.
    """
    # Validate championship exists / Valida que o campeonato existe
    champ_query = await db.execute(select(Championship).where(Championship.id == championship_id))
    if champ_query.scalar_one_or_none() is None:
        raise NotFoundException("Championship not found")

    # Main query: total points and races scored / Query principal: pontos totais e corridas pontuadas
    points_stmt = (
        select(
            RaceResult.team_id,
            Team.name.label("team_name"),
            Team.display_name.label("team_display_name"),
            func.sum(RaceResult.points).label("total_points"),
            func.count(RaceResult.id).label("races_scored"),
        )
        .join(Race, RaceResult.race_id == Race.id)
        .join(Team, RaceResult.team_id == Team.id)
        .where(Race.championship_id == championship_id, RaceResult.dsq == False)  # noqa: E712
        .group_by(RaceResult.team_id, Team.name, Team.display_name)
        .order_by(func.sum(RaceResult.points).desc())
    )
    points_result = await db.execute(points_stmt)
    points_rows = points_result.all()

    # Wins query (separate for SQLite compat) / Query de vitorias (separada para compatibilidade SQLite)
    wins_stmt = (
        select(
            RaceResult.team_id,
            func.count(RaceResult.id).label("wins"),
        )
        .join(Race, RaceResult.race_id == Race.id)
        .where(
            Race.championship_id == championship_id,
            RaceResult.position == 1,
            RaceResult.dsq == False,  # noqa: E712
        )
        .group_by(RaceResult.team_id)
    )
    wins_result = await db.execute(wins_stmt)
    wins_map: dict[uuid.UUID, int] = {row.team_id: row.wins for row in wins_result.all()}

    standings: list[dict[str, Any]] = []
    for idx, row in enumerate(points_rows, start=1):
        standings.append(
            {
                "position": idx,
                "team_id": row.team_id,
                "team_name": row.team_name,
                "team_display_name": row.team_display_name,
                "total_points": float(row.total_points),
                "races_scored": row.races_scored,
                "wins": wins_map.get(row.team_id, 0),
            }
        )

    return standings


async def get_driver_championship_standings(db: AsyncSession, championship_id: uuid.UUID) -> list[dict[str, Any]]:
    """
    Compute driver championship standings by aggregating race results per driver.
    Only includes results that have a driver_id. Excludes DSQ results.
    Wins counted via separate query for SQLite compatibility.

    Calcula classificacao de pilotos no campeonato agregando resultados por piloto.
    Inclui apenas resultados que possuem driver_id. Exclui resultados DSQ.
    Vitorias contadas via query separada para compatibilidade com SQLite.
    """
    # Validate championship exists / Valida que o campeonato existe
    champ_query = await db.execute(select(Championship).where(Championship.id == championship_id))
    if champ_query.scalar_one_or_none() is None:
        raise NotFoundException("Championship not found")

    # Main query: total points and races scored per driver / Query principal por piloto
    points_stmt = (
        select(
            RaceResult.driver_id,
            Driver.name.label("driver_name"),
            Driver.display_name.label("driver_display_name"),
            Driver.abbreviation.label("driver_abbreviation"),
            Driver.team_id.label("team_id"),
            Team.name.label("team_name"),
            Team.display_name.label("team_display_name"),
            func.sum(RaceResult.points).label("total_points"),
            func.count(RaceResult.id).label("races_scored"),
        )
        .join(Race, RaceResult.race_id == Race.id)
        .join(Driver, RaceResult.driver_id == Driver.id)
        .join(Team, Driver.team_id == Team.id)
        .where(
            Race.championship_id == championship_id,
            RaceResult.dsq == False,  # noqa: E712
            RaceResult.driver_id.isnot(None),
        )
        .group_by(
            RaceResult.driver_id,
            Driver.name,
            Driver.display_name,
            Driver.abbreviation,
            Driver.team_id,
            Team.name,
            Team.display_name,
        )
        .order_by(func.sum(RaceResult.points).desc())
    )
    points_result = await db.execute(points_stmt)
    points_rows = points_result.all()

    # Wins query per driver (separate for SQLite compat) / Query de vitorias por piloto
    wins_stmt = (
        select(
            RaceResult.driver_id,
            func.count(RaceResult.id).label("wins"),
        )
        .join(Race, RaceResult.race_id == Race.id)
        .where(
            Race.championship_id == championship_id,
            RaceResult.position == 1,
            RaceResult.dsq == False,  # noqa: E712
            RaceResult.driver_id.isnot(None),
        )
        .group_by(RaceResult.driver_id)
    )
    wins_result = await db.execute(wins_stmt)
    wins_map: dict[uuid.UUID, int] = {row.driver_id: row.wins for row in wins_result.all()}

    standings: list[dict[str, Any]] = []
    for idx, row in enumerate(points_rows, start=1):
        standings.append(
            {
                "position": idx,
                "driver_id": row.driver_id,
                "driver_name": row.driver_name,
                "driver_display_name": row.driver_display_name,
                "driver_abbreviation": row.driver_abbreviation,
                "team_id": row.team_id,
                "team_name": row.team_name,
                "team_display_name": row.team_display_name,
                "total_points": float(row.total_points),
                "races_scored": row.races_scored,
                "wins": wins_map.get(row.driver_id, 0),
            }
        )

    return standings
