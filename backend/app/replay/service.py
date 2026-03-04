"""
Race replay business logic.
Logica de negocios de replay de corrida.
"""

import uuid
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.drivers.models import Driver
from app.pitstops.models import PitStop
from app.races.models import Race
from app.replay.models import LapPosition, RaceEvent, RaceEventType
from app.results.models import RaceResult
from app.teams.models import Team
from app.telemetry.models import LapTime

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


# --- LapPosition services / Servicos de posicao por volta ---


async def list_positions(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_id: uuid.UUID | None = None,
    team_id: uuid.UUID | None = None,
    lap_number: int | None = None,
) -> list[LapPosition]:
    """
    List lap positions for a race, optionally filtered.
    Lista posicoes por volta de uma corrida, opcionalmente filtradas.
    """
    await _validate_race(db, race_id)
    stmt = (
        select(LapPosition).where(LapPosition.race_id == race_id).order_by(LapPosition.lap_number, LapPosition.position)
    )
    if driver_id is not None:
        stmt = stmt.where(LapPosition.driver_id == driver_id)
    if team_id is not None:
        stmt = stmt.where(LapPosition.team_id == team_id)
    if lap_number is not None:
        stmt = stmt.where(LapPosition.lap_number == lap_number)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_position_by_id(db: AsyncSession, position_id: uuid.UUID) -> LapPosition:
    """
    Get a lap position by ID. Raises NotFoundException if not found.
    Busca uma posicao por ID. Lanca NotFoundException se nao encontrada.
    """
    result = await db.execute(select(LapPosition).where(LapPosition.id == position_id))
    position = result.scalar_one_or_none()
    if position is None:
        raise NotFoundException("Lap position not found / Posicao por volta nao encontrada")
    return position


async def create_position(
    db: AsyncSession,
    race_id: uuid.UUID,
    driver_id: uuid.UUID,
    team_id: uuid.UUID,
    lap_number: int,
    position: int,
    gap_to_leader_ms: int | None = None,
    interval_ms: int | None = None,
) -> LapPosition:
    """
    Create a lap position. Validates FKs and uniqueness.
    Cria uma posicao por volta. Valida FKs e unicidade.
    """
    await _validate_race(db, race_id)
    await _validate_driver(db, driver_id)
    await _validate_team(db, team_id)

    # Check unique constraint / Verifica constraint de unicidade
    existing = await db.execute(
        select(LapPosition).where(
            LapPosition.race_id == race_id,
            LapPosition.driver_id == driver_id,
            LapPosition.lap_number == lap_number,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictException("Lap position already exists for this driver/race/lap number")

    lap_position = LapPosition(
        race_id=race_id,
        driver_id=driver_id,
        team_id=team_id,
        lap_number=lap_number,
        position=position,
        gap_to_leader_ms=gap_to_leader_ms,
        interval_ms=interval_ms,
    )
    db.add(lap_position)
    await db.commit()
    await db.refresh(lap_position)
    return lap_position


async def bulk_create_positions(
    db: AsyncSession,
    race_id: uuid.UUID,
    positions_data: list[dict[str, object]],
) -> list[LapPosition]:
    """
    Bulk create lap positions. Validates race FK.
    Cria posicoes por volta em massa. Valida FK da corrida.
    """
    await _validate_race(db, race_id)

    created: list[LapPosition] = []
    for data in positions_data:
        lap_position = LapPosition(
            race_id=race_id,
            driver_id=data["driver_id"],
            team_id=data["team_id"],
            lap_number=data["lap_number"],
            position=data["position"],
            gap_to_leader_ms=data.get("gap_to_leader_ms"),
            interval_ms=data.get("interval_ms"),
        )
        db.add(lap_position)
        created.append(lap_position)

    await db.commit()
    for pos in created:
        await db.refresh(pos)
    return created


async def update_position(
    db: AsyncSession,
    lap_position: LapPosition,
    position: int | None = None,
    gap_to_leader_ms: int | None = None,
    interval_ms: int | None = None,
) -> LapPosition:
    """
    Update a lap position. Only updates non-None fields.
    Atualiza uma posicao por volta. So atualiza campos nao-None.
    """
    if position is not None:
        lap_position.position = position
    if gap_to_leader_ms is not None:
        lap_position.gap_to_leader_ms = gap_to_leader_ms
    if interval_ms is not None:
        lap_position.interval_ms = interval_ms

    await db.commit()
    await db.refresh(lap_position)
    return lap_position


async def delete_position(db: AsyncSession, lap_position: LapPosition) -> None:
    """
    Delete a lap position.
    Exclui uma posicao por volta.
    """
    await db.delete(lap_position)
    await db.commit()


# --- RaceEvent services / Servicos de evento de corrida ---


async def list_events(
    db: AsyncSession,
    race_id: uuid.UUID,
    event_type: RaceEventType | None = None,
    driver_id: uuid.UUID | None = None,
    lap_number: int | None = None,
) -> list[RaceEvent]:
    """
    List race events for a race, optionally filtered.
    Lista eventos de corrida, opcionalmente filtrados.
    """
    await _validate_race(db, race_id)
    stmt = select(RaceEvent).where(RaceEvent.race_id == race_id).order_by(RaceEvent.lap_number)
    if event_type is not None:
        stmt = stmt.where(RaceEvent.event_type == event_type)
    if driver_id is not None:
        stmt = stmt.where(RaceEvent.driver_id == driver_id)
    if lap_number is not None:
        stmt = stmt.where(RaceEvent.lap_number == lap_number)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_event_by_id(db: AsyncSession, event_id: uuid.UUID) -> RaceEvent:
    """
    Get a race event by ID. Raises NotFoundException if not found.
    Busca um evento por ID. Lanca NotFoundException se nao encontrado.
    """
    result = await db.execute(select(RaceEvent).where(RaceEvent.id == event_id))
    event = result.scalar_one_or_none()
    if event is None:
        raise NotFoundException("Race event not found / Evento de corrida nao encontrado")
    return event


async def create_event(
    db: AsyncSession,
    race_id: uuid.UUID,
    lap_number: int,
    event_type: RaceEventType,
    description: str | None = None,
    driver_id: uuid.UUID | None = None,
) -> RaceEvent:
    """
    Create a race event. Validates FKs.
    Cria um evento de corrida. Valida FKs.
    """
    await _validate_race(db, race_id)
    if driver_id is not None:
        await _validate_driver(db, driver_id)

    event = RaceEvent(
        race_id=race_id,
        lap_number=lap_number,
        event_type=event_type,
        description=description,
        driver_id=driver_id,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def update_event(
    db: AsyncSession,
    event: RaceEvent,
    lap_number: int | None = None,
    event_type: RaceEventType | None = None,
    description: str | None = None,
    driver_id: uuid.UUID | None = None,
) -> RaceEvent:
    """
    Update a race event. Only updates non-None fields.
    Atualiza um evento de corrida. So atualiza campos nao-None.
    """
    if lap_number is not None:
        event.lap_number = lap_number
    if event_type is not None:
        event.event_type = event_type
    if description is not None:
        event.description = description
    if driver_id is not None:
        event.driver_id = driver_id

    await db.commit()
    await db.refresh(event)
    return event


async def delete_event(db: AsyncSession, event: RaceEvent) -> None:
    """
    Delete a race event.
    Exclui um evento de corrida.
    """
    await db.delete(event)
    await db.commit()


# --- Analysis services / Servicos de analise ---


async def get_full_replay(db: AsyncSession, race_id: uuid.UUID) -> dict[str, object]:
    """
    Get full race replay: positions + events + pit stops grouped by lap.
    Retorna replay completo: posicoes + eventos + pit stops agrupados por volta.
    """
    race = await _validate_race(db, race_id)

    # Fetch all data / Busca todos os dados
    pos_result = await db.execute(
        select(LapPosition).where(LapPosition.race_id == race_id).order_by(LapPosition.lap_number, LapPosition.position)
    )
    positions = list(pos_result.scalars().all())

    evt_result = await db.execute(select(RaceEvent).where(RaceEvent.race_id == race_id).order_by(RaceEvent.lap_number))
    events = list(evt_result.scalars().all())

    pit_result = await db.execute(select(PitStop).where(PitStop.race_id == race_id).order_by(PitStop.lap_number))
    pit_stops = list(pit_result.scalars().all())

    # Group by lap / Agrupar por volta
    laps_map: dict[int, dict[str, list[object]]] = defaultdict(lambda: {"positions": [], "events": [], "pit_stops": []})

    for pos in positions:
        laps_map[pos.lap_number]["positions"].append(
            {
                "driver_id": pos.driver_id,
                "driver_name": pos.driver.display_name if pos.driver else "",
                "team_id": pos.team_id,
                "position": pos.position,
                "gap_to_leader_ms": pos.gap_to_leader_ms,
                "interval_ms": pos.interval_ms,
            }
        )

    for evt in events:
        laps_map[evt.lap_number]["events"].append(
            {
                "event_type": evt.event_type,
                "description": evt.description,
                "driver_id": evt.driver_id,
                "driver_name": evt.driver.display_name if evt.driver else None,
            }
        )

    for pit in pit_stops:
        laps_map[pit.lap_number]["pit_stops"].append(
            {
                "driver_id": pit.driver_id,
                "driver_name": pit.driver.display_name if pit.driver else "",
                "duration_ms": pit.duration_ms,
                "tire_from": pit.tire_from.value if pit.tire_from else None,
                "tire_to": pit.tire_to.value if pit.tire_to else None,
            }
        )

    # Build sorted lap list / Constroi lista ordenada de voltas
    total_laps = race.laps_total or 0
    all_laps = sorted(laps_map.keys())
    laps_data = []
    for lap_num in all_laps:
        lap_data = laps_map[lap_num]
        laps_data.append(
            {
                "lap_number": lap_num,
                "positions": lap_data["positions"],
                "events": lap_data["events"],
                "pit_stops": lap_data["pit_stops"],
            }
        )

    return {
        "race_id": race_id,
        "total_laps": total_laps,
        "laps": laps_data,
    }


async def get_stint_analysis(db: AsyncSession, race_id: uuid.UUID) -> dict[str, object]:
    """
    Analyze stints: avg pace, best lap, degradation per tire stint.
    Analisa stints: ritmo medio, melhor volta, degradacao por stint de pneu.
    """
    race = await _validate_race(db, race_id)

    # Get pit stops to determine stint boundaries / Busca pit stops para definir limites de stint
    pit_result = await db.execute(
        select(PitStop).where(PitStop.race_id == race_id).order_by(PitStop.driver_id, PitStop.lap_number)
    )
    pit_stops = list(pit_result.scalars().all())

    # Get lap times / Busca tempos de volta
    lap_result = await db.execute(
        select(LapTime).where(LapTime.race_id == race_id).order_by(LapTime.driver_id, LapTime.lap_number)
    )
    lap_times = list(lap_result.scalars().all())

    # Group pit stops by driver / Agrupa pit stops por piloto
    driver_pits: dict[uuid.UUID, list[PitStop]] = defaultdict(list)
    for pit in pit_stops:
        driver_pits[pit.driver_id].append(pit)

    # Group lap times by driver / Agrupa tempos de volta por piloto
    driver_laps: dict[uuid.UUID, list[LapTime]] = defaultdict(list)
    for lap in lap_times:
        driver_laps[lap.driver_id].append(lap)

    # Get all drivers that have data / Busca todos os pilotos com dados
    all_driver_ids = set(driver_pits.keys()) | set(driver_laps.keys())

    # Driver name cache / Cache de nomes de pilotos
    driver_names: dict[uuid.UUID, str] = {}
    for lap in lap_times:
        if lap.driver_id not in driver_names and lap.driver:
            driver_names[lap.driver_id] = lap.driver.display_name
    for pit in pit_stops:
        if pit.driver_id not in driver_names and pit.driver:
            driver_names[pit.driver_id] = pit.driver.display_name

    drivers_data = []
    for d_id in sorted(all_driver_ids, key=str):
        pits = driver_pits.get(d_id, [])
        laps = driver_laps.get(d_id, [])
        d_name = driver_names.get(d_id, "Unknown")

        # Determine stint boundaries / Determina limites de stint
        stint_boundaries: list[tuple[int, int, str | None]] = []
        total_laps = race.laps_total or (max((lt.lap_number for lt in laps), default=0))

        if pits:
            # First stint: lap 1 to first pit
            tire_from = pits[0].tire_from
            start_compound = tire_from.value if tire_from else None
            stint_boundaries.append((1, pits[0].lap_number, start_compound))

            # Middle stints
            for i in range(len(pits) - 1):
                tire_to = pits[i].tire_to
                compound = tire_to.value if tire_to else None
                stint_boundaries.append((pits[i].lap_number + 1, pits[i + 1].lap_number, compound))

            # Last stint
            last_tire = pits[-1].tire_to
            last_compound = last_tire.value if last_tire else None
            stint_boundaries.append((pits[-1].lap_number + 1, total_laps, last_compound))
        elif laps:
            stint_boundaries.append((1, total_laps, None))

        # Calculate stint stats / Calcula estatisticas de stint
        stints_data = []
        for stint_num, (start_lap, end_lap, compound) in enumerate(stint_boundaries, 1):
            stint_laps = [lt for lt in laps if start_lap <= lt.lap_number <= end_lap and lt.is_valid]
            if not stint_laps:
                stints_data.append(
                    {
                        "driver_id": d_id,
                        "driver_name": d_name,
                        "stint_number": stint_num,
                        "compound": compound,
                        "start_lap": start_lap,
                        "end_lap": end_lap,
                        "total_laps": end_lap - start_lap + 1,
                        "avg_pace_ms": None,
                        "best_lap_ms": None,
                        "degradation_ms": None,
                    }
                )
                continue

            times = [lt.lap_time_ms for lt in stint_laps]
            avg_pace = int(sum(times) / len(times))
            best_lap = min(times)

            # Degradation: diff between last 3 laps avg and first 3 laps avg
            degradation = None
            if len(times) >= 4:
                first_avg = sum(times[:3]) / 3
                last_avg = sum(times[-3:]) / 3
                degradation = int(last_avg - first_avg)

            stints_data.append(
                {
                    "driver_id": d_id,
                    "driver_name": d_name,
                    "stint_number": stint_num,
                    "compound": compound,
                    "start_lap": start_lap,
                    "end_lap": end_lap,
                    "total_laps": end_lap - start_lap + 1,
                    "avg_pace_ms": avg_pace,
                    "best_lap_ms": best_lap,
                    "degradation_ms": degradation,
                }
            )

        drivers_data.append(
            {
                "driver_id": d_id,
                "driver_name": d_name,
                "stints": stints_data,
            }
        )

    return {
        "race_id": race_id,
        "drivers": drivers_data,
    }


async def get_overtakes(db: AsyncSession, race_id: uuid.UUID) -> dict[str, object]:
    """
    Detect overtakes from position changes between consecutive laps.
    Detecta ultrapassagens a partir de mudancas de posicao entre voltas consecutivas.
    """
    await _validate_race(db, race_id)

    pos_result = await db.execute(
        select(LapPosition)
        .where(LapPosition.race_id == race_id)
        .order_by(LapPosition.driver_id, LapPosition.lap_number)
    )
    positions = list(pos_result.scalars().all())

    # Group by driver / Agrupar por piloto
    driver_positions: dict[uuid.UUID, list[LapPosition]] = defaultdict(list)
    for pos in positions:
        driver_positions[pos.driver_id].append(pos)

    overtakes: list[dict[str, object]] = []
    for d_id, driver_pos_list in driver_positions.items():
        d_name = driver_pos_list[0].driver.display_name if driver_pos_list[0].driver else "Unknown"
        for i in range(1, len(driver_pos_list)):
            prev = driver_pos_list[i - 1]
            curr = driver_pos_list[i]
            # Position improved (lower number = better position)
            if curr.position < prev.position:
                overtakes.append(
                    {
                        "lap_number": curr.lap_number,
                        "driver_id": d_id,
                        "driver_name": d_name,
                        "from_position": prev.position,
                        "to_position": curr.position,
                        "positions_gained": prev.position - curr.position,
                    }
                )

    # Sort by lap number / Ordenar por numero de volta
    overtakes.sort(key=lambda x: (x["lap_number"], str(x["driver_id"])))

    return {
        "race_id": race_id,
        "total_overtakes": len(overtakes),
        "overtakes": overtakes,
    }


async def get_race_summary(db: AsyncSession, race_id: uuid.UUID) -> dict[str, object]:
    """
    Get race summary: leader changes, total overtakes, safety car laps, DNFs, fastest lap.
    Resumo da corrida: mudancas de lider, ultrapassagens, voltas de SC, DNFs, volta rapida.
    """
    race = await _validate_race(db, race_id)
    total_laps = race.laps_total or 0

    # Overtakes / Ultrapassagens
    overtakes_data = await get_overtakes(db, race_id)
    total_overtakes: int = overtakes_data["total_overtakes"]  # type: ignore[assignment]

    # Leader changes / Mudancas de lider
    pos_result = await db.execute(
        select(LapPosition)
        .where(LapPosition.race_id == race_id, LapPosition.position == 1)
        .order_by(LapPosition.lap_number)
    )
    leaders = list(pos_result.scalars().all())
    leader_changes = 0
    for i in range(1, len(leaders)):
        if leaders[i].driver_id != leaders[i - 1].driver_id:
            leader_changes += 1

    # Safety car laps / Voltas de safety car
    evt_result = await db.execute(
        select(RaceEvent).where(
            RaceEvent.race_id == race_id,
            RaceEvent.event_type.in_([RaceEventType.safety_car, RaceEventType.virtual_safety_car]),
        )
    )
    safety_car_events = list(evt_result.scalars().all())
    safety_car_laps = len({evt.lap_number for evt in safety_car_events})

    # DNF count / Contagem de DNFs
    dnf_result = await db.execute(select(RaceResult).where(RaceResult.race_id == race_id, RaceResult.dnf.is_(True)))
    dnf_count = len(list(dnf_result.scalars().all()))

    # Fastest lap / Volta mais rapida
    fastest_lap_data = None
    lap_result = await db.execute(
        select(LapTime)
        .where(LapTime.race_id == race_id, LapTime.is_valid.is_(True))
        .order_by(LapTime.lap_time_ms)
        .limit(1)
    )
    fastest = lap_result.scalar_one_or_none()
    if fastest:
        fastest_lap_data = {
            "driver_id": fastest.driver_id,
            "driver_name": fastest.driver.display_name if fastest.driver else "Unknown",
            "lap_number": fastest.lap_number,
            "lap_time_ms": fastest.lap_time_ms,
        }

    return {
        "race_id": race_id,
        "total_laps": total_laps,
        "total_overtakes": total_overtakes,
        "leader_changes": leader_changes,
        "safety_car_laps": safety_car_laps,
        "dnf_count": dnf_count,
        "fastest_lap": fastest_lap_data,
    }
