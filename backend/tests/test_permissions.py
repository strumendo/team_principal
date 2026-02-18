"""
Tests for permissions endpoints.
Testes para endpoints de permissoes.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.roles.models import Permission


@pytest.fixture
async def test_permission(db_session: AsyncSession) -> Permission:
    """
    Create a test permission in the database.
    Cria uma permissao de teste no banco de dados.
    """
    permission = Permission(codename="test:read", module="test", description="Test read permission")
    db_session.add(permission)
    await db_session.commit()
    await db_session.refresh(permission)
    return permission


@pytest.mark.asyncio
async def test_list_permissions_empty(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Test GET /api/v1/permissions/ returns empty list / Testa GET /permissions/ retorna lista vazia."""
    response = await client.get("/api/v1/permissions/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_permission(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Test POST /api/v1/permissions/ creates permission / Testa POST /permissions/ cria permissao."""
    response = await client.post(
        "/api/v1/permissions/",
        headers=auth_headers,
        json={"codename": "users:read", "module": "users", "description": "Read users"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["codename"] == "users:read"
    assert data["module"] == "users"
    assert data["description"] == "Read users"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_permission_duplicate(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Test POST /api/v1/permissions/ with duplicate codename returns 409 / Testa POST com codename duplicado."""
    payload = {"codename": "users:read", "module": "users"}
    await client.post("/api/v1/permissions/", headers=auth_headers, json=payload)
    response = await client.post("/api/v1/permissions/", headers=auth_headers, json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_permissions_filter_by_module(
    client: AsyncClient, auth_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test GET /api/v1/permissions/?module= filters by module / Testa filtro por modulo."""
    db_session.add(Permission(codename="users:read", module="users"))
    db_session.add(Permission(codename="roles:read", module="roles"))
    await db_session.commit()

    response = await client.get("/api/v1/permissions/?module=users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["module"] == "users"


@pytest.mark.asyncio
async def test_get_permission_by_id(
    client: AsyncClient, auth_headers: dict[str, str], test_permission: Permission
) -> None:
    """Test GET /api/v1/permissions/{id} returns permission / Testa GET /permissions/{id}."""
    response = await client.get(f"/api/v1/permissions/{test_permission.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["codename"] == "test:read"


@pytest.mark.asyncio
async def test_get_permission_not_found(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Test GET /api/v1/permissions/{id} with invalid ID returns 404 / Testa com ID invalido retorna 404."""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/v1/permissions/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_permission_unauthorized(client: AsyncClient) -> None:
    """Test POST /api/v1/permissions/ without token returns 401 / Testa POST sem token retorna 401."""
    response = await client.post(
        "/api/v1/permissions/",
        json={"codename": "test:write", "module": "test"},
    )
    assert response.status_code == 401
