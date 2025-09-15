import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type Environment = 'development' | 'staging' | 'production';

interface EnvironmentConfig {
  apiUrl: string;
  gatewayUrl: string;
  agentUrl: string;
  wsUrl: string;
  debugMode: boolean;
  features: {
    liveReload: boolean;
    hotReload: boolean;
    devTools: boolean;
    mockData: boolean;
    errorReporting: boolean;
  };
}

interface EnvironmentContextType {
  environment: Environment;
  config: EnvironmentConfig;
  setEnvironment: (env: Environment) => void;
  isProduction: boolean;
  isDevelopment: boolean;
  isStaging: boolean;
}

const EnvironmentContext = createContext<EnvironmentContextType | undefined>(undefined);

export const useEnvironment = () => {
  const context = useContext(EnvironmentContext);
  if (context === undefined) {
    throw new Error('useEnvironment must be used within an EnvironmentProvider');
  }
  return context;
};

interface EnvironmentProviderProps {
  children: ReactNode;
}

const getEnvironmentConfig = (env: Environment): EnvironmentConfig => {
  const configs: Record<Environment, EnvironmentConfig> = {
    development: {
      apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8080',
      gatewayUrl: process.env.REACT_APP_GATEWAY_URL || 'http://localhost:8000',
      agentUrl: process.env.REACT_APP_AGENT_URL || 'http://localhost:8503',
      wsUrl: process.env.REACT_APP_WS_URL || 'ws://localhost:8080',
      debugMode: true,
      features: {
        liveReload: true,
        hotReload: true,
        devTools: true,
        mockData: true,
        errorReporting: true,
      },
    },
    staging: {
      apiUrl: process.env.REACT_APP_STAGING_API_URL || 'https://staging-api.tta.example.com',
      gatewayUrl: process.env.REACT_APP_STAGING_GATEWAY_URL || 'https://staging-gateway.tta.example.com',
      agentUrl: process.env.REACT_APP_STAGING_AGENT_URL || 'https://staging-agent.tta.example.com',
      wsUrl: process.env.REACT_APP_STAGING_WS_URL || 'wss://staging-api.tta.example.com',
      debugMode: false,
      features: {
        liveReload: false,
        hotReload: false,
        devTools: true,
        mockData: false,
        errorReporting: true,
      },
    },
    production: {
      apiUrl: process.env.REACT_APP_PROD_API_URL || 'https://api.tta.example.com',
      gatewayUrl: process.env.REACT_APP_PROD_GATEWAY_URL || 'https://gateway.tta.example.com',
      agentUrl: process.env.REACT_APP_PROD_AGENT_URL || 'https://agent.tta.example.com',
      wsUrl: process.env.REACT_APP_PROD_WS_URL || 'wss://api.tta.example.com',
      debugMode: false,
      features: {
        liveReload: false,
        hotReload: false,
        devTools: false,
        mockData: false,
        errorReporting: true,
      },
    },
  };

  return configs[env];
};

export const EnvironmentProvider: React.FC<EnvironmentProviderProps> = ({ children }) => {
  const [environment, setEnvironmentState] = useState<Environment>(() => {
    // Determine initial environment
    const nodeEnv = process.env.NODE_ENV;
    const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';

    if (nodeEnv === 'production' && !hostname.includes('localhost')) {
      return 'production';
    } else if (hostname.includes('staging')) {
      return 'staging';
    } else {
      return 'development';
    }
  });

  const [config, setConfig] = useState<EnvironmentConfig>(() => getEnvironmentConfig(environment));

  const setEnvironment = (env: Environment) => {
    setEnvironmentState(env);
    setConfig(getEnvironmentConfig(env));

    // Store preference in localStorage
    localStorage.setItem('tta-dev-environment', env);
  };

  useEffect(() => {
    // Load saved environment preference
    const savedEnv = localStorage.getItem('tta-dev-environment') as Environment;
    if (savedEnv && savedEnv !== environment) {
      setEnvironment(savedEnv);
    }
  }, [environment]);

  useEffect(() => {
    // Set up environment-specific configurations
    if (config.debugMode) {
      console.log('TTA Developer Interface - Debug Mode Enabled');
      console.log('Environment:', environment);
      console.log('Config:', config);
    }

    // Set up error reporting
    if (config.features.errorReporting) {
      const handleError = (event: ErrorEvent) => {
        console.error('Global error in', environment, 'environment:', event.error);
        // In a real implementation, you might send this to an error reporting service
      };

      const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
        console.error('Unhandled promise rejection in', environment, 'environment:', event.reason);
        // In a real implementation, you might send this to an error reporting service
      };

      window.addEventListener('error', handleError);
      window.addEventListener('unhandledrejection', handleUnhandledRejection);

      return () => {
        window.removeEventListener('error', handleError);
        window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      };
    }
  }, [environment, config]);

  const value: EnvironmentContextType = {
    environment,
    config,
    setEnvironment,
    isProduction: environment === 'production',
    isDevelopment: environment === 'development',
    isStaging: environment === 'staging',
  };

  return (
    <EnvironmentContext.Provider value={value}>
      {children}
    </EnvironmentContext.Provider>
  );
};
