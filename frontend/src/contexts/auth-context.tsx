import { useEffect, useMemo, useState, type ReactNode } from "react";

import { apiRequest, clearAccessToken, getAccessToken, storeAccessToken } from "@/api/client";
import type { TokenResponse, User } from "@/api/types";
import { AuthContext, type AuthContextValue } from "@/contexts/auth-store";


export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(() => Boolean(getAccessToken()));

  useEffect(() => {
    if (!getAccessToken()) return;
    let active = true;
    apiRequest<User>("/auth/me", { authenticated: true })
      .then((currentUser) => {
        if (active) setUser(currentUser);
      })
      .catch(() => clearAccessToken())
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      login: async (email, password) => {
        const response = await apiRequest<TokenResponse>("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });
        storeAccessToken(response.access_token);
        setUser(response.user);
      },
      logout: () => {
        clearAccessToken();
        setUser(null);
      },
    }),
    [loading, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
