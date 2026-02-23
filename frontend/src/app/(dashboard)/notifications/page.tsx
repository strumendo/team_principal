/**
 * Notifications page with read/unread filter, actions, and pagination.
 * Pagina de notificacoes com filtro lida/nao lida, acoes e paginacao.
 */
"use client";

import { useEffect, useState, useCallback } from "react";
import { useSession } from "next-auth/react";
import Link from "next/link";
import type { NotificationListItem, NotificationType } from "@/types/notification";
import { notificationsApi } from "@/lib/api-client";

const TYPE_BADGE: Record<NotificationType, { label: string; color: string }> = {
  race_scheduled: { label: "Race Scheduled", color: "bg-blue-100 text-blue-800" },
  result_published: { label: "Results", color: "bg-green-100 text-green-800" },
  team_invite: { label: "Team Invite", color: "bg-purple-100 text-purple-800" },
  championship_update: { label: "Championship", color: "bg-orange-100 text-orange-800" },
  general: { label: "General", color: "bg-gray-100 text-gray-800" },
};

function getEntityLink(entityType: string | null, entityId: string | null): string | null {
  if (!entityType || !entityId) return null;
  switch (entityType) {
    case "race":
      return `/races/${entityId}`;
    case "championship":
      return `/championships/${entityId}`;
    case "team":
      return `/teams/${entityId}`;
    default:
      return null;
  }
}

type FilterTab = "all" | "unread" | "read";

export default function NotificationsPage() {
  const { data: session } = useSession();
  const [notifications, setNotifications] = useState<NotificationListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterTab>("all");

  const getToken = useCallback(() => {
    if (!session) return null;
    return (session as unknown as { accessToken: string }).accessToken;
  }, [session]);

  const fetchNotifications = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    setLoading(true);
    const isRead = filter === "all" ? undefined : filter === "read";
    const { data, error: err } = await notificationsApi.list(token, { is_read: isRead });
    if (err) {
      setError(err);
    } else {
      setNotifications(data || []);
      setError(null);
    }
    setLoading(false);
  }, [getToken, filter]);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const handleMarkAsRead = async (id: string) => {
    const token = getToken();
    if (!token) return;
    await notificationsApi.markAsRead(token, id);
    await fetchNotifications();
  };

  const handleMarkAllAsRead = async () => {
    const token = getToken();
    if (!token) return;
    await notificationsApi.markAllAsRead(token);
    await fetchNotifications();
  };

  const handleDelete = async (id: string) => {
    const token = getToken();
    if (!token) return;
    await notificationsApi.delete(token, id);
    await fetchNotifications();
  };

  const tabs: { key: FilterTab; label: string }[] = [
    { key: "all", label: "All / Todas" },
    { key: "unread", label: "Unread / Nao lidas" },
    { key: "read", label: "Read / Lidas" },
  ];

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Notifications / Notificacoes
        </h1>
        <button
          onClick={handleMarkAllAsRead}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Mark all as read / Marcar todas como lidas
        </button>
      </div>

      {/* Filter tabs / Abas de filtro */}
      <div className="mb-4 flex gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              filter === tab.key
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-gray-500">Loading... / Carregando...</p>
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : notifications.length === 0 ? (
        <p className="text-gray-500">
          No notifications. / Nenhuma notificacao.
        </p>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => {
            const badge = TYPE_BADGE[n.type];
            const entityLink = getEntityLink(n.entity_type, n.entity_id);
            return (
              <div
                key={n.id}
                className={`rounded-lg border p-4 ${
                  n.is_read
                    ? "border-gray-200 bg-white"
                    : "border-blue-200 bg-blue-50"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="mb-1 flex items-center gap-2">
                      <span
                        className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${badge.color}`}
                      >
                        {badge.label}
                      </span>
                      {!n.is_read && (
                        <span className="inline-block h-2 w-2 rounded-full bg-blue-600" />
                      )}
                    </div>
                    <h3 className="text-sm font-semibold text-gray-900">
                      {n.title}
                    </h3>
                    <p className="mt-1 text-sm text-gray-600">{n.message}</p>
                    <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
                      <span>
                        {new Date(n.created_at).toLocaleDateString(undefined, {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                      {entityLink && (
                        <Link
                          href={entityLink}
                          className="text-blue-600 hover:underline"
                        >
                          View details / Ver detalhes
                        </Link>
                      )}
                    </div>
                  </div>
                  <div className="ml-4 flex gap-2">
                    {!n.is_read && (
                      <button
                        onClick={() => handleMarkAsRead(n.id)}
                        className="rounded px-2 py-1 text-xs text-blue-600 hover:bg-blue-100"
                        title="Mark as read / Marcar como lida"
                      >
                        Mark read
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(n.id)}
                      className="rounded px-2 py-1 text-xs text-red-600 hover:bg-red-100"
                      title="Delete / Excluir"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
