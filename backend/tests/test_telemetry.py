"""
Tests for telemetry endpoints (lap times, car setups, driver comparison).
Testes para endpoints de telemetria (tempos de volta, setups de carro, comparacao de pilotos).
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus
from app.core.security import create_access_token
from app.drivers.models import Driver
from app.races.models import Race, RaceStatus
from app.roles.models import Permission, Role
from app.teams.models import Team
from app.telemetry.models import CarSetup, LapTime
from app.users.models import User


# --- Fixtures / Fixtures ---


@pytest.fixture
async def test_championship(db_session: AsyncSession) -> Championship:
    """Create a test championship / Cria um campeonato de teste."""
    champ = Championship(
        name="telemetry_champ_2026",
        display_name="Telemetry Champ 2026",
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
    team = Team(name="telemetry_team_alpha", display_name="Telemetry Alpha")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_team_b(db_session: AsyncSession) -> Team:
    """Create a second test team / Cria uma segunda equipe de teste."""
    team = Team(name="telemetry_team_beta", display_name="Telemetry Beta")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_driver(db_session: AsyncSession, test_team: Team) -> Driver:
    """Create a test driver / Cria um piloto de teste."""
    driver = Driver(
        name="tel_verstappen",
        display_name="Max Verstappen",
        abbreviation="TVR",
        number=1,
        team_id=test_team.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def test_driver_b(db_session: AsyncSession, test_team_b: Team) -> Driver:
    """Create a second test driver / Cria um segundo piloto de teste."""
    driver = Driver(
        name="tel_norris",
        display_name="Lando Norris",
        abbreviation="TNR",
        number=4,
        team_id=test_team_b.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def test_race(db_session: AsyncSession, test_championship: Championship) -> Race:
    """Create a finished test race / Cria uma corrida de teste finalizada."""
    race = Race(
        championship_id=test_championship.id,
        name="tel_round_01_monza",
        display_name="Telemetry Round 1 - Monza",
        round_number=1,
        status=RaceStatus.finished,
        track_name="Autodromo di Monza",
        laps_total=30,
    )
    db_session.add(race)
    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def test_lap(
    db_session: AsyncSession, test_race: Race, test_driver: Driver, test_team: Team
) -> LapTime:
    """Create a test lap time / Cria um tempo de volta de teste."""
    lap = LapTime(
        race_id=test_race.id,
        driver_id=test_driver.id,
        team_id=test_team.id,
        lap_number=1,
        lap_time_ms=92345,
        sector_1_ms=28000,
        sector_2_ms=34000,
        sector_3_ms=30345,
        is_valid=True,
        is_personal_best=True,
    )
    db_session.add(lap)
    await db_session.commit()
    await db_session.refresh(lap)
    return lap


@pytest.fixture
async def test_setup(
    db_session: AsyncSession, test_race: Race, test_driver: Driver, test_team: Team
) -> CarSetup:
    """Create a test car setup / Cria um setup de carro de teste."""
    setup = CarSetup(
        race_id=test_race.id,
        driver_id=test_driver.id,
        team_id=test_team.id,
        name="Monza Low Downforce",
        notes="Optimized for straights",
        front_wing=3.5,
        rear_wing=2.0,
        brake_bias=56.0,
    )
    db_session.add(setup)
    await db_session.commit()
    await db_session.refresh(setup)
    return setup


# =============================================================================
# Lap Time tests / Testes de tempo de volta
# =============================================================================


async def test_create_lap_time(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Create a single lap time / Cria um tempo de volta."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "lap_time_ms": 91234,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/laps", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["lap_number"] == 1
    assert data["lap_time_ms"] == 91234
    assert data["is_valid"] is True
    assert data["is_personal_best"] is False


async def test_create_lap_time_with_sectors(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Create a lap time with sector times / Cria tempo de volta com tempos de setor."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "lap_time_ms": 91234,
        "sector_1_ms": 28000,
        "sector_2_ms": 33234,
        "sector_3_ms": 30000,
        "is_personal_best": True,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/laps", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["sector_1_ms"] == 28000
    assert data["sector_2_ms"] == 33234
    assert data["sector_3_ms"] == 30000
    assert data["is_personal_best"] is True


async def test_create_lap_time_duplicate(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
    test_lap: LapTime,
) -> None:
    """Cannot create duplicate lap number / Nao pode criar numero de volta duplicado."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "lap_time_ms": 90000,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/laps", json=payload, headers=admin_headers)
    assert resp.status_code == 409


async def test_create_lap_time_invalid_race(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create lap time for non-existent race / Nao pode criar para corrida inexistente."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "lap_time_ms": 91234,
    }
    resp = await client.post(f"/api/v1/races/{uuid.uuid4()}/laps", json=payload, headers=admin_headers)
    assert resp.status_code == 404


async def test_bulk_create_lap_times(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Bulk create 3 lap times / Cria 3 tempos de volta em lote."""
    payload = {
        "laps": [
            {
                "driver_id": str(test_driver.id),
                "team_id": str(test_team.id),
                "lap_number": i,
                "lap_time_ms": 90000 + i * 100,
            }
            for i in range(1, 4)
        ]
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/laps/bulk", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 3


async def test_list_laps_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """List laps for empty race / Lista voltas de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/laps", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_laps_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_lap: LapTime,
) -> None:
    """List laps with data / Lista voltas com dados."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/laps", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["lap_number"] == 1
    assert data[0]["lap_time_ms"] == 92345


async def test_list_laps_filter_by_driver(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_driver_b: Driver,
    test_team: Team,
    test_team_b: Team,
) -> None:
    """List laps filtered by driver / Lista voltas filtradas por piloto."""
    lap_a = LapTime(
        race_id=test_race.id, driver_id=test_driver.id, team_id=test_team.id,
        lap_number=1, lap_time_ms=90000,
    )
    lap_b = LapTime(
        race_id=test_race.id, driver_id=test_driver_b.id, team_id=test_team_b.id,
        lap_number=1, lap_time_ms=91000,
    )
    db_session.add_all([lap_a, lap_b])
    await db_session.commit()

    resp = await client.get(
        f"/api/v1/races/{test_race.id}/laps?driver_id={test_driver.id}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["driver_id"] == str(test_driver.id)


async def test_lap_summary(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Get lap summary / Obtém resumo de voltas."""
    for i in range(1, 4):
        lap = LapTime(
            race_id=test_race.id, driver_id=test_driver.id, team_id=test_team.id,
            lap_number=i, lap_time_ms=90000 + i * 100,
            is_personal_best=(i == 1),
        )
        db_session.add(lap)
    await db_session.commit()

    resp = await client.get(f"/api/v1/races/{test_race.id}/laps/summary", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["drivers"]) == 1
    driver_summary = data["drivers"][0]
    assert driver_summary["driver_id"] == str(test_driver.id)
    assert driver_summary["fastest_lap_ms"] == 90100
    assert driver_summary["total_laps"] == 3
    assert driver_summary["personal_best_lap"] == 1
    assert data["overall_fastest"] is not None
    assert data["overall_fastest"]["lap_time_ms"] == 90100


async def test_lap_summary_empty_race(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """Summary for empty race / Resumo de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/laps/summary", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["drivers"] == []
    assert data["overall_fastest"] is None


async def test_delete_lap_time(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_lap: LapTime,
) -> None:
    """Delete a lap time / Exclui um tempo de volta."""
    resp = await client.delete(f"/api/v1/laps/{test_lap.id}", headers=admin_headers)
    assert resp.status_code == 204


async def test_delete_lap_time_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Delete non-existent lap time / Exclui tempo de volta inexistente."""
    resp = await client.delete(f"/api/v1/laps/{uuid.uuid4()}", headers=admin_headers)
    assert resp.status_code == 404


async def test_create_lap_unauthorized(
    client: AsyncClient,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create lap without auth / Nao pode criar volta sem autenticacao."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "lap_time_ms": 91234,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/laps", json=payload)
    assert resp.status_code == 401


async def test_create_lap_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create lap without permission / Nao pode criar volta sem permissao."""
    read_perm = Permission(codename="telemetry:read", module="telemetry")
    db_session.add(read_perm)
    await db_session.flush()
    reader_role = Role(name="tel_reader", display_name="Telemetry Reader", is_system=False)
    reader_role.permissions = [read_perm]
    db_session.add(reader_role)
    await db_session.flush()
    reader_user = User(email="tel_reader@example.com", hashed_password="hashed", full_name="Tel Reader")
    reader_user.roles = [reader_role]
    db_session.add(reader_user)
    await db_session.commit()
    await db_session.refresh(reader_user)
    token = create_access_token(subject=str(reader_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "lap_time_ms": 91234,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/laps", json=payload, headers=headers)
    assert resp.status_code == 403


# =============================================================================
# Car Setup tests / Testes de setup de carro
# =============================================================================


async def test_create_setup(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Create a car setup / Cria um setup de carro."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "name": "Monza Setup",
        "front_wing": 3.5,
        "rear_wing": 2.0,
        "brake_bias": 56.0,
        "notes": "Low downforce config",
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/setups", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Monza Setup"
    assert data["front_wing"] == 3.5
    assert data["brake_bias"] == 56.0
    assert data["notes"] == "Low downforce config"


async def test_list_setups_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """List setups for empty race / Lista setups de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/setups", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_setups_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_setup: CarSetup,
) -> None:
    """List setups with data / Lista setups com dados."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/setups", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Monza Low Downforce"


async def test_list_setups_filter_by_driver(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_driver_b: Driver,
    test_team: Team,
    test_team_b: Team,
) -> None:
    """List setups filtered by driver / Lista setups filtrados por piloto."""
    setup_a = CarSetup(
        race_id=test_race.id, driver_id=test_driver.id, team_id=test_team.id,
        name="Setup A",
    )
    setup_b = CarSetup(
        race_id=test_race.id, driver_id=test_driver_b.id, team_id=test_team_b.id,
        name="Setup B",
    )
    db_session.add_all([setup_a, setup_b])
    await db_session.commit()

    resp = await client.get(
        f"/api/v1/races/{test_race.id}/setups?driver_id={test_driver.id}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Setup A"


async def test_get_setup_detail(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_setup: CarSetup,
) -> None:
    """Get setup detail with driver and team / Busca detalhe do setup com piloto e equipe."""
    resp = await client.get(f"/api/v1/setups/{test_setup.id}", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Monza Low Downforce"
    assert data["driver"]["display_name"] == "Max Verstappen"
    assert data["team"]["display_name"] == "Telemetry Alpha"


async def test_update_setup_name(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_setup: CarSetup,
) -> None:
    """Update setup name / Atualiza nome do setup."""
    resp = await client.patch(
        f"/api/v1/setups/{test_setup.id}",
        json={"name": "Monza High Downforce"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Monza High Downforce"


async def test_update_setup_fields(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_setup: CarSetup,
) -> None:
    """Update setup aero fields / Atualiza campos de aerodinamica do setup."""
    resp = await client.patch(
        f"/api/v1/setups/{test_setup.id}",
        json={"front_wing": 5.0, "rear_wing": 4.5, "tire_pressure_fl": 22.5},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["front_wing"] == 5.0
    assert data["rear_wing"] == 4.5
    assert data["tire_pressure_fl"] == 22.5


async def test_delete_setup(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_setup: CarSetup,
) -> None:
    """Delete a car setup / Exclui um setup de carro."""
    resp = await client.delete(f"/api/v1/setups/{test_setup.id}", headers=admin_headers)
    assert resp.status_code == 204


async def test_delete_setup_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Delete non-existent setup / Exclui setup inexistente."""
    resp = await client.delete(f"/api/v1/setups/{uuid.uuid4()}", headers=admin_headers)
    assert resp.status_code == 404


async def test_create_setup_unauthorized(
    client: AsyncClient,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create setup without auth / Nao pode criar setup sem autenticacao."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "name": "Unauthorized Setup",
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/setups", json=payload)
    assert resp.status_code == 401


async def test_create_setup_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create setup without permission / Nao pode criar setup sem permissao."""
    read_perm = Permission(codename="telemetry:read", module="telemetry")
    db_session.add(read_perm)
    await db_session.flush()
    reader_role = Role(name="tel_setup_reader", display_name="Setup Reader", is_system=False)
    reader_role.permissions = [read_perm]
    db_session.add(reader_role)
    await db_session.flush()
    reader_user = User(email="tel_setup_reader@example.com", hashed_password="hashed", full_name="Setup Reader")
    reader_user.roles = [reader_role]
    db_session.add(reader_user)
    await db_session.commit()
    await db_session.refresh(reader_user)
    token = create_access_token(subject=str(reader_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "name": "Forbidden Setup",
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/setups", json=payload, headers=headers)
    assert resp.status_code == 403


async def test_create_setup_invalid_race(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create setup for non-existent race / Nao pode criar setup para corrida inexistente."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "name": "Bad Race Setup",
    }
    resp = await client.post(f"/api/v1/races/{uuid.uuid4()}/setups", json=payload, headers=admin_headers)
    assert resp.status_code == 404


# =============================================================================
# Compare tests / Testes de comparacao
# =============================================================================


async def test_compare_two_drivers(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_driver_b: Driver,
    test_team: Team,
    test_team_b: Team,
) -> None:
    """Compare two drivers / Compara dois pilotos."""
    for i in range(1, 4):
        db_session.add(LapTime(
            race_id=test_race.id, driver_id=test_driver.id, team_id=test_team.id,
            lap_number=i, lap_time_ms=90000 + i * 100,
        ))
        db_session.add(LapTime(
            race_id=test_race.id, driver_id=test_driver_b.id, team_id=test_team_b.id,
            lap_number=i, lap_time_ms=91000 + i * 100,
        ))
    await db_session.commit()

    driver_ids = f"{test_driver.id},{test_driver_b.id}"
    resp = await client.get(
        f"/api/v1/races/{test_race.id}/telemetry/compare?driver_ids={driver_ids}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["driver_id"] == str(test_driver.id)
    assert len(data[0]["laps"]) == 3
    assert data[1]["driver_id"] == str(test_driver_b.id)
    assert len(data[1]["laps"]) == 3


async def test_compare_empty_race(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
) -> None:
    """Compare with empty race / Compara com corrida vazia."""
    resp = await client.get(
        f"/api/v1/races/{test_race.id}/telemetry/compare?driver_ids={test_driver.id}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["laps"] == []


async def test_compare_max_three_enforced(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """Compare rejects more than 3 drivers / Comparacao rejeita mais de 3 pilotos."""
    ids = ",".join(str(uuid.uuid4()) for _ in range(4))
    resp = await client.get(
        f"/api/v1/races/{test_race.id}/telemetry/compare?driver_ids={ids}",
        headers=admin_headers,
    )
    assert resp.status_code == 400
