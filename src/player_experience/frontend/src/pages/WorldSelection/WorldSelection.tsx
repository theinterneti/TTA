import React, { useEffect, useState, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import {
  fetchAvailableWorlds,
  fetchWorldDetails,
  updateFilters,
  clearFilters,
  setSelectedWorld,
  clearSelectedWorld
} from '../../store/slices/worldSlice';
import WorldDetailsModal from '../../components/World/WorldDetailsModal';
import WorldCustomizationModal from '../../components/World/WorldCustomizationModal';

const WorldSelection: React.FC = () => {
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const { availableWorlds, isLoading, filters, selectedWorld } = useSelector((state: RootState) => state.world);
  const { selectedCharacter } = useSelector((state: RootState) => state.character);

  // Local state for search and modals
  const [searchTerm, setSearchTerm] = useState('');
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showCustomizationModal, setShowCustomizationModal] = useState(false);
  const [selectedWorldForDetails, setSelectedWorldForDetails] = useState<string | null>(null);

  useEffect(() => {
    if (profile?.player_id) {
      dispatch(fetchAvailableWorlds(profile.player_id) as any);
    }
  }, [dispatch, profile?.player_id]);

  // Filter and search worlds
  const filteredWorlds = useMemo(() => {
    let filtered = availableWorlds;

    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(world =>
        world.name.toLowerCase().includes(searchLower) ||
        world.description.toLowerCase().includes(searchLower) ||
        world.therapeutic_themes.some(theme => theme.toLowerCase().includes(searchLower))
      );
    }

    // Apply difficulty filter
    if (filters.difficulty.length > 0) {
      filtered = filtered.filter(world => filters.difficulty.includes(world.difficulty_level));
    }

    // Apply theme filter
    if (filters.themes.length > 0) {
      filtered = filtered.filter(world =>
        world.therapeutic_themes.some(theme => filters.themes.includes(theme))
      );
    }

    // Apply duration filter
    if (filters.duration) {
      filtered = filtered.filter(world => {
        const duration = world.estimated_duration.toLowerCase();
        switch (filters.duration) {
          case 'short':
            return duration.includes('1') || duration.includes('2');
          case 'medium':
            return duration.includes('3') || duration.includes('4') || duration.includes('5');
          case 'long':
            return duration.includes('6') || duration.includes('7') || duration.includes('8') || duration.includes('9');
          default:
            return true;
        }
      });
    }

    // Sort by compatibility score if character is selected
    if (selectedCharacter) {
      filtered = [...filtered].sort((a, b) => b.compatibility_score - a.compatibility_score);
    }

    return filtered;
  }, [availableWorlds, searchTerm, filters, selectedCharacter]);

  const handleViewDetails = async (worldId: string) => {
    setSelectedWorldForDetails(worldId);
    dispatch(fetchWorldDetails(worldId) as any);
    setShowDetailsModal(true);
  };

  const handleCustomizeWorld = (worldId: string) => {
    setSelectedWorldForDetails(worldId);
    setShowCustomizationModal(true);
  };

  const handleFilterChange = (filterType: string, value: any) => {
    dispatch(updateFilters({ [filterType]: value }) as any);
  };

  const handleClearFilters = () => {
    dispatch(clearFilters() as any);
    setSearchTerm('');
  };

  const getUniqueThemes = () => {
    const themes = new Set<string>();
    availableWorlds.forEach(world => {
      world.therapeutic_themes.forEach(theme => themes.add(theme));
    });
    return Array.from(themes).sort();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="ml-2 text-gray-600">Loading worlds...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">World Selection</h1>
        <p className="text-gray-600 mt-1">
          Choose therapeutic environments that match your current needs and goals
        </p>
      </div>

      {/* Character Selection Notice */}
      {!selectedCharacter && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <span className="text-yellow-800">
              Please select a character first to see world compatibility ratings.
            </span>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 lg:mb-0">
            Browse Worlds ({filteredWorlds.length} available)
          </h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleClearFilters}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              Clear all filters
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mb-4">
          <div className="relative">
            <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search worlds by name, description, or therapeutic themes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10"
            />
          </div>
        </div>

        {/* Filter Controls */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Difficulty Level
            </label>
            <select
              className="input-field"
              value={filters.difficulty[0] || ''}
              onChange={(e) => handleFilterChange('difficulty', e.target.value ? [e.target.value] : [])}
            >
              <option value="">All Levels</option>
              <option value="BEGINNER">Beginner</option>
              <option value="INTERMEDIATE">Intermediate</option>
              <option value="ADVANCED">Advanced</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Therapeutic Theme
            </label>
            <select
              className="input-field"
              value={filters.themes[0] || ''}
              onChange={(e) => handleFilterChange('themes', e.target.value ? [e.target.value] : [])}
            >
              <option value="">All Themes</option>
              {getUniqueThemes().map(theme => (
                <option key={theme} value={theme}>{theme}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration
            </label>
            <select
              className="input-field"
              value={filters.duration}
              onChange={(e) => handleFilterChange('duration', e.target.value)}
            >
              <option value="">Any Duration</option>
              <option value="short">Short (1-2 hours)</option>
              <option value="medium">Medium (3-5 hours)</option>
              <option value="long">Long (6+ hours)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sort By
            </label>
            <select className="input-field">
              <option value="compatibility">Best Match</option>
              <option value="name">Name</option>
              <option value="difficulty">Difficulty</option>
              <option value="duration">Duration</option>
            </select>
          </div>
        </div>
      </div>

      {/* Worlds Grid */}
      {filteredWorlds.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredWorlds.map((world) => (
            <div key={world.world_id} className="card p-6 hover:shadow-lg transition-shadow duration-200">
              {/* World Preview */}
              <div className="w-full h-32 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg mb-4 flex items-center justify-center">
                <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>

              {/* World Info */}
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">{world.name}</h3>
                  {selectedCharacter && (
                    <div className="flex items-center space-x-1">
                      <div className={`w-2 h-2 rounded-full ${
                        world.compatibility_score >= 0.8 ? 'bg-green-500' :
                        world.compatibility_score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                      }`} />
                      <span className="text-xs text-gray-600">
                        {Math.round(world.compatibility_score * 100)}% match
                      </span>
                    </div>
                  )}
                </div>

                <p className="text-sm text-gray-600">{world.description}</p>

                {/* Themes */}
                <div className="flex flex-wrap gap-1">
                  {world.therapeutic_themes.slice(0, 3).map((theme, index) => (
                    <span key={index} className="text-xs bg-therapeutic-calm text-blue-600 px-2 py-1 rounded">
                      {theme}
                    </span>
                  ))}
                  {world.therapeutic_themes.length > 3 && (
                    <span className="text-xs text-gray-500">
                      +{world.therapeutic_themes.length - 3} more
                    </span>
                  )}
                </div>

                {/* Metadata */}
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center">
                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {world.estimated_duration}
                  </span>
                  <span className={`px-2 py-1 rounded ${
                    world.difficulty_level === 'BEGINNER' ? 'bg-green-100 text-green-600' :
                    world.difficulty_level === 'INTERMEDIATE' ? 'bg-yellow-100 text-yellow-600' :
                    'bg-red-100 text-red-600'
                  }`}>
                    {world.difficulty_level}
                  </span>
                </div>

                {/* Actions */}
                <div className="pt-3 border-t border-gray-200 flex justify-between">
                  <button
                    className="text-sm text-primary-600 hover:text-primary-700"
                    onClick={() => handleViewDetails(world.world_id)}
                  >
                    View Details
                  </button>
                  <div className="flex space-x-2">
                    <button
                      className="text-sm text-gray-600 hover:text-gray-800"
                      onClick={() => handleCustomizeWorld(world.world_id)}
                      disabled={!selectedCharacter}
                    >
                      Customize
                    </button>
                    <button
                      className="btn-primary text-sm py-1 px-3"
                      disabled={!selectedCharacter}
                    >
                      Select World
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchTerm || filters.difficulty.length > 0 || filters.themes.length > 0 || filters.duration
              ? 'No worlds match your filters'
              : 'No worlds available'
            }
          </h3>
          <p className="text-gray-600">
            {searchTerm || filters.difficulty.length > 0 || filters.themes.length > 0 || filters.duration
              ? 'Try adjusting your search criteria or clearing filters'
              : 'Worlds will be loaded based on your therapeutic preferences'
            }
          </p>
        </div>
      )}

      {/* Modals */}
      {showDetailsModal && selectedWorldForDetails && (
        <WorldDetailsModal
          worldId={selectedWorldForDetails}
          isOpen={showDetailsModal}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedWorldForDetails(null);
            dispatch(clearSelectedWorld() as any);
          }}
          onCustomize={() => {
            setShowDetailsModal(false);
            setShowCustomizationModal(true);
          }}
        />
      )}

      {showCustomizationModal && selectedWorldForDetails && (
        <WorldCustomizationModal
          worldId={selectedWorldForDetails}
          isOpen={showCustomizationModal}
          onClose={() => {
            setShowCustomizationModal(false);
            setSelectedWorldForDetails(null);
          }}
          onConfirm={(parameters) => {
            // Handle world selection with custom parameters
            console.log('World selected with parameters:', parameters);
            setShowCustomizationModal(false);
            setSelectedWorldForDetails(null);
          }}
        />
      )}
    </div>
  );
};

export default WorldSelection;
