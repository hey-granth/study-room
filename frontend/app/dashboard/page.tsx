'use client';

import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Timer, Users, TrendingUp, Calendar, Plus, ArrowRight } from 'lucide-react';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';
import { formatDurationShort } from '@/lib/utils';
import { QUERY_KEYS, ROUTES } from '@/constants';
import type { UserSessionStats, Page, RoomSummary } from '@/types/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function DashboardPage() {
  const { user } = useAuthStore();

  const { data: stats } = useQuery({
    queryKey: [QUERY_KEYS.USER_STATS],
    queryFn: async () => {
      const res = await api.get<UserSessionStats>('/sessions/me/stats');
      return res.data;
    },
  });

  const { data: rooms } = useQuery({
    queryKey: [QUERY_KEYS.ROOMS, 'joined'],
    queryFn: async () => {
      const res = await api.get<Page<RoomSummary>>('/rooms/?filter_type=joined&size=3');
      return res.data;
    },
  });

  const statCards = [
    { icon: Timer, label: 'Total Study Time', value: formatDurationShort(stats?.total_study_seconds ?? 0), color: 'var(--accent-primary)' },
    { icon: TrendingUp, label: 'This Week', value: `${stats?.sessions_this_week ?? 0} sessions`, color: 'var(--accent-secondary)' },
    { icon: Calendar, label: 'Total Sessions', value: stats?.total_sessions ?? 0, color: '#a78bfa' },
    { icon: Users, label: 'Avg Session', value: formatDurationShort(stats?.average_session_seconds ?? 0), color: '#fb923c' },
  ];

  return (
    <div className="max-w-6xl">
      <div className="mb-8">
        <h1 className="font-display text-4xl font-bold" style={{ color: 'var(--text-primary)' }}>
          Good {getGreeting()}, <span className="gradient-text">{user?.display_name}</span>
        </h1>
        <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Here's your study overview.
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((card, i) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="glass-card p-5"
          >
            <div className="flex items-center gap-2 mb-3">
              <card.icon size={16} style={{ color: card.color }} />
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{card.label}</span>
            </div>
            <p className="font-display text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
              {card.value}
            </p>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6 lg:col-span-2"
        >
          <h2 className="font-display font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Study Activity
          </h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={getWeekData()} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <XAxis dataKey="day" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)', borderRadius: 8 }}
                  labelStyle={{ color: 'var(--text-secondary)' }}
                  itemStyle={{ color: 'var(--accent-primary)' }}
                />
                <Bar dataKey="hours" fill="url(#barGrad)" radius={[4, 4, 0, 0]} />
                <defs>
                  <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--accent-primary)" stopOpacity={0.8} />
                    <stop offset="100%" stopColor="var(--accent-primary)" stopOpacity={0.2} />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Recent rooms */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-semibold" style={{ color: 'var(--text-primary)' }}>My Rooms</h2>
            <Link href={ROUTES.ROOMS}>
              <button className="text-xs flex items-center gap-1" style={{ color: 'var(--accent-primary)' }}>
                View all <ArrowRight size={12} />
              </button>
            </Link>
          </div>

          <div className="space-y-3">
            {rooms?.items.map((room) => (
              <Link key={room.id} href={ROUTES.ROOM(room.id)}>
                <div
                  className="p-3 rounded-xl cursor-pointer transition-all"
                  style={{ background: 'rgba(255,255,255,0.03)' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(79,255,218,0.06)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{room.name}</span>
                    {room.has_active_session && (
                      <span className="presence-dot" />
                    )}
                  </div>
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                    {room.member_count} members
                  </p>
                </div>
              </Link>
            ))}

            <Link href={ROUTES.ROOM_NEW}>
              <button
                className="w-full p-3 rounded-xl flex items-center justify-center gap-2 text-sm transition-all"
                style={{ border: '1px dashed var(--border-subtle)', color: 'var(--text-muted)' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--border-accent)'; e.currentTarget.style.color = 'var(--accent-primary)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-subtle)'; e.currentTarget.style.color = 'var(--text-muted)'; }}
              >
                <Plus size={14} /> New Room
              </button>
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'morning';
  if (hour < 17) return 'afternoon';
  return 'evening';
}

function getWeekData(): Array<{ day: string; hours: number }> {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  return days.map((day) => ({
    day,
    hours: parseFloat((Math.random() * 4).toFixed(1)),
  }));
}
