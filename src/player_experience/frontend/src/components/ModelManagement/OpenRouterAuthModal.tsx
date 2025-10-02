import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import {
  validateApiKey,
  initiateOAuth,
  hideAuthModal,
  clearError,
} from '../../store/slices/openRouterAuthSlice';

interface OpenRouterAuthModalProps {
  onAuthSuccess?: () => void;
}

const OpenRouterAuthModal: React.FC<OpenRouterAuthModalProps> = ({
  onAuthSuccess,
}) => {
  const dispatch = useDispatch();
  const {
    showAuthModal,
    isLoading,
    error,
    oauthState,
    isAuthenticated,
    authMethod,
    user,
  } = useSelector((state: RootState) => state.openRouterAuth);

  const [activeTab, setActiveTab] = useState<'api_key' | 'oauth'>('api_key');
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [isValidating, setIsValidating] = useState(false);

  // Clear form when modal opens/closes
  useEffect(() => {
    if (!showAuthModal) {
      setApiKey('');
      setShowApiKey(false);
      setIsValidating(false);
    }
  }, [showAuthModal]);

  // Handle successful authentication
  useEffect(() => {
    if (isAuthenticated && showAuthModal) {
      onAuthSuccess?.();
      dispatch(hideAuthModal());
    }
  }, [isAuthenticated, showAuthModal, onAuthSuccess, dispatch]);

  const handleApiKeySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) return;

    setIsValidating(true);
    try {
      await dispatch(validateApiKey({ apiKey: apiKey.trim() }) as any);
    } finally {
      setIsValidating(false);
    }
  };

  const handleOAuthLogin = async () => {
    try {
      const result = await dispatch(initiateOAuth() as any);
      if (result.payload?.authUrl) {
        // Open OAuth URL in a popup window
        const popup = window.open(
          result.payload.authUrl,
          'openrouter-oauth',
          'width=500,height=600,scrollbars=yes,resizable=yes'
        );

        // Listen for the popup to close (OAuth completion)
        const checkClosed = setInterval(() => {
          if (popup?.closed) {
            clearInterval(checkClosed);
            // The OAuth callback will be handled by the backend
            // and the user state will be updated via WebSocket or polling
          }
        }, 1000);
      }
    } catch (error) {
      console.error('OAuth initiation failed:', error);
    }
  };

  const validateApiKeyFormat = (key: string): boolean => {
    // OpenRouter API keys follow the pattern: sk-or-v1-[64 hex characters]
    return /^sk-or-v1-[a-f0-9]{64}$/.test(key);
  };

  const isApiKeyValid = validateApiKeyFormat(apiKey);

  if (!showAuthModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Connect to OpenRouter
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Authenticate to access AI models
            </p>
          </div>
          <button
            onClick={() => dispatch(hideAuthModal())}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mx-6 mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-red-800 text-sm">{error}</span>
              <button
                onClick={() => dispatch(clearError())}
                className="ml-auto text-red-600 hover:text-red-800"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200 mx-6 mt-4">
          <button
            onClick={() => setActiveTab('api_key')}
            className={`flex-1 py-2 px-4 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'api_key'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            🔑 API Key
          </button>
          <button
            onClick={() => setActiveTab('oauth')}
            className={`flex-1 py-2 px-4 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'oauth'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            🔐 OAuth Login
          </button>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'api_key' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Enter Your OpenRouter API Key
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Your API key will be securely stored and encrypted. It will never be shared or stored in your browser.
                </p>
              </div>

              <form onSubmit={handleApiKeySubmit} className="space-y-4">
                <div>
                  <label htmlFor="api-key" className="block text-sm font-medium text-gray-700 mb-2">
                    API Key
                  </label>
                  <div className="relative">
                    <input
                      id="api-key"
                      type={showApiKey ? 'text' : 'password'}
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="sk-or-v1-..."
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 pr-10 ${
                        apiKey && !isApiKeyValid ? 'border-red-300' : 'border-gray-300'
                      }`}
                      disabled={isValidating || isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
                    >
                      {showApiKey ? (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                  {apiKey && !isApiKeyValid && (
                    <p className="text-red-600 text-xs mt-1">
                      Invalid API key format. Should start with "sk-or-v1-"
                    </p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={!isApiKeyValid || isValidating || isLoading}
                  className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  {isValidating || isLoading ? (
                    <div className="flex items-center justify-center">
                      <div className="spinner mr-2"></div>
                      Validating...
                    </div>
                  ) : (
                    'Connect with API Key'
                  )}
                </button>
              </form>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">🔒 Security Notice</h4>
                <ul className="text-blue-800 text-sm space-y-1">
                  <li>• Your API key is encrypted before storage</li>
                  <li>• Keys are never stored in your browser</li>
                  <li>• All requests are made server-side</li>
                  <li>• You can revoke access anytime</li>
                </ul>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">📝 How to get an API key</h4>
                <ol className="text-gray-700 text-sm space-y-1">
                  <li>1. Visit <a href="https://openrouter.ai" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">openrouter.ai</a></li>
                  <li>2. Sign up for a free account</li>
                  <li>3. Go to Keys section in your dashboard</li>
                  <li>4. Create a new API key</li>
                  <li>5. Copy and paste it here</li>
                </ol>
              </div>
            </div>
          )}

          {activeTab === 'oauth' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Sign in with OpenRouter
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Connect your OpenRouter account directly for seamless access to your models and usage data.
                </p>
              </div>

              <button
                onClick={handleOAuthLogin}
                disabled={oauthState.isLoading || isLoading}
                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center"
              >
                {oauthState.isLoading || isLoading ? (
                  <div className="flex items-center">
                    <div className="spinner mr-2"></div>
                    Connecting...
                  </div>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Sign in with OpenRouter
                  </>
                )}
              </button>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-2">✨ OAuth Benefits</h4>
                <ul className="text-green-800 text-sm space-y-1">
                  <li>• No need to manage API keys</li>
                  <li>• Automatic token refresh</li>
                  <li>• Access to usage statistics</li>
                  <li>• Secure authentication flow</li>
                  <li>• Easy account management</li>
                </ul>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">🔐 How OAuth works</h4>
                <ol className="text-gray-700 text-sm space-y-1">
                  <li>1. Click "Sign in with OpenRouter"</li>
                  <li>2. You'll be redirected to OpenRouter</li>
                  <li>3. Log in to your OpenRouter account</li>
                  <li>4. Authorize TTA to access your account</li>
                  <li>5. You'll be redirected back automatically</li>
                </ol>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-lg">
          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-500">
              Secure authentication powered by TTA
            </p>
            <button
              onClick={() => dispatch(hideAuthModal())}
              className="text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpenRouterAuthModal;
