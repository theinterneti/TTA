import React, { useEffect, useState, useCallback } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "../../store/store";
import { fetchCharacters } from "../../store/slices/characterSlice";
import CharacterCreationForm from "../../components/Character/CharacterCreationForm";
import CharacterEditForm from "../../components/Character/CharacterEditForm";
import CharacterCard from "../../components/Character/CharacterCard";

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
    preferred_intensity: "LOW" | "MEDIUM" | "HIGH";
    therapeutic_goals: string[];
  };
  created_at: string;
  last_active: string;
  active_worlds: string[];
}

const CharacterManagement: React.FC = () => {
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const { characters, selectedCharacter, isLoading, error } = useSelector(
    (state: RootState) => state.character
  );

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(
    null
  );
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  // Debug state changes
  useEffect(() => {
    console.log("🔍 CharacterManagement profile changed:", profile?.player_id);
  }, [profile]);

  useEffect(() => {
    console.log(
      "🔍 CharacterManagement characters changed:",
      characters.length
    );
  }, [characters]);

  useEffect(() => {
    console.log(
      "🔍 CharacterManagement showCreateForm changed:",
      showCreateForm
    );
  }, [showCreateForm]);

  useEffect(() => {
    if (profile?.player_id) {
      dispatch(fetchCharacters(profile.player_id) as any);
    }
  }, [dispatch, profile?.player_id]);

  const handleCreateCharacter = useCallback(() => {
    setShowCreateForm(true);
  }, []);

  const handleEditCharacter = useCallback((character: Character) => {
    setEditingCharacter(character);
    setShowEditForm(true);
  }, []);

  const handleCreateSuccess = useCallback(() => {
    // Character list will be updated automatically via Redux createCharacter action
    // No need to fetch again as createCharacter.fulfilled already adds the new character
    setShowCreateForm(false);
  }, []);

  const handleEditSuccess = useCallback(() => {
    // Character list will be updated automatically via Redux
    setEditingCharacter(null);
    setShowEditForm(false);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="ml-2 text-gray-600">Loading characters...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Character Management
          </h1>
          <p className="text-gray-600 mt-1">
            Create and manage your therapeutic adventure characters
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* View Toggle */}
          {characters.length > 0 && (
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode("grid")}
                className={`p-2 rounded-md transition-colors duration-200 ${
                  viewMode === "grid"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
                  />
                </svg>
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={`p-2 rounded-md transition-colors duration-200 ${
                  viewMode === "list"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 10h16M4 14h16M4 18h16"
                  />
                </svg>
              </button>
            </div>
          )}

          <button
            onClick={handleCreateCharacter}
            disabled={characters.length >= 5}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
            Create Character
          </button>
        </div>
      </div>

      {/* Character Limit Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center">
          <svg
            className="w-5 h-5 text-blue-600 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span className="text-blue-800">
            You have {characters.length} of 5 characters. Each character can
            have unique therapeutic preferences and goals.
          </span>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg
              className="w-5 h-5 text-red-600 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}

      {/* Characters Display */}
      {characters.length > 0 ? (
        <div
          className={
            viewMode === "grid"
              ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              : "space-y-4"
          }
        >
          {characters.map((character) => (
            <CharacterCard
              key={character.character_id}
              character={character}
              isSelected={
                selectedCharacter?.character_id === character.character_id
              }
              onEdit={handleEditCharacter}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <svg
            className="w-16 h-16 text-gray-300 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No characters yet
          </h3>
          <p className="text-gray-600 mb-6">
            Create your first character to begin your therapeutic journey
          </p>
          <button onClick={handleCreateCharacter} className="btn-primary">
            Create Your First Character
          </button>
        </div>
      )}

      {/* Character Creation Form */}
      {showCreateForm && (
        <CharacterCreationForm
          onClose={() => setShowCreateForm(false)}
          onSuccess={handleCreateSuccess}
        />
      )}

      {/* Character Edit Form */}
      {showEditForm && editingCharacter && (
        <CharacterEditForm
          character={editingCharacter}
          onClose={() => {
            setShowEditForm(false);
            setEditingCharacter(null);
          }}
          onSuccess={handleEditSuccess}
        />
      )}
    </div>
  );
};

export default CharacterManagement;
