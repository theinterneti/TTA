import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import { createCharacter } from '../../store/slices/characterSlice';
import { IntensityLevel } from '../../types';

interface CharacterCreationData {
  name: string;
  appearance: {
    description: string;
  };
  background: {
    story: string;
    personality_traits: string[];
    goals: string[];
  };
  therapeutic_profile: {
    comfort_level: number;
    preferred_intensity: IntensityLevel;
    therapeutic_goals: string[];
  };
}

interface CharacterCreationFormProps {
  onClose: () => void;
  onSuccess?: () => void;
}

const CharacterCreationForm: React.FC<CharacterCreationFormProps> = ({ onClose, onSuccess }) => {
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const { creationInProgress, error } = useSelector((state: RootState) => state.character);

  const [formData, setFormData] = useState<CharacterCreationData>({
    name: '',
    appearance: {
      description: '',
    },
    background: {
      story: '',
      personality_traits: [],
      goals: [],
    },
    therapeutic_profile: {
      comfort_level: 5,
      preferred_intensity: 'MEDIUM',
      therapeutic_goals: [],
    },
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [currentStep, setCurrentStep] = useState(1);
  const [newTrait, setNewTrait] = useState('');
  const [newGoal, setNewGoal] = useState('');
  const [newTherapeuticGoal, setNewTherapeuticGoal] = useState('');

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 1:
        if (!formData.name.trim()) {
          newErrors.name = 'Character name is required';
        } else if (formData.name.length > 50) {
          newErrors.name = 'Character name must be 50 characters or less';
        }
        if (!formData.appearance.description.trim()) {
          newErrors.appearance = 'Character appearance description is required';
        }
        break;
      case 2:
        if (!formData.background.story.trim()) {
          newErrors.story = 'Character background story is required';
        }
        if (formData.background.personality_traits.length === 0) {
          newErrors.traits = 'At least one personality trait is required';
        }
        if (formData.background.goals.length === 0) {
          newErrors.goals = 'At least one character goal is required';
        }
        break;
      case 3:
        if (formData.therapeutic_profile.therapeutic_goals.length === 0) {
          newErrors.therapeuticGoals = 'At least one therapeutic goal is required';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => {
      const keys = field.split('.');
      if (keys.length === 1) {
        return { ...prev, [field]: value };
      } else if (keys.length === 2) {
        return {
          ...prev,
          [keys[0]]: {
            ...prev[keys[0] as keyof CharacterCreationData],
            [keys[1]]: value,
          },
        };
      }
      return prev;
    });
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const addArrayItem = (field: string, value: string, setter: (value: string) => void) => {
    if (value.trim()) {
      const keys = field.split('.');
      setFormData(prev => ({
        ...prev,
        [keys[0]]: {
          ...prev[keys[0] as keyof CharacterCreationData],
          [keys[1]]: [...(prev[keys[0] as keyof CharacterCreationData] as any)[keys[1]], value.trim()],
        },
      }));
      setter('');
    }
  };

  const removeArrayItem = (field: string, index: number) => {
    const keys = field.split('.');
    setFormData(prev => ({
      ...prev,
      [keys[0]]: {
        ...prev[keys[0] as keyof CharacterCreationData],
        [keys[1]]: (prev[keys[0] as keyof CharacterCreationData] as any)[keys[1]].filter((_: any, i: number) => i !== index),
      },
    }));
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep(3) || !profile?.player_id) return;

    try {
      await dispatch(createCharacter({
        playerId: profile.player_id,
        characterData: formData,
      }) as any).unwrap();
      
      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Failed to create character:', error);
    }
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Character Name *
            </label>
            <input
              type="text"
              className={`input-field ${errors.name ? 'border-red-500' : ''}`}
              placeholder="Enter your character's name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              maxLength={50}
            />
            {errors.name && <p className="text-red-600 text-sm mt-1">{errors.name}</p>}
            <p className="text-gray-500 text-xs mt-1">{formData.name.length}/50 characters</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Appearance Description *
            </label>
            <textarea
              className={`input-field ${errors.appearance ? 'border-red-500' : ''}`}
              rows={4}
              placeholder="Describe your character's appearance, style, and any distinctive features..."
              value={formData.appearance.description}
              onChange={(e) => handleInputChange('appearance.description', e.target.value)}
            />
            {errors.appearance && <p className="text-red-600 text-sm mt-1">{errors.appearance}</p>}
          </div>
        </div>
      </div>

      {/* Character Preview */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Preview</h4>
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-primary-500 rounded-full flex items-center justify-center">
            <span className="text-white text-lg font-bold">
              {formData.name.charAt(0).toUpperCase() || '?'}
            </span>
          </div>
          <div>
            <p className="font-medium text-gray-900">{formData.name || 'Character Name'}</p>
            <p className="text-sm text-gray-600">
              {formData.appearance.description || 'Appearance description will appear here...'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Background & Personality</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Background Story *
            </label>
            <textarea
              className={`input-field ${errors.story ? 'border-red-500' : ''}`}
              rows={4}
              placeholder="Tell your character's story, their past experiences, and what brought them here..."
              value={formData.background.story}
              onChange={(e) => handleInputChange('background.story', e.target.value)}
            />
            {errors.story && <p className="text-red-600 text-sm mt-1">{errors.story}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Personality Traits *
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a personality trait"
                value={newTrait}
                onChange={(e) => setNewTrait(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('background.personality_traits', newTrait, setNewTrait);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('background.personality_traits', newTrait, setNewTrait)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.background.personality_traits.map((trait, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {trait}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('background.personality_traits', index)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            {errors.traits && <p className="text-red-600 text-sm mt-1">{errors.traits}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Character Goals *
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a character goal"
                value={newGoal}
                onChange={(e) => setNewGoal(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('background.goals', newGoal, setNewGoal);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('background.goals', newGoal, setNewGoal)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.background.goals.map((goal, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full"
                >
                  {goal}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('background.goals', index)}
                    className="ml-2 text-green-600 hover:text-green-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            {errors.goals && <p className="text-red-600 text-sm mt-1">{errors.goals}</p>}
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Therapeutic Profile</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Comfort Level (1-10)
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="1"
                max="10"
                className="flex-1"
                value={formData.therapeutic_profile.comfort_level}
                onChange={(e) => handleInputChange('therapeutic_profile.comfort_level', parseInt(e.target.value))}
              />
              <span className="text-lg font-medium text-gray-900 w-8">
                {formData.therapeutic_profile.comfort_level}
              </span>
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Cautious</span>
              <span>Very Comfortable</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred Therapeutic Intensity
            </label>
            <select
              className="input-field"
              value={formData.therapeutic_profile.preferred_intensity}
              onChange={(e) => handleInputChange('therapeutic_profile.preferred_intensity', e.target.value as IntensityLevel)}
            >
              <option value="LOW">Low - Gentle guidance and support</option>
              <option value="MEDIUM">Medium - Balanced therapeutic approach</option>
              <option value="HIGH">High - Intensive therapeutic work</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Therapeutic Goals *
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a therapeutic goal"
                value={newTherapeuticGoal}
                onChange={(e) => setNewTherapeuticGoal(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('therapeutic_profile.therapeutic_goals', newTherapeuticGoal, setNewTherapeuticGoal);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('therapeutic_profile.therapeutic_goals', newTherapeuticGoal, setNewTherapeuticGoal)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.therapeutic_profile.therapeutic_goals.map((goal, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full"
                >
                  {goal}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('therapeutic_profile.therapeutic_goals', index)}
                    className="ml-2 text-purple-600 hover:text-purple-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            {errors.therapeuticGoals && <p className="text-red-600 text-sm mt-1">{errors.therapeuticGoals}</p>}
          </div>
        </div>
      </div>

      {/* Final Preview */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Character Summary</h4>
        <div className="space-y-2 text-sm">
          <p><span className="font-medium">Name:</span> {formData.name}</p>
          <p><span className="font-medium">Comfort Level:</span> {formData.therapeutic_profile.comfort_level}/10</p>
          <p><span className="font-medium">Intensity:</span> {formData.therapeutic_profile.preferred_intensity}</p>
          <p><span className="font-medium">Traits:</span> {formData.background.personality_traits.join(', ')}</p>
          <p><span className="font-medium">Goals:</span> {formData.background.goals.join(', ')}</p>
          <p><span className="font-medium">Therapeutic Goals:</span> {formData.therapeutic_profile.therapeutic_goals.join(', ')}</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Create New Character</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Progress Steps */}
          <div className="flex items-center mt-4">
            {[1, 2, 3].map((step) => (
              <React.Fragment key={step}>
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step <= currentStep
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step}
                </div>
                {step < 3 && (
                  <div
                    className={`flex-1 h-1 mx-2 ${
                      step < currentStep ? 'bg-primary-600' : 'bg-gray-200'
                    }`}
                  />
                )}
              </React.Fragment>
            ))}
          </div>
          
          <div className="flex justify-between text-sm text-gray-600 mt-2">
            <span>Basic Info</span>
            <span>Background</span>
            <span>Therapeutic</span>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-4 overflow-y-auto max-h-[60vh]">
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
        </div>

        {/* Error Display */}
        {error && (
          <div className="px-6 py-2">
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
          <button
            onClick={currentStep === 1 ? onClose : handlePrevious}
            className="btn-secondary"
          >
            {currentStep === 1 ? 'Cancel' : 'Previous'}
          </button>
          
          {currentStep < 3 ? (
            <button onClick={handleNext} className="btn-primary">
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={creationInProgress}
              className="btn-primary disabled:opacity-50"
            >
              {creationInProgress ? (
                <div className="flex items-center">
                  <div className="spinner mr-2"></div>
                  Creating...
                </div>
              ) : (
                'Create Character'
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CharacterCreationForm;