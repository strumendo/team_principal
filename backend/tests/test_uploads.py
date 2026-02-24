"""
Tests for file upload endpoints (avatars, logos, photos).
Testes para endpoints de upload de arquivos (avatares, logos, fotos).
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.drivers.models import Driver
from app.teams.models import Team
from app.users.models import User


# --- Fixtures / Fixtures ---


@pytest.fixture
async def test_team(db_session: AsyncSession) -> Team:
    """Create a test team / Cria uma equipe de teste."""
    team = Team(
        name="upload_team",
        display_name="Upload Team",
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_driver(db_session: AsyncSession, test_team: Team) -> Driver:
    """Create a test driver / Cria um piloto de teste."""
    driver = Driver(
        name="upload_driver",
        display_name="Upload Driver",
        abbreviation="UPL",
        number=99,
        team_id=test_team.id,
    )
    db_session.add(driver)
    await db_session.commit()
    await db_session.refresh(driver)
    return driver


FAKE_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100
FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


# --- User avatar tests / Testes de avatar de usuario ---


async def test_upload_user_avatar_own(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Any authenticated user can upload their own avatar.
    Qualquer usuario autenticado pode enviar seu proprio avatar."""
    monkeypatch.setattr("app.uploads.storage.settings.UPLOAD_DIR", str(tmp_path))
    response = await client.post(
        f"/api/v1/uploads/users/{test_user.id}/avatar",
        headers=auth_headers,
        files={"file": ("avatar.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"].startswith("/uploads/avatars/")
    assert data["url"].endswith(".jpg")


async def test_upload_user_avatar_admin(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_user: User,
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Admin with users:update can upload another user's avatar.
    Admin com users:update pode enviar avatar de outro usuario."""
    monkeypatch.setattr("app.uploads.storage.settings.UPLOAD_DIR", str(tmp_path))
    response = await client.post(
        f"/api/v1/uploads/users/{test_user.id}/avatar",
        headers=admin_headers,
        files={"file": ("avatar.png", FAKE_PNG, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"].endswith(".png")


async def test_upload_user_avatar_forbidden(
    client: AsyncClient,
    auth_headers: dict[str, str],
    admin_user: User,
) -> None:
    """Regular user cannot upload another user's avatar.
    Usuario regular nao pode enviar avatar de outro usuario."""
    response = await client.post(
        f"/api/v1/uploads/users/{admin_user.id}/avatar",
        headers=auth_headers,
        files={"file": ("avatar.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert response.status_code == 403


async def test_upload_user_avatar_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Upload for non-existent user returns 404.
    Upload para usuario inexistente retorna 404."""
    fake_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/uploads/users/{fake_id}/avatar",
        headers=admin_headers,
        files={"file": ("avatar.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert response.status_code == 404


async def test_upload_user_avatar_replaces_old(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Re-uploading replaces old file and URL.
    Re-enviar substitui arquivo e URL antigos."""
    monkeypatch.setattr("app.uploads.storage.settings.UPLOAD_DIR", str(tmp_path))

    # First upload / Primeiro upload
    resp1 = await client.post(
        f"/api/v1/uploads/users/{test_user.id}/avatar",
        headers=auth_headers,
        files={"file": ("avatar1.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert resp1.status_code == 200
    url1 = resp1.json()["url"]

    # Second upload / Segundo upload
    resp2 = await client.post(
        f"/api/v1/uploads/users/{test_user.id}/avatar",
        headers=auth_headers,
        files={"file": ("avatar2.png", FAKE_PNG, "image/png")},
    )
    assert resp2.status_code == 200
    url2 = resp2.json()["url"]

    # URLs should be different / URLs devem ser diferentes
    assert url1 != url2


# --- Team logo tests / Testes de logo de equipe ---


async def test_upload_team_logo(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_team: Team,
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Upload team logo with teams:update permission.
    Upload de logo da equipe com permissao teams:update."""
    monkeypatch.setattr("app.uploads.storage.settings.UPLOAD_DIR", str(tmp_path))
    response = await client.post(
        f"/api/v1/uploads/teams/{test_team.id}/logo",
        headers=admin_headers,
        files={"file": ("logo.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"].startswith("/uploads/logos/")


async def test_upload_team_logo_forbidden(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_team: Team,
) -> None:
    """Regular user without teams:update cannot upload team logo.
    Usuario regular sem teams:update nao pode enviar logo da equipe."""
    response = await client.post(
        f"/api/v1/uploads/teams/{test_team.id}/logo",
        headers=auth_headers,
        files={"file": ("logo.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert response.status_code == 403


async def test_upload_team_logo_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Upload for non-existent team returns 404.
    Upload para equipe inexistente retorna 404."""
    fake_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/uploads/teams/{fake_id}/logo",
        headers=admin_headers,
        files={"file": ("logo.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert response.status_code == 404


# --- Driver photo tests / Testes de foto de piloto ---


async def test_upload_driver_photo(
    client: AsyncClient,
    admin_headers: dict[str, str],
    test_driver: Driver,
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Upload driver photo with drivers:update permission.
    Upload de foto do piloto com permissao drivers:update."""
    monkeypatch.setattr("app.uploads.storage.settings.UPLOAD_DIR", str(tmp_path))
    response = await client.post(
        f"/api/v1/uploads/drivers/{test_driver.id}/photo",
        headers=admin_headers,
        files={"file": ("photo.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"].startswith("/uploads/photos/")


async def test_upload_driver_photo_forbidden(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_driver: Driver,
) -> None:
    """Regular user without drivers:update cannot upload driver photo.
    Usuario regular sem drivers:update nao pode enviar foto do piloto."""
    response = await client.post(
        f"/api/v1/uploads/drivers/{test_driver.id}/photo",
        headers=auth_headers,
        files={"file": ("photo.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert response.status_code == 403


async def test_upload_driver_photo_not_found(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Upload for non-existent driver returns 404.
    Upload para piloto inexistente retorna 404."""
    fake_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/uploads/drivers/{fake_id}/photo",
        headers=admin_headers,
        files={"file": ("photo.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert response.status_code == 404


# --- Validation tests / Testes de validacao ---


async def test_upload_invalid_content_type(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
) -> None:
    """Upload with invalid content type returns 422.
    Upload com tipo de conteudo invalido retorna 422."""
    response = await client.post(
        f"/api/v1/uploads/users/{test_user.id}/avatar",
        headers=auth_headers,
        files={"file": ("file.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 422


async def test_upload_file_too_large(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Upload exceeding max size returns 422.
    Upload excedendo tamanho maximo retorna 422."""
    # Set a very small max size for testing / Definir tamanho maximo pequeno para teste
    monkeypatch.setattr("app.uploads.storage.settings.UPLOAD_MAX_SIZE_BYTES", 50)
    big_data = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    response = await client.post(
        f"/api/v1/uploads/users/{test_user.id}/avatar",
        headers=auth_headers,
        files={"file": ("big.jpg", big_data, "image/jpeg")},
    )
    assert response.status_code == 422


async def test_upload_unauthorized(
    client: AsyncClient,
    test_user: User,
) -> None:
    """Upload without auth token returns 401.
    Upload sem token de autenticacao retorna 401."""
    response = await client.post(
        f"/api/v1/uploads/users/{test_user.id}/avatar",
        files={"file": ("avatar.jpg", FAKE_JPEG, "image/jpeg")},
    )
    assert response.status_code == 401
