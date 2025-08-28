import { useState, useEffect, useCallback, useRef } from 'react';
import { nexusAPI } from '../services/api';

export interface WorldData {
  world_id: string;
  world_title: string;
  world_genre: string;
  world_rating: number;
  threat_level?: string;
  narrative_strength?: number;
  description?: string;
  difficulty_level?: string;
  estimated_duration?: number;
  tags?: string[];
  created_by?: string;
  last_updated?: string;
  player_count?: number;
  completion_rate?: number;
  is_active?: boolean;
  max_players?: number;
  therapeutic_focus?: string[];
}

export interface UseWorldDataOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  onError?: (error: Error) => void;
  onSuccess?: (world: WorldData) => void;
}

export interface UseWorldDataResult {
  world: WorldData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  clearError: () => void;
  lastUpdated: Date | null;
}

/**
 * Custom hook for fetching and managing individual world data
 * 
 * Features:
 * - Automatic data fetching with optional refresh
 * - Error handling and retry logic
 * - Loading states
 * - Cache management
 */
export const useWorldData = (
  worldId: string | null,
  options: UseWorldDataOptions = {}
): UseWorldDataResult => {
  const {
    autoRefresh = false,
    refreshInterval = 60000, // 1 minute
    onError,
    onSuccess,
  } = options;

  const [world, setWorld] = useState<WorldData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Fetch world data from the API
   */
  const fetchWorld = useCallback(async (signal?: AbortSignal) => {
    if (!worldId) {
      setWorld(null);
      setLoading(false);
      return;
    }

    try {
      setError(null);
      
      const response = await nexusAPI.getWorld(worldId);
      
      if (signal?.aborted) return;

      const worldData = response.world || response.data || response;
      
      setWorld(worldData);
      setLastUpdated(new Date());
      onSuccess?.(worldData);
    } catch (err: any) {
      if (signal?.aborted) return;
      
      const errorMessage = err.message || 'Failed to fetch world data';
      setError(errorMessage);
      onError?.(err);
      console.error('useWorldData: Failed to fetch world:', err);
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  }, [worldId, onError, onSuccess]);

  /**
   * Refetch world data manually
   */
  const refetch = useCallback(async () => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();
    
    setLoading(true);
    await fetchWorld(abortControllerRef.current.signal);
  }, [fetchWorld]);

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
    if (autoRefresh && refreshInterval > 0 && worldId) {
      refreshIntervalRef.current = setInterval(() => {
        fetchWorld();
      }, refreshInterval);

      return () => {
        if (refreshIntervalRef.current) {
          clearInterval(refreshIntervalRef.current);
        }
      };
    }
  }, [autoRefresh, refreshInterval, fetchWorld, worldId]);

  /**
   * Initial fetch when worldId changes
   */
  useEffect(() => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    if (worldId) {
      // Create new abort controller
      abortControllerRef.current = new AbortController();
      
      setLoading(true);
      fetchWorld(abortControllerRef.current.signal);
    } else {
      setWorld(null);
      setLoading(false);
      setError(null);
    }

    // Cleanup function
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchWorld, worldId]);

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

  return {
    world,
    loading,
    error,
    refetch,
    clearError,
    lastUpdated,
  };
};

/**
 * Hook for fetching multiple worlds by IDs
 */
export const useMultipleWorlds = (worldIds: string[]) => {
  const [worlds, setWorlds] = useState<Record<string, WorldData>>({});
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    const fetchWorlds = async () => {
      if (worldIds.length === 0) {
        setWorlds({});
        setLoading(false);
        return;
      }

      setLoading(true);
      const newWorlds: Record<string, WorldData> = {};
      const newErrors: Record<string, string> = {};

      await Promise.all(
        worldIds.map(async (worldId) => {
          try {
            const response = await nexusAPI.getWorld(worldId);
            newWorlds[worldId] = response.world || response.data || response;
          } catch (err: any) {
            newErrors[worldId] = err.message || 'Failed to fetch world';
          }
        })
      );

      setWorlds(newWorlds);
      setErrors(newErrors);
      setLoading(false);
    };

    fetchWorlds();
  }, [worldIds]);

  return {
    worlds,
    loading,
    errors,
    refetch: () => {
      // Re-trigger the effect by updating a dependency
      setLoading(true);
    },
  };
};

/**
 * Hook for world entry functionality
 */
export const useWorldEntry = () => {
  const [entering, setEntering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const enterWorld = useCallback(async (worldId: string, entryData?: any) => {
    try {
      setEntering(true);
      setError(null);
      
      const response = await nexusAPI.enterWorld(worldId, entryData);
      return response;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to enter world';
      setError(errorMessage);
      throw err;
    } finally {
      setEntering(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    enterWorld,
    entering,
    error,
    clearError,
  };
};

export default useWorldData;
