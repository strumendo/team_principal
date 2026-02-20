"""
Drivers API router.
Router da API de pilotos.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.drivers.schemas import (
    DriverCreateRequest,
    DriverDetailResponse,
    DriverListResponse,
    DriverResponse,
    DriverUpdateRequest,
)
from app.drivers.service import (
    create_driver,
    delete_driver,
    get_driver_by_id,
    list_drivers,
    update_driver,
)
from app.users.models import User

router = APIRouter(prefix="/api/v1/drivers", tags=["drivers"])


@router.get("/", response_model=list[DriverListResponse])
async def read_drivers(
    is_active: bool | None = Query(default=None, description="Filter by active status / Filtrar por status ativo"),
    team_id: uuid.UUID | None = Query(default=None, description="Filter by team / Filtrar por equipe"),
    _current_user: User = Depends(require_permissions("drivers:read")),
    db: AsyncSession = Depends(get_db),
) -> list[DriverListResponse]:
    """
    List all drivers, optionally filtered by active status and/or team.
    Lista todos os pilotos, opcionalmente filtrados por status ativo e/ou equipe.
    """
    return await list_drivers(db, is_active=is_active, team_id=team_id)  # type: ignore[return-value]


@router.get("/{driver_id}", response_model=DriverDetailResponse)
async def read_driver(
    driver_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("drivers:read")),
    db: AsyncSession = Depends(get_db),
) -> DriverDetailResponse:
    """
    Get a driver by ID (with team).
    Busca um piloto por ID (com equipe).
    """
    return await get_driver_by_id(db, driver_id)  # type: ignore[return-value]


@router.post("/", response_model=DriverResponse, status_code=201)
async def create_new_driver(
    body: DriverCreateRequest,
    _current_user: User = Depends(require_permissions("drivers:create")),
    db: AsyncSession = Depends(get_db),
) -> DriverResponse:
    """
    Create a new driver.
    Cria um novo piloto.
    """
    return await create_driver(  # type: ignore[return-value]
        db,
        name=body.name,
        display_name=body.display_name,
        abbreviation=body.abbreviation,
        number=body.number,
        team_id=body.team_id,
        nationality=body.nationality,
        date_of_birth=body.date_of_birth,
        photo_url=body.photo_url,
    )


@router.patch("/{driver_id}", response_model=DriverResponse)
async def update_existing_driver(
    driver_id: uuid.UUID,
    body: DriverUpdateRequest,
    _current_user: User = Depends(require_permissions("drivers:update")),
    db: AsyncSession = Depends(get_db),
) -> DriverResponse:
    """
    Update a driver's fields.
    Atualiza campos de um piloto.
    """
    driver = await get_driver_by_id(db, driver_id)
    return await update_driver(  # type: ignore[return-value]
        db,
        driver,
        display_name=body.display_name,
        abbreviation=body.abbreviation,
        number=body.number,
        nationality=body.nationality,
        date_of_birth=body.date_of_birth,
        photo_url=body.photo_url,
        is_active=body.is_active,
    )


@router.delete("/{driver_id}", status_code=204)
async def delete_existing_driver(
    driver_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("drivers:delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a driver.
    Exclui um piloto.
    """
    driver = await get_driver_by_id(db, driver_id)
    await delete_driver(db, driver)
    return Response(status_code=204)
