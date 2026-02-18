"""
FastAPI dependencies for authentication and authorization.
Dependencias FastAPI para autenticacao e autorizacao.
"""

import uuid
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CredentialsException, ForbiddenException
from app.core.security import decode_token
from app.db.session import get_db
from app.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Decode JWT token and return the current user.
    Decodifica o token JWT e retorna o usuario atual.
    """
    payload = decode_token(token)
    if payload is None:
        raise CredentialsException()

    token_type = payload.get("type")
    if token_type != "access":
        raise CredentialsException("Invalid token type")

    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise CredentialsException()

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise CredentialsException()

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise CredentialsException()

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Return the current user if active, otherwise raise Forbidden.
    Retorna o usuario atual se ativo, caso contrario lanca Forbidden.
    """
    if not current_user.is_active:
        raise ForbiddenException("Inactive user")
    return current_user


def require_permissions(
    *codenames: str,
) -> Callable[..., Coroutine[Any, Any, User]]:
    """
    Dependency factory: require ALL listed permissions (AND logic).
    Superuser bypasses all checks.

    Fabrica de dependencia: requer TODAS as permissoes listadas (logica AND).
    Superusuario ignora todas as verificacoes.
    """

    async def _check(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.is_superuser:
            return current_user

        user_permissions: set[str] = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(perm.codename)

        missing = set(codenames) - user_permissions
        if missing:
            raise ForbiddenException(f"Missing permissions: {', '.join(sorted(missing))}")

        return current_user

    return _check


def require_role(
    *role_names: str,
) -> Callable[..., Coroutine[Any, Any, User]]:
    """
    Dependency factory: require ANY of the listed roles (OR logic).
    Superuser bypasses all checks.

    Fabrica de dependencia: requer QUALQUER dos papeis listados (logica OR).
    Superusuario ignora todas as verificacoes.
    """

    async def _check(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.is_superuser:
            return current_user

        user_roles = {r.name for r in current_user.roles}
        if not user_roles & set(role_names):
            raise ForbiddenException(f"Required role: {' or '.join(role_names)}")

        return current_user

    return _check
