"""
Users API router.
Router da API de usuarios.
"""

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, require_permissions
from app.db.session import get_db
from app.users.models import User
from app.users.schemas import AdminUserCreateRequest, AdminUserUpdate, UserListResponse, UserResponse, UserUpdate
from app.users.service import admin_create_user, admin_update_user, get_user_by_id, list_users, update_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current authenticated user's profile.
    Retorna o perfil do usuario autenticado atual.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    body: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Update the current authenticated user's profile.
    Atualiza o perfil do usuario autenticado atual.
    """
    return await update_user(db, current_user, full_name=body.full_name, avatar_url=body.avatar_url)


@router.get("/", response_model=list[UserListResponse])
async def list_all_users(
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
    _current_user: User = Depends(require_permissions("users:list")),
    db: AsyncSession = Depends(get_db),
) -> Sequence[User]:
    """
    List all users (requires users:list permission).
    Lista todos os usuarios (requer permissao users:list).
    """
    return await list_users(db, is_active=is_active, search=search)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    body: AdminUserCreateRequest,
    _current_user: User = Depends(require_permissions("users:create")),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Create a new user (requires users:create permission).
    Cria um novo usuario (requer permissao users:create).
    """
    return await admin_create_user(
        db,
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        is_active=body.is_active,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: uuid.UUID,
    _current_user: User = Depends(require_permissions("users:read")),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get a user by ID (requires users:read permission).
    Busca um usuario por ID (requer permissao users:read).
    """
    return await get_user_by_id(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def admin_update(
    user_id: uuid.UUID,
    body: AdminUserUpdate,
    _current_user: User = Depends(require_permissions("users:update")),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Admin update a user (requires users:update permission).
    Atualizacao de usuario pelo admin (requer permissao users:update).
    """
    user = await get_user_by_id(db, user_id)
    return await admin_update_user(db, user, full_name=body.full_name, email=body.email, is_active=body.is_active)
