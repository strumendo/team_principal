"""
Teams API router.
Router da API de equipes.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.teams.schemas import (
    TeamCreateRequest,
    TeamListResponse,
    TeamResponse,
    TeamUpdateRequest,
)
from app.teams.service import (
    create_team,
    delete_team,
    get_team_by_id,
    list_teams,
    update_team,
)
from app.users.models import User

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])


@router.get("/", response_model=list[TeamListResponse])
async def read_teams(
    is_active: bool | None = Query(default=None, description="Filter by active status / Filtrar por status ativo"),
    _current_user: User = Depends(require_permissions("teams:read")),
    db: AsyncSession = Depends(get_db),
) -> list[TeamListResponse]:
    """
    List all teams, optionally filtered by active status.
    Lista todas as equipes, opcionalmente filtradas por status ativo.
    """
    return await list_teams(db, is_active=is_active)  # type: ignore[return-value]


@router.get("/{team_id}", response_model=TeamResponse)
async def read_team(
    team_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("teams:read")),
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """
    Get a team by ID.
    Busca uma equipe por ID.
    """
    return await get_team_by_id(db, team_id)  # type: ignore[return-value]


@router.post("/", response_model=TeamResponse, status_code=201)
async def create_new_team(
    body: TeamCreateRequest,
    _current_user: User = Depends(require_permissions("teams:create")),
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """
    Create a new team.
    Cria uma nova equipe.
    """
    return await create_team(  # type: ignore[return-value]
        db, name=body.name, display_name=body.display_name, description=body.description, logo_url=body.logo_url
    )


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_existing_team(
    team_id: uuid.UUID,
    body: TeamUpdateRequest,
    _current_user: User = Depends(require_permissions("teams:update")),
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """
    Update a team's fields.
    Atualiza campos de uma equipe.
    """
    team = await get_team_by_id(db, team_id)
    return await update_team(  # type: ignore[return-value]
        db, team, display_name=body.display_name, description=body.description,
        logo_url=body.logo_url, is_active=body.is_active
    )


@router.delete("/{team_id}", status_code=204)
async def delete_existing_team(
    team_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("teams:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a team.
    Exclui uma equipe.
    """
    team = await get_team_by_id(db, team_id)
    await delete_team(db, team)
    return Response(status_code=204)
