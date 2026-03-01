/**
 * WebSocket client for real-time notifications.
 * Cliente WebSocket para notificacoes em tempo real.
 */

const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/notifications";

type NotificationHandler = (notification: {
  id: string;
  type: string;
  title: string;
  message: string;
  created_at: string;
}) => void;

class NotificationWebSocket {
  private ws: WebSocket | null = null;
  private handlers: Set<NotificationHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private token: string | null = null;

  /**
   * Connect to the WebSocket server.
   * Conecta ao servidor WebSocket.
   */
  connect(token: string): void {
    this.token = token;
    this.reconnectAttempts = 0;
    this._connect();
  }

  private _connect(): void {
    if (!this.token) return;
    if (this.ws && this.ws.readyState === WebSocket.OPEN) return;

    try {
      this.ws = new WebSocket(`${WS_BASE_URL}/ws?token=${this.token}`);

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "new_notification" && data.notification) {
            this.handlers.forEach((handler) => handler(data.notification));
          }
        } catch {
          // Ignore malformed messages / Ignorar mensagens malformadas
        }
      };

      this.ws.onclose = () => {
        this._scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };
    } catch {
      this._scheduleReconnect();
    }
  }

  private _scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
    if (this.reconnectTimer) return;

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectAttempts++;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this._connect();
    }, delay);
  }

  /**
   * Disconnect from the WebSocket server.
   * Desconecta do servidor WebSocket.
   */
  disconnect(): void {
    this.token = null;
    this.reconnectAttempts = this.maxReconnectAttempts;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Subscribe to notification events. Returns an unsubscribe function.
   * Inscreve para eventos de notificacao. Retorna funcao de desinscricao.
   */
  onNotification(handler: NotificationHandler): () => void {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }
}

// Singleton instance / Instancia singleton
export const notificationWs = new NotificationWebSocket();
