"""
WebSocket connection manager for real-time notifications.
Gerenciador de conexoes WebSocket para notificacoes em tempo real.
"""

import uuid
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """
    In-memory WebSocket connection manager (single-server deployment).
    Gerenciador de conexoes WebSocket em memoria (deploy single-server).
    """

    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: uuid.UUID, websocket: WebSocket) -> None:
        """
        Accept and register a WebSocket connection for a user.
        Aceita e registra uma conexao WebSocket para um usuario.
        """
        await websocket.accept()
        self._connections[user_id].append(websocket)

    def disconnect(self, user_id: uuid.UUID, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection for a user.
        Remove uma conexao WebSocket de um usuario.
        """
        conns = self._connections.get(user_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns and user_id in self._connections:
            del self._connections[user_id]

    async def send_to_user(self, user_id: uuid.UUID, data: dict) -> None:
        """
        Send JSON data to all connections of a specific user.
        Envia dados JSON para todas as conexoes de um usuario especifico.
        """
        conns = self._connections.get(user_id, [])
        disconnected: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(user_id, ws)

    def get_connection_count(self, user_id: uuid.UUID) -> int:
        """
        Get the number of active connections for a user.
        Retorna o numero de conexoes ativas para um usuario.
        """
        return len(self._connections.get(user_id, []))


# Singleton instance / Instancia singleton
manager = ConnectionManager()
