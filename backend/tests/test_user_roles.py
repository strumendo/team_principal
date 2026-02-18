"""
Tests for user-role assignment endpoints.
Testes para endpoints de atribuicao de papel a usuario.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.roles.models import Role, user_roles
from app.users.models import User


@pytest.fixture
async def target_user(db_session: AsyncSession) -> User:
    """Create a target user for role assignment / Cria um usuario alvo para atribuicao de papel."""
    from app.core.security import hash_password

    user = User(
        email="target@example.com",
        hashed_password=hash_password("targetpass123"),
        full_name="Target User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def assignable_role(db_session: AsyncSession) -> Role:
    """Create a role to assign / Cria um papel para atribuir."""
    role = Role(name="pilot", display_name="Pilot", description="Pilot role")
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


# --- List user roles / Listar papeis do usuario ---


@pytest.mark.asyncio
async def test_list_user_roles_empty(
    client: AsyncClient, superuser_headers: dict[str, str], target_user: User
) -> None:
    """Test GET /users/{id}/roles returns empty list / Testa lista vazia de papeis."""
    response = await client.get(f"/api/v1/users/{target_user.id}/roles", headers=superuser_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_user_roles_not_found(client: AsyncClient, superuser_headers: dict[str, str]) -> None:
    """Test GET /users/{id}/roles with invalid user returns 404 / Testa usuario nao encontrado."""
    response = await client.get(f"/api/v1/users/{uuid.uuid4()}/roles", headers=superuser_headers)
    assert response.status_code == 404


# --- Assign role / Atribuir papel ---


@pytest.mark.asyncio
async def test_assign_role_to_user(
    client: AsyncClient,
    superuser_headers: dict[str, str],
    target_user: User,
    assignable_role: Role,
) -> None:
    """Test POST /users/{id}/roles assigns role / Testa atribuicao de papel."""
    response = await client.post(
        f"/api/v1/users/{target_user.id}/roles",
        headers=superuser_headers,
        json={"role_id": str(assignable_role.id)},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "pilot"


@pytest.mark.asyncio
async def test_assign_role_duplicate(
    client: AsyncClient,
    superuser_headers: dict[str, str],
    target_user: User,
    assignable_role: Role,
) -> None:
    """Test assigning same role twice returns 409 / Testa atribuicao duplicada retorna 409."""
    payload = {"role_id": str(assignable_role.id)}
    await client.post(f"/api/v1/users/{target_user.id}/roles", headers=superuser_headers, json=payload)
    response = await client.post(f"/api/v1/users/{target_user.id}/roles", headers=superuser_headers, json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_assign_role_user_not_found(
    client: AsyncClient, superuser_headers: dict[str, str], assignable_role: Role
) -> None:
    """Test assigning role to nonexistent user returns 404 / Testa usuario nao encontrado."""
    response = await client.post(
        f"/api/v1/users/{uuid.uuid4()}/roles",
        headers=superuser_headers,
        json={"role_id": str(assignable_role.id)},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_assign_role_role_not_found(
    client: AsyncClient, superuser_headers: dict[str, str], target_user: User
) -> None:
    """Test assigning nonexistent role returns 404 / Testa papel nao encontrado."""
    response = await client.post(
        f"/api/v1/users/{target_user.id}/roles",
        headers=superuser_headers,
        json={"role_id": str(uuid.uuid4())},
    )
    assert response.status_code == 404


# --- Revoke role / Revogar papel ---


@pytest.mark.asyncio
async def test_revoke_role_from_user(
    client: AsyncClient,
    superuser_headers: dict[str, str],
    target_user: User,
    assignable_role: Role,
) -> None:
    """Test DELETE /users/{id}/roles/{role_id} revokes role / Testa revogacao de papel."""
    await client.post(
        f"/api/v1/users/{target_user.id}/roles",
        headers=superuser_headers,
        json={"role_id": str(assignable_role.id)},
    )

    response = await client.delete(
        f"/api/v1/users/{target_user.id}/roles/{assignable_role.id}",
        headers=superuser_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_revoke_role_not_assigned(
    client: AsyncClient,
    superuser_headers: dict[str, str],
    target_user: User,
    assignable_role: Role,
) -> None:
    """Test revoking unassigned role returns 404 / Testa revogacao de papel nao atribuido."""
    response = await client.delete(
        f"/api/v1/users/{target_user.id}/roles/{assignable_role.id}",
        headers=superuser_headers,
    )
    assert response.status_code == 404


# --- Permission enforcement / Enforcement de permissoes ---


@pytest.mark.asyncio
async def test_assign_role_without_permission(
    client: AsyncClient, auth_headers: dict[str, str], target_user: User, assignable_role: Role
) -> None:
    """Test user without roles:assign gets 403 / Testa usuario sem permissao recebe 403."""
    response = await client.post(
        f"/api/v1/users/{target_user.id}/roles",
        headers=auth_headers,
        json={"role_id": str(assignable_role.id)},
    )
    assert response.status_code == 403


# --- assigned_by field / Campo assigned_by ---


@pytest.mark.asyncio
async def test_assigned_by_is_set(
    client: AsyncClient,
    superuser: User,
    superuser_headers: dict[str, str],
    target_user: User,
    assignable_role: Role,
    db_session: AsyncSession,
) -> None:
    """Test that assigned_by is filled with the assigner's ID / Testa que assigned_by e preenchido."""
    await client.post(
        f"/api/v1/users/{target_user.id}/roles",
        headers=superuser_headers,
        json={"role_id": str(assignable_role.id)},
    )

    result = await db_session.execute(
        select(user_roles).where(
            user_roles.c.user_id == target_user.id,
            user_roles.c.role_id == assignable_role.id,
        )
    )
    row = result.first()
    assert row is not None
    assert row.assigned_by == superuser.id
