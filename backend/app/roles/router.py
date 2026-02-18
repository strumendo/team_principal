"""
Permissions API router.
Router da API de permissoes.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.roles.schemas import PermissionCreateRequest, PermissionResponse
from app.roles.service import create_permission, get_permission_by_id, list_permissions
from app.users.models import User

permissions_router = APIRouter(prefix="/api/v1/permissions", tags=["permissions"])


@permissions_router.get("/", response_model=list[PermissionResponse])
async def read_permissions(
    module: str | None = Query(default=None, description="Filter by module / Filtrar por modulo"),
    _current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    """
    List all permissions, optionally filtered by module.
    Lista todas as permissoes, opcionalmente filtradas por modulo.
    """
    return await list_permissions(db, module=module)


@permissions_router.get("/{permission_id}", response_model=PermissionResponse)
async def read_permission(
    permission_id: uuid.UUID,
    _current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PermissionResponse:
    """
    Get a permission by ID.
    Busca uma permissao por ID.
    """
    return await get_permission_by_id(db, permission_id)  # type: ignore[return-value]


@permissions_router.post("/", response_model=PermissionResponse, status_code=201)
async def create_new_permission(
    body: PermissionCreateRequest,
    _current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PermissionResponse:
    """
    Create a new permission.
    Cria uma nova permissao.
    """
    return await create_permission(db, codename=body.codename, module=body.module, description=body.description)  # type: ignore[return-value]
