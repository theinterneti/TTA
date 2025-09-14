import React, { useState } from 'react';

interface TherapeuticSettings {
  intensity_level: 'LOW' | 'MEDIUM' | 'HIGH';
  preferred_approaches: string[];
  trigger_warnings: string[];
  comfort_topics: string[];
  avoid_topics: string[];
  crisis_contact_info?: {
    emergency_contact: string;
    therapist_contact?: string;
    preferred_crisis_resources: string[];
  };
}

interface TherapeuticSettingsSectionProps {
  settings: TherapeuticSettings;
  onUpdate: (updates: Partial<TherapeuticSettings>) => void;
}

const TherapeuticSettingsSection: React.FC<TherapeuticSettingsSectionProps> = ({
  settings,
  onUpdate,
}) => {
  const [customApproach, setCustomApproach] = useState('');
  const [showCustomApproachInput, setShowCustomApproachInput] = useState(false);

  const therapeuticApproaches = [
    'Cognitive Behavioral Therapy (CBT)',
    'Mindfulness-Based Therapy',
    'Narrative Therapy',
    'Solution-Focused Brief Therapy',
    'Acceptance & Commitment Therapy',
    'Dialectical Behavior Therapy',
    'Humanistic Therapy',
    'Psychodynamic Therapy',
  ];

  const handleIntensityChange = (intensity: 'LOW' | 'MEDIUM' | 'HIGH') => {
    onUpdate({ intensity_level: intensity });
  };

  const handleApproachToggle = (approach: string) => {
    const updatedApproaches = settings.preferred_approaches.includes(approach)
      ? settings.preferred_approaches.filter(a => a !== approach)
      : [...settings.preferred_approaches, approach];

    onUpdate({ preferred_approaches: updatedApproaches });
  };

  const handleAddCustomApproach = () => {
    if (customApproach.trim() && !settings.preferred_approaches.includes(customApproach.trim())) {
      onUpdate({
        preferred_approaches: [...settings.preferred_approaches, customApproach.trim()]
      });
      setCustomApproach('');
      setShowCustomApproachInput(false);
    }
  };

  const handleTopicsChange = (type: 'trigger_warnings' | 'comfort_topics' | 'avoid_topics', value: string) => {
    const topics = value.split(',').map(topic => topic.trim()).filter(topic => topic.length > 0);
    onUpdate({ [type]: topics });
  };

  const getIntensityDescription = (level: string) => {
    switch (level) {
      case 'LOW':
        return 'Gentle guidance with minimal therapeutic intervention. Focus on comfort and gradual progress.';
      case 'MEDIUM':
        return 'Balanced therapeutic approach with moderate intervention and structured support.';
      case 'HIGH':
        return 'Intensive therapeutic work with frequent interventions and deep exploration.';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Therapeutic Preferences</h3>
        <p className="text-gray-600 mb-6">
          Customize your therapeutic experience to match your comfort level and goals.
        </p>
      </div>

      {/* Therapeutic Intensity */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">
          Therapeutic Intensity Level
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(['LOW', 'MEDIUM', 'HIGH'] as const).map((level) => (
            <button
              key={level}
              onClick={() => handleIntensityChange(level)}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                settings.intensity_level === level
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <div className="font-medium text-lg mb-2">{level}</div>
              <div className="text-sm text-gray-600">
                {getIntensityDescription(level)}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Preferred Therapeutic Approaches */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">
          Preferred Therapeutic Approaches
        </label>
        <p className="text-sm text-gray-600 mb-4">
          Select the therapeutic approaches that resonate with you. You can choose multiple options.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {therapeuticApproaches.map((approach) => (
            <label key={approach} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50">
              <input
                type="checkbox"
                className="mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                checked={settings.preferred_approaches.includes(approach)}
                onChange={() => handleApproachToggle(approach)}
              />
              <div className="flex-1">
                <span className="text-sm font-medium text-gray-900">{approach}</span>
              </div>
            </label>
          ))}
        </div>

        {/* Custom Approaches */}
        <div className="mt-4">
          {settings.preferred_approaches
            .filter(approach => !therapeuticApproaches.includes(approach))
            .map((customApproach) => (
              <div key={customApproach} className="flex items-center justify-between p-2 bg-blue-50 rounded-lg mb-2">
                <span className="text-sm text-blue-900">{customApproach}</span>
                <button
                  onClick={() => handleApproachToggle(customApproach)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}

          {showCustomApproachInput ? (
            <div className="flex space-x-2 mt-2">
              <input
                type="text"
                value={customApproach}
                onChange={(e) => setCustomApproach(e.target.value)}
                placeholder="Enter custom therapeutic approach..."
                className="input-field flex-1"
                onKeyPress={(e) => e.key === 'Enter' && handleAddCustomApproach()}
              />
              <button
                onClick={handleAddCustomApproach}
                className="btn-primary text-sm px-3 py-2"
              >
                Add
              </button>
              <button
                onClick={() => {
                  setShowCustomApproachInput(false);
                  setCustomApproach('');
                }}
                className="btn-secondary text-sm px-3 py-2"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowCustomApproachInput(true)}
              className="text-sm text-primary-600 hover:text-primary-700 flex items-center mt-2"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add custom approach
            </button>
          )}
        </div>
      </div>

      {/* Trigger Warnings */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Trigger Warnings & Sensitive Topics
        </label>
        <p className="text-sm text-gray-600 mb-3">
          List topics that might be triggering or uncomfortable for you. Separate multiple topics with commas.
        </p>
        <textarea
          className="input-field"
          rows={3}
          placeholder="e.g., violence, loss, relationship conflicts, family issues..."
          value={settings.trigger_warnings.join(', ')}
          onChange={(e) => handleTopicsChange('trigger_warnings', e.target.value)}
        />
      </div>

      {/* Comfort Topics */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Comfort Topics & Interests
        </label>
        <p className="text-sm text-gray-600 mb-3">
          List topics that make you feel comfortable or that you enjoy discussing. These can be incorporated into your therapeutic experience.
        </p>
        <textarea
          className="input-field"
          rows={3}
          placeholder="e.g., nature, creativity, music, personal growth, mindfulness..."
          value={settings.comfort_topics.join(', ')}
          onChange={(e) => handleTopicsChange('comfort_topics', e.target.value)}
        />
      </div>

      {/* Topics to Avoid */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Topics to Avoid
        </label>
        <p className="text-sm text-gray-600 mb-3">
          List any topics you'd prefer to avoid entirely in your therapeutic sessions.
        </p>
        <textarea
          className="input-field"
          rows={3}
          placeholder="e.g., specific phobias, past trauma, certain life events..."
          value={settings.avoid_topics.join(', ')}
          onChange={(e) => handleTopicsChange('avoid_topics', e.target.value)}
        />
      </div>

      {/* Therapeutic Goals */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">💡 Therapeutic Goals Tip</h4>
        <p className="text-blue-800 text-sm">
          Your therapeutic preferences will be used to personalize your experience and match you with appropriate worlds and interventions.
          You can update these settings at any time as your needs and comfort level change.
        </p>
      </div>
    </div>
  );
};

export default TherapeuticSettingsSection;
