import React, { useState } from 'react';
import { TherapeuticApproach, THERAPEUTIC_APPROACHES_INFO, IntensityLevel } from '../../types/preferences';

interface TherapeuticApproachSelectorProps {
  selected: TherapeuticApproach[];
  onChange: (approaches: TherapeuticApproach[]) => void;
  intensityLevel?: IntensityLevel;
}

const TherapeuticApproachSelector: React.FC<TherapeuticApproachSelectorProps> = ({
  selected,
  onChange,
  intensityLevel,
}) => {
  const [expandedApproach, setExpandedApproach] = useState<TherapeuticApproach | null>(null);

  const handleApproachToggle = (approach: TherapeuticApproach) => {
    const updatedApproaches = selected.includes(approach)
      ? selected.filter(a => a !== approach)
      : [...selected, approach];

    onChange(updatedApproaches);
  };

  const isApproachCompatible = (approach: TherapeuticApproach) => {
    if (!intensityLevel) return true;
    const approachInfo = THERAPEUTIC_APPROACHES_INFO[approach];
    return approachInfo.intensity.includes(intensityLevel);
  };

  const getApproachIcon = (approach: TherapeuticApproach) => {
    const icons = {
      [TherapeuticApproach.CBT]: '🧠',
      [TherapeuticApproach.MINDFULNESS]: '🧘',
      [TherapeuticApproach.NARRATIVE]: '📖',
      [TherapeuticApproach.SOMATIC]: '🤸',
      [TherapeuticApproach.HUMANISTIC]: '💝',
      [TherapeuticApproach.PSYCHODYNAMIC]: '🔍',
      [TherapeuticApproach.ACCEPTANCE_COMMITMENT]: '🎯',
      [TherapeuticApproach.DIALECTICAL_BEHAVIOR]: '⚖️',
    };
    return icons[approach] || '🔧';
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Preferred Therapeutic Approaches
        </h3>
        <p className="text-gray-600 mb-6">
          Select the therapeutic approaches that resonate with you. You can choose multiple approaches
          that will be integrated into your personalized experience. Each approach offers different
          techniques and perspectives for growth and healing.
        </p>
      </div>

      {/* Quick Selection Buttons */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Quick Selection:</h4>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => onChange([TherapeuticApproach.MINDFULNESS, TherapeuticApproach.CBT])}
            className="btn-outline text-sm"
          >
            Beginner Friendly
          </button>
          <button
            onClick={() => onChange([TherapeuticApproach.CBT, TherapeuticApproach.ACCEPTANCE_COMMITMENT])}
            className="btn-outline text-sm"
          >
            Goal Oriented
          </button>
          <button
            onClick={() => onChange([TherapeuticApproach.MINDFULNESS, TherapeuticApproach.SOMATIC])}
            className="btn-outline text-sm"
          >
            Body-Mind Connection
          </button>
          <button
            onClick={() => onChange([TherapeuticApproach.NARRATIVE, TherapeuticApproach.HUMANISTIC])}
            className="btn-outline text-sm"
          >
            Story & Growth
          </button>
        </div>
      </div>

      {/* Approach Selection Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.values(TherapeuticApproach).map((approach) => {
          const info = THERAPEUTIC_APPROACHES_INFO[approach];
          const isSelected = selected.includes(approach);
          const isCompatible = isApproachCompatible(approach);
          const isExpanded = expandedApproach === approach;

          return (
            <div
              key={approach}
              className={`border-2 rounded-lg transition-all ${
                isSelected
                  ? 'border-primary-500 bg-primary-50'
                  : isCompatible
                  ? 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  : 'border-gray-100 bg-gray-50 opacity-60'
              }`}
            >
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <label className="flex items-start space-x-3 cursor-pointer flex-1">
                    <input
                      type="checkbox"
                      className="mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      checked={isSelected}
                      onChange={() => handleApproachToggle(approach)}
                      disabled={!isCompatible}
                    />
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <span className="text-xl mr-2">{getApproachIcon(approach)}</span>
                        <h4 className="font-semibold text-gray-900">{info.name}</h4>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{info.description}</p>

                      {!isCompatible && intensityLevel && (
                        <div className="text-xs text-amber-600 mb-2 flex items-center">
                          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                          Not recommended for {intensityLevel} intensity
                        </div>
                      )}

                      <div className="flex flex-wrap gap-1 mb-3">
                        {info.bestFor.slice(0, 3).map((condition, index) => (
                          <span
                            key={index}
                            className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
                          >
                            {condition}
                          </span>
                        ))}
                        {info.bestFor.length > 3 && (
                          <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                            +{info.bestFor.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  </label>

                  <button
                    onClick={() => setExpandedApproach(isExpanded ? null : approach)}
                    className="ml-2 p-1 text-gray-400 hover:text-gray-600"
                  >
                    <svg
                      className={`w-4 h-4 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="space-y-3">
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">Key Techniques:</h5>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {info.techniques.map((technique, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-primary-500 mr-2 mt-1">•</span>
                              <span>{technique}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">Best For:</h5>
                        <div className="flex flex-wrap gap-1">
                          {info.bestFor.map((condition, index) => (
                            <span
                              key={index}
                              className="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full"
                            >
                              {condition}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">Compatible Intensity Levels:</h5>
                        <div className="flex flex-wrap gap-1">
                          {info.intensity.map((level, index) => (
                            <span
                              key={index}
                              className={`inline-block px-2 py-1 text-xs rounded-full ${
                                level === intensityLevel
                                  ? 'bg-primary-100 text-primary-800'
                                  : 'bg-gray-100 text-gray-600'
                              }`}
                            >
                              {level.charAt(0).toUpperCase() + level.slice(1)}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selection Summary */}
      {selected.length > 0 && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <h4 className="font-medium text-primary-900 mb-2">
            Selected Approaches ({selected.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {selected.map((approach) => {
              const info = THERAPEUTIC_APPROACHES_INFO[approach];
              return (
                <div
                  key={approach}
                  className="flex items-center bg-white rounded-full px-3 py-1 text-sm"
                >
                  <span className="mr-2">{getApproachIcon(approach)}</span>
                  <span className="text-primary-800">{info.name}</span>
                  <button
                    onClick={() => handleApproachToggle(approach)}
                    className="ml-2 text-primary-600 hover:text-primary-800"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Guidance */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-400 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h4 className="font-medium text-blue-900 mb-1">💡 Choosing Therapeutic Approaches</h4>
            <div className="text-blue-800 text-sm space-y-1">
              <p>• <strong>Start with 1-3 approaches</strong> to avoid overwhelming your experience</p>
              <p>• <strong>Mix complementary approaches</strong> (e.g., CBT + Mindfulness) for balanced support</p>
              <p>• <strong>Consider your goals</strong> - different approaches excel at different outcomes</p>
              <p>• <strong>You can adjust</strong> your selections anytime as you discover what works best</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TherapeuticApproachSelector;
