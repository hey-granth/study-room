/** All API request and response types — mirrors backend Pydantic schemas exactly. */

export interface User {
  id: string;
  email: string;
  username: string;
  display_name: string;
  avatar_url: string | null;
  is_active: boolean;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserWithToken {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  display_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RoomSummary {
  id: string;
  name: string;
  description: string | null;
  is_public: boolean;
  max_participants: number;
  invite_code: string;
  owner_id: string;
  member_count: number;
  has_active_session: boolean;
}

export interface RoomDetail {
  id: string;
  name: string;
  description: string | null;
  is_public: boolean;
  max_participants: number;
  invite_code: string;
  owner_id: string;
  owner: User;
  members: User[];
  member_count: number;
}

export interface RoomCreate {
  name: string;
  description?: string;
  is_public?: boolean;
  max_participants?: number;
}

export interface PresenceUser {
  user_id: string;
  username: string;
  display_name: string;
  avatar_url: string | null;
  joined_at: string;
}

export interface StudySession {
  id: string;
  room_id: string;
  started_by: string;
  started_at: string;
  ended_at: string | null;
  duration_seconds: number | null;
  is_active: boolean;
}

export interface UserSessionStats {
  total_sessions: number;
  total_study_seconds: number;
  sessions_this_week: number;
  average_session_seconds: number;
  longest_session_seconds: number;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  code: string;
  timestamp: string;
}
