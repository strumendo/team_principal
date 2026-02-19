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
from app.roles.models import Permission, Role, role_permissions, user_roles  # noqa: F401
from app.championships.models import Championship, championship_entries  # noqa: F401
from app.races.models import Race, race_entries  # noqa: F401
from app.results.models import RaceResult  # noqa: F401
from app.teams.models import Team  # noqa: F401
from app.users.models import User  # noqa: F401

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


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """
    Create an admin user with the admin role and all permissions.
    Cria um usuario admin com o papel admin e todas as permissoes.
    """
    # Create permissions / Criar permissoes
    perms = []
    for codename, module in [
        ("permissions:read", "permissions"),
        ("permissions:create", "permissions"),
        ("permissions:assign", "permissions"),
        ("permissions:revoke", "permissions"),
        ("roles:read", "roles"),
        ("roles:create", "roles"),
        ("roles:update", "roles"),
        ("roles:delete", "roles"),
        ("roles:assign", "roles"),
        ("roles:revoke", "roles"),
        ("users:read", "users"),
        ("teams:read", "teams"),
        ("teams:create", "teams"),
        ("teams:update", "teams"),
        ("teams:delete", "teams"),
        ("teams:manage_members", "teams"),
        ("championships:read", "championships"),
        ("championships:create", "championships"),
        ("championships:update", "championships"),
        ("championships:delete", "championships"),
        ("championships:manage_entries", "championships"),
        ("races:read", "races"),
        ("races:create", "races"),
        ("races:update", "races"),
        ("races:delete", "races"),
        ("races:manage_entries", "races"),
        ("results:read", "results"),
        ("results:create", "results"),
        ("results:update", "results"),
        ("results:delete", "results"),
    ]:
        perm = Permission(codename=codename, module=module)
        db_session.add(perm)
        perms.append(perm)
    await db_session.flush()

    # Create admin role with permissions / Criar papel admin com permissoes
    admin_role = Role(name="admin", display_name="Admin", is_system=True)
    admin_role.permissions = perms
    db_session.add(admin_role)
    await db_session.flush()

    # Create admin user / Criar usuario admin
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("adminpassword123"),
        full_name="Admin User",
    )
    user.roles = [admin_role]
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user: User) -> dict[str, str]:
    """
    Provide auth headers for the admin user.
    Fornece headers de autenticacao para o usuario admin.
    """
    token = create_access_token(subject=str(admin_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def superuser(db_session: AsyncSession) -> User:
    """
    Create a superuser (bypasses all permission checks).
    Cria um superusuario (ignora todas as verificacoes de permissao).
    """
    user = User(
        email="super@example.com",
        hashed_password=hash_password("superpassword123"),
        full_name="Super User",
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def superuser_headers(superuser: User) -> dict[str, str]:
    """
    Provide auth headers for the superuser.
    Fornece headers de autenticacao para o superusuario.
    """
    token = create_access_token(subject=str(superuser.id))
    return {"Authorization": f"Bearer {token}"}
