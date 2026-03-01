/**
 * Toast popup for new real-time notifications (auto-dismiss 5s).
 * Popup toast para novas notificacoes em tempo real (auto-dismiss 5s).
 */
"use client";

import { useEffect, useState, useCallback } from "react";
import { useSession } from "next-auth/react";
import { notificationWs } from "@/lib/websocket";

interface ToastItem {
  id: string;
  title: string;
  message: string;
}

export default function NotificationToast() {
  const { data: session } = useSession();
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  useEffect(() => {
    if (!session) return;
    const token = (session as unknown as { accessToken: string }).accessToken;

    notificationWs.connect(token);

    const unsubscribe = notificationWs.onNotification((notification) => {
      const toastId = notification.id;
      setToasts((prev) => [...prev, { id: toastId, title: notification.title, message: notification.message }]);

      // Auto-dismiss after 5s / Auto-dismiss apos 5s
      setTimeout(() => {
        dismissToast(toastId);
      }, 5000);
    });

    return () => {
      unsubscribe();
      notificationWs.disconnect();
    };
  }, [session, dismissToast]);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className="w-80 rounded-lg border border-gray-200 bg-white p-4 shadow-lg"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-semibold text-gray-900">{toast.title}</p>
              <p className="mt-1 text-sm text-gray-600">{toast.message}</p>
            </div>
            <button
              onClick={() => dismissToast(toast.id)}
              className="ml-2 text-gray-400 hover:text-gray-600"
            >
              &times;
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
