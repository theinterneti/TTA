import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "../store/store";
import {
  verifyToken,
  refreshToken,
  clearAuth,
  login,
  logout,
} from "../store/slices/authSlice";

interface AuthContextType {
  // Auth state
  isAuthenticated: boolean;
  isLoading: boolean;
  user: any;
  error: string | null;

  // Auth actions
  login: (credentials: { username: string; password: string }) => Promise<any>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
  clearError: () => void;

  // Permission helpers
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;

  // Token management
  getAccessToken: () => string | null;
  isTokenExpired: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider Component
 *
 * Provides authentication context and automatic token management
 * throughout the application.
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const dispatch = useDispatch();
  const {
    isAuthenticated,
    isLoading,
    user,
    error,
    accessToken,
    tokenExpiresAt,
  } = useSelector((state: RootState) => state.auth);

  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize authentication on app start
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem(
        process.env.REACT_APP_JWT_STORAGE_KEY || "tta_access_token"
      );

      if (token && !user) {
        try {
          await dispatch(verifyToken() as any);
        } catch (error) {
          console.error("Initial token verification failed:", error);
          dispatch(clearAuth());
        }
      }

      setIsInitialized(true);
    };

    initializeAuth();
  }, [dispatch, user]);

  // Set up automatic token refresh
  useEffect(() => {
    if (!isAuthenticated || !tokenExpiresAt) return;

    const refreshThreshold = 5 * 60 * 1000; // 5 minutes before expiration
    const timeUntilRefresh = tokenExpiresAt - Date.now() - refreshThreshold;

    if (timeUntilRefresh <= 0) {
      // Token is already expired or about to expire, refresh immediately
      handleRefreshAuth();
      return;
    }

    const refreshTimer = setTimeout(() => {
      handleRefreshAuth();
    }, timeUntilRefresh);

    return () => clearTimeout(refreshTimer);
  }, [isAuthenticated, tokenExpiresAt]);

  // Set up token expiration listener
  useEffect(() => {
    const handleTokenExpired = () => {
      dispatch(clearAuth());
    };

    window.addEventListener("auth:token-expired", handleTokenExpired);
    return () =>
      window.removeEventListener("auth:token-expired", handleTokenExpired);
  }, [dispatch]);

  // Auth actions
  const handleLogin = async (credentials: {
    username: string;
    password: string;
  }) => {
    return dispatch(login(credentials) as any);
  };

  const handleLogout = async () => {
    await dispatch(logout() as any);
  };

  const handleRefreshAuth = async () => {
    try {
      await dispatch(refreshToken() as any);
    } catch (error) {
      console.error("Token refresh failed:", error);
      dispatch(clearAuth());
    }
  };

  const handleClearError = () => {
    // This would need to be implemented in the auth slice
    // dispatch(clearError());
  };

  // Permission helpers
  const hasRole = (role: string): boolean => {
    return user?.role === role;
  };

  const hasPermission = (permission: string): boolean => {
    return user?.permissions?.includes(permission) || false;
  };

  const hasAnyPermission = (permissions: string[]): boolean => {
    if (!user?.permissions) return false;
    return permissions.some((permission) =>
      user.permissions!.includes(permission)
    );
  };

  const hasAllPermissions = (permissions: string[]): boolean => {
    if (!user?.permissions) return false;
    return permissions.every((permission) =>
      user.permissions!.includes(permission)
    );
  };

  // Token management
  const getAccessToken = (): string | null => {
    return accessToken;
  };

  const isTokenExpired = (): boolean => {
    if (!tokenExpiresAt) return false;
    return Date.now() >= tokenExpiresAt;
  };

  const contextValue: AuthContextType = {
    // Auth state
    isAuthenticated,
    isLoading: isLoading || !isInitialized,
    user,
    error,

    // Auth actions
    login: handleLogin,
    logout: handleLogout,
    refreshAuth: handleRefreshAuth,
    clearError: handleClearError,

    // Permission helpers
    hasRole,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,

    // Token management
    getAccessToken,
    isTokenExpired,
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

/**
 * useAuth Hook
 *
 * Custom hook to access authentication context.
 * Must be used within an AuthProvider.
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
};

/**
 * useAuthState Hook
 *
 * Simplified hook that only returns auth state without actions.
 */
export const useAuthState = () => {
  const { isAuthenticated, isLoading, user, error } = useAuth();
  return { isAuthenticated, isLoading, user, error };
};

/**
 * useAuthActions Hook
 *
 * Hook that only returns auth actions without state.
 */
export const useAuthActions = () => {
  const { login, logout, refreshAuth, clearError } = useAuth();
  return { login, logout, refreshAuth, clearError };
};

/**
 * usePermissions Hook
 *
 * Hook that only returns permission checking functions.
 */
export const usePermissions = () => {
  const { hasRole, hasPermission, hasAnyPermission, hasAllPermissions } =
    useAuth();
  return { hasRole, hasPermission, hasAnyPermission, hasAllPermissions };
};

export default AuthContext;
