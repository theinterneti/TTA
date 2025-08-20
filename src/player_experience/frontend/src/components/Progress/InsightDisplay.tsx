import React, { useState } from 'react';
import { 
  LightBulbIcon, 
  TrendingUpIcon, 
  TrendingDownIcon, 
  ArrowRightIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/react/24/outline';

interface Recommendation {
  recommendation_id: string;
  title: string;
  description: string;
  recommendation_type: string;
  priority: number;
}

interface ProgressSummary {
  player_id: string;
  therapeutic_momentum: number;
  readiness_for_advancement: number;
  progress_trend: string;
  engagement_trend: string;
  challenge_areas: string[];
  strength_areas: string[];
  next_recommended_goals: string[];
  suggested_therapeutic_adjustments: string[];
  favorite_therapeutic_approach?: string;
  last_updated: string;
}

interface InsightDisplayProps {
  progressSummary: ProgressSummary;
  recommendations: Recommendation[];
  className?: string;
  expandable?: boolean;
}

const InsightDisplay: React.FC<InsightDisplayProps> = ({
  progressSummary,
  recommendations,
  className = '',
  expandable = true,
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['insights']));

  const toggleSection = (section: string) => {
    if (!expandable) return;
    
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
      case 'increasing':
        return <TrendingUpIcon className="h-5 w-5 text-green-500" />;
      case 'declining':
      case 'decreasing':
        return <TrendingDownIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ArrowRightIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving':
      case 'increasing':
        return 'text-green-700 bg-green-100';
      case 'declining':
      case 'decreasing':
        return 'text-red-700 bg-red-100';
      default:
        return 'text-gray-700 bg-gray-100';
    }
  };

  const getMomentumColor = (momentum: number) => {
    if (momentum >= 0.8) return 'text-green-700 bg-green-100';
    if (momentum >= 0.6) return 'text-blue-700 bg-blue-100';
    if (momentum >= 0.4) return 'text-yellow-700 bg-yellow-100';
    return 'text-red-700 bg-red-100';
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1:
        return 'bg-red-100 text-red-800 border-red-200';
      case 2:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 3:
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityLabel = (priority: number) => {
    switch (priority) {
      case 1:
        return 'High Priority';
      case 2:
        return 'Medium Priority';
      case 3:
        return 'Low Priority';
      default:
        return 'Normal';
    }
  };

  const SectionHeader: React.FC<{ title: string; sectionKey: string; icon: React.ReactNode }> = ({
    title,
    sectionKey,
    icon,
  }) => (
    <button
      onClick={() => toggleSection(sectionKey)}
      className={`w-full flex items-center justify-between p-3 text-left hover:bg-gray-50 transition-colors ${
        expandable ? 'cursor-pointer' : 'cursor-default'
      }`}
      disabled={!expandable}
    >
      <div className="flex items-center space-x-2">
        {icon}
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      {expandable && (
        expandedSections.has(sectionKey) ? (
          <ChevronUpIcon className="h-5 w-5 text-gray-500" />
        ) : (
          <ChevronDownIcon className="h-5 w-5 text-gray-500" />
        )
      )}
    </button>
  );

  return (
    <div className={`bg-white rounded-lg shadow-sm border ${className}`}>
      {/* Progress Insights Section */}
      <div className="border-b border-gray-200">
        <SectionHeader
          title="Progress Insights"
          sectionKey="insights"
          icon={<LightBulbIcon className="h-6 w-6 text-yellow-500" />}
        />
        
        {expandedSections.has('insights') && (
          <div className="p-4 space-y-4">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-sm text-gray-600 mb-1">Therapeutic Momentum</div>
                <div className={`text-lg font-semibold px-2 py-1 rounded ${getMomentumColor(progressSummary.therapeutic_momentum)}`}>
                  {(progressSummary.therapeutic_momentum * 100).toFixed(0)}%
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-sm text-gray-600 mb-1">Progress Trend</div>
                <div className={`flex items-center px-2 py-1 rounded ${getTrendColor(progressSummary.progress_trend)}`}>
                  {getTrendIcon(progressSummary.progress_trend)}
                  <span className="ml-2 font-medium capitalize">{progressSummary.progress_trend}</span>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-sm text-gray-600 mb-1">Readiness for Advancement</div>
                <div className={`text-lg font-semibold px-2 py-1 rounded ${getMomentumColor(progressSummary.readiness_for_advancement)}`}>
                  {(progressSummary.readiness_for_advancement * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Strengths and Challenges */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {progressSummary.strength_areas.length > 0 && (
                <div>
                  <h4 className="font-medium text-green-800 mb-2">💪 Strength Areas</h4>
                  <div className="space-y-1">
                    {progressSummary.strength_areas.map((area, index) => (
                      <div key={index} className="text-sm bg-green-50 text-green-700 px-2 py-1 rounded">
                        {area}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {progressSummary.challenge_areas.length > 0 && (
                <div>
                  <h4 className="font-medium text-orange-800 mb-2">🎯 Growth Areas</h4>
                  <div className="space-y-1">
                    {progressSummary.challenge_areas.map((area, index) => (
                      <div key={index} className="text-sm bg-orange-50 text-orange-700 px-2 py-1 rounded">
                        {area}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Favorite Therapeutic Approach */}
            {progressSummary.favorite_therapeutic_approach && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                <h4 className="font-medium text-purple-800 mb-1">🌟 Your Preferred Approach</h4>
                <p className="text-purple-700 text-sm">
                  {progressSummary.favorite_therapeutic_approach.replace('_', ' ')}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Recommendations Section */}
      <div className="border-b border-gray-200">
        <SectionHeader
          title="Personalized Recommendations"
          sectionKey="recommendations"
          icon={<ArrowRightIcon className="h-6 w-6 text-blue-500" />}
        />
        
        {expandedSections.has('recommendations') && (
          <div className="p-4">
            {recommendations.length > 0 ? (
              <div className="space-y-3">
                {recommendations.map((rec) => (
                  <div
                    key={rec.recommendation_id}
                    className={`border rounded-lg p-3 ${getPriorityColor(rec.priority)}`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium">{rec.title}</h4>
                      <span className="text-xs px-2 py-1 bg-white bg-opacity-50 rounded">
                        {getPriorityLabel(rec.priority)}
                      </span>
                    </div>
                    <p className="text-sm mb-2">{rec.description}</p>
                    <div className="text-xs opacity-75 capitalize">
                      {rec.recommendation_type.replace('_', ' ')}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-4">
                <LightBulbIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No specific recommendations at this time. Keep up the great work!</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Next Goals Section */}
      {progressSummary.next_recommended_goals.length > 0 && (
        <div>
          <SectionHeader
            title="Suggested Next Steps"
            sectionKey="goals"
            icon={<ArrowRightIcon className="h-6 w-6 text-green-500" />}
          />
          
          {expandedSections.has('goals') && (
            <div className="p-4">
              <div className="space-y-2">
                {progressSummary.next_recommended_goals.map((goal, index) => (
                  <div key={index} className="flex items-center space-x-3 p-2 bg-green-50 rounded">
                    <div className="w-6 h-6 bg-green-200 text-green-800 rounded-full flex items-center justify-center text-sm font-medium">
                      {index + 1}
                    </div>
                    <span className="text-green-800 text-sm">{goal}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Last Updated */}
      <div className="px-4 py-2 bg-gray-50 text-xs text-gray-500 rounded-b-lg">
        Last updated: {new Date(progressSummary.last_updated).toLocaleString()}
      </div>
    </div>
  );
};

export default InsightDisplay;