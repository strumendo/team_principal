"""
Auth business logic.
Logica de negocios de autenticacao.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, CredentialsException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.users.models import User


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """
    Authenticate a user by email and password.
    Autentica um usuario por email e senha.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.hashed_password):
        raise CredentialsException("Incorrect email or password")
    if not user.is_active:
        raise CredentialsException("Inactive user")
    return user


async def register_user(db: AsyncSession, email: str, password: str, full_name: str) -> User:
    """
    Register a new user.
    Registra um novo usuario.
    """
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none() is not None:
        raise ConflictException("Email already registered")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def create_tokens(user_id: str) -> dict[str, str]:
    """
    Create access and refresh tokens for a user.
    Cria tokens de acesso e atualizacao para um usuario.
    """
    return {
        "access_token": create_access_token(subject=user_id),
        "refresh_token": create_refresh_token(subject=user_id),
        "token_type": "bearer",
    }


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> dict[str, str]:
    """
    Validate refresh token and issue new token pair.
    Valida o token de atualizacao e emite um novo par de tokens.
    """
    payload = decode_token(refresh_token)
    if payload is None:
        raise CredentialsException("Invalid refresh token")

    if payload.get("type") != "refresh":
        raise CredentialsException("Invalid token type")

    user_id = payload.get("sub")
    if user_id is None:
        raise CredentialsException("Invalid refresh token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise CredentialsException("User not found or inactive")

    return create_tokens(str(user.id))
