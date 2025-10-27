import React from 'react';
import { IntensityLevel, INTENSITY_DESCRIPTIONS } from '../../types/preferences';

interface IntensityLevelSelectorProps {
  value: IntensityLevel;
  onChange: (level: IntensityLevel) => void;
}

const IntensityLevelSelector: React.FC<IntensityLevelSelectorProps> = ({
  value,
  onChange,
}) => {
  const intensityLevels = [
    {
      level: IntensityLevel.LOW,
      title: 'Low Intensity',
      icon: '🌱',
      color: 'green',
      features: [
        'Gentle, non-confrontational approach',
        'Focus on comfort and safety',
        'Gradual progress at your own pace',
        'Minimal therapeutic pressure',
        'Emphasis on self-care and relaxation'
      ]
    },
    {
      level: IntensityLevel.MEDIUM,
      title: 'Medium Intensity',
      icon: '⚖️',
      color: 'blue',
      features: [
        'Balanced therapeutic approach',
        'Moderate intervention and guidance',
        'Structured support with flexibility',
        'Regular check-ins and progress tracking',
        'Mix of comfort and gentle challenges'
      ]
    },
    {
      level: IntensityLevel.HIGH,
      title: 'High Intensity',
      icon: '🔥',
      color: 'orange',
      features: [
        'Intensive therapeutic work',
        'Frequent interventions and feedback',
        'Deep exploration of issues',
        'Challenging questions and exercises',
        'Accelerated progress focus'
      ]
    }
  ];

  const getColorClasses = (color: string, isSelected: boolean) => {
    const baseClasses = 'border-2 transition-all duration-200';

    if (isSelected) {
      switch (color) {
        case 'green':
          return `${baseClasses} border-green-500 bg-green-50 text-green-700`;
        case 'blue':
          return `${baseClasses} border-blue-500 bg-blue-50 text-blue-700`;
        case 'orange':
          return `${baseClasses} border-orange-500 bg-orange-50 text-orange-700`;
        default:
          return `${baseClasses} border-gray-500 bg-gray-50 text-gray-700`;
      }
    } else {
      return `${baseClasses} border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700`;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Therapeutic Intensity Level
        </h3>
        <p className="text-gray-600 mb-6">
          Choose the level of therapeutic intervention that feels most comfortable for you.
          This affects how direct, challenging, and intensive your therapeutic experience will be.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {intensityLevels.map((item) => (
          <button
            key={item.level}
            onClick={() => onChange(item.level)}
            className={`p-6 rounded-xl text-left ${getColorClasses(item.color, value === item.level)}`}
          >
            <div className="flex items-center mb-4">
              <span className="text-3xl mr-3">{item.icon}</span>
              <h4 className="text-lg font-semibold">{item.title}</h4>
            </div>

            <p className="text-sm mb-4 opacity-90">
              {INTENSITY_DESCRIPTIONS[item.level]}
            </p>

            <div className="space-y-2">
              <h5 className="font-medium text-sm">Key Features:</h5>
              <ul className="text-xs space-y-1">
                {item.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-current mr-2 mt-0.5">•</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            {value === item.level && (
              <div className="mt-4 pt-4 border-t border-current border-opacity-20">
                <div className="flex items-center text-sm font-medium">
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

      {/* Additional Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-400 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h4 className="font-medium text-blue-900 mb-1">💡 Choosing Your Intensity Level</h4>
            <div className="text-blue-800 text-sm space-y-2">
              <p>
                <strong>New to therapy?</strong> Start with Low or Medium intensity to build comfort and trust.
              </p>
              <p>
                <strong>Experienced with therapy?</strong> Medium or High intensity may help you progress more quickly.
              </p>
              <p>
                <strong>Feeling overwhelmed?</strong> Low intensity provides a gentle, supportive environment.
              </p>
              <p>
                <strong>Ready for change?</strong> High intensity offers more challenging and transformative work.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Current Selection Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Your Selection:</h4>
        <div className="flex items-center">
          <span className="text-2xl mr-3">
            {intensityLevels.find(item => item.level === value)?.icon}
          </span>
          <div>
            <p className="font-medium text-gray-900">
              {intensityLevels.find(item => item.level === value)?.title}
            </p>
            <p className="text-sm text-gray-600">
              {INTENSITY_DESCRIPTIONS[value]}
            </p>
          </div>
        </div>
      </div>

      {/* Flexibility Note */}
      <div className="text-center text-sm text-gray-500 border-t pt-4">
        <p>
          Don't worry - you can change your intensity level at any time as you become more comfortable
          or as your therapeutic needs evolve.
        </p>
      </div>
    </div>
  );
};

export default IntensityLevelSelector;
