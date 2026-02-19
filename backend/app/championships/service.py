"""
Championships business logic.
Logica de negocios de campeonatos.
"""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus
from app.core.exceptions import ConflictException, NotFoundException


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
    Delete a championship.
    Exclui um campeonato.
    """
    await db.delete(championship)
    await db.commit()
