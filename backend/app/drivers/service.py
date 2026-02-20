"""
Drivers business logic.
Logica de negocios de pilotos.
"""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.drivers.models import Driver
from app.teams.models import Team


async def list_drivers(
    db: AsyncSession,
    is_active: bool | None = None,
    team_id: uuid.UUID | None = None,
) -> list[Driver]:
    """
    List all drivers, optionally filtered by active status and/or team.
    Lista todos os pilotos, opcionalmente filtrados por status ativo e/ou equipe.
    """
    stmt = select(Driver).order_by(Driver.name)
    if is_active is not None:
        stmt = stmt.where(Driver.is_active == is_active)
    if team_id is not None:
        stmt = stmt.where(Driver.team_id == team_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_driver_by_id(db: AsyncSession, driver_id: uuid.UUID) -> Driver:
    """
    Get a driver by ID. Raises NotFoundException if not found.
    Busca um piloto por ID. Lanca NotFoundException se nao encontrado.
    """
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if driver is None:
        raise NotFoundException("Driver not found")
    return driver


async def create_driver(
    db: AsyncSession,
    name: str,
    display_name: str,
    abbreviation: str,
    number: int,
    team_id: uuid.UUID,
    nationality: str | None = None,
    date_of_birth: date | None = None,
    photo_url: str | None = None,
) -> Driver:
    """
    Create a new driver. Validates team exists, name/abbreviation uniqueness,
    and number uniqueness within team.

    Cria um novo piloto. Valida que equipe existe, unicidade de nome/abreviacao,
    e unicidade de numero dentro da equipe.
    """
    # Validate team exists / Valida que a equipe existe
    team_query = await db.execute(select(Team).where(Team.id == team_id))
    if team_query.scalar_one_or_none() is None:
        raise NotFoundException("Team not found")

    # Validate name uniqueness / Valida unicidade do nome
    name_query = await db.execute(select(Driver).where(Driver.name == name))
    if name_query.scalar_one_or_none() is not None:
        raise ConflictException("Driver name already exists")

    # Validate abbreviation uniqueness / Valida unicidade da abreviacao
    abbr_query = await db.execute(select(Driver).where(Driver.abbreviation == abbreviation))
    if abbr_query.scalar_one_or_none() is not None:
        raise ConflictException("Driver abbreviation already exists")

    # Validate number uniqueness within team / Valida unicidade do numero dentro da equipe
    num_query = await db.execute(
        select(Driver).where(Driver.team_id == team_id, Driver.number == number)
    )
    if num_query.scalar_one_or_none() is not None:
        raise ConflictException("Number already taken within this team")

    driver = Driver(
        name=name,
        display_name=display_name,
        abbreviation=abbreviation,
        number=number,
        team_id=team_id,
        nationality=nationality,
        date_of_birth=date_of_birth,
        photo_url=photo_url,
    )
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    return driver


async def update_driver(
    db: AsyncSession,
    driver: Driver,
    display_name: str | None = None,
    abbreviation: str | None = None,
    number: int | None = None,
    nationality: str | None = None,
    date_of_birth: date | None = None,
    photo_url: str | None = None,
    is_active: bool | None = None,
) -> Driver:
    """
    Update driver fields. Validates abbreviation and number uniqueness.
    Atualiza campos do piloto. Valida unicidade de abreviacao e numero.
    """
    # Validate abbreviation uniqueness if changed / Valida unicidade da abreviacao se alterada
    if abbreviation is not None and abbreviation != driver.abbreviation:
        abbr_query = await db.execute(select(Driver).where(Driver.abbreviation == abbreviation))
        if abbr_query.scalar_one_or_none() is not None:
            raise ConflictException("Driver abbreviation already exists")

    # Validate number uniqueness within team if changed / Valida unicidade do numero se alterado
    if number is not None and number != driver.number:
        num_query = await db.execute(
            select(Driver).where(Driver.team_id == driver.team_id, Driver.number == number)
        )
        if num_query.scalar_one_or_none() is not None:
            raise ConflictException("Number already taken within this team")

    if display_name is not None:
        driver.display_name = display_name
    if abbreviation is not None:
        driver.abbreviation = abbreviation
    if number is not None:
        driver.number = number
    if nationality is not None:
        driver.nationality = nationality
    if date_of_birth is not None:
        driver.date_of_birth = date_of_birth
    if photo_url is not None:
        driver.photo_url = photo_url
    if is_active is not None:
        driver.is_active = is_active

    await db.commit()
    await db.refresh(driver)
    return driver


async def delete_driver(db: AsyncSession, driver: Driver) -> None:
    """
    Delete a driver.
    Exclui um piloto.
    """
    await db.delete(driver)
    await db.commit()
