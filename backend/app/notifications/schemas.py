"""
Notification request/response schemas.
Schemas de requisicao/resposta de notificacao.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

NotificationType = Literal[
    "race_scheduled",
    "result_published",
    "team_invite",
    "championship_update",
    "general",
]


class NotificationResponse(BaseModel):
    """Notification response body / Corpo da resposta de notificacao."""

    id: uuid.UUID
    user_id: uuid.UUID
    type: NotificationType
    title: str
    message: str
    entity_type: str | None
    entity_id: uuid.UUID | None
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Notification list item / Item de listagem de notificacao."""

    id: uuid.UUID
    type: NotificationType
    title: str
    message: str
    entity_type: str | None
    entity_id: uuid.UUID | None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationCreateRequest(BaseModel):
    """
    Notification creation request body (admin).
    Corpo da requisicao de criacao de notificacao (admin).
    """

    type: NotificationType = "general"
    title: str
    message: str
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    user_ids: list[uuid.UUID] | None = None


class UnreadCountResponse(BaseModel):
    """Unread notification count / Contagem de notificacoes nao lidas."""

    unread_count: int
