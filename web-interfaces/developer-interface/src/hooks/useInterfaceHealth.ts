import { useState, useEffect, useCallback } from 'react';
import { useQuery } from 'react-query';
import { apiClient } from '@tta/shared-components';
import { webSocketManager, InterfaceHealthData } from '../services/WebSocketManager';

interface HealthStatus {
  patient?: 'healthy' | 'unhealthy' | 'unknown';
  clinical?: 'healthy' | 'unhealthy' | 'unknown';
  admin?: 'healthy' | 'unhealthy' | 'unknown';
  public?: 'healthy' | 'unhealthy' | 'unknown';
  stakeholder?: 'healthy' | 'unhealthy' | 'unknown';
  apiDocs?: 'healthy' | 'unhealthy' | 'unknown';
  developer?: 'healthy' | 'unhealthy' | 'unknown';
}

interface InterfaceHealthData {
  id: string;
  name: string;
  port: number;
  status: 'healthy' | 'unhealthy' | 'unknown';
  responseTime: number;
  lastCheck: Date;
  error?: string;
}

const checkInterfaceHealth = async (port: number): Promise<{ status: 'healthy' | 'unhealthy'; responseTime: number; error?: string }> => {
  const startTime = Date.now();

  try {
    const response = await fetch(`http://localhost:${port}/health`, {
      method: 'GET',
      timeout: 5000,
    });

    const responseTime = Date.now() - startTime;

    if (response.ok) {
      return { status: 'healthy', responseTime };
    } else {
      return {
        status: 'unhealthy',
        responseTime,
        error: `HTTP ${response.status}: ${response.statusText}`
      };
    }
  } catch (error) {
    const responseTime = Date.now() - startTime;
    return {
      status: 'unhealthy',
      responseTime,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
};

const checkAllInterfaces = async (): Promise<InterfaceHealthData[]> => {
  const interfaces = [
    { id: 'patient', name: 'Patient Interface', port: 3000 },
    { id: 'clinical', name: 'Clinical Dashboard', port: 3001 },
    { id: 'admin', name: 'Admin Interface', port: 3002 },
    { id: 'public', name: 'Public Portal', port: 3003 },
    { id: 'stakeholder', name: 'Stakeholder Dashboard', port: 3004 },
    { id: 'apiDocs', name: 'API Documentation', port: 3005 },
    { id: 'developer', name: 'Developer Interface', port: 3006 },
  ];

  const results = await Promise.allSettled(
    interfaces.map(async (interface_) => {
      const health = await checkInterfaceHealth(interface_.port);
      return {
        ...interface_,
        ...health,
        lastCheck: new Date(),
      };
    })
  );

  return results.map((result, index) => {
    if (result.status === 'fulfilled') {
      return result.value;
    } else {
      return {
        ...interfaces[index],
        status: 'unknown' as const,
        responseTime: 0,
        lastCheck: new Date(),
        error: 'Health check failed',
      };
    }
  });
};

export const useInterfaceHealth = () => {
  const [healthStatus, setHealthStatus] = useState<HealthStatus>({});
  const [realTimeData, setRealTimeData] = useState<InterfaceHealthData[]>([]);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);

  // WebSocket real-time updates
  useEffect(() => {
    const handleHealthUpdate = (healthData: InterfaceHealthData) => {
      setRealTimeData(prev => {
        const updated = [...prev];
        const index = updated.findIndex(item => item.id === healthData.id);
        if (index >= 0) {
          updated[index] = healthData;
        } else {
          updated.push(healthData);
        }
        return updated;
      });

      // Update status mapping
      setHealthStatus(prev => ({
        ...prev,
        [healthData.id]: healthData.status
      }));
    };

    const handleConnectionStatus = ({ status }: { status: string }) => {
      setIsWebSocketConnected(status === 'connected');
    };

    webSocketManager.on('health_update', handleHealthUpdate);
    webSocketManager.on('connection_status', handleConnectionStatus);

    // Request initial health check
    webSocketManager.requestHealthCheck();

    return () => {
      webSocketManager.off('health_update', handleHealthUpdate);
      webSocketManager.off('connection_status', handleConnectionStatus);
    };
  }, []);

  // Fallback to polling when WebSocket is not available
  const { data, isLoading, error, refetch } = useQuery(
    'interface-health',
    checkAllInterfaces,
    {
      refetchInterval: isWebSocketConnected ? false : 30000, // Only poll if WebSocket is not connected
      refetchOnWindowFocus: !isWebSocketConnected,
      retry: 2,
      enabled: !isWebSocketConnected, // Disable polling when WebSocket is active
      onSuccess: (data) => {
        if (!isWebSocketConnected) {
          const status: HealthStatus = {};
          data.forEach((interface_) => {
            status[interface_.id as keyof HealthStatus] = interface_.status;
          });
          setHealthStatus(status);
        }
      },
    }
  );

  const manualRefresh = useCallback(async () => {
    try {
      if (isWebSocketConnected) {
        webSocketManager.requestHealthCheck();
      } else {
        await refetch();
      }
    } catch (error) {
      console.error('Failed to refresh interface health:', error);
    }
  }, [refetch, isWebSocketConnected]);

  return {
    healthStatus,
    healthData: isWebSocketConnected ? realTimeData : (data || []),
    isLoading: isWebSocketConnected ? false : isLoading,
    error,
    refetch: manualRefresh,
    isWebSocketConnected,
    connectionStatus: webSocketManager.getConnectionStatus(),
  };
};

export const useSpecificInterfaceHealth = (interfaceId: string, port: number) => {
  const [status, setStatus] = useState<'healthy' | 'unhealthy' | 'unknown'>('unknown');
  const [responseTime, setResponseTime] = useState<number>(0);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      const result = await checkInterfaceHealth(port);
      setStatus(result.status);
      setResponseTime(result.responseTime);
      setError(result.error || null);
      setLastCheck(new Date());
    } catch (err) {
      setStatus('unknown');
      setError(err instanceof Error ? err.message : 'Unknown error');
      setLastCheck(new Date());
    }
  }, [port]);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [checkHealth]);

  return {
    status,
    responseTime,
    lastCheck,
    error,
    refresh: checkHealth,
  };
};
