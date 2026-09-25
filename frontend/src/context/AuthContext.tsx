/**
 * Global authentication state provider.
 *
 * On mount, if a token is already stored, it attempts to resolve the
 * current user (validating the token against the backend). Login stores
 * the JWT and fetches the user profile; logout clears local state only
 * (the backend issues short-lived stateless JWTs, so there is no
 * server-side session to invalidate).
 */

import { createContext, useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { getCurrentUser, login as loginRequest } from "../api/auth";
import { clearStoredToken, getStoredToken, setStoredToken } from "../api/client";
import type { CurrentUser } from "../types";

export interface AuthContextValue {
  user: CurrentUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const loadCurrentUser = useCallback(async () => {
    const token = getStoredToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch {
      // Token is invalid, expired, or the user no longer exists/is disabled.
      clearStoredToken();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCurrentUser();
  }, [loadCurrentUser]);

  const login = useCallback(async (email: string, password: string) => {
    const tokenResponse = await loginRequest({ email, password });
    setStoredToken(tokenResponse.access_token);
    const currentUser = await getCurrentUser();
    setUser(currentUser);
  }, []);

  const logout = useCallback(() => {
    clearStoredToken();
    setUser(null);
  }, []);

  const value: AuthContextValue = {
    user,
    isAuthenticated: user !== null,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}