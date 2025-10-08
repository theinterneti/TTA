import React, { useState } from 'react';
import { GoalRelationshipMap } from '../../../services/goalRelationshipService';
import { GoalProgress } from '../../../services/goalProgressService';
import { TherapeuticApproachAnalysis } from '../../../services/therapeuticApproachAlignmentService';
import GoalRelationshipGraph from './GoalRelationshipGraph';
import GoalProgressChart from './GoalProgressChart';
import TherapeuticJourneyMap from './TherapeuticJourneyMap';

interface GoalVisualizationDashboardProps {
  selectedGoals: string[];
  relationshipMap: GoalRelationshipMap;
  goalProgresses: GoalProgress[];
  approachAnalysis: TherapeuticApproachAnalysis;
  className?: string;
  onGoalClick?: (goalId: string) => void;
  onStageClick?: (stageId: string) => void;
}

type VisualizationType = 'relationships' | 'progress' | 'journey' | 'overview';
type ChartType = 'line' | 'bar' | 'radar' | 'doughnut';
type TimeRange = 'week' | 'month' | 'quarter' | 'year';

const GoalVisualizationDashboard: React.FC<GoalVisualizationDashboardProps> = ({
  selectedGoals,
  relationshipMap,
  goalProgresses,
  approachAnalysis,
  className = '',
  onGoalClick,
  onStageClick
}) => {
  const [activeView, setActiveView] = useState<VisualizationType>('overview');
  const [chartType, setChartType] = useState<ChartType>('line');
  const [timeRange, setTimeRange] = useState<TimeRange>('month');

  // Navigation tabs
  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊', description: 'Complete visualization dashboard' },
    { id: 'relationships', label: 'Relationships', icon: '🔗', description: 'Goal connections and conflicts' },
    { id: 'progress', label: 'Progress', icon: '📈', description: 'Progress tracking and trends' },
    { id: 'journey', label: 'Journey', icon: '🗺️', description: 'Therapeutic journey mapping' }
  ];

  // Chart type options for progress view
  const chartTypes = [
    { id: 'line', label: 'Line Chart', icon: '📈' },
    { id: 'bar', label: 'Bar Chart', icon: '📊' },
    { id: 'radar', label: 'Radar Chart', icon: '🎯' },
    { id: 'doughnut', label: 'Doughnut Chart', icon: '🍩' }
  ];

  // Time range options
  const timeRanges = [
    { id: 'week', label: '7 Days' },
    { id: 'month', label: '30 Days' },
    { id: 'quarter', label: '90 Days' },
    { id: 'year', label: '1 Year' }
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-blue-600">{selectedGoals.length}</div>
              <div className="text-sm text-blue-700">Active Goals</div>
            </div>
            <div className="text-2xl">🎯</div>
          </div>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-green-600">
                {Math.round(relationshipMap.overallCompatibility * 100)}%
              </div>
              <div className="text-sm text-green-700">Compatibility</div>
            </div>
            <div className="text-2xl">🤝</div>
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(approachAnalysis.treatmentEffectivenessScore * 100)}%
              </div>
              <div className="text-sm text-purple-700">Effectiveness</div>
            </div>
            <div className="text-2xl">⚡</div>
          </div>
        </div>

        <div className="bg-orange-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {goalProgresses.length > 0
                  ? Math.round(goalProgresses.reduce((sum, gp) => sum + gp.progress, 0) / goalProgresses.length)
                  : 0}%
              </div>
              <div className="text-sm text-orange-700">Avg Progress</div>
            </div>
            <div className="text-2xl">📊</div>
          </div>
        </div>
      </div>

      {/* Main visualizations grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GoalRelationshipGraph
          relationshipMap={relationshipMap}
          width={500}
          height={350}
          onNodeClick={onGoalClick}
        />

        <GoalProgressChart
          goalProgresses={goalProgresses}
          chartType="radar"
          selectedGoals={selectedGoals}
          height={350}
          showLegend={false}
        />
      </div>

      {/* Journey map */}
      <TherapeuticJourneyMap
        selectedGoals={selectedGoals}
        goalProgresses={goalProgresses}
        approachAnalysis={approachAnalysis}
        onStageClick={onStageClick}
      />
    </div>
  );

  const renderRelationships = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Goal Relationship Network</h3>
        <p className="text-gray-600">Explore connections, synergies, and conflicts between your therapeutic goals</p>
      </div>

      <GoalRelationshipGraph
        relationshipMap={relationshipMap}
        width={800}
        height={500}
        onNodeClick={onGoalClick}
        className="mx-auto"
      />

      {/* Relationship insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-green-50 rounded-lg p-4">
          <h4 className="font-semibold text-green-900 mb-2">Synergistic Pairs</h4>
          <div className="text-sm text-green-700">
            {relationshipMap.relationships.filter(r => r.relationshipType === 'synergistic').length} connections
          </div>
        </div>

        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">Complementary Goals</h4>
          <div className="text-sm text-blue-700">
            {relationshipMap.relationships.filter(r => r.relationshipType === 'complementary').length} connections
          </div>
        </div>

        <div className="bg-red-50 rounded-lg p-4">
          <h4 className="font-semibold text-red-900 mb-2">Potential Conflicts</h4>
          <div className="text-sm text-red-700">
            {relationshipMap.conflicts.length} identified
          </div>
        </div>
      </div>
    </div>
  );

  const renderProgress = () => (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Progress Visualization</h3>
          <p className="text-gray-600">Track your therapeutic goal progress over time</p>
        </div>

        <div className="flex items-center space-x-4">
          {/* Chart type selector */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Chart Type:</label>
            <select
              value={chartType}
              onChange={(e) => setChartType(e.target.value as ChartType)}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            >
              {chartTypes.map(type => (
                <option key={type.id} value={type.id}>
                  {type.icon} {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Time range selector (for line/bar charts) */}
          {(chartType === 'line' || chartType === 'bar') && (
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Time Range:</label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value as TimeRange)}
                className="border border-gray-300 rounded px-2 py-1 text-sm"
              >
                {timeRanges.map(range => (
                  <option key={range.id} value={range.id}>
                    {range.label}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Progress chart */}
      <GoalProgressChart
        goalProgresses={goalProgresses}
        chartType={chartType}
        selectedGoals={selectedGoals}
        height={400}
        timeRange={timeRange}
        showLegend={true}
      />
    </div>
  );

  const renderJourney = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Therapeutic Journey</h3>
        <p className="text-gray-600">Your personalized path through therapeutic stages and milestones</p>
      </div>

      <TherapeuticJourneyMap
        selectedGoals={selectedGoals}
        goalProgresses={goalProgresses}
        approachAnalysis={approachAnalysis}
        onStageClick={onStageClick}
      />
    </div>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'overview': return renderOverview();
      case 'relationships': return renderRelationships();
      case 'progress': return renderProgress();
      case 'journey': return renderJourney();
      default: return renderOverview();
    }
  };

  if (!selectedGoals.length) {
    return (
      <div className={`bg-gray-50 rounded-lg p-12 text-center ${className}`}>
        <div className="text-6xl mb-4">📊</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Goal Visualization Dashboard</h3>
        <p className="text-gray-600 mb-4">
          Select therapeutic goals to unlock powerful visualizations that help you understand relationships,
          track progress, and navigate your therapeutic journey.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
          {tabs.map(tab => (
            <div key={tab.id} className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="text-2xl mb-1">{tab.icon}</div>
              <div className="font-medium text-gray-900 text-sm">{tab.label}</div>
              <div className="text-xs text-gray-500">{tab.description}</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Navigation tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6" aria-label="Visualization tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveView(tab.id as VisualizationType)}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeView === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              aria-current={activeView === tab.id ? 'page' : undefined}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="p-6">
        {renderContent()}
      </div>
    </div>
  );
};

export default GoalVisualizationDashboard;
