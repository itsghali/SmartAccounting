"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { setTokens, clearTokens, isAuthenticated } from "@/lib/auth";
import type { User, TokenResponse } from "@/types";

export function useCurrentUser() {
  return useQuery<User>({
    queryKey: ["current-user"],
    queryFn: async () => {
      const { data } = await api.get("/auth/me");
      return data;
    },
    enabled: isAuthenticated(),
    retry: false,
  });
}

export function useLogin() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (creds: { email: string; password: string }) => {
      const { data } = await api.post<TokenResponse>("/auth/login", creds);
      return data;
    },
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      queryClient.invalidateQueries({ queryKey: ["current-user"] });
      router.push("/");
    },
  });
}

export function useRegister() {
  const router = useRouter();

  return useMutation({
    mutationFn: async (data: {
      email: string;
      password: string;
      first_name: string;
      last_name: string;
      company_name: string;
    }) => {
      const { data: resp } = await api.post<TokenResponse>("/auth/register", data);
      return resp;
    },
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      router.push("/");
    },
  });
}

export function useLogout() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return () => {
    clearTokens();
    queryClient.clear();
    router.push("/login");
  };
}
