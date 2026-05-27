'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { Users, Play, Square, Copy, Check, Send, Crown, Clock, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAuthStore } from '@/store/authStore';
import { useRoomStore } from '@/store/roomStore';
import { usePresenceStore } from '@/store/presenceStore';
import { formatDuration, timeAgo } from '@/lib/utils';
import { QUERY_KEYS, ROUTES } from '@/constants';
import type { RoomDetail, StudySession, Page } from '@/types/api';
import type { WSServerMessage } from '@/types/ws';

export default function RoomPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuthStore();
  const { activeSession, setActiveRoom, setActiveSession, clearRoom } = useRoomStore();
  const { participants, clearPresence } = usePresenceStore();
  const queryClient = useQueryClient();

  const [copied, setCopied] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const chatBottomRef = useRef<HTMLDivElement>(null);

  const { isConnected, sendMessage, chatMessages, connectionState } = useWebSocket(id);

  // Fetch room detail
  const { data: room } = useQuery({
    queryKey: QUERY_KEYS.ROOM(id),
    queryFn: async () => {
      const res = await api.get<RoomDetail>(`/rooms/${id}`);
      return res.data;
    },
  });

  // Fetch active session on mount
  const { data: fetchedSession } = useQuery({
    queryKey: QUERY_KEYS.ACTIVE_SESSION(id),
    queryFn: async () => {
      const res = await api.get<StudySession | null>(`/sessions/rooms/${id}/active`);
      return res.data;
    },
  });

  // Fetch session history
  const { data: history } = useQuery({
    queryKey: QUERY_KEYS.SESSION_HISTORY(id),
    queryFn: async () => {
      const res = await api.get<Page<StudySession>>(`/sessions/rooms/${id}/history`);
      return res.data;
    },
  });

  useEffect(() => {
    if (room) setActiveRoom(room);
    return () => { clearRoom(); clearPresence(); };
  }, [room, setActiveRoom, clearRoom, clearPresence]);

  useEffect(() => {
    if (fetchedSession) setActiveSession(fetchedSession);
  }, [fetchedSession, setActiveSession]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Session mutations
  const startSession = useMutation({
    mutationFn: () => api.post<StudySession>(`/sessions/rooms/${id}/start`),
    onSuccess: (res) => {
      setActiveSession(res.data);
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.ACTIVE_SESSION(id) });
    },
  });

  const endSession = useMutation({
    mutationFn: () => api.post<StudySession>(`/sessions/rooms/${id}/end`),
    onSuccess: () => {
      setActiveSession(null);
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.ACTIVE_SESSION(id) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.SESSION_HISTORY(id) });
    },
  });

  const copyInviteCode = async () => {
    if (room?.invite_code) {
      await navigator.clipboard.writeText(room.invite_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSendMessage = () => {
    const content = chatInput.trim();
    if (!content) return;
    sendMessage({ type: 'chat_message', payload: { content } });
    setChatInput('');
  };

  const isMember = room?.members.some((m) => m.id === user?.id);
  const isOwner = room?.owner_id === user?.id;

  return (
    <div className="flex gap-6 h-[calc(100vh-4rem)] -m-8 p-8 overflow-hidden">
      {/* Left: Participants */}
      <div className="w-60 flex-shrink-0 flex flex-col gap-4">
        <Link href={ROUTES.ROOMS}>
          <button className="flex items-center gap-2 text-sm mb-2"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={e => e.currentTarget.style.color = 'var(--text-primary)'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
          >
            <ArrowLeft size={14} /> Rooms
          </button>
        </Link>

        <div className="glass-card p-4 flex-1 overflow-hidden flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <Users size={15} style={{ color: 'var(--accent-primary)' }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
              Online ({participants.length})
            </span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2">
            {participants.length === 0 ? (
              <p className="text-xs text-center py-4" style={{ color: 'var(--text-muted)' }}>
                {isConnected ? 'No one else here yet' : 'Connecting...'}
              </p>
            ) : (
              participants.map((p) => (
                <div key={p.user_id} className="flex items-center gap-2 p-2 rounded-lg"
                  style={{ background: 'rgba(255,255,255,0.03)' }}>
                  <div className="relative">
                    <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                      style={{ background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))', color: '#0A0E1A' }}>
                      {p.display_name[0].toUpperCase()}
                    </div>
                    <span className="absolute -bottom-0.5 -right-0.5 presence-dot" style={{ width: 7, height: 7 }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                      {p.display_name}
                      {room?.owner_id === p.user_id && (
                        <Crown size={10} className="inline ml-1" style={{ color: '#fbbf24' }} />
                      )}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Invite code */}
          {room && (
            <div className="mt-4 pt-4" style={{ borderTop: '1px solid var(--border-subtle)' }}>
              <p className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>Invite code</p>
              <button
                onClick={copyInviteCode}
                className="flex items-center gap-2 w-full p-2 rounded-lg font-mono text-sm transition-all"
                style={{ background: 'rgba(79,255,218,0.06)', color: 'var(--accent-primary)', border: '1px solid var(--border-accent)' }}
              >
                {room.invite_code}
                {copied ? <Check size={13} /> : <Copy size={13} />}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Center: Session */}
      <div className="flex-1 flex flex-col gap-4 overflow-hidden">
        <div className="glass-card p-6">
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
            {room?.name ?? 'Loading...'}
          </h1>
          {room?.description && (
            <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>{room.description}</p>
          )}

          <div className="flex items-center gap-4">
            {/* Session Timer */}
            <div className="flex-1 text-center">
              <SessionTimer session={activeSession} />
            </div>

            {/* Controls */}
            {isMember && (
              <div className="flex flex-col gap-2">
                {activeSession ? (
                  <button
                    onClick={() => endSession.mutate()}
                    disabled={endSession.isPending}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all"
                    style={{ background: 'rgba(239,68,68,0.15)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)' }}
                  >
                    <Square size={14} /> End Session
                  </button>
                ) : (
                  <button
                    onClick={() => startSession.mutate()}
                    disabled={startSession.isPending}
                    className="btn-primary flex items-center gap-2"
                  >
                    <Play size={14} /> Start Session
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Session History */}
        <div className="glass-card p-5 flex-1 overflow-hidden flex flex-col">
          <h2 className="font-display font-semibold mb-3 text-sm" style={{ color: 'var(--text-primary)' }}>
            Session History
          </h2>
          <div className="flex-1 overflow-y-auto space-y-2">
            {history?.items.filter(s => !s.is_active).map((s) => (
              <div key={s.id} className="flex items-center justify-between p-3 rounded-lg"
                style={{ background: 'rgba(255,255,255,0.03)' }}>
                <div className="flex items-center gap-2">
                  <Clock size={13} style={{ color: 'var(--text-muted)' }} />
                  <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                    {new Date(s.started_at).toLocaleDateString()}
                  </span>
                </div>
                <span className="font-mono text-xs font-semibold" style={{ color: 'var(--accent-primary)' }}>
                  {formatDuration(s.duration_seconds ?? 0)}
                </span>
              </div>
            )) ?? (
              <p className="text-xs text-center py-4" style={{ color: 'var(--text-muted)' }}>No sessions yet</p>
            )}
          </div>
        </div>
      </div>

      {/* Right: Chat */}
      <div className="w-72 flex-shrink-0 flex flex-col glass-card overflow-hidden">
        <div className="p-4 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
          <h2 className="font-display font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Room Chat</h2>
          <div className="flex items-center gap-1.5 mt-1">
            <div className="w-1.5 h-1.5 rounded-full" style={{ background: isConnected ? 'var(--accent-primary)' : '#6b7280' }} />
            <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
              {connectionState === 'connected' ? 'Connected' : connectionState}
            </span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <AnimatePresence initial={false}>
            {chatMessages.map((msg, i) => {
              if (msg.type !== 'chat_message_broadcast') return null;
              const isMe = msg.payload.user_id === user?.id;
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}
                >
                  {!isMe && (
                    <span className="text-xs mb-1 ml-1" style={{ color: 'var(--text-muted)' }}>
                      {msg.payload.display_name}
                    </span>
                  )}
                  <div
                    className="px-3 py-2 rounded-2xl text-sm max-w-[85%] break-words"
                    style={{
                      background: isMe ? 'var(--accent-primary)' : 'rgba(255,255,255,0.06)',
                      color: isMe ? '#0A0E1A' : 'var(--text-primary)',
                    }}
                  >
                    {msg.payload.content}
                  </div>
                  <span className="text-xs mt-1 mx-1" style={{ color: 'var(--text-muted)' }}>
                    {timeAgo(msg.payload.sent_at)}
                  </span>
                </motion.div>
              );
            })}
          </AnimatePresence>
          <div ref={chatBottomRef} />
        </div>

        <div className="p-3 border-t" style={{ borderColor: 'var(--border-subtle)' }}>
          <div className="flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
              placeholder="Send a message..."
              className="input-field text-sm py-2"
              disabled={!isConnected}
            />
            <button
              onClick={handleSendMessage}
              disabled={!isConnected || !chatInput.trim()}
              className="px-3 py-2 rounded-xl flex-shrink-0 transition-all"
              style={{
                background: chatInput.trim() ? 'var(--accent-primary)' : 'rgba(255,255,255,0.06)',
                color: chatInput.trim() ? '#0A0E1A' : 'var(--text-muted)',
              }}
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function SessionTimer({ session }: { session: StudySession | null }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!session?.is_active) { setElapsed(0); return; }
    const start = new Date(session.started_at).getTime();
    const tick = () => setElapsed(Math.floor((Date.now() - start) / 1000));
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [session]);

  if (!session?.is_active) {
    return (
      <div>
        <p className="font-mono text-5xl font-bold" style={{ color: 'var(--text-muted)' }}>—:—:—</p>
        <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>No active session</p>
      </div>
    );
  }

  return (
    <div>
      <p className="font-mono text-5xl font-bold timer-active" style={{ color: 'var(--accent-primary)' }}>
        {formatDuration(elapsed)}
      </p>
      <p className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>Session in progress</p>
    </div>
  );
}
