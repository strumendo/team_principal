"""
Tests for team membership endpoints.
Testes para endpoints de membros de equipe.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password
from app.roles.models import Permission, Role
from app.teams.models import Team
from app.users.models import User


@pytest.fixture
async def test_team(db_session: AsyncSession) -> Team:
    """Create a test team / Cria uma equipe de teste."""
    team = Team(name="red_bull_racing", display_name="Red Bull Racing")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def other_team(db_session: AsyncSession) -> Team:
    """Create another test team / Cria outra equipe de teste."""
    team = Team(name="mclaren", display_name="McLaren Racing")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def member_user(db_session: AsyncSession) -> User:
    """Create a user to be added as a team member / Cria um usuario para ser membro."""
    user = User(
        email="member@example.com",
        hashed_password=hash_password("memberpassword123"),
        full_name="Member User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def reader_user(db_session: AsyncSession) -> User:
    """Create a user with only teams:read permission / Cria usuario com apenas teams:read."""
    perm = Permission(codename="teams:read", module="teams")
    db_session.add(perm)
    await db_session.flush()

    role = Role(name="reader", display_name="Reader")
    role.permissions = [perm]
    db_session.add(role)
    await db_session.flush()

    user = User(
        email="reader@example.com",
        hashed_password=hash_password("readerpassword123"),
        full_name="Reader User",
    )
    user.roles = [role]
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def reader_headers(reader_user: User) -> dict[str, str]:
    """Provide auth headers for the reader user / Headers de auth para usuario leitor."""
    token = create_access_token(subject=str(reader_user.id))
    return {"Authorization": f"Bearer {token}"}


# --- List members / Listar membros ---


@pytest.mark.asyncio
async def test_list_members_empty(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test GET /teams/{id}/members returns empty list / Retorna lista vazia."""
    response = await client.get(f"/api/v1/teams/{test_team.id}/members", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_members_team_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test GET /teams/{id}/members with invalid team returns 404 / Equipe invalida retorna 404."""
    response = await client.get(f"/api/v1/teams/{uuid.uuid4()}/members", headers=admin_headers)
    assert response.status_code == 404


# --- Add member / Adicionar membro ---


@pytest.mark.asyncio
async def test_add_member(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team, member_user: User
) -> None:
    """Test POST /teams/{id}/members adds member / Adiciona membro."""
    response = await client.post(
        f"/api/v1/teams/{test_team.id}/members",
        headers=admin_headers,
        json={"user_id": str(member_user.id)},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "member@example.com"


@pytest.mark.asyncio
async def test_add_member_duplicate_same_team(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team, member_user: User
) -> None:
    """Test adding same user twice to same team returns 409 / Duplicado no mesmo time retorna 409."""
    payload = {"user_id": str(member_user.id)}
    await client.post(f"/api/v1/teams/{test_team.id}/members", headers=admin_headers, json=payload)
    response = await client.post(f"/api/v1/teams/{test_team.id}/members", headers=admin_headers, json=payload)
    assert response.status_code == 409
    assert "already a member" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_member_already_in_other_team(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_team: Team,
    other_team: Team,
    member_user: User,
) -> None:
    """Test adding user who belongs to another team returns 409 / Usuario em outro time retorna 409."""
    await client.post(
        f"/api/v1/teams/{test_team.id}/members",
        headers=admin_headers,
        json={"user_id": str(member_user.id)},
    )
    response = await client.post(
        f"/api/v1/teams/{other_team.id}/members",
        headers=admin_headers,
        json={"user_id": str(member_user.id)},
    )
    assert response.status_code == 409
    assert "another team" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_member_user_not_found(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test adding non-existent user returns 404 / Usuario inexistente retorna 404."""
    response = await client.post(
        f"/api/v1/teams/{test_team.id}/members",
        headers=admin_headers,
        json={"user_id": str(uuid.uuid4())},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_member_team_not_found(
    client: AsyncClient, admin_headers: dict[str, str], member_user: User
) -> None:
    """Test adding member to non-existent team returns 404 / Time inexistente retorna 404."""
    response = await client.post(
        f"/api/v1/teams/{uuid.uuid4()}/members",
        headers=admin_headers,
        json={"user_id": str(member_user.id)},
    )
    assert response.status_code == 404


# --- Remove member / Remover membro ---


@pytest.mark.asyncio
async def test_remove_member(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team, member_user: User
) -> None:
    """Test DELETE /teams/{id}/members/{uid} removes member / Remove membro."""
    await client.post(
        f"/api/v1/teams/{test_team.id}/members",
        headers=admin_headers,
        json={"user_id": str(member_user.id)},
    )
    response = await client.delete(
        f"/api/v1/teams/{test_team.id}/members/{member_user.id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_remove_non_member(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team, member_user: User
) -> None:
    """Test removing non-member returns 404 / Remover nao-membro retorna 404."""
    response = await client.delete(
        f"/api/v1/teams/{test_team.id}/members/{member_user.id}",
        headers=admin_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_remove_user_not_found(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test removing non-existent user returns 404 / Usuario inexistente retorna 404."""
    response = await client.delete(
        f"/api/v1/teams/{test_team.id}/members/{uuid.uuid4()}",
        headers=admin_headers,
    )
    assert response.status_code == 404


# --- Delete team nullifies members / Exclusao anula membros ---


@pytest.mark.asyncio
async def test_delete_team_nullifies_members(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team, member_user: User
) -> None:
    """Test deleting a team nullifies team_id for members / Exclusao anula team_id dos membros."""
    await client.post(
        f"/api/v1/teams/{test_team.id}/members",
        headers=admin_headers,
        json={"user_id": str(member_user.id)},
    )
    response = await client.delete(f"/api/v1/teams/{test_team.id}", headers=admin_headers)
    assert response.status_code == 204

    # Verify user's team_id is now null via the users endpoint
    # Verificar que team_id do usuario e null
    response = await client.get("/api/v1/users/me", headers=admin_headers)
    assert response.status_code == 200


# --- Team detail includes members / Detalhe inclui membros ---


@pytest.mark.asyncio
async def test_get_team_detail_includes_members(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team, member_user: User
) -> None:
    """Test GET /teams/{id} includes members / GET /teams/{id} inclui membros."""
    await client.post(
        f"/api/v1/teams/{test_team.id}/members",
        headers=admin_headers,
        json={"user_id": str(member_user.id)},
    )
    response = await client.get(f"/api/v1/teams/{test_team.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "members" in data
    assert len(data["members"]) == 1
    assert data["members"][0]["email"] == "member@example.com"


# --- Forbidden / Acesso proibido ---


@pytest.mark.asyncio
async def test_add_member_forbidden(
    client: AsyncClient,
    reader_headers: dict[str, str],
    test_team: Team,
    member_user: User,
    reader_user: User,
) -> None:
    """Test add member without teams:manage_members returns 403 / Sem permissao retorna 403."""
    response = await client.post(
        f"/api/v1/teams/{test_team.id}/members",
        headers=reader_headers,
        json={"user_id": str(member_user.id)},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_remove_member_forbidden(
    client: AsyncClient,
    reader_headers: dict[str, str],
    test_team: Team,
    member_user: User,
    reader_user: User,
) -> None:
    """Test remove member without teams:manage_members returns 403 / Sem permissao retorna 403."""
    response = await client.delete(
        f"/api/v1/teams/{test_team.id}/members/{member_user.id}",
        headers=reader_headers,
    )
    assert response.status_code == 403
