import { createContext, useContext } from "react";

import type { User } from "@/api/types";

export type AuthContextValue = {
  user: User | null;
  loading: boolean;
  sessionError: string;
  retrySession: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
