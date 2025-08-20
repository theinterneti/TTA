import { renderHook, act, waitFor } from '@testing-library/react';
import { useDashboardData } from '../useDashboardData';

// Mock fetch
global.fetch = jest.fn();

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

const mockDashboardData = {
  player_id: 'player_1',
  active_characters: [
    {
      character_id: 'char_1',
      name: 'Alice',
      appearance: { description: 'A brave adventurer' },
      last_active: '2024-01-10T10:00:00Z',
      active_worlds: ['world_1'],
    },
  ],
  recent_sessions: [],
  progress_highlights: [
    {
      highlight_id: 'hl_1',
      title: 'Achievement',
      description: 'Great work!',
      highlight_type: 'milestone',
      achieved_at: '2024-01-10T10:00:00Z',
      therapeutic_value: 0.8,
      celebration_shown: false,
    },
  ],
  recommendations: [],
  upcoming_milestones: [],
  achieved_milestones: [],
  progress_summary: {
    player_id: 'player_1',
    therapeutic_momentum: 0.75,
    readiness_for_advancement: 0.8,
    progress_trend: 'improving',
    engagement_trend: 'increasing',
    challenge_areas: [],
    strength_areas: [],
    next_recommended_goals: [],
    suggested_therapeutic_adjustments: [],
    last_updated: '2024-01-10T10:00:00Z',
  },
  visualization_data: {
    time_buckets: ['2024-01-10'],
    series: { sessions: [1], duration_minutes: [30] },
    meta: { period_days: 1, units: { duration_minutes: 'minutes' } },
  },
};

describe('useDashboardData', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue('mock-token');
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockDashboardData),
    });
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('fetches dashboard data on mount', async () => {
    const { result } = renderHook(() =>
      useDashboardData({ playerId: 'player_1', autoRefresh: false })
    );

    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockDashboardData);
    expect(result.current.error).toBe(null);
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/players/player_1/dashboard',
      {
        headers: {
          'Authorization': 'Bearer mock-token',
          'Content-Type': 'application/json',
        },
      }
    );
  });

  it('handles fetch errors', async () => {
    (fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() =>
      useDashboardData({ playerId: 'player_1', autoRefresh: false })
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe('Network error');
  });

  it('handles HTTP errors', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: false,
      statusText: 'Not Found',
    });

    const { result } = renderHook(() =>
      useDashboardData({ playerId: 'player_1', autoRefresh: false })
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe('Failed to fetch dashboard data: Not Found');
  });

  it('refreshes data when refresh is called', async () => {
    const { result } = renderHook(() =>
      useDashboardData({ playerId: 'player_1', autoRefresh: false })
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetch).toHaveBeenCalledTimes(1);

    await act(async () => {
      await result.current.refresh();
    });

    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it('dismisses highlights locally and on server', async () => {
    const { result } = renderHook(() =>
      useDashboardData({ playerId: 'player_1', autoRefresh: false })
    );

    await waitFor(() => {
      expect(result.current.data).not.toBe(null);
    });

    // Mock the dismiss API call
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({}),
    });

    act(() => {
      result.current.dismissHighlight('hl_1');
    });

    // Check that highlight is marked as shown locally
    expect(result.current.data?.progress_highlights[0].celebration_shown).toBe(true);

    // Check that API was called
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/players/player_1/highlights/hl_1/dismiss',
        {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json',
          },
        }
      );
    });
  });

  it('updates character activity', async () => {
    const { result } = renderHook(() =>
      useDashboardData({ playerId: 'player_1', autoRefresh: false })
    );

    await waitFor(() => {
      expect(result.current.data).not.toBe(null);
    });

    const originalLastActive = result.current.data?.active_characters[0].last_active;

    act(() => {
      result.current.updateCharacterActivity('char_1');
    });

    const updatedLastActive = result.current.data?.active_characters[0].last_active;
    expect(updatedLastActive).not.toBe(originalLastActive);
    expect(new Date(updatedLastActive!).getTime()).toBeGreaterThan(
      new Date(originalLastActive!).getTime()
    );
  });

  it('sets up auto-refresh when enabled', async () => {
    jest.useFakeTimers();

    const { result } = renderHook(() =>
      useDashboardData({ 
        playerId: 'player_1', 
        autoRefresh: true, 
        refreshInterval: 1000 
      })
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetch).toHaveBeenCalledTimes(1);

    // Advance time by 1 second
    act(() => {
      jest.advanceTimersByTime(1000);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
    });

    // Advance time by another second
    act(() => {
      jest.advanceTimersByTime(1000);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(3);
    });
  });

  it('does not auto-refresh when disabled', async () => {
    jest.useFakeTimers();

    const { result } = renderHook(() =>
      useDashboardData({ 
        playerId: 'player_1', 
        autoRefresh: false, 
        refreshInterval: 1000 
      })
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetch).toHaveBeenCalledTimes(1);

    // Advance time by 2 seconds
    act(() => {
      jest.advanceTimersByTime(2000);
    });

    // Should still be only 1 call (initial fetch)
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('handles visibility change events', async () => {
    const { result } = renderHook(() =>
      useDashboardData({ playerId: 'player_1', autoRefresh: true })
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetch).toHaveBeenCalledTimes(1);

    // Simulate tab becoming hidden then visible again
    Object.defineProperty(document, 'hidden', {
      writable: true,
      value: true,
    });

    act(() => {
      document.dispatchEvent(new Event('visibilitychange'));
    });

    // Should not fetch when hidden
    expect(fetch).toHaveBeenCalledTimes(1);

    Object.defineProperty(document, 'hidden', {
      writable: true,
      value: false,
    });

    act(() => {
      document.dispatchEvent(new Event('visibilitychange'));
    });

    // Should fetch when visible again
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
    });
  });

  it('cleans up intervals and event listeners on unmount', () => {
    jest.useFakeTimers();
    const clearIntervalSpy = jest.spyOn(global, 'clearInterval');
    const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener');

    const { unmount } = renderHook(() =>
      useDashboardData({ 
        playerId: 'player_1', 
        autoRefresh: true, 
        refreshInterval: 1000 
      })
    );

    unmount();

    expect(clearIntervalSpy).toHaveBeenCalled();
    expect(removeEventListenerSpy).toHaveBeenCalledWith('visibilitychange', expect.any(Function));

    clearIntervalSpy.mockRestore();
    removeEventListenerSpy.mockRestore();
  });
});