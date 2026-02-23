"""
Tests for driver championship standings endpoint.
Testes para endpoint de classificacao de pilotos no campeonato.
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
async def driver_ver(db_session: AsyncSession, team_alpha: Team) -> Driver:
    """Create driver VER in team alpha / Cria piloto VER na equipe alpha."""
    driver = Driver(
        name="verstappen",
        display_name="Max Verstappen",
        abbreviation="VER",
        number=1,
        team_id=team_alpha.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


@pytest.fixture
async def driver_nor(db_session: AsyncSession, team_beta: Team) -> Driver:
    """Create driver NOR in team beta / Cria piloto NOR na equipe beta."""
    driver = Driver(
        name="norris",
        display_name="Lando Norris",
        abbreviation="NOR",
        number=4,
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

    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=team_alpha.id)
    )
    await db_session.execute(
        championship_entries.insert().values(championship_id=test_championship.id, team_id=team_beta.id)
    )
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
    """Create second finished race / Cria segunda corrida finalizada."""
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


# --- Driver standings / Classificacao de pilotos ---


async def test_get_driver_standings_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
) -> None:
    """Empty standings when no results / Classificacao vazia quando sem resultados."""
    resp = await client.get(
        f"/api/v1/championships/{test_championship.id}/driver-standings", headers=admin_headers
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_driver_standings_ordered_by_points(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    driver_ver: Driver,
    driver_nor: Driver,
    race_1: Race,
) -> None:
    """Driver standings ordered by total points / Classificacao de pilotos ordenada por pontos."""
    db_session.add(
        RaceResult(race_id=race_1.id, team_id=team_alpha.id, driver_id=driver_ver.id, position=1, points=25.0)
    )
    db_session.add(
        RaceResult(race_id=race_1.id, team_id=team_beta.id, driver_id=driver_nor.id, position=2, points=18.0)
    )
    await db_session.commit()

    resp = await client.get(
        f"/api/v1/championships/{test_championship.id}/driver-standings", headers=admin_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["driver_name"] == "verstappen"
    assert data[0]["driver_abbreviation"] == "VER"
    assert data[0]["total_points"] == 25.0
    assert data[0]["position"] == 1
    assert data[0]["team_name"] == "team_alpha"
    assert data[1]["driver_name"] == "norris"
    assert data[1]["total_points"] == 18.0
    assert data[1]["position"] == 2


async def test_get_driver_standings_excludes_dsq(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    driver_ver: Driver,
    driver_nor: Driver,
    race_1: Race,
) -> None:
    """DSQ results excluded from driver standings / Resultados DSQ excluidos da classificacao de pilotos."""
    db_session.add(
        RaceResult(race_id=race_1.id, team_id=team_alpha.id, driver_id=driver_ver.id, position=1, points=25.0)
    )
    db_session.add(
        RaceResult(
            race_id=race_1.id, team_id=team_beta.id, driver_id=driver_nor.id, position=2, points=18.0, dsq=True
        )
    )
    await db_session.commit()

    resp = await client.get(
        f"/api/v1/championships/{test_championship.id}/driver-standings", headers=admin_headers
    )
    data = resp.json()
    assert len(data) == 1
    assert data[0]["driver_name"] == "verstappen"


async def test_get_driver_standings_counts_wins(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    driver_ver: Driver,
    driver_nor: Driver,
    race_1: Race,
    race_2: Race,
) -> None:
    """Wins counted correctly per driver / Vitorias contadas corretamente por piloto."""
    # Race 1: VER wins / Corrida 1: VER vence
    db_session.add(
        RaceResult(race_id=race_1.id, team_id=team_alpha.id, driver_id=driver_ver.id, position=1, points=25.0)
    )
    db_session.add(
        RaceResult(race_id=race_1.id, team_id=team_beta.id, driver_id=driver_nor.id, position=2, points=18.0)
    )
    # Race 2: NOR wins / Corrida 2: NOR vence
    db_session.add(
        RaceResult(race_id=race_2.id, team_id=team_beta.id, driver_id=driver_nor.id, position=1, points=25.0)
    )
    db_session.add(
        RaceResult(race_id=race_2.id, team_id=team_alpha.id, driver_id=driver_ver.id, position=2, points=18.0)
    )
    await db_session.commit()

    resp = await client.get(
        f"/api/v1/championships/{test_championship.id}/driver-standings", headers=admin_headers
    )
    data = resp.json()
    ver = next(d for d in data if d["driver_name"] == "verstappen")
    nor = next(d for d in data if d["driver_name"] == "norris")
    assert ver["wins"] == 1
    assert nor["wins"] == 1
    assert ver["total_points"] == 43.0
    assert nor["total_points"] == 43.0
    assert ver["races_scored"] == 2
    assert nor["races_scored"] == 2


async def test_get_driver_standings_ignores_results_without_driver(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    driver_ver: Driver,
    race_1: Race,
) -> None:
    """Results without driver_id are excluded / Resultados sem driver_id sao excluidos."""
    # With driver / Com piloto
    db_session.add(
        RaceResult(race_id=race_1.id, team_id=team_alpha.id, driver_id=driver_ver.id, position=1, points=25.0)
    )
    # Without driver / Sem piloto
    db_session.add(
        RaceResult(race_id=race_1.id, team_id=team_beta.id, position=2, points=18.0)
    )
    await db_session.commit()

    resp = await client.get(
        f"/api/v1/championships/{test_championship.id}/driver-standings", headers=admin_headers
    )
    data = resp.json()
    assert len(data) == 1
    assert data[0]["driver_name"] == "verstappen"


async def test_get_driver_standings_championship_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """404 for non-existent championship / 404 para campeonato inexistente."""
    resp = await client.get(
        f"/api/v1/championships/{uuid.uuid4()}/driver-standings", headers=admin_headers
    )
    assert resp.status_code == 404


async def test_get_driver_standings_unauthorized(
    client: AsyncClient, test_championship: Championship
) -> None:
    """401 without auth / 401 sem autenticacao."""
    resp = await client.get(f"/api/v1/championships/{test_championship.id}/driver-standings")
    assert resp.status_code == 401


async def test_get_driver_standings_forbidden(
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

    resp = await client.get(
        f"/api/v1/championships/{test_championship.id}/driver-standings", headers=headers
    )
    assert resp.status_code == 403
