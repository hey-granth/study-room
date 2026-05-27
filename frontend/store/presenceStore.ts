/** Zustand store for room presence (who is online). */

'use client';

import { create } from 'zustand';
import type { PresenceUser } from '@/types/api';

interface PresenceState {
  participants: PresenceUser[];
  setParticipants: (participants: PresenceUser[]) => void;
  addParticipant: (user: PresenceUser) => void;
  removeParticipant: (userId: string) => void;
  clearPresence: () => void;
}

export const usePresenceStore = create<PresenceState>()((set) => ({
  participants: [],

  setParticipants: (participants) => set({ participants }),

  addParticipant: (user) =>
    set((state) => {
      const exists = state.participants.some((p) => p.user_id === user.user_id);
      if (exists) return state;
      return { participants: [...state.participants, user] };
    }),

  removeParticipant: (userId) =>
    set((state) => ({
      participants: state.participants.filter((p) => p.user_id !== userId),
    })),

  clearPresence: () => set({ participants: [] }),
}));
