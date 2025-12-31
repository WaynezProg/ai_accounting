import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import {
  type UserInfo,
  getCurrentUser,
  logout as apiLogout,
  setAuthToken,
  getAuthToken,
  isAuthenticated as checkIsAuthenticated,
} from '@/services/api';

type AuthContextType = {
  user: UserInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  authType: 'oauth' | 'api_token' | null;
  login: (token: string) => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authType, setAuthType] = useState<'oauth' | 'api_token' | null>(null);

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
    } finally {
      setIsLoading(false);
    }
  };

  const login = (token: string) => {
    setAuthToken(token);
    refreshUser();
  };

  const logout = async () => {
    try {
      await apiLogout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      setAuthType(null);
    }
  };

  useEffect(() => {
    // Check if there's a token on mount
    if (getAuthToken()) {
      refreshUser();
    } else {
      setIsLoading(false);
    }
  }, []);

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
