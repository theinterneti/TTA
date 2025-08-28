/**
 * useNexusState Hook
 * 
 * Custom hook for managing Nexus Codex state, including real-time updates
 * and connection to the Nexus API endpoints.
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';

interface NexusState {
  codex_id: string;
  total_worlds: number;
  active_story_weavers: number;
  silence_threat_level: number;
  narrative_strength: number;
  featured_worlds: Array<{
    world_id: string;
    title: string;
    genre: string;
    rating: number;
    player_count: number;
  }>;
  recent_activity: Array<{
    event_id: string;
    event_type: string;
    user_name: string;
    world_title?: string;
    description: string;
    timestamp: string;
  }>;
  timestamp: string;
}

interface UseNexusStateReturn {
  nexusState: NexusState | null;
  loading: boolean;
  error: string | null;
  refreshNexusState: () => Promise<void>;
  isConnected: boolean;
}

export const useNexusState = (): UseNexusStateReturn => {
  const [nexusState, setNexusState] = useState<NexusState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const { token } = useAuth();

  const fetchNexusState = useCallback(async () => {
    try {
      setError(null);
      
      const response = await fetch('/api/v1/nexus/state', {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch Nexus state: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setNexusState(data);
      setIsConnected(true);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      setIsConnected(false);
      console.error('Failed to fetch Nexus state:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  const refreshNexusState = useCallback(async () => {
    setLoading(true);
    await fetchNexusState();
  }, [fetchNexusState]);

  // Initial fetch
  useEffect(() => {
    fetchNexusState();
  }, [fetchNexusState]);

  // Set up real-time updates via WebSocket or polling
  useEffect(() => {
    if (!isConnected) return;

    // For now, use polling every 30 seconds
    // In production, this should be replaced with WebSocket connections
    const interval = setInterval(() => {
      fetchNexusState();
    }, 30000);

    return () => clearInterval(interval);
  }, [isConnected, fetchNexusState]);

  // WebSocket connection for real-time updates (future enhancement)
  useEffect(() => {
    if (!token || !isConnected) return;

    // TODO: Implement WebSocket connection for real-time updates
    // const ws = new WebSocket(`ws://localhost:8080/ws/nexus?token=${token}`);
    // 
    // ws.onmessage = (event) => {
    //   const data = JSON.parse(event.data);
    //   if (data.type === 'nexus_update') {
    //     setNexusState(prev => prev ? { ...prev, ...data.payload } : null);
    //   }
    // };
    // 
    // ws.onerror = (error) => {
    //   console.error('WebSocket error:', error);
    //   setIsConnected(false);
    // };
    // 
    // return () => {
    //   ws.close();
    // };
  }, [token, isConnected]);

  return {
    nexusState,
    loading,
    error,
    refreshNexusState,
    isConnected,
  };
};

/**
 * useStorySpheres Hook
 * 
 * Custom hook for managing story sphere data and visualization state.
 */

interface StorySphere {
  sphere_id: string;
  world_id: string;
  world_title: string;
  visual_state: 'bright_glow' | 'gentle_pulse' | 'dim_flicker' | 'dark_void';
  pulse_frequency: number;
  position: { x: number; y: number; z: number };
  color_primary: string;
  color_secondary: string;
  size_scale: number;
  connection_strength: number;
  world_genre: string;
  world_rating: number;
  world_player_count: number;
}

interface UseStorySpheresReturn {
  spheres: StorySphere[];
  loading: boolean;
  error: string | null;
  refreshSpheres: () => Promise<void>;
  filterSpheres: (filters: {
    genre?: string;
    threat_level?: string;
  }) => Promise<void>;
}

export const useStorySpheres = (): UseStorySpheresReturn => {
  const [spheres, setSpheres] = useState<StorySphere[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  const fetchSpheres = useCallback(async (filters?: { genre?: string; threat_level?: string }) => {
    try {
      setError(null);
      
      const params = new URLSearchParams();
      if (filters?.genre) params.append('genre', filters.genre);
      if (filters?.threat_level) params.append('threat_level', filters.threat_level);
      
      const url = `/api/v1/nexus/spheres${params.toString() ? `?${params.toString()}` : ''}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch story spheres: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setSpheres(data.spheres || []);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to fetch story spheres:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  const refreshSpheres = useCallback(async () => {
    setLoading(true);
    await fetchSpheres();
  }, [fetchSpheres]);

  const filterSpheres = useCallback(async (filters: { genre?: string; threat_level?: string }) => {
    setLoading(true);
    await fetchSpheres(filters);
  }, [fetchSpheres]);

  // Initial fetch
  useEffect(() => {
    fetchSpheres();
  }, [fetchSpheres]);

  return {
    spheres,
    loading,
    error,
    refreshSpheres,
    filterSpheres,
  };
};

/**
 * useWorldCreation Hook
 * 
 * Custom hook for managing world creation workflow and state.
 */

interface WorldCreationRequest {
  title: string;
  description: string;
  genre: string;
  therapeutic_focus: string[];
  difficulty_level?: string;
  estimated_duration?: number;
  is_public?: boolean;
  template_id?: string;
  world_parameters?: Record<string, any>;
  narrative_structure?: Record<string, any>;
}

interface UseWorldCreationReturn {
  createWorld: (worldData: WorldCreationRequest) => Promise<{ success: boolean; world_id?: string; error?: string }>;
  loading: boolean;
  error: string | null;
}

export const useWorldCreation = (): UseWorldCreationReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  const createWorld = useCallback(async (worldData: WorldCreationRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/nexus/worlds', {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(worldData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to create world: ${response.status}`);
      }

      const result = await response.json();
      return { success: true, world_id: result.world_id };

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [token]);

  return {
    createWorld,
    loading,
    error,
  };
};

/**
 * useWorldSearch Hook
 * 
 * Custom hook for searching and filtering worlds.
 */

interface WorldSearchFilters {
  query?: string;
  genre?: string;
  therapeutic_focus?: string[];
  difficulty?: string;
  rating_min?: number;
  sort_by?: string;
  limit?: number;
  offset?: number;
}

interface WorldSummary {
  world_id: string;
  title: string;
  description: string;
  genre: string;
  therapeutic_focus: string[];
  difficulty_level: string;
  estimated_duration: number;
  player_count: number;
  rating: number;
  therapeutic_efficacy: number;
  strength_level: number;
  tags: string[];
  is_featured: boolean;
  created_at: string;
}

interface UseWorldSearchReturn {
  searchWorlds: (filters: WorldSearchFilters) => Promise<void>;
  results: WorldSummary[];
  totalCount: number;
  loading: boolean;
  error: string | null;
  hasMore: boolean;
}

export const useWorldSearch = (): UseWorldSearchReturn => {
  const [results, setResults] = useState<WorldSummary[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const { token } = useAuth();

  const searchWorlds = useCallback(async (filters: WorldSearchFilters) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, value.toString());
          }
        }
      });

      const response = await fetch(`/api/v1/nexus/worlds/search?${params.toString()}`, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.results || []);
      setTotalCount(data.total_count || 0);
      setHasMore(data.has_more || false);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('World search failed:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  return {
    searchWorlds,
    results,
    totalCount,
    loading,
    error,
    hasMore,
  };
};
