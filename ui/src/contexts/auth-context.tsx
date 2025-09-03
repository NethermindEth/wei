"use client";

import * as React from "react";
import { AuthService, User } from "../services/auth";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; username?: string; first_name?: string; last_name?: string }) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = React.useState<User | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  // Initialize auth state on mount
  React.useEffect(() => {
    const initAuth = async () => {
      try {
        // Check if we're in the browser environment
        if (typeof window === 'undefined') {
          setIsLoading(false);
          return;
        }

        // Clear any invalid data from localStorage first
        try {
          AuthService.clearInvalidData();
        } catch (error) {
          console.warn('Failed to clear invalid data:', error);
        }

        const isAuth = AuthService.isAuthenticated();
        
        if (isAuth) {
          try {
            // Fetch fresh user profile from server
            const user = await AuthService.getCurrentUserProfile();
            setUser(user);
          } catch (error) {
            console.error('Failed to fetch user profile:', error);
            // Clear invalid auth state
            AuthService.logout();
            setUser(null);
          }
        } else {
          // Clear invalid auth state
          AuthService.logout();
          setUser(null);
        }
      } catch (error) {
        console.error("Auth initialization error:", error);
        AuthService.logout();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    // Use a small delay to ensure DOM is ready
    const timer = setTimeout(initAuth, 100);
    
    // Listen for storage changes (for cross-tab authentication)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'wei_user' || e.key === 'wei_access_token') {
        initAuth();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      clearTimeout(timer);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // Set up token refresh interval
  React.useEffect(() => {
    if (!user) return;

    const refreshInterval = setInterval(async () => {
      try {
        await AuthService.refreshToken();
      } catch (error) {
        console.error("Token refresh failed:", error);
        // If refresh fails, logout user
        logout();
      }
    }, 15 * 60 * 1000); // Refresh every 15 minutes

    return () => clearInterval(refreshInterval);
  }, [user]);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await AuthService.login({ email, password });
      
      // Ensure the user state is updated immediately
      setUser(response.user);
      
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: { email: string; password: string; username?: string; first_name?: string; last_name?: string }) => {
    setIsLoading(true);
    try {
      await AuthService.register(data);
      // After successful registration, automatically log in
      const response = await AuthService.login({ email: data.email, password: data.password });
      setUser(response.user);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    AuthService.logout();
    setUser(null);
  };

  const refreshToken = async () => {
    try {
      await AuthService.refreshToken();
    } catch (error) {
      console.error("Token refresh failed:", error);
      logout();
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
