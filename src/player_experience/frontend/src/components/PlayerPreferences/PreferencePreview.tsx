import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import { generatePreferencePreview } from '../../store/slices/playerPreferencesSlice';
import { PlayerPreferences } from '../../types/preferences';

interface PreferencePreviewProps {
  preferences: PlayerPreferences;
}

const PreferencePreview: React.FC<PreferencePreviewProps> = ({ preferences }) => {
  const dispatch = useDispatch();
  const { previewContext, isPreviewLoading } = useSelector(
    (state: RootState) => state.playerPreferences
  );

  const [testMessage, setTestMessage] = useState('I\'ve been feeling really anxious about work lately and I don\'t know how to handle it.');
  const [selectedScenario, setSelectedScenario] = useState('anxiety');

  const testScenarios = {
    anxiety: {
      message: 'I\'ve been feeling really anxious about work lately and I don\'t know how to handle it.',
      label: 'Work Anxiety',
      icon: '😰'
    },
    confidence: {
      message: 'I feel like I\'m not good enough and everyone else is more capable than me.',
      label: 'Low Confidence',
      icon: '😔'
    },
    stress: {
      message: 'Everything feels overwhelming right now. I have so much to do and not enough time.',
      label: 'Overwhelm',
      icon: '😵‍💫'
    },
    growth: {
      message: 'I want to grow as a person but I don\'t know where to start or what to focus on.',
      label: 'Personal Growth',
      icon: '🌱'
    },
    relationships: {
      message: 'I\'m having trouble communicating with my partner and we keep having the same arguments.',
      label: 'Relationship Issues',
      icon: '💔'
    }
  };

  useEffect(() => {
    if (preferences && testMessage) {
      const timer = setTimeout(() => {
        dispatch(generatePreferencePreview({ preferences, testMessage }) as any);
      }, 500);

      return () => clearTimeout(timer);
    }
  }, [preferences, testMessage, dispatch]);

  const handleScenarioChange = (scenario: keyof typeof testScenarios) => {
    setSelectedScenario(scenario);
    setTestMessage(testScenarios[scenario].message);
  };

  const getAdaptationColor = (adaptation: string) => {
    if (adaptation.includes('intensity') || adaptation.includes('Intensity')) return 'bg-blue-100 text-blue-800';
    if (adaptation.includes('approach') || adaptation.includes('Approach')) return 'bg-green-100 text-green-800';
    if (adaptation.includes('style') || adaptation.includes('Style')) return 'bg-purple-100 text-purple-800';
    if (adaptation.includes('topic') || adaptation.includes('Topic')) return 'bg-amber-100 text-amber-800';
    if (adaptation.includes('character') || adaptation.includes('Character')) return 'bg-pink-100 text-pink-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white border-t border-gray-200 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h4 className="text-lg font-semibold text-gray-900 mb-2">
            🔮 Preference Preview
          </h4>
          <p className="text-gray-600 text-sm">
            See how your preferences will affect AI responses in real therapeutic conversations.
          </p>
        </div>

        {/* Test Scenario Selection */}
        <div className="space-y-3">
          <h5 className="font-medium text-gray-900">Test Scenarios</h5>
          <div className="flex flex-wrap gap-2">
            {Object.entries(testScenarios).map(([key, scenario]) => (
              <button
                key={key}
                onClick={() => handleScenarioChange(key as keyof typeof testScenarios)}
                className={`flex items-center px-3 py-2 text-sm rounded-lg border transition-colors ${
                  selectedScenario === key
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <span className="mr-2">{scenario.icon}</span>
                <span>{scenario.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Custom Test Message */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Custom Test Message
          </label>
          <textarea
            value={testMessage}
            onChange={(e) => setTestMessage(e.target.value)}
            placeholder="Enter a message to see how your preferences affect the response..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            rows={3}
          />
        </div>

        {/* Preview Results */}
        <div className="space-y-4">
          {isPreviewLoading ? (
            <div className="flex items-center justify-center p-8 bg-gray-50 rounded-lg">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
              <span className="ml-3 text-gray-600">Generating preview...</span>
            </div>
          ) : previewContext ? (
            <div className="space-y-4">
              {/* User Message */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                    <span className="text-sm">You</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-800">{previewContext.user_message}</p>
                  </div>
                </div>
              </div>

              {/* AI Response */}
              <div className="bg-primary-50 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-primary-200 rounded-full flex items-center justify-center">
                    <span className="text-sm">🤗</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className="font-medium text-primary-800">
                        {preferences.character_name}
                      </span>
                      <span className="text-xs text-primary-600 ml-2">
                        in {preferences.preferred_setting.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <p className="text-primary-800 leading-relaxed">
                      {previewContext.preview_response}
                    </p>
                  </div>
                </div>
              </div>

              {/* Applied Adaptations */}
              {previewContext.adaptations_applied && previewContext.adaptations_applied.length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h5 className="font-medium text-blue-900 mb-3">
                    🎯 Applied Personalizations
                  </h5>
                  <div className="flex flex-wrap gap-2">
                    {previewContext.adaptations_applied.map((adaptation, index) => (
                      <span
                        key={index}
                        className={`inline-block px-3 py-1 text-xs rounded-full ${getAdaptationColor(adaptation)}`}
                      >
                        {adaptation}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Preference Summary */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-3">
                  📋 Active Preferences
                </h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Intensity:</span>
                    <span className="ml-2 text-gray-600 capitalize">
                      {preferences.intensity_level}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Style:</span>
                    <span className="ml-2 text-gray-600 capitalize">
                      {preferences.conversation_style}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Approaches:</span>
                    <span className="ml-2 text-gray-600">
                      {preferences.preferred_approaches.length} selected
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Goals:</span>
                    <span className="ml-2 text-gray-600">
                      {preferences.therapeutic_goals.length} selected
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center p-8 bg-gray-50 rounded-lg">
              <p className="text-gray-600">
                Enter a test message above to see how your preferences will personalize the AI response.
              </p>
            </div>
          )}
        </div>

        {/* Comparison Mode */}
        <div className="border-t pt-6">
          <div className="flex items-center justify-between mb-4">
            <h5 className="font-medium text-gray-900">
              📊 Comparison with Default Settings
            </h5>
            <button className="text-sm text-primary-600 hover:text-primary-700">
              Show Default Response
            </button>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-amber-400 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div>
                <h4 className="font-medium text-amber-900 mb-1">💡 Preview Tips</h4>
                <div className="text-amber-800 text-sm space-y-1">
                  <p>• <strong>Try different scenarios</strong> to see how preferences adapt to various situations</p>
                  <p>• <strong>Notice the language changes</strong> based on your intensity and style preferences</p>
                  <p>• <strong>Look for therapeutic approaches</strong> being integrated into responses</p>
                  <p>• <strong>Check comfort topics</strong> being naturally incorporated when appropriate</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Refresh Button */}
        <div className="text-center">
          <button
            onClick={() => dispatch(generatePreferencePreview({ preferences, testMessage }) as any)}
            disabled={isPreviewLoading}
            className="btn-secondary flex items-center mx-auto"
          >
            {isPreviewLoading ? (
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            )}
            Generate New Preview
          </button>
        </div>
      </div>
    </div>
  );
};

export default PreferencePreview;
