/**
 * Conflict Warning Banner Component
 * 
 * Displays real-time conflict warnings with severity indicators and quick actions
 * for therapeutic goal conflicts.
 */

import React, { useState } from 'react';
import { ConflictDetectionResult } from '../../../services/conflictDetectionService';

interface ConflictWarningBannerProps {
  conflictResult: ConflictDetectionResult;
  onViewDetails: () => void;
  onQuickResolve: () => void;
  onDismiss?: () => void;
  className?: string;
}

const ConflictWarningBanner: React.FC<ConflictWarningBannerProps> = ({
  conflictResult,
  onViewDetails,
  onQuickResolve,
  onDismiss,
  className = ''
}) => {
  const [isDismissed, setIsDismissed] = useState(false);

  const handleDismiss = () => {
    setIsDismissed(true);
    onDismiss?.();
  };

  const getWarningConfig = (warningLevel: string) => {
    switch (warningLevel) {
      case 'critical':
        return {
          bgColor: 'bg-red-100',
          borderColor: 'border-red-500',
          textColor: 'text-red-900',
          icon: '🚨',
          title: 'Critical Conflicts Detected',
          urgency: 'Immediate attention required'
        };
      case 'high':
        return {
          bgColor: 'bg-orange-100',
          borderColor: 'border-orange-500',
          textColor: 'text-orange-900',
          icon: '⚠️',
          title: 'High-Priority Conflicts',
          urgency: 'Should be addressed soon'
        };
      case 'medium':
        return {
          bgColor: 'bg-yellow-100',
          borderColor: 'border-yellow-500',
          textColor: 'text-yellow-900',
          icon: '⚡',
          title: 'Moderate Conflicts',
          urgency: 'May impact progress'
        };
      case 'low':
        return {
          bgColor: 'bg-blue-100',
          borderColor: 'border-blue-500',
          textColor: 'text-blue-900',
          icon: '💡',
          title: 'Minor Conflicts',
          urgency: 'Monitor for changes'
        };
      default:
        return {
          bgColor: 'bg-gray-100',
          borderColor: 'border-gray-500',
          textColor: 'text-gray-900',
          icon: '❓',
          title: 'Conflicts Detected',
          urgency: 'Review recommended'
        };
    }
  };

  const getRiskScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-red-600';
    if (score >= 0.6) return 'text-orange-600';
    if (score >= 0.4) return 'text-yellow-600';
    return 'text-blue-600';
  };

  // Don't render if no conflicts or dismissed
  if (conflictResult.warningLevel === 'none' || isDismissed) {
    return null;
  }

  const config = getWarningConfig(conflictResult.warningLevel);

  return (
    <div className={`${config.bgColor} border-l-4 ${config.borderColor} p-4 mb-4 ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <span className="text-2xl" role="img" aria-label="Warning icon">
            {config.icon}
          </span>
        </div>
        
        <div className="ml-3 flex-1">
          {/* Header */}
          <div className="flex items-center justify-between mb-2">
            <div>
              <h3 className={`text-lg font-semibold ${config.textColor}`}>
                {config.title}
              </h3>
              <p className={`text-sm ${config.textColor} opacity-80`}>
                {config.urgency}
              </p>
            </div>
            
            {/* Risk Score */}
            <div className="text-right">
              <div className={`text-2xl font-bold ${getRiskScoreColor(conflictResult.overallRiskScore)}`}>
                {Math.round(conflictResult.overallRiskScore * 100)}%
              </div>
              <div className="text-xs text-gray-600">Risk Score</div>
            </div>
          </div>

          {/* Conflict Summary */}
          <div className="mb-3">
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-1">
                <span className="font-medium">{conflictResult.summary.totalConflicts}</span>
                <span className={config.textColor}>
                  conflict{conflictResult.summary.totalConflicts !== 1 ? 's' : ''}
                </span>
              </div>
              
              {conflictResult.summary.criticalConflicts > 0 && (
                <div className="flex items-center space-x-1">
                  <span className="font-medium text-red-600">{conflictResult.summary.criticalConflicts}</span>
                  <span className="text-red-600">critical</span>
                </div>
              )}
              
              {conflictResult.summary.resolvableConflicts > 0 && (
                <div className="flex items-center space-x-1">
                  <span className="font-medium text-green-600">{conflictResult.summary.resolvableConflicts}</span>
                  <span className="text-green-600">auto-resolvable</span>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onViewDetails}
              className={`inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md ${config.textColor} bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              View Details
            </button>

            {conflictResult.summary.resolvableConflicts > 0 && (
              <button
                onClick={onQuickResolve}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Quick Resolve ({conflictResult.summary.resolvableConflicts})
              </button>
            )}

            {!conflictResult.safeToProceeed && (
              <div className="flex items-center text-sm text-red-600">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                Not safe to proceed
              </div>
            )}
          </div>

          {/* Recommended Actions Preview */}
          {conflictResult.recommendedActions.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <h4 className={`text-sm font-medium ${config.textColor} mb-1`}>
                Quick Recommendations:
              </h4>
              <ul className={`text-sm ${config.textColor} opacity-90 space-y-1`}>
                {conflictResult.recommendedActions.slice(0, 2).map((action, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>{action}</span>
                  </li>
                ))}
                {conflictResult.recommendedActions.length > 2 && (
                  <li className="text-xs opacity-70">
                    +{conflictResult.recommendedActions.length - 2} more recommendations
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>

        {/* Dismiss Button */}
        {onDismiss && (
          <div className="ml-4 flex-shrink-0">
            <button
              onClick={handleDismiss}
              className={`inline-flex rounded-md p-1.5 ${config.textColor} hover:bg-white hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
              aria-label="Dismiss warning"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConflictWarningBanner;
