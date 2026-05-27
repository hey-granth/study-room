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

const loginSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(1, 'Password is required'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { login, isLoggingIn, loginError } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (data: LoginForm) => {
    try {
      await login(data);
    } catch {
      // Error handled via loginError
    }
  };

  const apiError = loginError as AxiosError<ApiError> | null;

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
        Welcome back
      </h1>
      <p className="mb-8 text-sm" style={{ color: 'var(--text-secondary)' }}>
        Sign in to continue to your study rooms.
      </p>

      {apiError && (
        <div
          className="mb-4 p-3 rounded-lg text-sm"
          style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}
        >
          {apiError.response?.data?.detail ?? 'Login failed. Please try again.'}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>
            Email
          </label>
          <input
            {...register('email')}
            type="email"
            placeholder="you@example.com"
            className="input-field"
            autoComplete="email"
          />
          {errors.email && (
            <p className="mt-1 text-xs" style={{ color: '#f87171' }}>{errors.email.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm mb-1.5" style={{ color: 'var(--text-secondary)' }}>
            Password
          </label>
          <input
            {...register('password')}
            type="password"
            placeholder="••••••••"
            className="input-field"
            autoComplete="current-password"
          />
          {errors.password && (
            <p className="mt-1 text-xs" style={{ color: '#f87171' }}>{errors.password.message}</p>
          )}
        </div>

        <motion.button
          type="submit"
          disabled={isLoggingIn}
          className="btn-primary w-full flex items-center justify-center gap-2 py-3 mt-2"
          whileTap={{ scale: 0.98 }}
        >
          {isLoggingIn ? <Loader2 size={16} className="animate-spin" /> : null}
          {isLoggingIn ? 'Signing in...' : 'Sign in'}
        </motion.button>
      </form>

      <p className="mt-6 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>
        {"Don't have an account? "}
        <Link href={ROUTES.REGISTER} style={{ color: 'var(--accent-primary)' }} className="font-semibold">
          Sign up
        </Link>
      </p>
    </motion.div>
  );
}
