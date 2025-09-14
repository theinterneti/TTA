import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import { selectCharacterPreview, selectProgress } from '../../store/slices/conversationalCharacterSlice';

interface ConversationCompletionProps {
  onConfirmCreation: () => void;
  onEditCharacter: () => void;
  onStartNewConversation: () => void;
  characterPreview: any;
}

const ConversationCompletion: React.FC<ConversationCompletionProps> = ({
  onConfirmCreation,
  onEditCharacter,
  onStartNewConversation,
  characterPreview
}) => {
  const dispatch = useDispatch();
  const progress = useSelector(selectProgress);
  const [showFullPreview, setShowFullPreview] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  if (!characterPreview) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Preparing your character preview...</p>
      </div>
    );
  }

  const handleConfirmCreation = async () => {
    setIsCreating(true);
    try {
      await onConfirmCreation();
    } finally {
      setIsCreating(false);
    }
  };

  const getCompletenessColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-blue-600';
    if (score >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCompletenessMessage = (score: number) => {
    if (score >= 0.9) return 'Excellent! Your character is very well-defined.';
    if (score >= 0.7) return 'Great! Your character has enough detail to begin your therapeutic journey.';
    if (score >= 0.5) return 'Good start! You can always add more details later.';
    return 'Your character needs more information to be effective in therapy.';
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Your Therapeutic Companion is Ready!
        </h2>
        <p className="text-gray-600">
          Review your character and confirm creation to begin your therapeutic journey.
        </p>
      </div>

      {/* Completeness Score */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Character Completeness</h3>
          <span className={`text-2xl font-bold ${getCompletenessColor(characterPreview.completeness_score)}`}>
            {Math.round(characterPreview.completeness_score * 100)}%
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${
              characterPreview.completeness_score >= 0.7 ? 'bg-green-500' : 
              characterPreview.completeness_score >= 0.5 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${characterPreview.completeness_score * 100}%` }}
          ></div>
        </div>
        
        <p className={`text-sm ${getCompletenessColor(characterPreview.completeness_score)}`}>
          {getCompletenessMessage(characterPreview.completeness_score)}
        </p>

        {characterPreview.missing_fields && characterPreview.missing_fields.length > 0 && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h4 className="text-sm font-medium text-yellow-800 mb-2">Optional improvements:</h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              {characterPreview.missing_fields.map((field: string, index: number) => (
                <li key={index} className="flex items-center">
                  <span className="w-1.5 h-1.5 bg-yellow-400 rounded-full mr-2"></span>
                  {field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Character Preview */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Character Preview</h3>
          <button
            onClick={() => setShowFullPreview(!showFullPreview)}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            {showFullPreview ? 'Show Less' : 'Show Full Details'}
          </button>
        </div>

        {/* Basic Information */}
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Basic Information</h4>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-600">Name:</span>
                <span className="ml-2 font-medium">{characterPreview.character_preview?.name || 'Not specified'}</span>
              </div>
              <div>
                <span className="text-gray-600">Age Range:</span>
                <span className="ml-2">{characterPreview.character_preview?.appearance?.age_range || 'Not specified'}</span>
              </div>
              <div>
                <span className="text-gray-600">Gender Identity:</span>
                <span className="ml-2">{characterPreview.character_preview?.appearance?.gender_identity || 'Not specified'}</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-3">Therapeutic Profile</h4>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-600">Preferred Intensity:</span>
                <span className="ml-2 capitalize">{characterPreview.character_preview?.therapeutic_profile?.preferred_intensity || 'Not specified'}</span>
              </div>
              <div>
                <span className="text-gray-600">Readiness Level:</span>
                <span className="ml-2">
                  {characterPreview.character_preview?.therapeutic_profile?.readiness_level 
                    ? `${Math.round(characterPreview.character_preview.therapeutic_profile.readiness_level * 100)}%`
                    : 'Not specified'}
                </span>
              </div>
              <div>
                <span className="text-gray-600">Primary Concerns:</span>
                <span className="ml-2">
                  {characterPreview.character_preview?.therapeutic_profile?.primary_concerns?.length || 0} identified
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Full Details */}
        {showFullPreview && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Appearance */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Appearance</h4>
                <div className="text-sm text-gray-700 space-y-2">
                  <p><strong>Description:</strong> {characterPreview.character_preview?.appearance?.physical_description || 'Not provided'}</p>
                  <p><strong>Style:</strong> {characterPreview.character_preview?.appearance?.clothing_style || 'Not specified'}</p>
                  {characterPreview.character_preview?.appearance?.distinctive_features?.length > 0 && (
                    <p><strong>Distinctive Features:</strong> {characterPreview.character_preview.appearance.distinctive_features.join(', ')}</p>
                  )}
                </div>
              </div>

              {/* Background */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Background</h4>
                <div className="text-sm text-gray-700 space-y-2">
                  <p><strong>Backstory:</strong> {characterPreview.character_preview?.background?.backstory || 'Not provided'}</p>
                  {characterPreview.character_preview?.background?.personality_traits?.length > 0 && (
                    <p><strong>Personality:</strong> {characterPreview.character_preview.background.personality_traits.join(', ')}</p>
                  )}
                  {characterPreview.character_preview?.background?.core_values?.length > 0 && (
                    <p><strong>Values:</strong> {characterPreview.character_preview.background.core_values.join(', ')}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Therapeutic Details */}
            <div className="mt-6">
              <h4 className="font-medium text-gray-900 mb-3">Therapeutic Information</h4>
              <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-700">
                <div>
                  {characterPreview.character_preview?.therapeutic_profile?.primary_concerns?.length > 0 && (
                    <p><strong>Primary Concerns:</strong> {characterPreview.character_preview.therapeutic_profile.primary_concerns.join(', ')}</p>
                  )}
                  {characterPreview.character_preview?.therapeutic_profile?.comfort_zones?.length > 0 && (
                    <p className="mt-2"><strong>Comfort Zones:</strong> {characterPreview.character_preview.therapeutic_profile.comfort_zones.join(', ')}</p>
                  )}
                </div>
                <div>
                  {characterPreview.character_preview?.therapeutic_profile?.therapeutic_goals?.length > 0 && (
                    <p><strong>Goals:</strong> {characterPreview.character_preview.therapeutic_profile.therapeutic_goals.join(', ')}</p>
                  )}
                  {characterPreview.character_preview?.therapeutic_profile?.challenge_areas?.length > 0 && (
                    <p className="mt-2"><strong>Challenge Areas:</strong> {characterPreview.character_preview.therapeutic_profile.challenge_areas.join(', ')}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        {characterPreview.ready_for_creation ? (
          <>
            <button
              onClick={handleConfirmCreation}
              disabled={isCreating}
              className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isCreating ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creating Character...
                </div>
              ) : (
                'Create My Therapeutic Companion'
              )}
            </button>
            <button
              onClick={onEditCharacter}
              disabled={isCreating}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              Make Adjustments
            </button>
          </>
        ) : (
          <>
            <button
              onClick={onEditCharacter}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Continue Conversation
            </button>
            <button
              onClick={onStartNewConversation}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Start Over
            </button>
          </>
        )}
      </div>

      {/* Therapeutic Note */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="text-sm font-medium text-blue-900 mb-1">Remember</h4>
            <p className="text-sm text-blue-800">
              Your therapeutic companion is designed to support your healing journey. You can always update 
              their profile as you grow and discover more about yourself. This character will help create 
              a safe, personalized therapeutic experience tailored to your unique needs and goals.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationCompletion;
