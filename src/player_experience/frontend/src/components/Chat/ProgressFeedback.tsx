import React, { useState, useEffect } from 'react';

interface ProgressFeedbackProps {
  type: 'milestone' | 'achievement' | 'progress' | 'encouragement';
  title: string;
  description: string;
  progress?: {
    current: number;
    total: number;
    unit?: string;
  };
  milestone?: {
    name: string;
    icon?: string;
    level?: number;
  };
  showAnimation?: boolean;
  onDismiss?: () => void;
}

const ProgressFeedback: React.FC<ProgressFeedbackProps> = ({
  type,
  title,
  description,
  progress,
  milestone,
  showAnimation = true,
  onDismiss,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);

  useEffect(() => {
    // Trigger entrance animation
    const timer = setTimeout(() => setIsVisible(true), 100);
    
    // Trigger celebration animation for milestones and achievements
    if ((type === 'milestone' || type === 'achievement') && showAnimation) {
      const celebrationTimer = setTimeout(() => setShowCelebration(true), 500);
      return () => {
        clearTimeout(timer);
        clearTimeout(celebrationTimer);
      };
    }

    return () => clearTimeout(timer);
  }, [type, showAnimation]);

  const getTypeStyles = () => {
    switch (type) {
      case 'milestone':
        return {
          container: 'bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200',
          icon: 'text-purple-600',
          title: 'text-purple-900',
          description: 'text-purple-800',
          accent: 'bg-purple-500',
        };
      case 'achievement':
        return {
          container: 'bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200',
          icon: 'text-yellow-600',
          title: 'text-yellow-900',
          description: 'text-yellow-800',
          accent: 'bg-yellow-500',
        };
      case 'progress':
        return {
          container: 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200',
          icon: 'text-blue-600',
          title: 'text-blue-900',
          description: 'text-blue-800',
          accent: 'bg-blue-500',
        };
      case 'encouragement':
        return {
          container: 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200',
          icon: 'text-green-600',
          title: 'text-green-900',
          description: 'text-green-800',
          accent: 'bg-green-500',
        };
      default:
        return {
          container: 'bg-gray-50 border-gray-200',
          icon: 'text-gray-600',
          title: 'text-gray-900',
          description: 'text-gray-800',
          accent: 'bg-gray-500',
        };
    }
  };

  const getTypeIcon = () => {
    switch (type) {
      case 'milestone':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
        );
      case 'achievement':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
        );
      case 'progress':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        );
      case 'encouragement':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        );
      default:
        return null;
    }
  };

  const styles = getTypeStyles();

  return (
    <div className={`relative overflow-hidden rounded-lg border p-4 my-3 transition-all duration-500 transform ${
      isVisible ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
    } ${styles.container}`}>
      
      {/* Celebration particles for milestones and achievements */}
      {showCelebration && (type === 'milestone' || type === 'achievement') && (
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className={`absolute w-2 h-2 ${styles.accent} rounded-full animate-ping`}
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`,
                animationDuration: `${1 + Math.random()}s`,
              }}
            />
          ))}
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className={`${styles.icon} ${showCelebration ? 'animate-bounce' : ''}`}>
            {milestone?.icon ? (
              <span className="text-2xl">{milestone.icon}</span>
            ) : (
              getTypeIcon()
            )}
          </div>
          <div>
            <h4 className={`font-semibold ${styles.title}`}>
              {title}
              {milestone?.level && (
                <span className="ml-2 text-sm bg-white bg-opacity-50 px-2 py-1 rounded-full">
                  Level {milestone.level}
                </span>
              )}
            </h4>
            <p className={`text-sm ${styles.description} mt-1`}>
              {description}
            </p>
          </div>
        </div>

        {/* Dismiss button */}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Progress bar for progress type */}
      {progress && type === 'progress' && (
        <div className="mb-3">
          <div className="flex justify-between text-xs mb-1">
            <span className={styles.description}>
              {progress.current} of {progress.total} {progress.unit || 'completed'}
            </span>
            <span className={styles.description}>
              {Math.round((progress.current / progress.total) * 100)}%
            </span>
          </div>
          <div className="w-full bg-white bg-opacity-50 rounded-full h-2">
            <div 
              className={`${styles.accent} h-2 rounded-full transition-all duration-1000 ease-out`}
              style={{ width: `${(progress.current / progress.total) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Milestone details */}
      {milestone && type === 'milestone' && (
        <div className="bg-white bg-opacity-50 rounded-lg p-3 mt-3">
          <div className="flex items-center justify-between">
            <div>
              <h5 className={`font-medium ${styles.title}`}>
                {milestone.name}
              </h5>
              <p className={`text-xs ${styles.description} mt-1`}>
                Milestone achieved!
              </p>
            </div>
            <div className="text-2xl">
              {milestone.icon || '🎉'}
            </div>
          </div>
        </div>
      )}

      {/* Achievement badge */}
      {type === 'achievement' && (
        <div className="flex justify-center mt-3">
          <div className={`${styles.accent} text-white px-4 py-2 rounded-full text-sm font-medium shadow-lg ${
            showCelebration ? 'animate-pulse' : ''
          }`}>
            🏆 Achievement Unlocked!
          </div>
        </div>
      )}

      {/* Encouragement actions */}
      {type === 'encouragement' && (
        <div className="flex justify-center space-x-2 mt-3">
          <button className="bg-white bg-opacity-50 hover:bg-opacity-75 px-3 py-1 rounded-full text-xs font-medium transition-colors">
            Keep Going!
          </button>
          <button className="bg-white bg-opacity-50 hover:bg-opacity-75 px-3 py-1 rounded-full text-xs font-medium transition-colors">
            Share Progress
          </button>
        </div>
      )}

      {/* Animated border for special types */}
      {(type === 'milestone' || type === 'achievement') && showCelebration && (
        <div className="absolute inset-0 rounded-lg border-2 border-transparent bg-gradient-to-r from-transparent via-white to-transparent bg-clip-border animate-pulse" />
      )}
    </div>
  );
};

export default ProgressFeedback;