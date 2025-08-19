import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { selectCharacter, deleteCharacter } from '../../store/slices/characterSlice';

interface Character {
  character_id: string;
  player_id: string;
  name: string;
  appearance: {
    description: string;
    avatar_url?: string;
  };
  background: {
    story: string;
    personality_traits: string[];
    goals: string[];
  };
  therapeutic_profile: {
    comfort_level: number;
    preferred_intensity: 'LOW' | 'MEDIUM' | 'HIGH';
    therapeutic_goals: string[];
  };
  created_at: string;
  last_active: string;
  active_worlds: string[];
}

interface CharacterCardProps {
  character: Character;
  isSelected: boolean;
  onEdit: (character: Character) => void;
}

const CharacterCard: React.FC<CharacterCardProps> = ({ character, isSelected, onEdit }) => {
  const dispatch = useDispatch();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleSelect = () => {
    dispatch(selectCharacter(character));
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit(character);
  };

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    setIsDeleting(true);
    try {
      await dispatch(deleteCharacter(character.character_id) as any).unwrap();
    } catch (error) {
      console.error('Failed to delete character:', error);
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  const handleDeleteCancel = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDeleteConfirm(false);
  };

  const getIntensityColor = (intensity: string) => {
    switch (intensity) {
      case 'LOW':
        return 'bg-green-100 text-green-600';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-600';
      case 'HIGH':
        return 'bg-red-100 text-red-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getTimeSinceActive = (dateString: string) => {
    const now = new Date();
    const lastActive = new Date(dateString);
    const diffInHours = Math.floor((now.getTime() - lastActive.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Active now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return formatDate(dateString);
  };

  return (
    <div
      className={`card p-6 cursor-pointer transition-all duration-200 hover:shadow-lg relative ${
        isSelected
          ? 'ring-2 ring-primary-500 bg-primary-50'
          : 'hover:bg-gray-50'
      }`}
      onClick={handleSelect}
    >
      {/* Selection Indicator */}
      {isSelected && (
        <div className="absolute top-3 right-3">
          <div className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
      )}

      {/* Character Header */}
      <div className="flex items-center space-x-4 mb-4">
        <div className="w-12 h-12 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0">
          <span className="text-white text-lg font-bold">
            {character.name.charAt(0).toUpperCase()}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 truncate">{character.name}</h3>
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <span>Created {formatDate(character.created_at)}</span>
            <span>•</span>
            <span>{getTimeSinceActive(character.last_active)}</span>
          </div>
        </div>
      </div>

      {/* Character Description */}
      <div className="mb-4">
        <p className="text-sm text-gray-700 line-clamp-2">
          {character.appearance.description}
        </p>
      </div>

      {/* Character Stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="text-xs text-gray-600 mb-1">Comfort Level</div>
          <div className="flex items-center">
            <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
              <div
                className="bg-primary-600 h-2 rounded-full"
                style={{ width: `${(character.therapeutic_profile.comfort_level / 10) * 100}%` }}
              />
            </div>
            <span className="text-sm font-medium text-gray-900">
              {character.therapeutic_profile.comfort_level}/10
            </span>
          </div>
        </div>
        
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="text-xs text-gray-600 mb-1">Active Worlds</div>
          <div className="text-lg font-semibold text-gray-900">
            {character.active_worlds.length}
          </div>
        </div>
      </div>

      {/* Tags */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center space-x-2">
          <span className={`text-xs px-2 py-1 rounded ${getIntensityColor(character.therapeutic_profile.preferred_intensity)}`}>
            {character.therapeutic_profile.preferred_intensity} Intensity
          </span>
          {character.active_worlds.length > 0 && (
            <span className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded">
              Active
            </span>
          )}
        </div>

        {/* Personality Traits */}
        {character.background.personality_traits.length > 0 && (
          <div>
            <div className="text-xs font-medium text-gray-600 mb-1">Traits:</div>
            <div className="flex flex-wrap gap-1">
              {character.background.personality_traits.slice(0, 3).map((trait, index) => (
                <span key={index} className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                  {trait}
                </span>
              ))}
              {character.background.personality_traits.length > 3 && (
                <span className="text-xs text-gray-500">
                  +{character.background.personality_traits.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Therapeutic Goals */}
        {character.therapeutic_profile.therapeutic_goals.length > 0 && (
          <div>
            <div className="text-xs font-medium text-gray-600 mb-1">Goals:</div>
            <div className="flex flex-wrap gap-1">
              {character.therapeutic_profile.therapeutic_goals.slice(0, 2).map((goal, index) => (
                <span key={index} className="text-xs bg-purple-100 text-purple-600 px-2 py-1 rounded">
                  {goal}
                </span>
              ))}
              {character.therapeutic_profile.therapeutic_goals.length > 2 && (
                <span className="text-xs text-gray-500">
                  +{character.therapeutic_profile.therapeutic_goals.length - 2} more
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="pt-4 border-t border-gray-200 flex justify-between">
        <button
          onClick={handleEdit}
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          Edit Details
        </button>
        
        {!showDeleteConfirm ? (
          <button
            onClick={handleDeleteClick}
            className="text-sm text-red-600 hover:text-red-700 font-medium"
          >
            Delete
          </button>
        ) : (
          <div className="flex space-x-2">
            <button
              onClick={handleDeleteCancel}
              className="text-sm text-gray-600 hover:text-gray-700"
            >
              Cancel
            </button>
            <button
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="text-sm text-red-600 hover:text-red-700 font-medium disabled:opacity-50"
            >
              {isDeleting ? 'Deleting...' : 'Confirm'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CharacterCard;