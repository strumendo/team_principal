"""
Roles and permissions business logic.
Logica de negocios de papeis e permissoes.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.roles.models import Permission, Role


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


# --- Role services / Servicos de papel ---


async def list_roles(db: AsyncSession) -> list[Role]:
    """
    List all roles.
    Lista todos os papeis.
    """
    result = await db.execute(select(Role).order_by(Role.name))
    return list(result.scalars().all())


async def get_role_by_id(db: AsyncSession, role_id: uuid.UUID) -> Role:
    """
    Get a role by ID. Raises NotFoundException if not found.
    Busca um papel por ID. Lanca NotFoundException se nao encontrado.
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if role is None:
        raise NotFoundException("Role not found")
    return role


async def create_role(
    db: AsyncSession, name: str, display_name: str, description: str | None = None
) -> Role:
    """
    Create a new role. Raises ConflictException if name already exists.
    Cria um novo papel. Lanca ConflictException se o nome ja existe.
    """
    result = await db.execute(select(Role).where(Role.name == name))
    if result.scalar_one_or_none() is not None:
        raise ConflictException("Role name already exists")

    role = Role(name=name, display_name=display_name, description=description)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update_role(
    db: AsyncSession, role: Role, display_name: str | None = None, description: str | None = None
) -> Role:
    """
    Update role fields.
    Atualiza campos do papel.
    """
    if display_name is not None:
        role.display_name = display_name
    if description is not None:
        role.description = description
    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role: Role) -> None:
    """
    Delete a role. Rejects system roles.
    Exclui um papel. Rejeita papeis do sistema.
    """
    if role.is_system:
        raise ForbiddenException("Cannot delete system role")
    await db.delete(role)
    await db.commit()


async def assign_permission_to_role(db: AsyncSession, role_id: uuid.UUID, permission_id: uuid.UUID) -> Role:
    """
    Assign a permission to a role. Raises ConflictException if already assigned.
    Atribui uma permissao a um papel. Lanca ConflictException se ja atribuida.
    """
    role = await get_role_by_id(db, role_id)
    permission = await get_permission_by_id(db, permission_id)

    if permission in role.permissions:
        raise ConflictException("Permission already assigned to role")

    role.permissions.append(permission)
    await db.commit()
    await db.refresh(role)
    return role


async def revoke_permission_from_role(db: AsyncSession, role_id: uuid.UUID, permission_id: uuid.UUID) -> Role:
    """
    Revoke a permission from a role. Raises NotFoundException if not assigned.
    Revoga uma permissao de um papel. Lanca NotFoundException se nao atribuida.
    """
    role = await get_role_by_id(db, role_id)
    permission = await get_permission_by_id(db, permission_id)

    if permission not in role.permissions:
        raise NotFoundException("Permission not assigned to role")

    role.permissions.remove(permission)
    await db.commit()
    await db.refresh(role)
    return role
