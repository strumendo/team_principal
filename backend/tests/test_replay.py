"""
Tests for race replay endpoints.
Testes para endpoints de replay de corrida.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus
from app.drivers.models import Driver
from app.pitstops.models import PitStop, TireCompound
from app.races.models import Race, RaceStatus
from app.replay.models import LapPosition, RaceEvent, RaceEventType
from app.results.models import RaceResult
from app.teams.models import Team
from app.telemetry.models import LapTime

# --- Fixtures / Fixtures ---


@pytest.fixture
async def test_championship(db_session: AsyncSession) -> Championship:
    """Create a test championship / Cria um campeonato de teste."""
    champ = Championship(
        name="replay_champ_2026",
        display_name="Replay Champ 2026",
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
    team = Team(name="replay_team_alpha", display_name="Replay Alpha")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_driver(db_session: AsyncSession, test_team: Team) -> Driver:
    """Create a test driver / Cria um piloto de teste."""
    driver = Driver(
        name="rep_hamilton",
        display_name="Lewis Hamilton",
        abbreviation="RHM",
        number=44,
        team_id=test_team.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def test_team_b(db_session: AsyncSession) -> Team:
    """Create a second test team / Cria uma segunda equipe de teste."""
    team = Team(name="replay_team_beta", display_name="Replay Beta")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_driver_b(db_session: AsyncSession, test_team_b: Team) -> Driver:
    """Create a second test driver / Cria um segundo piloto de teste."""
    driver = Driver(
        name="rep_norris",
        display_name="Lando Norris",
        abbreviation="RNR",
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
        name="rep_round_01_silverstone",
        display_name="Replay Round 1 - Silverstone",
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
async def test_position(db_session: AsyncSession, test_race: Race, test_driver: Driver, test_team: Team) -> LapPosition:
    """Create a test lap position / Cria uma posicao de teste."""
    position = LapPosition(
        race_id=test_race.id,
        driver_id=test_driver.id,
        team_id=test_team.id,
        lap_number=1,
        position=1,
        gap_to_leader_ms=0,
        interval_ms=0,
    )
    db_session.add(position)
    await db_session.commit()
    await db_session.refresh(position)
    return position


@pytest.fixture
async def test_event(db_session: AsyncSession, test_race: Race) -> RaceEvent:
    """Create a test race event / Cria um evento de corrida de teste."""
    event = RaceEvent(
        race_id=test_race.id,
        lap_number=1,
        event_type=RaceEventType.race_start,
        description="Race started",
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)
    return event


# =============================================================================
# LapPosition tests / Testes de posicao por volta
# =============================================================================


async def test_create_position(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Create a lap position / Cria uma posicao por volta."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "position": 3,
        "gap_to_leader_ms": 1500,
        "interval_ms": 500,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/positions", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["lap_number"] == 1
    assert data["position"] == 3
    assert data["gap_to_leader_ms"] == 1500
    assert data["interval_ms"] == 500


async def test_create_position_duplicate(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
    test_position: LapPosition,
) -> None:
    """Cannot create duplicate position / Nao pode criar posicao duplicada."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "position": 2,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/positions", json=payload, headers=admin_headers)
    assert resp.status_code == 409


async def test_create_position_invalid_race(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create position for non-existent race / Nao pode criar para corrida inexistente."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "position": 1,
    }
    resp = await client.post(f"/api/v1/races/{uuid.uuid4()}/positions", json=payload, headers=admin_headers)
    assert resp.status_code == 404


async def test_list_positions_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """List positions for empty race / Lista posicoes de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/positions", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_positions_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_position: LapPosition,
) -> None:
    """List positions with data / Lista posicoes com dados."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/positions", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["lap_number"] == 1
    assert data[0]["position"] == 1


async def test_list_positions_filter_by_driver(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
    test_driver_b: Driver,
    test_team_b: Team,
) -> None:
    """List positions filtered by driver / Lista posicoes filtradas por piloto."""
    pos_a = LapPosition(
        race_id=test_race.id,
        driver_id=test_driver.id,
        team_id=test_team.id,
        lap_number=1,
        position=1,
    )
    pos_b = LapPosition(
        race_id=test_race.id,
        driver_id=test_driver_b.id,
        team_id=test_team_b.id,
        lap_number=1,
        position=2,
    )
    db_session.add_all([pos_a, pos_b])
    await db_session.commit()

    resp = await client.get(
        f"/api/v1/races/{test_race.id}/positions?driver_id={test_driver.id}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["driver_id"] == str(test_driver.id)


async def test_update_position(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_position: LapPosition,
) -> None:
    """Update a lap position / Atualiza uma posicao por volta."""
    resp = await client.patch(
        f"/api/v1/positions/{test_position.id}",
        json={"position": 5, "gap_to_leader_ms": 3000},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["position"] == 5
    assert data["gap_to_leader_ms"] == 3000


async def test_delete_position(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_position: LapPosition,
) -> None:
    """Delete a lap position / Exclui uma posicao por volta."""
    resp = await client.delete(f"/api/v1/positions/{test_position.id}", headers=admin_headers)
    assert resp.status_code == 204


# =============================================================================
# RaceEvent tests / Testes de evento de corrida
# =============================================================================


async def test_create_event(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
) -> None:
    """Create a race event / Cria um evento de corrida."""
    payload = {
        "lap_number": 10,
        "event_type": "safety_car",
        "description": "Debris on track",
        "driver_id": str(test_driver.id),
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/events", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["lap_number"] == 10
    assert data["event_type"] == "safety_car"
    assert data["description"] == "Debris on track"


async def test_list_events_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """List events for empty race / Lista eventos de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/events", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_events_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_event: RaceEvent,
) -> None:
    """List events with data / Lista eventos com dados."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/events", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["event_type"] == "race_start"


async def test_list_events_filter_by_type(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
) -> None:
    """List events filtered by type / Lista eventos filtrados por tipo."""
    evt1 = RaceEvent(
        race_id=test_race.id,
        lap_number=1,
        event_type=RaceEventType.race_start,
    )
    evt2 = RaceEvent(
        race_id=test_race.id,
        lap_number=15,
        event_type=RaceEventType.safety_car,
        description="Crash at turn 3",
    )
    db_session.add_all([evt1, evt2])
    await db_session.commit()

    resp = await client.get(
        f"/api/v1/races/{test_race.id}/events?event_type=safety_car",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["event_type"] == "safety_car"


async def test_update_event(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_event: RaceEvent,
) -> None:
    """Update a race event / Atualiza um evento de corrida."""
    resp = await client.patch(
        f"/api/v1/events/{test_event.id}",
        json={"description": "Updated description", "lap_number": 2},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == "Updated description"
    assert data["lap_number"] == 2


async def test_delete_event(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_event: RaceEvent,
) -> None:
    """Delete a race event / Exclui um evento de corrida."""
    resp = await client.delete(f"/api/v1/events/{test_event.id}", headers=admin_headers)
    assert resp.status_code == 204


# =============================================================================
# Bulk create tests / Testes de criacao em massa
# =============================================================================


async def test_bulk_create_positions(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
    test_driver_b: Driver,
    test_team_b: Team,
) -> None:
    """Bulk create lap positions / Cria posicoes em massa."""
    payload = {
        "positions": [
            {
                "driver_id": str(test_driver.id),
                "team_id": str(test_team.id),
                "lap_number": 1,
                "position": 1,
                "gap_to_leader_ms": 0,
            },
            {
                "driver_id": str(test_driver_b.id),
                "team_id": str(test_team_b.id),
                "lap_number": 1,
                "position": 2,
                "gap_to_leader_ms": 1200,
            },
        ]
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/positions/bulk", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 2


async def test_bulk_create_positions_invalid_race(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot bulk create for non-existent race / Nao pode criar em massa para corrida inexistente."""
    payload = {
        "positions": [
            {
                "driver_id": str(test_driver.id),
                "team_id": str(test_team.id),
                "lap_number": 1,
                "position": 1,
            },
        ]
    }
    resp = await client.post(f"/api/v1/races/{uuid.uuid4()}/positions/bulk", json=payload, headers=admin_headers)
    assert resp.status_code == 404


# =============================================================================
# Analysis tests / Testes de analise
# =============================================================================


async def test_replay_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Full replay with data / Replay completo com dados."""
    pos = LapPosition(
        race_id=test_race.id,
        driver_id=test_driver.id,
        team_id=test_team.id,
        lap_number=1,
        position=1,
        gap_to_leader_ms=0,
    )
    evt = RaceEvent(
        race_id=test_race.id,
        lap_number=1,
        event_type=RaceEventType.race_start,
    )
    db_session.add_all([pos, evt])
    await db_session.commit()

    resp = await client.get(f"/api/v1/races/{test_race.id}/replay", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["race_id"] == str(test_race.id)
    assert data["total_laps"] == 52
    assert len(data["laps"]) == 1
    assert data["laps"][0]["lap_number"] == 1
    assert len(data["laps"][0]["positions"]) == 1
    assert len(data["laps"][0]["events"]) == 1


async def test_replay_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """Replay for empty race / Replay de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/replay", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["laps"] == []


async def test_stints_analysis(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Stint analysis with data / Analise de stints com dados."""
    # Create pit stop and lap times / Cria pit stop e tempos de volta
    pit = PitStop(
        race_id=test_race.id,
        driver_id=test_driver.id,
        team_id=test_team.id,
        lap_number=15,
        duration_ms=2400,
        tire_from=TireCompound.soft,
        tire_to=TireCompound.medium,
    )
    db_session.add(pit)

    for lap_num in range(1, 21):
        lap = LapTime(
            race_id=test_race.id,
            driver_id=test_driver.id,
            team_id=test_team.id,
            lap_number=lap_num,
            lap_time_ms=90000 + lap_num * 100,
        )
        db_session.add(lap)
    await db_session.commit()

    resp = await client.get(f"/api/v1/races/{test_race.id}/analysis/stints", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["race_id"] == str(test_race.id)
    assert len(data["drivers"]) == 1
    assert len(data["drivers"][0]["stints"]) == 2  # Before and after pit stop


async def test_overtakes_detection(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Overtake detection / Deteccao de ultrapassagem."""
    # Driver goes from P3 to P1 over two laps / Piloto vai de P3 a P1 em duas voltas
    pos1 = LapPosition(
        race_id=test_race.id,
        driver_id=test_driver.id,
        team_id=test_team.id,
        lap_number=1,
        position=3,
    )
    pos2 = LapPosition(
        race_id=test_race.id,
        driver_id=test_driver.id,
        team_id=test_team.id,
        lap_number=2,
        position=1,
    )
    db_session.add_all([pos1, pos2])
    await db_session.commit()

    resp = await client.get(f"/api/v1/races/{test_race.id}/analysis/overtakes", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_overtakes"] == 1
    assert data["overtakes"][0]["from_position"] == 3
    assert data["overtakes"][0]["to_position"] == 1
    assert data["overtakes"][0]["positions_gained"] == 2


async def test_summary_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_race: Race,
    test_driver: Driver,
    test_driver_b: Driver,
    test_team: Team,
    test_team_b: Team,
) -> None:
    """Race summary with data / Resumo da corrida com dados."""
    # Positions: leader change on lap 2 / Posicoes: mudanca de lider na volta 2
    db_session.add_all(
        [
            LapPosition(
                race_id=test_race.id,
                driver_id=test_driver.id,
                team_id=test_team.id,
                lap_number=1,
                position=1,
            ),
            LapPosition(
                race_id=test_race.id,
                driver_id=test_driver_b.id,
                team_id=test_team_b.id,
                lap_number=1,
                position=2,
            ),
            LapPosition(
                race_id=test_race.id,
                driver_id=test_driver_b.id,
                team_id=test_team_b.id,
                lap_number=2,
                position=1,
            ),
            LapPosition(
                race_id=test_race.id,
                driver_id=test_driver.id,
                team_id=test_team.id,
                lap_number=2,
                position=2,
            ),
        ]
    )

    # Safety car event / Evento de safety car
    db_session.add(
        RaceEvent(
            race_id=test_race.id,
            lap_number=3,
            event_type=RaceEventType.safety_car,
        )
    )

    # DNF result / Resultado DNF
    db_session.add(
        RaceResult(
            race_id=test_race.id,
            team_id=test_team.id,
            driver_id=test_driver.id,
            position=10,
            points=0,
            dnf=True,
        )
    )

    # Fastest lap / Volta mais rapida
    db_session.add(
        LapTime(
            race_id=test_race.id,
            driver_id=test_driver_b.id,
            team_id=test_team_b.id,
            lap_number=5,
            lap_time_ms=88000,
        )
    )

    await db_session.commit()

    resp = await client.get(f"/api/v1/races/{test_race.id}/analysis/summary", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_laps"] == 52
    assert data["leader_changes"] == 1
    assert data["safety_car_laps"] == 1
    assert data["dnf_count"] == 1
    assert data["fastest_lap"]["lap_time_ms"] == 88000
    assert data["total_overtakes"] >= 0


async def test_summary_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """Race summary for empty race / Resumo de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/analysis/summary", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_overtakes"] == 0
    assert data["leader_changes"] == 0
    assert data["fastest_lap"] is None


async def test_overtakes_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_race: Race,
) -> None:
    """Overtakes for empty race / Ultrapassagens de corrida vazia."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/analysis/overtakes", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_overtakes"] == 0
    assert data["overtakes"] == []


# =============================================================================
# Auth tests / Testes de autenticacao
# =============================================================================


async def test_create_position_unauthorized(
    client: AsyncClient,
    test_race: Race,
    test_driver: Driver,
    test_team: Team,
) -> None:
    """Cannot create position without auth / Nao pode criar posicao sem autenticacao."""
    payload = {
        "driver_id": str(test_driver.id),
        "team_id": str(test_team.id),
        "lap_number": 1,
        "position": 1,
    }
    resp = await client.post(f"/api/v1/races/{test_race.id}/positions", json=payload)
    assert resp.status_code == 401


async def test_list_events_unauthorized(
    client: AsyncClient,
    test_race: Race,
) -> None:
    """Cannot list events without auth / Nao pode listar eventos sem autenticacao."""
    resp = await client.get(f"/api/v1/races/{test_race.id}/events")
    assert resp.status_code == 401


async def test_position_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Position not found / Posicao nao encontrada."""
    resp = await client.get(f"/api/v1/positions/{uuid.uuid4()}", headers=admin_headers)
    assert resp.status_code == 404
