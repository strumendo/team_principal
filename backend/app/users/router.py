"""
Users API router.
Router da API de usuarios.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, require_permissions
from app.db.session import get_db
from app.users.models import User
from app.users.schemas import UserResponse, UserUpdate
from app.users.service import get_user_by_id, update_user

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
