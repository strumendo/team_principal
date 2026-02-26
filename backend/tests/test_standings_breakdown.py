"""
Tests for championship standings breakdown endpoint.
Testes para endpoint de detalhamento de classificacao do campeonato.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus, championship_entries
from app.core.security import create_access_token
from app.drivers.models import Driver
from app.races.models import Race, RaceStatus, race_entries
from app.results.models import RaceResult
from app.roles.models import Role
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
async def team_alpha(db_session: AsyncSession) -> Team:
    """Create team alpha / Cria equipe alpha."""
    team = Team(name="team_alpha", display_name="Team Alpha")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def team_beta(db_session: AsyncSession) -> Team:
    """Create team beta / Cria equipe beta."""
    team = Team(name="team_beta", display_name="Team Beta")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def driver_alpha(db_session: AsyncSession, team_alpha: Team) -> Driver:
    """Create driver for team alpha / Cria piloto para equipe alpha."""
    driver = Driver(
        name="driver_alpha",
        display_name="Driver Alpha",
        abbreviation="DRA",
        number=1,
        team_id=team_alpha.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def driver_beta(db_session: AsyncSession, team_beta: Team) -> Driver:
    """Create driver for team beta / Cria piloto para equipe beta."""
    driver = Driver(
        name="driver_beta",
        display_name="Driver Beta",
        abbreviation="DRB",
        number=2,
        team_id=team_beta.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def race_1(
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
) -> Race:
    """Create first finished race with entries / Cria primeira corrida finalizada com inscricoes."""
    race = Race(
        championship_id=test_championship.id,
        name="round_01",
        display_name="Round 1",
        round_number=1,
        status=RaceStatus.finished,
    )
    db_session.add(race)
    await db_session.flush()

    # Enroll in championship / Inscreve no campeonato
    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=team_alpha.id)
    )
    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=team_beta.id)
    )

    # Enroll in race / Inscreve na corrida
    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=team_alpha.id))
    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=team_beta.id))

    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def race_2(
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    race_1: Race,
) -> Race:
    """Create second finished race with entries / Cria segunda corrida finalizada com inscricoes."""
    race = Race(
        championship_id=test_championship.id,
        name="round_02",
        display_name="Round 2",
        round_number=2,
        status=RaceStatus.finished,
    )
    db_session.add(race)
    await db_session.flush()

    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=team_alpha.id))
    await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=team_beta.id))

    await db_session.commit()
    await db_session.refresh(race)
    return race


BREAKDOWN_URL = "/api/v1/championships/{}/standings/breakdown"


async def test_breakdown_empty_no_results(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
) -> None:
    """Empty breakdown when no finished races / Detalhamento vazio sem corridas finalizadas."""
    resp = await client.get(BREAKDOWN_URL.format(test_championship.id), headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["races"] == []
    assert data["team_standings"] == []
    assert data["driver_standings"] == []


async def test_breakdown_races_ordered_by_round_number(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    race_1: Race,
    race_2: Race,
) -> None:
    """Races ordered by round_number / Corridas ordenadas por round_number."""
    # Add at least one result so races show up / Adiciona pelo menos um resultado
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_alpha.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_2.id, team_id=team_alpha.id, position=1, points=25.0))
    await db_session.commit()

    resp = await client.get(BREAKDOWN_URL.format(test_championship.id), headers=admin_headers)
    data = resp.json()
    assert len(data["races"]) == 2
    assert data["races"][0]["round_number"] == 1
    assert data["races"][1]["round_number"] == 2
    assert data["races"][0]["race_name"] == "round_01"
    assert data["races"][1]["race_name"] == "round_02"


async def test_breakdown_team_standings_with_race_points(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    race_1: Race,
    race_2: Race,
) -> None:
    """Team standings include per-race points / Classificacao de equipes inclui pontos por corrida."""
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_alpha.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_beta.id, position=2, points=18.0))
    db_session.add(RaceResult(race_id=race_2.id, team_id=team_alpha.id, position=2, points=18.0))
    db_session.add(RaceResult(race_id=race_2.id, team_id=team_beta.id, position=1, points=25.0))
    await db_session.commit()

    resp = await client.get(BREAKDOWN_URL.format(test_championship.id), headers=admin_headers)
    data = resp.json()

    assert len(data["team_standings"]) == 2
    # Both have 43 points
    alpha = next(t for t in data["team_standings"] if t["team_name"] == "team_alpha")
    beta = next(t for t in data["team_standings"] if t["team_name"] == "team_beta")
    assert alpha["total_points"] == 43.0
    assert beta["total_points"] == 43.0
    assert len(alpha["race_points"]) == 2
    assert len(beta["race_points"]) == 2


async def test_breakdown_team_standings_ordered_by_total_points(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    race_1: Race,
) -> None:
    """Team standings ordered by total_points descending / Equipes ordenadas por total_points desc."""
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_alpha.id, position=2, points=18.0))
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_beta.id, position=1, points=25.0))
    await db_session.commit()

    resp = await client.get(BREAKDOWN_URL.format(test_championship.id), headers=admin_headers)
    data = resp.json()

    assert data["team_standings"][0]["team_name"] == "team_beta"
    assert data["team_standings"][0]["position"] == 1
    assert data["team_standings"][0]["total_points"] == 25.0
    assert data["team_standings"][1]["team_name"] == "team_alpha"
    assert data["team_standings"][1]["position"] == 2
    assert data["team_standings"][1]["total_points"] == 18.0


async def test_breakdown_driver_standings(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    driver_alpha: Driver,
    driver_beta: Driver,
    race_1: Race,
) -> None:
    """Driver standings in breakdown / Classificacao de pilotos no detalhamento."""
    db_session.add(
        RaceResult(race_id=race_1.id, team_id=team_alpha.id, driver_id=driver_alpha.id, position=1, points=25.0)
    )
    db_session.add(
        RaceResult(race_id=race_1.id, team_id=team_beta.id, driver_id=driver_beta.id, position=2, points=18.0)
    )
    await db_session.commit()

    resp = await client.get(BREAKDOWN_URL.format(test_championship.id), headers=admin_headers)
    data = resp.json()

    assert len(data["driver_standings"]) == 2
    first = data["driver_standings"][0]
    assert first["driver_name"] == "driver_alpha"
    assert first["total_points"] == 25.0
    assert first["position"] == 1
    assert first["wins"] == 1
    assert len(first["race_points"]) == 1


async def test_breakdown_excludes_dsq_from_points(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    race_1: Race,
) -> None:
    """DSQ results have 0 points in breakdown / Resultados DSQ tem 0 pontos no detalhamento."""
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_alpha.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_beta.id, position=2, points=18.0, dsq=True))
    await db_session.commit()

    resp = await client.get(BREAKDOWN_URL.format(test_championship.id), headers=admin_headers)
    data = resp.json()

    alpha = next(t for t in data["team_standings"] if t["team_name"] == "team_alpha")
    beta = next(t for t in data["team_standings"] if t["team_name"] == "team_beta")
    assert alpha["total_points"] == 25.0
    assert beta["total_points"] == 0.0
    # DSQ race_points entry should show 0 points and dsq=True
    beta_rp = beta["race_points"][0]
    assert beta_rp["points"] == 0.0
    assert beta_rp["dsq"] is True


async def test_breakdown_team_wins_counted(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    race_1: Race,
    race_2: Race,
) -> None:
    """Wins counted correctly in breakdown / Vitorias contadas corretamente no detalhamento."""
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_alpha.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_beta.id, position=2, points=18.0))
    db_session.add(RaceResult(race_id=race_2.id, team_id=team_beta.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_2.id, team_id=team_alpha.id, position=2, points=18.0))
    await db_session.commit()

    resp = await client.get(BREAKDOWN_URL.format(test_championship.id), headers=admin_headers)
    data = resp.json()

    alpha = next(t for t in data["team_standings"] if t["team_name"] == "team_alpha")
    beta = next(t for t in data["team_standings"] if t["team_name"] == "team_beta")
    assert alpha["wins"] == 1
    assert beta["wins"] == 1


async def test_breakdown_championship_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """404 for non-existent championship / 404 para campeonato inexistente."""
    resp = await client.get(BREAKDOWN_URL.format(uuid.uuid4()), headers=admin_headers)
    assert resp.status_code == 404


async def test_breakdown_unauthorized(
    client: AsyncClient, test_championship: Championship
) -> None:
    """401 without auth / 401 sem autenticacao."""
    resp = await client.get(BREAKDOWN_URL.format(test_championship.id))
    assert resp.status_code == 401


async def test_breakdown_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
    test_championship: Championship,
) -> None:
    """403 without results:read permission / 403 sem permissao results:read."""
    no_perm_role = Role(name="noperm", display_name="No Perms", is_system=False)
    db_session.add(no_perm_role)
    await db_session.flush()

    user = User(
        email="noperm@example.com",
        hashed_password="hashed",
        full_name="No Perm User",
    )
    user.roles = [no_perm_role]
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token(subject=str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get(BREAKDOWN_URL.format(test_championship.id), headers=headers)
    assert resp.status_code == 403
