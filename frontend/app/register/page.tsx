'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { BookOpen, Loader2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { ROUTES } from '@/constants';
import type { AxiosError } from 'axios';
import type { ApiError } from '@/types/api';

const registerSchema = z.object({
  email: z.string().email('Enter a valid email'),
  username: z
    .string()
    .min(3, 'At least 3 characters')
    .max(50)
    .regex(/^[a-zA-Z0-9_-]+$/, 'Only letters, numbers, _ and -'),
  display_name: z.string().min(1, 'Display name is required').max(100),
  password: z
    .string()
    .min(8, 'At least 8 characters')
    .regex(/[A-Z]/, 'Must include an uppercase letter')
    .regex(/[0-9]/, 'Must include a number'),
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const { register: registerUser, isRegistering, registerError } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({ resolver: zodResolver(registerSchema) });

  const onSubmit = async (data: RegisterForm) => {
    try {
      await registerUser(data);
    } catch {
      // Handled via registerError
    }
  };

  const apiError = registerError as AxiosError<ApiError> | null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card-elevated p-8"
    >
      <div className="flex items-center gap-2 mb-8">
        <BookOpen size={22} style={{ color: 'var(--accent-primary)' }} />
        <span className="font-display text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
          StudyRoom
        </span>
      </div>

      <h1 className="font-display text-3xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
        Create account
      </h1>
      <p className="mb-8 text-sm" style={{ color: 'var(--text-secondary)' }}>
        Join thousands of students focusing together.
      </p>

      {apiError && (
        <div
          className="mb-4 p-3 rounded-lg text-sm"
          style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}
        >
          {apiError.response?.data?.detail ?? 'Registration failed. Please try again.'}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Username</label>
            <input {...register('username')} placeholder="studyguru" className="input-field" />
            {errors.username && <p className="mt-1 text-xs" style={{ color: '#f87171' }}>{errors.username.message}</p>}
          </div>
          <div>
            <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Display Name</label>
            <input {...register('display_name')} placeholder="Alex Chen" className="input-field" />
            {errors.display_name && <p className="mt-1 text-xs" style={{ color: '#f87171' }}>{errors.display_name.message}</p>}
          </div>
        </div>

        <div>
          <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Email</label>
          <input {...register('email')} type="email" placeholder="you@example.com" className="input-field" autoComplete="email" />
          {errors.email && <p className="mt-1 text-xs" style={{ color: '#f87171' }}>{errors.email.message}</p>}
        </div>

        <div>
          <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>Password</label>
          <input {...register('password')} type="password" placeholder="Secure password" className="input-field" autoComplete="new-password" />
          {errors.password && <p className="mt-1 text-xs" style={{ color: '#f87171' }}>{errors.password.message}</p>}
        </div>

        <motion.button
          type="submit"
          disabled={isRegistering}
          className="btn-primary w-full flex items-center justify-center gap-2 py-3 mt-2"
          whileTap={{ scale: 0.98 }}
        >
          {isRegistering ? <Loader2 size={16} className="animate-spin" /> : null}
          {isRegistering ? 'Creating account...' : 'Create Account'}
        </motion.button>
      </form>

      <p className="mt-6 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>
        Already have an account?{' '}
        <Link href={ROUTES.LOGIN} style={{ color: 'var(--accent-primary)' }} className="font-semibold">
          Sign in
        </Link>
      </p>
    </motion.div>
  );
}
