"""
Tests for teams CRUD endpoints.
Testes para endpoints CRUD de equipes.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.teams.models import Team
from app.users.models import User


@pytest.fixture
async def test_team(db_session: AsyncSession) -> Team:
    """Create a test team / Cria uma equipe de teste."""
    team = Team(
        name="red_bull_racing",
        display_name="Red Bull Racing",
        description="A racing team",
        logo_url="https://example.com/logo.png",
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def inactive_team(db_session: AsyncSession) -> Team:
    """Create an inactive test team / Cria uma equipe de teste inativa."""
    team = Team(
        name="inactive_team",
        display_name="Inactive Team",
        is_active=False,
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


# --- List teams / Listar equipes ---


@pytest.mark.asyncio
async def test_list_teams_empty(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test GET /api/v1/teams/ returns empty list / Testa GET /teams/ retorna lista vazia."""
    response = await client.get("/api/v1/teams/", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_teams_with_data(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test GET /api/v1/teams/ returns teams / Testa GET /teams/ retorna equipes."""
    response = await client.get("/api/v1/teams/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "red_bull_racing"
    assert "logo_url" not in data[0]


@pytest.mark.asyncio
async def test_list_teams_filter_active(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team, inactive_team: Team
) -> None:
    """Test GET /api/v1/teams/?is_active=true returns only active / Filtra apenas equipes ativas."""
    response = await client.get("/api/v1/teams/?is_active=true", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "red_bull_racing"


@pytest.mark.asyncio
async def test_list_teams_filter_inactive(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team, inactive_team: Team
) -> None:
    """Test GET /api/v1/teams/?is_active=false returns only inactive / Filtra apenas equipes inativas."""
    response = await client.get("/api/v1/teams/?is_active=false", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "inactive_team"


# --- Get team by ID / Buscar equipe por ID ---


@pytest.mark.asyncio
async def test_get_team_by_id(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test GET /api/v1/teams/{id} returns team / Testa GET /teams/{id} retorna equipe."""
    response = await client.get(f"/api/v1/teams/{test_team.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "red_bull_racing"
    assert data["display_name"] == "Red Bull Racing"
    assert data["logo_url"] == "https://example.com/logo.png"


@pytest.mark.asyncio
async def test_get_team_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test GET /api/v1/teams/{id} with invalid ID returns 404 / Testa com ID invalido retorna 404."""
    response = await client.get(f"/api/v1/teams/{uuid.uuid4()}", headers=admin_headers)
    assert response.status_code == 404


# --- Create team / Criar equipe ---


@pytest.mark.asyncio
async def test_create_team_full(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test POST /api/v1/teams/ creates team with all fields / Testa criacao com todos os campos."""
    response = await client.post(
        "/api/v1/teams/",
        headers=admin_headers,
        json={
            "name": "mclaren",
            "display_name": "McLaren Racing",
            "description": "Woking-based team",
            "logo_url": "https://example.com/mclaren.png",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "mclaren"
    assert data["display_name"] == "McLaren Racing"
    assert data["description"] == "Woking-based team"
    assert data["logo_url"] == "https://example.com/mclaren.png"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_team_minimal(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test POST /api/v1/teams/ creates team with required fields only / Testa criacao com campos obrigatorios."""
    response = await client.post(
        "/api/v1/teams/",
        headers=admin_headers,
        json={"name": "ferrari", "display_name": "Scuderia Ferrari"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "ferrari"
    assert data["description"] is None
    assert data["logo_url"] is None


@pytest.mark.asyncio
async def test_create_team_duplicate(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test POST /api/v1/teams/ with duplicate name returns 409 / Testa com nome duplicado retorna 409."""
    response = await client.post(
        "/api/v1/teams/",
        headers=admin_headers,
        json={"name": "red_bull_racing", "display_name": "Red Bull"},
    )
    assert response.status_code == 409


# --- Update team / Atualizar equipe ---


@pytest.mark.asyncio
async def test_update_team_display_name(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test PATCH /api/v1/teams/{id} updates display_name / Testa atualizacao de display_name."""
    response = await client.patch(
        f"/api/v1/teams/{test_team.id}",
        headers=admin_headers,
        json={"display_name": "Oracle Red Bull Racing"},
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Oracle Red Bull Racing"


@pytest.mark.asyncio
async def test_update_team_description(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test PATCH /api/v1/teams/{id} updates description / Testa atualizacao de descricao."""
    response = await client.patch(
        f"/api/v1/teams/{test_team.id}",
        headers=admin_headers,
        json={"description": "Updated description"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_team_deactivate(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test PATCH /api/v1/teams/{id} deactivates team / Testa desativacao de equipe."""
    response = await client.patch(
        f"/api/v1/teams/{test_team.id}",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_update_team_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test PATCH /api/v1/teams/{id} with invalid ID returns 404 / Testa com ID invalido retorna 404."""
    response = await client.patch(
        f"/api/v1/teams/{uuid.uuid4()}",
        headers=admin_headers,
        json={"display_name": "Nope"},
    )
    assert response.status_code == 404


# --- Delete team / Excluir equipe ---


@pytest.mark.asyncio
async def test_delete_team(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test DELETE /api/v1/teams/{id} deletes team / Testa DELETE de equipe."""
    response = await client.delete(f"/api/v1/teams/{test_team.id}", headers=admin_headers)
    assert response.status_code == 204

    response = await client.get(f"/api/v1/teams/{test_team.id}", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_team_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test DELETE /api/v1/teams/{id} with invalid ID returns 404 / Testa com ID invalido retorna 404."""
    response = await client.delete(f"/api/v1/teams/{uuid.uuid4()}", headers=admin_headers)
    assert response.status_code == 404


# --- Auth / Autenticacao ---


@pytest.mark.asyncio
async def test_list_teams_unauthorized(client: AsyncClient) -> None:
    """Test GET /api/v1/teams/ without token returns 401 / Testa sem token retorna 401."""
    response = await client.get("/api/v1/teams/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_team_forbidden(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User
) -> None:
    """Test POST /api/v1/teams/ without teams:create returns 403 / Testa sem permissao retorna 403."""
    response = await client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={"name": "no_perms", "display_name": "No Perms"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test admin with teams:read can list / Testa que admin com teams:read pode listar."""
    response = await client.get("/api/v1/teams/", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_admin_can_create(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test admin with teams:create can create / Testa que admin com teams:create pode criar."""
    response = await client.post(
        "/api/v1/teams/",
        headers=admin_headers,
        json={"name": "williams", "display_name": "Williams Racing"},
    )
    assert response.status_code == 201
