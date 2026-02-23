"""
Tests for notifications CRUD endpoints.
Testes para endpoints CRUD de notificacoes.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.models import Notification
from app.users.models import User


@pytest.fixture
async def test_notification(db_session: AsyncSession, test_user: User) -> Notification:
    """Create a test notification / Cria uma notificacao de teste."""
    notification = Notification(
        user_id=test_user.id,
        type="general",
        title="Test Notification",
        message="This is a test notification.",
    )
    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)
    return notification


@pytest.fixture
async def unread_notifications(db_session: AsyncSession, test_user: User) -> list[Notification]:
    """Create multiple unread notifications / Cria multiplas notificacoes nao lidas."""
    notifications = []
    for i in range(3):
        n = Notification(
            user_id=test_user.id,
            type="general",
            title=f"Notification {i}",
            message=f"Message {i}",
        )
        db_session.add(n)
        notifications.append(n)
    await db_session.commit()
    for n in notifications:
        await db_session.refresh(n)
    return notifications


@pytest.fixture
async def read_notification(db_session: AsyncSession, test_user: User) -> Notification:
    """Create a read notification / Cria uma notificacao lida."""
    notification = Notification(
        user_id=test_user.id,
        type="race_scheduled",
        title="Race Scheduled",
        message="A race has been scheduled.",
        entity_type="race",
        entity_id=uuid.uuid4(),
        is_read=True,
    )
    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)
    return notification


@pytest.fixture
async def other_user_notification(db_session: AsyncSession, admin_user: User) -> Notification:
    """Create a notification for another user / Cria uma notificacao para outro usuario."""
    notification = Notification(
        user_id=admin_user.id,
        type="team_invite",
        title="Team Invite",
        message="You have been invited to a team.",
    )
    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)
    return notification


# --- List notifications / Listar notificacoes ---


@pytest.mark.asyncio
async def test_list_notifications_empty(client: AsyncClient, auth_headers: dict[str, str], test_user: User) -> None:
    """Test GET /api/v1/notifications/ returns empty list / Testa retorna lista vazia."""
    response = await client.get("/api/v1/notifications/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_notifications_with_data(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User, test_notification: Notification
) -> None:
    """Test GET /api/v1/notifications/ returns notifications / Testa retorna notificacoes."""
    response = await client.get("/api/v1/notifications/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Notification"
    assert data[0]["type"] == "general"
    assert data[0]["is_read"] is False


@pytest.mark.asyncio
async def test_list_notifications_filter_unread(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    test_notification: Notification,
    read_notification: Notification,
) -> None:
    """Test filter by is_read=false / Testa filtro por nao lidas."""
    response = await client.get("/api/v1/notifications/?is_read=false", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Notification"


@pytest.mark.asyncio
async def test_list_notifications_filter_read(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    test_notification: Notification,
    read_notification: Notification,
) -> None:
    """Test filter by is_read=true / Testa filtro por lidas."""
    response = await client.get("/api/v1/notifications/?is_read=true", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Race Scheduled"


@pytest.mark.asyncio
async def test_list_notifications_filter_type(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    test_notification: Notification,
    read_notification: Notification,
) -> None:
    """Test filter by type / Testa filtro por tipo."""
    response = await client.get("/api/v1/notifications/?type=race_scheduled", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "race_scheduled"


@pytest.mark.asyncio
async def test_list_notifications_only_own(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    test_notification: Notification,
    other_user_notification: Notification,
) -> None:
    """Test user only sees own notifications / Testa que usuario so ve as proprias notificacoes."""
    response = await client.get("/api/v1/notifications/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Notification"


# --- Unread count / Contagem de nao lidas ---


@pytest.mark.asyncio
async def test_unread_count_zero(client: AsyncClient, auth_headers: dict[str, str], test_user: User) -> None:
    """Test unread count is 0 when no notifications / Testa contagem 0 sem notificacoes."""
    response = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_unread_count_with_unread(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User, unread_notifications: list[Notification]
) -> None:
    """Test unread count matches unread notifications / Testa contagem corresponde a nao lidas."""
    response = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["unread_count"] == 3


@pytest.mark.asyncio
async def test_unread_count_excludes_read(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    test_notification: Notification,
    read_notification: Notification,
) -> None:
    """Test unread count excludes read notifications / Testa contagem exclui notificacoes lidas."""
    response = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["unread_count"] == 1


@pytest.mark.asyncio
async def test_unread_count_excludes_other_users(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    other_user_notification: Notification,
) -> None:
    """Test unread count excludes other users' notifications / Testa contagem exclui notificacoes de outros."""
    response = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["unread_count"] == 0


# --- Mark as read / Marcar como lida ---


@pytest.mark.asyncio
async def test_mark_as_read(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User, test_notification: Notification
) -> None:
    """Test PATCH marks notification as read / Testa PATCH marca notificacao como lida."""
    response = await client.patch(
        f"/api/v1/notifications/{test_notification.id}/read", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True
    assert data["id"] == str(test_notification.id)


@pytest.mark.asyncio
async def test_mark_as_read_not_found(client: AsyncClient, auth_headers: dict[str, str], test_user: User) -> None:
    """Test PATCH with invalid ID returns 404 / Testa PATCH com ID invalido retorna 404."""
    response = await client.patch(
        f"/api/v1/notifications/{uuid.uuid4()}/read", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_mark_as_read_other_user_forbidden(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    other_user_notification: Notification,
) -> None:
    """Test cannot mark another user's notification / Testa que nao pode marcar notificacao de outro."""
    response = await client.patch(
        f"/api/v1/notifications/{other_user_notification.id}/read", headers=auth_headers
    )
    assert response.status_code == 403


# --- Mark all as read / Marcar todas como lidas ---


@pytest.mark.asyncio
async def test_mark_all_as_read(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    unread_notifications: list[Notification],
) -> None:
    """Test POST marks all unread as read / Testa POST marca todas nao lidas como lidas."""
    response = await client.post("/api/v1/notifications/mark-all-read", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["marked_count"] == 3

    # Verify all are now read / Verifica que todas estao lidas
    count_response = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)
    assert count_response.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_mark_all_as_read_empty(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User
) -> None:
    """Test mark-all-read with no unread returns 0 / Testa mark-all-read sem nao lidas retorna 0."""
    response = await client.post("/api/v1/notifications/mark-all-read", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["marked_count"] == 0


# --- Delete notification / Excluir notificacao ---


@pytest.mark.asyncio
async def test_delete_notification(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User, test_notification: Notification
) -> None:
    """Test DELETE own notification / Testa DELETE da propria notificacao."""
    response = await client.delete(
        f"/api/v1/notifications/{test_notification.id}", headers=auth_headers
    )
    assert response.status_code == 204

    # Verify deleted / Verifica exclusao
    list_response = await client.get("/api/v1/notifications/", headers=auth_headers)
    assert list_response.json() == []


@pytest.mark.asyncio
async def test_delete_notification_not_found(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User
) -> None:
    """Test DELETE with invalid ID returns 404 / Testa DELETE com ID invalido retorna 404."""
    response = await client.delete(
        f"/api/v1/notifications/{uuid.uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_other_user_notification_forbidden(
    client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
    other_user_notification: Notification,
) -> None:
    """Test cannot delete another user's notification / Testa que nao pode excluir notificacao de outro."""
    response = await client.delete(
        f"/api/v1/notifications/{other_user_notification.id}", headers=auth_headers
    )
    assert response.status_code == 403


# --- Create notification (admin) / Criar notificacao (admin) ---


@pytest.mark.asyncio
async def test_create_notification_single_user(
    client: AsyncClient,
    admin_headers: dict[str, str],
    admin_user: User,
    test_user: User,
) -> None:
    """Test POST creates notification for single user / Testa POST cria notificacao para um usuario."""
    response = await client.post(
        "/api/v1/notifications/",
        headers=admin_headers,
        json={
            "type": "general",
            "title": "Admin Notice",
            "message": "Important admin message.",
            "user_ids": [str(test_user.id)],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Admin Notice"
    assert data[0]["type"] == "general"
    assert data[0]["user_id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_create_notification_broadcast(
    client: AsyncClient,
    admin_headers: dict[str, str],
    admin_user: User,
    test_user: User,
) -> None:
    """Test POST broadcasts notification to multiple users / Testa POST envia para multiplos usuarios."""
    response = await client.post(
        "/api/v1/notifications/",
        headers=admin_headers,
        json={
            "type": "championship_update",
            "title": "Championship Update",
            "message": "The championship has been updated.",
            "user_ids": [str(test_user.id), str(admin_user.id)],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    user_ids = {item["user_id"] for item in data}
    assert str(test_user.id) in user_ids
    assert str(admin_user.id) in user_ids


@pytest.mark.asyncio
async def test_create_notification_with_entity(
    client: AsyncClient,
    admin_headers: dict[str, str],
    admin_user: User,
    test_user: User,
) -> None:
    """Test POST creates notification with entity link / Testa POST cria notificacao com link de entidade."""
    entity_id = str(uuid.uuid4())
    response = await client.post(
        "/api/v1/notifications/",
        headers=admin_headers,
        json={
            "type": "race_scheduled",
            "title": "Race Scheduled",
            "message": "A new race has been scheduled.",
            "entity_type": "race",
            "entity_id": entity_id,
            "user_ids": [str(test_user.id)],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["entity_type"] == "race"
    assert data[0]["entity_id"] == entity_id


@pytest.mark.asyncio
async def test_create_notification_no_user_ids(
    client: AsyncClient, admin_headers: dict[str, str], admin_user: User
) -> None:
    """Test POST with no user_ids returns empty list / Testa POST sem user_ids retorna lista vazia."""
    response = await client.post(
        "/api/v1/notifications/",
        headers=admin_headers,
        json={
            "title": "No Target",
            "message": "No one will see this.",
        },
    )
    assert response.status_code == 201
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_notification_forbidden(
    client: AsyncClient, auth_headers: dict[str, str], test_user: User
) -> None:
    """Test POST without notifications:create returns 403 / Testa sem permissao retorna 403."""
    response = await client.post(
        "/api/v1/notifications/",
        headers=auth_headers,
        json={
            "title": "Unauthorized",
            "message": "Should fail.",
            "user_ids": [str(test_user.id)],
        },
    )
    assert response.status_code == 403


# --- Auth / Autenticacao ---


@pytest.mark.asyncio
async def test_list_notifications_unauthorized(client: AsyncClient) -> None:
    """Test GET without token returns 401 / Testa GET sem token retorna 401."""
    response = await client.get("/api/v1/notifications/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unread_count_unauthorized(client: AsyncClient) -> None:
    """Test unread-count without token returns 401 / Testa unread-count sem token retorna 401."""
    response = await client.get("/api/v1/notifications/unread-count")
    assert response.status_code == 401
