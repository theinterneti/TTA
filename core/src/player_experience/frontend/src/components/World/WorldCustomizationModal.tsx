import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';

interface WorldParameters {
  therapeutic_intensity: 'LOW' | 'MEDIUM' | 'HIGH';
  narrative_style: 'GUIDED' | 'EXPLORATORY' | 'STRUCTURED';
  pacing: 'SLOW' | 'MODERATE' | 'FAST';
  interaction_frequency: 'MINIMAL' | 'REGULAR' | 'FREQUENT';
}

interface WorldCustomizationModalProps {
  worldId: string;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (parameters: WorldParameters) => void;
}

const WorldCustomizationModal: React.FC<WorldCustomizationModalProps> = ({
  worldId,
  isOpen,
  onClose,
  onConfirm,
}) => {
  const { selectedWorld } = useSelector((state: RootState) => state.world);
  const { selectedCharacter } = useSelector((state: RootState) => state.character);

  const [parameters, setParameters] = useState<WorldParameters>({
    therapeutic_intensity: 'MEDIUM',
    narrative_style: 'GUIDED',
    pacing: 'MODERATE',
    interaction_frequency: 'REGULAR',
  });

  const [previewMode, setPreviewMode] = useState(false);

  useEffect(() => {
    // Set default parameters based on character's therapeutic preferences
    if (selectedCharacter?.therapeutic_profile) {
      const profile = selectedCharacter.therapeutic_profile;
      setParameters(prev => ({
        ...prev,
        therapeutic_intensity: profile.preferred_intensity || 'MEDIUM',
        // Add other defaults based on character preferences
      }));
    }
  }, [selectedCharacter]);

  if (!isOpen || !selectedWorld) return null;

  const handleParameterChange = (param: keyof WorldParameters, value: string) => {
    setParameters(prev => ({
      ...prev,
      [param]: value,
    }));
  };

  const handleConfirm = () => {
    onConfirm(parameters);
  };

  const getParameterDescription = (param: keyof WorldParameters, value: string) => {
    const descriptions = {
      therapeutic_intensity: {
        LOW: 'Gentle therapeutic guidance with minimal intervention',
        MEDIUM: 'Balanced therapeutic support with moderate intervention',
        HIGH: 'Intensive therapeutic focus with frequent interventions',
      },
      narrative_style: {
        GUIDED: 'Clear direction with structured therapeutic goals',
        EXPLORATORY: 'Open-ended exploration with flexible outcomes',
        STRUCTURED: 'Systematic approach with defined milestones',
      },
      pacing: {
        SLOW: 'Relaxed pace allowing time for reflection',
        MODERATE: 'Balanced pacing with regular progress',
        FAST: 'Dynamic pace with quick therapeutic insights',
      },
      interaction_frequency: {
        MINIMAL: 'Fewer interactions, more self-reflection time',
        REGULAR: 'Balanced interaction with therapeutic guidance',
        FREQUENT: 'High interaction with continuous support',
      },
    };

    return descriptions[param][value as keyof typeof descriptions[typeof param]];
  };

  const isParameterCustomizable = (param: keyof WorldParameters) => {
    if (!selectedWorld.customizable_parameters) return true;
    return selectedWorld.customizable_parameters[param];
  };

  const getRecommendedValue = (param: keyof WorldParameters) => {
    // Logic to recommend values based on character profile and world compatibility
    if (!selectedCharacter?.therapeutic_profile) return null;

    const recommendations = {
      therapeutic_intensity: selectedCharacter.therapeutic_profile.preferred_intensity || 'MEDIUM',
      narrative_style: 'GUIDED', // Default recommendation
      pacing: 'MODERATE', // Default recommendation
      interaction_frequency: 'REGULAR', // Default recommendation
    };

    return recommendations[param];
  };

  const generatePreview = () => {
    return `This world will be customized with ${parameters.therapeutic_intensity.toLowerCase()} therapeutic intensity,
    using a ${parameters.narrative_style.toLowerCase()} narrative approach at a ${parameters.pacing.toLowerCase()} pace
    with ${parameters.interaction_frequency.toLowerCase()} therapeutic interactions.`;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Customize World Parameters</h2>
            <p className="text-gray-600 mt-1">{selectedWorld.name}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Character Context */}
          {selectedCharacter && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span className="font-medium text-blue-900">Customizing for {selectedCharacter.name}</span>
              </div>
              <p className="text-blue-800 text-sm">
                Parameters will be adjusted based on your character's therapeutic preferences and goals.
              </p>
            </div>
          )}

          {/* Parameter Controls */}
          <div className="space-y-6">
            {/* Therapeutic Intensity */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="text-lg font-semibold text-gray-900">
                  Therapeutic Intensity
                </label>
                {getRecommendedValue('therapeutic_intensity') && (
                  <span className="text-sm text-blue-600">
                    Recommended: {getRecommendedValue('therapeutic_intensity')}
                  </span>
                )}
              </div>
              <div className="grid grid-cols-3 gap-3">
                {['LOW', 'MEDIUM', 'HIGH'].map((value) => (
                  <button
                    key={value}
                    onClick={() => handleParameterChange('therapeutic_intensity', value)}
                    disabled={!isParameterCustomizable('therapeutic_intensity')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      parameters.therapeutic_intensity === value
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${!isParameterCustomizable('therapeutic_intensity') ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="font-medium">{value}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      {getParameterDescription('therapeutic_intensity', value)}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Narrative Style */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="text-lg font-semibold text-gray-900">
                  Narrative Style
                </label>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {['GUIDED', 'EXPLORATORY', 'STRUCTURED'].map((value) => (
                  <button
                    key={value}
                    onClick={() => handleParameterChange('narrative_style', value)}
                    disabled={!isParameterCustomizable('narrative_style')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      parameters.narrative_style === value
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${!isParameterCustomizable('narrative_style') ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="font-medium">{value}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      {getParameterDescription('narrative_style', value)}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Pacing */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="text-lg font-semibold text-gray-900">
                  Pacing
                </label>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {['SLOW', 'MODERATE', 'FAST'].map((value) => (
                  <button
                    key={value}
                    onClick={() => handleParameterChange('pacing', value)}
                    disabled={!isParameterCustomizable('pacing')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      parameters.pacing === value
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${!isParameterCustomizable('pacing') ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="font-medium">{value}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      {getParameterDescription('pacing', value)}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Interaction Frequency */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="text-lg font-semibold text-gray-900">
                  Interaction Frequency
                </label>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {['MINIMAL', 'REGULAR', 'FREQUENT'].map((value) => (
                  <button
                    key={value}
                    onClick={() => handleParameterChange('interaction_frequency', value)}
                    disabled={!isParameterCustomizable('interaction_frequency')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      parameters.interaction_frequency === value
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${!isParameterCustomizable('interaction_frequency') ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="font-medium">{value}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      {getParameterDescription('interaction_frequency', value)}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Preview */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-900">Experience Preview</h3>
              <button
                onClick={() => setPreviewMode(!previewMode)}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                {previewMode ? 'Hide Preview' : 'Show Preview'}
              </button>
            </div>
            {previewMode && (
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700">{generatePreview()}</p>
              </div>
            )}
          </div>

          {/* Warnings or Recommendations */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <svg className="w-5 h-5 text-yellow-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <div>
                <h4 className="font-medium text-yellow-800">Customization Note</h4>
                <p className="text-yellow-700 text-sm mt-1">
                  These parameters can be adjusted during your therapeutic journey based on your progress and comfort level.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Cancel
          </button>
          <div className="flex space-x-3">
            <button
              onClick={() => {
                // Reset to recommended values
                if (selectedCharacter?.therapeutic_profile) {
                  setParameters({
                    therapeutic_intensity: selectedCharacter.therapeutic_profile.preferred_intensity || 'MEDIUM',
                    narrative_style: 'GUIDED',
                    pacing: 'MODERATE',
                    interaction_frequency: 'REGULAR',
                  });
                }
              }}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Reset to Recommended
            </button>
            <button
              onClick={handleConfirm}
              className="btn-primary px-6 py-2"
            >
              Confirm & Select World
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorldCustomizationModal;
