import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import GoalVisualizationDashboard from '../GoalVisualizationDashboard';
import { GoalRelationshipMap } from '../../../../services/goalRelationshipService';
import { GoalProgress } from '../../../../services/goalProgressService';
import { TherapeuticApproachAnalysis } from '../../../../services/therapeuticApproachAlignmentService';

// Mock the child components
jest.mock('../GoalRelationshipGraph', () => {
  return function MockGoalRelationshipGraph({ relationshipMap, onNodeClick }: any) {
    return (
      <div data-testid="goal-relationship-graph">
        <div>Goals: {relationshipMap.goals.join(', ')}</div>
        <button onClick={() => onNodeClick?.('test-goal')}>Click Node</button>
      </div>
    );
  };
});

jest.mock('../GoalProgressChart', () => {
  return function MockGoalProgressChart({ goalProgresses, chartType, selectedGoals }: any) {
    return (
      <div data-testid="goal-progress-chart">
        <div>Chart Type: {chartType}</div>
        <div>Goals: {selectedGoals.join(', ')}</div>
        <div>Progress Count: {goalProgresses.length}</div>
      </div>
    );
  };
});

jest.mock('../TherapeuticJourneyMap', () => {
  return function MockTherapeuticJourneyMap({ selectedGoals, onStageClick }: any) {
    return (
      <div data-testid="therapeutic-journey-map">
        <div>Selected Goals: {selectedGoals.join(', ')}</div>
        <button onClick={() => onStageClick?.('test-stage')}>Click Stage</button>
      </div>
    );
  };
});

describe('GoalVisualizationDashboard', () => {
  const mockRelationshipMap: GoalRelationshipMap = {
    goals: ['anxiety_reduction', 'mindfulness_practice'],
    relationships: [],
    conflicts: [],
    complementarySuggestions: [],
    overallCompatibility: 0.85,
    therapeuticCoherence: 0.9
  };

  const mockGoalProgresses: GoalProgress[] = [
    {
      goalId: 'anxiety_reduction',
      progress: 75,
      startDate: new Date('2024-01-01'),
      lastUpdated: new Date('2024-01-15'),
      milestones: [],
      progressHistory: [],
      status: 'in_progress',
      estimatedCompletion: new Date('2024-02-01'),
      difficultyLevel: 'intermediate',
      therapeuticApproaches: ['CBT']
    }
  ];

  const mockApproachAnalysis: TherapeuticApproachAnalysis = {
    selectedGoals: ['anxiety_reduction', 'mindfulness_practice'],
    recommendedApproaches: [],
    approachAlignments: [],
    approachCompatibilities: [],
    overallCoherence: 0.8,
    treatmentEffectivenessScore: 0.85,
    integrationRecommendations: []
  };

  const defaultProps = {
    selectedGoals: ['anxiety_reduction', 'mindfulness_practice'],
    relationshipMap: mockRelationshipMap,
    goalProgresses: mockGoalProgresses,
    approachAnalysis: mockApproachAnalysis
  };

  describe('Rendering', () => {
    it('renders dashboard with navigation tabs', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Relationships')).toBeInTheDocument();
      expect(screen.getByText('Progress')).toBeInTheDocument();
      expect(screen.getByText('Journey')).toBeInTheDocument();
    });

    it('shows empty state when no goals selected', () => {
      render(
        <GoalVisualizationDashboard
          {...defaultProps}
          selectedGoals={[]}
        />
      );

      expect(screen.getByText('Goal Visualization Dashboard')).toBeInTheDocument();
      expect(screen.getByText(/Select therapeutic goals to unlock powerful visualizations/)).toBeInTheDocument();
      expect(screen.getAllByText('📊')).toHaveLength(2); // One in main icon, one in feature card
    });

    it('applies custom className', () => {
      const { container } = render(
        <GoalVisualizationDashboard
          {...defaultProps}
          className="custom-class"
        />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Tab Navigation', () => {
    it('starts with overview tab active', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      const overviewTab = screen.getByText('Overview');
      expect(overviewTab).toHaveClass('border-blue-500', 'text-blue-600');
    });

    it('switches to relationships tab when clicked', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      const relationshipsTab = screen.getByText('Relationships');
      fireEvent.click(relationshipsTab);

      expect(relationshipsTab).toHaveClass('border-blue-500', 'text-blue-600');
      expect(screen.getByText('Goal Relationship Network')).toBeInTheDocument();
    });

    it('switches to progress tab when clicked', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      const progressTab = screen.getByText('Progress');
      fireEvent.click(progressTab);

      expect(progressTab).toHaveClass('border-blue-500', 'text-blue-600');
      expect(screen.getByText('Progress Visualization')).toBeInTheDocument();
    });

    it('switches to journey tab when clicked', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      const journeyTab = screen.getByText('Journey');
      fireEvent.click(journeyTab);

      expect(journeyTab).toHaveClass('border-blue-500', 'text-blue-600');
      expect(screen.getByText('Therapeutic Journey')).toBeInTheDocument();
    });
  });

  describe('Overview Tab', () => {
    it('displays summary cards with correct metrics', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      expect(screen.getByText('2')).toBeInTheDocument(); // Active Goals
      expect(screen.getByText('Active Goals')).toBeInTheDocument();

      expect(screen.getAllByText('85%')).toHaveLength(2); // Compatibility and Effectiveness both show 85%
      expect(screen.getByText('Compatibility')).toBeInTheDocument();

      expect(screen.getByText('Effectiveness')).toBeInTheDocument();
      expect(screen.getByText('Avg Progress')).toBeInTheDocument();
    });

    it('renders all visualization components in overview', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      expect(screen.getByTestId('goal-relationship-graph')).toBeInTheDocument();
      expect(screen.getByTestId('goal-progress-chart')).toBeInTheDocument();
      expect(screen.getByTestId('therapeutic-journey-map')).toBeInTheDocument();
    });
  });

  describe('Relationships Tab', () => {
    it('displays relationship insights', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      fireEvent.click(screen.getByText('Relationships'));

      expect(screen.getByText('Synergistic Pairs')).toBeInTheDocument();
      expect(screen.getByText('Complementary Goals')).toBeInTheDocument();
      expect(screen.getByText('Potential Conflicts')).toBeInTheDocument();
    });

    it('renders relationship graph with larger dimensions', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      fireEvent.click(screen.getByText('Relationships'));

      const graph = screen.getByTestId('goal-relationship-graph');
      expect(graph).toBeInTheDocument();
    });
  });

  describe('Progress Tab', () => {
    it('displays chart type selector', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      fireEvent.click(screen.getByText('Progress'));

      expect(screen.getByText('Chart Type:')).toBeInTheDocument();
      expect(screen.getByDisplayValue('📈 Line Chart')).toBeInTheDocument();
    });

    it('changes chart type when selector is used', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      fireEvent.click(screen.getByText('Progress'));

      const chartTypeSelect = screen.getByDisplayValue('📈 Line Chart');
      fireEvent.change(chartTypeSelect, { target: { value: 'bar' } });

      const progressChart = screen.getByTestId('goal-progress-chart');
      expect(progressChart).toHaveTextContent('Chart Type: bar');
    });

    it('shows time range selector for line and bar charts', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      fireEvent.click(screen.getByText('Progress'));

      expect(screen.getByText('Time Range:')).toBeInTheDocument();
      expect(screen.getByDisplayValue('30 Days')).toBeInTheDocument();
    });

    it('hides time range selector for radar and doughnut charts', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      fireEvent.click(screen.getByText('Progress'));

      const chartTypeSelect = screen.getByDisplayValue('📈 Line Chart');
      fireEvent.change(chartTypeSelect, { target: { value: 'radar' } });

      expect(screen.queryByText('Time Range:')).not.toBeInTheDocument();
    });
  });

  describe('Journey Tab', () => {
    it('displays journey description', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      fireEvent.click(screen.getByText('Journey'));

      expect(screen.getByText('Your personalized path through therapeutic stages and milestones')).toBeInTheDocument();
    });

    it('renders therapeutic journey map', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      fireEvent.click(screen.getByText('Journey'));

      expect(screen.getByTestId('therapeutic-journey-map')).toBeInTheDocument();
    });
  });

  describe('Event Handlers', () => {
    it('calls onGoalClick when goal is clicked in visualization', () => {
      const mockOnGoalClick = jest.fn();
      render(
        <GoalVisualizationDashboard
          {...defaultProps}
          onGoalClick={mockOnGoalClick}
        />
      );

      const clickButton = screen.getByText('Click Node');
      fireEvent.click(clickButton);

      expect(mockOnGoalClick).toHaveBeenCalledWith('test-goal');
    });

    it('calls onStageClick when stage is clicked in journey map', () => {
      const mockOnStageClick = jest.fn();
      render(
        <GoalVisualizationDashboard
          {...defaultProps}
          onStageClick={mockOnStageClick}
        />
      );

      const clickButton = screen.getByText('Click Stage');
      fireEvent.click(clickButton);

      expect(mockOnStageClick).toHaveBeenCalledWith('test-stage');
    });
  });

  describe('Empty State Features', () => {
    it('shows feature preview cards in empty state', () => {
      render(
        <GoalVisualizationDashboard
          {...defaultProps}
          selectedGoals={[]}
        />
      );

      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Complete visualization dashboard')).toBeInTheDocument();
      expect(screen.getByText('Relationships')).toBeInTheDocument();
      expect(screen.getByText('Goal connections and conflicts')).toBeInTheDocument();
      expect(screen.getByText('Progress')).toBeInTheDocument();
      expect(screen.getByText('Progress tracking and trends')).toBeInTheDocument();
      expect(screen.getByText('Journey')).toBeInTheDocument();
      expect(screen.getByText('Therapeutic journey mapping')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes for tab navigation', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      const tabList = screen.getByRole('navigation', { name: 'Visualization tabs' });
      expect(tabList).toBeInTheDocument();

      const overviewTab = screen.getByText('Overview');
      expect(overviewTab).toHaveAttribute('aria-current', 'page');
    });

    it('updates aria-current when tab changes', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      const relationshipsTab = screen.getByText('Relationships');
      fireEvent.click(relationshipsTab);

      expect(relationshipsTab).toHaveAttribute('aria-current', 'page');

      const overviewTab = screen.getByText('Overview');
      expect(overviewTab).not.toHaveAttribute('aria-current', 'page');
    });
  });

  describe('Data Integration', () => {
    it('passes correct props to child components', () => {
      render(<GoalVisualizationDashboard {...defaultProps} />);

      const relationshipGraph = screen.getByTestId('goal-relationship-graph');
      expect(relationshipGraph).toHaveTextContent('Goals: anxiety_reduction, mindfulness_practice');

      const progressChart = screen.getByTestId('goal-progress-chart');
      expect(progressChart).toHaveTextContent('Goals: anxiety_reduction, mindfulness_practice');
      expect(progressChart).toHaveTextContent('Progress Count: 1');

      const journeyMap = screen.getByTestId('therapeutic-journey-map');
      expect(journeyMap).toHaveTextContent('Selected Goals: anxiety_reduction, mindfulness_practice');
    });
  });
});
