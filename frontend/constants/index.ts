/** Application-wide constants — no magic strings in components. */

export const APP_NAME = 'StudyRoom';
export const APP_TAGLINE = 'Focus Together. Achieve More.';

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  ROOMS: '/rooms',
  ROOM_NEW: '/rooms/new',
  ROOM: (id: string) => `/rooms/${id}`,
  PROFILE: '/profile',
} as const;

export const WS_RECONNECT_DELAYS_MS = [1000, 2000, 4000, 8000, 16000];
export const WS_HEARTBEAT_INTERVAL_MS = 30_000;
export const WS_MAX_RECONNECT_ATTEMPTS = 5;

export const QUERY_KEYS = {
  ROOMS: 'rooms',
  ROOM: (id: string) => ['room', id],
  ACTIVE_SESSION: (roomId: string) => ['session', 'active', roomId],
  SESSION_HISTORY: (roomId: string) => ['session', 'history', roomId],
  PARTICIPANTS: (roomId: string) => ['participants', roomId],
  USER_STATS: 'user-stats',
  ME: 'me',
} as const;

export const STALE_TIMES = {
  ROOMS: 30_000,
  ROOM_DETAIL: 10_000,
  SESSION: 5_000,
} as const;
