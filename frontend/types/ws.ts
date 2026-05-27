/** WebSocket message type discriminated union — mirrors backend WSMessageType enum. */

export type WSMessageType =
  | 'chat_message'
  | 'ping'
  | 'chat_message_broadcast'
  | 'user_joined'
  | 'user_left'
  | 'session_started'
  | 'session_ended'
  | 'participants_update'
  | 'pong'
  | 'error';

export interface WSMessage<T = unknown> {
  type: WSMessageType;
  payload: T;
  timestamp: string;
}

export interface ChatMessagePayload {
  id: string;
  user_id: string;
  username: string;
  display_name: string;
  content: string;
  sent_at: string;
}

export interface UserJoinedPayload {
  user_id: string;
  username: string;
  display_name: string;
}

export interface UserLeftPayload {
  user_id: string;
  username: string;
}

export interface SessionStartedPayload {
  session_id: string;
  started_by: string;
  started_at: string;
}

export interface SessionEndedPayload {
  session_id: string;
  ended_by: string;
  duration_seconds: number;
}

export interface ParticipantsUpdatePayload {
  participants: Array<{
    user_id: string;
    username: string;
    display_name: string;
    avatar_url: string | null;
    joined_at: string;
  }>;
}

export interface ErrorPayload {
  message: string;
}

/** Discriminated union covering every server-sent message type. */
export type WSServerMessage =
  | WSMessage<ChatMessagePayload> & { type: 'chat_message_broadcast' }
  | WSMessage<UserJoinedPayload> & { type: 'user_joined' }
  | WSMessage<UserLeftPayload> & { type: 'user_left' }
  | WSMessage<SessionStartedPayload> & { type: 'session_started' }
  | WSMessage<SessionEndedPayload> & { type: 'session_ended' }
  | WSMessage<ParticipantsUpdatePayload> & { type: 'participants_update' }
  | WSMessage<Record<string, never>> & { type: 'pong' }
  | WSMessage<ErrorPayload> & { type: 'error' };

/** Messages the client sends to the server. */
export type WSClientMessage =
  | { type: 'chat_message'; payload: { content: string } }
  | { type: 'ping'; payload: Record<string, never> };
