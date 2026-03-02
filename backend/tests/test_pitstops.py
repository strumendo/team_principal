"""
Tests for pit stop and race strategy endpoints.
Testes para endpoints de pit stop e estrategia de corrida.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus
from app.drivers.models import Driver
from app.pitstops.models import PitStop, RaceStrategy, TireCompound
from app.races.models import Race, RaceStatus
from app.teams.models import Team

# --- Fixtures / Fixtures ---


@pytest.fixture
async def test_championship(db_session: AsyncSession) -> Championship:
    """Create a test championship / Cria um campeonato de teste."""
    champ = Championship(
        name="pitstop_champ_2026",
        display_name="Pitstop Champ 2026",
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
    team = Team(name="pitstop_team_alpha", display_name="Pitstop Alpha")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_driver(db_session: AsyncSession, test_team: Team) -> Driver:
    """Create a test driver / Cria um piloto de teste."""
    driver = Driver(
        name="pit_hamilton",
        display_name="Lewis Hamilton",
        abbreviation="PHM",
        number=44,
        team_id=test_team.id,
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
        name="pit_round_01_silverstone",
        display_name="Pitstop Round 1 - Silverstone",
        round_number=1,
        status=RaceStatus.finished,
        track_name="Silverstone Circuit",
        laps_total=52,
    )
    db_session.add(race)
    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def test_pit_stop(
    db_session: AsyncSession, test_race: Race, test_driver: Driver, test_team: Team
) -> PitStop:
    """Create a test pit stop / Cria um pit stop de teste."""
    pit_stop = PitStop(
        race_id=test_race.id,
        driver_id=test_driver.id,
        team_id=test_team.id,
        lap_number=15,
        duration_ms=2450,
        tire_from=TireCompound.soft,
        tire_to=TireCompound.medium,
        notes="Clean stop",
    )
    db_session.add(pit_stop)
    await db_session.commit()
    await db_session.refresh(pit_stop)
    return pit_stop


@pytest.fixture
async def test_strategy(
    db_session: AsyncSession, test_race: Race, test_driver: Driver, test_team: Team
) -> RaceStrategy:
    """Create a test race strategy / Cria uma estrategia de corrida de teste."""
    strategy = RaceStrategy(
        race_id=test_race.id,
        driver_id=test_driver.id,
        team_id=test_team.id,
        name="Two Stop Medium-Hard",
        description="Start on mediums, switch to hards",
        target_stops=2,
        planned_laps="15,35",
        starting_compound=TireCompound.medium,
    )
    db_session.add(strategy)
    await db_session.commit()
    await db_session.refresh(strategy)
    return strategy


# =============================================================================
# Pit Stop tests / Testes de pit stop
# =============================================================================


async def test_create_pit_stop(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Create a pit stop / Cria um pit stop."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 15,
        "duration_ms": 2450,
        "tire_from": "soft",
        "tire_to": "medium",
        "notes": "Clean stop",
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/pitstops", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["lap_number"] == 15
    assert data["duration_ms"] == 2450
    assert data["tire_from"] == "soft"
    assert data["tire_to"] == "medium"
    assert data["notes"] == "Clean stop"


async def test_create_pit_stop_duplicate(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
    test_pit_stop: PitStop,
) -> None:
    """Cannot create duplicate pit stop / Nao pode criar pit stop duplicado."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 15,
        "duration_ms": 2500,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/pitstops", json=payload, headers=admin_headers)
    assert resp.status_code == 409


async def test_create_pit_stop_invalid_race(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create pit stop for non-existent race / Nao pode criar para corrida inexistente."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "duration_ms": 2500,
    }
    resp = await client.post(f"/api/v1/races/{uuid.uuid4()}/pitstops", json=payload, headers=admin_headers)
    assert resp.status_code == 404


async def test_list_pit_stops_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """List pit stops for empty race / Lista pit stops de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/pitstops", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_pit_stops_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_pit_stop: PitStop,
) -> None:
    """List pit stops with data / Lista pit stops com dados."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/pitstops", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["lap_number"] == 15
    assert data[0]["duration_ms"] == 2450


async def test_list_pit_stops_filter_by_driver(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """List pit stops filtered by driver / Lista pit stops filtrados por piloto."""
    # Create another driver + pit stop / Cria outro piloto + pit stop
    team_b = Team(name="pitstop_team_beta", display_name="Pitstop Beta")
    db_session.add(team_b)
    await db_session.flush()
    driver_b = Driver(
        name="pit_norris", display_name="Lando Norris", abbreviation="PNR", number=4, team_id=team_b.id
    )
    db_session.add(driver_b)
    await db_session.flush()

    pit_a = PitStop(
        race_id=test_race.id, driver_id=test_driver.id, team_id=test_team.id,
        lap_number=10, duration_ms=2400,
    )
    pit_b = PitStop(
        race_id=test_race.id, driver_id=driver_b.id, team_id=team_b.id,
        lap_number=12, duration_ms=2600,
    )
    db_session.add_all([pit_a, pit_b])
    await db_session.commit()

    resp = await client.get(
        f"/api/v1/races/{test_race.id}/pitstops?driver_id={test_driver.id}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["driver_id"] == str(test_driver.id)


async def test_get_pit_stop_detail(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_pit_stop: PitStop,
) -> None:
    """Get pit stop detail with driver and team / Busca detalhe do pit stop com piloto e equipe."""
    resp = await client.get(f"/api/v1/pitstops/{test_pit_stop.id}", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lap_number"] == 15
    assert data["driver"]["display_name"] == "Lewis Hamilton"
    assert data["team"]["display_name"] == "Pitstop Alpha"


async def test_update_pit_stop_duration(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_pit_stop: PitStop,
) -> None:
    """Update pit stop duration / Atualiza duracao do pit stop."""
    resp = await client.patch(
        f"/api/v1/pitstops/{test_pit_stop.id}",
        json={"duration_ms": 2300},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["duration_ms"] == 2300


async def test_update_pit_stop_tires(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_pit_stop: PitStop,
) -> None:
    """Update pit stop tire compounds / Atualiza compostos de pneu do pit stop."""
    resp = await client.patch(
        f"/api/v1/pitstops/{test_pit_stop.id}",
        json={"tire_from": "medium", "tire_to": "hard"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tire_from"] == "medium"
    assert data["tire_to"] == "hard"


async def test_delete_pit_stop(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_pit_stop: PitStop,
) -> None:
    """Delete a pit stop / Exclui um pit stop."""
    resp = await client.delete(f"/api/v1/pitstops/{test_pit_stop.id}", headers=admin_headers)
    assert resp.status_code == 204


async def test_delete_pit_stop_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Delete non-existent pit stop / Exclui pit stop inexistente."""
    resp = await client.delete(f"/api/v1/pitstops/{uuid.uuid4()}", headers=admin_headers)
    assert resp.status_code == 404


async def test_create_pit_stop_unauthorized(
    client: AsyncClient,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create pit stop without auth / Nao pode criar pit stop sem autenticacao."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "duration_ms": 2500,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/pitstops", json=payload)
    assert resp.status_code == 401


async def test_pit_stop_summary_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Pit stop summary with data / Resumo de pit stops com dados."""
    for lap, ms in [(15, 2400), (35, 2300), (52, 2500)]:
        pit = PitStop(
            race_id=test_race.id, driver_id=test_driver.id, team_id=test_team.id,
            lap_number=lap, duration_ms=ms,
        )
        db_session.add(pit)
    await db_session.commit()

    resp = await client.get(f"/api/v1/races/{test_race.id}/pitstops/summary", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["drivers"]) == 1
    summary = data["drivers"][0]
    assert summary["driver_id"] == str(test_driver.id)
    assert summary["total_stops"] == 3
    assert summary["fastest_pit_ms"] == 2300
    assert summary["avg_duration_ms"] == 2400


async def test_pit_stop_summary_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """Pit stop summary for empty race / Resumo de pit stops de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/pitstops/summary", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["drivers"] == []


# =============================================================================
# Race Strategy tests / Testes de estrategia de corrida
# =============================================================================


async def test_create_strategy(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Create a race strategy / Cria uma estrategia de corrida."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "name": "One Stop Soft-Hard",
        "description": "Start soft, long stint on hards",
        "target_stops": 1,
        "planned_laps": "20",
        "starting_compound": "soft",
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/strategies", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "One Stop Soft-Hard"
    assert data["target_stops"] == 1
    assert data["planned_laps"] == "20"
    assert data["starting_compound"] == "soft"
    assert data["is_active"] is True


async def test_list_strategies_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """List strategies for empty race / Lista estrategias de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/strategies", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_strategies_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_strategy: RaceStrategy,
) -> None:
    """List strategies with data / Lista estrategias com dados."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/strategies", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Two Stop Medium-Hard"


async def test_get_strategy_detail(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_strategy: RaceStrategy,
) -> None:
    """Get strategy detail with driver and team / Busca detalhe da estrategia com piloto e equipe."""
    resp = await client.get(f"/api/v1/strategies/{test_strategy.id}", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Two Stop Medium-Hard"
    assert data["driver"]["display_name"] == "Lewis Hamilton"
    assert data["team"]["display_name"] == "Pitstop Alpha"


async def test_update_strategy_name_and_stops(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_strategy: RaceStrategy,
) -> None:
    """Update strategy name and target stops / Atualiza nome e numero de paradas."""
    resp = await client.patch(
        f"/api/v1/strategies/{test_strategy.id}",
        json={"name": "Three Stop Aggressive", "target_stops": 3},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Three Stop Aggressive"
    assert data["target_stops"] == 3


async def test_update_strategy_deactivate(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_strategy: RaceStrategy,
) -> None:
    """Deactivate a strategy / Desativa uma estrategia."""
    resp = await client.patch(
        f"/api/v1/strategies/{test_strategy.id}",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_delete_strategy(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_strategy: RaceStrategy,
) -> None:
    """Delete a strategy / Exclui uma estrategia."""
    resp = await client.delete(f"/api/v1/strategies/{test_strategy.id}", headers=admin_headers)
    assert resp.status_code == 204


async def test_delete_strategy_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Delete non-existent strategy / Exclui estrategia inexistente."""
    resp = await client.delete(f"/api/v1/strategies/{uuid.uuid4()}", headers=admin_headers)
    assert resp.status_code == 404


async def test_create_strategy_unauthorized(
    client: AsyncClient,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create strategy without auth / Nao pode criar estrategia sem autenticacao."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "name": "Unauthorized Strategy",
        "target_stops": 1,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/strategies", json=payload)
    assert resp.status_code == 401


async def test_create_strategy_invalid_race(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create strategy for non-existent race / Nao pode criar para corrida inexistente."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "name": "Bad Race Strategy",
        "target_stops": 1,
    }
    resp = await client.post(f"/api/v1/races/{uuid.uuid4()}/strategies", json=payload, headers=admin_headers)
    assert resp.status_code == 404
