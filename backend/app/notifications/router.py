"""
Notifications API router.
Router da API de notificacoes.
"""

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, require_permissions
from app.db.session import get_db
from app.notifications.schemas import (
    NotificationCreateRequest,
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.notifications.service import (
    create_broadcast_notifications,
    create_notification,
    delete_notification,
    get_notification_by_id,
    get_unread_count,
    list_notifications,
    mark_all_as_read,
    mark_as_read,
)
from app.users.models import User

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationListResponse])
async def read_notifications(
    is_read: bool | None = Query(default=None, description="Filter by read status / Filtrar por status de leitura"),
    type: str | None = Query(default=None, description="Filter by type / Filtrar por tipo"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[NotificationListResponse]:
    """
    List own notifications, optionally filtered.
    Lista as proprias notificacoes, opcionalmente filtradas.
    """
    return await list_notifications(db, current_user.id, is_read=is_read, notification_type=type)  # type: ignore[return-value]


@router.get("/unread-count", response_model=UnreadCountResponse)
async def read_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UnreadCountResponse:
    """
    Get count of unread notifications.
    Retorna a contagem de notificacoes nao lidas.
    """
    count = await get_unread_count(db, current_user.id)
    return UnreadCountResponse(unread_count=count)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """
    Mark a notification as read. Only the owner can mark it.
    Marca uma notificacao como lida. Apenas o dono pode marca-la.
    """
    notification = await get_notification_by_id(db, notification_id)
    return await mark_as_read(db, notification, current_user.id)  # type: ignore[return-value]


@router.post("/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Mark all unread notifications as read.
    Marca todas as notificacoes nao lidas como lidas.
    """
    count = await mark_all_as_read(db, current_user.id)
    return {"marked_count": count}


@router.delete("/{notification_id}", status_code=204)
async def delete_own_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete own notification. Only the owner can delete it.
    Exclui a propria notificacao. Apenas o dono pode exclui-la.
    """
    notification = await get_notification_by_id(db, notification_id)
    await delete_notification(db, notification, current_user.id)
    return Response(status_code=204)


@router.post("/", response_model=list[NotificationResponse], status_code=201)
async def create_new_notification(
    body: NotificationCreateRequest,
    _current_user: User = Depends(require_permissions("notifications:create")),
    db: AsyncSession = Depends(get_db),
) -> list[NotificationResponse]:
    """
    Create notification(s). Admin only — requires notifications:create permission.
    If user_ids is provided, broadcasts to all listed users.
    If user_ids is omitted, returns an empty list (no-op for now).

    Cria notificacao(oes). Somente admin — requer permissao notifications:create.
    Se user_ids for fornecido, envia para todos os usuarios listados.
    Se user_ids for omitido, retorna lista vazia (no-op por enquanto).
    """
    if not body.user_ids:
        return []

    if len(body.user_ids) == 1:
        notification = await create_notification(
            db,
            user_id=body.user_ids[0],
            title=body.title,
            message=body.message,
            notification_type=body.type,
            entity_type=body.entity_type,
            entity_id=body.entity_id,
        )
        return [notification]  # type: ignore[list-item]

    return await create_broadcast_notifications(  # type: ignore[return-value]
        db,
        user_ids=body.user_ids,
        title=body.title,
        message=body.message,
        notification_type=body.type,
        entity_type=body.entity_type,
        entity_id=body.entity_id,
    )
