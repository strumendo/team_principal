"""
Tests for championship standings endpoint.
Testes para endpoint de classificacao do campeonato.
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


async def test_get_standings_empty_no_results(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
) -> None:
    """Empty standings when no results / Classificacao vazia quando sem resultados."""
    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_standings_with_data_ordered_by_points(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    race_1: Race,
) -> None:
    """Standings ordered by total points descending / Classificacao ordenada por pontos."""
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_alpha.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_beta.id, position=2, points=18.0))
    await db_session.commit()

    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["team_name"] == "team_alpha"
    assert data[0]["total_points"] == 25.0
    assert data[0]["position"] == 1
    assert data[1]["team_name"] == "team_beta"
    assert data[1]["total_points"] == 18.0
    assert data[1]["position"] == 2


async def test_get_standings_excludes_dsq_results(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    race_1: Race,
) -> None:
    """DSQ results excluded from standings / Resultados DSQ excluidos da classificacao."""
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_alpha.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_beta.id, position=2, points=18.0, dsq=True))
    await db_session.commit()

    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["team_name"] == "team_alpha"


async def test_get_standings_counts_wins_correctly(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    race_1: Race,
    race_2: Race,
) -> None:
    """Wins counted correctly / Vitorias contadas corretamente."""
    # Race 1: alpha wins / Corrida 1: alpha vence
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_alpha.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_beta.id, position=2, points=18.0))
    # Race 2: beta wins / Corrida 2: beta vence
    db_session.add(RaceResult(race_id=race_2.id, team_id=team_beta.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_2.id, team_id=team_alpha.id, position=2, points=18.0))
    await db_session.commit()

    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    data = resp.json()
    # Both have 43 points; alpha and beta each have 1 win
    alpha = next(d for d in data if d["team_name"] == "team_alpha")
    beta = next(d for d in data if d["team_name"] == "team_beta")
    assert alpha["wins"] == 1
    assert beta["wins"] == 1
    assert alpha["total_points"] == 43.0
    assert beta["total_points"] == 43.0


async def test_get_standings_multiple_races_accumulate_points(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    race_1: Race,
    race_2: Race,
) -> None:
    """Points accumulate across multiple races / Pontos acumulam ao longo de varias corridas."""
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_alpha.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_beta.id, position=2, points=18.0))
    db_session.add(RaceResult(race_id=race_2.id, team_id=team_alpha.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_2.id, team_id=team_beta.id, position=2, points=18.0))
    await db_session.commit()

    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    data = resp.json()
    assert data[0]["total_points"] == 50.0
    assert data[0]["races_scored"] == 2
    assert data[1]["total_points"] == 36.0
    assert data[1]["races_scored"] == 2


async def test_get_standings_position_assigned_1_indexed(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    test_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
    race_1: Race,
) -> None:
    """Standings positions are 1-indexed / Posicoes da classificacao comecam em 1."""
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_alpha.id, position=1, points=25.0))
    db_session.add(RaceResult(race_id=race_1.id, team_id=team_beta.id, position=2, points=18.0))
    await db_session.commit()

    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=admin_headers)
    data = resp.json()
    assert data[0]["position"] == 1
    assert data[1]["position"] == 2


async def test_get_standings_championship_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """404 for non-existent championship / 404 para campeonato inexistente."""
    resp = await client.get(f"/api/v1/championships/{uuid.uuid4()}/standings", headers=admin_headers)
    assert resp.status_code == 404


async def test_get_standings_unauthorized(
    client: AsyncClient, test_championship: Championship
) -> None:
    """401 without auth / 401 sem autenticacao."""
    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings")
    assert resp.status_code == 401


async def test_get_standings_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
    test_championship: Championship,
) -> None:
    """403 without results:read permission / 403 sem permissao results:read."""
    # Create user with no results permissions / Cria usuario sem permissoes de resultados
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

    resp = await client.get(f"/api/v1/championships/{test_championship.id}/standings", headers=headers)
    assert resp.status_code == 403
