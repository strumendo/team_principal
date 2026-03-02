"""
Telemetry business logic: lap times, car setups, driver comparison.
Logica de negocios de telemetria: tempos de volta, setups de carro, comparacao de pilotos.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.drivers.models import Driver
from app.races.models import Race
from app.teams.models import Team
from app.telemetry.models import CarSetup, LapTime

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


# --- Lap Time services / Servicos de tempo de volta ---


async def list_lap_times(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_id: uuid.UUID | None = None,
    team_id: uuid.UUID | None = None,
) -> list[LapTime]:
    """
    List lap times for a race, optionally filtered by driver or team.
    Lista tempos de volta de uma corrida, opcionalmente filtrados por piloto ou equipe.
    """
    await _validate_race(db, race_id)
    stmt = select(LapTime).where(LapTime.race_id == race_id).order_by(LapTime.lap_number)
    if driver_id is not None:
        stmt = stmt.where(LapTime.driver_id == driver_id)
    if team_id is not None:
        stmt = stmt.where(LapTime.team_id == team_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_lap_time_by_id(db: AsyncSession, lap_id: uuid.UUID) -> LapTime:
    """
    Get a lap time by ID. Raises NotFoundException if not found.
    Busca um tempo de volta por ID. Lanca NotFoundException se nao encontrado.
    """
    result = await db.execute(select(LapTime).where(LapTime.id == lap_id))
    lap = result.scalar_one_or_none()
    if lap is None:
        raise NotFoundException("Lap time not found / Tempo de volta nao encontrado")
    return lap


async def create_lap_time(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_id: uuid.UUID,
    team_id: uuid.UUID,
    lap_number: int,
    lap_time_ms: int,
    sector_1_ms: int | None = None,
    sector_2_ms: int | None = None,
    sector_3_ms: int | None = None,
    is_valid: bool = True,
    is_personal_best: bool = False,
) -> LapTime:
    """
    Create a single lap time. Validates FKs and uniqueness.
    Cria um tempo de volta. Valida FKs e unicidade.
    """
    await _validate_race(db, race_id)
    await _validate_driver(db, driver_id)
    await _validate_team(db, team_id)

    # Check unique constraint / Verifica constraint de unicidade
    existing = await db.execute(
        select(LapTime).where(
            LapTime.race_id == race_id,
            LapTime.driver_id == driver_id,
            LapTime.lap_number == lap_number,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictException("Lap time already exists for this driver/race/lap number")

    lap = LapTime(
        race_id=race_id,
        driver_id=driver_id,
        team_id=team_id,
        lap_number=lap_number,
        lap_time_ms=lap_time_ms,
        sector_1_ms=sector_1_ms,
        sector_2_ms=sector_2_ms,
        sector_3_ms=sector_3_ms,
        is_valid=is_valid,
        is_personal_best=is_personal_best,
    )
    db.add(lap)
    await db.commit()
    await db.refresh(lap)
    return lap


async def bulk_create_lap_times(
    db: AsyncSession,
    race_id: uuid.UUID,
    laps: list[dict],
) -> list[LapTime]:
    """
    Bulk create lap times for a race. Validates race exists.
    Cria tempos de volta em lote para uma corrida. Valida que a corrida existe.
    """
    await _validate_race(db, race_id)

    created: list[LapTime] = []
    for lap_data in laps:
        lap = LapTime(
            race_id=race_id,
            driver_id=lap_data["driver_id"],
            team_id=lap_data["team_id"],
            lap_number=lap_data["lap_number"],
            lap_time_ms=lap_data["lap_time_ms"],
            sector_1_ms=lap_data.get("sector_1_ms"),
            sector_2_ms=lap_data.get("sector_2_ms"),
            sector_3_ms=lap_data.get("sector_3_ms"),
            is_valid=lap_data.get("is_valid", True),
            is_personal_best=lap_data.get("is_personal_best", False),
        )
        db.add(lap)
        created.append(lap)

    await db.commit()
    for lap in created:
        await db.refresh(lap)
    return created


async def delete_lap_time(db: AsyncSession, lap: LapTime) -> None:
    """
    Delete a lap time.
    Exclui um tempo de volta.
    """
    await db.delete(lap)
    await db.commit()


async def get_lap_summary(db: AsyncSession, race_id: uuid.UUID) -> dict:
    """
    Get lap time summary for a race: fastest/avg per driver, overall fastest.
    Retorna resumo de tempos de volta: mais rapido/media por piloto, mais rapido geral.
    """
    await _validate_race(db, race_id)

    # Per-driver aggregates / Agregacoes por piloto
    stmt = (
        select(
            LapTime.driver_id,
            Driver.display_name.label("driver_display_name"),
            func.min(LapTime.lap_time_ms).label("fastest_lap_ms"),
            func.avg(LapTime.lap_time_ms).label("avg_lap_ms"),
            func.count(LapTime.id).label("total_laps"),
        )
        .join(Driver, LapTime.driver_id == Driver.id)
        .where(LapTime.race_id == race_id)
        .group_by(LapTime.driver_id, Driver.display_name)
        .order_by(func.min(LapTime.lap_time_ms))
    )
    result = await db.execute(stmt)
    rows = result.all()

    drivers = []
    for row in rows:
        # Find personal best lap number / Encontra numero da volta com melhor tempo pessoal
        pb_stmt = (
            select(LapTime.lap_number)
            .where(
                LapTime.race_id == race_id,
                LapTime.driver_id == row.driver_id,
                LapTime.is_personal_best == True,  # noqa: E712
            )
            .limit(1)
        )
        pb_result = await db.execute(pb_stmt)
        pb_lap = pb_result.scalar_one_or_none()

        drivers.append({
            "driver_id": row.driver_id,
            "driver_display_name": row.driver_display_name,
            "fastest_lap_ms": row.fastest_lap_ms,
            "avg_lap_ms": int(row.avg_lap_ms),
            "total_laps": row.total_laps,
            "personal_best_lap": pb_lap,
        })

    # Overall fastest / Volta mais rapida geral
    fastest_stmt = (
        select(LapTime)
        .where(LapTime.race_id == race_id)
        .order_by(LapTime.lap_time_ms)
        .limit(1)
    )
    fastest_result = await db.execute(fastest_stmt)
    overall_fastest = fastest_result.scalar_one_or_none()

    return {"drivers": drivers, "overall_fastest": overall_fastest}


# --- Car Setup services / Servicos de setup de carro ---


async def list_setups(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_id: uuid.UUID | None = None,
    team_id: uuid.UUID | None = None,
) -> list[CarSetup]:
    """
    List car setups for a race, optionally filtered.
    Lista setups de carro de uma corrida, opcionalmente filtrados.
    """
    await _validate_race(db, race_id)
    stmt = select(CarSetup).where(CarSetup.race_id == race_id).order_by(CarSetup.created_at)
    if driver_id is not None:
        stmt = stmt.where(CarSetup.driver_id == driver_id)
    if team_id is not None:
        stmt = stmt.where(CarSetup.team_id == team_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_setup_by_id(db: AsyncSession, setup_id: uuid.UUID) -> CarSetup:
    """
    Get a car setup by ID. Raises NotFoundException if not found.
    Busca um setup por ID. Lanca NotFoundException se nao encontrado.
    """
    result = await db.execute(select(CarSetup).where(CarSetup.id == setup_id))
    setup = result.scalar_one_or_none()
    if setup is None:
        raise NotFoundException("Car setup not found / Setup nao encontrado")
    return setup


async def create_setup(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_id: uuid.UUID,
    team_id: uuid.UUID,
    name: str,
    notes: str | None = None,
    front_wing: float | None = None,
    rear_wing: float | None = None,
    differential: float | None = None,
    brake_bias: float | None = None,
    tire_pressure_fl: float | None = None,
    tire_pressure_fr: float | None = None,
    tire_pressure_rl: float | None = None,
    tire_pressure_rr: float | None = None,
    suspension_stiffness: float | None = None,
    anti_roll_bar: float | None = None,
) -> CarSetup:
    """
    Create a car setup. Validates FKs.
    Cria um setup de carro. Valida FKs.
    """
    await _validate_race(db, race_id)
    await _validate_driver(db, driver_id)
    await _validate_team(db, team_id)

    setup = CarSetup(
        race_id=race_id,
        driver_id=driver_id,
        team_id=team_id,
        name=name,
        notes=notes,
        front_wing=front_wing,
        rear_wing=rear_wing,
        differential=differential,
        brake_bias=brake_bias,
        tire_pressure_fl=tire_pressure_fl,
        tire_pressure_fr=tire_pressure_fr,
        tire_pressure_rl=tire_pressure_rl,
        tire_pressure_rr=tire_pressure_rr,
        suspension_stiffness=suspension_stiffness,
        anti_roll_bar=anti_roll_bar,
    )
    db.add(setup)
    await db.commit()
    await db.refresh(setup)
    return setup


async def update_setup(
    db: AsyncSession,
    setup: CarSetup,
    name: str | None = None,
    notes: str | None = None,
    front_wing: float | None = None,
    rear_wing: float | None = None,
    differential: float | None = None,
    brake_bias: float | None = None,
    tire_pressure_fl: float | None = None,
    tire_pressure_fr: float | None = None,
    tire_pressure_rl: float | None = None,
    tire_pressure_rr: float | None = None,
    suspension_stiffness: float | None = None,
    anti_roll_bar: float | None = None,
    is_active: bool | None = None,
) -> CarSetup:
    """
    Update a car setup. Only updates non-None fields.
    Atualiza um setup de carro. So atualiza campos nao-None.
    """
    if name is not None:
        setup.name = name
    if notes is not None:
        setup.notes = notes
    if front_wing is not None:
        setup.front_wing = front_wing
    if rear_wing is not None:
        setup.rear_wing = rear_wing
    if differential is not None:
        setup.differential = differential
    if brake_bias is not None:
        setup.brake_bias = brake_bias
    if tire_pressure_fl is not None:
        setup.tire_pressure_fl = tire_pressure_fl
    if tire_pressure_fr is not None:
        setup.tire_pressure_fr = tire_pressure_fr
    if tire_pressure_rl is not None:
        setup.tire_pressure_rl = tire_pressure_rl
    if tire_pressure_rr is not None:
        setup.tire_pressure_rr = tire_pressure_rr
    if suspension_stiffness is not None:
        setup.suspension_stiffness = suspension_stiffness
    if anti_roll_bar is not None:
        setup.anti_roll_bar = anti_roll_bar
    if is_active is not None:
        setup.is_active = is_active

    await db.commit()
    await db.refresh(setup)
    return setup


async def delete_setup(db: AsyncSession, setup: CarSetup) -> None:
    """
    Delete a car setup.
    Exclui um setup de carro.
    """
    await db.delete(setup)
    await db.commit()


# --- Compare / Comparacao ---


async def compare_drivers(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_ids: list[uuid.UUID],
) -> list[dict]:
    """
    Compare lap times for up to 3 drivers in a race.
    Compara tempos de volta de ate 3 pilotos em uma corrida.
    """
    if len(driver_ids) > 3:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot compare more than 3 drivers / Nao e possivel comparar mais de 3 pilotos",
        )

    await _validate_race(db, race_id)

    comparisons = []
    for driver_id in driver_ids:
        driver = await _validate_driver(db, driver_id)
        laps_stmt = (
            select(LapTime)
            .where(LapTime.race_id == race_id, LapTime.driver_id == driver_id)
            .order_by(LapTime.lap_number)
        )
        result = await db.execute(laps_stmt)
        laps = list(result.scalars().all())
        comparisons.append({
            "driver_id": driver.id,
            "driver_display_name": driver.display_name,
            "laps": laps,
        })

    return comparisons
