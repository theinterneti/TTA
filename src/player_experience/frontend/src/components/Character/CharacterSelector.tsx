import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import { selectCharacter } from '../../store/slices/characterSlice';

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

interface CharacterSelectorProps {
  onSelect?: (character: Character) => void;
  showCreateButton?: boolean;
  onCreateNew?: () => void;
  compact?: boolean;
}

const CharacterSelector: React.FC<CharacterSelectorProps> = ({
  onSelect,
  showCreateButton = true,
  onCreateNew,
  compact = false,
}) => {
  const dispatch = useDispatch();
  const { characters, selectedCharacter, isLoading } = useSelector((state: RootState) => state.character);
  const [isOpen, setIsOpen] = useState(false);

  const handleSelect = (character: Character) => {
    dispatch(selectCharacter(character));
    onSelect?.(character);
    setIsOpen(false);
  };

  const handleCreateNew = () => {
    onCreateNew?.();
    setIsOpen(false);
  };

  const getIntensityColor = (intensity: string) => {
    switch (intensity) {
      case 'LOW':
        return 'text-green-600';
      case 'MEDIUM':
        return 'text-yellow-600';
      case 'HIGH':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  if (compact) {
    return (
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {selectedCharacter ? (
            <>
              <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-medium">
                  {selectedCharacter.name.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="text-sm font-medium text-gray-900">{selectedCharacter.name}</span>
            </>
          ) : (
            <>
              <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <span className="text-sm text-gray-600">Select Character</span>
            </>
          )}
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {isOpen && (
          <div className="absolute top-full left-0 mt-1 w-80 bg-white border border-gray-200 rounded-md shadow-lg z-50">
            <div className="p-2 max-h-64 overflow-y-auto">
              {characters.length > 0 ? (
                characters.map((character) => (
                  <button
                    key={character.character_id}
                    onClick={() => handleSelect(character)}
                    className={`w-full text-left p-3 rounded-md hover:bg-gray-50 transition-colors duration-200 ${
                      selectedCharacter?.character_id === character.character_id
                        ? 'bg-primary-50 border border-primary-200'
                        : ''
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-white text-sm font-medium">
                          {character.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">{character.name}</p>
                        <div className="flex items-center space-x-2 text-xs text-gray-600">
                          <span className={getIntensityColor(character.therapeutic_profile.preferred_intensity)}>
                            {character.therapeutic_profile.preferred_intensity}
                          </span>
                          <span>•</span>
                          <span>{character.active_worlds.length} worlds</span>
                        </div>
                      </div>
                      {selectedCharacter?.character_id === character.character_id && (
                        <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))
              ) : (
                <div className="p-4 text-center text-gray-500">
                  <svg className="w-8 h-8 text-gray-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <p className="text-sm">No characters yet</p>
                </div>
              )}
            </div>
            
            {showCreateButton && (
              <div className="border-t border-gray-200 p-2">
                <button
                  onClick={handleCreateNew}
                  className="w-full flex items-center justify-center space-x-2 p-2 text-primary-600 hover:bg-primary-50 rounded-md transition-colors duration-200"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span className="text-sm font-medium">Create New Character</span>
                </button>
              </div>
            )}
          </div>
        )}

        {/* Overlay to close dropdown */}
        {isOpen && (
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
        )}
      </div>
    );
  }

  // Full character selection interface
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Select Character</h3>
        {showCreateButton && (
          <button
            onClick={handleCreateNew}
            className="btn-primary text-sm"
          >
            Create New
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="spinner"></div>
          <span className="ml-2 text-gray-600">Loading characters...</span>
        </div>
      ) : characters.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {characters.map((character) => (
            <button
              key={character.character_id}
              onClick={() => handleSelect(character)}
              className={`text-left p-4 rounded-lg border-2 transition-all duration-200 hover:shadow-md ${
                selectedCharacter?.character_id === character.character_id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-medium">
                    {character.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{character.name}</h4>
                  <p className="text-sm text-gray-600">
                    {character.therapeutic_profile.preferred_intensity} intensity
                  </p>
                </div>
                {selectedCharacter?.character_id === character.character_id && (
                  <div className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </div>

              <p className="text-sm text-gray-700 line-clamp-2 mb-3">
                {character.appearance.description}
              </p>

              <div className="flex items-center justify-between text-xs text-gray-600">
                <span>Comfort: {character.therapeutic_profile.comfort_level}/10</span>
                <span>{character.active_worlds.length} active worlds</span>
              </div>

              {character.background.personality_traits.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {character.background.personality_traits.slice(0, 2).map((trait, index) => (
                    <span key={index} className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                      {trait}
                    </span>
                  ))}
                  {character.background.personality_traits.length > 2 && (
                    <span className="text-xs text-gray-500">
                      +{character.background.personality_traits.length - 2} more
                    </span>
                  )}
                </div>
              )}
            </button>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No characters yet</h3>
          <p className="text-gray-600 mb-6">
            Create your first character to begin your therapeutic journey
          </p>
          {showCreateButton && (
            <button
              onClick={handleCreateNew}
              className="btn-primary"
            >
              Create Your First Character
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default CharacterSelector;