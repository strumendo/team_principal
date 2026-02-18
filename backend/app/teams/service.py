"""
Teams business logic.
Logica de negocios de equipes.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.teams.models import Team


async def list_teams(db: AsyncSession, is_active: bool | None = None) -> list[Team]:
    """
    List all teams, optionally filtered by active status.
    Lista todas as equipes, opcionalmente filtradas por status ativo.
    """
    stmt = select(Team).order_by(Team.name)
    if is_active is not None:
        stmt = stmt.where(Team.is_active == is_active)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_team_by_id(db: AsyncSession, team_id: uuid.UUID) -> Team:
    """
    Get a team by ID. Raises NotFoundException if not found.
    Busca uma equipe por ID. Lanca NotFoundException se nao encontrada.
    """
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if team is None:
        raise NotFoundException("Team not found")
    return team


async def create_team(
    db: AsyncSession,
    name: str,
    display_name: str,
    description: str | None = None,
    logo_url: str | None = None,
) -> Team:
    """
    Create a new team. Raises ConflictException if name already exists.
    Cria uma nova equipe. Lanca ConflictException se o nome ja existe.
    """
    result = await db.execute(select(Team).where(Team.name == name))
    if result.scalar_one_or_none() is not None:
        raise ConflictException("Team name already exists")

    team = Team(name=name, display_name=display_name, description=description, logo_url=logo_url)
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


async def update_team(
    db: AsyncSession,
    team: Team,
    display_name: str | None = None,
    description: str | None = None,
    logo_url: str | None = None,
    is_active: bool | None = None,
) -> Team:
    """
    Update team fields.
    Atualiza campos da equipe.
    """
    if display_name is not None:
        team.display_name = display_name
    if description is not None:
        team.description = description
    if logo_url is not None:
        team.logo_url = logo_url
    if is_active is not None:
        team.is_active = is_active
    await db.commit()
    await db.refresh(team)
    return team


async def delete_team(db: AsyncSession, team: Team) -> None:
    """
    Delete a team.
    Exclui uma equipe.
    """
    await db.delete(team)
    await db.commit()
