"""
Tests for dashboard summary endpoint.
Testes para endpoint de resumo do dashboard.
"""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus, championship_entries
from app.core.security import create_access_token
from app.races.models import Race, RaceStatus, race_entries
from app.results.models import RaceResult
from app.roles.models import Role
from app.teams.models import Team
from app.users.models import User

ENDPOINT = "/api/v1/dashboard/summary"


# ── Fixtures / Fixtures ──────────────────────────────────────────


@pytest.fixture
async def active_championship(db_session: AsyncSession) -> Championship:
    """Create an active championship / Cria um campeonato ativo."""
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
async def planned_championship(db_session: AsyncSession) -> Championship:
    """Create a planned championship / Cria um campeonato planejado."""
    champ = Championship(
        name="formula_e_2027",
        display_name="Formula E 2027",
        season_year=2027,
        status=ChampionshipStatus.planned,
    )
    db_session.add(champ)
    await db_session.commit()
    await db_session.refresh(champ)
    return champ


@pytest.fixture
async def completed_championship(db_session: AsyncSession) -> Championship:
    """Create a completed championship / Cria um campeonato concluido."""
    champ = Championship(
        name="formula_e_2025",
        display_name="Formula E 2025",
        season_year=2025,
        status=ChampionshipStatus.completed,
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
async def enrolled_teams(
    db_session: AsyncSession,
    active_championship: Championship,
    team_alpha: Team,
    team_beta: Team,
) -> tuple[Team, Team]:
    """Enroll both teams in the active championship / Inscreve ambas equipes no campeonato ativo."""
    await db_session.execute(
        championship_entries.insert().values(championship_id=active_championship.id, team_id=team_alpha.id)
    )
    await db_session.execute(
        championship_entries.insert().values(championship_id=active_championship.id, team_id=team_beta.id)
    )
    await db_session.commit()
    return team_alpha, team_beta


@pytest.fixture
async def finished_race(
    db_session: AsyncSession,
    active_championship: Championship,
    enrolled_teams: tuple[Team, Team],
) -> Race:
    """Create a finished race with team entries / Cria uma corrida finalizada com inscricoes."""
    race = Race(
        championship_id=active_championship.id,
        name="round_01",
        display_name="Round 1",
        round_number=1,
        status=RaceStatus.finished,
        scheduled_at=datetime(2026, 1, 15, 14, 0, tzinfo=UTC),
    )
    db_session.add(race)
    await db_session.flush()

    for team in enrolled_teams:
        await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=team.id))

    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def scheduled_races(
    db_session: AsyncSession,
    active_championship: Championship,
) -> list[Race]:
    """Create multiple scheduled races / Cria multiplas corridas agendadas."""
    races = []
    for i in range(6):
        race = Race(
            championship_id=active_championship.id,
            name=f"round_{i + 2:02d}",
            display_name=f"Round {i + 2}",
            round_number=i + 2,
            status=RaceStatus.scheduled,
            scheduled_at=datetime(2026, 3 + i, 15, 14, 0, tzinfo=UTC),
            track_name=f"Track {i + 2}",
            track_country=f"Country {i + 2}",
        )
        db_session.add(race)
        races.append(race)
    await db_session.commit()
    for race in races:
        await db_session.refresh(race)
    return races


# ── Tests / Testes ────────────────────────────────────────────────


async def test_dashboard_summary_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Empty state returns empty lists / Estado vazio retorna listas vazias."""
    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_championships"] == []
    assert data["next_races"] == []
    assert data["championship_standings"] == []


async def test_dashboard_summary_active_championships(
    client: AsyncClient,
    admin_headers: dict[str, str],
    active_championship: Championship,
) -> None:
    """Active championships are returned / Campeonatos ativos sao retornados."""
    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["active_championships"]) == 1
    champ = data["active_championships"][0]
    assert champ["name"] == "formula_e_2026"
    assert champ["display_name"] == "Formula E 2026"
    assert champ["season_year"] == 2026
    assert champ["status"] == "active"


async def test_dashboard_summary_excludes_non_active(
    client: AsyncClient,
    admin_headers: dict[str, str],
    active_championship: Championship,
    planned_championship: Championship,
    completed_championship: Championship,
) -> None:
    """Only active championships returned / Apenas campeonatos ativos retornados."""
    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["active_championships"]) == 1
    assert data["active_championships"][0]["name"] == "formula_e_2026"


async def test_dashboard_summary_race_counts(
    client: AsyncClient,
    admin_headers: dict[str, str],
    active_championship: Championship,
    finished_race: Race,
    scheduled_races: list[Race],
) -> None:
    """Total and completed race counts are correct / Contagem de corridas esta correta."""
    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    champ = resp.json()["active_championships"][0]
    assert champ["total_races"] == 7  # 1 finished + 6 scheduled
    assert champ["completed_races"] == 1


async def test_dashboard_summary_team_count(
    client: AsyncClient,
    admin_headers: dict[str, str],
    active_championship: Championship,
    enrolled_teams: tuple[Team, Team],
) -> None:
    """Enrolled team count is correct / Contagem de equipes inscritas esta correta."""
    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    champ = resp.json()["active_championships"][0]
    assert champ["team_count"] == 2


async def test_dashboard_summary_next_races_ordered(
    client: AsyncClient,
    admin_headers: dict[str, str],
    active_championship: Championship,
    scheduled_races: list[Race],
) -> None:
    """Next races ordered by scheduled_at ascending / Proximas corridas ordenadas por data."""
    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    races = resp.json()["next_races"]
    assert len(races) == 5  # default limit
    dates = [r["scheduled_at"] for r in races]
    assert dates == sorted(dates)


async def test_dashboard_summary_next_races_limit(
    client: AsyncClient,
    admin_headers: dict[str, str],
    active_championship: Championship,
    scheduled_races: list[Race],
) -> None:
    """Next races respects the default limit of 5 / Proximas corridas respeita limite padrao."""
    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    races = resp.json()["next_races"]
    assert len(races) == 5  # 6 scheduled, limited to 5


async def test_dashboard_summary_next_races_excludes_non_scheduled(
    client: AsyncClient,
    admin_headers: dict[str, str],
    active_championship: Championship,
    finished_race: Race,
    scheduled_races: list[Race],
) -> None:
    """Only scheduled races included in next races / Apenas corridas agendadas nas proximas."""
    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    races = resp.json()["next_races"]
    statuses = {r["name"] for r in races}
    assert "round_01" not in statuses  # finished race excluded


async def test_dashboard_summary_next_races_excludes_null_scheduled_at(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    active_championship: Championship,
) -> None:
    """Races without scheduled_at are excluded / Corridas sem data agendada sao excluidas."""
    race = Race(
        championship_id=active_championship.id,
        name="round_no_date",
        display_name="Round No Date",
        round_number=99,
        status=RaceStatus.scheduled,
        scheduled_at=None,
    )
    db_session.add(race)
    await db_session.commit()

    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["next_races"] == []


async def test_dashboard_summary_standings_top_5(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    active_championship: Championship,
) -> None:
    """Standings are limited to top 5 per championship / Classificacao limitada ao top 5."""
    # Create 6 teams and enroll them / Cria 6 equipes e inscreve
    teams = []
    for i in range(6):
        team = Team(name=f"team_{i}", display_name=f"Team {i}")
        db_session.add(team)
        teams.append(team)
    await db_session.flush()

    for team in teams:
        await db_session.execute(
            championship_entries.insert().values(championship_id=active_championship.id, team_id=team.id)
        )

    # Create a finished race / Cria uma corrida finalizada
    race = Race(
        championship_id=active_championship.id,
        name="round_01",
        display_name="Round 1",
        round_number=1,
        status=RaceStatus.finished,
    )
    db_session.add(race)
    await db_session.flush()

    for i, team in enumerate(teams):
        await db_session.execute(race_entries.insert().values(race_id=race.id, team_id=team.id))
        db_session.add(RaceResult(race_id=race.id, team_id=team.id, position=i + 1, points=float(25 - i * 3)))
    await db_session.commit()

    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    standings = resp.json()["championship_standings"]
    assert len(standings) == 1
    assert len(standings[0]["standings"]) == 5


async def test_dashboard_summary_standings_empty(
    client: AsyncClient,
    admin_headers: dict[str, str],
    active_championship: Championship,
) -> None:
    """Empty standings when no results / Classificacao vazia quando sem resultados."""
    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["championship_standings"] == []


async def test_dashboard_summary_unauthorized(client: AsyncClient) -> None:
    """401 without auth / 401 sem autenticacao."""
    resp = await client.get(ENDPOINT)
    assert resp.status_code == 401


async def test_dashboard_summary_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """403 without required permissions / 403 sem permissoes necessarias."""
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

    resp = await client.get(ENDPOINT, headers=headers)
    assert resp.status_code == 403
