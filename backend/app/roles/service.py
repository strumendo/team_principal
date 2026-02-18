"""
Roles and permissions business logic.
Logica de negocios de papeis e permissoes.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.roles.models import Permission


async def list_permissions(db: AsyncSession, module: str | None = None) -> list[Permission]:
    """
    List all permissions, optionally filtered by module.
    Lista todas as permissoes, opcionalmente filtradas por modulo.
    """
    stmt = select(Permission).order_by(Permission.codename)
    if module is not None:
        stmt = stmt.where(Permission.module == module)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_permission_by_id(db: AsyncSession, permission_id: uuid.UUID) -> Permission:
    """
    Get a permission by ID. Raises NotFoundException if not found.
    Busca uma permissao por ID. Lanca NotFoundException se nao encontrada.
    """
    result = await db.execute(select(Permission).where(Permission.id == permission_id))
    permission = result.scalar_one_or_none()
    if permission is None:
        raise NotFoundException("Permission not found")
    return permission


async def create_permission(
    db: AsyncSession, codename: str, module: str, description: str | None = None
) -> Permission:
    """
    Create a new permission. Raises ConflictException if codename already exists.
    Cria uma nova permissao. Lanca ConflictException se codename ja existe.
    """
    result = await db.execute(select(Permission).where(Permission.codename == codename))
    if result.scalar_one_or_none() is not None:
        raise ConflictException("Permission codename already exists")

    permission = Permission(codename=codename, module=module, description=description)
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    return permission
