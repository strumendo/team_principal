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
    TeamAddMemberRequest,
    TeamCreateRequest,
    TeamDetailResponse,
    TeamListResponse,
    TeamMemberResponse,
    TeamResponse,
    TeamUpdateRequest,
)
from app.teams.service import (
    add_member,
    create_team,
    delete_team,
    get_team_by_id,
    list_team_members,
    list_teams,
    remove_member,
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


@router.get("/{team_id}", response_model=TeamDetailResponse)
async def read_team(
    team_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("teams:read")),
    db: AsyncSession = Depends(get_db),
) -> TeamDetailResponse:
    """
    Get a team by ID (with members).
    Busca uma equipe por ID (com membros).
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


# --- Membership endpoints / Endpoints de membros ---


@router.get("/{team_id}/members", response_model=list[TeamMemberResponse])
async def read_team_members(
    team_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("teams:read")),
    db: AsyncSession = Depends(get_db),
) -> list[TeamMemberResponse]:
    """
    List all members of a team.
    Lista todos os membros de uma equipe.
    """
    return await list_team_members(db, team_id)  # type: ignore[return-value]


@router.post("/{team_id}/members", response_model=list[TeamMemberResponse])
async def add_team_member(
    team_id: uuid.UUID,
    body: TeamAddMemberRequest,
    _current_user: User = Depends(require_permissions("teams:manage_members")),
    db: AsyncSession = Depends(get_db),
) -> list[TeamMemberResponse]:
    """
    Add a user to a team.
    Adiciona um usuario a uma equipe.
    """
    return await add_member(db, team_id, body.user_id)  # type: ignore[return-value]


@router.delete("/{team_id}/members/{user_id}", response_model=list[TeamMemberResponse])
async def remove_team_member(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("teams:manage_members")),
    db: AsyncSession = Depends(get_db),
) -> list[TeamMemberResponse]:
    """
    Remove a user from a team.
    Remove um usuario de uma equipe.
    """
    return await remove_member(db, team_id, user_id)  # type: ignore[return-value]
