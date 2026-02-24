"""
Tests for penalty impact on championship standings.
Testes para impacto de penalidades nas classificacoes do campeonato.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus, championship_entries
from app.drivers.models import Driver
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
async def test_team_a(db_session: AsyncSession) -> Team:
    """Create team A / Cria equipe A."""
    team = Team(name="team_alpha", display_name="Team Alpha")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_team_b(db_session: AsyncSession) -> Team:
    """Create team B / Cria equipe B."""
    team = Team(name="team_beta", display_name="Team Beta")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def driver_a(db_session: AsyncSession, test_team_a: Team) -> Driver:
    """Create driver for team A / Cria piloto para equipe A."""
    driver = Driver(
        name="driver_alpha",
        display_name="Driver Alpha",
        abbreviation="DRA",
        number=1,
        team_id=test_team_a.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def driver_b(db_session: AsyncSession, test_team_b: Team) -> Driver:
    """Create driver for team B / Cria piloto para equipe B."""
    driver = Driver(
        name="driver_beta",
        display_name="Driver Beta",
        abbreviation="DRB",
        number=2,
        team_id=test_team_b.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def race_with_results(
    db_session: AsyncSession,
    test_championship: Championship,
    test_team_a: Team,
    test_team_b: Team,
    driver_a: Driver,
    driver_b: Driver,
) -> Race:
    """
    Create a finished race with results for both teams.
    Team A: 25pts (P1), Team B: 18pts (P2).

    Cria uma corrida finalizada com resultados para ambas as equipes.
    Equipe A: 25pts (P1), Equipe B: 18pts (P2).
    """
    race = Race(
        championship_id=test_championship.id,
        name="round_01_monza",
        display_name="Round 1 - Monza",
        round_number=1,
        status=RaceStatus.finished,
    )
    db_session.add(race)
    await db_session.flush()

    # Enroll teams / Inscreve equipes
    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=test_team_a.id)
    )
    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=test_team_b.id)
    )
    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=test_team_a.id))
    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=test_team_b.id))

    # Create results / Cria resultados
    result_a = RaceResult(
        race_id=race.id, team_id=test_team_a.id, driver_id=driver_a.id, position=1, points=25.0
    )
    result_b = RaceResult(
        race_id=race.id, team_id=test_team_b.id, driver_id=driver_b.id, position=2, points=18.0
    )
    db_session.add_all([result_a, result_b])
    await db_session.commit()
    await db_session.refresh(race)
    return race


# --- Team Standings / Classificacao de Equipes ---


async def test_standings_without_penalties(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    race_with_results: Race,
) -> None:
    """Standings without penalties are unchanged / Classificacao sem penalidades inalterada."""
    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["total_points"] == 25.0
    assert data[1]["total_points"] == 18.0


async def test_team_standings_with_points_deduction(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    race_with_results: Race,
    test_team_a: Team,
) -> None:
    """Points deduction reduces team standings / Deducao de pontos reduz classificacao."""
    # Add 10-point penalty to team A / Adiciona penalidade de 10 pontos a equipe A
    penalty = Penalty(
        race_id=race_with_results.id,
        team_id=test_team_a.id,
        penalty_type="points_deduction",
        reason="Budget cap breach",
        points_deducted=10.0,
    )
    db_session.add(penalty)
    await db_session.commit()

    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    data = resp.json()
    # Team A: 25 - 10 = 15, Team B: 18
    # Team B should now be first / Equipe B deve ser primeira agora
    assert data[0]["team_name"] == "team_beta"
    assert data[0]["total_points"] == 18.0
    assert data[1]["team_name"] == "team_alpha"
    assert data[1]["total_points"] == 15.0


async def test_driver_standings_with_points_deduction(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    race_with_results: Race,
    test_team_a: Team,
    driver_a: Driver,
) -> None:
    """Points deduction reduces driver standings / Deducao de pontos reduz classificacao de pilotos."""
    # Add 10-point penalty to driver A / Adiciona penalidade de 10 pontos ao piloto A
    penalty = Penalty(
        race_id=race_with_results.id,
        team_id=test_team_a.id,
        driver_id=driver_a.id,
        penalty_type="points_deduction",
        reason="Dangerous driving",
        points_deducted=10.0,
    )
    db_session.add(penalty)
    await db_session.commit()

    resp = await client.get(
        f"/api/v1/championships/{test_championship.id}/driver-standings", headers=admin_headers
    )
    data = resp.json()
    # Driver A: 25 - 10 = 15, Driver B: 18
    assert data[0]["driver_name"] == "driver_beta"
    assert data[0]["total_points"] == 18.0
    assert data[1]["driver_name"] == "driver_alpha"
    assert data[1]["total_points"] == 15.0


async def test_only_active_penalties_deducted(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    race_with_results: Race,
    test_team_a: Team,
) -> None:
    """Inactive penalties are not deducted / Penalidades inativas nao sao deduzidas."""
    penalty = Penalty(
        race_id=race_with_results.id,
        team_id=test_team_a.id,
        penalty_type="points_deduction",
        reason="Overturned penalty",
        points_deducted=10.0,
        is_active=False,
    )
    db_session.add(penalty)
    await db_session.commit()

    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    data = resp.json()
    # No deduction since inactive / Sem deducao pois inativo
    assert data[0]["total_points"] == 25.0
    assert data[1]["total_points"] == 18.0


async def test_only_points_deduction_type_affects_standings(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    race_with_results: Race,
    test_team_a: Team,
) -> None:
    """Only points_deduction penalties affect standings / Apenas penalidades de deducao afetam classificacao."""
    # Create a warning and time penalty (not points_deduction)
    # Cria advertencia e penalidade de tempo (nao deducao de pontos)
    for ptype in ["warning", "time_penalty"]:
        penalty = Penalty(
            race_id=race_with_results.id,
            team_id=test_team_a.id,
            penalty_type=ptype,
            reason="Test penalty",
            points_deducted=10.0,  # Should be ignored for non-points_deduction types
        )
        db_session.add(penalty)
    await db_session.commit()

    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    data = resp.json()
    # No deduction since wrong type / Sem deducao pois tipo errado
    assert data[0]["total_points"] == 25.0


async def test_standings_reorder_after_deduction(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    race_with_results: Race,
    test_team_a: Team,
) -> None:
    """Standings are re-sorted after deductions / Classificacao re-ordenada apos deducoes."""
    # 20-point penalty makes team A go from 25 to 5 (below team B's 18)
    # Penalidade de 20 pontos faz equipe A ir de 25 para 5 (abaixo dos 18 da equipe B)
    penalty = Penalty(
        race_id=race_with_results.id,
        team_id=test_team_a.id,
        penalty_type="points_deduction",
        reason="Major infraction",
        points_deducted=20.0,
    )
    db_session.add(penalty)
    await db_session.commit()

    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    data = resp.json()
    assert data[0]["position"] == 1
    assert data[0]["team_name"] == "team_beta"
    assert data[0]["total_points"] == 18.0
    assert data[1]["position"] == 2
    assert data[1]["team_name"] == "team_alpha"
    assert data[1]["total_points"] == 5.0
