"""
Tests for penalties CRUD endpoints.
Testes para endpoints CRUD de penalidades.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus, championship_entries
from app.core.security import create_access_token
from app.drivers.models import Driver
from app.penalties.models import Penalty
from app.races.models import Race, RaceStatus, race_entries
from app.results.models import RaceResult
from app.roles.models import Permission, Role
from app.teams.models import Team
from app.users.models import User


@pytest.fixture
async def test_championship(db_session: AsyncSession) -> Championship:
    """Create a test championship / Cria um campeonato de teste."""
    champ = Championship(
        name="formula_e_2026",
        display_name="Formula E 2026",
        description="Electric racing championship",
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
async def test_team_b(db_session: AsyncSession) -> Team:
    """Create a second test team / Cria uma segunda equipe de teste."""
    team = Team(name="team_beta", display_name="Team Beta")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def finished_race(
    db_session: AsyncSession,
    test_championship: Championship,
    test_team: Team,
    test_team_b: Team,
) -> Race:
    """Create a finished race with teams enrolled / Cria uma corrida finalizada com equipes inscritas."""
    race = Race(
        championship_id=test_championship.id,
        name="round_01_monza",
        display_name="Round 1 - Monza",
        round_number=1,
        status=RaceStatus.finished,
        track_name="Autodromo di Monza",
        track_country="Italy",
        laps_total=30,
    )
    db_session.add(race)
    await db_session.flush()

    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=test_team.id)
    )
    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=test_team_b.id)
    )
    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=test_team.id))
    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=test_team_b.id))

    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def test_result(
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
) -> RaceResult:
    """Create a test race result / Cria um resultado de corrida de teste."""
    result = RaceResult(
        race_id=finished_race.id,
        team_id=test_team.id,
        position=1,
        points=25.0,
        laps_completed=30,
        fastest_lap=True,
    )
    db_session.add(result)
    await db_session.commit()
    await db_session.refresh(result)
    return result


@pytest.fixture
async def test_driver(db_session: AsyncSession, test_team: Team) -> Driver:
    """Create a test driver / Cria um piloto de teste."""
    driver = Driver(
        name="max_verstappen",
        display_name="Max Verstappen",
        abbreviation="VER",
        number=1,
        team_id=test_team.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def test_penalty(
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
) -> Penalty:
    """Create a test penalty / Cria uma penalidade de teste."""
    penalty = Penalty(
        race_id=finished_race.id,
        team_id=test_team.id,
        penalty_type="warning",
        reason="Track limits violation",
        points_deducted=0.0,
    )
    db_session.add(penalty)
    await db_session.commit()
    await db_session.refresh(penalty)
    return penalty


# --- List / Listar ---


async def test_list_penalties_empty(
    client: AsyncClient, admin_headers: dict[str, str], finished_race: Race
) -> None:
    """List penalties for a race with no penalties / Lista penalidades sem dados."""
    resp = await client.get(f"/api/v1/races/{finished_race.id}/penalties", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_penalties_with_data(
    client: AsyncClient, admin_headers: dict[str, str], finished_race: Race, test_penalty: Penalty
) -> None:
    """List penalties with existing data / Lista penalidades com dados existentes."""
    resp = await client.get(f"/api/v1/races/{finished_race.id}/penalties", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(test_penalty.id)
    assert data[0]["penalty_type"] == "warning"


async def test_list_penalties_race_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """List penalties for nonexistent race / Lista penalidades de corrida inexistente."""
    resp = await client.get(f"/api/v1/races/{uuid.uuid4()}/penalties", headers=admin_headers)
    assert resp.status_code == 404


# --- Create / Criar ---


async def test_create_penalty_all_fields(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
    test_driver: Driver,
    test_result: RaceResult,
) -> None:
    """Create penalty with all fields / Cria penalidade com todos os campos."""
    body = {
        "team_id": str(test_team.id),
        "driver_id": str(test_driver.id),
        "result_id": str(test_result.id),
        "penalty_type": "time_penalty",
        "reason": "Unsafe release",
        "points_deducted": 5.0,
        "time_penalty_seconds": 10,
        "lap_number": 15,
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["penalty_type"] == "time_penalty"
    assert data["reason"] == "Unsafe release"
    assert data["points_deducted"] == 5.0
    assert data["time_penalty_seconds"] == 10
    assert data["lap_number"] == 15
    assert data["is_active"] is True


async def test_create_penalty_minimal(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
) -> None:
    """Create penalty with minimal fields / Cria penalidade com campos minimos."""
    body = {
        "team_id": str(test_team.id),
        "penalty_type": "warning",
        "reason": "Track limits",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["penalty_type"] == "warning"
    assert data["points_deducted"] == 0.0
    assert data["driver_id"] is None
    assert data["result_id"] is None


async def test_create_penalty_warning_type(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
) -> None:
    """Create warning penalty / Cria penalidade de advertencia."""
    body = {"team_id": str(test_team.id), "penalty_type": "warning", "reason": "Impeding another driver"}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 201
    assert resp.json()["penalty_type"] == "warning"


async def test_create_penalty_grid_type(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
) -> None:
    """Create grid penalty / Cria penalidade de grid."""
    body = {"team_id": str(test_team.id), "penalty_type": "grid_penalty", "reason": "Engine change"}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 201
    assert resp.json()["penalty_type"] == "grid_penalty"


async def test_create_penalty_points_deduction_type(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
) -> None:
    """Create points deduction penalty / Cria penalidade de deducao de pontos."""
    body = {
        "team_id": str(test_team.id),
        "penalty_type": "points_deduction",
        "reason": "Budget cap breach",
        "points_deducted": 25.0,
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["penalty_type"] == "points_deduction"
    assert data["points_deducted"] == 25.0


async def test_create_penalty_race_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_team: Team,
) -> None:
    """Create penalty for nonexistent race / Cria penalidade para corrida inexistente."""
    body = {"team_id": str(test_team.id), "penalty_type": "warning", "reason": "Track limits"}
    resp = await client.post(f"/api/v1/races/{uuid.uuid4()}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 404


async def test_create_penalty_team_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
) -> None:
    """Create penalty for nonexistent team / Cria penalidade para equipe inexistente."""
    body = {"team_id": str(uuid.uuid4()), "penalty_type": "warning", "reason": "Track limits"}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 404


async def test_create_penalty_driver_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
) -> None:
    """Create penalty for nonexistent driver / Cria penalidade para piloto inexistente."""
    body = {
        "team_id": str(test_team.id),
        "driver_id": str(uuid.uuid4()),
        "penalty_type": "warning",
        "reason": "Track limits",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 404


async def test_create_penalty_result_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
) -> None:
    """Create penalty for nonexistent result / Cria penalidade para resultado inexistente."""
    body = {
        "team_id": str(test_team.id),
        "result_id": str(uuid.uuid4()),
        "penalty_type": "warning",
        "reason": "Track limits",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 404


async def test_create_penalty_result_wrong_race(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    test_team: Team,
    finished_race: Race,
) -> None:
    """Create penalty with result from different race / Cria penalidade com resultado de outra corrida."""
    # Create another race with result / Cria outra corrida com resultado
    race2 = Race(
        championship_id=test_championship.id,
        name="round_02_spa",
        display_name="Round 2 - Spa",
        round_number=2,
        status=RaceStatus.finished,
    )
    db_session.add(race2)
    await db_session.flush()
    await db_session.execute(race_entries.insert().values(race_id=race2.id, team_id=test_team.id))
    result2 = RaceResult(race_id=race2.id, team_id=test_team.id, position=1, points=25.0)
    db_session.add(result2)
    await db_session.commit()
    await db_session.refresh(result2)

    body = {
        "team_id": str(test_team.id),
        "result_id": str(result2.id),
        "penalty_type": "warning",
        "reason": "Track limits",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 409


async def test_create_penalty_invalid_type(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
) -> None:
    """Create penalty with invalid type / Cria penalidade com tipo invalido."""
    body = {"team_id": str(test_team.id), "penalty_type": "invalid_type", "reason": "Track limits"}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 422


# --- Get / Buscar ---


async def test_get_penalty_by_id(
    client: AsyncClient, admin_headers: dict[str, str], test_penalty: Penalty
) -> None:
    """Get penalty by ID / Busca penalidade por ID."""
    resp = await client.get(f"/api/v1/penalties/{test_penalty.id}", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(test_penalty.id)
    assert data["penalty_type"] == "warning"
    assert "team" in data


async def test_get_penalty_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Get nonexistent penalty / Busca penalidade inexistente."""
    resp = await client.get(f"/api/v1/penalties/{uuid.uuid4()}", headers=admin_headers)
    assert resp.status_code == 404


# --- Update / Atualizar ---


async def test_update_penalty_reason(
    client: AsyncClient, admin_headers: dict[str, str], test_penalty: Penalty
) -> None:
    """Update penalty reason / Atualiza razao da penalidade."""
    resp = await client.patch(
        f"/api/v1/penalties/{test_penalty.id}",
        json={"reason": "Updated reason"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["reason"] == "Updated reason"


async def test_update_penalty_points(
    client: AsyncClient, admin_headers: dict[str, str], test_penalty: Penalty
) -> None:
    """Update penalty points / Atualiza pontos da penalidade."""
    resp = await client.patch(
        f"/api/v1/penalties/{test_penalty.id}",
        json={"points_deducted": 10.0},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["points_deducted"] == 10.0


async def test_update_penalty_deactivate(
    client: AsyncClient, admin_headers: dict[str, str], test_penalty: Penalty
) -> None:
    """Deactivate penalty / Desativa penalidade."""
    resp = await client.patch(
        f"/api/v1/penalties/{test_penalty.id}",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_update_penalty_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Update nonexistent penalty / Atualiza penalidade inexistente."""
    resp = await client.patch(
        f"/api/v1/penalties/{uuid.uuid4()}",
        json={"reason": "Updated"},
        headers=admin_headers,
    )
    assert resp.status_code == 404


# --- Delete / Excluir ---


async def test_delete_penalty(
    client: AsyncClient, admin_headers: dict[str, str], test_penalty: Penalty
) -> None:
    """Delete penalty / Exclui penalidade."""
    resp = await client.delete(f"/api/v1/penalties/{test_penalty.id}", headers=admin_headers)
    assert resp.status_code == 204

    # Confirm deletion / Confirma exclusao
    resp2 = await client.get(f"/api/v1/penalties/{test_penalty.id}", headers=admin_headers)
    assert resp2.status_code == 404


async def test_delete_penalty_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Delete nonexistent penalty / Exclui penalidade inexistente."""
    resp = await client.delete(f"/api/v1/penalties/{uuid.uuid4()}", headers=admin_headers)
    assert resp.status_code == 404


# --- Auth / Autenticacao ---


async def test_list_penalties_unauthorized(
    client: AsyncClient, finished_race: Race
) -> None:
    """List penalties without auth / Lista penalidades sem autenticacao."""
    resp = await client.get(f"/api/v1/races/{finished_race.id}/penalties")
    assert resp.status_code == 401


async def test_create_penalty_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
) -> None:
    """Create penalty without permission / Cria penalidade sem permissao."""
    # Create user with only penalties:read / Cria usuario com apenas penalties:read
    read_perm = Permission(codename="penalties:read", module="penalties")
    db_session.add(read_perm)
    await db_session.flush()
    role = Role(name="reader", display_name="Reader")
    role.permissions = [read_perm]
    db_session.add(role)
    await db_session.flush()
    user = User(
        email="reader@example.com",
        hashed_password="hashed",
        full_name="Reader",
    )
    user.roles = [role]
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token(subject=str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    body = {"team_id": str(test_team.id), "penalty_type": "warning", "reason": "Test"}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=headers)
    assert resp.status_code == 403
