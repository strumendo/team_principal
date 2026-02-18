"""
Tests for RBAC dependencies (require_permissions, require_role, superuser bypass).
Testes para dependencias RBAC (require_permissions, require_role, superuser bypass).
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password
from app.roles.models import Permission, Role
from app.users.models import User


# --- Superuser bypass / Bypass de superusuario ---


@pytest.mark.asyncio
async def test_superuser_bypasses_permissions(
    client: AsyncClient, superuser_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test superuser can access permission-protected endpoints / Testa bypass de superusuario."""
    response = await client.get("/api/v1/permissions/", headers=superuser_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_superuser_bypasses_roles_endpoint(
    client: AsyncClient, superuser_headers: dict[str, str], db_session: AsyncSession
) -> None:
    """Test superuser can access roles endpoints / Testa superusuario acessa endpoints de papeis."""
    response = await client.get("/api/v1/roles/", headers=superuser_headers)
    assert response.status_code == 200


# --- User without permissions / Usuario sem permissoes ---


@pytest.mark.asyncio
async def test_user_without_permissions_gets_403(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """Test user without permissions gets 403 / Testa usuario sem permissoes recebe 403."""
    response = await client.get("/api/v1/permissions/", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_without_permissions_on_roles(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """Test user without roles:read permission gets 403 on roles / Testa 403 em papeis."""
    response = await client.get("/api/v1/roles/", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_without_users_read_gets_403(
    client: AsyncClient, test_user: User, auth_headers: dict[str, str]
) -> None:
    """Test user without users:read gets 403 on GET /users/{id} / Testa 403 em users/{id}."""
    response = await client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 403


# --- User with permissions / Usuario com permissoes ---


@pytest.mark.asyncio
async def test_admin_can_list_permissions(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test admin user can list permissions / Testa admin pode listar permissoes."""
    response = await client.get("/api/v1/permissions/", headers=admin_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_can_list_roles(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test admin user can list roles / Testa admin pode listar papeis."""
    response = await client.get("/api/v1/roles/", headers=admin_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_can_read_user_by_id(
    client: AsyncClient, admin_user: User, admin_headers: dict[str, str]
) -> None:
    """Test admin can read user by ID / Testa admin pode ler usuario por ID."""
    response = await client.get(f"/api/v1/users/{admin_user.id}", headers=admin_headers)
    assert response.status_code == 200


# --- require_permissions AND logic / Logica AND de require_permissions ---


@pytest.mark.asyncio
async def test_require_permissions_and_logic(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test that require_permissions checks ALL permissions (AND) / Testa logica AND."""
    # Create user with only permissions:read (missing permissions:create)
    perm_read = Permission(codename="permissions:read", module="permissions")
    db_session.add(perm_read)
    await db_session.flush()

    role = Role(name="reader", display_name="Reader")
    role.permissions = [perm_read]
    db_session.add(role)
    await db_session.flush()

    user = User(
        email="reader@example.com",
        hashed_password=hash_password("readerpass123"),
        full_name="Reader User",
    )
    user.roles = [role]
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token(subject=str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    # Can list permissions (has permissions:read) / Pode listar (tem permissions:read)
    response = await client.get("/api/v1/permissions/", headers=headers)
    assert response.status_code == 200

    # Cannot create permission (missing permissions:create) / Nao pode criar (falta permissions:create)
    response = await client.post(
        "/api/v1/permissions/",
        headers=headers,
        json={"codename": "test:new", "module": "test"},
    )
    assert response.status_code == 403


# --- require_role OR logic / Logica OR de require_role ---


@pytest.mark.asyncio
async def test_require_role_or_logic(db_session: AsyncSession) -> None:
    """Test that require_role checks ANY role (OR) / Testa logica OR."""
    from app.core.dependencies import require_role

    role_pilot = Role(name="pilot", display_name="Pilot")
    db_session.add(role_pilot)
    await db_session.flush()

    user = User(
        email="pilot@example.com",
        hashed_password=hash_password("pilotpass123"),
        full_name="Pilot User",
    )
    user.roles = [role_pilot]
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # require_role("admin", "pilot") should pass because user has "pilot"
    checker = require_role("admin", "pilot")
    result = await checker(current_user=user)
    assert result.id == user.id


@pytest.mark.asyncio
async def test_require_role_rejects_without_match(db_session: AsyncSession) -> None:
    """Test require_role rejects user without matching role / Testa rejeicao sem papel correspondente."""
    from app.core.dependencies import require_role
    from app.core.exceptions import ForbiddenException

    user = User(
        email="norole@example.com",
        hashed_password=hash_password("norolepass123"),
        full_name="No Role User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    checker = require_role("admin")
    with pytest.raises(ForbiddenException):
        await checker(current_user=user)


# --- Inactive user blocked / Usuario inativo bloqueado ---


@pytest.mark.asyncio
async def test_inactive_user_blocked(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test inactive user is blocked even with permissions / Testa usuario inativo bloqueado."""
    perm = Permission(codename="permissions:read", module="permissions")
    db_session.add(perm)
    await db_session.flush()

    role = Role(name="some_role", display_name="Some Role")
    role.permissions = [perm]
    db_session.add(role)
    await db_session.flush()

    user = User(
        email="inactive@example.com",
        hashed_password=hash_password("inactivepass123"),
        full_name="Inactive User",
        is_active=False,
    )
    user.roles = [role]
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token(subject=str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/permissions/", headers=headers)
    assert response.status_code == 403
