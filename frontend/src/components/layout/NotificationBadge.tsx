/**
 * Notification badge component with polling.
 * Componente de badge de notificacao com polling.
 *
 * Client component that polls /unread-count every 60s.
 * Componente cliente que consulta /unread-count a cada 60s.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { notificationsApi } from "@/lib/api-client";

export default function NotificationBadge() {
  const { data: session } = useSession();
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!session) return;
    const token = (session as unknown as { accessToken: string }).accessToken;

    const fetchCount = async () => {
      const { data } = await notificationsApi.getUnreadCount(token);
      if (data) {
        setCount(data.unread_count);
      }
    };

    fetchCount();
    const interval = setInterval(fetchCount, 60000);
    return () => clearInterval(interval);
  }, [session]);

  if (count === 0) return null;

  return (
    <span className="ml-auto inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1.5 text-xs font-bold text-white">
      {count > 99 ? "99+" : count}
    </span>
  );
}
