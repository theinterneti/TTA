/**
 * Conflict Resolution Interface Component
 * 
 * Provides user-friendly interface for resolving therapeutic goal conflicts
 * with guided resolution strategies and real-time feedback.
 */

import React, { useState } from 'react';
import { 
  EnhancedGoalConflict, 
  ConflictResolutionStrategy,
  applyAutomaticResolution 
} from '../../../services/conflictDetectionService';
import { THERAPEUTIC_GOALS } from '../../../types/preferences';

interface ConflictResolutionInterfaceProps {
  conflicts: EnhancedGoalConflict[];
  selectedGoals: string[];
  onResolveConflict: (conflictId: string, strategy: ConflictResolutionStrategy) => void;
  onApplyAutomaticResolution: () => void;
  onModifyGoals: (newGoals: string[]) => void;
  className?: string;
}

const ConflictResolutionInterface: React.FC<ConflictResolutionInterfaceProps> = ({
  conflicts,
  selectedGoals,
  onResolveConflict,
  onApplyAutomaticResolution,
  onModifyGoals,
  className = ''
}) => {
  const [expandedConflicts, setExpandedConflicts] = useState<Set<string>>(new Set());
  const [selectedStrategies, setSelectedStrategies] = useState<Record<string, string>>({});

  const toggleConflictExpansion = (conflictId: string) => {
    const newExpanded = new Set(expandedConflicts);
    if (newExpanded.has(conflictId)) {
      newExpanded.delete(conflictId);
    } else {
      newExpanded.add(conflictId);
    }
    setExpandedConflicts(newExpanded);
  };

  const selectStrategy = (conflictId: string, strategyId: string) => {
    setSelectedStrategies(prev => ({
      ...prev,
      [conflictId]: strategyId
    }));
  };

  const applyStrategy = (conflict: EnhancedGoalConflict) => {
    const strategyId = selectedStrategies[conflict.conflictId];
    const strategy = conflict.resolutionStrategies.find(s => s.strategyId === strategyId);
    if (strategy) {
      onResolveConflict(conflict.conflictId, strategy);
    }
  };

  const getSeverityColor = (level: string) => {
    switch (level) {
      case 'critical': return 'border-red-500 bg-red-50';
      case 'high': return 'border-orange-500 bg-orange-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      case 'low': return 'border-blue-500 bg-blue-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  const getSeverityIcon = (level: string) => {
    switch (level) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      case 'low': return '💡';
      default: return '❓';
    }
  };

  const getGoalLabel = (goalId: string) => {
    const goal = Object.values(THERAPEUTIC_GOALS).flat().find(g => g.id === goalId);
    return goal?.label || goalId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const autoResolvableConflicts = conflicts.filter(c => c.autoResolvable && c.severityLevel.level !== 'critical');
  const manualConflicts = conflicts.filter(c => !c.autoResolvable || c.severityLevel.level === 'critical');

  if (conflicts.length === 0) {
    return null;
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">🔧</span>
          <h3 className="text-xl font-semibold text-gray-900">Conflict Resolution</h3>
        </div>
        <div className="text-sm text-gray-500">
          {conflicts.length} conflict{conflicts.length !== 1 ? 's' : ''} detected
        </div>
      </div>

      {/* Auto-Resolvable Conflicts */}
      {autoResolvableConflicts.length > 0 && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-lg">✨</span>
              <h4 className="font-semibold text-green-900">Auto-Resolvable Conflicts</h4>
            </div>
            <button
              onClick={onApplyAutomaticResolution}
              className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              Apply Auto-Resolution
            </button>
          </div>
          <p className="text-sm text-green-700 mb-2">
            {autoResolvableConflicts.length} conflict{autoResolvableConflicts.length !== 1 ? 's' : ''} can be resolved automatically with recommended adjustments.
          </p>
          <ul className="text-xs text-green-600 space-y-1">
            {autoResolvableConflicts.map(conflict => (
              <li key={conflict.conflictId}>
                • {conflict.description}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Manual Resolution Required */}
      {manualConflicts.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-900 flex items-center space-x-2">
            <span>🎯</span>
            <span>Conflicts Requiring Your Attention</span>
          </h4>

          {manualConflicts.map(conflict => (
            <div
              key={conflict.conflictId}
              className={`border-2 rounded-lg p-4 transition-all ${getSeverityColor(conflict.severityLevel.level)}`}
            >
              {/* Conflict Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-lg">{getSeverityIcon(conflict.severityLevel.level)}</span>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      conflict.severityLevel.level === 'critical' ? 'bg-red-100 text-red-800' :
                      conflict.severityLevel.level === 'high' ? 'bg-orange-100 text-orange-800' :
                      conflict.severityLevel.level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {conflict.severityLevel.level.toUpperCase()} PRIORITY
                    </span>
                    <span className="text-xs text-gray-500">
                      {conflict.severityLevel.urgency.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <h5 className="font-medium text-gray-900 mb-1">
                    {conflict.conflictingGoals.map(getGoalLabel).join(' + ')}
                  </h5>
                  <p className="text-sm text-gray-700">{conflict.description}</p>
                </div>
                <button
                  onClick={() => toggleConflictExpansion(conflict.conflictId)}
                  className="ml-4 p-2 text-gray-400 hover:text-gray-600 focus:outline-none"
                  aria-label={expandedConflicts.has(conflict.conflictId) ? 'Collapse details' : 'Expand details'}
                >
                  <svg
                    className={`w-5 h-5 transform transition-transform ${
                      expandedConflicts.has(conflict.conflictId) ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>

              {/* Expanded Details */}
              {expandedConflicts.has(conflict.conflictId) && (
                <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
                  {/* Impact Analysis */}
                  <div>
                    <h6 className="font-medium text-gray-900 mb-2">Impact Analysis</h6>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div className="text-center">
                        <div className="text-lg font-semibold text-red-600">
                          {Math.round(conflict.impactAnalysis.therapeuticRisk * 100)}%
                        </div>
                        <div className="text-xs text-gray-600">Therapeutic Risk</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-semibold text-orange-600">
                          {Math.round(conflict.impactAnalysis.progressImpact * 100)}%
                        </div>
                        <div className="text-xs text-gray-600">Progress Impact</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-semibold text-blue-600">
                          {Math.round(conflict.impactAnalysis.userExperienceImpact * 100)}%
                        </div>
                        <div className="text-xs text-gray-600">UX Impact</div>
                      </div>
                    </div>
                  </div>

                  {/* Resolution Strategies */}
                  <div>
                    <h6 className="font-medium text-gray-900 mb-3">Resolution Strategies</h6>
                    <div className="space-y-3">
                      {conflict.resolutionStrategies.map(strategy => (
                        <div
                          key={strategy.strategyId}
                          className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                            selectedStrategies[conflict.conflictId] === strategy.strategyId
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => selectStrategy(conflict.conflictId, strategy.strategyId)}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h6 className="font-medium text-gray-900">{strategy.title}</h6>
                            <div className="flex items-center space-x-2">
                              <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                                strategy.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                                strategy.difficulty === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-red-100 text-red-700'
                              }`}>
                                {strategy.difficulty}
                              </span>
                              <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                                strategy.clinicalEvidence === 'high' ? 'bg-green-100 text-green-700' :
                                strategy.clinicalEvidence === 'medium' ? 'bg-blue-100 text-blue-700' :
                                'bg-gray-100 text-gray-700'
                              }`}>
                                {strategy.clinicalEvidence} evidence
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{strategy.description}</p>
                          <div className="text-xs text-gray-500">
                            <span>⏱️ {strategy.timeframe}</span>
                            <span className="mx-2">•</span>
                            <span>🎯 {strategy.expectedOutcome}</span>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Apply Strategy Button */}
                    {selectedStrategies[conflict.conflictId] && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <button
                          onClick={() => applyStrategy(conflict)}
                          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                        >
                          Apply Selected Strategy
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Clinical Guidance */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <h6 className="font-medium text-blue-900 mb-1 flex items-center">
                      <span className="mr-2">👨‍⚕️</span>
                      Clinical Guidance
                    </h6>
                    <p className="text-sm text-blue-800">{conflict.clinicalGuidance}</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConflictResolutionInterface;
