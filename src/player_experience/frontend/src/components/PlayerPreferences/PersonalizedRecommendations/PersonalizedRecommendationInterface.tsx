/**
 * Personalized Recommendation Interface Component
 * 
 * Displays intelligent, contextual recommendations for therapeutic goals,
 * concerns, and approaches with user-friendly interaction and feedback capabilities.
 */

import React, { useState, useEffect } from 'react';
import {
  ContextualRecommendation,
  RecommendationResult,
  RecommendationType,
  RecommendationPriority,
  RecommendationTimeframe
} from '../../../services/personalizedRecommendationEngine';

interface PersonalizedRecommendationInterfaceProps {
  recommendationResult: RecommendationResult;
  onAcceptRecommendation: (recommendationId: string) => void;
  onDismissRecommendation: (recommendationId: string) => void;
  onProvideFeedback: (recommendationId: string, rating: number, comments?: string) => void;
  onRequestMoreInfo: (recommendationId: string) => void;
  className?: string;
  maxDisplayRecommendations?: number;
}

const PersonalizedRecommendationInterface: React.FC<PersonalizedRecommendationInterfaceProps> = ({
  recommendationResult,
  onAcceptRecommendation,
  onDismissRecommendation,
  onProvideFeedback,
  onRequestMoreInfo,
  className = '',
  maxDisplayRecommendations = 6
}) => {
  const [expandedRecommendations, setExpandedRecommendations] = useState<Set<string>>(new Set());
  const [feedbackMode, setFeedbackMode] = useState<string | null>(null);
  const [feedbackRating, setFeedbackRating] = useState<number>(3);
  const [feedbackComments, setFeedbackComments] = useState<string>('');
  const [filterPriority, setFilterPriority] = useState<RecommendationPriority | 'all'>('all');
  const [filterTimeframe, setFilterTimeframe] = useState<RecommendationTimeframe | 'all'>('all');

  const { recommendations, recommendationSummary, personalizationScore, confidenceLevel } = recommendationResult;

  // Filter recommendations based on selected filters
  const filteredRecommendations = recommendations.filter(rec => {
    if (filterPriority !== 'all' && rec.priority !== filterPriority) return false;
    if (filterTimeframe !== 'all' && rec.timeframe !== filterTimeframe) return false;
    return true;
  }).slice(0, maxDisplayRecommendations);

  const toggleExpanded = (recommendationId: string) => {
    const newExpanded = new Set(expandedRecommendations);
    if (newExpanded.has(recommendationId)) {
      newExpanded.delete(recommendationId);
    } else {
      newExpanded.add(recommendationId);
    }
    setExpandedRecommendations(newExpanded);
  };

  const handleFeedbackSubmit = (recommendationId: string) => {
    onProvideFeedback(recommendationId, feedbackRating, feedbackComments);
    setFeedbackMode(null);
    setFeedbackRating(3);
    setFeedbackComments('');
  };

  const getPriorityIcon = (priority: RecommendationPriority): string => {
    switch (priority) {
      case 'critical': return '🚨';
      case 'high': return '⚡';
      case 'medium': return '💡';
      case 'low': return '💭';
      case 'optional': return '✨';
      default: return '💡';
    }
  };

  const getPriorityColor = (priority: RecommendationPriority): string => {
    switch (priority) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'low': return 'text-gray-600 bg-gray-50 border-gray-200';
      case 'optional': return 'text-purple-600 bg-purple-50 border-purple-200';
      default: return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getTypeIcon = (type: RecommendationType): string => {
    switch (type) {
      case 'goal_suggestion': return '🎯';
      case 'approach_optimization': return '🔄';
      case 'progress_enhancement': return '📈';
      case 'integration_support': return '🔗';
      case 'skill_building': return '🛠️';
      case 'milestone_adjustment': return '🏁';
      default: return '💡';
    }
  };

  const getConfidenceBadge = (confidence: number): string => {
    if (confidence >= 0.8) return 'High Confidence';
    if (confidence >= 0.6) return 'Medium Confidence';
    return 'Lower Confidence';
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800';
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  if (recommendations.length === 0) {
    return (
      <div className={`bg-blue-50 border border-blue-200 rounded-lg p-6 ${className}`}>
        <div className="text-center">
          <div className="text-4xl mb-3">🌟</div>
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            You're doing great!
          </h3>
          <p className="text-blue-700">
            No specific recommendations at this time. Continue with your current therapeutic journey.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">🤖</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Personalized Recommendations
              </h3>
              <p className="text-sm text-gray-600">
                AI-powered suggestions tailored to your therapeutic journey
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              confidenceLevel === 'high' ? 'bg-green-100 text-green-800' :
              confidenceLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {confidenceLevel.charAt(0).toUpperCase() + confidenceLevel.slice(1)} Confidence
            </span>
            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
              {Math.round(personalizationScore * 100)}% Personalized
            </span>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center space-x-2">
            <label htmlFor="priority-filter" className="text-sm font-medium text-gray-700">
              Priority:
            </label>
            <select
              id="priority-filter"
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value as RecommendationPriority | 'all')}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
              <option value="optional">Optional</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <label htmlFor="timeframe-filter" className="text-sm font-medium text-gray-700">
              Timeframe:
            </label>
            <select
              id="timeframe-filter"
              value={filterTimeframe}
              onChange={(e) => setFilterTimeframe(e.target.value as RecommendationTimeframe | 'all')}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All</option>
              <option value="immediate">Immediate</option>
              <option value="this_week">This Week</option>
              <option value="this_month">This Month</option>
              <option value="next_quarter">Next Quarter</option>
              <option value="long_term">Long Term</option>
            </select>
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="divide-y divide-gray-200">
        {filteredRecommendations.map((recommendation) => (
          <div key={recommendation.id} className="p-6">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start space-x-3 flex-1">
                <div className="text-2xl">{getTypeIcon(recommendation.type)}</div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-semibold text-gray-900">{recommendation.title}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(recommendation.priority)}`}>
                      {getPriorityIcon(recommendation.priority)} {recommendation.priority}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(recommendation.confidence)}`}>
                      {getConfidenceBadge(recommendation.confidence)}
                    </span>
                  </div>
                  <p className="text-gray-700 mb-2">{recommendation.description}</p>
                  
                  {/* Timeframe and Expected Outcome */}
                  <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                    <span>⏱️ {recommendation.timeframe.replace('_', ' ')}</span>
                    <span>🎯 {recommendation.expectedOutcome}</span>
                  </div>

                  {/* Expanded Details */}
                  {expandedRecommendations.has(recommendation.id) && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h6 className="font-medium text-gray-900 mb-2">Personalization Factors</h6>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {recommendation.personalizationFactors.map((factor, index) => (
                              <li key={index} className="flex items-center space-x-2">
                                <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                                <span>{factor.description}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h6 className="font-medium text-gray-900 mb-2">Clinical Evidence</h6>
                          <p className="text-sm text-gray-600 mb-2">
                            Evidence Level: <span className="font-medium">{recommendation.clinicalEvidence}</span>
                          </p>
                          <p className="text-sm text-gray-600">
                            Adaptation Reason: {recommendation.adaptationReason}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => toggleExpanded(recommendation.id)}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  {expandedRecommendations.has(recommendation.id) ? 'Show Less' : 'Show Details'}
                </button>
                <button
                  onClick={() => onRequestMoreInfo(recommendation.id)}
                  className="text-sm text-gray-600 hover:text-gray-800"
                >
                  More Info
                </button>
              </div>
              
              <div className="flex items-center space-x-2">
                {feedbackMode === recommendation.id ? (
                  <div className="flex items-center space-x-2">
                    <select
                      value={feedbackRating}
                      onChange={(e) => setFeedbackRating(Number(e.target.value))}
                      className="text-sm border border-gray-300 rounded px-2 py-1"
                    >
                      <option value={1}>1 - Not helpful</option>
                      <option value={2}>2 - Somewhat helpful</option>
                      <option value={3}>3 - Moderately helpful</option>
                      <option value={4}>4 - Very helpful</option>
                      <option value={5}>5 - Extremely helpful</option>
                    </select>
                    <button
                      onClick={() => handleFeedbackSubmit(recommendation.id)}
                      className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                    >
                      Submit
                    </button>
                    <button
                      onClick={() => setFeedbackMode(null)}
                      className="px-3 py-1 bg-gray-300 text-gray-700 text-sm rounded hover:bg-gray-400"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => onDismissRecommendation(recommendation.id)}
                      className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded hover:bg-gray-200"
                    >
                      Dismiss
                    </button>
                    <button
                      onClick={() => setFeedbackMode(recommendation.id)}
                      className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded hover:bg-yellow-200"
                    >
                      Feedback
                    </button>
                    <button
                      onClick={() => onAcceptRecommendation(recommendation.id)}
                      className="px-4 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 font-medium"
                    >
                      Accept
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Footer */}
      <div className="p-4 bg-gray-50 border-t border-gray-200 rounded-b-lg">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            Showing {filteredRecommendations.length} of {recommendations.length} recommendations
          </span>
          <span>
            Next review: {recommendationResult.nextReviewDate.toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default PersonalizedRecommendationInterface;
