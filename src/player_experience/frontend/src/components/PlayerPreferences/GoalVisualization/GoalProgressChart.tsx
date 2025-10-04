import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Radar, Doughnut } from 'react-chartjs-2';
import { GoalProgress } from '../../../services/goalProgressService';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale,
  ArcElement
);

interface GoalProgressChartProps {
  goalProgresses: GoalProgress[];
  chartType?: 'line' | 'bar' | 'radar' | 'doughnut';
  selectedGoals?: string[];
  height?: number;
  className?: string;
  showLegend?: boolean;
  timeRange?: 'week' | 'month' | 'quarter' | 'year';
}

const GoalProgressChart: React.FC<GoalProgressChartProps> = ({
  goalProgresses,
  chartType = 'line',
  selectedGoals = [],
  height = 300,
  className = '',
  showLegend = true,
  timeRange = 'month'
}) => {
  // Helper function to get goal label
  const getGoalLabel = (goalId: string): string => {
    return goalId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Helper function to get goal color
  const getGoalColor = (goalId: string, alpha: number = 1): string => {
    const colors = [
      `rgba(59, 130, 246, ${alpha})`, // blue
      `rgba(16, 185, 129, ${alpha})`, // green
      `rgba(139, 92, 246, ${alpha})`, // purple
      `rgba(245, 158, 11, ${alpha})`, // yellow
      `rgba(239, 68, 68, ${alpha})`, // red
      `rgba(236, 72, 153, ${alpha})`, // pink
      `rgba(14, 165, 233, ${alpha})`, // sky
      `rgba(34, 197, 94, ${alpha})`, // emerald
      `rgba(168, 85, 247, ${alpha})`, // violet
      `rgba(251, 146, 60, ${alpha})`, // orange
    ];
    
    const index = goalId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
    return colors[index];
  };

  // Filter progresses based on selected goals
  const filteredProgresses = selectedGoals.length > 0 
    ? goalProgresses.filter(gp => selectedGoals.includes(gp.goalId))
    : goalProgresses;

  // Generate time-based progress data for line/bar charts
  const generateTimeBasedData = () => {
    if (!filteredProgresses.length) return { labels: [], datasets: [] };

    // Generate time labels based on range
    const now = new Date();
    const labels: string[] = [];
    const dataPoints: number = timeRange === 'week' ? 7 : timeRange === 'month' ? 30 : timeRange === 'quarter' ? 90 : 365;
    
    for (let i = dataPoints - 1; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      labels.push(date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        ...(timeRange === 'year' && { year: '2-digit' })
      }));
    }

    const datasets = filteredProgresses.map((goalProgress, index) => {
      // Simulate progress data over time (in real implementation, this would come from actual history)
      const data = labels.map((_, i) => {
        const progressRatio = i / (labels.length - 1);
        const currentProgress = goalProgress.progress;
        const simulatedProgress = Math.max(0, Math.min(100, currentProgress * progressRatio + Math.random() * 10 - 5));
        return Math.round(simulatedProgress);
      });

      return {
        label: getGoalLabel(goalProgress.goalId),
        data,
        borderColor: getGoalColor(goalProgress.goalId),
        backgroundColor: getGoalColor(goalProgress.goalId, 0.1),
        fill: chartType === 'line',
        tension: 0.4,
      };
    });

    return { labels, datasets };
  };

  // Generate current progress data for radar/doughnut charts
  const generateCurrentProgressData = () => {
    if (!filteredProgresses.length) return { labels: [], datasets: [] };

    const labels = filteredProgresses.map(gp => getGoalLabel(gp.goalId));
    const data = filteredProgresses.map(gp => gp.progress);
    const colors = filteredProgresses.map(gp => getGoalColor(gp.goalId));
    const backgroundColors = filteredProgresses.map(gp => getGoalColor(gp.goalId, 0.6));

    if (chartType === 'radar') {
      return {
        labels,
        datasets: [{
          label: 'Goal Progress',
          data,
          borderColor: 'rgba(59, 130, 246, 1)',
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          pointBackgroundColor: colors,
          pointBorderColor: colors,
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: colors,
        }]
      };
    }

    // Doughnut chart
    return {
      labels,
      datasets: [{
        data,
        backgroundColor: backgroundColors,
        borderColor: colors,
        borderWidth: 2,
      }]
    };
  };

  // Chart options
  const getChartOptions = () => {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: showLegend,
          position: 'top' as const,
        },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              if (chartType === 'radar' || chartType === 'doughnut') {
                return `${context.label}: ${context.parsed}%`;
              }
              return `${context.dataset.label}: ${context.parsed.y}%`;
            }
          }
        }
      },
    };

    if (chartType === 'line' || chartType === 'bar') {
      return {
        ...baseOptions,
        scales: {
          x: {
            display: true,
            title: {
              display: true,
              text: 'Time'
            }
          },
          y: {
            display: true,
            title: {
              display: true,
              text: 'Progress (%)'
            },
            min: 0,
            max: 100,
          }
        }
      };
    }

    if (chartType === 'radar') {
      return {
        ...baseOptions,
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            ticks: {
              stepSize: 20,
              callback: (value: any) => `${value}%`
            }
          }
        }
      };
    }

    return baseOptions;
  };

  // Get chart data based on type
  const chartData = (chartType === 'line' || chartType === 'bar') 
    ? generateTimeBasedData() 
    : generateCurrentProgressData();

  // Get chart component
  const getChartComponent = () => {
    switch (chartType) {
      case 'line':
        return <Line data={chartData} options={getChartOptions()} />;
      case 'bar':
        return <Bar data={chartData} options={getChartOptions()} />;
      case 'radar':
        return <Radar data={chartData} options={getChartOptions()} />;
      case 'doughnut':
        return <Doughnut data={chartData} options={getChartOptions()} />;
      default:
        return <Line data={chartData} options={getChartOptions()} />;
    }
  };

  if (!filteredProgresses.length) {
    return (
      <div className={`flex items-center justify-center bg-gray-50 rounded-lg ${className}`} style={{ height }}>
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-2">📊</div>
          <p>No progress data available</p>
          <p className="text-sm">Start tracking goals to see progress visualization</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Goal Progress {chartType === 'radar' || chartType === 'doughnut' ? 'Overview' : 'Trends'}
        </h3>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <span>{filteredProgresses.length} goal{filteredProgresses.length !== 1 ? 's' : ''}</span>
          {(chartType === 'line' || chartType === 'bar') && (
            <>
              <span>•</span>
              <span>{timeRange === 'week' ? '7 days' : timeRange === 'month' ? '30 days' : timeRange === 'quarter' ? '90 days' : '1 year'}</span>
            </>
          )}
        </div>
      </div>
      
      <div style={{ height: height - 80 }}>
        {getChartComponent()}
      </div>

      {/* Progress summary */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="font-semibold text-gray-900">
              {Math.round(filteredProgresses.reduce((sum, gp) => sum + gp.progress, 0) / filteredProgresses.length)}%
            </div>
            <div className="text-gray-500">Average Progress</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-green-600">
              {filteredProgresses.filter(gp => gp.progress >= 75).length}
            </div>
            <div className="text-gray-500">Near Complete</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-blue-600">
              {filteredProgresses.filter(gp => gp.progress >= 25 && gp.progress < 75).length}
            </div>
            <div className="text-gray-500">In Progress</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-gray-600">
              {filteredProgresses.filter(gp => gp.progress < 25).length}
            </div>
            <div className="text-gray-500">Getting Started</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GoalProgressChart;
