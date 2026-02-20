"""
Tests for drivers CRUD endpoints.
Testes para endpoints CRUD de pilotos.
"""

import uuid
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.drivers.models import Driver
from app.teams.models import Team
from app.users.models import User


@pytest.fixture
async def test_team(db_session: AsyncSession) -> Team:
    """Create a test team / Cria uma equipe de teste."""
    team = Team(
        name="red_bull_racing",
        display_name="Red Bull Racing",
        description="A racing team",
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def second_team(db_session: AsyncSession) -> Team:
    """Create a second test team / Cria uma segunda equipe de teste."""
    team = Team(
        name="mclaren",
        display_name="McLaren Racing",
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_driver(db_session: AsyncSession, test_team: Team) -> Driver:
    """Create a test driver / Cria um piloto de teste."""
    driver = Driver(
        name="verstappen",
        display_name="Max Verstappen",
        abbreviation="VER",
        number=1,
        nationality="Dutch",
        date_of_birth=date(1997, 9, 30),
        photo_url="https://example.com/ver.png",
        team_id=test_team.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def inactive_driver(db_session: AsyncSession, test_team: Team) -> Driver:
    """Create an inactive test driver / Cria um piloto de teste inativo."""
    driver = Driver(
        name="ricciardo",
        display_name="Daniel Ricciardo",
        abbreviation="RIC",
        number=3,
        team_id=test_team.id,
        is_active=False,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def second_team_driver(db_session: AsyncSession, second_team: Team) -> Driver:
    """Create a driver in the second team / Cria um piloto na segunda equipe."""
    driver = Driver(
        name="norris",
        display_name="Lando Norris",
        abbreviation="NOR",
        number=4,
        team_id=second_team.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


# --- List drivers / Listar pilotos ---


@pytest.mark.asyncio
async def test_list_drivers_empty(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test GET /api/v1/drivers/ returns empty list / Testa GET /drivers/ retorna lista vazia."""
    response = await client.get("/api/v1/drivers/", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_drivers_with_data(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver
) -> None:
    """Test GET /api/v1/drivers/ returns drivers / Testa GET /drivers/ retorna pilotos."""
    response = await client.get("/api/v1/drivers/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "verstappen"
    assert data[0]["abbreviation"] == "VER"
    assert data[0]["number"] == 1


@pytest.mark.asyncio
async def test_list_drivers_filter_active(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver, inactive_driver: Driver
) -> None:
    """Test GET /api/v1/drivers/?is_active=true returns only active / Filtra apenas pilotos ativos."""
    response = await client.get("/api/v1/drivers/?is_active=true", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "verstappen"


@pytest.mark.asyncio
async def test_list_drivers_filter_inactive(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver, inactive_driver: Driver
) -> None:
    """Test GET /api/v1/drivers/?is_active=false returns only inactive / Filtra apenas pilotos inativos."""
    response = await client.get("/api/v1/drivers/?is_active=false", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "ricciardo"


@pytest.mark.asyncio
async def test_list_drivers_filter_team(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_driver: Driver,
    second_team_driver: Driver,
) -> None:
    """Test GET /api/v1/drivers/?team_id=... filters by team / Filtra por equipe."""
    response = await client.get(
        f"/api/v1/drivers/?team_id={test_driver.team_id}", headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "verstappen"


@pytest.mark.asyncio
async def test_list_drivers_filter_active_and_team(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_driver: Driver,
    inactive_driver: Driver,
    second_team_driver: Driver,
) -> None:
    """Test combined filters / Testa filtros combinados."""
    response = await client.get(
        f"/api/v1/drivers/?is_active=true&team_id={test_driver.team_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "verstappen"


# --- Get driver by ID / Buscar piloto por ID ---


@pytest.mark.asyncio
async def test_get_driver_by_id(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver
) -> None:
    """Test GET /api/v1/drivers/{id} returns driver with team / Testa GET retorna piloto com equipe."""
    response = await client.get(f"/api/v1/drivers/{test_driver.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "verstappen"
    assert data["display_name"] == "Max Verstappen"
    assert data["abbreviation"] == "VER"
    assert data["number"] == 1
    assert data["nationality"] == "Dutch"
    assert data["date_of_birth"] == "1997-09-30"
    assert data["photo_url"] == "https://example.com/ver.png"
    assert "team" in data
    assert data["team"]["name"] == "red_bull_racing"


@pytest.mark.asyncio
async def test_get_driver_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test GET /api/v1/drivers/{id} with invalid ID returns 404 / Testa com ID invalido retorna 404."""
    response = await client.get(f"/api/v1/drivers/{uuid.uuid4()}", headers=admin_headers)
    assert response.status_code == 404


# --- Create driver / Criar piloto ---


@pytest.mark.asyncio
async def test_create_driver_full(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test POST /api/v1/drivers/ creates driver with all fields / Testa criacao com todos os campos."""
    response = await client.post(
        "/api/v1/drivers/",
        headers=admin_headers,
        json={
            "name": "perez",
            "display_name": "Sergio Perez",
            "abbreviation": "PER",
            "number": 11,
            "nationality": "Mexican",
            "date_of_birth": "1990-01-26",
            "photo_url": "https://example.com/per.png",
            "team_id": str(test_team.id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "perez"
    assert data["display_name"] == "Sergio Perez"
    assert data["abbreviation"] == "PER"
    assert data["number"] == 11
    assert data["nationality"] == "Mexican"
    assert data["date_of_birth"] == "1990-01-26"
    assert data["photo_url"] == "https://example.com/per.png"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_driver_minimal(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test POST /api/v1/drivers/ creates driver with required fields only / Testa com campos obrigatorios."""
    response = await client.post(
        "/api/v1/drivers/",
        headers=admin_headers,
        json={
            "name": "hamilton",
            "display_name": "Lewis Hamilton",
            "abbreviation": "HAM",
            "number": 44,
            "team_id": str(test_team.id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "hamilton"
    assert data["nationality"] is None
    assert data["date_of_birth"] is None
    assert data["photo_url"] is None


@pytest.mark.asyncio
async def test_create_driver_abbreviation_uppercase(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test abbreviation is stored uppercase / Testa que abreviacao e armazenada em maiusculas."""
    response = await client.post(
        "/api/v1/drivers/",
        headers=admin_headers,
        json={
            "name": "leclerc",
            "display_name": "Charles Leclerc",
            "abbreviation": "lec",
            "number": 16,
            "team_id": str(test_team.id),
        },
    )
    assert response.status_code == 201
    assert response.json()["abbreviation"] == "LEC"


@pytest.mark.asyncio
async def test_create_driver_duplicate_name(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver, test_team: Team
) -> None:
    """Test POST with duplicate name returns 409 / Testa com nome duplicado retorna 409."""
    response = await client.post(
        "/api/v1/drivers/",
        headers=admin_headers,
        json={
            "name": "verstappen",
            "display_name": "Another Verstappen",
            "abbreviation": "AVR",
            "number": 99,
            "team_id": str(test_team.id),
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_driver_duplicate_abbreviation(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver, test_team: Team
) -> None:
    """Test POST with duplicate abbreviation returns 409 / Testa com abreviacao duplicada retorna 409."""
    response = await client.post(
        "/api/v1/drivers/",
        headers=admin_headers,
        json={
            "name": "new_driver",
            "display_name": "New Driver",
            "abbreviation": "VER",
            "number": 99,
            "team_id": str(test_team.id),
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_driver_duplicate_number_same_team(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver, test_team: Team
) -> None:
    """Test POST with duplicate number in same team returns 409 / Testa com numero duplicado na mesma equipe."""
    response = await client.post(
        "/api/v1/drivers/",
        headers=admin_headers,
        json={
            "name": "new_driver",
            "display_name": "New Driver",
            "abbreviation": "NEW",
            "number": 1,
            "team_id": str(test_team.id),
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_driver_same_number_different_team(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver, second_team: Team
) -> None:
    """Test POST with same number in different team succeeds / Mesmo numero em equipe diferente funciona."""
    response = await client.post(
        "/api/v1/drivers/",
        headers=admin_headers,
        json={
            "name": "piastri",
            "display_name": "Oscar Piastri",
            "abbreviation": "PIA",
            "number": 1,
            "team_id": str(second_team.id),
        },
    )
    assert response.status_code == 201
    assert response.json()["number"] == 1


@pytest.mark.asyncio
async def test_create_driver_team_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Test POST with nonexistent team returns 404 / Testa com equipe inexistente retorna 404."""
    response = await client.post(
        "/api/v1/drivers/",
        headers=admin_headers,
        json={
            "name": "ghost",
            "display_name": "Ghost Driver",
            "abbreviation": "GHO",
            "number": 0,
            "team_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_driver_invalid_abbreviation_length(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Test POST with invalid abbreviation returns 422 / Testa com abreviacao invalida retorna 422."""
    response = await client.post(
        "/api/v1/drivers/",
        headers=admin_headers,
        json={
            "name": "bad_abbr",
            "display_name": "Bad Abbr",
            "abbreviation": "AB",
            "number": 50,
            "team_id": str(test_team.id),
        },
    )
    assert response.status_code == 422


# --- Update driver / Atualizar piloto ---


@pytest.mark.asyncio
async def test_update_driver_display_name(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver
) -> None:
    """Test PATCH /api/v1/drivers/{id} updates display_name / Testa atualizacao de display_name."""
    response = await client.patch(
        f"/api/v1/drivers/{test_driver.id}",
        headers=admin_headers,
        json={"display_name": "Max Emilian Verstappen"},
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Max Emilian Verstappen"


@pytest.mark.asyncio
async def test_update_driver_abbreviation(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver
) -> None:
    """Test PATCH updates abbreviation / Testa atualizacao de abreviacao."""
    response = await client.patch(
        f"/api/v1/drivers/{test_driver.id}",
        headers=admin_headers,
        json={"abbreviation": "MVR"},
    )
    assert response.status_code == 200
    assert response.json()["abbreviation"] == "MVR"


@pytest.mark.asyncio
async def test_update_driver_abbreviation_conflict(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver, inactive_driver: Driver
) -> None:
    """Test PATCH with duplicate abbreviation returns 409 / Testa com abreviacao duplicada retorna 409."""
    response = await client.patch(
        f"/api/v1/drivers/{test_driver.id}",
        headers=admin_headers,
        json={"abbreviation": "RIC"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_driver_number(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver
) -> None:
    """Test PATCH updates number / Testa atualizacao de numero."""
    response = await client.patch(
        f"/api/v1/drivers/{test_driver.id}",
        headers=admin_headers,
        json={"number": 33},
    )
    assert response.status_code == 200
    assert response.json()["number"] == 33


@pytest.mark.asyncio
async def test_update_driver_number_conflict(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver, inactive_driver: Driver
) -> None:
    """Test PATCH with duplicate number in same team returns 409 / Testa numero duplicado na equipe."""
    response = await client.patch(
        f"/api/v1/drivers/{test_driver.id}",
        headers=admin_headers,
        json={"number": 3},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_driver_deactivate(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver
) -> None:
    """Test PATCH deactivates driver / Testa desativacao de piloto."""
    response = await client.patch(
        f"/api/v1/drivers/{test_driver.id}",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_update_driver_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test PATCH with invalid ID returns 404 / Testa com ID invalido retorna 404."""
    response = await client.patch(
        f"/api/v1/drivers/{uuid.uuid4()}",
        headers=admin_headers,
        json={"display_name": "Nope"},
    )
    assert response.status_code == 404


# --- Delete driver / Excluir piloto ---


@pytest.mark.asyncio
async def test_delete_driver(
    client: AsyncClient, admin_headers: dict[str, str], test_driver: Driver
) -> None:
    """Test DELETE /api/v1/drivers/{id} deletes driver / Testa DELETE de piloto."""
    response = await client.delete(f"/api/v1/drivers/{test_driver.id}", headers=admin_headers)
    assert response.status_code == 204

    response = await client.get(f"/api/v1/drivers/{test_driver.id}", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_driver_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test DELETE with invalid ID returns 404 / Testa com ID invalido retorna 404."""
    response = await client.delete(f"/api/v1/drivers/{uuid.uuid4()}", headers=admin_headers)
    assert response.status_code == 404


# --- Auth / Autenticacao ---


@pytest.mark.asyncio
async def test_list_drivers_unauthorized(client: AsyncClient) -> None:
    """Test GET /api/v1/drivers/ without token returns 401 / Testa sem token retorna 401."""
    response = await client.get("/api/v1/drivers/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_driver_forbidden(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User, test_team: Team
) -> None:
    """Test POST /api/v1/drivers/ without drivers:create returns 403 / Testa sem permissao retorna 403."""
    response = await client.post(
        "/api/v1/drivers/",
        headers=auth_headers,
        json={
            "name": "no_perms",
            "display_name": "No Perms",
            "abbreviation": "NOP",
            "number": 0,
            "team_id": str(test_team.id),
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_driver_forbidden(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User, test_driver: Driver
) -> None:
    """Test PATCH without drivers:update returns 403 / Testa sem permissao retorna 403."""
    response = await client.patch(
        f"/api/v1/drivers/{test_driver.id}",
        headers=auth_headers,
        json={"display_name": "No Perms"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_driver_forbidden(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User, test_driver: Driver
) -> None:
    """Test DELETE without drivers:delete returns 403 / Testa sem permissao retorna 403."""
    response = await client.delete(
        f"/api/v1/drivers/{test_driver.id}",
        headers=auth_headers,
    )
    assert response.status_code == 403
