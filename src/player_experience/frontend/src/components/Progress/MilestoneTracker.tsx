import React from 'react';
import { CheckCircleIcon, ClockIcon, StarIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/react/24/solid';

interface Milestone {
  milestone_id: string;
  title: string;
  description: string;
  target_date?: string;
  achieved_date?: string;
  progress_percentage: number;
  required_actions: string[];
  completed_actions: string[];
  therapeutic_approaches_involved: string[];
  reward_description: string;
  is_achieved: boolean;
}

interface MilestoneTrackerProps {
  milestones: Milestone[];
  activeMilestones: Milestone[];
  className?: string;
  showAll?: boolean;
  maxDisplay?: number;
}

const MilestoneTracker: React.FC<MilestoneTrackerProps> = ({
  milestones,
  activeMilestones,
  className = '',
  showAll = false,
  maxDisplay = 5,
}) => {
  const allMilestones = [...milestones, ...activeMilestones].sort((a, b) => {
    // Sort by achievement status, then by progress percentage
    if (a.is_achieved !== b.is_achieved) {
      return a.is_achieved ? -1 : 1;
    }
    return b.progress_percentage - a.progress_percentage;
  });

  const displayMilestones = showAll ? allMilestones : allMilestones.slice(0, maxDisplay);

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getProgressColor = (percentage: number, isAchieved: boolean) => {
    if (isAchieved) return 'bg-green-500';
    if (percentage >= 75) return 'bg-blue-500';
    if (percentage >= 50) return 'bg-yellow-500';
    if (percentage >= 25) return 'bg-orange-500';
    return 'bg-gray-300';
  };

  const getStatusIcon = (milestone: Milestone) => {
    if (milestone.is_achieved) {
      return <CheckCircleIconSolid className="h-6 w-6 text-green-500" />;
    }
    if (milestone.progress_percentage > 0) {
      return <ClockIcon className="h-6 w-6 text-blue-500" />;
    }
    return <CheckCircleIcon className="h-6 w-6 text-gray-400" />;
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Milestones</h3>
        <div className="flex items-center text-sm text-gray-500">
          <StarIcon className="h-4 w-4 mr-1" />
          {milestones.length} achieved
        </div>
      </div>

      <div className="space-y-4">
        {displayMilestones.map((milestone) => (
          <div
            key={milestone.milestone_id}
            className={`border rounded-lg p-4 transition-all duration-200 hover:shadow-md ${
              milestone.is_achieved
                ? 'border-green-200 bg-green-50'
                : milestone.progress_percentage > 0
                ? 'border-blue-200 bg-blue-50'
                : 'border-gray-200 bg-gray-50'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                {getStatusIcon(milestone)}
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {milestone.title}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {milestone.description}
                  </p>

                  {milestone.reward_description && (
                    <div className="mt-2 text-xs text-purple-600 bg-purple-100 rounded px-2 py-1 inline-block">
                      🎁 {milestone.reward_description}
                    </div>
                  )}
                </div>
              </div>

              <div className="text-right ml-4">
                <div className="text-sm font-medium text-gray-900">
                  {milestone.progress_percentage.toFixed(0)}%
                </div>
                {milestone.achieved_date && (
                  <div className="text-xs text-gray-500">
                    {formatDate(milestone.achieved_date)}
                  </div>
                )}
                {!milestone.is_achieved && milestone.target_date && (
                  <div className="text-xs text-gray-500">
                    Due: {formatDate(milestone.target_date)}
                  </div>
                )}
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Progress</span>
                <span>
                  {milestone.completed_actions.length} / {milestone.required_actions.length} actions
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(
                    milestone.progress_percentage,
                    milestone.is_achieved
                  )}`}
                  style={{ width: `${milestone.progress_percentage}%` }}
                />
              </div>
            </div>

            {/* Actions list (for active milestones) */}
            {!milestone.is_achieved && milestone.required_actions.length > 0 && (
              <div className="mt-3">
                <div className="text-xs font-medium text-gray-700 mb-2">Required Actions:</div>
                <div className="space-y-1">
                  {milestone.required_actions.slice(0, 3).map((action, index) => (
                    <div key={index} className="flex items-center text-xs">
                      <div
                        className={`w-3 h-3 rounded-full mr-2 flex-shrink-0 ${
                          milestone.completed_actions.includes(action)
                            ? 'bg-green-500'
                            : 'bg-gray-300'
                        }`}
                      />
                      <span
                        className={
                          milestone.completed_actions.includes(action)
                            ? 'text-gray-500 line-through'
                            : 'text-gray-700'
                        }
                      >
                        {action}
                      </span>
                    </div>
                  ))}
                  {milestone.required_actions.length > 3 && (
                    <div className="text-xs text-gray-500 ml-5">
                      +{milestone.required_actions.length - 3} more actions
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Therapeutic approaches */}
            {milestone.therapeutic_approaches_involved.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1">
                {milestone.therapeutic_approaches_involved.map((approach, index) => (
                  <span
                    key={index}
                    className="inline-block px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded-full"
                  >
                    {approach.replace('_', ' ')}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {!showAll && allMilestones.length > maxDisplay && (
        <div className="mt-4 text-center">
          <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
            View all {allMilestones.length} milestones
          </button>
        </div>
      )}
    </div>
  );
};

export default MilestoneTracker;
