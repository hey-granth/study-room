/** Auth hook — wraps auth store with API calls. */

'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';
import type { LoginRequest, RegisterRequest, User, UserWithToken } from '@/types/api';
import { ROUTES } from '@/constants';

/**
 * Hook providing auth state and operations.
 * @returns Auth state, login, register, logout functions.
 */
export function useAuth() {
  const router = useRouter();
  const { user, isAuthenticated, setAuth, clearAuth, updateUser } = useAuthStore();

  const registerMutation = useMutation({
    mutationFn: async (data: RegisterRequest): Promise<UserWithToken> => {
      const res = await api.post<UserWithToken>('/auth/register', data);
      return res.data;
    },
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token);
      router.push(ROUTES.DASHBOARD);
    },
  });

  const loginMutation = useMutation({
    mutationFn: async (data: LoginRequest): Promise<UserWithToken> => {
      const res = await api.post<UserWithToken>('/auth/login', data);
      return res.data;
    },
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token);
      router.push(ROUTES.DASHBOARD);
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async (): Promise<void> => {
      await api.post('/auth/logout');
    },
    onSettled: () => {
      clearAuth();
      router.push(ROUTES.HOME);
    },
  });

  return {
    user,
    isAuthenticated,
    register: registerMutation.mutateAsync,
    login: loginMutation.mutateAsync,
    logout: logoutMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
  };
}
