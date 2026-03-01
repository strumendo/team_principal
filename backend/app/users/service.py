"""
Users business logic.
Logica de negocios de usuarios.
"""

import uuid
from collections.abc import Sequence

from pydantic import EmailStr
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.security import hash_password
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


async def list_users(
    db: AsyncSession,
    is_active: bool | None = None,
    search: str | None = None,
) -> Sequence[User]:
    """
    List users ordered by created_at desc. Filter by is_active and search by name/email.
    Lista usuarios ordenados por created_at desc. Filtra por is_active e busca por nome/email.
    """
    stmt = select(User).order_by(User.created_at.desc())
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                User.full_name.ilike(pattern),
                User.email.ilike(pattern),
            )
        )
    result = await db.execute(stmt)
    return result.scalars().all()


async def admin_create_user(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: str,
    is_active: bool = True,
) -> User:
    """
    Create a new user as admin. Checks email uniqueness.
    Cria um novo usuario como admin. Verifica unicidade do email.
    """
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none() is not None:
        raise ConflictException("Email already in use")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        is_active=is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def admin_update_user(
    db: AsyncSession,
    user: User,
    full_name: str | None = None,
    email: EmailStr | None = None,
    is_active: bool | None = None,
) -> User:
    """
    Admin update user fields. Email change checks uniqueness.
    Atualizacao de usuario pelo admin. Mudanca de email verifica unicidade.
    """
    if email is not None and email != user.email:
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none() is not None:
            raise ConflictException("Email already in use")
        user.email = email
    if full_name is not None:
        user.full_name = full_name
    if is_active is not None:
        user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    return user
