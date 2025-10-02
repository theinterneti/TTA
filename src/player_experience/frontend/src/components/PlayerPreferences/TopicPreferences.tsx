import React, { useState } from 'react';
import { COMFORT_TOPICS, ComfortTopic } from '../../types/preferences';

interface TopicPreferencesProps {
  comfortTopics: string[];
  triggerTopics: string[];
  avoidTopics: string[];
  onChange: (updates: {
    comfort_topics?: string[];
    trigger_topics?: string[];
    avoid_topics?: string[];
  }) => void;
}

const TopicPreferences: React.FC<TopicPreferencesProps> = ({
  comfortTopics,
  triggerTopics,
  avoidTopics,
  onChange,
}) => {
  const [activeTab, setActiveTab] = useState<'comfort' | 'trigger' | 'avoid'>('comfort');
  const [customTopic, setCustomTopic] = useState('');

  const comfortTopicCategories = {
    'Nature & Environment': [
      { id: 'nature', label: 'Nature & Outdoors', icon: '🌿', description: 'Trees, animals, natural settings' },
      { id: 'animals', label: 'Animals', icon: '🐾', description: 'Pets, wildlife, animal stories' },
    ],
    'Creative Expression': [
      { id: 'creativity', label: 'Creativity', icon: '🎨', description: 'Art, writing, creative projects' },
      { id: 'music', label: 'Music', icon: '🎵', description: 'Songs, instruments, musical experiences' },
      { id: 'art', label: 'Art', icon: '🖼️', description: 'Visual arts, galleries, artistic expression' },
    ],
    'Learning & Growth': [
      { id: 'reading', label: 'Reading & Books', icon: '📚', description: 'Literature, learning, knowledge' },
      { id: 'learning', label: 'Learning', icon: '🧠', description: 'New skills, education, discovery' },
      { id: 'personal_growth', label: 'Personal Growth', icon: '🌱', description: 'Self-improvement, development' },
    ],
    'Wellness & Mindfulness': [
      { id: 'meditation', label: 'Meditation', icon: '🧘', description: 'Mindfulness, quiet reflection' },
      { id: 'breathing_exercises', label: 'Breathing', icon: '💨', description: 'Breathing techniques, relaxation' },
      { id: 'movement', label: 'Movement', icon: '🤸', description: 'Exercise, dance, physical activity' },
    ],
    'Relationships & Connection': [
      { id: 'family', label: 'Family', icon: '👨‍👩‍👧‍👦', description: 'Family relationships, connections' },
      { id: 'friendship', label: 'Friendship', icon: '👫', description: 'Friends, social connections' },
    ],
    'Life & Experiences': [
      { id: 'achievement', label: 'Achievement', icon: '🏆', description: 'Accomplishments, success stories' },
      { id: 'hobbies', label: 'Hobbies', icon: '🎯', description: 'Personal interests, pastimes' },
      { id: 'travel', label: 'Travel', icon: '✈️', description: 'Places, adventures, exploration' },
      { id: 'spirituality', label: 'Spirituality', icon: '🕯️', description: 'Spiritual practices, meaning' },
    ]
  };

  const commonTriggerTopics = [
    'Violence or aggression', 'Death or loss', 'Relationship conflicts', 'Family dysfunction',
    'Financial stress', 'Health issues', 'Trauma or abuse', 'Criticism or judgment',
    'Abandonment or rejection', 'Failure or mistakes', 'Body image issues', 'Substance use',
    'Work stress', 'Academic pressure', 'Social anxiety situations', 'Perfectionism'
  ];

  const commonAvoidTopics = [
    'Politics', 'Religion (specific)', 'Graphic violence', 'Sexual content',
    'Substance abuse details', 'Self-harm methods', 'Suicide methods', 'Eating disorder behaviors',
    'Specific phobias', 'Past trauma details', 'Medical procedures', 'Financial details',
    'Legal issues', 'Relationship breakups', 'Death of loved ones', 'Childhood abuse'
  ];

  const handleComfortTopicToggle = (topic: string) => {
    const updated = comfortTopics.includes(topic)
      ? comfortTopics.filter(t => t !== topic)
      : [...comfortTopics, topic];
    onChange({ comfort_topics: updated });
  };

  const handleTriggerTopicToggle = (topic: string) => {
    const updated = triggerTopics.includes(topic)
      ? triggerTopics.filter(t => t !== topic)
      : [...triggerTopics, topic];
    onChange({ trigger_topics: updated });
  };

  const handleAvoidTopicToggle = (topic: string) => {
    const updated = avoidTopics.includes(topic)
      ? avoidTopics.filter(t => t !== topic)
      : [...avoidTopics, topic];
    onChange({ avoid_topics: updated });
  };

  const addCustomTopic = () => {
    if (!customTopic.trim()) return;

    const topic = customTopic.trim();
    
    if (activeTab === 'comfort' && !comfortTopics.includes(topic)) {
      onChange({ comfort_topics: [...comfortTopics, topic] });
    } else if (activeTab === 'trigger' && !triggerTopics.includes(topic)) {
      onChange({ trigger_topics: [...triggerTopics, topic] });
    } else if (activeTab === 'avoid' && !avoidTopics.includes(topic)) {
      onChange({ avoid_topics: [...avoidTopics, topic] });
    }
    
    setCustomTopic('');
  };

  const removeCustomTopic = (topic: string, type: 'comfort' | 'trigger' | 'avoid') => {
    if (type === 'comfort') {
      onChange({ comfort_topics: comfortTopics.filter(t => t !== topic) });
    } else if (type === 'trigger') {
      onChange({ trigger_topics: triggerTopics.filter(t => t !== topic) });
    } else if (type === 'avoid') {
      onChange({ avoid_topics: avoidTopics.filter(t => t !== topic) });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Topic Preferences
        </h3>
        <p className="text-gray-600 mb-6">
          Help personalize your experience by indicating topics that make you comfortable, 
          topics that might be triggering, and topics you'd prefer to avoid entirely.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('comfort')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'comfort'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            🌟 Comfort Topics ({comfortTopics.length})
          </button>
          <button
            onClick={() => setActiveTab('trigger')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'trigger'
                ? 'border-amber-500 text-amber-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            ⚠️ Trigger Topics ({triggerTopics.length})
          </button>
          <button
            onClick={() => setActiveTab('avoid')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'avoid'
                ? 'border-red-500 text-red-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            🚫 Avoid Topics ({avoidTopics.length})
          </button>
        </nav>
      </div>

      {/* Comfort Topics Tab */}
      {activeTab === 'comfort' && (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-medium text-green-900 mb-2">🌟 Comfort Topics</h4>
            <p className="text-green-800 text-sm">
              These topics make you feel comfortable, safe, and positive. They can be incorporated 
              into your therapeutic conversations to create a supportive atmosphere.
            </p>
          </div>

          {Object.entries(comfortTopicCategories).map(([category, topics]) => (
            <div key={category} className="space-y-3">
              <h5 className="font-semibold text-gray-900">{category}</h5>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {topics.map((topic) => (
                  <label
                    key={topic.id}
                    className={`flex items-start space-x-3 p-3 rounded-lg border cursor-pointer transition-all ${
                      comfortTopics.includes(topic.id)
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <input
                      type="checkbox"
                      className="mt-1 rounded border-gray-300 text-green-600 focus:ring-green-500"
                      checked={comfortTopics.includes(topic.id)}
                      onChange={() => handleComfortTopicToggle(topic.id)}
                    />
                    <div className="flex-1">
                      <div className="flex items-center mb-1">
                        <span className="text-lg mr-2">{topic.icon}</span>
                        <span className="font-medium text-gray-900">{topic.label}</span>
                      </div>
                      <p className="text-sm text-gray-600">{topic.description}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Trigger Topics Tab */}
      {activeTab === 'trigger' && (
        <div className="space-y-6">
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <h4 className="font-medium text-amber-900 mb-2">⚠️ Trigger Topics</h4>
            <p className="text-amber-800 text-sm">
              These topics might cause emotional distress or discomfort. The AI will approach 
              these areas with extra care and sensitivity, or avoid them if you prefer.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {commonTriggerTopics.map((topic) => (
              <label
                key={topic}
                className={`flex items-center space-x-3 p-3 rounded-lg border cursor-pointer transition-all ${
                  triggerTopics.includes(topic)
                    ? 'border-amber-500 bg-amber-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-amber-600 focus:ring-amber-500"
                  checked={triggerTopics.includes(topic)}
                  onChange={() => handleTriggerTopicToggle(topic)}
                />
                <span className="text-sm text-gray-900">{topic}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Avoid Topics Tab */}
      {activeTab === 'avoid' && (
        <div className="space-y-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="font-medium text-red-900 mb-2">🚫 Topics to Avoid</h4>
            <p className="text-red-800 text-sm">
              These topics will be completely avoided in your therapeutic conversations. 
              The AI will not bring up these subjects or explore them.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {commonAvoidTopics.map((topic) => (
              <label
                key={topic}
                className={`flex items-center space-x-3 p-3 rounded-lg border cursor-pointer transition-all ${
                  avoidTopics.includes(topic)
                    ? 'border-red-500 bg-red-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                  checked={avoidTopics.includes(topic)}
                  onChange={() => handleAvoidTopicToggle(topic)}
                />
                <span className="text-sm text-gray-900">{topic}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Custom Topics Section */}
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900">
          Add Custom {activeTab === 'comfort' ? 'Comfort' : activeTab === 'trigger' ? 'Trigger' : 'Avoid'} Topic
        </h4>
        
        {/* Display custom topics */}
        {activeTab === 'comfort' && 
          comfortTopics.filter(topic => !COMFORT_TOPICS.includes(topic as ComfortTopic)).map((topic) => (
            <div key={topic} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="text-green-900">{topic}</span>
              <button
                onClick={() => removeCustomTopic(topic, 'comfort')}
                className="text-green-600 hover:text-green-800"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))
        }

        {activeTab === 'trigger' && 
          triggerTopics.filter(topic => !commonTriggerTopics.includes(topic)).map((topic) => (
            <div key={topic} className="flex items-center justify-between p-3 bg-amber-50 rounded-lg">
              <span className="text-amber-900">{topic}</span>
              <button
                onClick={() => removeCustomTopic(topic, 'trigger')}
                className="text-amber-600 hover:text-amber-800"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))
        }

        {activeTab === 'avoid' && 
          avoidTopics.filter(topic => !commonAvoidTopics.includes(topic)).map((topic) => (
            <div key={topic} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
              <span className="text-red-900">{topic}</span>
              <button
                onClick={() => removeCustomTopic(topic, 'avoid')}
                className="text-red-600 hover:text-red-800"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))
        }

        {/* Add custom topic input */}
        <div className="flex space-x-2">
          <input
            type="text"
            value={customTopic}
            onChange={(e) => setCustomTopic(e.target.value)}
            placeholder={`Add a custom ${activeTab} topic...`}
            className="input-field flex-1"
            onKeyPress={(e) => e.key === 'Enter' && addCustomTopic()}
          />
          <button
            onClick={addCustomTopic}
            className="btn-primary text-sm px-4"
          >
            Add
          </button>
        </div>
      </div>

      {/* Summary */}
      {(comfortTopics.length > 0 || triggerTopics.length > 0 || avoidTopics.length > 0) && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Topic Preferences Summary</h4>
          
          {comfortTopics.length > 0 && (
            <div className="mb-3">
              <h5 className="text-sm font-medium text-green-800 mb-2">
                🌟 Comfort Topics ({comfortTopics.length}):
              </h5>
              <div className="flex flex-wrap gap-1">
                {comfortTopics.slice(0, 8).map((topic) => (
                  <span
                    key={topic}
                    className="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full"
                  >
                    {topic.replace(/_/g, ' ')}
                  </span>
                ))}
                {comfortTopics.length > 8 && (
                  <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                    +{comfortTopics.length - 8} more
                  </span>
                )}
              </div>
            </div>
          )}

          {triggerTopics.length > 0 && (
            <div className="mb-3">
              <h5 className="text-sm font-medium text-amber-800 mb-2">
                ⚠️ Trigger Topics ({triggerTopics.length}):
              </h5>
              <div className="flex flex-wrap gap-1">
                {triggerTopics.slice(0, 6).map((topic) => (
                  <span
                    key={topic}
                    className="inline-block px-2 py-1 text-xs bg-amber-100 text-amber-800 rounded-full"
                  >
                    {topic}
                  </span>
                ))}
                {triggerTopics.length > 6 && (
                  <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                    +{triggerTopics.length - 6} more
                  </span>
                )}
              </div>
            </div>
          )}

          {avoidTopics.length > 0 && (
            <div>
              <h5 className="text-sm font-medium text-red-800 mb-2">
                🚫 Avoid Topics ({avoidTopics.length}):
              </h5>
              <div className="flex flex-wrap gap-1">
                {avoidTopics.slice(0, 6).map((topic) => (
                  <span
                    key={topic}
                    className="inline-block px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full"
                  >
                    {topic}
                  </span>
                ))}
                {avoidTopics.length > 6 && (
                  <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                    +{avoidTopics.length - 6} more
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Guidance */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-400 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h4 className="font-medium text-blue-900 mb-1">💡 Topic Preference Tips</h4>
            <div className="text-blue-800 text-sm space-y-1">
              <p>• <strong>Be specific</strong> - detailed preferences help create better experiences</p>
              <p>• <strong>It's okay to change</strong> - your comfort levels may evolve over time</p>
              <p>• <strong>Trust your instincts</strong> - if something doesn't feel right, add it to avoid topics</p>
              <p>• <strong>Balance is key</strong> - having some comfort topics helps create positive experiences</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopicPreferences;
