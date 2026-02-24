"""
Tests for penalty DSQ synchronization.
Testes para sincronizacao DSQ de penalidades.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus, championship_entries
from app.penalties.models import Penalty
from app.races.models import Race, RaceStatus, race_entries
from app.results.models import RaceResult
from app.teams.models import Team


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
async def finished_race(
    db_session: AsyncSession,
    test_championship: Championship,
    test_team: Team,
) -> Race:
    """Create a finished race with team enrolled / Cria uma corrida finalizada com equipe inscrita."""
    race = Race(
        championship_id=test_championship.id,
        name="round_01_monza",
        display_name="Round 1 - Monza",
        round_number=1,
        status=RaceStatus.finished,
    )
    db_session.add(race)
    await db_session.flush()
    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=test_team.id)
    )
    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=test_team.id))
    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def test_result(
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
) -> RaceResult:
    """Create a test result (dsq=False) / Cria um resultado de teste (dsq=False)."""
    result = RaceResult(
        race_id=finished_race.id,
        team_id=test_team.id,
        position=1,
        points=25.0,
    )
    db_session.add(result)
    await db_session.commit()
    await db_session.refresh(result)
    return result


# --- DSQ Sync Tests / Testes de Sincronizacao DSQ ---


async def test_create_dsq_penalty_sets_result_dsq(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
    test_result: RaceResult,
) -> None:
    """Creating a DSQ penalty sets result.dsq=True / Criar penalidade DSQ define result.dsq=True."""
    body = {
        "team_id": str(test_team.id),
        "result_id": str(test_result.id),
        "penalty_type": "disqualification",
        "reason": "Failed technical inspection",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 201

    # Verify result.dsq is now True / Verifica que result.dsq agora e True
    await db_session.refresh(test_result)
    assert test_result.dsq is True


async def test_create_dsq_penalty_without_result(
    client: AsyncClient,
    admin_headers: dict[str, str],
    finished_race: Race,
    test_team: Team,
) -> None:
    """Creating a DSQ penalty without result_id does not crash / Criar DSQ sem result_id nao causa erro."""
    body = {
        "team_id": str(test_team.id),
        "penalty_type": "disqualification",
        "reason": "Failed technical inspection",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 201


async def test_delete_dsq_penalty_reverts_result(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
    test_result: RaceResult,
) -> None:
    """Deleting a DSQ penalty reverts result.dsq / Excluir penalidade DSQ reverte result.dsq."""
    # Create DSQ penalty / Cria penalidade DSQ
    body = {
        "team_id": str(test_team.id),
        "result_id": str(test_result.id),
        "penalty_type": "disqualification",
        "reason": "Failed inspection",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    penalty_id = resp.json()["id"]

    # Delete it / Exclui
    resp2 = await client.delete(f"/api/v1/penalties/{penalty_id}", headers=admin_headers)
    assert resp2.status_code == 204

    # Verify result.dsq reverted / Verifica que result.dsq reverteu
    await db_session.refresh(test_result)
    assert test_result.dsq is False


async def test_delete_dsq_keeps_dsq_when_other_exists(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
    test_result: RaceResult,
) -> None:
    """Deleting DSQ penalty keeps dsq=True when another DSQ exists / Manter dsq=True quando outra DSQ existe."""
    # Create two DSQ penalties / Cria duas penalidades DSQ
    body1 = {
        "team_id": str(test_team.id),
        "result_id": str(test_result.id),
        "penalty_type": "disqualification",
        "reason": "Failed inspection 1",
    }
    body2 = {
        "team_id": str(test_team.id),
        "result_id": str(test_result.id),
        "penalty_type": "disqualification",
        "reason": "Failed inspection 2",
    }
    resp1 = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body1, headers=admin_headers)
    await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body2, headers=admin_headers)
    penalty1_id = resp1.json()["id"]

    # Delete first DSQ / Exclui primeira DSQ
    await client.delete(f"/api/v1/penalties/{penalty1_id}", headers=admin_headers)

    # Result should still be DSQ (second penalty) / Resultado ainda deve ser DSQ
    await db_session.refresh(test_result)
    assert test_result.dsq is True


async def test_update_type_to_dsq_sets_result(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
    test_result: RaceResult,
) -> None:
    """Updating type to DSQ sets result.dsq / Atualizar tipo para DSQ define result.dsq."""
    # Create a warning penalty with result / Cria penalidade de advertencia com resultado
    body = {
        "team_id": str(test_team.id),
        "result_id": str(test_result.id),
        "penalty_type": "warning",
        "reason": "Initial warning",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    penalty_id = resp.json()["id"]

    # Update to DSQ / Atualiza para DSQ
    resp2 = await client.patch(
        f"/api/v1/penalties/{penalty_id}",
        json={"penalty_type": "disqualification"},
        headers=admin_headers,
    )
    assert resp2.status_code == 200

    await db_session.refresh(test_result)
    assert test_result.dsq is True


async def test_update_type_from_dsq_reverts_result(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
    test_result: RaceResult,
) -> None:
    """Updating type from DSQ reverts result.dsq / Atualizar tipo de DSQ reverte result.dsq."""
    # Create DSQ penalty / Cria penalidade DSQ
    body = {
        "team_id": str(test_team.id),
        "result_id": str(test_result.id),
        "penalty_type": "disqualification",
        "reason": "Failed inspection",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    penalty_id = resp.json()["id"]

    # Update to warning / Atualiza para advertencia
    resp2 = await client.patch(
        f"/api/v1/penalties/{penalty_id}",
        json={"penalty_type": "warning"},
        headers=admin_headers,
    )
    assert resp2.status_code == 200

    await db_session.refresh(test_result)
    assert test_result.dsq is False


async def test_non_dsq_penalty_no_dsq_effect(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
    test_result: RaceResult,
) -> None:
    """Non-DSQ penalty does not affect result.dsq / Penalidade nao-DSQ nao afeta result.dsq."""
    body = {
        "team_id": str(test_team.id),
        "result_id": str(test_result.id),
        "penalty_type": "time_penalty",
        "reason": "Speeding in pit lane",
        "time_penalty_seconds": 5,
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    assert resp.status_code == 201

    await db_session.refresh(test_result)
    assert test_result.dsq is False


async def test_inactive_dsq_penalty_no_dsq_sync(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    finished_race: Race,
    test_team: Team,
    test_result: RaceResult,
) -> None:
    """Creating DSQ then deactivating reverts dsq / Criar DSQ e desativar reverte dsq."""
    # Create DSQ penalty / Cria penalidade DSQ
    body = {
        "team_id": str(test_team.id),
        "result_id": str(test_result.id),
        "penalty_type": "disqualification",
        "reason": "Failed inspection",
    }
    resp = await client.post(f"/api/v1/races/{finished_race.id}/penalties", json=body, headers=admin_headers)
    penalty_id = resp.json()["id"]

    await db_session.refresh(test_result)
    assert test_result.dsq is True

    # Deactivate / Desativa
    resp2 = await client.patch(
        f"/api/v1/penalties/{penalty_id}",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert resp2.status_code == 200

    await db_session.refresh(test_result)
    assert test_result.dsq is False
