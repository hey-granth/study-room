/** WebSocket hook with auto-reconnect and heartbeat. */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useRoomStore } from '@/store/roomStore';
import { usePresenceStore } from '@/store/presenceStore';
import type { WSClientMessage, WSServerMessage } from '@/types/ws';
import { WS_HEARTBEAT_INTERVAL_MS, WS_MAX_RECONNECT_ATTEMPTS, WS_RECONNECT_DELAYS_MS } from '@/constants';

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8000/api/v1/ws';

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface UseWebSocketReturn {
  isConnected: boolean;
  sendMessage: (message: WSClientMessage) => void;
  lastMessage: WSServerMessage | null;
  connectionState: ConnectionState;
  chatMessages: WSServerMessage[];
}

/**
 * WebSocket hook for a specific room.
 * Handles connect, reconnect with exponential backoff, heartbeat, and message dispatch.
 *
 * @param roomId - The room to connect to.
 * @returns Connection state and message utilities.
 */
export function useWebSocket(roomId: string): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const heartbeatRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isMountedRef = useRef(true);

  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [lastMessage, setLastMessage] = useState<WSServerMessage | null>(null);
  const [chatMessages, setChatMessages] = useState<WSServerMessage[]>([]);

  const { accessToken } = useAuthStore();
  const { setActiveSession } = useRoomStore();
  const { setParticipants } = usePresenceStore();

  const connect = useCallback(() => {
    if (!accessToken || !isMountedRef.current) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnectionState('connecting');
    const url = `${WS_BASE}/rooms/${roomId}?token=${encodeURIComponent(accessToken)}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!isMountedRef.current) { ws.close(); return; }
      setConnectionState('connected');
      reconnectCountRef.current = 0;

      // Start heartbeat
      heartbeatRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping', payload: {} }));
        }
      }, WS_HEARTBEAT_INTERVAL_MS);
    };

    ws.onmessage = (event: MessageEvent<string>) => {
      try {
        const msg = JSON.parse(event.data) as WSServerMessage;
        setLastMessage(msg);

        switch (msg.type) {
          case 'chat_message_broadcast':
            setChatMessages((prev) => [...prev, msg]);
            break;
          case 'participants_update':
            setParticipants(msg.payload.participants);
            break;
          case 'session_started':
            setActiveSession({
              id: msg.payload.session_id,
              room_id: roomId,
              started_by: msg.payload.started_by,
              started_at: msg.payload.started_at,
              ended_at: null,
              duration_seconds: null,
              is_active: true,
            });
            break;
          case 'session_ended':
            setActiveSession(null);
            break;
          default:
            break;
        }
      } catch {
        // Non-JSON message — ignore
      }
    };

    ws.onerror = () => {
      setConnectionState('error');
    };

    ws.onclose = () => {
      if (!isMountedRef.current) return;
      setConnectionState('disconnected');
      if (heartbeatRef.current) clearInterval(heartbeatRef.current);

      // Reconnect with exponential backoff
      if (reconnectCountRef.current < WS_MAX_RECONNECT_ATTEMPTS) {
        const delay = WS_RECONNECT_DELAYS_MS[reconnectCountRef.current] ?? 16000;
        reconnectCountRef.current += 1;
        reconnectTimerRef.current = setTimeout(connect, delay);
      } else {
        setConnectionState('error');
      }
    };
  }, [roomId, accessToken, setActiveSession, setParticipants]);

  useEffect(() => {
    isMountedRef.current = true;
    connect();

    return () => {
      isMountedRef.current = false;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      if (heartbeatRef.current) clearInterval(heartbeatRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((message: WSClientMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  return {
    isConnected: connectionState === 'connected',
    sendMessage,
    lastMessage,
    connectionState,
    chatMessages,
  };
}
