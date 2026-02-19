"""
Championships business logic.
Logica de negocios de campeonatos.
"""

import uuid
from datetime import date
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus, championship_entries
from app.core.exceptions import ConflictException, NotFoundException
from app.teams.models import Team


async def list_championships(
    db: AsyncSession,
    status: ChampionshipStatus | None = None,
    season_year: int | None = None,
    is_active: bool | None = None,
) -> list[Championship]:
    """
    List all championships, optionally filtered.
    Lista todos os campeonatos, opcionalmente filtrados.
    """
    stmt = select(Championship).order_by(Championship.name)
    if status is not None:
        stmt = stmt.where(Championship.status == status)
    if season_year is not None:
        stmt = stmt.where(Championship.season_year == season_year)
    if is_active is not None:
        stmt = stmt.where(Championship.is_active == is_active)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_championship_by_id(db: AsyncSession, championship_id: uuid.UUID) -> Championship:
    """
    Get a championship by ID. Raises NotFoundException if not found.
    Busca um campeonato por ID. Lanca NotFoundException se nao encontrado.
    """
    result = await db.execute(select(Championship).where(Championship.id == championship_id))
    championship = result.scalar_one_or_none()
    if championship is None:
        raise NotFoundException("Championship not found")
    await db.refresh(championship, ["teams"])
    return championship


async def create_championship(
    db: AsyncSession,
    name: str,
    display_name: str,
    season_year: int,
    description: str | None = None,
    status: ChampionshipStatus = ChampionshipStatus.planned,
    start_date: date | None = None,
    end_date: date | None = None,
) -> Championship:
    """
    Create a new championship. Raises ConflictException if name already exists.
    Cria um novo campeonato. Lanca ConflictException se o nome ja existe.
    """
    result = await db.execute(select(Championship).where(Championship.name == name))
    if result.scalar_one_or_none() is not None:
        raise ConflictException("Championship name already exists")

    championship = Championship(
        name=name,
        display_name=display_name,
        description=description,
        season_year=season_year,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
    db.add(championship)
    await db.commit()
    await db.refresh(championship)
    return championship


async def update_championship(
    db: AsyncSession,
    championship: Championship,
    display_name: str | None = None,
    description: str | None = None,
    season_year: int | None = None,
    status: ChampionshipStatus | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    is_active: bool | None = None,
) -> Championship:
    """
    Update championship fields.
    Atualiza campos do campeonato.
    """
    if display_name is not None:
        championship.display_name = display_name
    if description is not None:
        championship.description = description
    if season_year is not None:
        championship.season_year = season_year
    if status is not None:
        championship.status = status
    if start_date is not None:
        championship.start_date = start_date
    if end_date is not None:
        championship.end_date = end_date
    if is_active is not None:
        championship.is_active = is_active
    await db.commit()
    await db.refresh(championship)
    return championship


async def delete_championship(db: AsyncSession, championship: Championship) -> None:
    """
    Delete a championship. Clears entries before deleting.
    Exclui um campeonato. Limpa inscricoes antes de excluir.
    """
    championship.teams.clear()
    await db.flush()
    await db.delete(championship)
    await db.commit()


# --- Entry services / Servicos de inscricao ---


async def list_championship_entries(db: AsyncSession, championship_id: uuid.UUID) -> list[dict[str, Any]]:
    """
    List all entries of a championship with registration date.
    Lista todas as inscricoes de um campeonato com data de registro.
    """
    await get_championship_by_id(db, championship_id)

    stmt = (
        select(
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            Team.display_name.label("team_display_name"),
            Team.is_active.label("team_is_active"),
            championship_entries.c.registered_at,
        )
        .join(Team, championship_entries.c.team_id == Team.id)
        .where(championship_entries.c.championship_id == championship_id)
        .order_by(Team.name)
    )
    result = await db.execute(stmt)
    return [row._asdict() for row in result.all()]


async def add_championship_entry(
    db: AsyncSession, championship_id: uuid.UUID, team_id: uuid.UUID
) -> list[dict[str, Any]]:
    """
    Add a team to a championship. Raises NotFoundException if team/championship not found.
    Raises ConflictException if team already enrolled.

    Adiciona uma equipe a um campeonato. Lanca NotFoundException se equipe/campeonato nao encontrado.
    Lanca ConflictException se equipe ja inscrita.
    """
    await get_championship_by_id(db, championship_id)

    result = await db.execute(select(Team).where(Team.id == team_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundException("Team not found")

    existing = await db.execute(
        select(championship_entries).where(
            championship_entries.c.championship_id == championship_id,
            championship_entries.c.team_id == team_id,
        )
    )
    if existing.first() is not None:
        raise ConflictException("Team is already enrolled in this championship")

    await db.execute(championship_entries.insert().values(championship_id=championship_id, team_id=team_id))
    await db.commit()

    return await list_championship_entries(db, championship_id)


async def remove_championship_entry(
    db: AsyncSession, championship_id: uuid.UUID, team_id: uuid.UUID
) -> list[dict[str, Any]]:
    """
    Remove a team from a championship. Raises NotFoundException if entry not found.
    Remove uma equipe de um campeonato. Lanca NotFoundException se inscricao nao encontrada.
    """
    await get_championship_by_id(db, championship_id)

    existing = await db.execute(
        select(championship_entries).where(
            championship_entries.c.championship_id == championship_id,
            championship_entries.c.team_id == team_id,
        )
    )
    if existing.first() is None:
        raise NotFoundException("Team is not enrolled in this championship")

    await db.execute(
        delete(championship_entries).where(
            championship_entries.c.championship_id == championship_id,
            championship_entries.c.team_id == team_id,
        )
    )
    await db.commit()

    return await list_championship_entries(db, championship_id)
