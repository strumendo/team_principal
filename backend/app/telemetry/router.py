"""
Telemetry API router: lap times, car setups, driver comparison.
Router da API de telemetria: tempos de volta, setups de carro, comparacao de pilotos.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.telemetry.schemas import (
    CarSetupCreateRequest,
    CarSetupDetailResponse,
    CarSetupResponse,
    CarSetupUpdateRequest,
    DriverComparison,
    LapTimeBulkCreateRequest,
    LapTimeCreateRequest,
    LapTimeResponse,
    LapTimeSummaryResponse,
)
from app.telemetry.service import (
    bulk_create_lap_times,
    compare_drivers,
    create_lap_time,
    create_setup,
    delete_lap_time,
    delete_setup,
    get_lap_summary,
    get_lap_time_by_id,
    get_setup_by_id,
    list_lap_times,
    list_setups,
    update_setup,
)
from app.users.models import User

router = APIRouter(tags=["telemetry"])


# --- Lap Time endpoints / Endpoints de tempo de volta ---


@router.get("/api/v1/races/{race_id}/laps", response_model=list[LapTimeResponse])
async def read_laps(
    race_id: uuid.UUID,
    driver_id: uuid.UUID | None = Query(default=None, description="Filter by driver / Filtrar por piloto"),
    team_id: uuid.UUID | None = Query(default=None, description="Filter by team / Filtrar por equipe"),
    _current_user: User = Depends(require_permissions("telemetry:read")),
    db: AsyncSession = Depends(get_db),
) -> list[LapTimeResponse]:
    """
    List lap times for a race, optionally filtered.
    Lista tempos de volta de uma corrida, opcionalmente filtrados.
    """
    return await list_lap_times(db, race_id, driver_id=driver_id, team_id=team_id)  # type: ignore[return-value]


@router.post("/api/v1/races/{race_id}/laps", response_model=LapTimeResponse, status_code=201)
async def create_single_lap(
    race_id: uuid.UUID,
    body: LapTimeCreateRequest,
    _current_user: User = Depends(require_permissions("telemetry:create")),
    db: AsyncSession = Depends(get_db),
) -> LapTimeResponse:
    """
    Create a single lap time.
    Cria um tempo de volta.
    """
    return await create_lap_time(  # type: ignore[return-value]
        db,
        race_id=race_id,
        driver_id=body.driver_id,
        team_id=body.team_id,
        lap_number=body.lap_number,
        lap_time_ms=body.lap_time_ms,
        sector_1_ms=body.sector_1_ms,
        sector_2_ms=body.sector_2_ms,
        sector_3_ms=body.sector_3_ms,
        is_valid=body.is_valid,
        is_personal_best=body.is_personal_best,
    )


@router.post("/api/v1/races/{race_id}/laps/bulk", response_model=list[LapTimeResponse], status_code=201)
async def create_bulk_laps(
    race_id: uuid.UUID,
    body: LapTimeBulkCreateRequest,
    _current_user: User = Depends(require_permissions("telemetry:create")),
    db: AsyncSession = Depends(get_db),
) -> list[LapTimeResponse]:
    """
    Bulk create lap times for a race.
    Cria tempos de volta em lote para uma corrida.
    """
    laps_data = [lap.model_dump() for lap in body.laps]
    return await bulk_create_lap_times(db, race_id, laps_data)  # type: ignore[return-value]


@router.get("/api/v1/races/{race_id}/laps/summary", response_model=LapTimeSummaryResponse)
async def read_lap_summary(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("telemetry:read")),
    db: AsyncSession = Depends(get_db),
) -> LapTimeSummaryResponse:
    """
    Get lap time summary for a race (fastest/avg per driver, overall fastest).
    Retorna resumo de tempos de volta (mais rapido/media por piloto, mais rapido geral).
    """
    return await get_lap_summary(db, race_id)  # type: ignore[return-value]


@router.delete("/api/v1/laps/{lap_id}", status_code=204)
async def delete_existing_lap(
    lap_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("telemetry:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a lap time.
    Exclui um tempo de volta.
    """
    lap = await get_lap_time_by_id(db, lap_id)
    await delete_lap_time(db, lap)
    return Response(status_code=204)


# --- Car Setup endpoints / Endpoints de setup de carro ---


@router.get("/api/v1/races/{race_id}/setups", response_model=list[CarSetupResponse])
async def read_setups(
    race_id: uuid.UUID,
    driver_id: uuid.UUID | None = Query(default=None, description="Filter by driver / Filtrar por piloto"),
    team_id: uuid.UUID | None = Query(default=None, description="Filter by team / Filtrar por equipe"),
    _current_user: User = Depends(require_permissions("telemetry:read")),
    db: AsyncSession = Depends(get_db),
) -> list[CarSetupResponse]:
    """
    List car setups for a race, optionally filtered.
    Lista setups de carro de uma corrida, opcionalmente filtrados.
    """
    return await list_setups(db, race_id, driver_id=driver_id, team_id=team_id)  # type: ignore[return-value]


@router.post("/api/v1/races/{race_id}/setups", response_model=CarSetupResponse, status_code=201)
async def create_new_setup(
    race_id: uuid.UUID,
    body: CarSetupCreateRequest,
    _current_user: User = Depends(require_permissions("telemetry:create")),
    db: AsyncSession = Depends(get_db),
) -> CarSetupResponse:
    """
    Create a car setup.
    Cria um setup de carro.
    """
    return await create_setup(  # type: ignore[return-value]
        db,
        race_id=race_id,
        driver_id=body.driver_id,
        team_id=body.team_id,
        name=body.name,
        notes=body.notes,
        front_wing=body.front_wing,
        rear_wing=body.rear_wing,
        differential=body.differential,
        brake_bias=body.brake_bias,
        tire_pressure_fl=body.tire_pressure_fl,
        tire_pressure_fr=body.tire_pressure_fr,
        tire_pressure_rl=body.tire_pressure_rl,
        tire_pressure_rr=body.tire_pressure_rr,
        suspension_stiffness=body.suspension_stiffness,
        anti_roll_bar=body.anti_roll_bar,
    )


@router.get("/api/v1/setups/{setup_id}", response_model=CarSetupDetailResponse)
async def read_setup(
    setup_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("telemetry:read")),
    db: AsyncSession = Depends(get_db),
) -> CarSetupDetailResponse:
    """
    Get a car setup by ID (with driver and team).
    Busca um setup por ID (com piloto e equipe).
    """
    return await get_setup_by_id(db, setup_id)  # type: ignore[return-value]


@router.patch("/api/v1/setups/{setup_id}", response_model=CarSetupResponse)
async def update_existing_setup(
    setup_id: uuid.UUID,
    body: CarSetupUpdateRequest,
    _current_user: User = Depends(require_permissions("telemetry:update")),
    db: AsyncSession = Depends(get_db),
) -> CarSetupResponse:
    """
    Update a car setup.
    Atualiza um setup de carro.
    """
    setup = await get_setup_by_id(db, setup_id)
    return await update_setup(  # type: ignore[return-value]
        db,
        setup,
        name=body.name,
        notes=body.notes,
        front_wing=body.front_wing,
        rear_wing=body.rear_wing,
        differential=body.differential,
        brake_bias=body.brake_bias,
        tire_pressure_fl=body.tire_pressure_fl,
        tire_pressure_fr=body.tire_pressure_fr,
        tire_pressure_rl=body.tire_pressure_rl,
        tire_pressure_rr=body.tire_pressure_rr,
        suspension_stiffness=body.suspension_stiffness,
        anti_roll_bar=body.anti_roll_bar,
        is_active=body.is_active,
    )


@router.delete("/api/v1/setups/{setup_id}", status_code=204)
async def delete_existing_setup(
    setup_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("telemetry:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a car setup.
    Exclui um setup de carro.
    """
    setup = await get_setup_by_id(db, setup_id)
    await delete_setup(db, setup)
    return Response(status_code=204)


# --- Compare endpoint / Endpoint de comparacao ---


@router.get("/api/v1/races/{race_id}/telemetry/compare", response_model=list[DriverComparison])
async def compare_race_drivers(
    race_id: uuid.UUID,
    driver_ids: str = Query(description="Comma-separated driver UUIDs (max 3) / UUIDs de pilotos separados por virgula"),
    _current_user: User = Depends(require_permissions("telemetry:read")),
    db: AsyncSession = Depends(get_db),
) -> list[DriverComparison]:
    """
    Compare lap times for up to 3 drivers in a race.
    Compara tempos de volta de ate 3 pilotos em uma corrida.
    """
    ids = [uuid.UUID(d.strip()) for d in driver_ids.split(",") if d.strip()]
    return await compare_drivers(db, race_id, ids)  # type: ignore[return-value]
