"""
Race replay API router.
Router da API de replay de corrida.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.replay.models import RaceEventType
from app.replay.schemas import (
    FullReplayResponse,
    LapPositionBulkCreateRequest,
    LapPositionCreateRequest,
    LapPositionDetailResponse,
    LapPositionResponse,
    LapPositionUpdateRequest,
    OvertakesResponse,
    RaceEventCreateRequest,
    RaceEventDetailResponse,
    RaceEventResponse,
    RaceEventUpdateRequest,
    RaceSummaryResponse,
    StintAnalysisResponse,
)
from app.replay.service import (
    bulk_create_positions,
    create_event,
    create_position,
    delete_event,
    delete_position,
    get_event_by_id,
    get_full_replay,
    get_overtakes,
    get_position_by_id,
    get_race_summary,
    get_stint_analysis,
    list_events,
    list_positions,
    update_event,
    update_position,
)
from app.users.models import User

router = APIRouter(tags=["replay"])


# --- LapPosition endpoints / Endpoints de posicao por volta ---


@router.get("/api/v1/races/{race_id}/positions", response_model=list[LapPositionResponse])
async def read_positions(
    race_id: uuid.UUID,
    driver_id: uuid.UUID | None = Query(default=None, description="Filter by driver / Filtrar por piloto"),
    team_id: uuid.UUID | None = Query(default=None, description="Filter by team / Filtrar por equipe"),
    lap_number: int | None = Query(default=None, description="Filter by lap / Filtrar por volta"),
    _current_user: User = Depends(require_permissions("replay:read")),
    db: AsyncSession = Depends(get_db),
) -> list[LapPositionResponse]:
    """
    List lap positions for a race, optionally filtered.
    Lista posicoes por volta de uma corrida, opcionalmente filtradas.
    """
    return await list_positions(db, race_id, driver_id=driver_id, team_id=team_id, lap_number=lap_number)  # type: ignore[return-value]


@router.post("/api/v1/races/{race_id}/positions", response_model=LapPositionResponse, status_code=201)
async def create_new_position(
    race_id: uuid.UUID,
    body: LapPositionCreateRequest,
    _current_user: User = Depends(require_permissions("replay:create")),
    db: AsyncSession = Depends(get_db),
) -> LapPositionResponse:
    """
    Create a lap position.
    Cria uma posicao por volta.
    """
    return await create_position(  # type: ignore[return-value]
        db,
        race_id=race_id,
        driver_id=body.driver_id,
        team_id=body.team_id,
        lap_number=body.lap_number,
        position=body.position,
        gap_to_leader_ms=body.gap_to_leader_ms,
        interval_ms=body.interval_ms,
    )


@router.post("/api/v1/races/{race_id}/positions/bulk", response_model=list[LapPositionResponse], status_code=201)
async def bulk_create_new_positions(
    race_id: uuid.UUID,
    body: LapPositionBulkCreateRequest,
    _current_user: User = Depends(require_permissions("replay:create")),
    db: AsyncSession = Depends(get_db),
) -> list[LapPositionResponse]:
    """
    Bulk create lap positions.
    Cria posicoes por volta em massa.
    """
    positions_data: list[dict[str, object]] = [
        {
            "driver_id": p.driver_id,
            "team_id": p.team_id,
            "lap_number": p.lap_number,
            "position": p.position,
            "gap_to_leader_ms": p.gap_to_leader_ms,
            "interval_ms": p.interval_ms,
        }
        for p in body.positions
    ]
    return await bulk_create_positions(db, race_id, positions_data)  # type: ignore[return-value]


@router.get("/api/v1/positions/{position_id}", response_model=LapPositionDetailResponse)
async def read_position(
    position_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("replay:read")),
    db: AsyncSession = Depends(get_db),
) -> LapPositionDetailResponse:
    """
    Get a lap position by ID (with driver and team).
    Busca uma posicao por ID (com piloto e equipe).
    """
    return await get_position_by_id(db, position_id)  # type: ignore[return-value]


@router.patch("/api/v1/positions/{position_id}", response_model=LapPositionResponse)
async def update_existing_position(
    position_id: uuid.UUID,
    body: LapPositionUpdateRequest,
    _current_user: User = Depends(require_permissions("replay:update")),
    db: AsyncSession = Depends(get_db),
) -> LapPositionResponse:
    """
    Update a lap position.
    Atualiza uma posicao por volta.
    """
    lap_position = await get_position_by_id(db, position_id)
    return await update_position(  # type: ignore[return-value]
        db,
        lap_position,
        position=body.position,
        gap_to_leader_ms=body.gap_to_leader_ms,
        interval_ms=body.interval_ms,
    )


@router.delete("/api/v1/positions/{position_id}", status_code=204)
async def delete_existing_position(
    position_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("replay:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a lap position.
    Exclui uma posicao por volta.
    """
    lap_position = await get_position_by_id(db, position_id)
    await delete_position(db, lap_position)
    return Response(status_code=204)


# --- RaceEvent endpoints / Endpoints de evento de corrida ---


@router.get("/api/v1/races/{race_id}/events", response_model=list[RaceEventResponse])
async def read_events(
    race_id: uuid.UUID,
    event_type: RaceEventType | None = Query(default=None, description="Filter by event type / Filtrar por tipo"),
    driver_id: uuid.UUID | None = Query(default=None, description="Filter by driver / Filtrar por piloto"),
    lap_number: int | None = Query(default=None, description="Filter by lap / Filtrar por volta"),
    _current_user: User = Depends(require_permissions("replay:read")),
    db: AsyncSession = Depends(get_db),
) -> list[RaceEventResponse]:
    """
    List race events for a race, optionally filtered.
    Lista eventos de corrida, opcionalmente filtrados.
    """
    return await list_events(db, race_id, event_type=event_type, driver_id=driver_id, lap_number=lap_number)  # type: ignore[return-value]


@router.post("/api/v1/races/{race_id}/events", response_model=RaceEventResponse, status_code=201)
async def create_new_event(
    race_id: uuid.UUID,
    body: RaceEventCreateRequest,
    _current_user: User = Depends(require_permissions("replay:create")),
    db: AsyncSession = Depends(get_db),
) -> RaceEventResponse:
    """
    Create a race event.
    Cria um evento de corrida.
    """
    return await create_event(  # type: ignore[return-value]
        db,
        race_id=race_id,
        lap_number=body.lap_number,
        event_type=body.event_type,
        description=body.description,
        driver_id=body.driver_id,
    )


@router.get("/api/v1/events/{event_id}", response_model=RaceEventDetailResponse)
async def read_event(
    event_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("replay:read")),
    db: AsyncSession = Depends(get_db),
) -> RaceEventDetailResponse:
    """
    Get a race event by ID (with optional driver).
    Busca um evento por ID (com piloto opcional).
    """
    return await get_event_by_id(db, event_id)  # type: ignore[return-value]


@router.patch("/api/v1/events/{event_id}", response_model=RaceEventResponse)
async def update_existing_event(
    event_id: uuid.UUID,
    body: RaceEventUpdateRequest,
    _current_user: User = Depends(require_permissions("replay:update")),
    db: AsyncSession = Depends(get_db),
) -> RaceEventResponse:
    """
    Update a race event.
    Atualiza um evento de corrida.
    """
    event = await get_event_by_id(db, event_id)
    return await update_event(  # type: ignore[return-value]
        db,
        event,
        lap_number=body.lap_number,
        event_type=body.event_type,
        description=body.description,
        driver_id=body.driver_id,
    )


@router.delete("/api/v1/events/{event_id}", status_code=204)
async def delete_existing_event(
    event_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("replay:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a race event.
    Exclui um evento de corrida.
    """
    event = await get_event_by_id(db, event_id)
    await delete_event(db, event)
    return Response(status_code=204)


# --- Analysis endpoints / Endpoints de analise ---


@router.get("/api/v1/races/{race_id}/replay", response_model=FullReplayResponse)
async def read_full_replay(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("replay:read")),
    db: AsyncSession = Depends(get_db),
) -> FullReplayResponse:
    """
    Get full race replay: positions + events + pit stops grouped by lap.
    Retorna replay completo da corrida: posicoes + eventos + pit stops agrupados por volta.
    """
    return await get_full_replay(db, race_id)  # type: ignore[return-value]


@router.get("/api/v1/races/{race_id}/analysis/stints", response_model=StintAnalysisResponse)
async def read_stint_analysis(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("replay:read")),
    db: AsyncSession = Depends(get_db),
) -> StintAnalysisResponse:
    """
    Get stint analysis: avg pace, best lap, degradation per tire stint.
    Retorna analise de stints: ritmo medio, melhor volta, degradacao por stint de pneu.
    """
    return await get_stint_analysis(db, race_id)  # type: ignore[return-value]


@router.get("/api/v1/races/{race_id}/analysis/overtakes", response_model=OvertakesResponse)
async def read_overtakes(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("replay:read")),
    db: AsyncSession = Depends(get_db),
) -> OvertakesResponse:
    """
    Detect overtakes from position changes between consecutive laps.
    Detecta ultrapassagens a partir de mudancas de posicao entre voltas consecutivas.
    """
    return await get_overtakes(db, race_id)  # type: ignore[return-value]


@router.get("/api/v1/races/{race_id}/analysis/summary", response_model=RaceSummaryResponse)
async def read_race_summary(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("replay:read")),
    db: AsyncSession = Depends(get_db),
) -> RaceSummaryResponse:
    """
    Get race summary: leader changes, total overtakes, safety car laps, DNFs, fastest lap.
    Resumo da corrida: mudancas de lider, ultrapassagens, voltas de SC, DNFs, volta rapida.
    """
    return await get_race_summary(db, race_id)  # type: ignore[return-value]
