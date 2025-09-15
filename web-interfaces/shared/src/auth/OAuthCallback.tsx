import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import { apiClient } from '../api/client';

export interface OAuthCallbackProps {
  onSuccess?: (user: any) => void;
  onError?: (error: string) => void;
}

export const OAuthCallback: React.FC<OAuthCallbackProps> = ({
  onSuccess,
  onError,
}) => {
  const { provider } = useParams<{ provider: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setUser, setToken } = useAuth();

  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState('Processing authentication...');

  useEffect(() => {
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = async () => {
    try {
      // Get callback parameters
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');

      // Check for OAuth errors
      if (error) {
        throw new Error(errorDescription || `OAuth error: ${error}`);
      }

      if (!code || !state || !provider) {
        throw new Error('Missing required OAuth parameters');
      }

      // Verify state parameter
      const storedState = sessionStorage.getItem(`oauth_state_${provider}`);
      if (!storedState || storedState !== state) {
        throw new Error('Invalid OAuth state parameter - possible CSRF attack');
      }

      // Get interface type
      const interfaceType = sessionStorage.getItem('oauth_interface_type') || 'patient';

      setMessage('Exchanging authorization code...');

      // Exchange code for tokens
      const response = await apiClient.post(`/auth/oauth/${provider}/callback`, {
        code,
        state,
        interface_type: interfaceType,
      });

      const { access_token, user_info } = response.data;

      // Clean up session storage
      sessionStorage.removeItem(`oauth_state_${provider}`);
      sessionStorage.removeItem('oauth_interface_type');

      // Update auth context
      setToken(access_token);
      setUser(user_info);

      // Store token
      localStorage.setItem(`tta_token_${interfaceType}`, access_token);

      setStatus('success');
      setMessage('Authentication successful! Redirecting...');

      // Call success callback
      onSuccess?.(user_info);

      // Redirect to appropriate dashboard
      setTimeout(() => {
        const redirectPath = interfaceType === 'clinical' ? '/clinical/dashboard' : '/dashboard';
        navigate(redirectPath, { replace: true });
      }, 2000);

    } catch (error) {
      console.error('OAuth callback error:', error);

      const errorMessage = error instanceof Error ? error.message : 'Authentication failed';
      setStatus('error');
      setMessage(errorMessage);

      // Call error callback
      onError?.(errorMessage);

      // Clean up session storage
      if (provider) {
        sessionStorage.removeItem(`oauth_state_${provider}`);
      }
      sessionStorage.removeItem('oauth_interface_type');

      // Redirect to login after delay
      setTimeout(() => {
        navigate('/login', { replace: true });
      }, 3000);
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return (
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        );
      case 'success':
        return (
          <div className="rounded-full h-12 w-12 bg-green-100 flex items-center justify-center">
            <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'error':
        return (
          <div className="rounded-full h-12 w-12 bg-red-100 flex items-center justify-center">
            <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'text-blue-600';
      case 'success':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
    }
  };

  const getProviderName = () => {
    const providerNames = {
      google: 'Google',
      microsoft: 'Microsoft',
      apple: 'Apple',
      facebook: 'Facebook',
    };
    return providerNames[provider as keyof typeof providerNames] || provider;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            {getStatusIcon()}
          </div>

          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            {status === 'processing' && 'Authenticating...'}
            {status === 'success' && 'Welcome!'}
            {status === 'error' && 'Authentication Failed'}
          </h2>

          {provider && (
            <p className="text-sm text-gray-600 mb-4">
              Signing in with {getProviderName()}
            </p>
          )}

          <p className={`text-sm ${getStatusColor()}`}>
            {message}
          </p>

          {status === 'processing' && (
            <div className="mt-6">
              <div className="bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
              </div>
            </div>
          )}

          {status === 'success' && (
            <div className="mt-6 p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-green-800">
                🎉 Authentication successful! You'll be redirected to your dashboard shortly.
              </p>
            </div>
          )}

          {status === 'error' && (
            <div className="mt-6 space-y-4">
              <div className="p-4 bg-red-50 rounded-lg">
                <p className="text-sm text-red-800">
                  ❌ We couldn't complete your authentication. You'll be redirected to the login page.
                </p>
              </div>

              <button
                onClick={() => navigate('/login', { replace: true })}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Return to Login
              </button>
            </div>
          )}

          <div className="mt-8 text-center">
            <p className="text-xs text-gray-500">
              Secure authentication powered by TTA OAuth 2.0
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OAuthCallback;
