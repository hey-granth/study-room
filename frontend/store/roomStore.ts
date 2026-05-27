/** Zustand store for active room state. */

'use client';

import { create } from 'zustand';
import type { RoomDetail, StudySession } from '@/types/api';

interface RoomState {
  activeRoom: RoomDetail | null;
  activeSession: StudySession | null;
  setActiveRoom: (room: RoomDetail | null) => void;
  setActiveSession: (session: StudySession | null) => void;
  clearRoom: () => void;
}

export const useRoomStore = create<RoomState>()((set) => ({
  activeRoom: null,
  activeSession: null,

  setActiveRoom: (room) => set({ activeRoom: room }),
  setActiveSession: (session) => set({ activeSession: session }),
  clearRoom: () => set({ activeRoom: null, activeSession: null }),
}));
