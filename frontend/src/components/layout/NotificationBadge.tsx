/**
 * Notification badge with WebSocket + polling fallback.
 * Badge de notificacao com WebSocket + fallback de polling.
 *
 * Connects via WebSocket for real-time updates; polls every 60s as fallback.
 * Conecta via WebSocket para atualizacoes em tempo real; poll a cada 60s como fallback.
 */
"use client";

import { useEffect, useState, useCallback } from "react";
import { useSession } from "next-auth/react";
import { notificationsApi } from "@/lib/api-client";
import { notificationWs } from "@/lib/websocket";

export default function NotificationBadge() {
  const { data: session } = useSession();
  const [count, setCount] = useState(0);

  const fetchCount = useCallback(async (token: string) => {
    const { data } = await notificationsApi.getUnreadCount(token);
    if (data) {
      setCount(data.unread_count);
    }
  }, []);

  useEffect(() => {
    if (!session) return;
    const token = (session as unknown as { accessToken: string }).accessToken;

    // Initial fetch / Busca inicial
    fetchCount(token);

    // Polling fallback (60s) / Fallback de polling (60s)
    const interval = setInterval(() => fetchCount(token), 60000);

    // WebSocket for real-time increments / WebSocket para incrementos em tempo real
    const unsubscribe = notificationWs.onNotification(() => {
      setCount((prev) => prev + 1);
    });

    return () => {
      clearInterval(interval);
      unsubscribe();
    };
  }, [session, fetchCount]);

  if (count === 0) return null;

  return (
    <span className="ml-auto inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1.5 text-xs font-bold text-white">
      {count > 99 ? "99+" : count}
    </span>
  );
}
