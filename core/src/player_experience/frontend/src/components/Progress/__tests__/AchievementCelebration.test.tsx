import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AchievementCelebration from '../AchievementCelebration';

const mockHighlight = {
  highlight_id: 'hl_1',
  title: '🔥 7-Day Streak Achievement!',
  description: 'Incredible consistency! You have maintained therapeutic engagement for 7 consecutive days',
  highlight_type: 'milestone',
  achieved_at: '2024-01-10T10:00:00Z',
  related_character_id: 'char_1',
  related_world_id: 'world_1',
  therapeutic_value: 0.8,
  celebration_shown: false,
};

const mockCelebrationData = {
  milestone_id: 'ms_1',
  title: '7-Day Engagement Streak',
  description: 'Maintained consistent therapeutic engagement for 7 consecutive days',
  celebration_message: '🔥 Amazing consistency! 7-Day Engagement Streak shows your dedication to growth!',
  reward_unlocked: 'Unlocked advanced therapeutic techniques and personalized content',
  therapeutic_value: 0.85,
  suggested_next_milestone: '14-Day Engagement Streak',
  celebration_type: 'progress_milestone',
  timestamp: '2024-01-10T10:00:00Z',
};

describe('AchievementCelebration', () => {
  const mockOnDismiss = jest.fn();
  const mockOnCelebrationComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('renders achievement highlights', () => {
    render(
      <AchievementCelebration
        highlights={[mockHighlight]}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('🔥 7-Day Streak Achievement!')).toBeInTheDocument();
    expect(screen.getByText(/Incredible consistency!/)).toBeInTheDocument();
    expect(screen.getByText('80% therapeutic value')).toBeInTheDocument();
    expect(screen.getByText('milestone')).toBeInTheDocument();
  });

  it('does not render highlights that have been celebrated', () => {
    const celebratedHighlight = { ...mockHighlight, celebration_shown: true };

    render(
      <AchievementCelebration
        highlights={[celebratedHighlight]}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.queryByText('🔥 7-Day Streak Achievement!')).not.toBeInTheDocument();
  });

  it('calls onDismiss when highlight is dismissed', () => {
    render(
      <AchievementCelebration
        highlights={[mockHighlight]}
        onDismiss={mockOnDismiss}
      />
    );

    const dismissButton = screen.getByLabelText('Dismiss achievement');
    fireEvent.click(dismissButton);

    expect(mockOnDismiss).toHaveBeenCalledWith('hl_1');
  });

  it('displays celebration modal when celebrationData is provided', () => {
    render(
      <AchievementCelebration
        highlights={[]}
        celebrationData={mockCelebrationData}
        onDismiss={mockOnDismiss}
        onCelebrationComplete={mockOnCelebrationComplete}
      />
    );

    expect(screen.getByText('Congratulations!')).toBeInTheDocument();
    expect(screen.getByText('7-Day Engagement Streak')).toBeInTheDocument();
    expect(screen.getByText(/Amazing consistency!/)).toBeInTheDocument();
    expect(screen.getByText('Reward Unlocked!')).toBeInTheDocument();
    expect(screen.getByText(/Unlocked advanced therapeutic techniques/)).toBeInTheDocument();
    expect(screen.getByText('Therapeutic Value: 85%')).toBeInTheDocument();
  });

  it('shows suggested next milestone in celebration', () => {
    render(
      <AchievementCelebration
        highlights={[]}
        celebrationData={mockCelebrationData}
        onDismiss={mockOnDismiss}
        onCelebrationComplete={mockOnCelebrationComplete}
      />
    );

    expect(screen.getByText('Next Challenge:')).toBeInTheDocument();
    expect(screen.getByText('14-Day Engagement Streak')).toBeInTheDocument();
  });

  it('calls onCelebrationComplete when celebration is dismissed', () => {
    render(
      <AchievementCelebration
        highlights={[]}
        celebrationData={mockCelebrationData}
        onDismiss={mockOnDismiss}
        onCelebrationComplete={mockOnCelebrationComplete}
      />
    );

    const continueButton = screen.getByText('Continue Journey');
    fireEvent.click(continueButton);

    expect(mockOnCelebrationComplete).toHaveBeenCalledWith('ms_1');
  });

  it('auto-dismisses celebration after 5 seconds', async () => {
    render(
      <AchievementCelebration
        highlights={[]}
        celebrationData={mockCelebrationData}
        onDismiss={mockOnDismiss}
        onCelebrationComplete={mockOnCelebrationComplete}
      />
    );

    expect(screen.getByText('Congratulations!')).toBeInTheDocument();

    // Fast-forward time by 5 seconds
    jest.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(mockOnCelebrationComplete).toHaveBeenCalledWith('ms_1');
    });
  });

  it('displays correct celebration icon based on type', () => {
    const majorAchievementData = {
      ...mockCelebrationData,
      celebration_type: 'major_achievement',
    };

    render(
      <AchievementCelebration
        highlights={[]}
        celebrationData={majorAchievementData}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('🏆')).toBeInTheDocument();
  });

  it('displays correct highlight icon based on type', () => {
    const breakthroughHighlight = {
      ...mockHighlight,
      highlight_type: 'breakthrough',
    };

    render(
      <AchievementCelebration
        highlights={[breakthroughHighlight]}
        onDismiss={mockOnDismiss}
      />
    );

    // Check that the breakthrough icon is rendered (SparklesIcon)
    const iconElement = screen.getByText('🔥 7-Day Streak Achievement!').closest('div')?.querySelector('svg');
    expect(iconElement).toBeInTheDocument();
  });

  it('formats dates correctly', () => {
    render(
      <AchievementCelebration
        highlights={[mockHighlight]}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('1/10/2024')).toBeInTheDocument();
  });

  it('applies correct therapeutic value styling', () => {
    const highValueHighlight = { ...mockHighlight, therapeutic_value: 0.9 };
    const mediumValueHighlight = { ...mockHighlight, highlight_id: 'hl_2', therapeutic_value: 0.6 };
    const lowValueHighlight = { ...mockHighlight, highlight_id: 'hl_3', therapeutic_value: 0.3 };

    render(
      <AchievementCelebration
        highlights={[highValueHighlight, mediumValueHighlight, lowValueHighlight]}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('90% therapeutic value')).toHaveClass('text-green-600', 'bg-green-100');
    expect(screen.getByText('60% therapeutic value')).toHaveClass('text-blue-600', 'bg-blue-100');
    expect(screen.getByText('30% therapeutic value')).toHaveClass('text-gray-600', 'bg-gray-100');
  });

  it('handles multiple highlights correctly', () => {
    const secondHighlight = {
      ...mockHighlight,
      highlight_id: 'hl_2',
      title: 'Skill Mastery Achievement!',
      highlight_type: 'skill_development',
    };

    render(
      <AchievementCelebration
        highlights={[mockHighlight, secondHighlight]}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('🔥 7-Day Streak Achievement!')).toBeInTheDocument();
    expect(screen.getByText('Skill Mastery Achievement!')).toBeInTheDocument();
  });

  it('does not show celebration modal when celebrationData is not provided', () => {
    render(
      <AchievementCelebration
        highlights={[mockHighlight]}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.queryByText('Congratulations!')).not.toBeInTheDocument();
  });
});
