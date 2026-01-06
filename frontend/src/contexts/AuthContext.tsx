import { createContext, useContext, useState, useEffect, useRef, type ReactNode } from 'react';
import {
  type UserInfo,
  getCurrentUser,
  logout as apiLogout,
  setAuthToken,
  setAuthSession,
  getAuthToken,
  getAccessTokenExpiry,
  getRefreshToken,
  isAuthenticated as checkIsAuthenticated,
  refreshSession,
} from '@/services/api';

type AuthContextType = {
  user: UserInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  authType: 'oauth' | 'api_token' | null;
  login: (token: string, options?: { refreshToken?: string; expiresAt?: string }) => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authType, setAuthType] = useState<'oauth' | 'api_token' | null>(null);
  const refreshTimeoutRef = useRef<number | null>(null);

  const getExpiryMs = (expiry: string) => {
    const hasTimezone = /[zZ]|[+-]\d{2}:\d{2}$/.test(expiry);
    const normalized = hasTimezone ? expiry : `${expiry}Z`;
    return new Date(normalized).getTime();
  };

  const refreshUser = async () => {
    if (!checkIsAuthenticated()) {
      setUser(null);
      setIsAuthenticated(false);
      setAuthType(null);
      setIsLoading(false);
      return;
    }

    try {
      const response = await getCurrentUser();
      setUser(response.user);
      setIsAuthenticated(true);
      setAuthType(response.auth_type);
    } catch (error) {
      console.error('Failed to get user info:', error);
      setUser(null);
      setIsAuthenticated(false);
      setAuthType(null);
      // Token might be invalid, clear it
      setAuthToken(null);
      if (refreshTimeoutRef.current) {
        window.clearTimeout(refreshTimeoutRef.current);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const scheduleRefresh = () => {
    const expiry = getAccessTokenExpiry();
    const refreshToken = getRefreshToken();
    if (!expiry || !refreshToken) {
      return;
    }

    const expiresAtMs = getExpiryMs(expiry);
    const now = Date.now();
    const bufferMs = 60 * 1000;
    const delay = Math.max(expiresAtMs - now - bufferMs, 0);

    if (refreshTimeoutRef.current) {
      window.clearTimeout(refreshTimeoutRef.current);
    }

    refreshTimeoutRef.current = window.setTimeout(async () => {
      try {
        const latestRefreshToken = getRefreshToken();
        if (!latestRefreshToken) {
          throw new Error('Missing refresh token');
        }
        await refreshSession(latestRefreshToken);
        await refreshUser();
        scheduleRefresh();
      } catch (error) {
        console.error('Auto refresh failed:', error);
        setAuthToken(null);
        setUser(null);
        setIsAuthenticated(false);
        setAuthType(null);
        if (refreshTimeoutRef.current) {
          window.clearTimeout(refreshTimeoutRef.current);
        }
      }
    }, delay);
  };

  const login = (token: string, options?: { refreshToken?: string; expiresAt?: string }) => {
    if (options?.refreshToken && options?.expiresAt) {
      setAuthSession(token, options.refreshToken, options.expiresAt);
      scheduleRefresh();
    } else {
      setAuthToken(token);
    }
    refreshUser();
  };

  const logout = async () => {
    try {
      await apiLogout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      if (refreshTimeoutRef.current) {
        window.clearTimeout(refreshTimeoutRef.current);
      }
      setUser(null);
      setIsAuthenticated(false);
      setAuthType(null);
    }
  };

  useEffect(() => {
    // Check if there's a token on mount
    if (getAuthToken()) {
      refreshUser();
      scheduleRefresh();
    } else {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    scheduleRefresh();
    return () => {
      if (refreshTimeoutRef.current) {
        window.clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, [isAuthenticated, authType]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        authType,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
