"""
Pit stop and race strategy business logic.
Logica de negocios de pit stop e estrategia de corrida.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.drivers.models import Driver
from app.pitstops.models import PitStop, RaceStrategy, TireCompound
from app.races.models import Race
from app.teams.models import Team

# --- Helpers / Auxiliares ---


async def _validate_race(db: AsyncSession, race_id: uuid.UUID) -> Race:
    """Validate race exists / Valida que a corrida existe."""
    result = await db.execute(select(Race).where(Race.id == race_id))
    race = result.scalar_one_or_none()
    if race is None:
        raise NotFoundException("Race not found / Corrida nao encontrada")
    return race


async def _validate_driver(db: AsyncSession, driver_id: uuid.UUID) -> Driver:
    """Validate driver exists / Valida que o piloto existe."""
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if driver is None:
        raise NotFoundException("Driver not found / Piloto nao encontrado")
    return driver


async def _validate_team(db: AsyncSession, team_id: uuid.UUID) -> Team:
    """Validate team exists / Valida que a equipe existe."""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if team is None:
        raise NotFoundException("Team not found / Equipe nao encontrada")
    return team


# --- Pit Stop services / Servicos de pit stop ---


async def list_pit_stops(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_id: uuid.UUID | None = None,
    team_id: uuid.UUID | None = None,
) -> list[PitStop]:
    """
    List pit stops for a race, optionally filtered by driver or team.
    Lista pit stops de uma corrida, opcionalmente filtrados por piloto ou equipe.
    """
    await _validate_race(db, race_id)
    stmt = select(PitStop).where(PitStop.race_id == race_id).order_by(PitStop.lap_number)
    if driver_id is not None:
        stmt = stmt.where(PitStop.driver_id == driver_id)
    if team_id is not None:
        stmt = stmt.where(PitStop.team_id == team_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_pit_stop_by_id(db: AsyncSession, pit_stop_id: uuid.UUID) -> PitStop:
    """
    Get a pit stop by ID. Raises NotFoundException if not found.
    Busca um pit stop por ID. Lanca NotFoundException se nao encontrado.
    """
    result = await db.execute(select(PitStop).where(PitStop.id == pit_stop_id))
    pit_stop = result.scalar_one_or_none()
    if pit_stop is None:
        raise NotFoundException("Pit stop not found / Pit stop nao encontrado")
    return pit_stop


async def create_pit_stop(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_id: uuid.UUID,
    team_id: uuid.UUID,
    lap_number: int,
    duration_ms: int,
    tire_from: TireCompound | None = None,
    tire_to: TireCompound | None = None,
    notes: str | None = None,
) -> PitStop:
    """
    Create a pit stop. Validates FKs and uniqueness.
    Cria um pit stop. Valida FKs e unicidade.
    """
    await _validate_race(db, race_id)
    await _validate_driver(db, driver_id)
    await _validate_team(db, team_id)

    # Check unique constraint / Verifica constraint de unicidade
    existing = await db.execute(
        select(PitStop).where(
            PitStop.race_id == race_id,
            PitStop.driver_id == driver_id,
            PitStop.lap_number == lap_number,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictException("Pit stop already exists for this driver/race/lap number")

    pit_stop = PitStop(
        race_id=race_id,
        driver_id=driver_id,
        team_id=team_id,
        lap_number=lap_number,
        duration_ms=duration_ms,
        tire_from=tire_from,
        tire_to=tire_to,
        notes=notes,
    )
    db.add(pit_stop)
    await db.commit()
    await db.refresh(pit_stop)
    return pit_stop


async def update_pit_stop(
    db: AsyncSession,
    pit_stop: PitStop,
    duration_ms: int | None = None,
    tire_from: TireCompound | None = None,
    tire_to: TireCompound | None = None,
    notes: str | None = None,
) -> PitStop:
    """
    Update a pit stop. Only updates non-None fields.
    Atualiza um pit stop. So atualiza campos nao-None.
    """
    if duration_ms is not None:
        pit_stop.duration_ms = duration_ms
    if tire_from is not None:
        pit_stop.tire_from = tire_from
    if tire_to is not None:
        pit_stop.tire_to = tire_to
    if notes is not None:
        pit_stop.notes = notes

    await db.commit()
    await db.refresh(pit_stop)
    return pit_stop


async def delete_pit_stop(db: AsyncSession, pit_stop: PitStop) -> None:
    """
    Delete a pit stop.
    Exclui um pit stop.
    """
    await db.delete(pit_stop)
    await db.commit()


async def get_pit_stop_summary(db: AsyncSession, race_id: uuid.UUID) -> dict[str, list[dict[str, object]]]:
    """
    Get pit stop summary for a race: total stops, avg duration, fastest per driver.
    Retorna resumo de pit stops: total de paradas, duracao media, mais rapida por piloto.
    """
    await _validate_race(db, race_id)

    stmt = (
        select(
            PitStop.driver_id,
            Driver.display_name.label("driver_display_name"),
            func.count(PitStop.id).label("total_stops"),
            func.avg(PitStop.duration_ms).label("avg_duration_ms"),
            func.min(PitStop.duration_ms).label("fastest_pit_ms"),
        )
        .join(Driver, PitStop.driver_id == Driver.id)
        .where(PitStop.race_id == race_id)
        .group_by(PitStop.driver_id, Driver.display_name)
        .order_by(func.min(PitStop.duration_ms))
    )
    result = await db.execute(stmt)
    rows = result.all()

    drivers = []
    for row in rows:
        drivers.append({
            "driver_id": row.driver_id,
            "driver_display_name": row.driver_display_name,
            "total_stops": row.total_stops,
            "avg_duration_ms": int(row.avg_duration_ms),
            "fastest_pit_ms": row.fastest_pit_ms,
        })

    return {"drivers": drivers}


# --- Race Strategy services / Servicos de estrategia de corrida ---


async def list_strategies(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_id: uuid.UUID | None = None,
    team_id: uuid.UUID | None = None,
) -> list[RaceStrategy]:
    """
    List race strategies for a race, optionally filtered.
    Lista estrategias de corrida, opcionalmente filtradas.
    """
    await _validate_race(db, race_id)
    stmt = select(RaceStrategy).where(RaceStrategy.race_id == race_id).order_by(RaceStrategy.created_at)
    if driver_id is not None:
        stmt = stmt.where(RaceStrategy.driver_id == driver_id)
    if team_id is not None:
        stmt = stmt.where(RaceStrategy.team_id == team_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_strategy_by_id(db: AsyncSession, strategy_id: uuid.UUID) -> RaceStrategy:
    """
    Get a race strategy by ID. Raises NotFoundException if not found.
    Busca uma estrategia por ID. Lanca NotFoundException se nao encontrada.
    """
    result = await db.execute(select(RaceStrategy).where(RaceStrategy.id == strategy_id))
    strategy = result.scalar_one_or_none()
    if strategy is None:
        raise NotFoundException("Strategy not found / Estrategia nao encontrada")
    return strategy


async def create_strategy(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_id: uuid.UUID,
    team_id: uuid.UUID,
    name: str,
    description: str | None = None,
    target_stops: int = 1,
    planned_laps: str | None = None,
    starting_compound: TireCompound | None = None,
) -> RaceStrategy:
    """
    Create a race strategy. Validates FKs.
    Cria uma estrategia de corrida. Valida FKs.
    """
    await _validate_race(db, race_id)
    await _validate_driver(db, driver_id)
    await _validate_team(db, team_id)

    strategy = RaceStrategy(
        race_id=race_id,
        driver_id=driver_id,
        team_id=team_id,
        name=name,
        description=description,
        target_stops=target_stops,
        planned_laps=planned_laps,
        starting_compound=starting_compound,
    )
    db.add(strategy)
    await db.commit()
    await db.refresh(strategy)
    return strategy


async def update_strategy(
    db: AsyncSession,
    strategy: RaceStrategy,
    name: str | None = None,
    description: str | None = None,
    target_stops: int | None = None,
    planned_laps: str | None = None,
    starting_compound: TireCompound | None = None,
    is_active: bool | None = None,
) -> RaceStrategy:
    """
    Update a race strategy. Only updates non-None fields.
    Atualiza uma estrategia de corrida. So atualiza campos nao-None.
    """
    if name is not None:
        strategy.name = name
    if description is not None:
        strategy.description = description
    if target_stops is not None:
        strategy.target_stops = target_stops
    if planned_laps is not None:
        strategy.planned_laps = planned_laps
    if starting_compound is not None:
        strategy.starting_compound = starting_compound
    if is_active is not None:
        strategy.is_active = is_active

    await db.commit()
    await db.refresh(strategy)
    return strategy


async def delete_strategy(db: AsyncSession, strategy: RaceStrategy) -> None:
    """
    Delete a race strategy.
    Exclui uma estrategia de corrida.
    """
    await db.delete(strategy)
    await db.commit()
