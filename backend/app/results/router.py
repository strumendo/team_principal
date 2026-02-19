"""
Race results API router.
Router da API de resultados de corrida.
"""

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.results.schemas import (
    ChampionshipStandingResponse,
    RaceResultCreateRequest,
    RaceResultDetailResponse,
    RaceResultListResponse,
    RaceResultResponse,
    RaceResultUpdateRequest,
)
from app.results.service import (
    create_result,
    delete_result,
    get_championship_standings,
    get_result_by_id,
    list_race_results,
    update_result,
)
from app.users.models import User

router = APIRouter(tags=["results"])


@router.get("/api/v1/races/{race_id}/results", response_model=list[RaceResultListResponse])
async def read_race_results(
    race_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("results:read")),
    db: AsyncSession = Depends(get_db),
) -> list[RaceResultListResponse]:
    """
    List all results for a race, ordered by position.
    Lista todos os resultados de uma corrida, ordenados por posicao.
    """
    return await list_race_results(db, race_id)  # type: ignore[return-value]


@router.post("/api/v1/races/{race_id}/results", response_model=RaceResultResponse, status_code=201)
async def create_new_result(
    race_id: uuid.UUID,
    body: RaceResultCreateRequest,
    _current_user: User = Depends(require_permissions("results:create")),
    db: AsyncSession = Depends(get_db),
) -> RaceResultResponse:
    """
    Create a new race result.
    Cria um novo resultado de corrida.
    """
    return await create_result(  # type: ignore[return-value]
        db,
        race_id=race_id,
        team_id=body.team_id,
        position=body.position,
        points=body.points,
        laps_completed=body.laps_completed,
        fastest_lap=body.fastest_lap,
        dnf=body.dnf,
        dsq=body.dsq,
        notes=body.notes,
    )


@router.get("/api/v1/results/{result_id}", response_model=RaceResultDetailResponse)
async def read_result(
    result_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("results:read")),
    db: AsyncSession = Depends(get_db),
) -> RaceResultDetailResponse:
    """
    Get a race result by ID.
    Busca um resultado de corrida por ID.
    """
    return await get_result_by_id(db, result_id)  # type: ignore[return-value]


@router.patch("/api/v1/results/{result_id}", response_model=RaceResultResponse)
async def update_existing_result(
    result_id: uuid.UUID,
    body: RaceResultUpdateRequest,
    _current_user: User = Depends(require_permissions("results:update")),
    db: AsyncSession = Depends(get_db),
) -> RaceResultResponse:
    """
    Update a race result's fields.
    Atualiza campos de um resultado de corrida.
    """
    race_result = await get_result_by_id(db, result_id)
    return await update_result(  # type: ignore[return-value]
        db,
        race_result,
        position=body.position,
        points=body.points,
        laps_completed=body.laps_completed,
        fastest_lap=body.fastest_lap,
        dnf=body.dnf,
        dsq=body.dsq,
        notes=body.notes,
    )


@router.get("/api/v1/championships/{championship_id}/standings", response_model=list[ChampionshipStandingResponse])
async def read_championship_standings(
    championship_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("results:read")),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:  # type: ignore[type-arg]
    """
    Get championship standings aggregated from race results.
    Obtem classificacao do campeonato agregada dos resultados de corrida.
    """
    return await get_championship_standings(db, championship_id)


@router.delete("/api/v1/results/{result_id}", status_code=204)
async def delete_existing_result(
    result_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("results:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a race result.
    Exclui um resultado de corrida.
    """
    race_result = await get_result_by_id(db, result_id)
    await delete_result(db, race_result)
    return Response(status_code=204)
