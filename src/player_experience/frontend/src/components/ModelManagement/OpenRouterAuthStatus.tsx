import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import {
  showAuthModal,
  logout,
  refreshUserInfo,
} from '../../store/slices/openRouterAuthSlice';

interface OpenRouterAuthStatusProps {
  showFullDetails?: boolean;
  onAuthRequired?: () => void;
}

const OpenRouterAuthStatus: React.FC<OpenRouterAuthStatusProps> = ({
  showFullDetails = true,
  onAuthRequired,
}) => {
  const dispatch = useDispatch();
  const {
    isAuthenticated,
    authMethod,
    user,
    apiKeyValid,
    apiKeyValidatedAt,
    lastValidated,
    isLoading,
  } = useSelector((state: RootState) => state.openRouterAuth);

  // Refresh user info periodically if authenticated
  useEffect(() => {
    if (isAuthenticated && authMethod === 'oauth') {
      const interval = setInterval(() => {
        dispatch(refreshUserInfo() as any);
      }, 5 * 60 * 1000); // Refresh every 5 minutes

      return () => clearInterval(interval);
    }
  }, [isAuthenticated, authMethod, dispatch]);

  const handleAuthClick = () => {
    if (isAuthenticated) {
      // Show user menu or logout
      return;
    } else {
      onAuthRequired?.();
      dispatch(showAuthModal());
    }
  };

  const handleLogout = async () => {
    await dispatch(logout() as any);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const getAuthStatusColor = () => {
    if (isAuthenticated) return 'text-green-600 bg-green-50 border-green-200';
    return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  };

  const getAuthStatusText = () => {
    if (isAuthenticated) {
      return authMethod === 'oauth' ? 'OAuth Connected' : 'API Key Valid';
    }
    return 'Not Connected';
  };

  const getAuthIcon = () => {
    if (isAuthenticated) {
      return authMethod === 'oauth' ? '🔐' : '🔑';
    }
    return '⚠️';
  };

  if (!showFullDetails) {
    // Compact view for use in other components
    return (
      <div className="flex items-center space-x-2">
        <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getAuthStatusColor()}`}>
          <span className="mr-1">{getAuthIcon()}</span>
          {getAuthStatusText()}
        </div>
        {!isAuthenticated && (
          <button
            onClick={handleAuthClick}
            className="text-xs text-primary-600 hover:text-primary-700 underline"
          >
            Connect
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">
          OpenRouter Authentication
        </h3>
        <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getAuthStatusColor()}`}>
          <span className="mr-2">{getAuthIcon()}</span>
          {getAuthStatusText()}
        </div>
      </div>

      {isAuthenticated ? (
        <div className="space-y-4">
          {/* User Information */}
          {user && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-medium text-green-900 mb-3">Account Information</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                {user.name && (
                  <div>
                    <span className="font-medium text-green-800">Name:</span>
                    <span className="ml-2 text-green-700">{user.name}</span>
                  </div>
                )}
                {user.email && (
                  <div>
                    <span className="font-medium text-green-800">Email:</span>
                    <span className="ml-2 text-green-700">{user.email}</span>
                  </div>
                )}
                {user.credits !== undefined && (
                  <div>
                    <span className="font-medium text-green-800">Credits:</span>
                    <span className="ml-2 text-green-700">${user.credits.toFixed(2)}</span>
                  </div>
                )}
                {user.usage && (
                  <>
                    <div>
                      <span className="font-medium text-green-800">Requests:</span>
                      <span className="ml-2 text-green-700">{user.usage.requests.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="font-medium text-green-800">Tokens:</span>
                      <span className="ml-2 text-green-700">{user.usage.tokens.toLocaleString()}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Authentication Details */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3">Authentication Details</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Method:</span>
                <span className="text-gray-900 font-medium">
                  {authMethod === 'oauth' ? 'OAuth 2.0' : 'API Key'}
                </span>
              </div>
              {authMethod === 'api_key' && apiKeyValidatedAt && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Key Validated:</span>
                  <span className="text-gray-900">{formatDate(apiKeyValidatedAt)}</span>
                </div>
              )}
              {lastValidated && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Checked:</span>
                  <span className="text-gray-900">{formatDate(lastValidated)}</span>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <button
              onClick={() => dispatch(refreshUserInfo() as any)}
              disabled={isLoading}
              className="text-sm text-primary-600 hover:text-primary-700 disabled:text-gray-400 flex items-center"
            >
              {isLoading ? (
                <>
                  <div className="spinner mr-2"></div>
                  Refreshing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh Info
                </>
              )}
            </button>
            
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:text-red-700 flex items-center"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Disconnect
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Not Authenticated State */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-yellow-600 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <div>
                <h4 className="font-medium text-yellow-900 mb-2">Authentication Required</h4>
                <p className="text-yellow-800 text-sm mb-3">
                  Connect your OpenRouter account to access AI models and manage your usage.
                </p>
                <button
                  onClick={handleAuthClick}
                  className="bg-yellow-600 hover:bg-yellow-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Connect to OpenRouter
                </button>
              </div>
            </div>
          </div>

          {/* Benefits of Authentication */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-3">🚀 Benefits of Connecting</h4>
            <ul className="text-blue-800 text-sm space-y-1">
              <li>• Access to 100+ AI models</li>
              <li>• Free tier models available</li>
              <li>• Real-time usage tracking</li>
              <li>• Cost management tools</li>
              <li>• Secure credential handling</li>
            </ul>
          </div>

          {/* Authentication Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center mb-2">
                <span className="text-2xl mr-2">🔑</span>
                <h5 className="font-medium text-gray-900">API Key</h5>
              </div>
              <p className="text-gray-600 text-sm mb-3">
                Use your OpenRouter API key for direct access
              </p>
              <ul className="text-gray-500 text-xs space-y-1">
                <li>• Quick setup</li>
                <li>• Full control</li>
                <li>• Secure storage</li>
              </ul>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center mb-2">
                <span className="text-2xl mr-2">🔐</span>
                <h5 className="font-medium text-gray-900">OAuth Login</h5>
              </div>
              <p className="text-gray-600 text-sm mb-3">
                Sign in directly with your OpenRouter account
              </p>
              <ul className="text-gray-500 text-xs space-y-1">
                <li>• No API key needed</li>
                <li>• Auto token refresh</li>
                <li>• Usage statistics</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OpenRouterAuthStatus;
