import React from 'react';
import { Line, Bar } from 'react-chartjs-2';
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
} from 'chart.js';

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
  Filler
);

interface ProgressVizSeries {
  time_buckets: string[];
  series: {
    sessions: number[];
    duration_minutes: number[];
  };
  meta: {
    period_days: number;
    units: {
      duration_minutes: string;
    };
  };
}

interface ProgressChartProps {
  data: ProgressVizSeries;
  chartType?: 'line' | 'bar';
  metric?: 'sessions' | 'duration_minutes' | 'both';
  height?: number;
  className?: string;
}

const ProgressChart: React.FC<ProgressChartProps> = ({
  data,
  chartType = 'line',
  metric = 'both',
  height = 300,
  className = '',
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const chartData = {
    labels: data.time_buckets.map(formatDate),
    datasets: [
      ...(metric === 'sessions' || metric === 'both'
        ? [
            {
              label: 'Sessions',
              data: data.series.sessions,
              borderColor: 'rgb(59, 130, 246)',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              fill: chartType === 'line',
              tension: 0.4,
              yAxisID: 'y',
            },
          ]
        : []),
      ...(metric === 'duration_minutes' || metric === 'both'
        ? [
            {
              label: 'Duration (minutes)',
              data: data.series.duration_minutes,
              borderColor: 'rgb(16, 185, 129)',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              fill: chartType === 'line',
              tension: 0.4,
              yAxisID: metric === 'both' ? 'y1' : 'y',
            },
          ]
        : []),
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `Progress Over Last ${data.meta.period_days} Days`,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date',
        },
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: metric === 'duration_minutes' ? 'Duration (minutes)' : 'Sessions',
        },
        beginAtZero: true,
      },
      ...(metric === 'both'
        ? {
            y1: {
              type: 'linear' as const,
              display: true,
              position: 'right' as const,
              title: {
                display: true,
                text: 'Duration (minutes)',
              },
              beginAtZero: true,
              grid: {
                drawOnChartArea: false,
              },
            },
          }
        : {}),
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  };

  const ChartComponent = chartType === 'line' ? Line : Bar;

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-4 ${className}`}>
      <div style={{ height: `${height}px` }}>
        <ChartComponent data={chartData} options={options} />
      </div>
    </div>
  );
};

export default ProgressChart;