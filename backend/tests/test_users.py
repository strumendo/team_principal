"""
Tests for users endpoints.
Testes para endpoints de usuarios.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.users.models import User


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, test_user: User, auth_headers: dict[str, str]) -> None:
    """Test GET /api/v1/users/me returns current user / Testa GET /users/me retorna usuario atual."""
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient) -> None:
    """Test GET /api/v1/users/me without token returns 401 / Testa GET /users/me sem token retorna 401."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_me(client: AsyncClient, test_user: User, auth_headers: dict[str, str]) -> None:
    """Test PATCH /api/v1/users/me updates profile / Testa PATCH /users/me atualiza perfil."""
    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"full_name": "Updated Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_get_user_by_id(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str]
) -> None:
    """Test GET /api/v1/users/{id} returns user (requires users:read) / Testa GET /users/{id}."""
    response = await client.get(f"/api/v1/users/{admin_user.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == admin_user.email


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    """Test GET /api/v1/users/{id} with invalid ID returns 404 / Testa GET /users/{id} com ID invalido retorna 404."""
    response = await client.get(
        "/api/v1/users/00000000-0000-0000-0000-000000000000",
        headers=superuser_headers,
    )
    assert response.status_code == 404


# --- List users tests / Testes de listagem de usuarios ---


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, admin_user: User, admin_headers: dict[str, str]) -> None:
    """Test GET /api/v1/users/ returns list with admin_user / Testa GET /users/ retorna lista com admin_user."""
    response = await client.get("/api/v1/users/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    emails = [u["email"] for u in data]
    assert admin_user.email in emails


@pytest.mark.asyncio
async def test_list_users_multiple(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test GET /api/v1/users/ returns multiple users / Testa GET /users/ retorna multiplos usuarios."""
    extra = User(
        email="extra@example.com",
        hashed_password=hash_password("password123"),
        full_name="Extra User",
    )
    db_session.add(extra)
    await db_session.commit()

    response = await client.get("/api/v1/users/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_list_users_filter_active(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test GET /api/v1/users/?is_active=true filters active users / Testa filtro is_active=true."""
    inactive = User(
        email="inactive@example.com",
        hashed_password=hash_password("password123"),
        full_name="Inactive User",
        is_active=False,
    )
    db_session.add(inactive)
    await db_session.commit()

    response = await client.get("/api/v1/users/?is_active=true", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    for u in data:
        assert u["is_active"] is True


@pytest.mark.asyncio
async def test_list_users_filter_inactive(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test GET /api/v1/users/?is_active=false filters inactive users / Testa filtro is_active=false."""
    inactive = User(
        email="inactive2@example.com",
        hashed_password=hash_password("password123"),
        full_name="Inactive User 2",
        is_active=False,
    )
    db_session.add(inactive)
    await db_session.commit()

    response = await client.get("/api/v1/users/?is_active=false", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    for u in data:
        assert u["is_active"] is False


@pytest.mark.asyncio
async def test_list_users_search_name(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test GET /api/v1/users/?search= filters by name / Testa filtro search por nome."""
    unique = User(
        email="unique@example.com",
        hashed_password=hash_password("password123"),
        full_name="Xylophone Player",
    )
    db_session.add(unique)
    await db_session.commit()

    response = await client.get("/api/v1/users/?search=Xylophone", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Xylophone Player"


@pytest.mark.asyncio
async def test_list_users_search_email(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test GET /api/v1/users/?search= filters by email / Testa filtro search por email."""
    unique = User(
        email="searchme@unique.com",
        hashed_password=hash_password("password123"),
        full_name="Search Me",
    )
    db_session.add(unique)
    await db_session.commit()

    response = await client.get("/api/v1/users/?search=searchme@unique", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "searchme@unique.com"


@pytest.mark.asyncio
async def test_list_users_unauthorized(client: AsyncClient) -> None:
    """Test GET /api/v1/users/ without token returns 401 / Testa GET /users/ sem token retorna 401."""
    response = await client.get("/api/v1/users/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_forbidden(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test GET /api/v1/users/ without users:list returns 403 / Testa GET /users/ sem users:list retorna 403."""
    response = await client.get("/api/v1/users/", headers=auth_headers)
    assert response.status_code == 403


# --- Admin update user tests / Testes de atualizacao de usuario pelo admin ---


@pytest.mark.asyncio
async def test_admin_update_user_full_name(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test PATCH /api/v1/users/{id} updates full_name / Testa PATCH /users/{id} atualiza full_name."""
    target = User(
        email="target@example.com",
        hashed_password=hash_password("password123"),
        full_name="Target User",
    )
    db_session.add(target)
    await db_session.commit()
    await db_session.refresh(target)

    response = await client.patch(
        f"/api/v1/users/{target.id}",
        headers=admin_headers,
        json={"full_name": "Updated Target"},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Target"


@pytest.mark.asyncio
async def test_admin_update_user_deactivate(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test PATCH /api/v1/users/{id} deactivates user / Testa PATCH /users/{id} desativa usuario."""
    target = User(
        email="deactivate@example.com",
        hashed_password=hash_password("password123"),
        full_name="Deactivate Me",
    )
    db_session.add(target)
    await db_session.commit()
    await db_session.refresh(target)

    response = await client.patch(
        f"/api/v1/users/{target.id}",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_admin_update_user_email(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test PATCH /api/v1/users/{id} updates email / Testa PATCH /users/{id} atualiza email."""
    target = User(
        email="oldemail@example.com",
        hashed_password=hash_password("password123"),
        full_name="Email User",
    )
    db_session.add(target)
    await db_session.commit()
    await db_session.refresh(target)

    response = await client.patch(
        f"/api/v1/users/{target.id}",
        headers=admin_headers,
        json={"email": "newemail@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newemail@example.com"


@pytest.mark.asyncio
async def test_admin_update_user_email_conflict(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test PATCH /api/v1/users/{id} with duplicate email returns 409 / Testa email duplicado retorna 409."""
    target = User(
        email="conflict1@example.com",
        hashed_password=hash_password("password123"),
        full_name="Conflict User 1",
    )
    other = User(
        email="conflict2@example.com",
        hashed_password=hash_password("password123"),
        full_name="Conflict User 2",
    )
    db_session.add_all([target, other])
    await db_session.commit()
    await db_session.refresh(target)

    response = await client.patch(
        f"/api/v1/users/{target.id}",
        headers=admin_headers,
        json={"email": "conflict2@example.com"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_admin_update_user_not_found(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str]
) -> None:
    """Test PATCH /api/v1/users/{id} with invalid ID returns 404 / Testa ID invalido retorna 404."""
    response = await client.patch(
        "/api/v1/users/00000000-0000-0000-0000-000000000000",
        headers=admin_headers,
        json={"full_name": "Nope"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_update_user_forbidden(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test PATCH /api/v1/users/{id} without users:update returns 403 / Testa sem users:update retorna 403."""
    response = await client.patch(
        f"/api/v1/users/{test_user.id}",
        headers=auth_headers,
        json={"full_name": "Nope"},
    )
    assert response.status_code == 403
