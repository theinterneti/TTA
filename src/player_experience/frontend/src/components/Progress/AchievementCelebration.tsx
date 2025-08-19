import React, { useState, useEffect } from 'react';
import { XMarkIcon, SparklesIcon, TrophyIcon, FireIcon } from '@heroicons/react/24/outline';

interface ProgressHighlight {
  highlight_id: string;
  title: string;
  description: string;
  highlight_type: string;
  achieved_at: string;
  related_character_id?: string;
  related_world_id?: string;
  therapeutic_value: number;
  celebration_shown: boolean;
}

interface CelebrationData {
  milestone_id: string;
  title: string;
  description: string;
  celebration_message: string;
  reward_unlocked: string;
  therapeutic_value: number;
  suggested_next_milestone?: string;
  celebration_type: string;
  timestamp: string;
}

interface AchievementCelebrationProps {
  highlights: ProgressHighlight[];
  celebrationData?: CelebrationData;
  onDismiss: (highlightId: string) => void;
  onCelebrationComplete?: (celebrationId: string) => void;
  className?: string;
}

const AchievementCelebration: React.FC<AchievementCelebrationProps> = ({
  highlights,
  celebrationData,
  onDismiss,
  onCelebrationComplete,
  className = '',
}) => {
  const [visibleHighlights, setVisibleHighlights] = useState<ProgressHighlight[]>([]);
  const [showCelebration, setShowCelebration] = useState(false);

  useEffect(() => {
    // Show new highlights that haven't been celebrated yet
    const newHighlights = highlights.filter(h => !h.celebration_shown);
    setVisibleHighlights(newHighlights);
  }, [highlights]);

  useEffect(() => {
    if (celebrationData) {
      setShowCelebration(true);
      // Auto-dismiss celebration after 5 seconds
      const timer = setTimeout(() => {
        handleCelebrationDismiss();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [celebrationData]);

  const handleCelebrationDismiss = () => {
    setShowCelebration(false);
    if (celebrationData && onCelebrationComplete) {
      onCelebrationComplete(celebrationData.milestone_id);
    }
  };

  const getHighlightIcon = (type: string) => {
    switch (type) {
      case 'breakthrough':
        return <SparklesIcon className="h-6 w-6 text-yellow-500" />;
      case 'milestone':
        return <TrophyIcon className="h-6 w-6 text-purple-500" />;
      case 'skill_development':
        return <FireIcon className="h-6 w-6 text-orange-500" />;
      default:
        return <SparklesIcon className="h-6 w-6 text-blue-500" />;
    }
  };

  const getCelebrationIcon = (type: string) => {
    switch (type) {
      case 'major_achievement':
        return '🏆';
      case 'skill_mastery':
        return '🎯';
      case 'progress_milestone':
        return '⭐';
      default:
        return '🎉';
    }
  };

  const getTherapeuticValueColor = (value: number) => {
    if (value >= 0.8) return 'text-green-600 bg-green-100';
    if (value >= 0.6) return 'text-blue-600 bg-blue-100';
    if (value >= 0.4) return 'text-yellow-600 bg-yellow-100';
    return 'text-gray-600 bg-gray-100';
  };

  return (
    <div className={className}>
      {/* Major Celebration Modal */}
      {showCelebration && celebrationData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-6 text-white text-center">
              <div className="text-4xl mb-2">
                {getCelebrationIcon(celebrationData.celebration_type)}
              </div>
              <h2 className="text-xl font-bold mb-2">Congratulations!</h2>
              <p className="text-purple-100">{celebrationData.title}</p>
            </div>
            
            <div className="p-6">
              <div className="text-center mb-4">
                <p className="text-gray-700 mb-3">{celebrationData.celebration_message}</p>
                
                {celebrationData.reward_unlocked && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
                    <div className="flex items-center justify-center text-yellow-800">
                      <TrophyIcon className="h-5 w-5 mr-2" />
                      <span className="font-medium">Reward Unlocked!</span>
                    </div>
                    <p className="text-yellow-700 text-sm mt-1">
                      {celebrationData.reward_unlocked}
                    </p>
                  </div>
                )}
                
                <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center">
                    <SparklesIcon className="h-4 w-4 mr-1" />
                    <span>Therapeutic Value: {(celebrationData.therapeutic_value * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
              
              {celebrationData.suggested_next_milestone && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                  <h4 className="font-medium text-blue-900 mb-1">Next Challenge:</h4>
                  <p className="text-blue-700 text-sm">{celebrationData.suggested_next_milestone}</p>
                </div>
              )}
              
              <div className="flex justify-center">
                <button
                  onClick={handleCelebrationDismiss}
                  className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Continue Journey
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Achievement Highlights */}
      {visibleHighlights.length > 0 && (
        <div className="space-y-3">
          {visibleHighlights.map((highlight) => (
            <div
              key={highlight.highlight_id}
              className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 shadow-sm animate-pulse"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getHighlightIcon(highlight.highlight_type)}
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      {highlight.title}
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {highlight.description}
                    </p>
                    
                    <div className="flex items-center space-x-3 text-xs">
                      <span className="text-gray-500">
                        {new Date(highlight.achieved_at).toLocaleDateString()}
                      </span>
                      <span
                        className={`px-2 py-1 rounded-full ${getTherapeuticValueColor(
                          highlight.therapeutic_value
                        )}`}
                      >
                        {(highlight.therapeutic_value * 100).toFixed(0)}% therapeutic value
                      </span>
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full capitalize">
                        {highlight.highlight_type.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={() => onDismiss(highlight.highlight_id)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="Dismiss achievement"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AchievementCelebration;