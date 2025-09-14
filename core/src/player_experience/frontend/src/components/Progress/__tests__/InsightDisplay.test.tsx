import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import InsightDisplay from '../InsightDisplay';

const mockProgressSummary = {
  player_id: 'player_1',
  therapeutic_momentum: 0.75,
  readiness_for_advancement: 0.8,
  progress_trend: 'improving',
  engagement_trend: 'increasing',
  challenge_areas: ['Emotional Regulation', 'Stress Management'],
  strength_areas: ['Mindfulness Practice', 'Goal Setting'],
  next_recommended_goals: ['Practice daily meditation', 'Complete CBT exercises', 'Set weekly therapeutic goals'],
  suggested_therapeutic_adjustments: ['Increase session frequency', 'Focus on anxiety management'],
  favorite_therapeutic_approach: 'CBT',
  last_updated: '2024-01-10T10:00:00Z',
};

const mockRecommendations = [
  {
    recommendation_id: 'rec_1',
    title: 'Ready for advanced therapeutic techniques',
    description: 'Your consistent progress shows you\'re ready for more challenging therapeutic work.',
    recommendation_type: 'therapeutic_advancement',
    priority: 1,
  },
  {
    recommendation_id: 'rec_2',
    title: 'Maintain your excellent pace',
    description: 'Your engagement and momentum look strong. Keep going with your current routine.',
    recommendation_type: 'therapeutic_approach',
    priority: 2,
  },
  {
    recommendation_id: 'rec_3',
    title: 'Focus on skill mastery',
    description: 'You\'re excelling at learning new skills. Consider practicing advanced applications.',
    recommendation_type: 'skill_building',
    priority: 3,
  },
];

describe('InsightDisplay', () => {
  it('renders progress insights section', () => {
    render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={mockRecommendations}
      />
    );

    expect(screen.getByText('Progress Insights')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument(); // Therapeutic momentum
    expect(screen.getByText('80%')).toBeInTheDocument(); // Readiness for advancement
    expect(screen.getByText('Improving')).toBeInTheDocument(); // Progress trend
  });

  it('displays strength and challenge areas', () => {
    render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={mockRecommendations}
      />
    );

    expect(screen.getByText('💪 Strength Areas')).toBeInTheDocument();
    expect(screen.getByText('Mindfulness Practice')).toBeInTheDocument();
    expect(screen.getByText('Goal Setting')).toBeInTheDocument();

    expect(screen.getByText('🎯 Growth Areas')).toBeInTheDocument();
    expect(screen.getByText('Emotional Regulation')).toBeInTheDocument();
    expect(screen.getByText('Stress Management')).toBeInTheDocument();
  });

  it('shows favorite therapeutic approach', () => {
    render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={mockRecommendations}
      />
    );

    expect(screen.getByText('🌟 Your Preferred Approach')).toBeInTheDocument();
    expect(screen.getByText('CBT')).toBeInTheDocument();
  });

  it('renders recommendations with correct priority styling', () => {
    render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={mockRecommendations}
      />
    );

    expect(screen.getByText('Ready for advanced therapeutic techniques')).toBeInTheDocument();
    expect(screen.getByText('High Priority')).toBeInTheDocument();
    expect(screen.getByText('Medium Priority')).toBeInTheDocument();
    expect(screen.getByText('Low Priority')).toBeInTheDocument();
  });

  it('displays next recommended goals', () => {
    render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={mockRecommendations}
      />
    );

    expect(screen.getByText('Suggested Next Steps')).toBeInTheDocument();
    expect(screen.getByText('Practice daily meditation')).toBeInTheDocument();
    expect(screen.getByText('Complete CBT exercises')).toBeInTheDocument();
    expect(screen.getByText('Set weekly therapeutic goals')).toBeInTheDocument();
  });

  it('toggles sections when expandable', () => {
    render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={mockRecommendations}
        expandable={true}
      />
    );

    // Initially insights should be expanded
    expect(screen.getByText('75%')).toBeInTheDocument();

    // Click to collapse insights
    const insightsHeader = screen.getByText('Progress Insights');
    fireEvent.click(insightsHeader);

    // Insights should be collapsed (content not visible)
    expect(screen.queryByText('75%')).not.toBeInTheDocument();

    // Click to expand again
    fireEvent.click(insightsHeader);
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('does not toggle sections when not expandable', () => {
    render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={mockRecommendations}
        expandable={false}
      />
    );

    const insightsHeader = screen.getByText('Progress Insights');
    fireEvent.click(insightsHeader);

    // Content should still be visible
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('displays correct trend icons and colors', () => {
    render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={mockRecommendations}
      />
    );

    const progressTrendElement = screen.getByText('Improving').closest('div');
    expect(progressTrendElement).toHaveClass('text-green-700', 'bg-green-100');
  });

  it('handles declining trends correctly', () => {
    const decliningProgressSummary = {
      ...mockProgressSummary,
      progress_trend: 'declining',
      engagement_trend: 'decreasing',
    };

    render(
      <InsightDisplay
        progressSummary={decliningProgressSummary}
        recommendations={mockRecommendations}
      />
    );

    const progressTrendElement = screen.getByText('Declining').closest('div');
    expect(progressTrendElement).toHaveClass('text-red-700', 'bg-red-100');
  });

  it('displays momentum with appropriate colors', () => {
    const highMomentumSummary = { ...mockProgressSummary, therapeutic_momentum: 0.9 };
    const { rerender } = render(
      <InsightDisplay
        progressSummary={highMomentumSummary}
        recommendations={mockRecommendations}
      />
    );

    let momentumElement = screen.getByText('90%').closest('div');
    expect(momentumElement).toHaveClass('text-green-700', 'bg-green-100');

    const lowMomentumSummary = { ...mockProgressSummary, therapeutic_momentum: 0.3 };
    rerender(
      <InsightDisplay
        progressSummary={lowMomentumSummary}
        recommendations={mockRecommendations}
      />
    );

    momentumElement = screen.getByText('30%').closest('div');
    expect(momentumElement).toHaveClass('text-red-700', 'bg-red-100');
  });

  it('shows empty state when no recommendations', () => {
    render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={[]}
      />
    );

    expect(screen.getByText('No specific recommendations at this time. Keep up the great work!')).toBeInTheDocument();
  });

  it('does not show next goals section when no goals', () => {
    const summaryWithoutGoals = {
      ...mockProgressSummary,
      next_recommended_goals: [],
    };

    render(
      <InsightDisplay
        progressSummary={summaryWithoutGoals}
        recommendations={mockRecommendations}
      />
    );

    expect(screen.queryByText('Suggested Next Steps')).not.toBeInTheDocument();
  });

  it('formats last updated date correctly', () => {
    render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={mockRecommendations}
      />
    );

    expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <InsightDisplay
        progressSummary={mockProgressSummary}
        recommendations={mockRecommendations}
        className="custom-class"
      />
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('handles missing favorite therapeutic approach', () => {
    const summaryWithoutApproach = {
      ...mockProgressSummary,
      favorite_therapeutic_approach: undefined,
    };

    render(
      <InsightDisplay
        progressSummary={summaryWithoutApproach}
        recommendations={mockRecommendations}
      />
    );

    expect(screen.queryByText('🌟 Your Preferred Approach')).not.toBeInTheDocument();
  });
});
