"""
Races business logic.
Logica de negocios de corridas.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, championship_entries
from app.core.exceptions import ConflictException, NotFoundException
from app.races.models import Race, RaceStatus, race_entries
from app.teams.models import Team


async def list_races(
    db: AsyncSession,
    championship_id: uuid.UUID,
    status: RaceStatus | None = None,
    is_active: bool | None = None,
) -> list[Race]:
    """
    List all races of a championship, optionally filtered.
    Lista todas as corridas de um campeonato, opcionalmente filtradas.
    """
    # Validate championship exists / Valida que o campeonato existe
    champ_result = await db.execute(select(Championship).where(Championship.id == championship_id))
    if champ_result.scalar_one_or_none() is None:
        raise NotFoundException("Championship not found")

    stmt = select(Race).where(Race.championship_id == championship_id).order_by(Race.round_number)
    if status is not None:
        stmt = stmt.where(Race.status == status)
    if is_active is not None:
        stmt = stmt.where(Race.is_active == is_active)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_race_by_id(db: AsyncSession, race_id: uuid.UUID) -> Race:
    """
    Get a race by ID. Raises NotFoundException if not found.
    Busca uma corrida por ID. Lanca NotFoundException se nao encontrada.
    """
    result = await db.execute(select(Race).where(Race.id == race_id))
    race = result.scalar_one_or_none()
    if race is None:
        raise NotFoundException("Race not found")
    await db.refresh(race, ["teams"])
    return race


async def create_race(
    db: AsyncSession,
    championship_id: uuid.UUID,
    name: str,
    display_name: str,
    round_number: int,
    description: str | None = None,
    status: RaceStatus = RaceStatus.scheduled,
    scheduled_at: datetime | None = None,
    track_name: str | None = None,
    track_country: str | None = None,
    laps_total: int | None = None,
) -> Race:
    """
    Create a new race within a championship. Raises ConflictException if name already exists in championship.
    Cria uma nova corrida dentro de um campeonato. Lanca ConflictException se o nome ja existe no campeonato.
    """
    # Validate championship exists / Valida que o campeonato existe
    champ_result = await db.execute(select(Championship).where(Championship.id == championship_id))
    if champ_result.scalar_one_or_none() is None:
        raise NotFoundException("Championship not found")

    # Check unique name within championship / Verifica nome unico dentro do campeonato
    name_result = await db.execute(select(Race).where(Race.championship_id == championship_id, Race.name == name))
    if name_result.scalar_one_or_none() is not None:
        raise ConflictException("Race name already exists in this championship")

    race = Race(
        championship_id=championship_id,
        name=name,
        display_name=display_name,
        description=description,
        round_number=round_number,
        status=status,
        scheduled_at=scheduled_at,
        track_name=track_name,
        track_country=track_country,
        laps_total=laps_total,
    )
    db.add(race)
    await db.commit()
    await db.refresh(race)
    return race


async def update_race(
    db: AsyncSession,
    race: Race,
    display_name: str | None = None,
    description: str | None = None,
    round_number: int | None = None,
    status: RaceStatus | None = None,
    scheduled_at: datetime | None = None,
    track_name: str | None = None,
    track_country: str | None = None,
    laps_total: int | None = None,
    is_active: bool | None = None,
) -> Race:
    """
    Update race fields.
    Atualiza campos da corrida.
    """
    if display_name is not None:
        race.display_name = display_name
    if description is not None:
        race.description = description
    if round_number is not None:
        race.round_number = round_number
    if status is not None:
        race.status = status
    if scheduled_at is not None:
        race.scheduled_at = scheduled_at
    if track_name is not None:
        race.track_name = track_name
    if track_country is not None:
        race.track_country = track_country
    if laps_total is not None:
        race.laps_total = laps_total
    if is_active is not None:
        race.is_active = is_active
    await db.commit()
    await db.refresh(race)
    return race


async def delete_race(db: AsyncSession, race: Race) -> None:
    """
    Delete a race. Clears entries before deleting.
    Exclui uma corrida. Limpa inscricoes antes de excluir.
    """
    race.teams.clear()
    await db.flush()
    await db.delete(race)
    await db.commit()


# --- Entry services / Servicos de inscricao ---


async def list_race_entries(db: AsyncSession, race_id: uuid.UUID) -> list[dict[str, Any]]:
    """
    List all entries of a race with registration date.
    Lista todas as inscricoes de uma corrida com data de registro.
    """
    await get_race_by_id(db, race_id)

    stmt = (
        select(
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            Team.display_name.label("team_display_name"),
            Team.is_active.label("team_is_active"),
            race_entries.c.registered_at,
        )
        .join(Team, race_entries.c.team_id == Team.id)
        .where(race_entries.c.race_id == race_id)
        .order_by(Team.name)
    )
    result = await db.execute(stmt)
    return [row._asdict() for row in result.all()]


async def add_race_entry(db: AsyncSession, race_id: uuid.UUID, team_id: uuid.UUID) -> list[dict[str, Any]]:
    """
    Add a team to a race. Validates team is enrolled in the race's championship.
    Raises NotFoundException if race/team not found. Raises ConflictException if already enrolled
    or team not in championship.

    Adiciona uma equipe a uma corrida. Valida que a equipe esta inscrita no campeonato da corrida.
    Lanca NotFoundException se corrida/equipe nao encontrada. Lanca ConflictException se ja inscrita
    ou equipe nao esta no campeonato.
    """
    race = await get_race_by_id(db, race_id)

    result = await db.execute(select(Team).where(Team.id == team_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundException("Team not found")

    # Validate team is enrolled in the race's championship / Valida inscricao no campeonato
    champ_entry = await db.execute(
        select(championship_entries).where(
            championship_entries.c.championship_id == race.championship_id,
            championship_entries.c.team_id == team_id,
        )
    )
    if champ_entry.first() is None:
        raise ConflictException("Team is not enrolled in this championship")

    # Check for duplicate entry / Verifica inscricao duplicada
    existing = await db.execute(
        select(race_entries).where(
            race_entries.c.race_id == race_id,
            race_entries.c.team_id == team_id,
        )
    )
    if existing.first() is not None:
        raise ConflictException("Team is already enrolled in this race")

    await db.execute(race_entries.insert().values(race_id=race_id, team_id=team_id))
    await db.commit()

    return await list_race_entries(db, race_id)


async def remove_race_entry(db: AsyncSession, race_id: uuid.UUID, team_id: uuid.UUID) -> list[dict[str, Any]]:
    """
    Remove a team from a race. Raises NotFoundException if entry not found.
    Remove uma equipe de uma corrida. Lanca NotFoundException se inscricao nao encontrada.
    """
    await get_race_by_id(db, race_id)

    existing = await db.execute(
        select(race_entries).where(
            race_entries.c.race_id == race_id,
            race_entries.c.team_id == team_id,
        )
    )
    if existing.first() is None:
        raise NotFoundException("Team is not enrolled in this race")

    await db.execute(
        delete(race_entries).where(
            race_entries.c.race_id == race_id,
            race_entries.c.team_id == team_id,
        )
    )
    await db.commit()

    return await list_race_entries(db, race_id)
