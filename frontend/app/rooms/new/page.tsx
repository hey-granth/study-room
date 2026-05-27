'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { ROUTES } from '@/constants';
import type { RoomDetail } from '@/types/api';
import Link from 'next/link';

const schema = z.object({
  name: z.string().min(1, 'Room name is required').max(100),
  description: z.string().max(500).optional(),
  is_public: z.boolean(),
  max_participants: z.number().min(2).max(100),
});

type FormData = z.infer<typeof schema>;

export default function NewRoomPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { is_public: true, max_participants: 20 },
  });

  const isPublic = watch('is_public');

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const res = await api.post<RoomDetail>('/rooms/', data);
      router.push(ROUTES.ROOM(res.data.id));
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      setError(err.response?.data?.detail ?? 'Failed to create room');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <Link href={ROUTES.ROOMS}>
        <button className="flex items-center gap-2 text-sm mb-6 transition-colors"
          style={{ color: 'var(--text-muted)' }}
          onMouseEnter={e => e.currentTarget.style.color = 'var(--text-primary)'}
          onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
        >
          <ArrowLeft size={15} /> Back to rooms
        </button>
      </Link>

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-card-elevated p-8">
        <h1 className="font-display text-3xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
          Create Study Room
        </h1>
        <p className="mb-8 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Set up your virtual study space. An invite code will be generated automatically.
        </p>

        {error && (
          <div className="mb-4 p-3 rounded-lg text-sm"
            style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Room Name *</label>
            <input {...register('name')} placeholder="e.g. CS Finals Study Group" className="input-field" />
            {errors.name && <p className="mt-1 text-xs" style={{ color: '#f87171' }}>{errors.name.message}</p>}
          </div>

          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Description</label>
            <textarea
              {...register('description')}
              placeholder="What will you study in this room?"
              className="input-field resize-none"
              rows={3}
            />
          </div>

          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Max Participants</label>
            <input
              type="number"
              {...register('max_participants', { valueAsNumber: true })}
              min={2}
              max={100}
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>Visibility</label>
            <div className="flex gap-3">
              {[
                { value: true, label: '🌐 Public', desc: 'Anyone can discover and join' },
                { value: false, label: '🔒 Private', desc: 'Invite code required to join' },
              ].map(({ value, label, desc }) => (
                <button
                  key={String(value)}
                  type="button"
                  onClick={() => setValue('is_public', value)}
                  className="flex-1 p-4 rounded-xl text-left transition-all"
                  style={{
                    border: `1px solid ${isPublic === value ? 'var(--border-accent)' : 'var(--border-subtle)'}`,
                    background: isPublic === value ? 'rgba(79,255,218,0.06)' : 'transparent',
                  }}
                >
                  <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{label}</p>
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{desc}</p>
                </button>
              ))}
            </div>
          </div>

          <motion.button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full flex items-center justify-center gap-2 py-3"
            whileTap={{ scale: 0.98 }}
          >
            {isSubmitting ? <Loader2 size={16} className="animate-spin" /> : null}
            {isSubmitting ? 'Creating...' : 'Create Room'}
          </motion.button>
        </form>
      </motion.div>
    </div>
  );
}
