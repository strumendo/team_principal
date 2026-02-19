"""
Tests for race results CRUD endpoints.
Testes para endpoints CRUD de resultados de corrida.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus, championship_entries
from app.core.security import create_access_token
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
    team = Team(
        name="team_alpha",
        display_name="Team Alpha",
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_team_b(db_session: AsyncSession) -> Team:
    """Create a second test team / Cria uma segunda equipe de teste."""
    team = Team(
        name="team_beta",
        display_name="Team Beta",
    )
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

    # Enroll teams in championship / Inscreve equipes no campeonato
    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=test_team.id)
    )
    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=test_team_b.id)
    )

    # Enroll teams in race / Inscreve equipes na corrida
    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=test_team.id))
    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=test_team_b.id))

    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def scheduled_race(db_session: AsyncSession, test_championship: Championship) -> Race:
    """Create a scheduled (not finished) race / Cria uma corrida agendada (nao finalizada)."""
    race = Race(
        championship_id=test_championship.id,
        name="round_02_spa",
        display_name="Round 2 - Spa",
        round_number=2,
        status=RaceStatus.scheduled,
    )
    db_session.add(race)
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


# --- List / Listar ---


async def test_list_race_results_empty(
    client: AsyncClient, admin_headers: dict[str, str], finished_race: Race
) -> None:
    """List results for a race with no results / Lista resultados de uma corrida sem resultados."""
    resp = await client.get(f"/api/v1/races/{finished_race.id}/results", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_race_results_with_data(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_result: RaceResult,
) -> None:
    """List results for a race with data / Lista resultados com dados."""
    resp = await client.get(f"/api/v1/races/{finished_race.id}/results", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["position"] == 1
    assert data[0]["points"] == 25.0


async def test_list_race_results_ordered_by_position(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
    test_team_b: Team,
) -> None:
    """List results ordered by position / Lista resultados ordenados por posicao."""
    r1 = RaceResult(race_id=finished_race.id, team_id=test_team_b.id, position=2, points=18.0)
    r2 = RaceResult(race_id=finished_race.id, team_id=test_team.id, position=1, points=25.0)
    db_session.add_all([r1, r2])
    await db_session.commit()

    resp = await client.get(f"/api/v1/races/{finished_race.id}/results", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["position"] == 1
    assert data[1]["position"] == 2


async def test_list_race_results_race_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """List results for a non-existent race / Lista resultados de corrida inexistente."""
    resp = await client.get(f"/api/v1/races/{uuid.uuid4()}/results", headers=admin_headers)
    assert resp.status_code == 404


# --- Create / Criar ---


async def test_create_result_success(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
) -> None:
    """Create a result with all fields / Cria um resultado com todos os campos."""
    payload = {
        "team_id": str(test_team.id),
        "position": 1,
        "points": 25.0,
        "laps_completed": 30,
        "fastest_lap": True,
        "dnf": False,
        "dsq": False,
        "notes": "Great race performance",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/results", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["position"] == 1
    assert data["points"] == 25.0
    assert data["fastest_lap"] is True
    assert data["notes"] == "Great race performance"


async def test_create_result_minimal_fields(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
) -> None:
    """Create a result with minimal required fields / Cria um resultado com campos minimos."""
    payload = {
        "team_id": str(test_team.id),
        "position": 1,
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/results", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["points"] == 0.0
    assert data["fastest_lap"] is False
    assert data["dnf"] is False
    assert data["dsq"] is False
    assert data["laps_completed"] is None
    assert data["notes"] is None


async def test_create_result_race_not_finished(
    client: AsyncClient,
    admin_headers: dict[str, str],
    scheduled_race: Race,
    test_team: Team,
) -> None:
    """Cannot create result for unfinished race / Nao pode criar resultado para corrida nao finalizada."""
    payload = {"team_id": str(test_team.id), "position": 1}
    resp = await client.post(f"/api/v1/races/{scheduled_race.id}/results", json=payload, headers=admin_headers)
    assert resp.status_code == 409


async def test_create_result_team_not_enrolled(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    finished_race: Race,
) -> None:
    """Cannot create result for unenrolled team / Nao pode criar resultado para equipe nao inscrita."""
    unenrolled_team = Team(name="team_gamma", display_name="Team Gamma")
    db_session.add(unenrolled_team)
    await db_session.commit()
    await db_session.refresh(unenrolled_team)

    payload = {"team_id": str(unenrolled_team.id), "position": 1}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/results", json=payload, headers=admin_headers)
    assert resp.status_code == 409


async def test_create_result_duplicate_team(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
    test_result: RaceResult,
) -> None:
    """Cannot create duplicate result for same team / Nao pode criar resultado duplicado para mesma equipe."""
    payload = {"team_id": str(test_team.id), "position": 2}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/results", json=payload, headers=admin_headers)
    assert resp.status_code == 409


async def test_create_result_duplicate_position_non_dsq(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
    test_team_b: Team,
    test_result: RaceResult,
) -> None:
    """Cannot have same position for two non-DSQ results / Nao pode ter mesma posicao para dois nao-DSQ."""
    payload = {"team_id": str(test_team_b.id), "position": 1, "points": 25.0}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/results", json=payload, headers=admin_headers)
    assert resp.status_code == 409


async def test_create_result_dsq_allows_duplicate_position(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
    test_team_b: Team,
    test_result: RaceResult,
) -> None:
    """DSQ result can share position with non-DSQ / Resultado DSQ pode compartilhar posicao com nao-DSQ."""
    payload = {"team_id": str(test_team_b.id), "position": 1, "dsq": True}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/results", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    assert resp.json()["dsq"] is True


async def test_create_result_race_not_found(
    client: AsyncClient, admin_headers: dict[str, str], test_team: Team
) -> None:
    """Cannot create result for non-existent race / Nao pode criar resultado para corrida inexistente."""
    payload = {"team_id": str(test_team.id), "position": 1}
    resp = await client.post(f"/api/v1/races/{uuid.uuid4()}/results", json=payload, headers=admin_headers)
    assert resp.status_code == 404


async def test_create_result_team_not_found(
    client: AsyncClient, admin_headers: dict[str, str], finished_race: Race
) -> None:
    """Cannot create result for non-existent team / Nao pode criar resultado para equipe inexistente."""
    payload = {"team_id": str(uuid.uuid4()), "position": 1}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/results", json=payload, headers=admin_headers)
    assert resp.status_code == 404


# --- Get / Buscar ---


async def test_get_result_by_id(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_result: RaceResult,
    test_team: Team,
) -> None:
    """Get a result by ID with team detail / Busca resultado por ID com detalhe da equipe."""
    resp = await client.get(f"/api/v1/results/{test_result.id}", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["position"] == 1
    assert data["team"]["name"] == "team_alpha"
    assert data["team"]["display_name"] == "Team Alpha"


async def test_get_result_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Get a non-existent result / Busca resultado inexistente."""
    resp = await client.get(f"/api/v1/results/{uuid.uuid4()}", headers=admin_headers)
    assert resp.status_code == 404


# --- Update / Atualizar ---


async def test_update_result_points(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_result: RaceResult,
) -> None:
    """Update result points / Atualiza pontos do resultado."""
    resp = await client.patch(
        f"/api/v1/results/{test_result.id}",
        json={"points": 30.0, "notes": "Bonus point for fastest lap"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["points"] == 30.0
    assert data["notes"] == "Bonus point for fastest lap"


async def test_update_result_position_conflict(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
    test_team_b: Team,
    test_result: RaceResult,
) -> None:
    """Cannot update to position taken by another non-DSQ / Nao pode atualizar para posicao ocupada."""
    r2 = RaceResult(race_id=finished_race.id, team_id=test_team_b.id, position=2, points=18.0)
    db_session.add(r2)
    await db_session.commit()
    await db_session.refresh(r2)

    resp = await client.patch(
        f"/api/v1/results/{r2.id}",
        json={"position": 1},
        headers=admin_headers,
    )
    assert resp.status_code == 409


async def test_update_result_dsq_bypasses_position_check(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
    test_team_b: Team,
    test_result: RaceResult,
) -> None:
    """DSQ result can update to taken position / Resultado DSQ pode atualizar para posicao ocupada."""
    r2 = RaceResult(race_id=finished_race.id, team_id=test_team_b.id, position=2, points=0.0, dsq=True)
    db_session.add(r2)
    await db_session.commit()
    await db_session.refresh(r2)

    resp = await client.patch(
        f"/api/v1/results/{r2.id}",
        json={"position": 1},
        headers=admin_headers,
    )
    assert resp.status_code == 200


async def test_update_result_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Update a non-existent result / Atualiza resultado inexistente."""
    resp = await client.patch(f"/api/v1/results/{uuid.uuid4()}", json={"points": 10.0}, headers=admin_headers)
    assert resp.status_code == 404


# --- Delete / Excluir ---


async def test_delete_result(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_result: RaceResult,
) -> None:
    """Delete a result / Exclui um resultado."""
    resp = await client.delete(f"/api/v1/results/{test_result.id}", headers=admin_headers)
    assert resp.status_code == 204

    # Confirm deletion / Confirma exclusao
    resp = await client.get(f"/api/v1/results/{test_result.id}", headers=admin_headers)
    assert resp.status_code == 404


async def test_delete_result_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Delete a non-existent result / Exclui resultado inexistente."""
    resp = await client.delete(f"/api/v1/results/{uuid.uuid4()}", headers=admin_headers)
    assert resp.status_code == 404


# --- Auth / Autenticacao ---


async def test_create_result_unauthorized(
    client: AsyncClient, finished_race: Race, test_team: Team
) -> None:
    """Cannot create result without auth / Nao pode criar resultado sem autenticacao."""
    payload = {"team_id": str(test_team.id), "position": 1}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/results", json=payload)
    assert resp.status_code == 401


async def test_create_result_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
) -> None:
    """Cannot create result without permission / Nao pode criar resultado sem permissao."""
    # Create a user with only results:read / Cria usuario com apenas results:read
    read_perm = Permission(codename="results:read", module="results")
    db_session.add(read_perm)
    await db_session.flush()

    reader_role = Role(name="reader", display_name="Reader", is_system=False)
    reader_role.permissions = [read_perm]
    db_session.add(reader_role)
    await db_session.flush()

    reader_user = User(
        email="reader@example.com",
        hashed_password="hashed",
        full_name="Reader User",
    )
    reader_user.roles = [reader_role]
    db_session.add(reader_user)
    await db_session.commit()
    await db_session.refresh(reader_user)

    token = create_access_token(subject=str(reader_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"team_id": str(test_team.id), "position": 1}
    resp = await client.post(f"/api/v1/races/{finished_race.id}/results", json=payload, headers=headers)
    assert resp.status_code == 403
