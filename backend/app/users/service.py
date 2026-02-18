"""
Users business logic.
Logica de negocios de usuarios.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.users.models import User


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
    """
    Get a user by ID. Raises NotFoundException if not found.
    Busca um usuario por ID. Lanca NotFoundException se nao encontrado.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("User not found")
    return user


async def update_user(
    db: AsyncSession, user: User, full_name: str | None = None, avatar_url: str | None = None
) -> User:
    """
    Update user profile fields.
    Atualiza campos do perfil do usuario.
    """
    if full_name is not None:
        user.full_name = full_name
    if avatar_url is not None:
        user.avatar_url = avatar_url
    await db.commit()
    await db.refresh(user)
    return user
