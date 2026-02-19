"""
Tests for races CRUD endpoints.
Testes para endpoints CRUD de corridas.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus
from app.races.models import Race, RaceStatus
from app.users.models import User


@pytest.fixture
async def test_championship(db_session: AsyncSession) -> Championship:
    """Create a test championship / Cria um campeonato de teste."""
    champ = Championship(
        name="formula_e_2026",
        display_name="Formula E 2026",
        description="Electric racing championship",
        season_year=2026,
        status=ChampionshipStatus.planned,
    )
    db_session.add(champ)
    await db_session.commit()
    await db_session.refresh(champ)
    return champ


@pytest.fixture
async def test_race(db_session: AsyncSession, test_championship: Championship) -> Race:
    """Create a test race / Cria uma corrida de teste."""
    race = Race(
        championship_id=test_championship.id,
        name="round_01_monza",
        display_name="Round 1 - Monza",
        description="Opening race at Monza",
        round_number=1,
        status=RaceStatus.scheduled,
        track_name="Autodromo di Monza",
        track_country="Italy",
        laps_total=30,
    )
    db_session.add(race)
    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def active_race(db_session: AsyncSession, test_championship: Championship) -> Race:
    """Create an active race / Cria uma corrida ativa."""
    race = Race(
        championship_id=test_championship.id,
        name="round_02_spa",
        display_name="Round 2 - Spa",
        round_number=2,
        status=RaceStatus.active,
        track_name="Spa-Francorchamps",
        track_country="Belgium",
    )
    db_session.add(race)
    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def finished_race(db_session: AsyncSession, test_championship: Championship) -> Race:
    """Create a finished race / Cria uma corrida finalizada."""
    race = Race(
        championship_id=test_championship.id,
        name="round_03_silverstone",
        display_name="Round 3 - Silverstone",
        round_number=3,
        status=RaceStatus.finished,
        is_active=False,
    )
    db_session.add(race)
    await db_session.commit()
    await db_session.refresh(race)
    return race


# --- List races / Listar corridas ---


@pytest.mark.asyncio
async def test_list_races_empty(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test GET /api/v1/championships/{id}/races returns empty list / Testa retorna lista vazia."""
    response = await client.get(
        f"/api/v1/championships/{test_championship.id}/races", headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_races_with_data(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test GET /api/v1/championships/{id}/races returns races / Testa retorna corridas."""
    response = await client.get(
        f"/api/v1/championships/{test_race.championship_id}/races", headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "round_01_monza"


@pytest.mark.asyncio
async def test_list_races_ordered_by_round(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race, active_race: Race
) -> None:
    """Test races are ordered by round_number / Testa ordenacao por round_number."""
    response = await client.get(
        f"/api/v1/championships/{test_race.championship_id}/races", headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["round_number"] == 1
    assert data[1]["round_number"] == 2


@pytest.mark.asyncio
async def test_list_races_filter_by_status(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race, active_race: Race
) -> None:
    """Test GET /championships/{id}/races?status=active filters correctly / Filtra por status."""
    response = await client.get(
        f"/api/v1/championships/{test_race.championship_id}/races?status=active",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "round_02_spa"


@pytest.mark.asyncio
async def test_list_races_filter_by_active(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race, finished_race: Race
) -> None:
    """Test GET /championships/{id}/races?is_active=true filters correctly / Filtra por ativo."""
    response = await client.get(
        f"/api/v1/championships/{test_race.championship_id}/races?is_active=true",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "round_01_monza"


@pytest.mark.asyncio
async def test_list_races_championship_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test GET /championships/{id}/races with invalid championship returns 404."""
    response = await client.get(
        f"/api/v1/championships/{uuid.uuid4()}/races", headers=admin_headers
    )
    assert response.status_code == 404


# --- Get race by ID / Buscar corrida por ID ---


@pytest.mark.asyncio
async def test_get_race_by_id(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test GET /api/v1/races/{id} returns race / Retorna corrida."""
    response = await client.get(f"/api/v1/races/{test_race.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "round_01_monza"
    assert data["display_name"] == "Round 1 - Monza"
    assert data["description"] == "Opening race at Monza"
    assert data["round_number"] == 1
    assert data["status"] == "scheduled"
    assert data["track_name"] == "Autodromo di Monza"
    assert data["track_country"] == "Italy"
    assert data["laps_total"] == 30


@pytest.mark.asyncio
async def test_get_race_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test GET /api/v1/races/{id} with invalid ID returns 404."""
    response = await client.get(f"/api/v1/races/{uuid.uuid4()}", headers=admin_headers)
    assert response.status_code == 404


# --- Create race / Criar corrida ---


@pytest.mark.asyncio
async def test_create_race_full(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test POST /championships/{id}/races creates with all fields / Cria com todos os campos."""
    response = await client.post(
        f"/api/v1/championships/{test_championship.id}/races",
        headers=admin_headers,
        json={
            "name": "round_01_interlagos",
            "display_name": "Round 1 - Interlagos",
            "description": "Opening race in Brazil",
            "round_number": 1,
            "status": "qualifying",
            "scheduled_at": "2026-03-15T14:00:00Z",
            "track_name": "Interlagos",
            "track_country": "Brazil",
            "laps_total": 45,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "round_01_interlagos"
    assert data["display_name"] == "Round 1 - Interlagos"
    assert data["description"] == "Opening race in Brazil"
    assert data["round_number"] == 1
    assert data["status"] == "qualifying"
    assert data["track_name"] == "Interlagos"
    assert data["track_country"] == "Brazil"
    assert data["laps_total"] == 45
    assert data["is_active"] is True
    assert data["championship_id"] == str(test_championship.id)


@pytest.mark.asyncio
async def test_create_race_minimal(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test POST /championships/{id}/races creates with required fields only / Campos obrigatorios."""
    response = await client.post(
        f"/api/v1/championships/{test_championship.id}/races",
        headers=admin_headers,
        json={
            "name": "round_01_basic",
            "display_name": "Round 1",
            "round_number": 1,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "round_01_basic"
    assert data["description"] is None
    assert data["status"] == "scheduled"
    assert data["scheduled_at"] is None
    assert data["track_name"] is None
    assert data["track_country"] is None
    assert data["laps_total"] is None


@pytest.mark.asyncio
async def test_create_race_duplicate_name(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test POST with duplicate name in same championship returns 409."""
    response = await client.post(
        f"/api/v1/championships/{test_race.championship_id}/races",
        headers=admin_headers,
        json={
            "name": "round_01_monza",
            "display_name": "Another Race",
            "round_number": 4,
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_race_championship_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test POST with invalid championship ID returns 404."""
    response = await client.post(
        f"/api/v1/championships/{uuid.uuid4()}/races",
        headers=admin_headers,
        json={
            "name": "round_01_test",
            "display_name": "Test Race",
            "round_number": 1,
        },
    )
    assert response.status_code == 404


# --- Update race / Atualizar corrida ---


@pytest.mark.asyncio
async def test_update_race_display_name(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test PATCH updates display_name / Atualiza display_name."""
    response = await client.patch(
        f"/api/v1/races/{test_race.id}",
        headers=admin_headers,
        json={"display_name": "Round 1 - Monza GP"},
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Round 1 - Monza GP"


@pytest.mark.asyncio
async def test_update_race_status(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test PATCH updates status / Atualiza status."""
    response = await client.patch(
        f"/api/v1/races/{test_race.id}",
        headers=admin_headers,
        json={"status": "active"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "active"


@pytest.mark.asyncio
async def test_update_race_deactivate(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test PATCH deactivates race / Desativa corrida."""
    response = await client.patch(
        f"/api/v1/races/{test_race.id}",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_update_race_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test PATCH with invalid ID returns 404."""
    response = await client.patch(
        f"/api/v1/races/{uuid.uuid4()}",
        headers=admin_headers,
        json={"display_name": "Nope"},
    )
    assert response.status_code == 404


# --- Delete race / Excluir corrida ---


@pytest.mark.asyncio
async def test_delete_race(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test DELETE /api/v1/races/{id} / Testa DELETE de corrida."""
    response = await client.delete(f"/api/v1/races/{test_race.id}", headers=admin_headers)
    assert response.status_code == 204

    response = await client.get(f"/api/v1/races/{test_race.id}", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_race_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test DELETE with invalid ID returns 404."""
    response = await client.delete(f"/api/v1/races/{uuid.uuid4()}", headers=admin_headers)
    assert response.status_code == 404


# --- Auth / Autenticacao ---


@pytest.mark.asyncio
async def test_list_races_unauthorized(
    client: AsyncClient, test_championship: Championship
) -> None:
    """Test GET /championships/{id}/races without token returns 401."""
    response = await client.get(f"/api/v1/championships/{test_championship.id}/races")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_race_forbidden(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    test_championship: Championship,
) -> None:
    """Test POST without races:create returns 403."""
    response = await client.post(
        f"/api/v1/championships/{test_championship.id}/races",
        headers=auth_headers,
        json={"name": "no_perms", "display_name": "No Perms", "round_number": 1},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_races(
    client: AsyncClient, admin_headers: dict[str, str], test_race: Race
) -> None:
    """Test admin with races:read can list / Admin pode listar."""
    response = await client.get(
        f"/api/v1/championships/{test_race.championship_id}/races", headers=admin_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_admin_can_create_race(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test admin with races:create can create / Admin pode criar."""
    response = await client.post(
        f"/api/v1/championships/{test_championship.id}/races",
        headers=admin_headers,
        json={"name": "admin_race", "display_name": "Admin Race", "round_number": 1},
    )
    assert response.status_code == 201
