/** TanStack Query client configuration. */

import { QueryClient } from '@tanstack/react-query';
import { STALE_TIMES } from '@/constants';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: STALE_TIMES.ROOMS,
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});
