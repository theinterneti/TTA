import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProgressChart from '../ProgressChart';

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
}));

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
}));

const mockProgressData = {
  time_buckets: ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
  series: {
    sessions: [2, 1, 3, 2, 1],
    duration_minutes: [45, 30, 60, 40, 25],
  },
  meta: {
    period_days: 5,
    units: {
      duration_minutes: 'minutes',
    },
  },
};

describe('ProgressChart', () => {
  it('renders line chart by default', () => {
    render(<ProgressChart data={mockProgressData} />);

    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    expect(screen.queryByTestId('bar-chart')).not.toBeInTheDocument();
  });

  it('renders bar chart when specified', () => {
    render(<ProgressChart data={mockProgressData} chartType="bar" />);

    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    expect(screen.queryByTestId('line-chart')).not.toBeInTheDocument();
  });

  it('includes both metrics by default', () => {
    render(<ProgressChart data={mockProgressData} />);

    const chartElement = screen.getByTestId('line-chart');
    const chartData = JSON.parse(chartElement.getAttribute('data-chart-data') || '{}');

    expect(chartData.datasets).toHaveLength(2);
    expect(chartData.datasets[0].label).toBe('Sessions');
    expect(chartData.datasets[1].label).toBe('Duration (minutes)');
  });

  it('shows only sessions when metric is sessions', () => {
    render(<ProgressChart data={mockProgressData} metric="sessions" />);

    const chartElement = screen.getByTestId('line-chart');
    const chartData = JSON.parse(chartElement.getAttribute('data-chart-data') || '{}');

    expect(chartData.datasets).toHaveLength(1);
    expect(chartData.datasets[0].label).toBe('Sessions');
  });

  it('shows only duration when metric is duration_minutes', () => {
    render(<ProgressChart data={mockProgressData} metric="duration_minutes" />);

    const chartElement = screen.getByTestId('line-chart');
    const chartData = JSON.parse(chartElement.getAttribute('data-chart-data') || '{}');

    expect(chartData.datasets).toHaveLength(1);
    expect(chartData.datasets[0].label).toBe('Duration (minutes)');
  });

  it('formats dates correctly in labels', () => {
    render(<ProgressChart data={mockProgressData} />);

    const chartElement = screen.getByTestId('line-chart');
    const chartData = JSON.parse(chartElement.getAttribute('data-chart-data') || '{}');

    expect(chartData.labels).toEqual(['Jan 1', 'Jan 2', 'Jan 3', 'Jan 4', 'Jan 5']);
  });

  it('applies custom className', () => {
    const { container } = render(<ProgressChart data={mockProgressData} className="custom-class" />);

    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('sets correct chart title based on period', () => {
    render(<ProgressChart data={mockProgressData} />);

    const chartElement = screen.getByTestId('line-chart');
    const chartOptions = JSON.parse(chartElement.getAttribute('data-chart-options') || '{}');

    expect(chartOptions.plugins.title.text).toBe('Progress Over Last 5 Days');
  });

  it('configures dual y-axes for both metrics', () => {
    render(<ProgressChart data={mockProgressData} metric="both" />);

    const chartElement = screen.getByTestId('line-chart');
    const chartOptions = JSON.parse(chartElement.getAttribute('data-chart-options') || '{}');

    expect(chartOptions.scales.y).toBeDefined();
    expect(chartOptions.scales.y1).toBeDefined();
    expect(chartOptions.scales.y1.position).toBe('right');
  });

  it('uses single y-axis for single metric', () => {
    render(<ProgressChart data={mockProgressData} metric="sessions" />);

    const chartElement = screen.getByTestId('line-chart');
    const chartOptions = JSON.parse(chartElement.getAttribute('data-chart-options') || '{}');

    expect(chartOptions.scales.y).toBeDefined();
    expect(chartOptions.scales.y1).toBeUndefined();
  });
});
