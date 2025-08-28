import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';
import { RootState } from '../../store/store';
import { verifyToken } from '../../store/slices/authSlice';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
  requiredPermissions?: string[];
  fallbackPath?: string;
}

/**
 * ProtectedRoute Component
 * 
 * Wraps components that require authentication and/or specific permissions.
 * Automatically verifies tokens and redirects unauthorized users.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  requiredPermissions = [],
  fallbackPath = '/auth/login',
}) => {
  const dispatch = useDispatch();
  const location = useLocation();
  const { isAuthenticated, user, accessToken, isLoading } = useSelector(
    (state: RootState) => state.auth
  );
  const [isVerifying, setIsVerifying] = useState(true);

  useEffect(() => {
    const verifyAuthentication = async () => {
      if (accessToken && !user) {
        // We have a token but no user data, verify the token
        try {
          await dispatch(verifyToken() as any);
        } catch (error) {
          console.error('Token verification failed:', error);
        }
      }
      setIsVerifying(false);
    };

    verifyAuthentication();
  }, [dispatch, accessToken, user]);

  // Show loading spinner while verifying authentication
  if (isLoading || isVerifying) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verifying authentication...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !accessToken) {
    return (
      <Navigate
        to={fallbackPath}
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  // Check role requirements
  if (requiredRole && user?.role !== requiredRole) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-red-600 rounded-lg flex items-center justify-center">
            <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Access Denied
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            You don't have the required role ({requiredRole}) to access this page.
          </p>
          <button
            onClick={() => window.history.back()}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Check permission requirements
  if (requiredPermissions.length > 0 && user?.permissions) {
    const hasRequiredPermissions = requiredPermissions.every(permission =>
      user.permissions?.includes(permission)
    );

    if (!hasRequiredPermissions) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 bg-red-600 rounded-lg flex items-center justify-center">
              <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Insufficient Permissions
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              You don't have the required permissions to access this page.
            </p>
            <p className="mt-1 text-center text-xs text-gray-500">
              Required: {requiredPermissions.join(', ')}
            </p>
            <button
              onClick={() => window.history.back()}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              Go Back
            </button>
          </div>
        </div>
      );
    }
  }

  // All checks passed, render the protected content
  return <>{children}</>;
};

export default ProtectedRoute;
