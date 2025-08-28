import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
import { RootState } from '../store/store';
import { verifyToken, clearAuth } from '../store/slices/authSlice';

interface AuthGuardOptions {
  requiredRole?: string;
  requiredPermissions?: string[];
  redirectTo?: string;
  autoRedirect?: boolean;
}

interface AuthGuardResult {
  isAuthenticated: boolean;
  isAuthorized: boolean;
  isLoading: boolean;
  user: any;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
  logout: () => void;
}

/**
 * useAuthGuard Hook
 * 
 * Provides authentication and authorization utilities for components.
 * Automatically handles token verification and permission checking.
 */
export const useAuthGuard = (options: AuthGuardOptions = {}): AuthGuardResult => {
  const {
    requiredRole,
    requiredPermissions = [],
    redirectTo = '/auth/login',
    autoRedirect = true,
  } = options;

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  
  const { isAuthenticated, user, accessToken, isLoading } = useSelector(
    (state: RootState) => state.auth
  );
  
  const [isVerifying, setIsVerifying] = useState(false);

  // Verify token on mount if we have one but no user data
  useEffect(() => {
    const verifyAuthentication = async () => {
      if (accessToken && !user && !isLoading) {
        setIsVerifying(true);
        try {
          await dispatch(verifyToken() as any);
        } catch (error) {
          console.error('Token verification failed:', error);
          if (autoRedirect) {
            navigate(redirectTo, { 
              state: { from: location.pathname },
              replace: true 
            });
          }
        } finally {
          setIsVerifying(false);
        }
      }
    };

    verifyAuthentication();
  }, [dispatch, accessToken, user, isLoading, navigate, redirectTo, location.pathname, autoRedirect]);

  // Check if user has specific role
  const hasRole = (role: string): boolean => {
    return user?.role === role;
  };

  // Check if user has specific permission
  const hasPermission = (permission: string): boolean => {
    return user?.permissions?.includes(permission) || false;
  };

  // Check if user has any of the specified permissions
  const hasAnyPermission = (permissions: string[]): boolean => {
    if (!user?.permissions) return false;
    return permissions.some(permission => user.permissions.includes(permission));
  };

  // Check if user has all of the specified permissions
  const hasAllPermissions = (permissions: string[]): boolean => {
    if (!user?.permissions) return false;
    return permissions.every(permission => user.permissions.includes(permission));
  };

  // Logout function
  const logout = () => {
    dispatch(clearAuth());
    if (autoRedirect) {
      navigate(redirectTo, { replace: true });
    }
  };

  // Check authorization based on requirements
  const isAuthorized = (() => {
    if (!isAuthenticated) return false;
    
    // Check role requirement
    if (requiredRole && !hasRole(requiredRole)) {
      return false;
    }
    
    // Check permission requirements
    if (requiredPermissions.length > 0 && !hasAllPermissions(requiredPermissions)) {
      return false;
    }
    
    return true;
  })();

  // Auto-redirect if not authorized
  useEffect(() => {
    if (!isLoading && !isVerifying && autoRedirect) {
      if (!isAuthenticated) {
        navigate(redirectTo, { 
          state: { from: location.pathname },
          replace: true 
        });
      } else if (!isAuthorized) {
        navigate('/unauthorized', { replace: true });
      }
    }
  }, [isAuthenticated, isAuthorized, isLoading, isVerifying, autoRedirect, navigate, redirectTo, location.pathname]);

  return {
    isAuthenticated,
    isAuthorized,
    isLoading: isLoading || isVerifying,
    user,
    hasRole,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    logout,
  };
};

/**
 * useRequireAuth Hook
 * 
 * Simplified hook that requires authentication and redirects if not authenticated.
 */
export const useRequireAuth = (redirectTo: string = '/auth/login') => {
  return useAuthGuard({ autoRedirect: true, redirectTo });
};

/**
 * useRequireRole Hook
 * 
 * Hook that requires a specific role and redirects if not authorized.
 */
export const useRequireRole = (role: string, redirectTo: string = '/auth/login') => {
  return useAuthGuard({ requiredRole: role, autoRedirect: true, redirectTo });
};

/**
 * useRequirePermissions Hook
 * 
 * Hook that requires specific permissions and redirects if not authorized.
 */
export const useRequirePermissions = (permissions: string[], redirectTo: string = '/auth/login') => {
  return useAuthGuard({ requiredPermissions: permissions, autoRedirect: true, redirectTo });
};

/**
 * useOptionalAuth Hook
 * 
 * Hook that provides auth state without automatic redirects.
 */
export const useOptionalAuth = () => {
  return useAuthGuard({ autoRedirect: false });
};

export default useAuthGuard;
