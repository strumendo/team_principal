"""
Tests for WebSocket notifications and ConnectionManager.
Testes para notificacoes WebSocket e ConnectionManager.
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from app.core.security import create_access_token
from app.main import create_app
from app.notifications.websocket import ConnectionManager
from app.users.models import User


pytestmark = pytest.mark.asyncio


class TestConnectionManager:
    """Unit tests for ConnectionManager / Testes unitarios do ConnectionManager."""

    async def test_connect_and_disconnect(self) -> None:
        """Test connect and disconnect lifecycle / Testa ciclo de vida connect/disconnect."""
        mgr = ConnectionManager()
        user_id = uuid.uuid4()

        class FakeWS:
            async def accept(self) -> None:
                pass

            async def send_json(self, data: dict) -> None:
                pass

        ws = FakeWS()
        await mgr.connect(user_id, ws)  # type: ignore[arg-type]
        assert mgr.get_connection_count(user_id) == 1

        mgr.disconnect(user_id, ws)  # type: ignore[arg-type]
        assert mgr.get_connection_count(user_id) == 0

    async def test_send_to_user(self) -> None:
        """Test sending data to a connected user / Testa envio de dados para usuario conectado."""
        mgr = ConnectionManager()
        user_id = uuid.uuid4()
        received: list[dict] = []

        class FakeWS:
            async def accept(self) -> None:
                pass

            async def send_json(self, data: dict) -> None:
                received.append(data)

        ws = FakeWS()
        await mgr.connect(user_id, ws)  # type: ignore[arg-type]
        await mgr.send_to_user(user_id, {"type": "test", "data": "hello"})
        assert len(received) == 1
        assert received[0]["type"] == "test"

    async def test_send_to_nonexistent_user(self) -> None:
        """Test sending to a user with no connections / Testa envio para usuario sem conexoes."""
        mgr = ConnectionManager()
        # Should not raise / Nao deve lancar excecao
        await mgr.send_to_user(uuid.uuid4(), {"type": "test"})

    async def test_multiple_connections(self) -> None:
        """Test multiple WS connections for same user / Testa multiplas conexoes WS do mesmo usuario."""
        mgr = ConnectionManager()
        user_id = uuid.uuid4()
        received_1: list[dict] = []
        received_2: list[dict] = []

        class FakeWS1:
            async def accept(self) -> None:
                pass

            async def send_json(self, data: dict) -> None:
                received_1.append(data)

        class FakeWS2:
            async def accept(self) -> None:
                pass

            async def send_json(self, data: dict) -> None:
                received_2.append(data)

        ws1, ws2 = FakeWS1(), FakeWS2()
        await mgr.connect(user_id, ws1)  # type: ignore[arg-type]
        await mgr.connect(user_id, ws2)  # type: ignore[arg-type]
        assert mgr.get_connection_count(user_id) == 2

        await mgr.send_to_user(user_id, {"type": "broadcast"})
        assert len(received_1) == 1
        assert len(received_2) == 1


def test_ws_missing_token() -> None:
    """WebSocket without token should be closed / WebSocket sem token deve ser fechado."""
    app = create_app()
    client = TestClient(app)

    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/notifications/ws"):
            pass


def test_ws_invalid_token() -> None:
    """WebSocket with invalid token should be closed / WebSocket com token invalido deve ser fechado."""
    app = create_app()
    client = TestClient(app)

    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/notifications/ws?token=invalidtoken"):
            pass
