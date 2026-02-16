"""
Test fixtures for the backend test suite.
Fixtures de teste para a suite de testes do backend.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.users.models import User  # noqa: F401
from app.roles.models import Role, Permission, role_permissions, user_roles  # noqa: F401

# Use in-memory SQLite for tests / Usa SQLite em memoria para testes
TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """
    Create tables before each test and drop after.
    Cria tabelas antes de cada teste e remove depois.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a test database session.
    Fornece uma sessao de banco de dados de teste.
    """
    async with test_async_session() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP test client with dependency overrides.
    Fornece um cliente HTTP de teste async com dependencias sobrescritas.
    """
    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Create a test user in the database.
    Cria um usuario de teste no banco de dados.
    """
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """
    Provide auth headers with a valid access token for the test user.
    Fornece headers de autenticacao com um token de acesso valido para o usuario de teste.
    """
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}
