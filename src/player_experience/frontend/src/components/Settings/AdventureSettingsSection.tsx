/**
 * Adventure Settings Section
 *
 * Entertainment-first settings interface that presents therapeutic options
 * using gaming and storytelling language while maintaining clinical accuracy
 */

import React, { useState } from 'react';
import { useTranslation } from '../../services/terminologyTranslation';
import { FullUIModeToggle } from './UIModeToggle';

interface AdventureSettings {
  story_intensity: 'gentle' | 'balanced' | 'challenging';
  preferred_story_styles: string[];
  comfort_themes: string[];
  avoid_themes: string[];
  emergency_support?: {
    emergency_contact: string;
    support_contact?: string;
    preferred_help_resources: string[];
  };
}

interface AdventureSettingsSectionProps {
  settings: AdventureSettings;
  onUpdate: (updates: Partial<AdventureSettings>) => void;
}

const AdventureSettingsSection: React.FC<AdventureSettingsSectionProps> = ({
  settings,
  onUpdate,
}) => {
  const [customStyle, setCustomStyle] = useState('');
  const [showCustomStyleInput, setShowCustomStyleInput] = useState(false);
  const { translate, isEntertainmentMode } = useTranslation();

  const storyStyles = [
    {
      id: 'problem_solving',
      name: 'Problem-Solving Adventures',
      description: 'Stories that help you tackle challenges step by step',
      icon: '🧩'
    },
    {
      id: 'mindful_journeys',
      name: 'Mindful Journeys',
      description: 'Peaceful adventures focused on awareness and presence',
      icon: '🧘'
    },
    {
      id: 'personal_stories',
      name: 'Personal Story Exploration',
      description: 'Adventures that help you explore your own narrative',
      icon: '📖'
    },
    {
      id: 'goal_quests',
      name: 'Goal-Focused Quests',
      description: 'Adventures designed to help you achieve specific objectives',
      icon: '🎯'
    },
    {
      id: 'values_adventures',
      name: 'Values-Based Adventures',
      description: 'Stories that explore what matters most to you',
      icon: '⭐'
    },
    {
      id: 'emotional_balance',
      name: 'Emotional Balance Training',
      description: 'Adventures that help you master your emotional responses',
      icon: '⚖️'
    },
    {
      id: 'self_discovery',
      name: 'Self-Discovery Stories',
      description: 'Adventures focused on understanding yourself better',
      icon: '🔍'
    },
    {
      id: 'character_depth',
      name: 'Deep Character Exploration',
      description: 'Complex stories that explore character motivations and growth',
      icon: '🎭'
    }
  ];

  const handleIntensityChange = (intensity: 'gentle' | 'balanced' | 'challenging') => {
    onUpdate({ story_intensity: intensity });
  };

  const handleStyleToggle = (styleId: string) => {
    const updatedStyles = settings.preferred_story_styles.includes(styleId)
      ? settings.preferred_story_styles.filter(s => s !== styleId)
      : [...settings.preferred_story_styles, styleId];

    onUpdate({ preferred_story_styles: updatedStyles });
  };

  const handleCustomStyleAdd = () => {
    if (customStyle.trim() && !settings.preferred_story_styles.includes(customStyle.trim())) {
      onUpdate({
        preferred_story_styles: [...settings.preferred_story_styles, customStyle.trim()]
      });
      setCustomStyle('');
      setShowCustomStyleInput(false);
    }
  };

  const handleThemesChange = (type: 'comfort_themes' | 'avoid_themes', value: string) => {
    const themes = value.split(',').map(theme => theme.trim()).filter(theme => theme.length > 0);
    onUpdate({ [type]: themes });
  };

  const getIntensityDescription = (level: string) => {
    switch (level) {
      case 'gentle':
        return 'Calm, supportive adventures with minimal challenge. Perfect for relaxation and gentle growth.';
      case 'balanced':
        return 'Moderate adventures with balanced challenge and support. Good for steady personal development.';
      case 'challenging':
        return 'Intensive adventures with meaningful challenges. Ideal for significant personal growth and change.';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-8">
      {/* UI Mode Toggle */}
      <FullUIModeToggle />

      {/* Story Intensity Settings */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {isEntertainmentMode() ? 'Adventure Intensity' : 'Therapeutic Intensity'}
        </h3>
        <p className="text-sm text-gray-600 mb-6">
          Choose how challenging and intensive you'd like your story experiences to be.
        </p>

        <div className="space-y-4">
          {(['gentle', 'balanced', 'challenging'] as const).map((level) => (
            <label key={level} className="flex items-start space-x-3 cursor-pointer">
              <input
                type="radio"
                name="story_intensity"
                value={level}
                checked={settings.story_intensity === level}
                onChange={() => handleIntensityChange(level)}
                className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
              />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-900 capitalize">{level}</span>
                  {level === 'gentle' && <span className="text-green-500">🌱</span>}
                  {level === 'balanced' && <span className="text-blue-500">⚖️</span>}
                  {level === 'challenging' && <span className="text-orange-500">🔥</span>}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {getIntensityDescription(level)}
                </p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Story Styles */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Preferred Story Styles
        </h3>
        <p className="text-sm text-gray-600 mb-6">
          Select the types of adventures and story approaches that appeal to you most.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {storyStyles.map((style) => (
            <label key={style.id} className="flex items-start space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.preferred_story_styles.includes(style.id)}
                onChange={() => handleStyleToggle(style.id)}
                className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{style.icon}</span>
                  <span className="font-medium text-gray-900">{style.name}</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{style.description}</p>
              </div>
            </label>
          ))}
        </div>

        {/* Custom Style Input */}
        {showCustomStyleInput ? (
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={customStyle}
              onChange={(e) => setCustomStyle(e.target.value)}
              placeholder="Enter custom story style..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <button
              onClick={handleCustomStyleAdd}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              Add
            </button>
            <button
              onClick={() => {
                setShowCustomStyleInput(false);
                setCustomStyle('');
              }}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowCustomStyleInput(true)}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            + Add Custom Story Style
          </button>
        )}
      </div>

      {/* Theme Preferences */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Story Theme Preferences
        </h3>
        <p className="text-sm text-gray-600 mb-6">
          Help us personalize your adventures by telling us what themes you enjoy and what you'd prefer to avoid.
        </p>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Favorite Themes
            </label>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              rows={3}
              placeholder="e.g., nature, friendship, creativity, adventure, mystery..."
              value={settings.comfort_themes.join(', ')}
              onChange={(e) => handleThemesChange('comfort_themes', e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              Separate themes with commas. These will be emphasized in your adventures.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Themes to Avoid
            </label>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              rows={3}
              placeholder="e.g., violence, loss, conflict, medical themes..."
              value={settings.avoid_themes.join(', ')}
              onChange={(e) => handleThemesChange('avoid_themes', e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              Separate themes with commas. We'll avoid including these in your adventures.
            </p>
          </div>
        </div>
      </div>

      {/* Emergency Support */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-red-900 mb-4">
          Emergency Support
        </h3>
        <p className="text-sm text-red-700 mb-4">
          If you ever need immediate help during your adventures, we want to make sure you have the support you need.
        </p>

        <div className="bg-white rounded-md p-4 border border-red-200">
          <p className="text-sm text-gray-600 mb-2">
            <strong>Crisis Support:</strong> If you're in immediate danger or having thoughts of self-harm,
            please contact emergency services (911) or a crisis hotline immediately.
          </p>
          <p className="text-sm text-gray-600">
            <strong>24/7 Crisis Text Line:</strong> Text HOME to 741741
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdventureSettingsSection;
