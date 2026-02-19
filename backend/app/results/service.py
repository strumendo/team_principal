"""
Race results business logic.
Logica de negocios de resultados de corrida.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
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
) -> RaceResult:
    """
    Update race result fields.
    Atualiza campos do resultado de corrida.
    """
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
