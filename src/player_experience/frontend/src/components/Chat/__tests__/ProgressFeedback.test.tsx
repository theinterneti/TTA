import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProgressFeedback from '../ProgressFeedback';

describe('ProgressFeedback', () => {
  const mockOnDismiss = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders milestone feedback correctly', () => {
    render(
      <ProgressFeedback
        type="milestone"
        title="First Session Complete!"
        description="You've completed your first therapeutic session."
        milestone={{
          name: "First Steps",
          icon: "🎯",
          level: 1
        }}
      />
    );

    expect(screen.getByText('First Session Complete!')).toBeInTheDocument();
    expect(screen.getByText("You've completed your first therapeutic session.")).toBeInTheDocument();
    expect(screen.getByText('First Steps')).toBeInTheDocument();
    expect(screen.getByText('Level 1')).toBeInTheDocument();
    expect(screen.getByText('🎯')).toBeInTheDocument();
  });

  it('renders achievement feedback with celebration', () => {
    render(
      <ProgressFeedback
        type="achievement"
        title="Achievement Unlocked!"
        description="You've mastered breathing exercises."
        showAnimation={true}
      />
    );

    expect(screen.getByText('Achievement Unlocked!')).toBeInTheDocument();
    expect(screen.getByText("You've mastered breathing exercises.")).toBeInTheDocument();
    expect(screen.getByText('🏆 Achievement Unlocked!')).toBeInTheDocument();
  });

  it('renders progress feedback with progress bar', () => {
    render(
      <ProgressFeedback
        type="progress"
        title="Making Great Progress"
        description="Keep up the excellent work!"
        progress={{
          current: 7,
          total: 10,
          unit: "sessions"
        }}
      />
    );

    expect(screen.getByText('Making Great Progress')).toBeInTheDocument();
    expect(screen.getByText('7 of 10 sessions completed')).toBeInTheDocument();
    expect(screen.getByText('70%')).toBeInTheDocument();

    // Check progress bar
    const progressBar = screen.container.querySelector('.bg-blue-500');
    expect(progressBar).toHaveStyle('width: 70%');
  });

  it('renders encouragement feedback with action buttons', () => {
    render(
      <ProgressFeedback
        type="encouragement"
        title="You're Doing Great!"
        description="Every step forward is progress worth celebrating."
      />
    );

    expect(screen.getByText("You're Doing Great!")).toBeInTheDocument();
    expect(screen.getByText('Every step forward is progress worth celebrating.')).toBeInTheDocument();
    expect(screen.getByText('Keep Going!')).toBeInTheDocument();
    expect(screen.getByText('Share Progress')).toBeInTheDocument();
  });

  it('applies correct styling for each type', () => {
    const { rerender } = render(
      <ProgressFeedback
        type="milestone"
        title="Milestone"
        description="Description"
      />
    );

    expect(screen.container.firstChild).toHaveClass('from-purple-50', 'to-pink-50');

    rerender(
      <ProgressFeedback
        type="achievement"
        title="Achievement"
        description="Description"
      />
    );

    expect(screen.container.firstChild).toHaveClass('from-yellow-50', 'to-orange-50');

    rerender(
      <ProgressFeedback
        type="progress"
        title="Progress"
        description="Description"
      />
    );

    expect(screen.container.firstChild).toHaveClass('from-blue-50', 'to-indigo-50');

    rerender(
      <ProgressFeedback
        type="encouragement"
        title="Encouragement"
        description="Description"
      />
    );

    expect(screen.container.firstChild).toHaveClass('from-green-50', 'to-emerald-50');
  });

  it('shows dismiss button when onDismiss is provided', () => {
    render(
      <ProgressFeedback
        type="progress"
        title="Progress Update"
        description="You're making progress!"
        onDismiss={mockOnDismiss}
      />
    );

    const dismissButton = screen.container.querySelector('button');
    expect(dismissButton).toBeInTheDocument();

    fireEvent.click(dismissButton!);
    expect(mockOnDismiss).toHaveBeenCalled();
  });

  it('does not show dismiss button when onDismiss is not provided', () => {
    render(
      <ProgressFeedback
        type="progress"
        title="Progress Update"
        description="You're making progress!"
      />
    );

    const dismissButton = screen.container.querySelector('button');
    expect(dismissButton).toBeNull();
  });

  it('shows entrance animation', async () => {
    render(
      <ProgressFeedback
        type="milestone"
        title="Milestone"
        description="Description"
        showAnimation={true}
      />
    );

    const container = screen.container.firstChild;
    
    // Initially should have translate-y-4 and opacity-0 (before animation)
    // After animation, should have translate-y-0 and opacity-100
    await waitFor(() => {
      expect(container).toHaveClass('translate-y-0', 'opacity-100');
    });
  });

  it('displays appropriate icons for each type', () => {
    const { rerender } = render(
      <ProgressFeedback
        type="milestone"
        title="Milestone"
        description="Description"
      />
    );

    expect(screen.container.querySelector('svg')).toBeInTheDocument();

    rerender(
      <ProgressFeedback
        type="achievement"
        title="Achievement"
        description="Description"
      />
    );

    expect(screen.container.querySelector('svg')).toBeInTheDocument();

    rerender(
      <ProgressFeedback
        type="progress"
        title="Progress"
        description="Description"
      />
    );

    expect(screen.container.querySelector('svg')).toBeInTheDocument();

    rerender(
      <ProgressFeedback
        type="encouragement"
        title="Encouragement"
        description="Description"
      />
    );

    expect(screen.container.querySelector('svg')).toBeInTheDocument();
  });

  it('handles milestone without level', () => {
    render(
      <ProgressFeedback
        type="milestone"
        title="Milestone"
        description="Description"
        milestone={{
          name: "Basic Milestone",
          icon: "⭐"
        }}
      />
    );

    expect(screen.getByText('Basic Milestone')).toBeInTheDocument();
    expect(screen.getByText('⭐')).toBeInTheDocument();
    expect(screen.queryByText(/Level/)).not.toBeInTheDocument();
  });

  it('handles progress without unit', () => {
    render(
      <ProgressFeedback
        type="progress"
        title="Progress"
        description="Description"
        progress={{
          current: 5,
          total: 8
        }}
      />
    );

    expect(screen.getByText('5 of 8 completed')).toBeInTheDocument();
  });

  it('calculates progress percentage correctly', () => {
    render(
      <ProgressFeedback
        type="progress"
        title="Progress"
        description="Description"
        progress={{
          current: 3,
          total: 4
        }}
      />
    );

    expect(screen.getByText('75%')).toBeInTheDocument();
    
    const progressBar = screen.container.querySelector('.bg-blue-500');
    expect(progressBar).toHaveStyle('width: 75%');
  });

  it('shows celebration particles for milestone and achievement types', () => {
    render(
      <ProgressFeedback
        type="milestone"
        title="Milestone"
        description="Description"
        showAnimation={true}
      />
    );

    // Should have celebration particles (animated dots)
    const particles = screen.container.querySelectorAll('.animate-ping');
    expect(particles.length).toBeGreaterThan(0);
  });

  it('does not show celebration particles when animation is disabled', () => {
    render(
      <ProgressFeedback
        type="milestone"
        title="Milestone"
        description="Description"
        showAnimation={false}
      />
    );

    const particles = screen.container.querySelectorAll('.animate-ping');
    expect(particles).toHaveLength(0);
  });
});