"""
Tests for calendar endpoint.
Testes para endpoint do calendario.
"""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus
from app.core.security import create_access_token
from app.races.models import Race, RaceStatus
from app.roles.models import Role
from app.users.models import User

ENDPOINT = "/api/v1/calendar/races"


# ── Fixtures / Fixtures ──────────────────────────────────────────


@pytest.fixture
async def championship_a(db_session: AsyncSession) -> Championship:
    """Create championship A / Cria campeonato A."""
    champ = Championship(
        name="gt_series_2026",
        display_name="GT Series 2026",
        season_year=2026,
        status=ChampionshipStatus.active,
    )
    db_session.add(champ)
    await db_session.commit()
    await db_session.refresh(champ)
    return champ


@pytest.fixture
async def championship_b(db_session: AsyncSession) -> Championship:
    """Create championship B / Cria campeonato B."""
    champ = Championship(
        name="endurance_cup_2026",
        display_name="Endurance Cup 2026",
        season_year=2026,
        status=ChampionshipStatus.planned,
    )
    db_session.add(champ)
    await db_session.commit()
    await db_session.refresh(champ)
    return champ


@pytest.fixture
async def march_races(
    db_session: AsyncSession,
    championship_a: Championship,
) -> list[Race]:
    """Create races in March 2026 / Cria corridas em marco 2026."""
    races = []
    for i, day in enumerate([5, 12, 19], start=1):
        race = Race(
            championship_id=championship_a.id,
            name=f"gt_round_{i:02d}",
            display_name=f"GT Round {i}",
            round_number=i,
            status=RaceStatus.scheduled,
            scheduled_at=datetime(2026, 3, day, 14, 0, tzinfo=UTC),
            track_name=f"Track {i}",
            track_country=f"Country {i}",
        )
        db_session.add(race)
        races.append(race)
    await db_session.commit()
    for race in races:
        await db_session.refresh(race)
    return races


@pytest.fixture
async def march_race_champ_b(
    db_session: AsyncSession,
    championship_b: Championship,
) -> Race:
    """Create a race in March from championship B / Cria corrida em marco do campeonato B."""
    race = Race(
        championship_id=championship_b.id,
        name="endurance_round_01",
        display_name="Endurance Round 1",
        round_number=1,
        status=RaceStatus.active,
        scheduled_at=datetime(2026, 3, 8, 10, 0, tzinfo=UTC),
        track_name="Endurance Track",
        track_country="Brazil",
    )
    db_session.add(race)
    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def april_race(
    db_session: AsyncSession,
    championship_a: Championship,
) -> Race:
    """Create a race in April / Cria corrida em abril."""
    race = Race(
        championship_id=championship_a.id,
        name="gt_round_04",
        display_name="GT Round 4",
        round_number=4,
        status=RaceStatus.scheduled,
        scheduled_at=datetime(2026, 4, 10, 14, 0, tzinfo=UTC),
    )
    db_session.add(race)
    await db_session.commit()
    await db_session.refresh(race)
    return race


@pytest.fixture
async def race_no_date(
    db_session: AsyncSession,
    championship_a: Championship,
) -> Race:
    """Create a race without scheduled_at / Cria corrida sem data agendada."""
    race = Race(
        championship_id=championship_a.id,
        name="gt_round_tbd",
        display_name="GT Round TBD",
        round_number=99,
        status=RaceStatus.scheduled,
        scheduled_at=None,
    )
    db_session.add(race)
    await db_session.commit()
    await db_session.refresh(race)
    return race


# ── Tests / Testes ────────────────────────────────────────────────


async def test_calendar_races_for_month(
    client: AsyncClient,
    admin_headers: dict[str, str],
    championship_a: Championship,
    march_races: list[Race],
) -> None:
    """Returns races scheduled in the given month / Retorna corridas agendadas no mes."""
    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 3}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    for race in data:
        assert race["championship_id"] == str(championship_a.id)
        assert race["championship_display_name"] == "GT Series 2026"


async def test_calendar_races_ordered_by_date(
    client: AsyncClient,
    admin_headers: dict[str, str],
    championship_a: Championship,
    march_races: list[Race],
) -> None:
    """Races are ordered by scheduled_at ascending / Corridas ordenadas por data."""
    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 3}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    dates = [r["scheduled_at"] for r in data]
    assert dates == sorted(dates)


async def test_calendar_races_filter_by_championship(
    client: AsyncClient,
    admin_headers: dict[str, str],
    championship_a: Championship,
    championship_b: Championship,
    march_races: list[Race],
    march_race_champ_b: Race,
) -> None:
    """Filter by championship_id returns only that championship's races / Filtra por campeonato."""
    # Without filter: all 4 races / Sem filtro: todas as 4 corridas
    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 3}, headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 4

    # Filter by championship A / Filtrar por campeonato A
    resp = await client.get(
        ENDPOINT,
        params={"year": 2026, "month": 3, "championship_id": str(championship_a.id)},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert all(r["championship_id"] == str(championship_a.id) for r in data)

    # Filter by championship B / Filtrar por campeonato B
    resp = await client.get(
        ENDPOINT,
        params={"year": 2026, "month": 3, "championship_id": str(championship_b.id)},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["display_name"] == "Endurance Round 1"


async def test_calendar_races_empty_month(
    client: AsyncClient,
    admin_headers: dict[str, str],
    championship_a: Championship,
    march_races: list[Race],
) -> None:
    """Returns empty list for a month with no races / Retorna lista vazia para mes sem corridas."""
    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 6}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_calendar_races_excludes_other_months(
    client: AsyncClient,
    admin_headers: dict[str, str],
    championship_a: Championship,
    march_races: list[Race],
    april_race: Race,
) -> None:
    """March query excludes April races / Consulta de marco exclui corridas de abril."""
    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 3}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert all("GT Round 4" != r["display_name"] for r in data)


async def test_calendar_races_excludes_no_date(
    client: AsyncClient,
    admin_headers: dict[str, str],
    championship_a: Championship,
    march_races: list[Race],
    race_no_date: Race,
) -> None:
    """Races without scheduled_at are excluded / Corridas sem data sao excluidas."""
    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 3}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert all(r["display_name"] != "GT Round TBD" for r in data)


async def test_calendar_races_response_fields(
    client: AsyncClient,
    admin_headers: dict[str, str],
    championship_a: Championship,
    march_races: list[Race],
) -> None:
    """Response includes all expected fields / Resposta inclui todos os campos esperados."""
    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 3}, headers=admin_headers)
    assert resp.status_code == 200
    race = resp.json()[0]
    assert "id" in race
    assert "display_name" in race
    assert "round_number" in race
    assert "status" in race
    assert "scheduled_at" in race
    assert "track_name" in race
    assert "track_country" in race
    assert "championship_id" in race
    assert "championship_display_name" in race
    assert "championship_status" in race


async def test_calendar_races_championship_status(
    client: AsyncClient,
    admin_headers: dict[str, str],
    championship_b: Championship,
    march_race_champ_b: Race,
) -> None:
    """Championship status is included in response / Status do campeonato esta na resposta."""
    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 3}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["championship_status"] == "planned"


async def test_calendar_races_unauthorized(client: AsyncClient) -> None:
    """401 without auth token / 401 sem token de autenticacao."""
    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 3})
    assert resp.status_code == 401


async def test_calendar_races_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """403 without races:read permission / 403 sem permissao races:read."""
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

    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 3}, headers=headers)
    assert resp.status_code == 403


async def test_calendar_races_december_boundary(
    client: AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    championship_a: Championship,
) -> None:
    """December query works correctly (year boundary) / Consulta de dezembro funciona (limite de ano)."""
    race = Race(
        championship_id=championship_a.id,
        name="gt_finale",
        display_name="GT Finale",
        round_number=10,
        status=RaceStatus.scheduled,
        scheduled_at=datetime(2026, 12, 20, 14, 0, tzinfo=UTC),
    )
    db_session.add(race)
    await db_session.commit()

    resp = await client.get(ENDPOINT, params={"year": 2026, "month": 12}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["display_name"] == "GT Finale"


async def test_calendar_races_default_params(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Endpoint works without explicit year/month params / Endpoint funciona sem parametros explicitos."""
    resp = await client.get(ENDPOINT, headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
