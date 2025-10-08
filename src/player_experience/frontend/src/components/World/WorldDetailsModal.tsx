import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import { checkWorldCompatibility } from '../../store/slices/worldSlice';

interface WorldDetailsModalProps {
  worldId: string;
  isOpen: boolean;
  onClose: () => void;
  onCustomize: () => void;
}

const WorldDetailsModal: React.FC<WorldDetailsModalProps> = ({
  worldId,
  isOpen,
  onClose,
  onCustomize,
}) => {
  const dispatch = useDispatch();
  const { selectedWorld, isLoading } = useSelector((state: RootState) => state.world);
  const { selectedCharacter } = useSelector((state: RootState) => state.character);

  useEffect(() => {
    if (selectedCharacter && worldId) {
      dispatch(checkWorldCompatibility({
        characterId: selectedCharacter.character_id,
        worldId
      }) as any);
    }
  }, [dispatch, selectedCharacter, worldId]);

  if (!isOpen || !selectedWorld) return null;

  const getCompatibilityColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getCompatibilityText = (score: number) => {
    if (score >= 0.8) return 'Excellent Match';
    if (score >= 0.6) return 'Good Match';
    return 'Needs Consideration';
  };

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case 'BEGINNER': return 'bg-green-100 text-green-600';
      case 'INTERMEDIATE': return 'bg-yellow-100 text-yellow-600';
      case 'ADVANCED': return 'bg-red-100 text-red-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{selectedWorld.name}</h2>
            <div className="flex items-center space-x-4 mt-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(selectedWorld.difficulty_level)}`}>
                {selectedWorld.difficulty_level}
              </span>
              <span className="text-sm text-gray-600 flex items-center">
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {selectedWorld.estimated_duration}
              </span>
              {selectedCharacter && (
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCompatibilityColor(selectedWorld.compatibility_score)}`}>
                  {Math.round(selectedWorld.compatibility_score * 100)}% - {getCompatibilityText(selectedWorld.compatibility_score)}
                </span>
              )}
            </div>
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
          {/* World Preview */}
          <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center">
            {selectedWorld.preview_image ? (
              <img
                src={selectedWorld.preview_image}
                alt={selectedWorld.name}
                className="w-full h-full object-cover rounded-lg"
              />
            ) : (
              <div className="text-center">
                <svg className="w-16 h-16 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-gray-500">World Preview</p>
              </div>
            )}
          </div>

          {/* Description */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Description</h3>
            <p className="text-gray-700 leading-relaxed">
              {selectedWorld.detailed_description || selectedWorld.description}
            </p>
          </div>

          {/* Therapeutic Themes */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Therapeutic Themes</h3>
            <div className="flex flex-wrap gap-2">
              {selectedWorld.therapeutic_themes.map((theme, index) => (
                <span key={index} className="px-3 py-1 bg-therapeutic-calm text-blue-600 rounded-full text-sm">
                  {theme}
                </span>
              ))}
            </div>
          </div>

          {/* Therapeutic Approaches */}
          {selectedWorld.therapeutic_approaches && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Therapeutic Approaches</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {selectedWorld.therapeutic_approaches.map((approach, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">{approach}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Prerequisites */}
          {selectedWorld.prerequisites && selectedWorld.prerequisites.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Prerequisites</h3>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <ul className="space-y-2">
                  {selectedWorld.prerequisites.map((prerequisite, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <svg className="w-4 h-4 text-yellow-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      <span className="text-yellow-800">{prerequisite}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Customizable Parameters */}
          {selectedWorld.customizable_parameters && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Customization Options</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(selectedWorld.customizable_parameters).map(([param, available]) => (
                  <div key={param} className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${available ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <span className={`text-sm ${available ? 'text-gray-700' : 'text-gray-400'}`}>
                      {param.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Compatibility Details */}
          {selectedCharacter && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Compatibility Analysis</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-gray-700">Overall Compatibility</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCompatibilityColor(selectedWorld.compatibility_score)}`}>
                    {Math.round(selectedWorld.compatibility_score * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      selectedWorld.compatibility_score >= 0.8 ? 'bg-green-500' :
                      selectedWorld.compatibility_score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${selectedWorld.compatibility_score * 100}%` }}
                  />
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Based on your character's therapeutic preferences and current goals
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Close
          </button>
          <div className="flex space-x-3">
            <button
              onClick={onCustomize}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              disabled={!selectedCharacter}
            >
              Customize Parameters
            </button>
            <button
              className="btn-primary px-6 py-2"
              disabled={!selectedCharacter}
            >
              Select This World
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorldDetailsModal;
