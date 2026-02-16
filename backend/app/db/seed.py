"""
Database seeding script for initial system roles.
Script de seed do banco de dados para papeis iniciais do sistema.

Usage / Uso: python -m app.db.seed
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.base import Base  # noqa: F401
from app.roles.models import Role

# System roles / Papeis do sistema
SYSTEM_ROLES = [
    {
        "name": "admin",
        "display_name": "Admin",
        "description": "Full system access / Acesso total ao sistema",
        "is_system": True,
    },
    {
        "name": "tech_lead",
        "display_name": "Tech Lead",
        "description": "Technical leadership and setup management / Lideranca tecnica e gerenciamento de setup",
        "is_system": True,
    },
    {
        "name": "performance_lead",
        "display_name": "Performance Lead",
        "description": "Performance analysis and telemetry / Analise de desempenho e telemetria",
        "is_system": True,
    },
    {
        "name": "radio_support",
        "display_name": "Radio/Support",
        "description": "Communication and race support / Comunicacao e suporte de corrida",
        "is_system": True,
    },
    {
        "name": "pilot",
        "display_name": "Pilot",
        "description": "Driver with access to own data / Piloto com acesso aos proprios dados",
        "is_system": True,
    },
    {
        "name": "media",
        "display_name": "Media",
        "description": "Content creation and media management / Criacao de conteudo e gerenciamento de midia",
        "is_system": True,
    },
]


async def seed_roles(session: AsyncSession) -> None:
    """
    Seed system roles if they don't exist.
    Popula papeis do sistema se nao existirem.
    """
    for role_data in SYSTEM_ROLES:
        result = await session.execute(select(Role).where(Role.name == role_data["name"]))
        existing = result.scalar_one_or_none()
        if existing is None:
            session.add(Role(**role_data))
            print(f"  Created role / Papel criado: {role_data['display_name']}")
        else:
            print(f"  Role already exists / Papel ja existe: {role_data['display_name']}")
    await session.commit()


async def main() -> None:
    """
    Main seed function.
    Funcao principal de seed.
    """
    print("Seeding database... / Populando banco de dados...")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed_roles(session)

    await engine.dispose()
    print("Done! / Concluido!")


if __name__ == "__main__":
    asyncio.run(main())
