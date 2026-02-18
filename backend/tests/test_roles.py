"""
Tests for roles endpoints.
Testes para endpoints de papeis.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.roles.models import Permission, Role
from app.users.models import User


@pytest.fixture
async def test_permission(db_session: AsyncSession) -> Permission:
    """Create a test permission / Cria uma permissao de teste."""
    permission = Permission(codename="test:read", module="test", description="Test read")
    db_session.add(permission)
    await db_session.commit()
    await db_session.refresh(permission)
    return permission


@pytest.fixture
async def test_role(db_session: AsyncSession) -> Role:
    """Create a custom (non-system) test role / Cria um papel de teste customizado."""
    role = Role(name="custom_role", display_name="Custom Role", description="A custom role")
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest.fixture
async def test_system_role(db_session: AsyncSession) -> Role:
    """Create a system test role / Cria um papel de teste do sistema."""
    role = Role(name="sys_role", display_name="System Role", description="A system role", is_system=True)
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


# --- List roles / Listar papeis ---


@pytest.mark.asyncio
async def test_list_roles_empty(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    """Test GET /api/v1/roles/ returns empty list / Testa GET /roles/ retorna lista vazia."""
    response = await client.get("/api/v1/roles/", headers=superuser_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_roles(client: AsyncClient, superuser_headers: dict[str, str], test_role: Role) -> None:
    """Test GET /api/v1/roles/ returns roles / Testa GET /roles/ retorna papeis."""
    response = await client.get("/api/v1/roles/", headers=superuser_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "custom_role"
    assert "permissions" not in data[0]


# --- Get role by ID / Buscar papel por ID ---


@pytest.mark.asyncio
async def test_get_role_by_id(client: AsyncClient, superuser_headers: dict[str, str], test_role: Role) -> None:
    """Test GET /api/v1/roles/{id} returns role with permissions / Testa GET /roles/{id}."""
    response = await client.get(f"/api/v1/roles/{test_role.id}", headers=superuser_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "custom_role"
    assert "permissions" in data
    assert data["permissions"] == []


@pytest.mark.asyncio
async def test_get_role_not_found(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    """Test GET /api/v1/roles/{id} with invalid ID returns 404 / Testa com ID invalido retorna 404."""
    response = await client.get(f"/api/v1/roles/{uuid.uuid4()}", headers=superuser_headers)
    assert response.status_code == 404


# --- Create role / Criar papel ---


@pytest.mark.asyncio
async def test_create_role(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    """Test POST /api/v1/roles/ creates role / Testa POST /roles/ cria papel."""
    response = await client.post(
        "/api/v1/roles/",
        headers=superuser_headers,
        json={"name": "new_role", "display_name": "New Role", "description": "A new role"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "new_role"
    assert data["display_name"] == "New Role"
    assert data["is_system"] is False


@pytest.mark.asyncio
async def test_create_role_duplicate(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    """Test POST /api/v1/roles/ with duplicate name returns 409 / Testa com nome duplicado retorna 409."""
    payload = {"name": "dup_role", "display_name": "Dup Role"}
    await client.post("/api/v1/roles/", headers=superuser_headers, json=payload)
    response = await client.post("/api/v1/roles/", headers=superuser_headers, json=payload)
    assert response.status_code == 409


# --- Update role / Atualizar papel ---


@pytest.mark.asyncio
async def test_update_role(client: AsyncClient, superuser_headers: dict[str, str], test_role: Role) -> None:
    """Test PATCH /api/v1/roles/{id} updates role / Testa PATCH /roles/{id} atualiza papel."""
    response = await client.patch(
        f"/api/v1/roles/{test_role.id}",
        headers=superuser_headers,
        json={"display_name": "Updated Role"},
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Updated Role"


# --- Delete role / Excluir papel ---


@pytest.mark.asyncio
async def test_delete_role(client: AsyncClient, superuser_headers: dict[str, str], test_role: Role) -> None:
    """Test DELETE /api/v1/roles/{id} deletes non-system role / Testa DELETE de papel nao-sistema."""
    response = await client.delete(f"/api/v1/roles/{test_role.id}", headers=superuser_headers)
    assert response.status_code == 204

    response = await client.get(f"/api/v1/roles/{test_role.id}", headers=superuser_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_system_role_forbidden(
    client: AsyncClient, superuser_headers: dict[str, str], test_system_role: Role
) -> None:
    """Test DELETE /api/v1/roles/{id} rejects system role / Testa rejeicao de exclusao de papel do sistema."""
    response = await client.delete(f"/api/v1/roles/{test_system_role.id}", headers=superuser_headers)
    assert response.status_code == 403


# --- Assign/revoke permission / Atribuir/revogar permissao ---


@pytest.mark.asyncio
async def test_assign_permission_to_role(
    client: AsyncClient, superuser_headers: dict[str, str], test_role: Role, test_permission: Permission
) -> None:
    """Test POST /roles/{id}/permissions assigns permission / Testa atribuicao de permissao."""
    response = await client.post(
        f"/api/v1/roles/{test_role.id}/permissions",
        headers=superuser_headers,
        json={"permission_id": str(test_permission.id)},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["permissions"]) == 1
    assert data["permissions"][0]["codename"] == "test:read"


@pytest.mark.asyncio
async def test_assign_permission_duplicate(
    client: AsyncClient, superuser_headers: dict[str, str], test_role: Role, test_permission: Permission
) -> None:
    """Test assigning same permission twice returns 409 / Testa atribuicao duplicada retorna 409."""
    payload = {"permission_id": str(test_permission.id)}
    await client.post(f"/api/v1/roles/{test_role.id}/permissions", headers=superuser_headers, json=payload)
    response = await client.post(f"/api/v1/roles/{test_role.id}/permissions", headers=superuser_headers, json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_revoke_permission_from_role(
    client: AsyncClient, superuser_headers: dict[str, str], test_role: Role, test_permission: Permission
) -> None:
    """Test DELETE /roles/{id}/permissions/{pid} revokes permission / Testa revogacao de permissao."""
    await client.post(
        f"/api/v1/roles/{test_role.id}/permissions",
        headers=superuser_headers,
        json={"permission_id": str(test_permission.id)},
    )

    response = await client.delete(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=superuser_headers,
    )
    assert response.status_code == 200
    assert response.json()["permissions"] == []


@pytest.mark.asyncio
async def test_revoke_permission_not_assigned(
    client: AsyncClient, superuser_headers: dict[str, str], test_role: Role, test_permission: Permission
) -> None:
    """Test revoking unassigned permission returns 404 / Testa revogacao de permissao nao atribuida."""
    response = await client.delete(
        f"/api/v1/roles/{test_role.id}/permissions/{test_permission.id}",
        headers=superuser_headers,
    )
    assert response.status_code == 404
