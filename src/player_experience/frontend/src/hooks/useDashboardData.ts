// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Hooks/Usedashboarddata]]
import { useState, useEffect, useCallback } from 'react';

interface Character {
  character_id: string;
  name: string;
  appearance: {
    avatar_url?: string;
    description: string;
  };
  last_active: string;
  active_worlds: string[];
}

interface SessionSummary {
  session_id: string;
  character_id: string;
  world_id: string;
  world_name: string;
  start_time: string;
  end_time?: string;
  duration_minutes: number;
  key_achievements: string[];
  therapeutic_interventions_count: number;
}

interface ProgressHighlight {
  highlight_id: string;
  title: string;
  description: string;
  highlight_type: string;
  achieved_at: string;
  therapeutic_value: number;
  celebration_shown: boolean;
}

interface Milestone {
  milestone_id: string;
  title: string;
  description: string;
  progress_percentage: number;
  is_achieved: boolean;
  achieved_date?: string;
  target_date?: string;
  required_actions: string[];
  completed_actions: string[];
  therapeutic_approaches_involved: string[];
  reward_description: string;
}

interface Recommendation {
  recommendation_id: string;
  title: string;
  description: string;
  recommendation_type: string;
  priority: number;
}

interface ProgressVizSeries {
  time_buckets: string[];
  series: {
    sessions: number[];
    duration_minutes: number[];
  };
  meta: {
    period_days: number;
    units: {
      duration_minutes: string;
    };
  };
}

interface ProgressSummary {
  player_id: string;
  therapeutic_momentum: number;
  readiness_for_advancement: number;
  progress_trend: string;
  engagement_trend: string;
  challenge_areas: string[];
  strength_areas: string[];
  next_recommended_goals: string[];
  suggested_therapeutic_adjustments: string[];
  favorite_therapeutic_approach?: string;
  last_updated: string;
}

interface PlayerDashboardData {
  player_id: string;
  active_characters: Character[];
  recent_sessions: SessionSummary[];
  progress_highlights: ProgressHighlight[];
  recommendations: Recommendation[];
  upcoming_milestones: Milestone[];
  achieved_milestones: Milestone[];
  progress_summary: ProgressSummary;
  visualization_data: ProgressVizSeries;
}

interface UseDashboardDataOptions {
  playerId: string;
  refreshInterval?: number;
  autoRefresh?: boolean;
}

interface UseDashboardDataReturn {
  data: PlayerDashboardData | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  dismissHighlight: (highlightId: string) => void;
  updateCharacterActivity: (characterId: string) => void;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const useDashboardData = ({
  playerId,
  refreshInterval = 30000,
  autoRefresh = true,
}: UseDashboardDataOptions): UseDashboardDataReturn => {
  const [data, setData] = useState<PlayerDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setError(null);

      // Fetch dashboard data from API
      const response = await fetch(`${API_BASE_URL}/api/players/${playerId}/dashboard`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch dashboard data: ${response.statusText}`);
      }

      const dashboardData = await response.json();
      setData(dashboardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
      console.error('Dashboard data fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [playerId]);

  const refresh = useCallback(async () => {
    setLoading(true);
    await fetchDashboardData();
  }, [fetchDashboardData]);

  const dismissHighlight = useCallback((highlightId: string) => {
    setData(prevData => {
      if (!prevData) return prevData;

      return {
        ...prevData,
        progress_highlights: prevData.progress_highlights.map(highlight =>
          highlight.highlight_id === highlightId
            ? { ...highlight, celebration_shown: true }
            : highlight
        ),
      };
    });

    // Also update on server
    fetch(`${API_BASE_URL}/api/players/${playerId}/highlights/${highlightId}/dismiss`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        'Content-Type': 'application/json',
      },
    }).catch(err => {
      console.error('Failed to dismiss highlight on server:', err);
    });
  }, [playerId]);

  const updateCharacterActivity = useCallback((characterId: string) => {
    setData(prevData => {
      if (!prevData) return prevData;

      return {
        ...prevData,
        active_characters: prevData.active_characters.map(character =>
          character.character_id === characterId
            ? { ...character, last_active: new Date().toISOString() }
            : character
        ),
      };
    });
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Auto-refresh setup
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchDashboardData();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [fetchDashboardData, refreshInterval, autoRefresh]);

  // Handle visibility change to refresh when tab becomes active
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && autoRefresh) {
        fetchDashboardData();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [fetchDashboardData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh,
    dismissHighlight,
    updateCharacterActivity,
  };
};
