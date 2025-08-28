import { useState, useEffect, useCallback, useRef } from 'react';
import { nexusAPI } from '../services/api';
import { useAuthGuard } from './useAuthGuard';

export interface NexusState {
  status: string;
  active_worlds: number;
  total_players: number;
  narrative_strength: number;
  hub_energy: number;
  last_updated: string;
  system_health: 'healthy' | 'degraded' | 'critical';
  active_sessions: number;
  pending_worlds: number;
  maintenance_mode: boolean;
}

export interface UseNexusStateOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  onError?: (error: Error) => void;
  onStateChange?: (state: NexusState) => void;
  requireAuth?: boolean;
}

export interface UseNexusStateResult {
  state: NexusState | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  clearError: () => void;
  lastUpdated: Date | null;
  isConnected: boolean;
}

/**
 * Custom hook for managing Nexus Codex central hub state
 * 
 * Features:
 * - Real-time hub status monitoring
 * - Automatic refresh with configurable intervals
 * - Authentication-aware (optional)
 * - Error handling and retry logic
 * - Connection status tracking
 */
export const useNexusState = (options: UseNexusStateOptions = {}): UseNexusStateResult => {
  const {
    autoRefresh = true,
    refreshInterval = 30000, // 30 seconds
    onError,
    onStateChange,
    requireAuth = true,
  } = options;

  const { isAuthenticated } = useAuthGuard({ autoRedirect: false });
  
  const [state, setState] = useState<NexusState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const retryCountRef = useRef(0);
  const maxRetries = 3;

  /**
   * Fetch nexus state from the API
   */
  const fetchNexusState = useCallback(async (signal?: AbortSignal) => {
    // Skip if authentication is required but user is not authenticated
    if (requireAuth && !isAuthenticated) {
      setLoading(false);
      setIsConnected(false);
      return;
    }

    try {
      setError(null);
      
      const response = await nexusAPI.getState();
      
      if (signal?.aborted) return;

      const nexusState = response.state || response.data || response;
      
      setState(nexusState);
      setLastUpdated(new Date());
      setIsConnected(true);
      retryCountRef.current = 0; // Reset retry count on success
      
      onStateChange?.(nexusState);
    } catch (err: any) {
      if (signal?.aborted) return;
      
      const errorMessage = err.message || 'Failed to fetch nexus state';
      setError(errorMessage);
      setIsConnected(false);
      
      // Retry logic for network errors
      if (retryCountRef.current < maxRetries && 
          (err.message?.includes('network') || err.message?.includes('fetch'))) {
        retryCountRef.current++;
        console.warn(`useNexusState: Retrying (${retryCountRef.current}/${maxRetries})...`);
        
        // Exponential backoff: 1s, 2s, 4s
        const retryDelay = Math.pow(2, retryCountRef.current - 1) * 1000;
        setTimeout(() => {
          if (!signal?.aborted) {
            fetchNexusState(signal);
          }
        }, retryDelay);
        return;
      }
      
      onError?.(err);
      console.error('useNexusState: Failed to fetch nexus state:', err);
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  }, [isAuthenticated, requireAuth, onError, onStateChange]);

  /**
   * Refetch nexus state manually
   */
  const refetch = useCallback(async () => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();
    
    setLoading(true);
    retryCountRef.current = 0; // Reset retry count for manual refetch
    await fetchNexusState(abortControllerRef.current.signal);
  }, [fetchNexusState]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Set up automatic refresh
   */
  useEffect(() => {
    if (autoRefresh && refreshInterval > 0 && (requireAuth ? isAuthenticated : true)) {
      refreshIntervalRef.current = setInterval(() => {
        fetchNexusState();
      }, refreshInterval);

      return () => {
        if (refreshIntervalRef.current) {
          clearInterval(refreshIntervalRef.current);
        }
      };
    }
  }, [autoRefresh, refreshInterval, fetchNexusState, requireAuth, isAuthenticated]);

  /**
   * Initial fetch when component mounts or auth state changes
   */
  useEffect(() => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();
    
    setLoading(true);
    retryCountRef.current = 0;
    fetchNexusState(abortControllerRef.current.signal);

    // Cleanup function
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchNexusState]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  /**
   * Handle authentication state changes
   */
  useEffect(() => {
    if (requireAuth && !isAuthenticated) {
      setState(null);
      setIsConnected(false);
      setLoading(false);
    }
  }, [isAuthenticated, requireAuth]);

  return {
    state,
    loading,
    error,
    refetch,
    clearError,
    lastUpdated,
    isConnected,
  };
};

/**
 * Simplified hook for basic nexus state without authentication requirement
 */
export const usePublicNexusState = () => {
  return useNexusState({
    requireAuth: false,
    autoRefresh: true,
    refreshInterval: 60000, // 1 minute for public access
  });
};

/**
 * Hook for authenticated nexus state with faster refresh
 */
export const useAuthenticatedNexusState = () => {
  return useNexusState({
    requireAuth: true,
    autoRefresh: true,
    refreshInterval: 15000, // 15 seconds for authenticated users
  });
};

export default useNexusState;
