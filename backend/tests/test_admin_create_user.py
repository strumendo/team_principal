"""
Tests for admin user creation endpoint.
Testes para o endpoint de criacao de usuario pelo admin.
"""

import pytest
from httpx import AsyncClient

from app.users.models import User


pytestmark = pytest.mark.asyncio


async def test_admin_create_user_success(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Admin can create a new user / Admin pode criar um novo usuario."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "password": "securepass123",
            "full_name": "New User",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["is_active"] is True
    assert "id" in data


async def test_admin_create_user_duplicate_email(
    client: AsyncClient, admin_headers: dict[str, str], admin_user: User
) -> None:
    """Creating user with existing email returns 409 / Criar usuario com email existente retorna 409."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": admin_user.email,
            "password": "securepass123",
            "full_name": "Duplicate User",
        },
        headers=admin_headers,
    )
    assert response.status_code == 409


async def test_admin_create_user_inactive(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Admin can create an inactive user / Admin pode criar um usuario inativo."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "inactive@example.com",
            "password": "securepass123",
            "full_name": "Inactive User",
            "is_active": False,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["is_active"] is False


async def test_admin_create_user_forbidden(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """Regular user cannot create users / Usuario comum nao pode criar usuarios."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "forbidden@example.com",
            "password": "securepass123",
            "full_name": "Forbidden User",
        },
        headers=auth_headers,
    )
    assert response.status_code == 403


async def test_admin_create_user_unauthorized(client: AsyncClient) -> None:
    """Unauthenticated request returns 401 / Requisicao sem autenticacao retorna 401."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "unauth@example.com",
            "password": "securepass123",
            "full_name": "Unauth User",
        },
    )
    assert response.status_code == 401


async def test_admin_create_user_missing_fields(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Missing required fields returns 422 / Campos obrigatorios ausentes retorna 422."""
    response = await client.post(
        "/api/v1/users/",
        json={"email": "partial@example.com"},
        headers=admin_headers,
    )
    assert response.status_code == 422
