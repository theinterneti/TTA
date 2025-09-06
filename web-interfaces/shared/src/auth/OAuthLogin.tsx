import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

export interface OAuthProvider {
  id: string;
  name: string;
  enabled: boolean;
}

export interface OAuthLoginProps {
  interfaceType: 'patient' | 'clinical' | 'admin';
  onSuccess?: (user: any) => void;
  onError?: (error: string) => void;
  className?: string;
}

export const OAuthLogin: React.FC<OAuthLoginProps> = ({
  interfaceType,
  onSuccess,
  onError,
  className = '',
}) => {
  const [providers, setProviders] = useState<OAuthProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [authLoading, setAuthLoading] = useState<string | null>(null);

  useEffect(() => {
    loadOAuthProviders();
  }, []);

  const loadOAuthProviders = async () => {
    try {
      const response = await apiClient.get('/auth/oauth/providers');
      setProviders(response.data);
    } catch (error) {
      console.error('Failed to load OAuth providers:', error);
      onError?.('Failed to load authentication providers');
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthLogin = async (providerId: string) => {
    setAuthLoading(providerId);
    
    try {
      // Get authorization URL
      const response = await apiClient.get(
        `/auth/oauth/${providerId}/authorize`,
        {
          params: {
            interface_type: interfaceType,
            redirect_uri: `${window.location.origin}/auth/callback/${providerId}`,
          },
        }
      );

      const { authorization_url, state } = response.data;

      // Store state for callback verification
      sessionStorage.setItem(`oauth_state_${providerId}`, state);
      sessionStorage.setItem('oauth_interface_type', interfaceType);

      // Redirect to OAuth provider
      window.location.href = authorization_url;
    } catch (error) {
      console.error(`OAuth login failed for ${providerId}:`, error);
      onError?.(`Failed to authenticate with ${providerId}`);
      setAuthLoading(null);
    }
  };

  const getProviderIcon = (providerId: string) => {
    const icons = {
      google: (
        <svg className="w-5 h-5" viewBox="0 0 24 24">
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
          />
        </svg>
      ),
      microsoft: (
        <svg className="w-5 h-5" viewBox="0 0 24 24">
          <path fill="#F25022" d="M1 1h10v10H1z" />
          <path fill="#00A4EF" d="M13 1h10v10H13z" />
          <path fill="#7FBA00" d="M1 13h10v10H1z" />
          <path fill="#FFB900" d="M13 13h10v10H13z" />
        </svg>
      ),
      apple: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
        </svg>
      ),
      facebook: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="#1877F2">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
        </svg>
      ),
    };
    return icons[providerId as keyof typeof icons] || null;
  };

  const getProviderButtonClass = (providerId: string) => {
    const baseClass = "w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium transition-colors duration-200";
    
    const providerClasses = {
      google: "bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500",
      microsoft: "bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500",
      apple: "bg-black text-white hover:bg-gray-800 focus:ring-gray-500",
      facebook: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    };

    return `${baseClass} ${providerClasses[providerId as keyof typeof providerClasses] || 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`;
  };

  if (loading) {
    return (
      <div className={`space-y-3 ${className}`}>
        <div className="animate-pulse">
          <div className="h-10 bg-gray-200 rounded-md"></div>
        </div>
        <div className="animate-pulse">
          <div className="h-10 bg-gray-200 rounded-md"></div>
        </div>
      </div>
    );
  }

  if (providers.length === 0) {
    return (
      <div className={`text-center text-gray-500 ${className}`}>
        <p>No OAuth providers available</p>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="text-center">
        <p className="text-sm text-gray-600 mb-4">
          {interfaceType === 'clinical' 
            ? 'Quick sign-in for healthcare providers'
            : 'Sign in with your preferred account'
          }
        </p>
      </div>
      
      {providers.map((provider) => (
        <button
          key={provider.id}
          onClick={() => handleOAuthLogin(provider.id)}
          disabled={!provider.enabled || authLoading === provider.id}
          className={getProviderButtonClass(provider.id)}
        >
          {authLoading === provider.id ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
              Connecting...
            </div>
          ) : (
            <div className="flex items-center">
              {getProviderIcon(provider.id)}
              <span className="ml-2">Continue with {provider.name}</span>
            </div>
          )}
        </button>
      ))}
      
      {interfaceType === 'patient' && (
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            By continuing, you agree to our Terms of Service and Privacy Policy.
            Your therapeutic data is protected and secure.
          </p>
        </div>
      )}
      
      {interfaceType === 'clinical' && (
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Clinical access requires additional verification.
            All activities are logged for HIPAA compliance.
          </p>
        </div>
      )}
    </div>
  );
};

export default OAuthLogin;
