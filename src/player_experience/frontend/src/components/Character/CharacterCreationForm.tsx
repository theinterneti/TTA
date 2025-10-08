import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { createCharacter } from '../../store/slices/characterSlice';
import { RootState } from '../../store/store';
import { IntensityLevel } from '../../types';
import { parseAPIError, validateName } from '../../utils/characterValidation';

interface CharacterCreationFormProps {
  onClose: () => void;
  onSuccess?: () => void;
}

interface TherapeuticGoal {
  goal_id: string;
  description: string;
  target_date?: string;
  progress_percentage: number;
  is_active: boolean;
  therapeutic_approaches: string[];
}

interface FormData {
  name: string;
  appearance: {
    age_range: string;
    gender_identity: string;
    physical_description: string;
    clothing_style: string;
    distinctive_features: string[];
    avatar_image_url?: string;
  };
  background: {
    name: string;
    backstory: string;
    personality_traits: string[];
    core_values: string[];
    fears_and_anxieties: string[];
    strengths_and_skills: string[];
    life_goals: string[];
    relationships: Record<string, string>;
  };
  therapeutic_profile: {
    primary_concerns: string[];
    therapeutic_goals: TherapeuticGoal[];
    preferred_intensity: IntensityLevel;
    comfort_zones: string[];
    readiness_level: number;
    therapeutic_approaches: string[];
  };
}

const CharacterCreationForm: React.FC<CharacterCreationFormProps> = ({
  onClose,
  onSuccess,
}) => {
  const dispatch = useDispatch();
  const { creationInProgress } = useSelector((state: RootState) => state.character);
  const { profile } = useSelector((state: RootState) => state.player);

  const [currentStep, setCurrentStep] = useState(1);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<FormData>({
    name: '',
    appearance: {
      age_range: 'adult',
      gender_identity: 'non-binary',
      physical_description: '',
      clothing_style: 'casual',
      distinctive_features: [],
      avatar_image_url: undefined,
    },
    background: {
      name: '',
      backstory: '',
      personality_traits: [],
      core_values: [],
      fears_and_anxieties: [],
      strengths_and_skills: [],
      life_goals: [],
      relationships: {},
    },
    therapeutic_profile: {
      primary_concerns: [],
      therapeutic_goals: [],
      preferred_intensity: 'MEDIUM' as IntensityLevel,
      comfort_zones: [],
      readiness_level: 0.5,
      therapeutic_approaches: [],
    },
  });

  // State for adding array items
  const [newTrait, setNewTrait] = useState('');
  const [newGoal, setNewGoal] = useState('');
  const [newValue, setNewValue] = useState('');
  const [newFear, setNewFear] = useState('');
  const [newSkill, setNewSkill] = useState('');
  const [newConcern, setNewConcern] = useState('');
  const [newComfortZone, setNewComfortZone] = useState('');
  const [newTherapeuticGoal, setNewTherapeuticGoal] = useState('');

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => {
      const keys = field.split('.');
      if (keys.length === 1) {
        return { ...prev, [field]: value };
      } else if (keys.length === 2) {
        const parentKey = keys[0] as keyof typeof formData;
        const parentObj = prev[parentKey] as any;
        return {
          ...prev,
          [keys[0]]: {
            ...parentObj,
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

  const addArrayItem = (field: string, value: string, setter: (val: string) => void) => {
    if (!value.trim()) return;

    setFormData(prev => {
      const keys = field.split('.');
      if (keys.length === 2) {
        const parentKey = keys[0] as keyof typeof formData;
        const childKey = keys[1];
        const parentObj = prev[parentKey] as any;
        const currentArray = parentObj[childKey] as string[];

        return {
          ...prev,
          [parentKey]: {
            ...parentObj,
            [childKey]: [...currentArray, value.trim()],
          },
        };
      }
      return prev;
    });

    setter('');
  };

  const removeArrayItem = (field: string, index: number) => {
    setFormData(prev => {
      const keys = field.split('.');
      if (keys.length === 2) {
        const parentKey = keys[0] as keyof typeof formData;
        const childKey = keys[1];
        const parentObj = prev[parentKey] as any;
        const currentArray = parentObj[childKey] as string[];

        return {
          ...prev,
          [parentKey]: {
            ...parentObj,
            [childKey]: currentArray.filter((_, i) => i !== index),
          },
        };
      }
      return prev;
    });
  };

  const addTherapeuticGoal = (description: string) => {
    if (!description.trim()) return;

    const newGoal: TherapeuticGoal = {
      goal_id: `goal_${Date.now()}`,
      description: description.trim(),
      progress_percentage: 0,
      is_active: true,
      therapeutic_approaches: [],
    };

    setFormData(prev => ({
      ...prev,
      therapeutic_profile: {
        ...prev.therapeutic_profile,
        therapeutic_goals: [...prev.therapeutic_profile.therapeutic_goals, newGoal],
      },
    }));

    setNewTherapeuticGoal('');
  };

  const removeTherapeuticGoal = (index: number) => {
    setFormData(prev => ({
      ...prev,
      therapeutic_profile: {
        ...prev.therapeutic_profile,
        therapeutic_goals: prev.therapeutic_profile.therapeutic_goals.filter((_, i) => i !== index),
      },
    }));
  };

  const validateStep1 = (): boolean => {
    const newErrors: Record<string, string> = {};

    const nameError = validateName(formData.name);
    if (nameError) {
      newErrors.name = nameError;
    }

    if (!formData.appearance.physical_description.trim()) {
      newErrors.appearance = 'Physical description is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.background.backstory.trim()) {
      newErrors.backstory = 'Background story is required';
    }

    if (formData.background.personality_traits.length === 0) {
      newErrors.traits = 'At least one personality trait is required';
    }

    if (formData.background.life_goals.length === 0) {
      newErrors.goals = 'At least one life goal is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep3 = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (formData.therapeutic_profile.primary_concerns.length === 0) {
      newErrors.concerns = 'At least one primary concern is required';
    }

    if (formData.therapeutic_profile.therapeutic_goals.length === 0) {
      newErrors.therapeuticGoals = 'At least one therapeutic goal is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    let isValid = false;

    if (currentStep === 1) {
      isValid = validateStep1();
    } else if (currentStep === 2) {
      isValid = validateStep2();
    }

    if (isValid) {
      setCurrentStep(prev => prev + 1);
      setErrors({});
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => prev - 1);
    setErrors({});
  };

  const handleSubmit = async () => {
    if (!validateStep3()) return;

    if (!profile?.player_id) {
      setError('Player ID not found. Please log in again.');
      return;
    }

    try {
      // Sync background name with character name
      const characterData = {
        ...formData,
        background: {
          ...formData.background,
          name: formData.name,
        },
      };

      await dispatch(createCharacter({
        playerId: profile.player_id,
        characterData,
      }) as any).unwrap();

      onSuccess?.();
      onClose();
    } catch (err: any) {
      console.error('Failed to create character:', err);
      setError(parseAPIError(err));
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
            />
            {errors.name && <p className="text-red-600 text-sm mt-1">{errors.name}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Age Range
              </label>
              <select
                className="input-field"
                value={formData.appearance.age_range}
                onChange={(e) => handleInputChange('appearance.age_range', e.target.value)}
              >
                <option value="child">Child</option>
                <option value="teen">Teen</option>
                <option value="adult">Adult</option>
                <option value="elder">Elder</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Gender Identity
              </label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g., non-binary, male, female"
                value={formData.appearance.gender_identity}
                onChange={(e) => handleInputChange('appearance.gender_identity', e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Physical Description *
            </label>
            <textarea
              className={`input-field ${errors.appearance ? 'border-red-500' : ''}`}
              rows={4}
              placeholder="Describe your character's physical appearance, style, and any distinctive features..."
              value={formData.appearance.physical_description}
              onChange={(e) => handleInputChange('appearance.physical_description', e.target.value)}
            />
            {errors.appearance && <p className="text-red-600 text-sm mt-1">{errors.appearance}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Clothing Style
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g., casual, formal, bohemian, etc."
              value={formData.appearance.clothing_style}
              onChange={(e) => handleInputChange('appearance.clothing_style', e.target.value)}
            />
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
              {formData.appearance.physical_description || 'Physical description will appear here...'}
            </p>
            <p className="text-xs text-gray-500">
              {formData.appearance.age_range} • {formData.appearance.gender_identity} • {formData.appearance.clothing_style}
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
              className={`input-field ${errors.backstory ? 'border-red-500' : ''}`}
              rows={4}
              placeholder="Tell your character's story, their past experiences, and what brought them here..."
              value={formData.background.backstory}
              onChange={(e) => handleInputChange('background.backstory', e.target.value)}
            />
            {errors.backstory && <p className="text-red-600 text-sm mt-1">{errors.backstory}</p>}
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
              Life Goals *
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a life goal"
                value={newGoal}
                onChange={(e) => setNewGoal(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('background.life_goals', newGoal, setNewGoal);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('background.life_goals', newGoal, setNewGoal)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.background.life_goals.map((goal, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full"
                >
                  {goal}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('background.life_goals', index)}
                    className="ml-2 text-green-600 hover:text-green-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            {errors.goals && <p className="text-red-600 text-sm mt-1">{errors.goals}</p>}
          </div>

          {/* Core Values */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Core Values
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a core value"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('background.core_values', newValue, setNewValue);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('background.core_values', newValue, setNewValue)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.background.core_values.map((value, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full"
                >
                  {value}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('background.core_values', index)}
                    className="ml-2 text-purple-600 hover:text-purple-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
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
          {/* Primary Concerns */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Primary Concerns *
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a primary concern"
                value={newConcern}
                onChange={(e) => setNewConcern(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('therapeutic_profile.primary_concerns', newConcern, setNewConcern);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('therapeutic_profile.primary_concerns', newConcern, setNewConcern)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.therapeutic_profile.primary_concerns.map((concern, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full"
                >
                  {concern}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('therapeutic_profile.primary_concerns', index)}
                    className="ml-2 text-orange-600 hover:text-orange-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            {errors.concerns && <p className="text-red-600 text-sm mt-1">{errors.concerns}</p>}
          </div>

          {/* Readiness Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Readiness Level (0.0 - 1.0)
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                className="flex-1"
                value={formData.therapeutic_profile.readiness_level}
                onChange={(e) => handleInputChange('therapeutic_profile.readiness_level', parseFloat(e.target.value))}
              />
              <span className="text-lg font-medium text-gray-900 w-12">
                {formData.therapeutic_profile.readiness_level.toFixed(1)}
              </span>
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Not Ready</span>
              <span>Fully Ready</span>
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

          {/* Comfort Zones */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Comfort Zones
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a comfort zone"
                value={newComfortZone}
                onChange={(e) => setNewComfortZone(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('therapeutic_profile.comfort_zones', newComfortZone, setNewComfortZone);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('therapeutic_profile.comfort_zones', newComfortZone, setNewComfortZone)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.therapeutic_profile.comfort_zones.map((zone, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-teal-100 text-teal-800 text-sm rounded-full"
                >
                  {zone}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('therapeutic_profile.comfort_zones', index)}
                    className="ml-2 text-teal-600 hover:text-teal-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
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
                    addTherapeuticGoal(newTherapeuticGoal);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addTherapeuticGoal(newTherapeuticGoal)}
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
                  {goal.description}
                  <button
                    type="button"
                    onClick={() => removeTherapeuticGoal(index)}
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
          <p><span className="font-medium">Readiness Level:</span> {formData.therapeutic_profile.readiness_level.toFixed(1)}</p>
          <p><span className="font-medium">Intensity:</span> {formData.therapeutic_profile.preferred_intensity}</p>
          <p><span className="font-medium">Traits:</span> {formData.background.personality_traits.join(', ') || 'None'}</p>
          <p><span className="font-medium">Goals:</span> {formData.background.life_goals.join(', ') || 'None'}</p>
          <p><span className="font-medium">Therapeutic Goals:</span> {formData.therapeutic_profile.therapeutic_goals.map(g => g.description).join(', ') || 'None'}</p>
        </div>
      </div>
    </div>
  );

  const handleBackdropClick = (e: React.MouseEvent) => {
    // Only close if clicking on the backdrop itself, not the modal content
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div
        className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
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
