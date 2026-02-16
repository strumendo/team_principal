"""
Database session management (async engine + sessionmaker).
Gerenciamento de sessao do banco de dados (engine async + sessionmaker).
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.
    Dependencia FastAPI que fornece uma sessao assincrona do banco de dados.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
