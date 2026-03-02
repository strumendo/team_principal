"""
Pit stop and race strategy API router.
Router da API de pit stop e estrategia de corrida.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.pitstops.schemas import (
    PitStopCreateRequest,
    PitStopDetailResponse,
    PitStopResponse,
    PitStopSummaryResponse,
    PitStopUpdateRequest,
    RaceStrategyCreateRequest,
    RaceStrategyDetailResponse,
    RaceStrategyResponse,
    RaceStrategyUpdateRequest,
)
from app.pitstops.service import (
    create_pit_stop,
    create_strategy,
    delete_pit_stop,
    delete_strategy,
    get_pit_stop_by_id,
    get_pit_stop_summary,
    get_strategy_by_id,
    list_pit_stops,
    list_strategies,
    update_pit_stop,
    update_strategy,
)
from app.users.models import User

router = APIRouter(tags=["pitstops"])


# --- Pit Stop endpoints / Endpoints de pit stop ---


@router.get("/api/v1/races/{race_id}/pitstops", response_model=list[PitStopResponse])
async def read_pit_stops(
    race_id: uuid.UUID,
    driver_id: uuid.UUID | None = Query(default=None, description="Filter by driver / Filtrar por piloto"),
    team_id: uuid.UUID | None = Query(default=None, description="Filter by team / Filtrar por equipe"),
    _current_user: User = Depends(require_permissions("pitstops:read")),
    db: AsyncSession = Depends(get_db),
) -> list[PitStopResponse]:
    """
    List pit stops for a race, optionally filtered.
    Lista pit stops de uma corrida, opcionalmente filtrados.
    """
    return await list_pit_stops(db, race_id, driver_id=driver_id, team_id=team_id)  # type: ignore[return-value]


@router.post("/api/v1/races/{race_id}/pitstops", response_model=PitStopResponse, status_code=201)
async def create_new_pit_stop(
    race_id: uuid.UUID,
    body: PitStopCreateRequest,
    _current_user: User = Depends(require_permissions("pitstops:create")),
    db: AsyncSession = Depends(get_db),
) -> PitStopResponse:
    """
    Create a pit stop.
    Cria um pit stop.
    """
    return await create_pit_stop(  # type: ignore[return-value]
        db,
        race_id=race_id,
        driver_id=body.driver_id,
        team_id=body.team_id,
        lap_number=body.lap_number,
        duration_ms=body.duration_ms,
        tire_from=body.tire_from,
        tire_to=body.tire_to,
        notes=body.notes,
    )


@router.get("/api/v1/races/{race_id}/pitstops/summary", response_model=PitStopSummaryResponse)
async def read_pit_stop_summary(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("pitstops:read")),
    db: AsyncSession = Depends(get_db),
) -> PitStopSummaryResponse:
    """
    Get pit stop summary for a race (total stops, avg duration, fastest per driver).
    Retorna resumo de pit stops (total de paradas, duracao media, mais rapida por piloto).
    """
    return await get_pit_stop_summary(db, race_id)  # type: ignore[return-value]


@router.get("/api/v1/pitstops/{pit_stop_id}", response_model=PitStopDetailResponse)
async def read_pit_stop(
    pit_stop_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("pitstops:read")),
    db: AsyncSession = Depends(get_db),
) -> PitStopDetailResponse:
    """
    Get a pit stop by ID (with driver and team).
    Busca um pit stop por ID (com piloto e equipe).
    """
    return await get_pit_stop_by_id(db, pit_stop_id)  # type: ignore[return-value]


@router.patch("/api/v1/pitstops/{pit_stop_id}", response_model=PitStopResponse)
async def update_existing_pit_stop(
    pit_stop_id: uuid.UUID,
    body: PitStopUpdateRequest,
    _current_user: User = Depends(require_permissions("pitstops:update")),
    db: AsyncSession = Depends(get_db),
) -> PitStopResponse:
    """
    Update a pit stop.
    Atualiza um pit stop.
    """
    pit_stop = await get_pit_stop_by_id(db, pit_stop_id)
    return await update_pit_stop(  # type: ignore[return-value]
        db,
        pit_stop,
        duration_ms=body.duration_ms,
        tire_from=body.tire_from,
        tire_to=body.tire_to,
        notes=body.notes,
    )


@router.delete("/api/v1/pitstops/{pit_stop_id}", status_code=204)
async def delete_existing_pit_stop(
    pit_stop_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("pitstops:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a pit stop.
    Exclui um pit stop.
    """
    pit_stop = await get_pit_stop_by_id(db, pit_stop_id)
    await delete_pit_stop(db, pit_stop)
    return Response(status_code=204)


# --- Race Strategy endpoints / Endpoints de estrategia de corrida ---


@router.get("/api/v1/races/{race_id}/strategies", response_model=list[RaceStrategyResponse])
async def read_strategies(
    race_id: uuid.UUID,
    driver_id: uuid.UUID | None = Query(default=None, description="Filter by driver / Filtrar por piloto"),
    team_id: uuid.UUID | None = Query(default=None, description="Filter by team / Filtrar por equipe"),
    _current_user: User = Depends(require_permissions("strategies:read")),
    db: AsyncSession = Depends(get_db),
) -> list[RaceStrategyResponse]:
    """
    List race strategies for a race, optionally filtered.
    Lista estrategias de corrida, opcionalmente filtradas.
    """
    return await list_strategies(db, race_id, driver_id=driver_id, team_id=team_id)  # type: ignore[return-value]


@router.post("/api/v1/races/{race_id}/strategies", response_model=RaceStrategyResponse, status_code=201)
async def create_new_strategy(
    race_id: uuid.UUID,
    body: RaceStrategyCreateRequest,
    _current_user: User = Depends(require_permissions("strategies:create")),
    db: AsyncSession = Depends(get_db),
) -> RaceStrategyResponse:
    """
    Create a race strategy.
    Cria uma estrategia de corrida.
    """
    return await create_strategy(  # type: ignore[return-value]
        db,
        race_id=race_id,
        driver_id=body.driver_id,
        team_id=body.team_id,
        name=body.name,
        description=body.description,
        target_stops=body.target_stops,
        planned_laps=body.planned_laps,
        starting_compound=body.starting_compound,
    )


@router.get("/api/v1/strategies/{strategy_id}", response_model=RaceStrategyDetailResponse)
async def read_strategy(
    strategy_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("strategies:read")),
    db: AsyncSession = Depends(get_db),
) -> RaceStrategyDetailResponse:
    """
    Get a race strategy by ID (with driver and team).
    Busca uma estrategia por ID (com piloto e equipe).
    """
    return await get_strategy_by_id(db, strategy_id)  # type: ignore[return-value]


@router.patch("/api/v1/strategies/{strategy_id}", response_model=RaceStrategyResponse)
async def update_existing_strategy(
    strategy_id: uuid.UUID,
    body: RaceStrategyUpdateRequest,
    _current_user: User = Depends(require_permissions("strategies:update")),
    db: AsyncSession = Depends(get_db),
) -> RaceStrategyResponse:
    """
    Update a race strategy.
    Atualiza uma estrategia de corrida.
    """
    strategy = await get_strategy_by_id(db, strategy_id)
    return await update_strategy(  # type: ignore[return-value]
        db,
        strategy,
        name=body.name,
        description=body.description,
        target_stops=body.target_stops,
        planned_laps=body.planned_laps,
        starting_compound=body.starting_compound,
        is_active=body.is_active,
    )


@router.delete("/api/v1/strategies/{strategy_id}", status_code=204)
async def delete_existing_strategy(
    strategy_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("strategies:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a race strategy.
    Exclui uma estrategia de corrida.
    """
    strategy = await get_strategy_by_id(db, strategy_id)
    await delete_strategy(db, strategy)
    return Response(status_code=204)
