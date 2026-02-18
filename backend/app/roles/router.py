"""
Permissions and Roles API routers.
Routers da API de permissoes e papeis.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permissions
from app.db.session import get_db
from app.roles.schemas import (
    PermissionCreateRequest,
    PermissionResponse,
    RoleCreateRequest,
    RoleListResponse,
    RolePermissionRequest,
    RoleResponse,
    RoleUpdateRequest,
    UserRoleAssignRequest,
)
from app.roles.service import (
    assign_permission_to_role,
    assign_role_to_user,
    create_permission,
    create_role,
    delete_role,
    get_permission_by_id,
    get_role_by_id,
    list_permissions,
    list_roles,
    list_user_roles,
    revoke_permission_from_role,
    revoke_role_from_user,
    update_role,
)
from app.users.models import User

permissions_router = APIRouter(prefix="/api/v1/permissions", tags=["permissions"])
roles_router = APIRouter(prefix="/api/v1/roles", tags=["roles"])
user_roles_router = APIRouter(prefix="/api/v1/users", tags=["user-roles"])


# --- Permissions endpoints / Endpoints de permissoes ---


@permissions_router.get("/", response_model=list[PermissionResponse])
async def read_permissions(
    module: str | None = Query(default=None, description="Filter by module / Filtrar por modulo"),
    _current_user: User = Depends(require_permissions("permissions:read")),
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
    _current_user: User = Depends(require_permissions("permissions:read")),
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
    _current_user: User = Depends(require_permissions("permissions:create")),
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
    _current_user: User = Depends(require_permissions("roles:read")),
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
    _current_user: User = Depends(require_permissions("roles:read")),
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
    _current_user: User = Depends(require_permissions("roles:create")),
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
    _current_user: User = Depends(require_permissions("roles:update")),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """
    Update a role's display name or description.
    Atualiza o nome de exibicao ou descricao de um papel.
    """
    role = await get_role_by_id(db, role_id)
    return await update_role(  # type: ignore[return-value]
        db, role, display_name=body.display_name, description=body.description
    )


@roles_router.delete("/{role_id}", status_code=204)
async def delete_existing_role(
    role_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("roles:delete")),
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
    _current_user: User = Depends(require_permissions("permissions:assign")),
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
    _current_user: User = Depends(require_permissions("permissions:revoke")),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """
    Revoke a permission from a role.
    Revoga uma permissao de um papel.
    """
    return await revoke_permission_from_role(db, role_id, permission_id)  # type: ignore[return-value]


# --- User-role endpoints / Endpoints de usuario-papel ---


@user_roles_router.get("/{user_id}/roles", response_model=list[RoleListResponse])
async def read_user_roles(
    user_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("roles:read")),
    db: AsyncSession = Depends(get_db),
) -> list:
    """
    List all roles assigned to a user.
    Lista todos os papeis atribuidos a um usuario.
    """
    return await list_user_roles(db, user_id)


@user_roles_router.post("/{user_id}/roles", response_model=list[RoleListResponse])
async def assign_user_role(
    user_id: uuid.UUID,
    body: UserRoleAssignRequest,
    current_user: User = Depends(require_permissions("roles:assign")),
    db: AsyncSession = Depends(get_db),
) -> list:
    """
    Assign a role to a user.
    Atribui um papel a um usuario.
    """
    await assign_role_to_user(db, user_id, body.role_id, assigned_by=current_user.id)
    return await list_user_roles(db, user_id)


@user_roles_router.delete("/{user_id}/roles/{role_id}", response_model=list[RoleListResponse])
async def revoke_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("roles:revoke")),
    db: AsyncSession = Depends(get_db),
) -> list:
    """
    Revoke a role from a user.
    Revoga um papel de um usuario.
    """
    await revoke_role_from_user(db, user_id, role_id)
    return await list_user_roles(db, user_id)
