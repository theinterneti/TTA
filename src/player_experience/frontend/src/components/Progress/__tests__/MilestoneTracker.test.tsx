import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import MilestoneTracker from '../MilestoneTracker';

const mockAchievedMilestone = {
  milestone_id: 'ms_1',
  title: '7-Day Streak',
  description: 'Completed 7 consecutive days of therapeutic sessions',
  target_date: '2024-01-15',
  achieved_date: '2024-01-10',
  progress_percentage: 100,
  required_actions: ['Complete daily session', 'Engage with therapeutic content', 'Reflect on progress'],
  completed_actions: ['Complete daily session', 'Engage with therapeutic content', 'Reflect on progress'],
  therapeutic_approaches_involved: ['CBT', 'Mindfulness'],
  reward_description: 'Unlocked advanced therapeutic techniques',
  is_achieved: true,
};

const mockActiveMilestone = {
  milestone_id: 'ms_2',
  title: 'Skill Builder Level 2',
  description: 'Master 5 therapeutic skills',
  target_date: '2024-02-01',
  achieved_date: undefined,
  progress_percentage: 60,
  required_actions: ['Learn breathing technique', 'Practice mindfulness', 'Complete CBT exercise', 'Journal daily', 'Set therapeutic goals'],
  completed_actions: ['Learn breathing technique', 'Practice mindfulness', 'Complete CBT exercise'],
  therapeutic_approaches_involved: ['CBT', 'Mindfulness', 'Journaling'],
  reward_description: 'Access to personalized therapeutic content',
  is_achieved: false,
};

describe('MilestoneTracker', () => {
  it('renders milestones correctly', () => {
    render(
      <MilestoneTracker
        milestones={[mockAchievedMilestone]}
        activeMilestones={[mockActiveMilestone]}
      />
    );

    expect(screen.getByText('7-Day Streak')).toBeInTheDocument();
    expect(screen.getByText('Skill Builder Level 2')).toBeInTheDocument();
    expect(screen.getByText('1 achieved')).toBeInTheDocument();
  });

  it('displays progress percentages correctly', () => {
    render(
      <MilestoneTracker
        milestones={[mockAchievedMilestone]}
        activeMilestones={[mockActiveMilestone]}
      />
    );

    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.getByText('60%')).toBeInTheDocument();
  });

  it('shows achieved date for completed milestones', () => {
    render(
      <MilestoneTracker
        milestones={[mockAchievedMilestone]}
        activeMilestones={[]}
      />
    );

    expect(screen.getByText('Jan 10, 2024')).toBeInTheDocument();
  });

  it('shows target date for active milestones', () => {
    render(
      <MilestoneTracker
        milestones={[]}
        activeMilestones={[mockActiveMilestone]}
      />
    );

    expect(screen.getByText('Due: Feb 1, 2024')).toBeInTheDocument();
  });

  it('displays reward descriptions', () => {
    render(
      <MilestoneTracker
        milestones={[mockAchievedMilestone]}
        activeMilestones={[mockActiveMilestone]}
      />
    );

    expect(screen.getByText('🎁 Unlocked advanced therapeutic techniques')).toBeInTheDocument();
    expect(screen.getByText('🎁 Access to personalized therapeutic content')).toBeInTheDocument();
  });

  it('shows progress bars with correct widths', () => {
    const { container } = render(
      <MilestoneTracker
        milestones={[mockAchievedMilestone]}
        activeMilestones={[mockActiveMilestone]}
      />
    );

    const progressBars = container.querySelectorAll('[style*="width"]');
    expect(progressBars[0]).toHaveStyle('width: 100%');
    expect(progressBars[1]).toHaveStyle('width: 60%');
  });

  it('displays action completion status', () => {
    render(
      <MilestoneTracker
        milestones={[]}
        activeMilestones={[mockActiveMilestone]}
      />
    );

    expect(screen.getByText('3 / 5 actions')).toBeInTheDocument();
    expect(screen.getByText('Learn breathing technique')).toBeInTheDocument();
    expect(screen.getByText('Practice mindfulness')).toBeInTheDocument();
    expect(screen.getByText('Complete CBT exercise')).toBeInTheDocument();
  });

  it('shows therapeutic approaches as tags', () => {
    render(
      <MilestoneTracker
        milestones={[mockAchievedMilestone]}
        activeMilestones={[]}
      />
    );

    expect(screen.getByText('CBT')).toBeInTheDocument();
    expect(screen.getByText('Mindfulness')).toBeInTheDocument();
  });

  it('limits display to maxDisplay when showAll is false', () => {
    const manyMilestones = Array.from({ length: 10 }, (_, i) => ({
      ...mockAchievedMilestone,
      milestone_id: `ms_${i}`,
      title: `Milestone ${i}`,
    }));

    render(
      <MilestoneTracker
        milestones={manyMilestones}
        activeMilestones={[]}
        maxDisplay={3}
        showAll={false}
      />
    );

    expect(screen.getByText('View all 10 milestones')).toBeInTheDocument();
    expect(screen.getAllByText(/Milestone \d+/)).toHaveLength(3);
  });

  it('shows all milestones when showAll is true', () => {
    const manyMilestones = Array.from({ length: 10 }, (_, i) => ({
      ...mockAchievedMilestone,
      milestone_id: `ms_${i}`,
      title: `Milestone ${i}`,
    }));

    render(
      <MilestoneTracker
        milestones={manyMilestones}
        activeMilestones={[]}
        showAll={true}
      />
    );

    expect(screen.queryByText('View all 10 milestones')).not.toBeInTheDocument();
    expect(screen.getAllByText(/Milestone \d+/)).toHaveLength(10);
  });

  it('applies correct styling for achieved milestones', () => {
    const { container } = render(
      <MilestoneTracker
        milestones={[mockAchievedMilestone]}
        activeMilestones={[]}
      />
    );

    const achievedMilestone = container.querySelector('.border-green-200');
    expect(achievedMilestone).toBeInTheDocument();
    expect(achievedMilestone).toHaveClass('bg-green-50');
  });

  it('applies correct styling for active milestones', () => {
    const { container } = render(
      <MilestoneTracker
        milestones={[]}
        activeMilestones={[mockActiveMilestone]}
      />
    );

    const activeMilestone = container.querySelector('.border-blue-200');
    expect(activeMilestone).toBeInTheDocument();
    expect(activeMilestone).toHaveClass('bg-blue-50');
  });

  it('sorts milestones by achievement status and progress', () => {
    const lowProgressMilestone = {
      ...mockActiveMilestone,
      milestone_id: 'ms_3',
      title: 'Low Progress Milestone',
      progress_percentage: 20,
    };

    render(
      <MilestoneTracker
        milestones={[mockAchievedMilestone]}
        activeMilestones={[mockActiveMilestone, lowProgressMilestone]}
      />
    );

    const milestoneElements = screen.getAllByText(/Day Streak|Skill Builder|Low Progress/);
    expect(milestoneElements[0]).toHaveTextContent('7-Day Streak'); // Achieved first
    expect(milestoneElements[1]).toHaveTextContent('Skill Builder Level 2'); // Higher progress
    expect(milestoneElements[2]).toHaveTextContent('Low Progress Milestone'); // Lower progress
  });
});
