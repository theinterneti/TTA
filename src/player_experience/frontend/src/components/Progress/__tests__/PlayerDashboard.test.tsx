import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PlayerDashboard from '../PlayerDashboard';

// Mock the chart components
jest.mock('../ProgressChart', () => {
  return function MockProgressChart({ data, chartType, metric }: any) {
    return (
      <div data-testid={`progress-chart-${chartType}-${metric}`}>
        Progress Chart: {chartType} - {metric}
      </div>
    );
  };
});

jest.mock('../MilestoneTracker', () => {
  return function MockMilestoneTracker({ milestones, activeMilestones, showAll, maxDisplay }: any) {
    return (
      <div data-testid="milestone-tracker">
        Milestones: {milestones.length} achieved, {activeMilestones.length} active
        {showAll ? ' (showing all)' : ` (max ${maxDisplay})`}
      </div>
    );
  };
});

jest.mock('../AchievementCelebration', () => {
  return function MockAchievementCelebration({ highlights, onDismiss }: any) {
    return (
      <div data-testid="achievement-celebration">
        {highlights.map((h: any) => (
          <div key={h.highlight_id}>
            {h.title}
            <button onClick={() => onDismiss(h.highlight_id)}>Dismiss</button>
          </div>
        ))}
      </div>
    );
  };
});

jest.mock('../InsightDisplay', () => {
  return function MockInsightDisplay({ progressSummary, recommendations }: any) {
    return (
      <div data-testid="insight-display">
        Insights for {progressSummary.player_id}: {recommendations.length} recommendations
      </div>
    );
  };
});

const mockDashboardData = {
  player_id: 'player_1',
  active_characters: [
    {
      character_id: 'char_1',
      name: 'Alice',
      appearance: {
        avatar_url: 'https://example.com/avatar1.jpg',
        description: 'A brave adventurer',
      },
      last_active: '2024-01-10T10:00:00Z',
      active_worlds: ['world_1', 'world_2'],
    },
    {
      character_id: 'char_2',
      name: 'Bob',
      appearance: {
        description: 'A wise scholar',
      },
      last_active: '2024-01-09T15:30:00Z',
      active_worlds: ['world_3'],
    },
  ],
  recent_sessions: [
    {
      session_id: 'session_1',
      character_id: 'char_1',
      world_id: 'world_1',
      world_name: 'Peaceful Forest',
      start_time: '2024-01-10T09:00:00Z',
      end_time: '2024-01-10T09:45:00Z',
      duration_minutes: 45,
      key_achievements: ['Completed breathing exercise', 'Practiced mindfulness'],
      therapeutic_interventions_count: 3,
    },
    {
      session_id: 'session_2',
      character_id: 'char_2',
      world_id: 'world_3',
      world_name: 'Ancient Library',
      start_time: '2024-01-09T14:00:00Z',
      end_time: '2024-01-09T14:30:00Z',
      duration_minutes: 30,
      key_achievements: ['Learned new coping strategy'],
      therapeutic_interventions_count: 2,
    },
  ],
  progress_highlights: [
    {
      highlight_id: 'hl_1',
      title: '7-Day Streak Achievement!',
      description: 'Maintained consistent engagement',
      highlight_type: 'milestone',
      achieved_at: '2024-01-10T10:00:00Z',
      therapeutic_value: 0.8,
      celebration_shown: false,
    },
  ],
  recommendations: [
    {
      recommendation_id: 'rec_1',
      title: 'Try advanced techniques',
      description: 'You are ready for more challenging work',
      recommendation_type: 'therapeutic_advancement',
      priority: 1,
    },
    {
      recommendation_id: 'rec_2',
      title: 'Maintain your pace',
      description: 'Keep up the excellent work',
      recommendation_type: 'encouragement',
      priority: 2,
    },
  ],
  upcoming_milestones: [
    {
      milestone_id: 'ms_1',
      title: 'Skill Builder Level 2',
      description: 'Master 5 therapeutic skills',
      progress_percentage: 60,
      is_achieved: false,
      target_date: '2024-02-01',
      required_actions: ['Learn technique A', 'Practice technique B'],
      completed_actions: ['Learn technique A'],
      therapeutic_approaches_involved: ['CBT'],
      reward_description: 'Advanced content access',
    },
  ],
  achieved_milestones: [
    {
      milestone_id: 'ms_2',
      title: '7-Day Streak',
      description: 'Completed 7 consecutive days',
      progress_percentage: 100,
      is_achieved: true,
      achieved_date: '2024-01-10',
      required_actions: ['Daily session'],
      completed_actions: ['Daily session'],
      therapeutic_approaches_involved: ['Behavioral Activation'],
      reward_description: 'Streak badge',
    },
  ],
  progress_summary: {
    player_id: 'player_1',
    therapeutic_momentum: 0.75,
    readiness_for_advancement: 0.8,
    progress_trend: 'improving',
    engagement_trend: 'increasing',
    challenge_areas: ['Stress Management'],
    strength_areas: ['Mindfulness'],
    next_recommended_goals: ['Practice daily meditation'],
    suggested_therapeutic_adjustments: ['Increase session frequency'],
    favorite_therapeutic_approach: 'CBT',
    last_updated: '2024-01-10T10:00:00Z',
  },
  visualization_data: {
    time_buckets: ['2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10'],
    series: {
      sessions: [1, 2, 1, 1, 2],
      duration_minutes: [30, 60, 25, 30, 45],
    },
    meta: {
      period_days: 5,
      units: {
        duration_minutes: 'minutes',
      },
    },
  },
};

describe('PlayerDashboard', () => {
  const mockOnCharacterSelect = jest.fn();
  const mockOnSessionStart = jest.fn();
  const mockOnHighlightDismiss = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders dashboard header and quick stats', () => {
    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    expect(screen.getByText('Your Therapeutic Journey')).toBeInTheDocument();
    expect(screen.getByText('Welcome back! Here\'s your progress overview and next steps.')).toBeInTheDocument();

    // Quick stats
    expect(screen.getByText('2')).toBeInTheDocument(); // Active characters
    expect(screen.getByText('2')).toBeInTheDocument(); // Recent sessions (same number)
    expect(screen.getByText('1')).toBeInTheDocument(); // Achievements
    expect(screen.getByText('75%')).toBeInTheDocument(); // Momentum
  });

  it('displays character overview with correct information', () => {
    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
    expect(screen.getByText('2 active worlds')).toBeInTheDocument();
    expect(screen.getByText('1 active world')).toBeInTheDocument();
  });

  it('calls onCharacterSelect when character is clicked', () => {
    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    const aliceCharacter = screen.getByText('Alice').closest('div');
    fireEvent.click(aliceCharacter!);

    expect(mockOnCharacterSelect).toHaveBeenCalledWith('char_1');
  });

  it('calls onSessionStart when continue button is clicked', () => {
    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    const continueButtons = screen.getAllByText('Continue');
    fireEvent.click(continueButtons[0]);

    expect(mockOnSessionStart).toHaveBeenCalledWith('char_1', 'world_1');
  });

  it('displays recent activity correctly', () => {
    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    expect(screen.getByText('Session in Peaceful Forest')).toBeInTheDocument();
    expect(screen.getByText('45 minutes • 3 interventions')).toBeInTheDocument();
    expect(screen.getByText('🎯 Completed breathing exercise +1 more')).toBeInTheDocument();

    expect(screen.getByText('Session in Ancient Library')).toBeInTheDocument();
    expect(screen.getByText('30 minutes • 2 interventions')).toBeInTheDocument();
  });

  it('shows quick recommendations', () => {
    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    expect(screen.getByText('Try advanced techniques')).toBeInTheDocument();
    expect(screen.getByText('You are ready for more challenging work')).toBeInTheDocument();
    expect(screen.getByText('Maintain your pace')).toBeInTheDocument();
  });

  it('switches between tabs correctly', () => {
    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    // Initially on overview tab
    expect(screen.getByText('Your Characters')).toBeInTheDocument();

    // Switch to progress tab
    fireEvent.click(screen.getByText('Progress'));
    expect(screen.getByTestId('progress-chart-line-both')).toBeInTheDocument();
    expect(screen.getByTestId('progress-chart-bar-sessions')).toBeInTheDocument();

    // Switch to insights tab
    fireEvent.click(screen.getByText('Insights'));
    expect(screen.getByTestId('insight-display')).toBeInTheDocument();
  });

  it('renders achievement celebrations', () => {
    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    expect(screen.getByTestId('achievement-celebration')).toBeInTheDocument();
    expect(screen.getByText('7-Day Streak Achievement!')).toBeInTheDocument();
  });

  it('handles highlight dismissal', () => {
    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    const dismissButton = screen.getByText('Dismiss');
    fireEvent.click(dismissButton);

    expect(mockOnHighlightDismiss).toHaveBeenCalledWith('hl_1');
  });

  it('displays empty states correctly', () => {
    const emptyData = {
      ...mockDashboardData,
      recent_sessions: [],
      recommendations: [],
    };

    render(
      <PlayerDashboard
        dashboardData={emptyData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    expect(screen.getByText('No recent sessions. Start your therapeutic journey!')).toBeInTheDocument();
    expect(screen.getByText('No specific recommendations at this time.')).toBeInTheDocument();
  });

  it('formats time ago correctly', () => {
    // Mock current time to be consistent
    const mockDate = new Date('2024-01-10T11:00:00Z');
    jest.spyOn(global, 'Date').mockImplementation(() => mockDate as any);

    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
      />
    );

    // Alice was last active 1 hour ago
    expect(screen.getByText('Last active: 1h ago')).toBeInTheDocument();

    (global.Date as any).mockRestore();
  });

  it('applies custom className', () => {
    const { container } = render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
        className="custom-dashboard"
      />
    );

    expect(container.firstChild).toHaveClass('custom-dashboard');
  });

  it('updates last refresh time', async () => {
    jest.useFakeTimers();

    render(
      <PlayerDashboard
        dashboardData={mockDashboardData}
        onCharacterSelect={mockOnCharacterSelect}
        onSessionStart={mockOnSessionStart}
        onHighlightDismiss={mockOnHighlightDismiss}
        refreshInterval={1000}
      />
    );

    const initialTime = screen.getByText(/Last updated:/).textContent;

    // Advance time by 2 seconds
    jest.advanceTimersByTime(2000);

    await waitFor(() => {
      const updatedTime = screen.getByText(/Last updated:/).textContent;
      expect(updatedTime).not.toBe(initialTime);
    });

    jest.useRealTimers();
  });
});
