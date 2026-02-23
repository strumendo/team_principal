"""
Notifications business logic.
Logica de negocios de notificacoes.
"""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.notifications.models import Notification


async def list_notifications(
    db: AsyncSession,
    user_id: uuid.UUID,
    is_read: bool | None = None,
    notification_type: str | None = None,
) -> list[Notification]:
    """
    List notifications for a user, optionally filtered by read status and type.
    Lista notificacoes de um usuario, opcionalmente filtradas por status de leitura e tipo.
    """
    stmt = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
    if is_read is not None:
        stmt = stmt.where(Notification.is_read == is_read)
    if notification_type is not None:
        stmt = stmt.where(Notification.type == notification_type)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_unread_count(db: AsyncSession, user_id: uuid.UUID) -> int:
    """
    Get count of unread notifications for a user.
    Retorna a contagem de notificacoes nao lidas de um usuario.
    """
    stmt = (
        select(func.count())
        .select_from(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_notification_by_id(db: AsyncSession, notification_id: uuid.UUID) -> Notification:
    """
    Get a notification by ID. Raises NotFoundException if not found.
    Busca uma notificacao por ID. Lanca NotFoundException se nao encontrada.
    """
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notification = result.scalar_one_or_none()
    if notification is None:
        raise NotFoundException("Notification not found")
    return notification


async def mark_as_read(db: AsyncSession, notification: Notification, user_id: uuid.UUID) -> Notification:
    """
    Mark a notification as read. Enforces ownership.
    Marca uma notificacao como lida. Valida propriedade.
    """
    if notification.user_id != user_id:
        raise ForbiddenException("Cannot access another user's notification")
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_all_as_read(db: AsyncSession, user_id: uuid.UUID) -> int:
    """
    Mark all unread notifications as read for a user. Returns count updated.
    Marca todas as notificacoes nao lidas como lidas para um usuario. Retorna contagem atualizada.
    """
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount  # type: ignore[return-value]


async def delete_notification(db: AsyncSession, notification: Notification, user_id: uuid.UUID) -> None:
    """
    Delete a notification. Enforces ownership.
    Exclui uma notificacao. Valida propriedade.
    """
    if notification.user_id != user_id:
        raise ForbiddenException("Cannot delete another user's notification")
    await db.delete(notification)
    await db.commit()


async def create_notification(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    message: str,
    notification_type: str = "general",
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
) -> Notification:
    """
    Create a notification for a single user.
    Cria uma notificacao para um unico usuario.
    """
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def create_broadcast_notifications(
    db: AsyncSession,
    user_ids: list[uuid.UUID],
    title: str,
    message: str,
    notification_type: str = "general",
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
) -> list[Notification]:
    """
    Create notifications for multiple users (broadcast).
    Cria notificacoes para multiplos usuarios (broadcast).
    """
    notifications = []
    for uid in user_ids:
        notification = Notification(
            user_id=uid,
            type=notification_type,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        db.add(notification)
        notifications.append(notification)
    await db.commit()
    for n in notifications:
        await db.refresh(n)
    return notifications


# --- Helper functions for future event-driven usage ---
# --- Funcoes auxiliares para uso futuro baseado em eventos ---


async def notify_race_scheduled(
    db: AsyncSession,
    user_ids: list[uuid.UUID],
    race_name: str,
    race_id: uuid.UUID,
) -> list[Notification]:
    """
    Notify users about a newly scheduled race.
    Notifica usuarios sobre uma corrida recem agendada.
    """
    return await create_broadcast_notifications(
        db,
        user_ids=user_ids,
        title=f"Race Scheduled: {race_name}",
        message=f"The race '{race_name}' has been scheduled.",
        notification_type="race_scheduled",
        entity_type="race",
        entity_id=race_id,
    )


async def notify_result_published(
    db: AsyncSession,
    user_ids: list[uuid.UUID],
    race_name: str,
    race_id: uuid.UUID,
) -> list[Notification]:
    """
    Notify users about published race results.
    Notifica usuarios sobre resultados de corrida publicados.
    """
    return await create_broadcast_notifications(
        db,
        user_ids=user_ids,
        title=f"Results Published: {race_name}",
        message=f"Results for '{race_name}' have been published.",
        notification_type="result_published",
        entity_type="race",
        entity_id=race_id,
    )


async def notify_team_invite(
    db: AsyncSession,
    user_id: uuid.UUID,
    team_name: str,
    team_id: uuid.UUID,
) -> Notification:
    """
    Notify a user about a team invitation.
    Notifica um usuario sobre um convite de equipe.
    """
    return await create_notification(
        db,
        user_id=user_id,
        title=f"Team Invite: {team_name}",
        message=f"You have been invited to join '{team_name}'.",
        notification_type="team_invite",
        entity_type="team",
        entity_id=team_id,
    )
