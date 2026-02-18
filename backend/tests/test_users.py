"""
Tests for users endpoints.
Testes para endpoints de usuarios.
"""

import pytest
from httpx import AsyncClient

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
