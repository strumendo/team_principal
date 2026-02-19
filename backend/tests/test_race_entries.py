"""
Tests for race entries (team enrollment per race) endpoints.
Testes para endpoints de inscricao de equipes por corrida.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus, championship_entries
from app.races.models import Race, RaceStatus
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
    team = Team(name="team_alpha", display_name="Team Alpha")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def second_team(db_session: AsyncSession) -> Team:
    """Create a second test team / Cria uma segunda equipe de teste."""
    team = Team(name="team_beta", display_name="Team Beta")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def enrolled_team(
    db_session: AsyncSession, test_championship: Championship, test_team: Team
) -> Team:
    """Create a team enrolled in the championship / Cria equipe inscrita no campeonato."""
    await db_session.execute(
        championship_entries.insert().values(
            championship_id=test_championship.id, team_id=test_team.id
        )
    )
    await db_session.commit()
    return test_team


@pytest.fixture
async def test_race(db_session: AsyncSession, test_championship: Championship) -> Race:
    """Create a test race / Cria uma corrida de teste."""
    race = Race(
        championship_id=test_championship.id,
        name="round_01_monza",
        display_name="Round 1 - Monza",
        round_number=1,
        status=RaceStatus.scheduled,
    )
    db_session.add(race)
    await db_session.commit()
    await db_session.refresh(race)
    return race


# --- List race entries / Listar inscricoes de corrida ---


@pytest.mark.asyncio
async def test_list_race_entries_empty(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test GET /api/v1/races/{id}/entries returns empty list / Retorna lista vazia."""
    response = await client.get(f"/api/v1/races/{test_race.id}/entries", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_race_entries_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    enrolled_team: Team,
    db_session: AsyncSession,
) -> None:
    """Test GET /api/v1/races/{id}/entries returns entries / Retorna inscricoes."""
    from app.races.models import race_entries

    await db_session.execute(
        race_entries.insert().values(race_id=test_race.id, team_id=enrolled_team.id)
    )
    await db_session.commit()

    response = await client.get(f"/api/v1/races/{test_race.id}/entries", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["team_name"] == "team_alpha"
    assert "registered_at" in data[0]


@pytest.mark.asyncio
async def test_list_race_entries_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test GET /api/v1/races/{id}/entries with invalid race returns 404."""
    response = await client.get(f"/api/v1/races/{uuid.uuid4()}/entries", headers=admin_headers)
    assert response.status_code == 404


# --- Add race entry / Adicionar inscricao de corrida ---


@pytest.mark.asyncio
async def test_add_race_entry(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    enrolled_team: Team,
) -> None:
    """Test POST /api/v1/races/{id}/entries adds team / Adiciona equipe."""
    response = await client.post(
        f"/api/v1/races/{test_race.id}/entries",
        headers=admin_headers,
        json={"team_id": str(enrolled_team.id)},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["team_name"] == "team_alpha"


@pytest.mark.asyncio
async def test_add_race_entry_team_not_in_championship(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_team: Team,
) -> None:
    """Test POST returns 409 when team not enrolled in championship / Equipe nao inscrita no campeonato."""
    response = await client.post(
        f"/api/v1/races/{test_race.id}/entries",
        headers=admin_headers,
        json={"team_id": str(test_team.id)},
    )
    assert response.status_code == 409
    assert "not enrolled in this championship" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_race_entry_duplicate(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    enrolled_team: Team,
) -> None:
    """Test POST returns 409 when team already enrolled / Equipe ja inscrita."""
    # First add
    await client.post(
        f"/api/v1/races/{test_race.id}/entries",
        headers=admin_headers,
        json={"team_id": str(enrolled_team.id)},
    )
    # Duplicate
    response = await client.post(
        f"/api/v1/races/{test_race.id}/entries",
        headers=admin_headers,
        json={"team_id": str(enrolled_team.id)},
    )
    assert response.status_code == 409
    assert "already enrolled" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_race_entry_race_not_found(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test POST with invalid race returns 404."""
    response = await client.post(
        f"/api/v1/races/{uuid.uuid4()}/entries",
        headers=admin_headers,
        json={"team_id": str(test_team.id)},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_race_entry_team_not_found(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test POST with invalid team returns 404."""
    response = await client.post(
        f"/api/v1/races/{test_race.id}/entries",
        headers=admin_headers,
        json={"team_id": str(uuid.uuid4())},
    )
    assert response.status_code == 404


# --- Remove race entry / Remover inscricao de corrida ---


@pytest.mark.asyncio
async def test_remove_race_entry(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    enrolled_team: Team,
) -> None:
    """Test DELETE /api/v1/races/{id}/entries/{team_id} removes team / Remove equipe."""
    # Add first
    await client.post(
        f"/api/v1/races/{test_race.id}/entries",
        headers=admin_headers,
        json={"team_id": str(enrolled_team.id)},
    )
    # Remove
    response = await client.delete(
        f"/api/v1/races/{test_race.id}/entries/{enrolled_team.id}", headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_remove_race_entry_not_found(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test DELETE with non-enrolled team returns 404."""
    response = await client.delete(
        f"/api/v1/races/{test_race.id}/entries/{uuid.uuid4()}", headers=admin_headers
    )
    assert response.status_code == 404


# --- Auth / Autenticacao ---


@pytest.mark.asyncio
async def test_list_race_entries_unauthorized(
    client: AsyncClient, test_race: Race
) -> None:
    """Test GET /races/{id}/entries without token returns 401."""
    response = await client.get(f"/api/v1/races/{test_race.id}/entries")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_race_entry_forbidden(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    test_race: Race,
    enrolled_team: Team,
) -> None:
    """Test POST without races:manage_entries returns 403."""
    response = await client.post(
        f"/api/v1/races/{test_race.id}/entries",
        headers=auth_headers,
        json={"team_id": str(enrolled_team.id)},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_race_detail_includes_teams(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    enrolled_team: Team,
) -> None:
    """Test GET /api/v1/races/{id} includes teams list / Inclui lista de equipes."""
    # Add team to race
    await client.post(
        f"/api/v1/races/{test_race.id}/entries",
        headers=admin_headers,
        json={"team_id": str(enrolled_team.id)},
    )
    # Get race detail
    response = await client.get(f"/api/v1/races/{test_race.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "teams" in data
    assert len(data["teams"]) == 1
    assert data["teams"][0]["name"] == "team_alpha"
