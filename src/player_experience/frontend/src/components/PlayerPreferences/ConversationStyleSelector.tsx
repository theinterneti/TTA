import React, { useState } from 'react';
import { ConversationStyle, CONVERSATION_STYLE_DESCRIPTIONS } from '../../types/preferences';

interface ConversationStyleSelectorProps {
  value: ConversationStyle;
  onChange: (style: ConversationStyle) => void;
}

const ConversationStyleSelector: React.FC<ConversationStyleSelectorProps> = ({
  value,
  onChange,
}) => {
  const [previewStyle, setPreviewStyle] = useState<ConversationStyle | null>(null);

  const conversationStyles = [
    {
      style: ConversationStyle.GENTLE,
      title: 'Gentle',
      icon: '🌸',
      color: 'pink',
      characteristics: [
        'Soft, nurturing tone',
        'Patient and understanding',
        'Emphasizes comfort and safety',
        'Avoids confrontation',
        'Focuses on self-compassion'
      ],
      sampleResponse: "I can sense that you're feeling overwhelmed right now, and that's completely understandable. Let's take this one step at a time, at whatever pace feels comfortable for you. You're doing the best you can, and that's enough.",
      bestFor: ['High sensitivity', 'Trauma recovery', 'Anxiety', 'First-time therapy']
    },
    {
      style: ConversationStyle.DIRECT,
      title: 'Direct',
      icon: '🎯',
      color: 'blue',
      characteristics: [
        'Clear, straightforward communication',
        'Honest feedback and observations',
        'Goal-oriented approach',
        'Challenges unhelpful patterns',
        'Focuses on practical solutions'
      ],
      sampleResponse: "I notice you're using a lot of 'should' statements about yourself. Let's examine whether these expectations are realistic and helpful, or if they're actually creating more stress in your life.",
      bestFor: ['Goal achievement', 'Breaking patterns', 'Time-limited work', 'Practical problem-solving']
    },
    {
      style: ConversationStyle.EXPLORATORY,
      title: 'Exploratory',
      icon: '🔍',
      color: 'purple',
      characteristics: [
        'Curious and open-ended questions',
        'Encourages self-discovery',
        'Values the journey over destination',
        'Explores multiple perspectives',
        'Embraces uncertainty and growth'
      ],
      sampleResponse: "That's an interesting observation about yourself. I'm curious - what do you think might be underneath that feeling? What would it be like to explore this from a different angle?",
      bestFor: ['Self-discovery', 'Creative problem-solving', 'Personal growth', 'Complex issues']
    },
    {
      style: ConversationStyle.SUPPORTIVE,
      title: 'Supportive',
      icon: '🤗',
      color: 'green',
      characteristics: [
        'Encouraging and validating',
        'Celebrates progress and strengths',
        'Provides emotional support',
        'Builds confidence and self-esteem',
        'Focuses on positive reinforcement'
      ],
      sampleResponse: "You've shown incredible strength in sharing that with me. The fact that you're here, working on yourself, shows real courage. Let's build on this progress and celebrate how far you've already come.",
      bestFor: ['Low self-esteem', 'Depression', 'Building confidence', 'Motivation challenges']
    }
  ];

  const getColorClasses = (color: string, isSelected: boolean, isPreview: boolean = false) => {
    const baseClasses = 'border-2 transition-all duration-200';

    if (isSelected) {
      switch (color) {
        case 'pink':
          return `${baseClasses} border-pink-500 bg-pink-50 text-pink-700`;
        case 'blue':
          return `${baseClasses} border-blue-500 bg-blue-50 text-blue-700`;
        case 'purple':
          return `${baseClasses} border-purple-500 bg-purple-50 text-purple-700`;
        case 'green':
          return `${baseClasses} border-green-500 bg-green-50 text-green-700`;
        default:
          return `${baseClasses} border-gray-500 bg-gray-50 text-gray-700`;
      }
    } else if (isPreview) {
      return `${baseClasses} border-gray-300 bg-gray-50 text-gray-700 ring-2 ring-gray-200`;
    } else {
      return `${baseClasses} border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700`;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Conversation Style
        </h3>
        <p className="text-gray-600 mb-6">
          Choose the communication style that feels most comfortable and effective for you.
          This affects the tone, approach, and manner of interaction in your therapeutic conversations.
        </p>
      </div>

      {/* Style Selection Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {conversationStyles.map((item) => (
          <div
            key={item.style}
            className={`p-6 rounded-xl cursor-pointer ${getColorClasses(
              item.color,
              value === item.style,
              previewStyle === item.style
            )}`}
            onClick={() => onChange(item.style)}
            onMouseEnter={() => setPreviewStyle(item.style)}
            onMouseLeave={() => setPreviewStyle(null)}
          >
            <div className="flex items-center mb-4">
              <span className="text-3xl mr-3">{item.icon}</span>
              <h4 className="text-lg font-semibold">{item.title}</h4>
            </div>

            <p className="text-sm mb-4 opacity-90">
              {CONVERSATION_STYLE_DESCRIPTIONS[item.style]}
            </p>

            <div className="space-y-3">
              <div>
                <h5 className="font-medium text-sm mb-2">Characteristics:</h5>
                <ul className="text-xs space-y-1">
                  {item.characteristics.map((characteristic, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-current mr-2 mt-0.5">•</span>
                      <span>{characteristic}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h5 className="font-medium text-sm mb-2">Best For:</h5>
                <div className="flex flex-wrap gap-1">
                  {item.bestFor.map((use, index) => (
                    <span
                      key={index}
                      className="inline-block px-2 py-1 text-xs bg-white bg-opacity-60 rounded-full"
                    >
                      {use}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {value === item.style && (
              <div className="mt-4 pt-4 border-t border-current border-opacity-20">
                <div className="flex items-center text-sm font-medium">
                  <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Selected
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Sample Response Preview */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h4 className="font-medium text-gray-900 mb-4">Sample Response Preview</h4>
        <div className="bg-white rounded-lg p-4 border-l-4 border-primary-500">
          <p className="text-sm text-gray-600 mb-2 italic">
            "I've been feeling really stressed about work lately and I don't know how to handle it..."
          </p>
          <div className="border-t pt-3 mt-3">
            <p className="text-sm text-gray-800">
              {conversationStyles.find(s => s.style === (previewStyle || value))?.sampleResponse}
            </p>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Hover over different styles to see how the response changes
        </p>
      </div>

      {/* Style Comparison */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-3">Style Comparison</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <h5 className="font-medium text-blue-800 mb-1">🌸 Gentle</h5>
            <p className="text-blue-700 text-xs">Comfort-focused, patient, nurturing</p>
          </div>
          <div>
            <h5 className="font-medium text-blue-800 mb-1">🎯 Direct</h5>
            <p className="text-blue-700 text-xs">Goal-oriented, honest, practical</p>
          </div>
          <div>
            <h5 className="font-medium text-blue-800 mb-1">🔍 Exploratory</h5>
            <p className="text-blue-700 text-xs">Curious, open-ended, discovery-focused</p>
          </div>
          <div>
            <h5 className="font-medium text-blue-800 mb-1">🤗 Supportive</h5>
            <p className="text-blue-700 text-xs">Encouraging, validating, strength-based</p>
          </div>
        </div>
      </div>

      {/* Current Selection Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Your Selection:</h4>
        <div className="flex items-center">
          <span className="text-2xl mr-3">
            {conversationStyles.find(item => item.style === value)?.icon}
          </span>
          <div>
            <p className="font-medium text-gray-900">
              {conversationStyles.find(item => item.style === value)?.title} Style
            </p>
            <p className="text-sm text-gray-600">
              {CONVERSATION_STYLE_DESCRIPTIONS[value]}
            </p>
          </div>
        </div>
      </div>

      {/* Guidance */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-amber-400 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h4 className="font-medium text-amber-900 mb-1">💡 Choosing Your Style</h4>
            <div className="text-amber-800 text-sm space-y-1">
              <p>• <strong>Trust your instincts</strong> - choose what feels most comfortable initially</p>
              <p>• <strong>Consider your current state</strong> - you might prefer gentler approaches during difficult times</p>
              <p>• <strong>Think about your goals</strong> - direct styles work well for specific objectives</p>
              <p>• <strong>You can change this</strong> anytime as your needs and comfort level evolve</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationStyleSelector;
