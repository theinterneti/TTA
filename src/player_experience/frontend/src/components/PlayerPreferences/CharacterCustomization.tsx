import React, { useState } from 'react';
import { PreferredSetting, SETTING_DESCRIPTIONS } from '../../types/preferences';

interface CharacterCustomizationProps {
  characterName: string;
  preferredSetting: PreferredSetting;
  onChange: (updates: { character_name?: string; preferred_setting?: PreferredSetting }) => void;
}

const CharacterCustomization: React.FC<CharacterCustomizationProps> = ({
  characterName,
  preferredSetting,
  onChange,
}) => {
  const [customName, setCustomName] = useState(characterName);
  const [previewSetting, setPreviewSetting] = useState<PreferredSetting | null>(null);

  const handleNameChange = (name: string) => {
    setCustomName(name);
    onChange({ character_name: name });
  };

  const handleSettingChange = (setting: PreferredSetting) => {
    onChange({ preferred_setting: setting });
  };

  const suggestedNames = [
    'Alex', 'Jordan', 'Casey', 'Riley', 'Sage', 'River', 'Phoenix', 'Rowan',
    'Avery', 'Quinn', 'Emery', 'Skyler', 'Cameron', 'Morgan', 'Reese', 'Blake'
  ];

  const settings = [
    {
      id: PreferredSetting.PEACEFUL_FOREST,
      name: 'Peaceful Forest',
      icon: '🌲',
      image: '🌲🌿🦋',
      atmosphere: 'Serene and grounding',
      benefits: ['Natural calm', 'Grounding energy', 'Fresh perspective'],
      sounds: 'Gentle rustling leaves, distant bird songs'
    },
    {
      id: PreferredSetting.MOUNTAIN_RETREAT,
      name: 'Mountain Retreat',
      icon: '⛰️',
      image: '⛰️☁️🏔️',
      atmosphere: 'Expansive and inspiring',
      benefits: ['Clarity of thought', 'Sense of perspective', 'Inner strength'],
      sounds: 'Gentle wind, distant echoes, peaceful silence'
    },
    {
      id: PreferredSetting.OCEAN_SANCTUARY,
      name: 'Ocean Sanctuary',
      icon: '🌊',
      image: '🌊🐚🌅',
      atmosphere: 'Rhythmic and cleansing',
      benefits: ['Emotional flow', 'Cleansing energy', 'Rhythmic calm'],
      sounds: 'Gentle waves, seabirds, ocean breeze'
    },
    {
      id: PreferredSetting.URBAN_GARDEN,
      name: 'Urban Garden',
      icon: '🏙️',
      image: '🏙️🌺🦋',
      atmosphere: 'Balanced and accessible',
      benefits: ['Modern comfort', 'Growth mindset', 'Balanced energy'],
      sounds: 'Gentle fountain, distant city hum, nature sounds'
    },
    {
      id: PreferredSetting.COZY_LIBRARY,
      name: 'Cozy Library',
      icon: '📚',
      image: '📚☕🕯️',
      atmosphere: 'Warm and contemplative',
      benefits: ['Deep reflection', 'Intellectual comfort', 'Safe exploration'],
      sounds: 'Soft pages turning, gentle fire crackling, quiet ambiance'
    },
    {
      id: PreferredSetting.STARLIT_MEADOW,
      name: 'Starlit Meadow',
      icon: '✨',
      image: '✨🌙🌾',
      atmosphere: 'Mystical and expansive',
      benefits: ['Wonder and awe', 'Infinite possibilities', 'Peaceful reflection'],
      sounds: 'Gentle night breeze, distant owl calls, rustling grass'
    },
    {
      id: PreferredSetting.QUIET_GARDEN,
      name: 'Quiet Garden',
      icon: '🌸',
      image: '🌸🦋🌿',
      atmosphere: 'Intimate and nurturing',
      benefits: ['Personal growth', 'Gentle healing', 'Safe intimacy'],
      sounds: 'Soft breeze, gentle water feature, bird songs'
    },
    {
      id: PreferredSetting.FOREST_CLEARING,
      name: 'Forest Clearing',
      icon: '🌳',
      image: '🌳☀️🌼',
      atmosphere: 'Open and protected',
      benefits: ['Clarity and openness', 'Protected space', 'Natural wisdom'],
      sounds: 'Gentle breeze through trees, distant forest sounds, peaceful quiet'
    }
  ];

  const currentSetting = settings.find(s => s.id === (previewSetting || preferredSetting));

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Character & Setting Customization
        </h3>
        <p className="text-gray-600 mb-6">
          Personalize your therapeutic companion and choose the environment where your 
          conversations will take place. These choices help create a more immersive and 
          comfortable experience.
        </p>
      </div>

      {/* Character Name Section */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-gray-900">Character Name</h4>
        <p className="text-gray-600 text-sm">
          Choose a name for your therapeutic companion. This creates a more personal connection 
          and helps you feel more comfortable during conversations.
        </p>
        
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Character Name
            </label>
            <input
              type="text"
              value={customName}
              onChange={(e) => handleNameChange(e.target.value)}
              placeholder="Enter a name for your companion..."
              className="input-field max-w-md"
            />
          </div>

          {/* Suggested Names */}
          <div>
            <p className="text-sm text-gray-600 mb-2">Suggested names:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedNames.map((name) => (
                <button
                  key={name}
                  onClick={() => handleNameChange(name)}
                  className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                    customName === name
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Setting Selection */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-gray-900">Preferred Setting</h4>
        <p className="text-gray-600 text-sm">
          Choose the environment where you'd like your therapeutic conversations to take place. 
          Different settings can evoke different feelings and support various types of work.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {settings.map((setting) => (
            <button
              key={setting.id}
              onClick={() => handleSettingChange(setting.id)}
              onMouseEnter={() => setPreviewSetting(setting.id)}
              onMouseLeave={() => setPreviewSetting(null)}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                preferredSetting === setting.id
                  ? 'border-primary-500 bg-primary-50'
                  : previewSetting === setting.id
                  ? 'border-gray-300 bg-gray-50 ring-2 ring-gray-200'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center mb-2">
                <span className="text-2xl mr-2">{setting.icon}</span>
                <h5 className="font-semibold text-gray-900">{setting.name}</h5>
              </div>
              
              <div className="text-2xl mb-2">{setting.image}</div>
              
              <p className="text-sm text-gray-600 mb-2">{setting.atmosphere}</p>
              
              <div className="space-y-2">
                <div>
                  <p className="text-xs font-medium text-gray-700">Benefits:</p>
                  <div className="flex flex-wrap gap-1">
                    {setting.benefits.map((benefit, index) => (
                      <span
                        key={index}
                        className="inline-block px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full"
                      >
                        {benefit}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {preferredSetting === setting.id && (
                <div className="mt-3 pt-3 border-t border-primary-200">
                  <div className="flex items-center text-sm font-medium text-primary-700">
                    <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Selected
                  </div>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Setting Preview */}
      {currentSetting && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
          <h4 className="font-semibold text-gray-900 mb-3">Setting Preview</h4>
          <div className="flex items-start space-x-4">
            <div className="text-4xl">{currentSetting.image}</div>
            <div className="flex-1">
              <h5 className="font-medium text-gray-900 mb-1">{currentSetting.name}</h5>
              <p className="text-gray-700 mb-2">{SETTING_DESCRIPTIONS[currentSetting.id]}</p>
              <div className="text-sm text-gray-600">
                <p><strong>Atmosphere:</strong> {currentSetting.atmosphere}</p>
                <p><strong>Ambient sounds:</strong> {currentSetting.sounds}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Character Preview */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h4 className="font-semibold text-gray-900 mb-3">Your Therapeutic Companion</h4>
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-2xl">🤗</span>
          </div>
          <div>
            <h5 className="font-medium text-gray-900 text-lg">{customName || 'Your Companion'}</h5>
            <p className="text-gray-600">
              Your therapeutic guide in the {currentSetting?.name.toLowerCase() || 'chosen setting'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              "I'm here to support you on your journey of growth and healing."
            </p>
          </div>
        </div>
      </div>

      {/* Customization Tips */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-amber-400 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h4 className="font-medium text-amber-900 mb-1">💡 Customization Tips</h4>
            <div className="text-amber-800 text-sm space-y-1">
              <p>• <strong>Choose a name that feels comfortable</strong> - it can be gender-neutral or meaningful to you</p>
              <p>• <strong>Pick a setting that resonates</strong> - different environments support different types of work</p>
              <p>• <strong>Consider your mood</strong> - you might prefer calming settings during stressful times</p>
              <p>• <strong>Experiment and change</strong> - you can update these preferences anytime</p>
            </div>
          </div>
        </div>
      </div>

      {/* Setting Categories */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-3">Setting Categories</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <h5 className="font-medium text-blue-800 mb-1">🌲 Nature</h5>
            <p className="text-blue-700 text-xs">Forest, Mountain, Ocean, Meadow</p>
          </div>
          <div>
            <h5 className="font-medium text-blue-800 mb-1">🏙️ Urban</h5>
            <p className="text-blue-700 text-xs">Garden, Library</p>
          </div>
          <div>
            <h5 className="font-medium text-blue-800 mb-1">🌸 Intimate</h5>
            <p className="text-blue-700 text-xs">Quiet Garden, Cozy Library</p>
          </div>
          <div>
            <h5 className="font-medium text-blue-800 mb-1">✨ Expansive</h5>
            <p className="text-blue-700 text-xs">Mountain, Starlit Meadow, Ocean</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CharacterCustomization;
