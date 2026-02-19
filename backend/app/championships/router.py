"""
Championships API router.
Router da API de campeonatos.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import ChampionshipStatus
from app.championships.schemas import (
    ChampionshipCreateRequest,
    ChampionshipDetailResponse,
    ChampionshipEntryRequest,
    ChampionshipEntryResponse,
    ChampionshipListResponse,
    ChampionshipResponse,
    ChampionshipUpdateRequest,
)
from app.championships.service import (
    add_championship_entry,
    create_championship,
    delete_championship,
    get_championship_by_id,
    list_championship_entries,
    list_championships,
    remove_championship_entry,
    update_championship,
)
from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.users.models import User

router = APIRouter(prefix="/api/v1/championships", tags=["championships"])


@router.get("/", response_model=list[ChampionshipListResponse])
async def read_championships(
    status: ChampionshipStatus | None = Query(default=None, description="Filter by status / Filtrar por status"),
    season_year: int | None = Query(default=None, description="Filter by season year / Filtrar por ano da temporada"),
    is_active: bool | None = Query(default=None, description="Filter by active status / Filtrar por status ativo"),
    _current_user: User = Depends(require_permissions("championships:read")),
    db: AsyncSession = Depends(get_db),
) -> list[ChampionshipListResponse]:
    """
    List all championships, optionally filtered by status, season_year, and is_active.
    Lista todos os campeonatos, opcionalmente filtrados por status, season_year e is_active.
    """
    return await list_championships(db, status=status, season_year=season_year, is_active=is_active)  # type: ignore[return-value]


@router.get("/{championship_id}", response_model=ChampionshipDetailResponse)
async def read_championship(
    championship_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("championships:read")),
    db: AsyncSession = Depends(get_db),
) -> ChampionshipDetailResponse:
    """
    Get a championship by ID.
    Busca um campeonato por ID.
    """
    return await get_championship_by_id(db, championship_id)  # type: ignore[return-value]


@router.post("/", response_model=ChampionshipResponse, status_code=201)
async def create_new_championship(
    body: ChampionshipCreateRequest,
    _current_user: User = Depends(require_permissions("championships:create")),
    db: AsyncSession = Depends(get_db),
) -> ChampionshipResponse:
    """
    Create a new championship.
    Cria um novo campeonato.
    """
    return await create_championship(  # type: ignore[return-value]
        db,
        name=body.name,
        display_name=body.display_name,
        season_year=body.season_year,
        description=body.description,
        status=body.status,
        start_date=body.start_date,
        end_date=body.end_date,
    )


@router.patch("/{championship_id}", response_model=ChampionshipResponse)
async def update_existing_championship(
    championship_id: uuid.UUID,
    body: ChampionshipUpdateRequest,
    _current_user: User = Depends(require_permissions("championships:update")),
    db: AsyncSession = Depends(get_db),
) -> ChampionshipResponse:
    """
    Update a championship's fields.
    Atualiza campos de um campeonato.
    """
    championship = await get_championship_by_id(db, championship_id)
    return await update_championship(  # type: ignore[return-value]
        db,
        championship,
        display_name=body.display_name,
        description=body.description,
        season_year=body.season_year,
        status=body.status,
        start_date=body.start_date,
        end_date=body.end_date,
        is_active=body.is_active,
    )


@router.delete("/{championship_id}", status_code=204)
async def delete_existing_championship(
    championship_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("championships:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a championship.
    Exclui um campeonato.
    """
    championship = await get_championship_by_id(db, championship_id)
    await delete_championship(db, championship)
    return Response(status_code=204)


# --- Entry endpoints / Endpoints de inscricao ---


@router.get("/{championship_id}/entries", response_model=list[ChampionshipEntryResponse])
async def read_championship_entries(
    championship_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("championships:read")),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:  # type: ignore[type-arg]
    """
    List all entries of a championship.
    Lista todas as inscricoes de um campeonato.
    """
    return await list_championship_entries(db, championship_id)


@router.post("/{championship_id}/entries", response_model=list[ChampionshipEntryResponse])
async def add_entry(
    championship_id: uuid.UUID,
    body: ChampionshipEntryRequest,
    _current_user: User = Depends(require_permissions("championships:manage_entries")),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:  # type: ignore[type-arg]
    """
    Add a team to a championship.
    Adiciona uma equipe a um campeonato.
    """
    return await add_championship_entry(db, championship_id, body.team_id)


@router.delete("/{championship_id}/entries/{team_id}", response_model=list[ChampionshipEntryResponse])
async def remove_entry(
    championship_id: uuid.UUID,
    team_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("championships:manage_entries")),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:  # type: ignore[type-arg]
    """
    Remove a team from a championship.
    Remove uma equipe de um campeonato.
    """
    return await remove_championship_entry(db, championship_id, team_id)
