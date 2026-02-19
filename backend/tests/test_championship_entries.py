"""
Tests for championship entries (team enrollment) endpoints.
Testes para endpoints de inscricao de equipes em campeonatos.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus
from app.teams.models import Team
from app.users.models import User


@pytest.fixture
async def test_championship(db_session: AsyncSession) -> Championship:
    """Create a test championship / Cria um campeonato de teste."""
    champ = Championship(
        name="formula_e_2026",
        display_name="Formula E 2026",
        season_year=2026,
        status=ChampionshipStatus.active,
    )
    db_session.add(champ)
    await db_session.commit()
    await db_session.refresh(champ)
    return champ


@pytest.fixture
async def test_team(db_session: AsyncSession) -> Team:
    """Create a test team / Cria uma equipe de teste."""
    team = Team(name="red_bull_racing", display_name="Red Bull Racing")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def second_team(db_session: AsyncSession) -> Team:
    """Create a second test team / Cria uma segunda equipe de teste."""
    team = Team(name="mclaren", display_name="McLaren Racing")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


# --- List entries / Listar inscricoes ---


@pytest.mark.asyncio
async def test_list_entries_empty(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test GET /entries returns empty list / Retorna lista vazia."""
    response = await client.get(
        f"/api/v1/championships/{test_championship.id}/entries", headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_entries_championship_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test GET /entries with invalid championship returns 404."""
    response = await client.get(
        f"/api/v1/championships/{uuid.uuid4()}/entries", headers=admin_headers
    )
    assert response.status_code == 404


# --- Add entry / Adicionar inscricao ---


@pytest.mark.asyncio
async def test_add_entry(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    test_team: Team,
) -> None:
    """Test POST /entries adds a team / Adiciona uma equipe."""
    response = await client.post(
        f"/api/v1/championships/{test_championship.id}/entries",
        headers=admin_headers,
        json={"team_id": str(test_team.id)},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["team_name"] == "red_bull_racing"
    assert "registered_at" in data[0]


@pytest.mark.asyncio
async def test_add_entry_duplicate(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    test_team: Team,
) -> None:
    """Test POST /entries with duplicate team returns 409."""
    await client.post(
        f"/api/v1/championships/{test_championship.id}/entries",
        headers=admin_headers,
        json={"team_id": str(test_team.id)},
    )
    response = await client.post(
        f"/api/v1/championships/{test_championship.id}/entries",
        headers=admin_headers,
        json={"team_id": str(test_team.id)},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_add_entry_team_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
) -> None:
    """Test POST /entries with invalid team returns 404."""
    response = await client.post(
        f"/api/v1/championships/{test_championship.id}/entries",
        headers=admin_headers,
        json={"team_id": str(uuid.uuid4())},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_entry_championship_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_team: Team,
) -> None:
    """Test POST /entries with invalid championship returns 404."""
    response = await client.post(
        f"/api/v1/championships/{uuid.uuid4()}/entries",
        headers=admin_headers,
        json={"team_id": str(test_team.id)},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_multiple_entries(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    test_team: Team,
    second_team: Team,
) -> None:
    """Test adding multiple teams / Adiciona multiplas equipes."""
    await client.post(
        f"/api/v1/championships/{test_championship.id}/entries",
        headers=admin_headers,
        json={"team_id": str(test_team.id)},
    )
    response = await client.post(
        f"/api/v1/championships/{test_championship.id}/entries",
        headers=admin_headers,
        json={"team_id": str(second_team.id)},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


# --- Remove entry / Remover inscricao ---


@pytest.mark.asyncio
async def test_remove_entry(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    test_team: Team,
) -> None:
    """Test DELETE /entries/{team_id} removes a team / Remove uma equipe."""
    await client.post(
        f"/api/v1/championships/{test_championship.id}/entries",
        headers=admin_headers,
        json={"team_id": str(test_team.id)},
    )
    response = await client.delete(
        f"/api/v1/championships/{test_championship.id}/entries/{test_team.id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_remove_entry_not_enrolled(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    test_team: Team,
) -> None:
    """Test DELETE /entries/{team_id} with non-enrolled team returns 404."""
    response = await client.delete(
        f"/api/v1/championships/{test_championship.id}/entries/{test_team.id}",
        headers=admin_headers,
    )
    assert response.status_code == 404


# --- Cascading delete / Exclusao em cascata ---


@pytest.mark.asyncio
async def test_delete_championship_clears_entries(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    test_team: Team,
) -> None:
    """Test DELETE championship also clears entries / DELETE campeonato limpa inscricoes."""
    await client.post(
        f"/api/v1/championships/{test_championship.id}/entries",
        headers=admin_headers,
        json={"team_id": str(test_team.id)},
    )
    response = await client.delete(
        f"/api/v1/championships/{test_championship.id}", headers=admin_headers
    )
    assert response.status_code == 204


# --- Detail includes teams / Detalhe inclui equipes ---


@pytest.mark.asyncio
async def test_get_championship_detail_includes_teams(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    test_team: Team,
) -> None:
    """Test GET /{id} includes teams list / GET /{id} inclui lista de equipes."""
    await client.post(
        f"/api/v1/championships/{test_championship.id}/entries",
        headers=admin_headers,
        json={"team_id": str(test_team.id)},
    )
    response = await client.get(
        f"/api/v1/championships/{test_championship.id}", headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["teams"]) == 1
    assert data["teams"][0]["name"] == "red_bull_racing"


# --- RBAC / Controle de acesso ---


@pytest.mark.asyncio
async def test_add_entry_forbidden(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    test_championship: Championship,
    test_team: Team,
) -> None:
    """Test POST /entries without manage_entries returns 403."""
    response = await client.post(
        f"/api/v1/championships/{test_championship.id}/entries",
        headers=auth_headers,
        json={"team_id": str(test_team.id)},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_remove_entry_forbidden(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    test_championship: Championship,
    test_team: Team,
) -> None:
    """Test DELETE /entries/{team_id} without manage_entries returns 403."""
    response = await client.delete(
        f"/api/v1/championships/{test_championship.id}/entries/{test_team.id}",
        headers=auth_headers,
    )
    assert response.status_code == 403
