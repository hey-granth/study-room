'use client';

import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Timer, TrendingUp, Calendar, Award } from 'lucide-react';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';
import { formatDurationShort } from '@/lib/utils';
import { QUERY_KEYS } from '@/constants';
import type { UserSessionStats } from '@/types/api';

export default function ProfilePage() {
  const { user } = useAuthStore();

  const { data: stats } = useQuery({
    queryKey: [QUERY_KEYS.USER_STATS],
    queryFn: async () => {
      const res = await api.get<UserSessionStats>('/sessions/me/stats');
      return res.data;
    },
  });

  const achievements = [
    { icon: '🔥', title: 'First Session', desc: 'Completed your first study session', unlocked: (stats?.total_sessions ?? 0) >= 1 },
    { icon: '⏰', title: 'Hour Scholar', desc: 'Studied for a total of 1 hour', unlocked: (stats?.total_study_seconds ?? 0) >= 3600 },
    { icon: '📚', title: 'Consistent', desc: 'Studied 3 days in a row', unlocked: (stats?.sessions_this_week ?? 0) >= 3 },
    { icon: '🏆', title: 'Deep Focus', desc: 'Completed a 2-hour session', unlocked: (stats?.longest_session_seconds ?? 0) >= 7200 },
  ];

  return (
    <div className="max-w-3xl">
      <h1 className="font-display text-4xl font-bold mb-8" style={{ color: 'var(--text-primary)' }}>Profile</h1>

      {/* Avatar + info */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card-elevated p-8 mb-6 flex items-center gap-6"
      >
        <div className="w-20 h-20 rounded-full flex items-center justify-center text-3xl font-bold flex-shrink-0"
          style={{ background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))', color: '#0A0E1A' }}>
          {user?.display_name?.[0]?.toUpperCase() ?? 'U'}
        </div>
        <div>
          <h2 className="font-display text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{user?.display_name}</h2>
          <p style={{ color: 'var(--text-muted)' }}>@{user?.username}</p>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>{user?.email}</p>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[
          { icon: Timer, label: 'Total Study Time', value: formatDurationShort(stats?.total_study_seconds ?? 0), color: 'var(--accent-primary)' },
          { icon: TrendingUp, label: 'Avg Session', value: formatDurationShort(stats?.average_session_seconds ?? 0), color: 'var(--accent-secondary)' },
          { icon: Calendar, label: 'Total Sessions', value: stats?.total_sessions ?? 0, color: '#a78bfa' },
          { icon: Award, label: 'Best Session', value: formatDurationShort(stats?.longest_session_seconds ?? 0), color: '#fb923c' },
        ].map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="glass-card p-5"
          >
            <s.icon size={16} style={{ color: s.color }} className="mb-3" />
            <p className="font-display text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{s.value}</p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{s.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Achievements */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card p-6"
      >
        <h2 className="font-display font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Achievements</h2>
        <div className="grid grid-cols-2 gap-3">
          {achievements.map((a) => (
            <div key={a.title}
              className="p-4 rounded-xl flex items-start gap-3 transition-all"
              style={{
                background: a.unlocked ? 'rgba(79,255,218,0.06)' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${a.unlocked ? 'var(--border-accent)' : 'var(--border-subtle)'}`,
                opacity: a.unlocked ? 1 : 0.4,
              }}
            >
              <span className="text-2xl">{a.icon}</span>
              <div>
                <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{a.title}</p>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{a.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
