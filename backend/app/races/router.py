"""
Races API router.
Router da API de corridas.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.races.models import RaceStatus
from app.races.schemas import (
    RaceCreateRequest,
    RaceDetailResponse,
    RaceEntryRequest,
    RaceEntryResponse,
    RaceListResponse,
    RaceResponse,
    RaceUpdateRequest,
)
from app.races.service import (
    add_race_entry,
    create_race,
    delete_race,
    get_race_by_id,
    list_race_entries,
    list_races,
    remove_race_entry,
    update_race,
)
from app.users.models import User

router = APIRouter(tags=["races"])


@router.get("/api/v1/championships/{championship_id}/races", response_model=list[RaceListResponse])
async def read_races(
    championship_id: uuid.UUID,
    status: RaceStatus | None = Query(default=None, description="Filter by status / Filtrar por status"),
    is_active: bool | None = Query(default=None, description="Filter by active status / Filtrar por status ativo"),
    _current_user: User = Depends(require_permissions("races:read")),
    db: AsyncSession = Depends(get_db),
) -> list[RaceListResponse]:
    """
    List all races of a championship, optionally filtered by status and is_active.
    Lista todas as corridas de um campeonato, opcionalmente filtradas por status e is_active.
    """
    return await list_races(db, championship_id, status=status, is_active=is_active)  # type: ignore[return-value]


@router.post("/api/v1/championships/{championship_id}/races", response_model=RaceResponse, status_code=201)
async def create_new_race(
    championship_id: uuid.UUID,
    body: RaceCreateRequest,
    _current_user: User = Depends(require_permissions("races:create")),
    db: AsyncSession = Depends(get_db),
) -> RaceResponse:
    """
    Create a new race within a championship.
    Cria uma nova corrida dentro de um campeonato.
    """
    return await create_race(  # type: ignore[return-value]
        db,
        championship_id=championship_id,
        name=body.name,
        display_name=body.display_name,
        round_number=body.round_number,
        description=body.description,
        status=body.status,
        scheduled_at=body.scheduled_at,
        track_name=body.track_name,
        track_country=body.track_country,
        laps_total=body.laps_total,
    )


@router.get("/api/v1/races/{race_id}", response_model=RaceDetailResponse)
async def read_race(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("races:read")),
    db: AsyncSession = Depends(get_db),
) -> RaceDetailResponse:
    """
    Get a race by ID.
    Busca uma corrida por ID.
    """
    return await get_race_by_id(db, race_id)  # type: ignore[return-value]


@router.patch("/api/v1/races/{race_id}", response_model=RaceResponse)
async def update_existing_race(
    race_id: uuid.UUID,
    body: RaceUpdateRequest,
    _current_user: User = Depends(require_permissions("races:update")),
    db: AsyncSession = Depends(get_db),
) -> RaceResponse:
    """
    Update a race's fields.
    Atualiza campos de uma corrida.
    """
    race = await get_race_by_id(db, race_id)
    return await update_race(  # type: ignore[return-value]
        db,
        race,
        display_name=body.display_name,
        description=body.description,
        round_number=body.round_number,
        status=body.status,
        scheduled_at=body.scheduled_at,
        track_name=body.track_name,
        track_country=body.track_country,
        laps_total=body.laps_total,
        is_active=body.is_active,
    )


@router.delete("/api/v1/races/{race_id}", status_code=204)
async def delete_existing_race(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("races:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a race.
    Exclui uma corrida.
    """
    race = await get_race_by_id(db, race_id)
    await delete_race(db, race)
    return Response(status_code=204)


# --- Entry endpoints / Endpoints de inscricao ---


@router.get("/api/v1/races/{race_id}/entries", response_model=list[RaceEntryResponse])
async def read_race_entries(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("races:read")),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:  # type: ignore[type-arg]
    """
    List all entries of a race.
    Lista todas as inscricoes de uma corrida.
    """
    return await list_race_entries(db, race_id)


@router.post("/api/v1/races/{race_id}/entries", response_model=list[RaceEntryResponse])
async def add_entry(
    race_id: uuid.UUID,
    body: RaceEntryRequest,
    _current_user: User = Depends(require_permissions("races:manage_entries")),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:  # type: ignore[type-arg]
    """
    Add a team to a race. Team must be enrolled in the race's championship.
    Adiciona uma equipe a uma corrida. Equipe deve estar inscrita no campeonato da corrida.
    """
    return await add_race_entry(db, race_id, body.team_id)


@router.delete("/api/v1/races/{race_id}/entries/{team_id}", response_model=list[RaceEntryResponse])
async def remove_entry(
    race_id: uuid.UUID,
    team_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("races:manage_entries")),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:  # type: ignore[type-arg]
    """
    Remove a team from a race.
    Remove uma equipe de uma corrida.
    """
    return await remove_race_entry(db, race_id, team_id)
