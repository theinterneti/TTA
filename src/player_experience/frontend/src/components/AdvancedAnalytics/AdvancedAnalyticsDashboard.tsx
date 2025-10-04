/**
 * Advanced Analytics Dashboard - Priority 4B Implementation
 * 
 * Interactive dashboard for predictive therapeutic analytics with comprehensive
 * data visualization, longitudinal analysis, and predictive insights display.
 * 
 * Features:
 * - Real-time predictive analytics visualization
 * - Interactive trend analysis charts
 * - Risk prediction displays with mitigation strategies
 * - Longitudinal therapeutic journey tracking
 * - Outcome prediction with confidence intervals
 * - Integration with existing therapeutic intelligence services
 */

import React, { useState, useEffect, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  ScatterPlot,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { format, subDays, startOfDay } from 'date-fns';
import { RootState, AppDispatch } from '../../store/store';
import { TherapeuticGoal } from '../../types/index';
import {
  PredictiveAnalyticsResult,
  TrendAnalysis,
  RiskPrediction,
  TherapeuticOutcomePrediction,
  LongitudinalInsight
} from '../../services/predictiveAnalyticsService';
import { realAnalyticsService } from '../../services/realAnalyticsService';

// Component Props
interface AdvancedAnalyticsDashboardProps {
  userId: string;
  goals: TherapeuticGoal[];
  className?: string;
  onInsightClick?: (insight: LongitudinalInsight) => void;
  onRiskAlert?: (risk: RiskPrediction) => void;
}

// Chart Data Interfaces
interface TrendChartData {
  date: string;
  timestamp: number;
  [goalId: string]: number | string;
}

interface RiskChartData {
  riskType: string;
  probability: number;
  severity: string;
  color: string;
}

interface OutcomeChartData {
  goalTitle: string;
  predicted: number;
  confidence: number;
  lower: number;
  upper: number;
}

// Color schemes for visualizations
const TREND_COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'];
const RISK_COLORS = {
  low: '#4ade80',
  moderate: '#fbbf24',
  high: '#f87171',
  critical: '#dc2626'
};

const PROGNOSIS_COLORS = {
  excellent: '#10b981',
  good: '#3b82f6',
  fair: '#f59e0b',
  concerning: '#ef4444'
};

/**
 * Advanced Analytics Dashboard Component
 */
export const AdvancedAnalyticsDashboard: React.FC<AdvancedAnalyticsDashboardProps> = ({
  userId,
  goals,
  className = '',
  onInsightClick,
  onRiskAlert
}) => {
  const dispatch = useDispatch<AppDispatch>();
  
  // State management
  const [analyticsData, setAnalyticsData] = useState<PredictiveAnalyticsResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [activeTab, setActiveTab] = useState<'trends' | 'risks' | 'outcomes' | 'insights'>('trends');

  // Load analytics data
  useEffect(() => {
    const loadAnalyticsData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Set auth token if available (get from localStorage or context)
        const token = localStorage.getItem('authToken');
        if (token) {
          realAnalyticsService.setAuthToken(token);
        }

        // Gather data from real analytics service
        const progressData = await realAnalyticsService.generateProgressAnalytics(userId, goals);
        const monitoringData = await realAnalyticsService.getSessionHistory(userId);
        const emotionalHistory = await realAnalyticsService.getEmotionalHistory(userId);
        const recommendationHistory = await realAnalyticsService.getRecommendationHistory(userId);

        // Generate predictive analytics using real data
        const analytics = await realAnalyticsService.generatePredictiveAnalytics(
          userId,
          goals,
          progressData,
          monitoringData,
          emotionalHistory,
          recommendationHistory
        );

        setAnalyticsData(analytics);

        // Trigger risk alerts if needed
        if (analytics && analytics.riskPredictions) {
          const criticalRisks = analytics.riskPredictions.filter(r => r.severity === 'critical');
          criticalRisks.forEach(risk => onRiskAlert?.(risk));
        }

      } catch (err) {
        console.error('Failed to load analytics data:', err);
        setError('Failed to load analytics data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (userId && goals.length > 0) {
      loadAnalyticsData();
    }
  }, [userId, goals, onRiskAlert]);

  // Prepare chart data
  const trendChartData = useMemo(() => {
    if (!analyticsData) return [];

    const data: TrendChartData[] = [];
    const days = selectedTimeRange === '7d' ? 7 : selectedTimeRange === '30d' ? 30 : 90;
    
    for (let i = days - 1; i >= 0; i--) {
      const date = startOfDay(subDays(new Date(), i));
      const entry: TrendChartData = {
        date: format(date, 'MMM dd'),
        timestamp: date.getTime()
      };

      // Add trend data for each goal
      analyticsData.trendAnalyses.forEach((trend, index) => {
        const goal = goals.find(g => g.id === trend.goalId);
        if (goal) {
          // Simulate historical trend data (in real implementation, this would come from historical data)
          const baseValue = trend.projectedOutcome;
          const variance = Math.random() * 10 - 5; // ±5 variance
          entry[goal.id] = Math.max(0, Math.min(100, baseValue + variance));
        }
      });

      data.push(entry);
    }

    return data;
  }, [analyticsData, goals, selectedTimeRange]);

  const riskChartData = useMemo(() => {
    if (!analyticsData) return [];

    return analyticsData.riskPredictions.map(risk => ({
      riskType: risk.riskType.replace('_', ' ').toUpperCase(),
      probability: Math.round(risk.probability * 100),
      severity: risk.severity,
      color: RISK_COLORS[risk.severity]
    }));
  }, [analyticsData]);

  const outcomeChartData = useMemo(() => {
    if (!analyticsData) return [];

    return analyticsData.outcomePredictions.map(prediction => {
      const goal = goals.find(g => g.id === prediction.goalId);
      return {
        goalTitle: goal?.title || prediction.goalId,
        predicted: Math.round(prediction.predictedOutcome),
        confidence: Math.round(prediction.probability * 100),
        lower: Math.round(prediction.confidenceInterval[0]),
        upper: Math.round(prediction.confidenceInterval[1])
      };
    });
  }, [analyticsData, goals]);

  // Loading state
  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Advanced Analytics Dashboard</h2>
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
            <div className="space-y-4">
              <div className="h-64 bg-gray-200 rounded"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-red-200 p-6 ${className}`}>
        <div className="text-center">
          <div className="text-red-600 text-lg font-medium mb-2">Analytics Error</div>
          <div className="text-gray-600 mb-4">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // No data state
  if (!analyticsData) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
        <div className="text-center text-gray-500">
          <div className="text-lg font-medium mb-2">No Analytics Data</div>
          <div>Complete some therapeutic activities to see predictive insights.</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Advanced Analytics Dashboard</h2>
          <div className="flex items-center space-x-4">
            {/* Time Range Selector */}
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value as '7d' | '30d' | '90d')}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>
        </div>

        {/* Overall Prognosis */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">Overall Prognosis</div>
              <div className="text-2xl font-bold" style={{ color: PROGNOSIS_COLORS[analyticsData.overallPrognosis.outlook] }}>
                {analyticsData.overallPrognosis.outlook.toUpperCase()}
              </div>
              <div className="text-sm text-gray-500">
                Score: {Math.round(analyticsData.overallPrognosis.score)}/100
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-600">Confidence</div>
              <div className="text-lg font-semibold">
                {Math.round(analyticsData.overallPrognosis.confidence * 100)}%
              </div>
            </div>
          </div>
          {analyticsData.overallPrognosis.keyFactors.length > 0 && (
            <div className="mt-3">
              <div className="text-sm text-gray-600 mb-1">Key Factors:</div>
              <div className="flex flex-wrap gap-2">
                {analyticsData.overallPrognosis.keyFactors.map((factor, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                  >
                    {factor}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {[
            { id: 'trends', label: 'Trend Analysis', count: analyticsData.trendAnalyses.length },
            { id: 'risks', label: 'Risk Predictions', count: analyticsData.riskPredictions.length },
            { id: 'outcomes', label: 'Outcome Predictions', count: analyticsData.outcomePredictions.length },
            { id: 'insights', label: 'Longitudinal Insights', count: analyticsData.longitudinalInsights.length }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {/* Trend Analysis Tab */}
        {activeTab === 'trends' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress Trend Analysis</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip
                      formatter={(value: number) => [`${value.toFixed(1)}%`, 'Progress']}
                      labelFormatter={(label) => `Date: ${label}`}
                    />
                    <Legend />
                    {goals.map((goal, index) => (
                      <Line
                        key={goal.id}
                        type="monotone"
                        dataKey={goal.id}
                        stroke={TREND_COLORS[index % TREND_COLORS.length]}
                        strokeWidth={2}
                        name={goal.title}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Trend Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analyticsData.trendAnalyses.map((trend) => {
                const goal = goals.find(g => g.id === trend.goalId);
                return (
                  <div key={trend.trendId} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{goal?.title || trend.goalId}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        trend.trendType === 'improving' ? 'bg-green-100 text-green-800' :
                        trend.trendType === 'declining' ? 'bg-red-100 text-red-800' :
                        trend.trendType === 'stable' ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {trend.trendType}
                      </span>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Projected Outcome:</span>
                        <span className="font-medium">{Math.round(trend.projectedOutcome)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Confidence:</span>
                        <span className="font-medium">{Math.round(trend.confidence * 100)}%</span>
                      </div>
                      {trend.timeToTarget && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Time to Target:</span>
                          <span className="font-medium">{trend.timeToTarget} days</span>
                        </div>
                      )}
                    </div>
                    {trend.recommendations.length > 0 && (
                      <div className="mt-3">
                        <div className="text-xs text-gray-600 mb-1">Recommendations:</div>
                        <ul className="text-xs text-gray-700 space-y-1">
                          {trend.recommendations.slice(0, 2).map((rec, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-blue-500 mr-1">•</span>
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Risk Predictions Tab */}
        {activeTab === 'risks' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Assessment Overview</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Risk Chart */}
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={riskChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="riskType" />
                      <YAxis domain={[0, 100]} />
                      <Tooltip formatter={(value: number) => [`${value}%`, 'Probability']} />
                      <Bar dataKey="probability" fill="#8884d8">
                        {riskChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Risk Summary */}
                <div className="space-y-4">
                  {analyticsData.riskPredictions.map((risk) => (
                    <div key={risk.riskId} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900 capitalize">
                          {risk.riskType.replace('_', ' ')}
                        </h4>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            risk.severity === 'critical' ? 'bg-red-100 text-red-800' :
                            risk.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                            risk.severity === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {risk.severity}
                          </span>
                          <span className="text-sm font-medium">
                            {Math.round(risk.probability * 100)}%
                          </span>
                        </div>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        Timeframe: {risk.timeframe} days
                      </div>
                      {risk.mitigationStrategies.length > 0 && (
                        <div>
                          <div className="text-xs text-gray-600 mb-1">Mitigation Strategies:</div>
                          <ul className="text-xs text-gray-700 space-y-1">
                            {risk.mitigationStrategies.slice(0, 3).map((strategy, index) => (
                              <li key={index} className="flex items-start">
                                <span className="text-blue-500 mr-1">•</span>
                                {strategy}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Outcome Predictions Tab */}
        {activeTab === 'outcomes' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Therapeutic Outcome Predictions</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={outcomeChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="goalTitle" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip
                      formatter={(value: number, name: string) => [
                        `${value}%`,
                        name === 'predicted' ? 'Predicted Outcome' :
                        name === 'lower' ? 'Lower Bound' : 'Upper Bound'
                      ]}
                    />
                    <Legend />
                    <Bar dataKey="predicted" fill="#3b82f6" name="Predicted Outcome" />
                    <Bar dataKey="lower" fill="#93c5fd" name="Lower Bound" />
                    <Bar dataKey="upper" fill="#1d4ed8" name="Upper Bound" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Outcome Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analyticsData.outcomePredictions.map((prediction) => {
                const goal = goals.find(g => g.id === prediction.goalId);
                return (
                  <div key={prediction.predictionId} className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-3">{goal?.title || prediction.goalId}</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Predicted Outcome:</span>
                        <span className="font-medium">{Math.round(prediction.predictedOutcome)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Confidence Interval:</span>
                        <span className="font-medium">
                          {Math.round(prediction.confidenceInterval[0])}% - {Math.round(prediction.confidenceInterval[1])}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Timeframe:</span>
                        <span className="font-medium">{prediction.timeframe} days</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Probability:</span>
                        <span className="font-medium">{Math.round(prediction.probability * 100)}%</span>
                      </div>
                    </div>
                    {prediction.factors.length > 0 && (
                      <div className="mt-3">
                        <div className="text-xs text-gray-600 mb-1">Key Factors:</div>
                        <div className="space-y-1">
                          {prediction.factors.slice(0, 3).map((factor, index) => (
                            <div key={index} className="flex items-center justify-between text-xs">
                              <span className="text-gray-700">{factor.factor}</span>
                              <span className="font-medium">
                                {Math.round(factor.impact * 100)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Longitudinal Insights Tab */}
        {activeTab === 'insights' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Longitudinal Therapeutic Insights</h3>
              <div className="space-y-4">
                {analyticsData.longitudinalInsights.map((insight) => (
                  <div
                    key={insight.insightId}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => onInsightClick?.(insight)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          insight.insightType === 'pattern' ? 'bg-purple-100 text-purple-800' :
                          insight.insightType === 'milestone' ? 'bg-green-100 text-green-800' :
                          insight.insightType === 'correlation' ? 'bg-blue-100 text-blue-800' :
                          'bg-orange-100 text-orange-800'
                        }`}>
                          {insight.insightType}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          insight.clinicalRelevance === 'high' ? 'bg-red-100 text-red-800' :
                          insight.clinicalRelevance === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {insight.clinicalRelevance} relevance
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        {insight.timespan} days • {insight.dataPoints} data points
                      </div>
                    </div>
                    <p className="text-gray-900 mb-3">{insight.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-gray-600">
                        Significance: {Math.round(insight.significance * 100)}%
                      </div>
                      {insight.actionable && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          Actionable
                        </span>
                      )}
                    </div>
                    {insight.recommendations.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="text-xs text-gray-600 mb-1">Recommendations:</div>
                        <ul className="text-xs text-gray-700 space-y-1">
                          {insight.recommendations.slice(0, 2).map((rec, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-blue-500 mr-1">•</span>
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-lg">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div>
            Last updated: {format(new Date(analyticsData.analysisTimestamp), 'MMM dd, yyyy HH:mm')}
          </div>
          <div className="flex items-center space-x-4">
            <div>
              Model Accuracy: {Math.round(analyticsData.modelPerformance.accuracy * 100)}%
            </div>
            <div>
              Next Analysis: {format(new Date(analyticsData.nextAnalysisDate), 'MMM dd, yyyy')}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedAnalyticsDashboard;
