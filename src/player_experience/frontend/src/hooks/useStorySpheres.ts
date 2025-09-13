import { useCallback, useEffect, useRef, useState } from "react";
import { nexusAPI } from "../services/api";

export interface StorySphereData {
  sphere_id: string;
  world_id: string;
  world_title: string;
  visual_state: string;
  pulse_frequency: number;
  position: { x: number; y: number; z: number };
  color_primary: string;
  color_secondary: string;
  size_scale: number;
  world_genre: string;
  world_rating: number;
  threat_level?: string;
  narrative_strength?: number;
  last_updated?: string;
}

export interface StorySphereFilters {
  genre?: string;
  threat_level?: string;
  min_rating?: number;
  max_rating?: number;
}

export interface UseStorySphereOptions {
  filters?: StorySphereFilters;
  autoRefresh?: boolean;
  refreshInterval?: number;
  onError?: (error: Error) => void;
  onSuccess?: (spheres: StorySphereData[]) => void;
}

export interface UseStorySphereResult {
  spheres: StorySphereData[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  updateFilters: (filters: StorySphereFilters) => void;
  clearError: () => void;
  lastUpdated: Date | null;
}

/**
 * Custom hook for managing story spheres data from the Nexus Codex API
 *
 * Features:
 * - Automatic data fetching with filters
 * - Real-time updates with configurable refresh interval
 * - Error handling and retry logic
 * - Loading states
 * - Filter management
 */
export const useStorySpheres = (
  options: UseStorySphereOptions = {}
): UseStorySphereResult => {
  const {
    filters = {},
    autoRefresh = true,
    refreshInterval = 30000, // 30 seconds
    onError,
    onSuccess,
  } = options;

  const [spheres, setSpheres] = useState<StorySphereData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentFilters, setCurrentFilters] =
    useState<StorySphereFilters>(filters);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Fetch spheres from the API
   */
  const fetchSpheres = useCallback(
    async (signal?: AbortSignal) => {
      try {
        setError(null);

        const response = await nexusAPI.getSpheres(currentFilters);

        if (signal?.aborted) return;

        const spheresData =
          (response as any).spheres || (response as any).data || response;

        if (Array.isArray(spheresData)) {
          setSpheres(spheresData);
          setLastUpdated(new Date());
          onSuccess?.(spheresData);
        } else {
          throw new Error("Invalid response format: expected array of spheres");
        }
      } catch (err: any) {
        if (signal?.aborted) return;

        const errorMessage = err.message || "Failed to fetch story spheres";
        setError(errorMessage);
        onError?.(err);
        console.error("useStorySpheres: Failed to fetch spheres:", err);
      } finally {
        if (!signal?.aborted) {
          setLoading(false);
        }
      }
    },
    [currentFilters, onError, onSuccess]
  );

  /**
   * Refetch spheres manually
   */
  const refetch = useCallback(async () => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    setLoading(true);
    await fetchSpheres(abortControllerRef.current.signal);
  }, [fetchSpheres]);

  /**
   * Update filters and refetch data
   */
  const updateFilters = useCallback((newFilters: StorySphereFilters) => {
    setCurrentFilters((prev) => ({ ...prev, ...newFilters }));
  }, []);

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
    if (autoRefresh && refreshInterval > 0) {
      refreshIntervalRef.current = setInterval(() => {
        fetchSpheres();
      }, refreshInterval);

      return () => {
        if (refreshIntervalRef.current) {
          clearInterval(refreshIntervalRef.current);
        }
      };
    }
  }, [autoRefresh, refreshInterval, fetchSpheres]);

  /**
   * Initial fetch and filter change handling
   */
  useEffect(() => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    setLoading(true);
    fetchSpheres(abortControllerRef.current.signal);

    // Cleanup function
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchSpheres]);

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
    spheres,
    loading,
    error,
    refetch,
    updateFilters,
    clearError,
    lastUpdated,
  };
};

/**
 * Simplified hook for basic sphere fetching without filters
 */
export const useBasicStorySpheres = () => {
  return useStorySpheres({
    autoRefresh: true,
    refreshInterval: 60000, // 1 minute
  });
};

/**
 * Hook for filtered sphere fetching with specific genre
 */
export const useGenreFilteredSpheres = (genre: string) => {
  return useStorySpheres({
    filters: { genre },
    autoRefresh: true,
    refreshInterval: 30000,
  });
};

/**
 * Hook for threat level filtered spheres
 */
export const useThreatLevelSpheres = (threatLevel: string) => {
  return useStorySpheres({
    filters: { threat_level: threatLevel },
    autoRefresh: true,
    refreshInterval: 45000,
  });
};

export default useStorySpheres;
