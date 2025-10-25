/**
 * Progress Analytics Interface - Priority 3D Implementation
 *
 * Comprehensive progress monitoring and analytics interface for therapeutic goals.
 * Provides real-time progress visualization, outcome measurement display, and therapeutic insights.
 *
 * Features:
 * - Interactive progress analytics dashboard
 * - Real-time progress tracking visualization
 * - Outcome measurement display with clinical significance
 * - Therapeutic insights and recommendations
 * - Risk assessment and mitigation guidance
 * - Data quality metrics and validation
 * - Accessibility-compliant interface (WCAG 2.1 AA)
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  ProgressTrackingResult,
  ProgressAnalytics,
  OutcomeMeasurement,
  TherapeuticInsight,
  RiskAssessment,
  ProgressRecommendation,
  NextAction,
  DataQualityMetrics,
  ProgressTrend,
  SeverityLevel,
  ClinicalSignificance,
  InsightType,
  ClinicalRelevance,
  ConfidenceLevel
} from '../../../services/progressTrackingService';

interface ProgressAnalyticsInterfaceProps {
  progressResult: ProgressTrackingResult;
  onRecordProgress: (goalId: string, progressValue: number, notes?: string) => void;
  onRecordOutcome: (measurementType: string, score: number) => void;
  onAcceptRecommendation: (recommendationId: string) => void;
  onDismissRecommendation: (recommendationId: string) => void;
  onScheduleAction: (actionId: string, dueDate: Date) => void;
  onRequestDetailedInsight: (insightId: string) => void;
  className?: string;
}

type ViewMode = 'overview' | 'detailed' | 'insights' | 'recommendations';
type TimeframeFilter = 'week' | 'month' | 'quarter' | 'year';

export const ProgressAnalyticsInterface: React.FC<ProgressAnalyticsInterfaceProps> = ({
  progressResult,
  onRecordProgress,
  onRecordOutcome,
  onAcceptRecommendation,
  onDismissRecommendation,
  onScheduleAction,
  onRequestDetailedInsight,
  className = ''
}) => {
  const [activeView, setActiveView] = useState<ViewMode>('overview');
  const [selectedGoalId, setSelectedGoalId] = useState<string | null>(null);
  const [timeframeFilter, setTimeframeFilter] = useState<TimeframeFilter>('month');
  const [showRiskDetails, setShowRiskDetails] = useState(false);
  const [expandedInsights, setExpandedInsights] = useState<Set<string>>(new Set());

  // Memoized calculations for performance
  const overallProgressScore = useMemo(() => {
    return Math.round(progressResult.overallEffectiveness);
  }, [progressResult.overallEffectiveness]);

  const riskLevel = useMemo(() => {
    return progressResult.riskAssessment.overallRisk;
  }, [progressResult.riskAssessment.overallRisk]);

  const dataQualityScore = useMemo(() => {
    return Math.round(progressResult.dataQuality.overallQuality);
  }, [progressResult.dataQuality.overallQuality]);

  // Event handlers
  const handleViewChange = useCallback((view: ViewMode) => {
    setActiveView(view);
  }, []);

  const handleGoalSelection = useCallback((goalId: string) => {
    setSelectedGoalId(goalId === selectedGoalId ? null : goalId);
  }, [selectedGoalId]);

  const handleInsightExpansion = useCallback((insightId: string) => {
    setExpandedInsights(prev => {
      const newSet = new Set(prev);
      if (newSet.has(insightId)) {
        newSet.delete(insightId);
      } else {
        newSet.add(insightId);
      }
      return newSet;
    });
  }, []);

  const handleRecommendationAction = useCallback((recommendationId: string, action: 'accept' | 'dismiss') => {
    if (action === 'accept') {
      onAcceptRecommendation(recommendationId);
    } else {
      onDismissRecommendation(recommendationId);
    }
  }, [onAcceptRecommendation, onDismissRecommendation]);

  // Helper functions
  const getProgressTrendIcon = (trend: ProgressTrend): string => {
    switch (trend) {
      case ProgressTrend.IMPROVING: return '📈';
      case ProgressTrend.STABLE: return '➡️';
      case ProgressTrend.DECLINING: return '📉';
      case ProgressTrend.FLUCTUATING: return '📊';
      default: return '❓';
    }
  };

  const getRiskLevelColor = (risk: SeverityLevel): string => {
    switch (risk) {
      case SeverityLevel.MINIMAL: return 'text-green-600';
      case SeverityLevel.MILD: return 'text-yellow-600';
      case SeverityLevel.MODERATE: return 'text-orange-600';
      case SeverityLevel.SEVERE: return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getConfidenceBadgeColor = (confidence: ConfidenceLevel): string => {
    switch (confidence) {
      case ConfidenceLevel.VERY_HIGH: return 'bg-green-100 text-green-800';
      case ConfidenceLevel.HIGH: return 'bg-blue-100 text-blue-800';
      case ConfidenceLevel.MEDIUM: return 'bg-yellow-100 text-yellow-800';
      case ConfidenceLevel.LOW: return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getClinicalSignificanceIcon = (significance: ClinicalSignificance): string => {
    switch (significance) {
      case ClinicalSignificance.HIGHLY_SIGNIFICANT: return '🔴';
      case ClinicalSignificance.CLINICALLY_MEANINGFUL: return '🟡';
      case ClinicalSignificance.NOT_SIGNIFICANT: return '🟢';
      case ClinicalSignificance.REQUIRES_ATTENTION: return '⚠️';
      default: return '⚪';
    }
  };

  return (
    <div className={`progress-analytics-interface bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Header with Navigation */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-gray-900">Progress Analytics</h2>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Data Quality:</span>
            <div className={`px-2 py-1 rounded text-sm font-medium ${
              dataQualityScore >= 80 ? 'bg-green-100 text-green-800' :
              dataQualityScore >= 60 ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {dataQualityScore}%
            </div>
          </div>
        </div>

        {/* View Navigation */}
        <nav className="flex space-x-1" role="tablist">
          {[
            { key: 'overview', label: 'Overview', icon: '📊' },
            { key: 'detailed', label: 'Detailed Analysis', icon: '🔍' },
            { key: 'insights', label: 'Therapeutic Insights', icon: '💡' },
            { key: 'recommendations', label: 'Recommendations', icon: '🎯' }
          ].map(({ key, label, icon }) => (
            <button
              key={key}
              id={`${key}-tab`}
              onClick={() => handleViewChange(key as ViewMode)}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                activeView === key
                  ? 'bg-blue-100 text-blue-700 border border-blue-200'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
              role="tab"
              aria-selected={activeView === key}
              aria-controls={`${key}-panel`}
            >
              <span className="mr-2" aria-hidden="true">{icon}</span>
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Panel */}
      {activeView === 'overview' && (
        <div id="overview-panel" role="tabpanel" aria-labelledby="overview-tab" className="p-6">
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Overall Effectiveness */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-600">Overall Effectiveness</p>
                  <p className="text-3xl font-bold text-blue-900">{overallProgressScore}%</p>
                </div>
                <div className="text-4xl">🎯</div>
              </div>
              <p className="text-sm text-blue-700 mt-2">
                {overallProgressScore >= 80 ? 'Excellent progress across goals' :
                 overallProgressScore >= 60 ? 'Good therapeutic progress' :
                 overallProgressScore >= 40 ? 'Moderate progress, room for improvement' :
                 'Consider adjusting therapeutic approach'}
              </p>
            </div>

            {/* Risk Assessment */}
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6 border border-green-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-600">Risk Level</p>
                  <p className={`text-2xl font-bold capitalize ${getRiskLevelColor(riskLevel)}`}>
                    {riskLevel.replace('_', ' ')}
                  </p>
                </div>
                <div className="text-4xl">🛡️</div>
              </div>
              <button
                onClick={() => setShowRiskDetails(!showRiskDetails)}
                className="text-sm text-green-700 hover:text-green-800 mt-2 underline"
              >
                {showRiskDetails ? 'Hide details' : 'View risk factors'}
              </button>
            </div>

            {/* Active Goals */}
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-600">Active Goals</p>
                  <p className="text-3xl font-bold text-purple-900">{progressResult.currentProgress.length}</p>
                </div>
                <div className="text-4xl">🎪</div>
              </div>
              <p className="text-sm text-purple-700 mt-2">
                {progressResult.milestones.filter(m => !m.achievedAt).length} upcoming milestones
              </p>
            </div>
          </div>

          {/* Risk Details (Expandable) */}
          {showRiskDetails && (
            <div className="mb-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h3 className="text-lg font-semibold text-yellow-800 mb-3">Risk Assessment Details</h3>
              <div className="space-y-3">
                {progressResult.riskAssessment.riskFactors.map((risk, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <span className={`inline-block w-2 h-2 rounded-full mt-2 ${
                      risk.severity === SeverityLevel.SEVERE ? 'bg-red-500' :
                      risk.severity === SeverityLevel.MODERATE ? 'bg-orange-500' :
                      'bg-yellow-500'
                    }`}></span>
                    <div>
                      <p className="font-medium text-gray-900">{risk.description}</p>
                      <ul className="text-sm text-gray-600 mt-1 ml-4">
                        {risk.recommendations.map((rec, recIndex) => (
                          <li key={recIndex} className="list-disc">{rec}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Goal Progress Summary */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Goal Progress Summary</h3>
            {progressResult.currentProgress.map((goalAnalytics) => (
              <div
                key={goalAnalytics.goalId}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleGoalSelection(goalAnalytics.goalId)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl" aria-hidden="true">
                      {getProgressTrendIcon(goalAnalytics.progressTrend)}
                    </span>
                    <div>
                      <h4 className="font-medium text-gray-900">Goal {goalAnalytics.goalId}</h4>
                      <p className="text-sm text-gray-600">
                        {goalAnalytics.overallProgress}% complete • {goalAnalytics.progressTrend.replace('_', ' ')} trend
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-gray-900">
                      {Math.round(goalAnalytics.therapeuticEffectiveness)}%
                    </div>
                    <div className="text-sm text-gray-500">effectiveness</div>
                  </div>
                </div>

                {/* Expanded Goal Details */}
                {selectedGoalId === goalAnalytics.goalId && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">Velocity:</span>
                        <span className="ml-2 text-gray-900">{Math.round(goalAnalytics.velocityScore)}</span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Consistency:</span>
                        <span className="ml-2 text-gray-900">{Math.round(goalAnalytics.consistencyScore)}</span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Risk Factors:</span>
                        <span className="ml-2 text-gray-900">{goalAnalytics.riskFactors.length}</span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Recommendations:</span>
                        <span className="ml-2 text-gray-900">{goalAnalytics.recommendations.length}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Analysis Panel */}
      {activeView === 'detailed' && (
        <div id="detailed-panel" role="tabpanel" aria-labelledby="detailed-tab" className="p-6">
          <div className="space-y-8">
            {/* Outcome Measurements */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Clinical Outcome Measurements</h3>
              {progressResult.outcomeMeasurements.length > 0 ? (
                <div className="space-y-3">
                  {progressResult.outcomeMeasurements.map((measurement) => (
                    <div key={measurement.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <span className="text-xl" aria-hidden="true">
                          {getClinicalSignificanceIcon(measurement.clinicalSignificance)}
                        </span>
                        <div>
                          <p className="font-medium text-gray-900">{measurement.measurementType.toUpperCase()}</p>
                          <p className="text-sm text-gray-600">
                            {measurement.score}/{measurement.maxScore} • {measurement.severity?.replace('_', ' ')}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-500">
                          {measurement.timestamp.toLocaleDateString()}
                        </div>
                        <div className={`text-sm font-medium ${
                          measurement.trendDirection === 'improving' ? 'text-green-600' :
                          measurement.trendDirection === 'worsening' ? 'text-red-600' :
                          'text-gray-600'
                        }`}>
                          {measurement.trendDirection}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No outcome measurements recorded yet.</p>
                  <button
                    onClick={() => onRecordOutcome('PHQ9', 0)}
                    className="mt-2 text-blue-600 hover:text-blue-700 underline"
                  >
                    Record your first measurement
                  </button>
                </div>
              )}
            </div>

            {/* Data Quality Breakdown */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Quality Metrics</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(progressResult.dataQuality).map(([metric, value]) => (
                  <div key={metric} className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{Math.round(value)}%</div>
                    <div className="text-sm text-gray-600 capitalize">{metric.replace(/([A-Z])/g, ' $1').trim()}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Progress Entries */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Progress Entries</h3>
              {progressResult.recentEntries.length > 0 ? (
                <div className="space-y-2">
                  {progressResult.recentEntries.slice(0, 10).map((entry) => (
                    <div key={entry.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <div>
                        <span className="font-medium text-gray-900">Goal {entry.goalId}</span>
                        <span className="mx-2 text-gray-400">•</span>
                        <span className="text-gray-600">{entry.progressValue}%</span>
                        {entry.notes && (
                          <>
                            <span className="mx-2 text-gray-400">•</span>
                            <span className="text-sm text-gray-500">{entry.notes}</span>
                          </>
                        )}
                      </div>
                      <div className="text-sm text-gray-500">
                        {entry.timestamp.toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No progress entries recorded yet.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Therapeutic Insights Panel */}
      {activeView === 'insights' && (
        <div id="insights-panel" role="tabpanel" aria-labelledby="insights-tab" className="p-6">
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Therapeutic Insights</h3>

            {progressResult.therapeuticInsights.length > 0 ? (
              <div className="space-y-4">
                {progressResult.therapeuticInsights.map((insight) => (
                  <div key={insight.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-medium text-gray-900">{insight.title}</h4>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${getConfidenceBadgeColor(insight.confidence)}`}>
                            {insight.confidence} confidence
                          </span>
                        </div>
                        <p className="text-gray-700 mb-3">{insight.description}</p>

                        {expandedInsights.has(insight.id) && (
                          <div className="space-y-3">
                            <div>
                              <p className="text-sm font-medium text-gray-700 mb-1">Clinical Relevance:</p>
                              <span className={`px-2 py-1 text-xs font-medium rounded ${
                                insight.clinicalRelevance === ClinicalRelevance.CRITICAL ? 'bg-red-100 text-red-800' :
                                insight.clinicalRelevance === ClinicalRelevance.HIGH ? 'bg-orange-100 text-orange-800' :
                                insight.clinicalRelevance === ClinicalRelevance.MODERATE ? 'bg-yellow-100 text-yellow-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {insight.clinicalRelevance}
                              </span>
                            </div>

                            {insight.actionable && insight.recommendations.length > 0 && (
                              <div>
                                <p className="text-sm font-medium text-gray-700 mb-2">Recommendations:</p>
                                <ul className="text-sm text-gray-600 space-y-1">
                                  {insight.recommendations.map((rec, index) => (
                                    <li key={index} className="flex items-start">
                                      <span className="text-blue-500 mr-2">•</span>
                                      {rec}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleInsightExpansion(insight.id)}
                          className="text-blue-600 hover:text-blue-700 text-sm underline"
                        >
                          {expandedInsights.has(insight.id) ? 'Less' : 'More'}
                        </button>
                        {insight.actionable && (
                          <button
                            onClick={() => onRequestDetailedInsight(insight.id)}
                            className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                          >
                            Act on This
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <div className="text-4xl mb-4">🔍</div>
                <p className="text-lg mb-2">No insights available yet</p>
                <p className="text-sm">Continue tracking your progress to generate therapeutic insights.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recommendations Panel */}
      {activeView === 'recommendations' && (
        <div id="recommendations-panel" role="tabpanel" aria-labelledby="recommendations-tab" className="p-6">
          <div className="space-y-8">
            {/* Progress Recommendations */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress Recommendations</h3>
              {progressResult.recommendations.length > 0 ? (
                <div className="space-y-3">
                  {progressResult.recommendations.map((recommendation) => (
                    <div key={recommendation.id} className="flex items-start justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-medium text-gray-900">{recommendation.title}</h4>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            recommendation.priority === 'high' ? 'bg-red-100 text-red-800' :
                            recommendation.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {recommendation.priority} priority
                          </span>
                        </div>
                        <p className="text-gray-700">{recommendation.description}</p>
                      </div>

                      {recommendation.actionable && (
                        <div className="flex items-center space-x-2 ml-4">
                          <button
                            onClick={() => handleRecommendationAction(recommendation.id, 'accept')}
                            className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
                          >
                            Accept
                          </button>
                          <button
                            onClick={() => handleRecommendationAction(recommendation.id, 'dismiss')}
                            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                          >
                            Dismiss
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No recommendations available at this time.</p>
                </div>
              )}
            </div>

            {/* Next Actions */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Suggested Next Actions</h3>
              {progressResult.nextActions.length > 0 ? (
                <div className="space-y-3">
                  {progressResult.nextActions.map((action) => (
                    <div key={action.id} className="flex items-start justify-between p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-medium text-blue-900">{action.title}</h4>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            action.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                            action.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                            action.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {action.priority}
                          </span>
                        </div>
                        <p className="text-blue-800">{action.description}</p>
                        {action.dueDate && (
                          <p className="text-sm text-blue-600 mt-1">
                            Due: {action.dueDate.toLocaleDateString()}
                          </p>
                        )}
                      </div>

                      <button
                        onClick={() => onScheduleAction(action.id, action.dueDate || new Date())}
                        className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors ml-4"
                      >
                        Schedule
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No immediate actions required.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Footer with Last Updated */}
      <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>Last updated: {progressResult.generatedAt.toLocaleString()}</span>
          <span>Showing {timeframeFilter} view</span>
        </div>
      </div>
    </div>
  );
};

export default ProgressAnalyticsInterface;
