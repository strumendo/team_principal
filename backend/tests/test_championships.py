"""
Tests for championships CRUD endpoints.
Testes para endpoints CRUD de campeonatos.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.championships.models import Championship, ChampionshipStatus
from app.users.models import User


@pytest.fixture
async def test_championship(db_session: AsyncSession) -> Championship:
    """Create a test championship / Cria um campeonato de teste."""
    champ = Championship(
        name="formula_e_2026",
        display_name="Formula E 2026",
        description="Electric racing championship",
        season_year=2026,
        status=ChampionshipStatus.planned,
    )
    db_session.add(champ)
    await db_session.commit()
    await db_session.refresh(champ)
    return champ


@pytest.fixture
async def active_championship(db_session: AsyncSession) -> Championship:
    """Create an active championship / Cria um campeonato ativo."""
    champ = Championship(
        name="gt3_series_2026",
        display_name="GT3 Series 2026",
        season_year=2026,
        status=ChampionshipStatus.active,
    )
    db_session.add(champ)
    await db_session.commit()
    await db_session.refresh(champ)
    return champ


@pytest.fixture
async def completed_championship(db_session: AsyncSession) -> Championship:
    """Create a completed championship from 2025 / Cria um campeonato concluido de 2025."""
    champ = Championship(
        name="endurance_2025",
        display_name="Endurance 2025",
        season_year=2025,
        status=ChampionshipStatus.completed,
        is_active=False,
    )
    db_session.add(champ)
    await db_session.commit()
    await db_session.refresh(champ)
    return champ


# --- List championships / Listar campeonatos ---


@pytest.mark.asyncio
async def test_list_championships_empty(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test GET /api/v1/championships/ returns empty list / Testa retorna lista vazia."""
    response = await client.get("/api/v1/championships/", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_championships_with_data(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test GET /api/v1/championships/ returns championships / Testa retorna campeonatos."""
    response = await client.get("/api/v1/championships/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "formula_e_2026"


@pytest.mark.asyncio
async def test_list_championships_filter_by_status(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    active_championship: Championship,
) -> None:
    """Test GET /championships/?status=active filters correctly / Filtra por status."""
    response = await client.get("/api/v1/championships/?status=active", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "gt3_series_2026"


@pytest.mark.asyncio
async def test_list_championships_filter_by_season_year(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    completed_championship: Championship,
) -> None:
    """Test GET /championships/?season_year=2025 filters correctly / Filtra por ano."""
    response = await client.get("/api/v1/championships/?season_year=2025", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "endurance_2025"


@pytest.mark.asyncio
async def test_list_championships_filter_by_active(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_championship: Championship,
    completed_championship: Championship,
) -> None:
    """Test GET /championships/?is_active=true filters correctly / Filtra por ativo."""
    response = await client.get("/api/v1/championships/?is_active=true", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "formula_e_2026"


# --- Get championship by ID / Buscar campeonato por ID ---


@pytest.mark.asyncio
async def test_get_championship_by_id(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test GET /api/v1/championships/{id} returns championship / Retorna campeonato."""
    response = await client.get(f"/api/v1/championships/{test_championship.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "formula_e_2026"
    assert data["display_name"] == "Formula E 2026"
    assert data["description"] == "Electric racing championship"
    assert data["season_year"] == 2026
    assert data["status"] == "planned"


@pytest.mark.asyncio
async def test_get_championship_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test GET /api/v1/championships/{id} with invalid ID returns 404."""
    response = await client.get(f"/api/v1/championships/{uuid.uuid4()}", headers=admin_headers)
    assert response.status_code == 404


# --- Create championship / Criar campeonato ---


@pytest.mark.asyncio
async def test_create_championship_full(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test POST /api/v1/championships/ creates with all fields / Cria com todos os campos."""
    response = await client.post(
        "/api/v1/championships/",
        headers=admin_headers,
        json={
            "name": "lmp2_2026",
            "display_name": "LMP2 Championship 2026",
            "description": "Prototype racing",
            "season_year": 2026,
            "status": "active",
            "start_date": "2026-03-01",
            "end_date": "2026-11-30",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "lmp2_2026"
    assert data["display_name"] == "LMP2 Championship 2026"
    assert data["description"] == "Prototype racing"
    assert data["season_year"] == 2026
    assert data["status"] == "active"
    assert data["start_date"] == "2026-03-01"
    assert data["end_date"] == "2026-11-30"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_championship_minimal(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test POST /api/v1/championships/ creates with required fields only / Campos obrigatorios."""
    response = await client.post(
        "/api/v1/championships/",
        headers=admin_headers,
        json={
            "name": "gt4_2026",
            "display_name": "GT4 Cup 2026",
            "season_year": 2026,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "gt4_2026"
    assert data["description"] is None
    assert data["status"] == "planned"
    assert data["start_date"] is None
    assert data["end_date"] is None


@pytest.mark.asyncio
async def test_create_championship_duplicate(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test POST /api/v1/championships/ with duplicate name returns 409."""
    response = await client.post(
        "/api/v1/championships/",
        headers=admin_headers,
        json={
            "name": "formula_e_2026",
            "display_name": "Another Name",
            "season_year": 2026,
        },
    )
    assert response.status_code == 409


# --- Update championship / Atualizar campeonato ---


@pytest.mark.asyncio
async def test_update_championship_display_name(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test PATCH updates display_name / Atualiza display_name."""
    response = await client.patch(
        f"/api/v1/championships/{test_championship.id}",
        headers=admin_headers,
        json={"display_name": "Formula E Season 2026"},
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Formula E Season 2026"


@pytest.mark.asyncio
async def test_update_championship_status(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test PATCH updates status / Atualiza status."""
    response = await client.patch(
        f"/api/v1/championships/{test_championship.id}",
        headers=admin_headers,
        json={"status": "active"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "active"


@pytest.mark.asyncio
async def test_update_championship_deactivate(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test PATCH deactivates championship / Desativa campeonato."""
    response = await client.patch(
        f"/api/v1/championships/{test_championship.id}",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_update_championship_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test PATCH with invalid ID returns 404."""
    response = await client.patch(
        f"/api/v1/championships/{uuid.uuid4()}",
        headers=admin_headers,
        json={"display_name": "Nope"},
    )
    assert response.status_code == 404


# --- Delete championship / Excluir campeonato ---


@pytest.mark.asyncio
async def test_delete_championship(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test DELETE /api/v1/championships/{id} / Testa DELETE de campeonato."""
    response = await client.delete(f"/api/v1/championships/{test_championship.id}", headers=admin_headers)
    assert response.status_code == 204

    response = await client.get(f"/api/v1/championships/{test_championship.id}", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_championship_not_found(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test DELETE with invalid ID returns 404."""
    response = await client.delete(f"/api/v1/championships/{uuid.uuid4()}", headers=admin_headers)
    assert response.status_code == 404


# --- Auth / Autenticacao ---


@pytest.mark.asyncio
async def test_list_championships_unauthorized(client: AsyncClient) -> None:
    """Test GET /api/v1/championships/ without token returns 401."""
    response = await client.get("/api/v1/championships/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_championship_forbidden(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User
) -> None:
    """Test POST without championships:create returns 403."""
    response = await client.post(
        "/api/v1/championships/",
        headers=auth_headers,
        json={"name": "no_perms", "display_name": "No Perms", "season_year": 2026},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list(
    client: AsyncClient, admin_headers: dict[str, str], test_championship: Championship
) -> None:
    """Test admin with championships:read can list / Admin pode listar."""
    response = await client.get("/api/v1/championships/", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_admin_can_create(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    """Test admin with championships:create can create / Admin pode criar."""
    response = await client.post(
        "/api/v1/championships/",
        headers=admin_headers,
        json={"name": "test_champ", "display_name": "Test Championship", "season_year": 2026},
    )
    assert response.status_code == 201
