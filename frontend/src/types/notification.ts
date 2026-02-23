/**
 * Notification TypeScript interfaces.
 * Interfaces TypeScript de notificacao.
 */

export type NotificationType =
  | "race_scheduled"
  | "result_published"
  | "team_invite"
  | "championship_update"
  | "general";

export interface NotificationListItem {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  entity_type: string | null;
  entity_id: string | null;
  is_read: boolean;
  created_at: string;
}

export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  entity_type: string | null;
  entity_id: string | null;
  is_read: boolean;
  created_at: string;
  updated_at: string;
}

export interface UnreadCount {
  unread_count: number;
}
