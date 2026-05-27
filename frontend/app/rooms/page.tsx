'use client';

import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useState } from 'react';
import { Plus, Search, Users, Zap } from 'lucide-react';
import { api } from '@/lib/api';
import { QUERY_KEYS, ROUTES } from '@/constants';
import type { Page, RoomSummary } from '@/types/api';

type FilterType = 'all' | 'owned' | 'joined';

export default function RoomsPage() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<FilterType>('all');

  const { data, isLoading } = useQuery({
    queryKey: [QUERY_KEYS.ROOMS, filter, search],
    queryFn: async () => {
      const params = new URLSearchParams({ filter_type: filter, size: '30' });
      if (search) params.set('search', search);
      const res = await api.get<Page<RoomSummary>>(`/rooms/?${params}`);
      return res.data;
    },
    staleTime: 30_000,
  });

  return (
    <div className="max-w-6xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-4xl font-bold" style={{ color: 'var(--text-primary)' }}>Study Rooms</h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
            {data?.total ?? 0} rooms available
          </p>
        </div>
        <Link href={ROUTES.ROOM_NEW}>
          <button className="btn-primary flex items-center gap-2">
            <Plus size={16} /> New Room
          </button>
        </Link>
      </div>

      {/* Filter + Search */}
      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search rooms..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-field pl-9"
          />
        </div>
        <div className="flex rounded-xl overflow-hidden" style={{ border: '1px solid var(--border-subtle)' }}>
          {(['all', 'joined', 'owned'] as FilterType[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className="px-4 py-2 text-sm font-medium capitalize transition-all"
              style={{
                background: filter === f ? 'rgba(79,255,218,0.12)' : 'transparent',
                color: filter === f ? 'var(--accent-primary)' : 'var(--text-muted)',
              }}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Rooms grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card h-36 animate-pulse" style={{ background: 'rgba(26,34,53,0.5)' }} />
          ))}
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.items.map((room, i) => (
            <RoomCard key={room.id} room={room} index={i} />
          ))}
          {data?.items.length === 0 && (
            <div className="col-span-3 text-center py-16" style={{ color: 'var(--text-muted)' }}>
              <p className="text-lg">No rooms found.</p>
              <Link href={ROUTES.ROOM_NEW}>
                <button className="btn-primary mt-4">Create the first one</button>
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function RoomCard({ room, index }: { room: RoomSummary; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -3 }}
    >
      <Link href={ROUTES.ROOM(room.id)}>
        <div
          className="glass-card p-5 h-full cursor-pointer transition-all"
          onMouseEnter={e => (e.currentTarget.style.borderColor = 'rgba(79,255,218,0.15)')}
          onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border-subtle)')}
        >
          <div className="flex items-start justify-between mb-3">
            <h3 className="font-display font-semibold text-lg leading-tight" style={{ color: 'var(--text-primary)' }}>
              {room.name}
            </h3>
            {room.has_active_session && (
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs"
                style={{ background: 'rgba(79,255,218,0.1)', color: 'var(--accent-primary)', border: '1px solid var(--border-accent)' }}>
                <span className="presence-dot" style={{ width: 6, height: 6 }} />
                Live
              </div>
            )}
          </div>

          {room.description && (
            <p className="text-sm mb-4 line-clamp-2" style={{ color: 'var(--text-secondary)' }}>
              {room.description}
            </p>
          )}

          <div className="flex items-center gap-4 mt-auto">
            <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
              <Users size={12} />
              {room.member_count}/{room.max_participants}
            </div>
            <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
              {room.is_public ? '🌐 Public' : '🔒 Private'}
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
