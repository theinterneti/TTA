import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import { updateCharacter } from '../../store/slices/characterSlice';
import { IntensityLevel } from '../../types';

interface Character {
  character_id: string;
  player_id: string;
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
    therapeutic_goals: Array<{
      goal_id: string;
      description: string;
      target_date?: string;
      progress_percentage: number;
      is_active: boolean;
      therapeutic_approaches: string[];
    }>;
    preferred_intensity: IntensityLevel;
    comfort_zones: string[];
    readiness_level: number;
    therapeutic_approaches: string[];
  };
  created_at: string;
  last_active: string;
  active_worlds: string[];
}

interface CharacterEditFormProps {
  character: Character;
  onClose: () => void;
  onSuccess?: () => void;
}

const CharacterEditForm: React.FC<CharacterEditFormProps> = ({ character, onClose, onSuccess }) => {
  const dispatch = useDispatch();
  const { isLoading, error } = useSelector((state: RootState) => state.character);

  const [formData, setFormData] = useState({
    name: character.name,
    appearance: {
      age_range: character.appearance.age_range,
      gender_identity: character.appearance.gender_identity,
      physical_description: character.appearance.physical_description,
      clothing_style: character.appearance.clothing_style,
      distinctive_features: [...character.appearance.distinctive_features],
      avatar_image_url: character.appearance.avatar_image_url,
    },
    background: {
      name: character.background.name,
      backstory: character.background.backstory,
      personality_traits: [...character.background.personality_traits],
      core_values: [...character.background.core_values],
      fears_and_anxieties: [...character.background.fears_and_anxieties],
      strengths_and_skills: [...character.background.strengths_and_skills],
      life_goals: [...character.background.life_goals],
      relationships: { ...character.background.relationships },
    },
    therapeutic_profile: {
      primary_concerns: [...character.therapeutic_profile.primary_concerns],
      therapeutic_goals: [...character.therapeutic_profile.therapeutic_goals],
      preferred_intensity: character.therapeutic_profile.preferred_intensity,
      comfort_zones: [...character.therapeutic_profile.comfort_zones],
      readiness_level: character.therapeutic_profile.readiness_level,
      therapeutic_approaches: [...character.therapeutic_profile.therapeutic_approaches],
    },
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [hasChanges, setHasChanges] = useState(false);
  const [newTrait, setNewTrait] = useState('');
  const [newGoal, setNewGoal] = useState('');
  const [newTherapeuticGoal, setNewTherapeuticGoal] = useState('');

  // Track changes
  useEffect(() => {
    const hasFormChanges = 
      formData.name !== character.name ||
      formData.appearance.description !== character.appearance.description ||
      formData.background.story !== character.background.story ||
      JSON.stringify(formData.background.personality_traits) !== JSON.stringify(character.background.personality_traits) ||
      JSON.stringify(formData.background.goals) !== JSON.stringify(character.background.goals) ||
      formData.therapeutic_profile.comfort_level !== character.therapeutic_profile.comfort_level ||
      formData.therapeutic_profile.preferred_intensity !== character.therapeutic_profile.preferred_intensity ||
      JSON.stringify(formData.therapeutic_profile.therapeutic_goals) !== JSON.stringify(character.therapeutic_profile.therapeutic_goals);
    
    setHasChanges(hasFormChanges);
  }, [formData, character]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Character name is required';
    } else if (formData.name.length > 50) {
      newErrors.name = 'Character name must be 50 characters or less';
    }

    if (!formData.appearance.description.trim()) {
      newErrors.appearance = 'Character appearance description is required';
    }

    if (!formData.background.story.trim()) {
      newErrors.story = 'Character background story is required';
    }

    if (formData.background.personality_traits.length === 0) {
      newErrors.traits = 'At least one personality trait is required';
    }

    if (formData.background.goals.length === 0) {
      newErrors.goals = 'At least one character goal is required';
    }

    if (formData.therapeutic_profile.therapeutic_goals.length === 0) {
      newErrors.therapeuticGoals = 'At least one therapeutic goal is required';
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

  const addArrayItem = (field: string, value: string, setter: (value: string) => void) => {
    if (value.trim()) {
      const keys = field.split('.');
      setFormData(prev => {
        const parentKey = keys[0] as keyof typeof formData;
        const parentObj = prev[parentKey] as any;
        return {
          ...prev,
          [keys[0]]: {
            ...parentObj,
            [keys[1]]: [...parentObj[keys[1]], value.trim()],
          },
        };
      });
      setter('');
    }
  };

  const removeArrayItem = (field: string, index: number) => {
    const keys = field.split('.');
    setFormData(prev => {
      const parentKey = keys[0] as keyof typeof formData;
      const parentObj = prev[parentKey] as any;
      return {
        ...prev,
        [keys[0]]: {
          ...parentObj,
          [keys[1]]: parentObj[keys[1]].filter((_: any, i: number) => i !== index),
        },
      };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      await dispatch(updateCharacter({
        characterId: character.character_id,
        updates: formData,
      }) as any).unwrap();
      
      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Failed to update character:', error);
    }
  };

  const handleCancel = () => {
    if (hasChanges) {
      if (window.confirm('You have unsaved changes. Are you sure you want to cancel?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Edit Character</h2>
              <p className="text-sm text-gray-600 mt-1">
                Modify your character's details and therapeutic preferences
              </p>
            </div>
            <button
              onClick={handleCancel}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {hasChanges && (
            <div className="mt-2 text-sm text-amber-600 bg-amber-50 px-3 py-2 rounded-md">
              You have unsaved changes
            </div>
          )}
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="flex flex-col h-full">
          <div className="px-6 py-4 overflow-y-auto max-h-[60vh] space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                      value={formData.appearance.description}
                      onChange={(e) => handleInputChange('appearance.description', e.target.value)}
                    />
                    {errors.appearance && <p className="text-red-600 text-sm mt-1">{errors.appearance}</p>}
                  </div>
                </div>
              </div>

              {/* Character Preview */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Preview</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-12 h-12 bg-primary-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-lg font-bold">
                        {formData.name.charAt(0).toUpperCase() || '?'}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{formData.name || 'Character Name'}</p>
                      <p className="text-sm text-gray-600">
                        {formData.therapeutic_profile.preferred_intensity} Intensity
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">
                    {formData.appearance.description || 'Appearance description...'}
                  </p>
                </div>
              </div>
            </div>

            {/* Background */}
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
                    value={formData.background.story}
                    onChange={(e) => handleInputChange('background.story', e.target.value)}
                  />
                  {errors.story && <p className="text-red-600 text-sm mt-1">{errors.story}</p>}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
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

            {/* Therapeutic Profile */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Therapeutic Profile</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
              type="button"
              onClick={handleCancel}
              className="btn-secondary"
            >
              Cancel
            </button>
            
            <button
              type="submit"
              disabled={isLoading || !hasChanges}
              className="btn-primary disabled:opacity-50"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="spinner mr-2"></div>
                  Saving...
                </div>
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CharacterEditForm;