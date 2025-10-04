import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import GoalProgressChart from '../GoalProgressChart';
import { GoalProgress } from '../../../../services/goalProgressService';

// Mock Chart.js components
jest.mock('react-chartjs-2', () => ({
  Line: ({ data, options }: any) => (
    <div data-testid="line-chart" data-chart-data={JSON.stringify(data)} data-chart-options={JSON.stringify(options)}>
      Line Chart
    </div>
  ),
  Bar: ({ data, options }: any) => (
    <div data-testid="bar-chart" data-chart-data={JSON.stringify(data)} data-chart-options={JSON.stringify(options)}>
      Bar Chart
    </div>
  ),
  Radar: ({ data, options }: any) => (
    <div data-testid="radar-chart" data-chart-data={JSON.stringify(data)} data-chart-options={JSON.stringify(options)}>
      Radar Chart
    </div>
  ),
  Doughnut: ({ data, options }: any) => (
    <div data-testid="doughnut-chart" data-chart-data={JSON.stringify(data)} data-chart-options={JSON.stringify(options)}>
      Doughnut Chart
    </div>
  ),
}));

// Mock Chart.js registration
jest.mock('chart.js', () => ({
  Chart: {
    register: jest.fn(),
  },
  CategoryScale: {},
  LinearScale: {},
  PointElement: {},
  LineElement: {},
  BarElement: {},
  Title: {},
  Tooltip: {},
  Legend: {},
  Filler: {},
  RadialLinearScale: {},
  ArcElement: {},
}));

describe('GoalProgressChart', () => {
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
      therapeuticApproaches: ['CBT', 'Mindfulness']
    },
    {
      goalId: 'mindfulness_practice',
      progress: 50,
      startDate: new Date('2024-01-01'),
      lastUpdated: new Date('2024-01-15'),
      milestones: [],
      progressHistory: [],
      status: 'in_progress',
      estimatedCompletion: new Date('2024-03-01'),
      difficultyLevel: 'beginner',
      therapeuticApproaches: ['Mindfulness', 'ACT']
    },
    {
      goalId: 'stress_management',
      progress: 25,
      startDate: new Date('2024-01-01'),
      lastUpdated: new Date('2024-01-15'),
      milestones: [],
      progressHistory: [],
      status: 'not_started',
      estimatedCompletion: new Date('2024-04-01'),
      difficultyLevel: 'beginner',
      therapeuticApproaches: ['CBT']
    }
  ];

  describe('Rendering', () => {
    it('renders line chart by default', () => {
      render(<GoalProgressChart goalProgresses={mockGoalProgresses} />);

      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      expect(screen.getByText('Goal Progress Trends')).toBeInTheDocument();
    });

    it('renders different chart types', () => {
      const { rerender } = render(
        <GoalProgressChart goalProgresses={mockGoalProgresses} chartType="bar" />
      );
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();

      rerender(<GoalProgressChart goalProgresses={mockGoalProgresses} chartType="radar" />);
      expect(screen.getByTestId('radar-chart')).toBeInTheDocument();

      rerender(<GoalProgressChart goalProgresses={mockGoalProgresses} chartType="doughnut" />);
      expect(screen.getByTestId('doughnut-chart')).toBeInTheDocument();
    });

    it('shows empty state when no progress data', () => {
      render(<GoalProgressChart goalProgresses={[]} />);

      expect(screen.getByText('No progress data available')).toBeInTheDocument();
      expect(screen.getByText('Start tracking goals to see progress visualization')).toBeInTheDocument();
      expect(screen.getByText('📊')).toBeInTheDocument();
    });

    it('applies custom className and height', () => {
      const { container } = render(
        <GoalProgressChart
          goalProgresses={mockGoalProgresses}
          className="custom-class"
          height={400}
        />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Chart Configuration', () => {
    it('configures line chart with proper data structure', () => {
      render(<GoalProgressChart goalProgresses={mockGoalProgresses} chartType="line" />);

      const chart = screen.getByTestId('line-chart');
      const chartData = JSON.parse(chart.getAttribute('data-chart-data') || '{}');
      
      expect(chartData.labels).toBeDefined();
      expect(chartData.datasets).toBeDefined();
      expect(chartData.datasets.length).toBe(mockGoalProgresses.length);
    });

    it('configures radar chart with current progress data', () => {
      render(<GoalProgressChart goalProgresses={mockGoalProgresses} chartType="radar" />);

      const chart = screen.getByTestId('radar-chart');
      const chartData = JSON.parse(chart.getAttribute('data-chart-data') || '{}');
      
      expect(chartData.labels).toEqual([
        'Anxiety Reduction',
        'Mindfulness Practice',
        'Stress Management'
      ]);
      expect(chartData.datasets[0].data).toEqual([75, 50, 25]);
    });

    it('configures doughnut chart with progress percentages', () => {
      render(<GoalProgressChart goalProgresses={mockGoalProgresses} chartType="doughnut" />);

      const chart = screen.getByTestId('doughnut-chart');
      const chartData = JSON.parse(chart.getAttribute('data-chart-data') || '{}');
      
      expect(chartData.datasets[0].data).toEqual([75, 50, 25]);
    });
  });

  describe('Goal Filtering', () => {
    it('filters progress data by selected goals', () => {
      render(
        <GoalProgressChart
          goalProgresses={mockGoalProgresses}
          selectedGoals={['anxiety_reduction', 'mindfulness_practice']}
          chartType="radar"
        />
      );

      const chart = screen.getByTestId('radar-chart');
      const chartData = JSON.parse(chart.getAttribute('data-chart-data') || '{}');
      
      expect(chartData.labels).toHaveLength(2);
      expect(chartData.datasets[0].data).toEqual([75, 50]);
    });

    it('shows all goals when no selection filter', () => {
      render(<GoalProgressChart goalProgresses={mockGoalProgresses} chartType="radar" />);

      const chart = screen.getByTestId('radar-chart');
      const chartData = JSON.parse(chart.getAttribute('data-chart-data') || '{}');
      
      expect(chartData.labels).toHaveLength(3);
      expect(chartData.datasets[0].data).toEqual([75, 50, 25]);
    });
  });

  describe('Progress Summary', () => {
    it('displays progress summary statistics', () => {
      render(<GoalProgressChart goalProgresses={mockGoalProgresses} />);

      // Average progress: (75 + 50 + 25) / 3 = 50%
      expect(screen.getByText('50%')).toBeInTheDocument();
      expect(screen.getByText('Average Progress')).toBeInTheDocument();

      // Near complete (>= 75%): 1 goal
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('Near Complete')).toBeInTheDocument();

      // In progress (25-74%): 1 goal
      expect(screen.getByText('In Progress')).toBeInTheDocument();

      // Getting started (< 25%): 1 goal
      expect(screen.getByText('Getting Started')).toBeInTheDocument();
    });

    it('shows goal count in header', () => {
      render(<GoalProgressChart goalProgresses={mockGoalProgresses} />);

      expect(screen.getByText('3 goals')).toBeInTheDocument();
    });

    it('shows filtered goal count', () => {
      render(
        <GoalProgressChart
          goalProgresses={mockGoalProgresses}
          selectedGoals={['anxiety_reduction']}
        />
      );

      expect(screen.getByText('1 goal')).toBeInTheDocument();
    });
  });

  describe('Time Range', () => {
    it('displays time range for line/bar charts', () => {
      render(
        <GoalProgressChart
          goalProgresses={mockGoalProgresses}
          chartType="line"
          timeRange="week"
        />
      );

      expect(screen.getByText('7 days')).toBeInTheDocument();
    });

    it('does not show time range for radar/doughnut charts', () => {
      render(
        <GoalProgressChart
          goalProgresses={mockGoalProgresses}
          chartType="radar"
          timeRange="week"
        />
      );

      expect(screen.queryByText('7 days')).not.toBeInTheDocument();
    });
  });

  describe('Legend and Options', () => {
    it('shows legend when enabled', () => {
      render(
        <GoalProgressChart
          goalProgresses={mockGoalProgresses}
          showLegend={true}
        />
      );

      const chart = screen.getByTestId('line-chart');
      const chartOptions = JSON.parse(chart.getAttribute('data-chart-options') || '{}');
      
      expect(chartOptions.plugins.legend.display).toBe(true);
    });

    it('hides legend when disabled', () => {
      render(
        <GoalProgressChart
          goalProgresses={mockGoalProgresses}
          showLegend={false}
        />
      );

      const chart = screen.getByTestId('line-chart');
      const chartOptions = JSON.parse(chart.getAttribute('data-chart-options') || '{}');
      
      expect(chartOptions.plugins.legend.display).toBe(false);
    });
  });

  describe('Accessibility', () => {
    it('provides meaningful chart titles', () => {
      render(<GoalProgressChart goalProgresses={mockGoalProgresses} chartType="line" />);
      expect(screen.getByText('Goal Progress Trends')).toBeInTheDocument();

      render(<GoalProgressChart goalProgresses={mockGoalProgresses} chartType="radar" />);
      expect(screen.getByText('Goal Progress Overview')).toBeInTheDocument();
    });

    it('provides descriptive empty state', () => {
      render(<GoalProgressChart goalProgresses={[]} />);

      expect(screen.getByText('No progress data available')).toBeInTheDocument();
      expect(screen.getByText('Start tracking goals to see progress visualization')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('handles empty selected goals gracefully', () => {
      render(
        <GoalProgressChart
          goalProgresses={mockGoalProgresses}
          selectedGoals={[]}
        />
      );

      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    });

    it('handles goals with zero progress', () => {
      const zeroProgressGoals: GoalProgress[] = [
        {
          ...mockGoalProgresses[0],
          progress: 0
        }
      ];

      render(<GoalProgressChart goalProgresses={zeroProgressGoals} />);

      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      expect(screen.getByText('0%')).toBeInTheDocument();
    });
  });
});
