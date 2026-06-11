// frontend/src/hooks/useAuth.ts

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/lib/api";

export function useAuth() {
  const { isAuthenticated, user, setUser, logout, hydrate } = useAuthStore();

  useEffect(() => { hydrate(); }, []);

  const { isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const { data } = await authApi.getMe();
      setUser(data);
      return data;
    },
    enabled: isAuthenticated && !user,
    retry: false,
  });

  return { user, isAuthenticated, isLoading, logout };
}