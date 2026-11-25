import { useEffect, useMemo, useState, type ReactNode } from "react";

import { ApiError, apiRequest, clearAccessToken, getAccessToken, storeAccessToken } from "@/api/client";
import type { TokenResponse, User } from "@/api/types";
import { AuthContext, type AuthContextValue } from "@/contexts/auth-store";


export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(() => Boolean(getAccessToken()));
  const [sessionError, setSessionError] = useState("");
  const [sessionAttempt, setSessionAttempt] = useState(0);

  useEffect(() => {
    if (!getAccessToken()) {
      setLoading(false);
      return;
    }
    let active = true;
    setSessionError("");
    apiRequest<User>("/auth/me", { authenticated: true })
      .then((currentUser) => {
        if (active) setUser(currentUser);
      })
      .catch((reason: unknown) => {
        if (!active) return;
        if (reason instanceof ApiError && reason.status === 401) {
          clearAccessToken();
          setUser(null);
          return;
        }
        setSessionError("Clarifi cannot reach the API. Check the service and try again.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [sessionAttempt]);

  useEffect(() => {
    const handleUnauthorized = () => setUser(null);
    window.addEventListener("clarifi:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("clarifi:unauthorized", handleUnauthorized);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      sessionError,
      retrySession: () => {
        setLoading(true);
        setSessionAttempt((current) => current + 1);
      },
      login: async (email, password) => {
        const response = await apiRequest<TokenResponse>("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });
        storeAccessToken(response.access_token);
        setUser(response.user);
      },
      register: async (fullName, email, password) => {
        const response = await apiRequest<TokenResponse>("/auth/register", {
          method: "POST",
          body: JSON.stringify({ full_name: fullName, email, password }),
        });
        storeAccessToken(response.access_token);
        setUser(response.user);
      },
      logout: () => {
        clearAccessToken();
        setUser(null);
      },
    }),
    [loading, sessionError, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
