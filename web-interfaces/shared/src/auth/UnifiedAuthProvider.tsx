/**
 * Unified Authentication Provider
 *
 * Consolidated authentication provider that replaces all existing auth implementations
 * with a single, consistent system serving all TTA interfaces.
 */

import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import { apiClient } from '../api/client';

// Unified Types
export enum UserRole {
  PATIENT = 'patient',
  CLINICIAN = 'clinician',
  ADMIN = 'admin',
  STAKEHOLDER = 'stakeholder',
  DEVELOPER = 'developer'
}

export enum InterfaceType {
  PATIENT = 'patient',
  CLINICAL = 'clinical',
  ADMIN = 'admin',
  PUBLIC = 'public',
  DEVELOPER = 'developer'
}

export enum Permission {
  // Patient permissions
  CREATE_CHARACTER = 'create_character',
  VIEW_PROGRESS = 'view_progress',
  ACCESS_THERAPEUTIC_CONTENT = 'access_therapeutic_content',

  // Clinical permissions
  VIEW_PATIENT_DATA = 'view_patient_data',
  MANAGE_THERAPEUTIC_SESSIONS = 'manage_therapeutic_sessions',
  ACCESS_CRISIS_TOOLS = 'access_crisis_tools',
  GENERATE_REPORTS = 'generate_reports',

  // Admin permissions
  MANAGE_USERS = 'manage_users',
  MANAGE_SYSTEM_CONFIG = 'manage_system_config',
  VIEW_AUDIT_LOGS = 'view_audit_logs',
  MANAGE_ROLES = 'manage_roles',

  // Developer permissions
  ACCESS_DEBUG_TOOLS = 'access_debug_tools',
  MANAGE_API_KEYS = 'manage_api_keys',
  VIEW_SYSTEM_METRICS = 'view_system_metrics'
}

export interface UserProfile {
  firstName?: string;
  lastName?: string;
  organization?: string;
  therapeuticPreferences?: {
    preferredFrameworks: string[];
    intensityLevel: string;
    privacySettings: {
      shareProgress: boolean;
      allowResearchParticipation: boolean;
    };
  };
  uiPreferences?: {
    theme: string;
    accessibilitySettings: {
      highContrast: boolean;
      largeText: boolean;
      screenReaderSupport: boolean;
    };
    language: string;
  };
}

export interface UnifiedUser {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  permissions: Permission[];
  interfaceAccess: InterfaceType[];
  profile: UserProfile;
  mfaEnabled: boolean;
  mfaVerified?: boolean;
  lastLogin?: string;
  isActive: boolean;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
  refreshExpiresIn: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
  interfaceType: InterfaceType;
  deviceId?: string;
  rememberMe?: boolean;
}

export interface SessionInfo {
  sessionId: string;
  userId: string;
  interfaceType: InterfaceType;
  createdAt: string;
  lastActivity: string;
  expiresAt: string;
  isActive: boolean;
}

// Context Type
export interface UnifiedAuthContextType {
  // Authentication State
  user: UnifiedUser | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Authentication Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
  clearError: () => void;

  // Permission Helpers
  hasRole: (role: UserRole) => boolean;
  hasPermission: (permission: Permission) => boolean;
  hasInterfaceAccess: (interfaceType: InterfaceType) => boolean;

  // Profile Management
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>;

  // Session Management
  extendSession: () => Promise<void>;
  getSessionInfo: () => SessionInfo | null;

  // Display Helpers
  getDisplayName: () => string;
}

// Context
const UnifiedAuthContext = createContext<UnifiedAuthContextType | undefined>(undefined);

// Provider Props
interface UnifiedAuthProviderProps {
  children: ReactNode;
  apiBaseUrl: string;
  interfaceType: InterfaceType;
}

// Storage Keys - Standardized across all interfaces
const ACCESS_TOKEN_KEY = 'tta_access_token';
const REFRESH_TOKEN_KEY = 'tta_refresh_token';
const SESSION_ID_KEY = 'tta_session_id';

// Provider Component
export const UnifiedAuthProvider: React.FC<UnifiedAuthProviderProps> = ({
  children,
  apiBaseUrl,
  interfaceType
}) => {
  // State
  const [user, setUser] = useState<UnifiedUser | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);

  // Initialize authentication on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  // Auto-refresh token before expiration
  useEffect(() => {
    if (tokens && isAuthenticated) {
      const refreshTime = (tokens.expiresIn - 300) * 1000; // 5 minutes before expiration
      const timer = setTimeout(() => {
        refreshAuth().catch(console.error);
      }, refreshTime);

      return () => clearTimeout(timer);
    }
  }, [tokens, isAuthenticated]);

  const initializeAuth = async () => {
    try {
      const storedAccessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
      const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

      if (storedAccessToken && storedRefreshToken) {
        // Validate stored tokens
        await validateStoredTokens(storedAccessToken, storedRefreshToken);
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      clearAuthData();
    } finally {
      setIsLoading(false);
    }
  };

  const validateStoredTokens = async (accessToken: string, refreshToken: string) => {
    try {
      // Try to get user profile with stored token
      const response = await apiClient.get('/auth/profile', {
        headers: { Authorization: `Bearer ${accessToken}` },
        baseURL: apiBaseUrl
      });

      const userData = response.data;

      // Validate interface access
      if (!userData.interfaceAccess.includes(interfaceType)) {
        throw new Error(`No access to ${interfaceType} interface`);
      }

      setUser(userData);
      setTokens({
        accessToken,
        refreshToken,
        tokenType: 'bearer',
        expiresIn: 1800, // Default 30 minutes
        refreshExpiresIn: 604800 // Default 7 days
      });
      setIsAuthenticated(true);

    } catch (error) {
      // Token invalid, try refresh
      try {
        await performTokenRefresh(refreshToken);
      } catch (refreshError) {
        throw refreshError;
      }
    }
  };

  const login = async (credentials: LoginCredentials) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await apiClient.post('/auth/login', credentials, {
        baseURL: apiBaseUrl
      });

      const { user: userData, tokens: tokenData, sessionId } = response.data;

      // Validate interface access
      if (!userData.interfaceAccess.includes(interfaceType)) {
        throw new Error(`Access denied to ${interfaceType} interface`);
      }

      // Store tokens
      localStorage.setItem(ACCESS_TOKEN_KEY, tokenData.accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, tokenData.refreshToken);
      localStorage.setItem(SESSION_ID_KEY, sessionId);

      // Update state
      setUser(userData);
      setTokens(tokenData);
      setIsAuthenticated(true);
      setSessionInfo({
        sessionId,
        userId: userData.id,
        interfaceType,
        createdAt: new Date().toISOString(),
        lastActivity: new Date().toISOString(),
        expiresAt: new Date(Date.now() + tokenData.expiresIn * 1000).toISOString(),
        isActive: true
      });

    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || 'Login failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      const sessionId = localStorage.getItem(SESSION_ID_KEY);
      if (sessionId) {
        await apiClient.post('/auth/logout', { sessionId }, {
          headers: tokens ? { Authorization: `Bearer ${tokens.accessToken}` } : {},
          baseURL: apiBaseUrl
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuthData();
    }
  };

  const refreshAuth = async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    await performTokenRefresh(refreshToken);
  };

  const performTokenRefresh = async (refreshToken: string) => {
    try {
      const response = await apiClient.post('/auth/refresh', {
        refreshToken
      }, {
        baseURL: apiBaseUrl
      });

      const tokenData = response.data;

      // Store new tokens
      localStorage.setItem(ACCESS_TOKEN_KEY, tokenData.accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, tokenData.refreshToken);

      setTokens(tokenData);

      // Get updated user profile
      const profileResponse = await apiClient.get('/auth/profile', {
        headers: { Authorization: `Bearer ${tokenData.accessToken}` },
        baseURL: apiBaseUrl
      });

      setUser(profileResponse.data);

    } catch (error) {
      clearAuthData();
      throw error;
    }
  };

  const clearAuthData = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(SESSION_ID_KEY);
    setUser(null);
    setTokens(null);
    setIsAuthenticated(false);
    setSessionInfo(null);
    setError(null);
  };

  const clearError = () => setError(null);

  // Permission helpers
  const hasRole = useCallback((role: UserRole): boolean => {
    return user?.role === role;
  }, [user]);

  const hasPermission = useCallback((permission: Permission): boolean => {
    return user?.permissions?.includes(permission) || false;
  }, [user]);

  const hasInterfaceAccess = useCallback((interfaceType: InterfaceType): boolean => {
    return user?.interfaceAccess?.includes(interfaceType) || false;
  }, [user]);

  // Profile management
  const updateProfile = async (updates: Partial<UserProfile>) => {
    if (!tokens) throw new Error('Not authenticated');

    try {
      const response = await apiClient.put('/auth/profile', updates, {
        headers: { Authorization: `Bearer ${tokens.accessToken}` },
        baseURL: apiBaseUrl
      });

      setUser(response.data);
    } catch (error) {
      console.error('Profile update error:', error);
      throw error;
    }
  };

  // Session management
  const extendSession = async () => {
    if (!tokens || !sessionInfo) throw new Error('No active session');

    try {
      await apiClient.post('/auth/extend-session', {
        sessionId: sessionInfo.sessionId
      }, {
        headers: { Authorization: `Bearer ${tokens.accessToken}` },
        baseURL: apiBaseUrl
      });

      // Update session info
      setSessionInfo({
        ...sessionInfo,
        lastActivity: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 30 * 60 * 1000).toISOString() // Extend by 30 minutes
      });
    } catch (error) {
      console.error('Session extension error:', error);
      throw error;
    }
  };

  const getSessionInfo = (): SessionInfo | null => sessionInfo;

  // Display helpers
  const getDisplayName = (): string => {
    if (!user) return '';

    if (user.profile.firstName && user.profile.lastName) {
      return `${user.profile.firstName} ${user.profile.lastName}`;
    } else if (user.profile.firstName) {
      return user.profile.firstName;
    } else {
      return user.username;
    }
  };

  const contextValue: UnifiedAuthContextType = {
    // State
    user,
    tokens,
    isAuthenticated,
    isLoading,
    error,

    // Actions
    login,
    logout,
    refreshAuth,
    clearError,

    // Permission helpers
    hasRole,
    hasPermission,
    hasInterfaceAccess,

    // Profile management
    updateProfile,

    // Session management
    extendSession,
    getSessionInfo,

    // Display helpers
    getDisplayName
  };

  return (
    <UnifiedAuthContext.Provider value={contextValue}>
      {children}
    </UnifiedAuthContext.Provider>
  );
};

// Hook
export const useUnifiedAuth = (): UnifiedAuthContextType => {
  const context = useContext(UnifiedAuthContext);
  if (context === undefined) {
    throw new Error('useUnifiedAuth must be used within a UnifiedAuthProvider');
  }
  return context;
};

// Export for backward compatibility
export const useAuth = useUnifiedAuth;
