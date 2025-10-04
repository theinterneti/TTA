import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import {
  fetchPlayerPreferences,
  savePlayerPreferences,
  createPlayerPreferences,
  updatePreferencesLocal,
  markChangesSaved,
  clearError,
  validatePreferences,
} from '../../store/slices/playerPreferencesSlice';
import IntensityLevelSelector from './IntensityLevelSelector';
import TherapeuticApproachSelector from './TherapeuticApproachSelector';
import ConversationStyleSelector from './ConversationStyleSelector';
import TherapeuticGoalsSelector from './TherapeuticGoalsSelector';
import CharacterCustomization from './CharacterCustomization';
import TopicPreferences from './TopicPreferences';
import PreferencePreview from './PreferencePreview';
import { PlayerPreferences } from '../../types/preferences';

interface PlayerPreferencesConfigurationProps {
  playerId: string;
  isOnboarding?: boolean;
  onComplete?: (preferences: PlayerPreferences) => void;
  onCancel?: () => void;
}

const PlayerPreferencesConfiguration: React.FC<PlayerPreferencesConfigurationProps> = ({
  playerId,
  isOnboarding = false,
  onComplete,
  onCancel,
}) => {
  const dispatch = useDispatch();
  const { 
    preferences, 
    isLoading, 
    isSaving, 
    error, 
    hasUnsavedChanges, 
    validationResult 
  } = useSelector((state: RootState) => state.playerPreferences);

  const [activeTab, setActiveTab] = useState('intensity');
  const [showUnsavedWarning, setShowUnsavedWarning] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  // Load preferences on component mount
  useEffect(() => {
    const loadPreferences = async () => {
      try {
        await dispatch(fetchPlayerPreferences(playerId) as any);
      } catch (error) {
        // If preferences don't exist, create default ones
        if (isOnboarding) {
          await dispatch(createPlayerPreferences(playerId) as any);
        }
      }
    };

    loadPreferences();
  }, [dispatch, playerId, isOnboarding]);

  // Clear error when component unmounts
  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  const handleSavePreferences = async () => {
    if (!preferences) return;

    try {
      // Validate preferences before saving
      const validation = await dispatch(validatePreferences(preferences) as any);
      
      if (validation.payload?.isValid) {
        await dispatch(savePlayerPreferences({ 
          playerId, 
          preferences 
        }) as any);
        
        dispatch(markChangesSaved());
        setShowUnsavedWarning(false);
        
        if (onComplete) {
          onComplete(preferences);
        }
      }
    } catch (error) {
      console.error('Failed to save preferences:', error);
    }
  };

  const handleTabChange = (tab: string) => {
    if (hasUnsavedChanges && !isOnboarding) {
      setShowUnsavedWarning(true);
      return;
    }
    setActiveTab(tab);
  };

  const handlePreferenceUpdate = (updates: Partial<PlayerPreferences>) => {
    dispatch(updatePreferencesLocal(updates));
  };

  const tabs = [
    { id: 'intensity', label: 'Intensity Level', icon: '⚡' },
    { id: 'approaches', label: 'Therapeutic Approaches', icon: '🧠' },
    { id: 'style', label: 'Conversation Style', icon: '💬' },
    { id: 'goals', label: 'Therapeutic Goals', icon: '🎯' },
    { id: 'character', label: 'Character & Setting', icon: '🎭' },
    { id: 'topics', label: 'Topic Preferences', icon: '📝' },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-gray-600">Loading preferences...</span>
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-600 mb-4">Unable to load preferences.</p>
        <button
          onClick={() => dispatch(createPlayerPreferences(playerId) as any)}
          className="btn-primary"
        >
          Create Default Preferences
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {isOnboarding ? 'Welcome! Let\'s Personalize Your Experience' : 'Player Preferences'}
            </h2>
            <p className="text-gray-600 mt-1">
              {isOnboarding 
                ? 'Configure your therapeutic preferences to create a personalized experience.'
                : 'Manage your therapeutic preferences and customization settings.'
              }
            </p>
          </div>
          
          {showPreview && (
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="btn-secondary"
            >
              {showPreview ? 'Hide Preview' : 'Show Preview'}
            </button>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* Validation Results */}
        {validationResult && !validationResult.isValid && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h4 className="font-medium text-yellow-800 mb-2">Validation Issues:</h4>
            <ul className="list-disc list-inside text-yellow-700 text-sm">
              {validationResult.errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="flex">
        {/* Sidebar Navigation */}
        <div className="w-64 bg-gray-50 border-r border-gray-200">
          <nav className="p-4 space-y-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={`w-full flex items-center px-3 py-2 text-left rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary-100 text-primary-700 border border-primary-200'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <span className="text-lg mr-3">{tab.icon}</span>
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </nav>

          {/* Progress Indicator */}
          {isOnboarding && (
            <div className="p-4 border-t border-gray-200">
              <div className="text-sm text-gray-600 mb-2">Setup Progress</div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((tabs.findIndex(t => t.id === activeTab) + 1) / tabs.length) * 100}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Step {tabs.findIndex(t => t.id === activeTab) + 1} of {tabs.length}
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="flex-1">
          <div className="p-6">
            {activeTab === 'intensity' && (
              <IntensityLevelSelector
                value={preferences.intensity_level}
                onChange={(level) => handlePreferenceUpdate({ intensity_level: level })}
              />
            )}

            {activeTab === 'approaches' && (
              <TherapeuticApproachSelector
                selected={preferences.preferred_approaches}
                onChange={(approaches) => handlePreferenceUpdate({ preferred_approaches: approaches })}
              />
            )}

            {activeTab === 'style' && (
              <ConversationStyleSelector
                value={preferences.conversation_style}
                onChange={(style) => handlePreferenceUpdate({ conversation_style: style })}
              />
            )}

            {activeTab === 'goals' && (
              <TherapeuticGoalsSelector
                selected={preferences.therapeutic_goals}
                primaryConcerns={preferences.primary_concerns}
                onChange={(goals, concerns) => handlePreferenceUpdate({ 
                  therapeutic_goals: goals,
                  primary_concerns: concerns 
                })}
              />
            )}

            {activeTab === 'character' && (
              <CharacterCustomization
                characterName={preferences.character_name}
                preferredSetting={preferences.preferred_setting}
                onChange={(updates) => handlePreferenceUpdate(updates)}
              />
            )}

            {activeTab === 'topics' && (
              <TopicPreferences
                comfortTopics={preferences.comfort_topics}
                triggerTopics={preferences.trigger_topics}
                avoidTopics={preferences.avoid_topics}
                onChange={(updates) => handlePreferenceUpdate(updates)}
              />
            )}
          </div>

          {/* Preview Panel */}
          {showPreview && (
            <div className="border-t border-gray-200">
              <PreferencePreview preferences={preferences} />
            </div>
          )}

          {/* Action Buttons */}
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {hasUnsavedChanges && (
                <span className="text-sm text-amber-600 flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Unsaved changes
                </span>
              )}
              
              <button
                onClick={() => setShowPreview(!showPreview)}
                className="btn-secondary text-sm"
              >
                {showPreview ? 'Hide' : 'Show'} Preview
              </button>
            </div>

            <div className="flex items-center space-x-3">
              {onCancel && (
                <button
                  onClick={onCancel}
                  className="btn-secondary"
                  disabled={isSaving}
                >
                  Cancel
                </button>
              )}
              
              <button
                onClick={handleSavePreferences}
                disabled={isSaving || (validationResult && !validationResult.isValid)}
                className="btn-primary flex items-center"
              >
                {isSaving && (
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                )}
                {isOnboarding ? 'Complete Setup' : 'Save Preferences'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Unsaved Changes Warning Modal */}
      {showUnsavedWarning && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Unsaved Changes</h3>
            <p className="text-gray-600 mb-4">
              You have unsaved changes. Do you want to save them before switching tabs?
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowUnsavedWarning(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowUnsavedWarning(false);
                  setActiveTab(activeTab);
                }}
                className="btn-outline"
              >
                Discard Changes
              </button>
              <button
                onClick={handleSavePreferences}
                className="btn-primary"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlayerPreferencesConfiguration;
