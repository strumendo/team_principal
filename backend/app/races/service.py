"""
Races business logic.
Logica de negocios de corridas.
"""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship
from app.core.exceptions import ConflictException, NotFoundException
from app.races.models import Race, RaceStatus


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
    result = await db.execute(select(Championship).where(Championship.id == championship_id))
    if result.scalar_one_or_none() is None:
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
    result = await db.execute(select(Championship).where(Championship.id == championship_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundException("Championship not found")

    # Check unique name within championship / Verifica nome unico dentro do campeonato
    result = await db.execute(select(Race).where(Race.championship_id == championship_id, Race.name == name))
    if result.scalar_one_or_none() is not None:
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
    Delete a race.
    Exclui uma corrida.
    """
    await db.delete(race)
    await db.commit()
