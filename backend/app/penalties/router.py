"""
Penalties API router.
Router da API de penalidades.
"""

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.penalties.schemas import (
    PenaltyCreateRequest,
    PenaltyDetailResponse,
    PenaltyListResponse,
    PenaltyResponse,
    PenaltyUpdateRequest,
)
from app.penalties.service import (
    create_penalty,
    delete_penalty,
    get_penalty_by_id,
    list_penalties_by_race,
    update_penalty,
)
from app.users.models import User

router = APIRouter(tags=["penalties"])


@router.get("/api/v1/races/{race_id}/penalties", response_model=list[PenaltyListResponse])
async def read_race_penalties(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("penalties:read")),
    db: AsyncSession = Depends(get_db),
) -> list[PenaltyListResponse]:
    """
    List all penalties for a race.
    Lista todas as penalidades de uma corrida.
    """
    return await list_penalties_by_race(db, race_id)  # type: ignore[return-value]


@router.post("/api/v1/races/{race_id}/penalties", response_model=PenaltyResponse, status_code=201)
async def create_race_penalty(
    race_id: uuid.UUID,
    body: PenaltyCreateRequest,
    _current_user: User = Depends(require_permissions("penalties:create")),
    db: AsyncSession = Depends(get_db),
) -> PenaltyResponse:
    """
    Create a penalty for a race.
    Cria uma penalidade para uma corrida.
    """
    return await create_penalty(  # type: ignore[return-value]
        db,
        race_id=race_id,
        team_id=body.team_id,
        penalty_type=body.penalty_type,
        reason=body.reason,
        points_deducted=body.points_deducted,
        time_penalty_seconds=body.time_penalty_seconds,
        lap_number=body.lap_number,
        driver_id=body.driver_id,
        result_id=body.result_id,
    )


@router.get("/api/v1/penalties/{penalty_id}", response_model=PenaltyDetailResponse)
async def read_penalty(
    penalty_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("penalties:read")),
    db: AsyncSession = Depends(get_db),
) -> PenaltyDetailResponse:
    """
    Get a single penalty with detail info.
    Busca uma penalidade individual com info detalhada.
    """
    penalty = await get_penalty_by_id(db, penalty_id)
    team_dict = None
    driver_dict = None
    if penalty.team:
        team_dict = {
            "id": str(penalty.team.id),
            "name": penalty.team.name,
            "display_name": penalty.team.display_name,
        }
    if penalty.driver:
        driver_dict = {
            "id": str(penalty.driver.id),
            "name": penalty.driver.name,
            "display_name": penalty.driver.display_name,
            "abbreviation": penalty.driver.abbreviation,
        }
    return PenaltyDetailResponse(
        id=penalty.id,
        race_id=penalty.race_id,
        result_id=penalty.result_id,
        team_id=penalty.team_id,
        driver_id=penalty.driver_id,
        penalty_type=penalty.penalty_type,
        reason=penalty.reason,
        points_deducted=penalty.points_deducted,
        time_penalty_seconds=penalty.time_penalty_seconds,
        lap_number=penalty.lap_number,
        is_active=penalty.is_active,
        created_at=penalty.created_at,
        updated_at=penalty.updated_at,
        team=team_dict,
        driver=driver_dict,
    )


@router.patch("/api/v1/penalties/{penalty_id}", response_model=PenaltyResponse)
async def update_existing_penalty(
    penalty_id: uuid.UUID,
    body: PenaltyUpdateRequest,
    _current_user: User = Depends(require_permissions("penalties:update")),
    db: AsyncSession = Depends(get_db),
) -> PenaltyResponse:
    """
    Update a penalty.
    Atualiza uma penalidade.
    """
    penalty = await get_penalty_by_id(db, penalty_id)
    return await update_penalty(  # type: ignore[return-value]
        db,
        penalty,
        penalty_type=body.penalty_type,
        reason=body.reason,
        points_deducted=body.points_deducted,
        time_penalty_seconds=body.time_penalty_seconds,
        lap_number=body.lap_number,
        result_id=body.result_id,
        driver_id=body.driver_id,
        is_active=body.is_active,
    )


@router.delete("/api/v1/penalties/{penalty_id}", status_code=204)
async def delete_existing_penalty(
    penalty_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("penalties:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a penalty.
    Exclui uma penalidade.
    """
    penalty = await get_penalty_by_id(db, penalty_id)
    await delete_penalty(db, penalty)
    return Response(status_code=204)
