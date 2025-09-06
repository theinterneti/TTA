import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { jwtDecode } from 'jose';
import { apiClient } from '../api/client';

// Import unified auth types and provider
import {
  UnifiedAuthProvider,
  useUnifiedAuth,
  UnifiedUser,
  UserRole,
  InterfaceType,
  Permission
} from './UnifiedAuthProvider';

// Backward compatibility types
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'patient' | 'clinician' | 'admin' | 'stakeholder' | 'developer';
  permissions: string[];
  profile?: {
    firstName?: string;
    lastName?: string;
    organization?: string;
  };
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
  apiBaseUrl: string;
  interfaceType: 'patient' | 'clinical' | 'admin' | 'public' | 'stakeholder' | 'docs';
}

export const AuthProvider: React.FC<AuthProviderProps> = ({
  children,
  apiBaseUrl,
  interfaceType,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = localStorage.getItem(`tta_token_${interfaceType}`);
        if (storedToken) {
          const decoded = jwtDecode(storedToken);
          const currentTime = Date.now() / 1000;

          if (decoded.exp && decoded.exp > currentTime) {
            setToken(storedToken);
            await loadUserProfile(storedToken);
          } else {
            // Token expired, remove it
            localStorage.removeItem(`tta_token_${interfaceType}`);
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        localStorage.removeItem(`tta_token_${interfaceType}`);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, [interfaceType]);

  const loadUserProfile = async (authToken: string) => {
    try {
      const response = await apiClient.get('/auth/profile', {
        headers: { Authorization: `Bearer ${authToken}` },
        baseURL: apiBaseUrl,
      });
      setUser(response.data);
    } catch (error) {
      console.error('Error loading user profile:', error);
      throw error;
    }
  };

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await apiClient.post(
        '/auth/login',
        { username, password, interface_type: interfaceType },
        { baseURL: apiBaseUrl }
      );

      const { access_token, user: userData } = response.data;

      // Validate user role matches interface type
      if (!isValidRoleForInterface(userData.role, interfaceType)) {
        throw new Error(`Invalid role ${userData.role} for ${interfaceType} interface`);
      }

      setToken(access_token);
      setUser(userData);
      localStorage.setItem(`tta_token_${interfaceType}`, access_token);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem(`tta_token_${interfaceType}`);
  };

  const refreshToken = async () => {
    try {
      const response = await apiClient.post(
        '/auth/refresh',
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
          baseURL: apiBaseUrl,
        }
      );

      const { access_token } = response.data;
      setToken(access_token);
      localStorage.setItem(`tta_token_${interfaceType}`, access_token);
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
      throw error;
    }
  };

  const hasPermission = (permission: string): boolean => {
    return user?.permissions?.includes(permission) || false;
  };

  const hasRole = (role: string): boolean => {
    return user?.role === role;
  };

  const isValidRoleForInterface = (userRole: string, interface_type: string): boolean => {
    const roleMapping = {
      patient: ['patient'],
      clinical: ['clinician', 'admin'],
      admin: ['admin'],
      public: [], // No authentication required
      stakeholder: ['stakeholder', 'admin'],
      docs: ['developer', 'admin'],
    };

    const allowedRoles = roleMapping[interface_type as keyof typeof roleMapping];
    return allowedRoles.length === 0 || allowedRoles.includes(userRole);
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
    logout,
    refreshToken,
    hasPermission,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;
