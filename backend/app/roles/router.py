"""
Permissions and Roles API routers.
Routers da API de permissoes e papeis.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.roles.schemas import (
    PermissionCreateRequest,
    PermissionResponse,
    RoleCreateRequest,
    RoleListResponse,
    RolePermissionRequest,
    RoleResponse,
    RoleUpdateRequest,
)
from app.roles.service import (
    assign_permission_to_role,
    create_permission,
    create_role,
    delete_role,
    get_permission_by_id,
    get_role_by_id,
    list_permissions,
    list_roles,
    revoke_permission_from_role,
    update_role,
)
from app.users.models import User

permissions_router = APIRouter(prefix="/api/v1/permissions", tags=["permissions"])
roles_router = APIRouter(prefix="/api/v1/roles", tags=["roles"])


# --- Permissions endpoints / Endpoints de permissoes ---


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
    return await create_permission(  # type: ignore[return-value]
        db, codename=body.codename, module=body.module, description=body.description
    )


# --- Roles endpoints / Endpoints de papeis ---


@roles_router.get("/", response_model=list[RoleListResponse])
async def read_roles(
    _current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    """
    List all roles (without permissions).
    Lista todos os papeis (sem permissoes).
    """
    return await list_roles(db)


@roles_router.get("/{role_id}", response_model=RoleResponse)
async def read_role(
    role_id: uuid.UUID,
    _current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """
    Get a role by ID (with permissions).
    Busca um papel por ID (com permissoes).
    """
    return await get_role_by_id(db, role_id)  # type: ignore[return-value]


@roles_router.post("/", response_model=RoleResponse, status_code=201)
async def create_new_role(
    body: RoleCreateRequest,
    _current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """
    Create a new role.
    Cria um novo papel.
    """
    return await create_role(  # type: ignore[return-value]
        db, name=body.name, display_name=body.display_name, description=body.description
    )


@roles_router.patch("/{role_id}", response_model=RoleResponse)
async def update_existing_role(
    role_id: uuid.UUID,
    body: RoleUpdateRequest,
    _current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """
    Update a role's display name or description.
    Atualiza o nome de exibicao ou descricao de um papel.
    """
    role = await get_role_by_id(db, role_id)
    return await update_role(db, role, display_name=body.display_name, description=body.description)  # type: ignore[return-value]


@roles_router.delete("/{role_id}", status_code=204)
async def delete_existing_role(
    role_id: uuid.UUID,
    _current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete a non-system role.
    Exclui um papel que nao e do sistema.
    """
    role = await get_role_by_id(db, role_id)
    await delete_role(db, role)
    return Response(status_code=204)


@roles_router.post("/{role_id}/permissions", response_model=RoleResponse)
async def assign_permission(
    role_id: uuid.UUID,
    body: RolePermissionRequest,
    _current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """
    Assign a permission to a role.
    Atribui uma permissao a um papel.
    """
    return await assign_permission_to_role(db, role_id, body.permission_id)  # type: ignore[return-value]


@roles_router.delete("/{role_id}/permissions/{permission_id}", response_model=RoleResponse)
async def revoke_permission(
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
    _current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """
    Revoke a permission from a role.
    Revoga uma permissao de um papel.
    """
    return await revoke_permission_from_role(db, role_id, permission_id)  # type: ignore[return-value]
