import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TherapeuticJourneyMap from '../TherapeuticJourneyMap';
import { GoalProgress } from '../../../../services/goalProgressService';
import { TherapeuticApproachAnalysis } from '../../../../services/therapeuticApproachAlignmentService';

describe('TherapeuticJourneyMap', () => {
  const mockGoalProgresses: GoalProgress[] = [
    {
      goalId: 'mindfulness_practice',
      progress: 80,
      startDate: new Date('2024-01-01'),
      lastUpdated: new Date('2024-01-15'),
      milestones: [],
      progressHistory: [],
      status: 'in_progress',
      estimatedCompletion: new Date('2024-02-01'),
      difficultyLevel: 'intermediate',
      therapeuticApproaches: ['Mindfulness']
    },
    {
      goalId: 'anxiety_reduction',
      progress: 60,
      startDate: new Date('2024-01-01'),
      lastUpdated: new Date('2024-01-15'),
      milestones: [],
      progressHistory: [],
      status: 'in_progress',
      estimatedCompletion: new Date('2024-03-01'),
      difficultyLevel: 'intermediate',
      therapeuticApproaches: ['CBT']
    }
  ];

  const mockApproachAnalysis: TherapeuticApproachAnalysis = {
    selectedGoals: ['mindfulness_practice', 'anxiety_reduction'],
    recommendedApproaches: [],
    approachAlignments: [],
    approachCompatibilities: [],
    overallCoherence: 0.8,
    treatmentEffectivenessScore: 0.85,
    integrationRecommendations: []
  };

  describe('Rendering', () => {
    it('renders journey map with selected goals', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice', 'anxiety_reduction']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      expect(screen.getByText('Therapeutic Journey Map')).toBeInTheDocument();
      expect(screen.getByText('Your personalized path to therapeutic goals')).toBeInTheDocument();
    });

    it('shows empty state when no goals selected', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={[]}
          goalProgresses={[]}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      expect(screen.getByText('Your Therapeutic Journey')).toBeInTheDocument();
      expect(screen.getByText('Select therapeutic goals to see your personalized journey map')).toBeInTheDocument();
      expect(screen.getByText('🗺️')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      const { container } = render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
          className="custom-class"
        />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Journey Stages', () => {
    it('generates foundation building stage for appropriate goals', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice', 'emotional_regulation']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      // Foundation stage should be generated for mindfulness and emotional regulation goals
      expect(screen.getByText('Foundation Building')).toBeInTheDocument();
      expect(screen.getByText('Establishing core therapeutic skills and self-awareness')).toBeInTheDocument();
      expect(screen.getByText('🌱')).toBeInTheDocument();
    });

    it('generates skill development stage for appropriate goals', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['anxiety_reduction', 'stress_management']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      expect(screen.getByText('Skill Development')).toBeInTheDocument();
      expect(screen.getByText('Building specific therapeutic skills and coping strategies')).toBeInTheDocument();
      expect(screen.getByText('🛠️')).toBeInTheDocument();
    });

    it('generates integration stage for appropriate goals', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['work_life_balance', 'perfectionism_reduction']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      expect(screen.getByText('Integration & Application')).toBeInTheDocument();
      expect(screen.getByText('Applying skills to real-world situations and relationships')).toBeInTheDocument();
      expect(screen.getByText('🌟')).toBeInTheDocument();
    });

    it('generates healing stage for trauma-related goals', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['trauma_recovery', 'grief_processing']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      expect(screen.getByText('Healing & Recovery')).toBeInTheDocument();
      expect(screen.getByText('Deep healing work and trauma processing')).toBeInTheDocument();
      expect(screen.getByText('🕊️')).toBeInTheDocument();
    });
  });

  describe('Stage Status', () => {
    it('shows completed status for high progress goals', () => {
      const highProgressGoals: GoalProgress[] = [
        {
          ...mockGoalProgresses[0],
          progress: 85
        }
      ];

      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={highProgressGoals}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      expect(screen.getByText('COMPLETED')).toBeInTheDocument();
    });

    it('shows current status for medium progress goals', () => {
      const mediumProgressGoals: GoalProgress[] = [
        {
          ...mockGoalProgresses[0],
          progress: 50
        }
      ];

      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={mediumProgressGoals}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      expect(screen.getByText('CURRENT')).toBeInTheDocument();
    });

    it('shows upcoming status for low progress goals', () => {
      const lowProgressGoals: GoalProgress[] = [
        {
          ...mockGoalProgresses[0],
          progress: 10
        }
      ];

      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={lowProgressGoals}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      expect(screen.getByText('UPCOMING')).toBeInTheDocument();
    });
  });

  describe('Stage Interactions', () => {
    it('expands stage details when clicked', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      const stageIcon = screen.getByText('🌱');
      fireEvent.click(stageIcon);

      expect(screen.getByText('Goals')).toBeInTheDocument();
      expect(screen.getByText('Therapeutic Approaches')).toBeInTheDocument();
      expect(screen.getByText('Key Milestones')).toBeInTheDocument();
    });

    it('calls onStageClick when stage is clicked', () => {
      const mockOnStageClick = jest.fn();
      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
          onStageClick={mockOnStageClick}
        />
      );

      const stageIcon = screen.getByText('🌱');
      fireEvent.click(stageIcon);

      expect(mockOnStageClick).toHaveBeenCalledWith('foundation');
    });

    it('collapses stage when clicked again', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      const stageIcon = screen.getByText('🌱');

      // First click to expand
      fireEvent.click(stageIcon);
      expect(screen.getByText('Goals')).toBeInTheDocument();

      // Second click to collapse
      fireEvent.click(stageIcon);
      expect(screen.queryByText('Goals')).not.toBeInTheDocument();
    });
  });

  describe('Progress Visualization', () => {
    it('displays progress bars for each stage', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      // Progress should be displayed for stages
      expect(screen.getByText('Progress')).toBeInTheDocument();
      expect(screen.getByText('80%')).toBeInTheDocument();
    });

    it('shows correct progress colors based on completion', () => {
      const { container } = render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      // High progress should show green
      const progressBar = container.querySelector('.bg-green-500');
      expect(progressBar).toBeInTheDocument();
    });
  });

  describe('Journey Insights', () => {
    it('displays journey insights section', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice', 'anxiety_reduction']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      expect(screen.getByText('Journey Insights')).toBeInTheDocument();
      expect(screen.getByText('Current Focus')).toBeInTheDocument();
      expect(screen.getByText('Overall Progress')).toBeInTheDocument();
      expect(screen.getByText('Estimated Timeline')).toBeInTheDocument();
    });

    it('calculates overall progress correctly', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice', 'anxiety_reduction']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      // Should show average progress - the component shows stage completion, not overall percentage
      expect(screen.getByText('Overall Progress')).toBeInTheDocument();
      expect(screen.getByText('70%')).toBeInTheDocument();
    });
  });

  describe('Stage Dependencies', () => {
    it('shows blocked status when prerequisites not met', () => {
      const lowFoundationProgress: GoalProgress[] = [
        {
          ...mockGoalProgresses[0],
          goalId: 'mindfulness_practice',
          progress: 20
        },
        {
          ...mockGoalProgresses[1],
          goalId: 'anxiety_reduction',
          progress: 30
        }
      ];

      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice', 'anxiety_reduction']}
          goalProgresses={lowFoundationProgress}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      // Skill development should be blocked if foundation isn't complete
      expect(screen.getByText('BLOCKED')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('provides proper ARIA labels and roles', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      // Stage icons should be clickable
      const stageIcon = screen.getByText('🌱');
      expect(stageIcon.closest('div')).toHaveClass('cursor-pointer');
    });

    it('provides meaningful empty state message', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={[]}
          goalProgresses={[]}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      expect(screen.getByText('Select therapeutic goals to see your personalized journey map')).toBeInTheDocument();
    });
  });

  describe('Goal Label Formatting', () => {
    it('formats goal IDs into readable labels', () => {
      render(
        <TherapeuticJourneyMap
          selectedGoals={['mindfulness_practice']}
          goalProgresses={mockGoalProgresses}
          approachAnalysis={mockApproachAnalysis}
        />
      );

      const stageIcon = screen.getByText('🌱');
      fireEvent.click(stageIcon);

      expect(screen.getByText('Mindfulness Practice')).toBeInTheDocument();
    });
  });
});
