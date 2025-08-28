import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface GenreFilterProps {
  selectedGenre?: string;
  selectedThreatLevel?: string;
  onGenreChange: (genre: string | undefined) => void;
  onThreatLevelChange: (threatLevel: string | undefined) => void;
  availableGenres?: string[];
  availableThreatLevels?: string[];
  isOpen?: boolean;
  onToggle?: () => void;
}

const DEFAULT_GENRES = [
  'Fantasy',
  'Sci-Fi',
  'Mystery',
  'Adventure',
  'Horror',
  'Romance',
  'Thriller',
  'Drama',
  'Comedy',
  'Historical',
];

const DEFAULT_THREAT_LEVELS = [
  'Low',
  'Medium',
  'High',
  'Critical',
];

const GenreFilter: React.FC<GenreFilterProps> = ({
  selectedGenre,
  selectedThreatLevel,
  onGenreChange,
  onThreatLevelChange,
  availableGenres = DEFAULT_GENRES,
  availableThreatLevels = DEFAULT_THREAT_LEVELS,
  isOpen = false,
  onToggle,
}) => {
  const [internalOpen, setInternalOpen] = useState(false);
  
  const isFilterOpen = onToggle ? isOpen : internalOpen;
  const toggleFilter = onToggle || (() => setInternalOpen(!internalOpen));

  const handleGenreSelect = (genre: string) => {
    if (selectedGenre === genre) {
      onGenreChange(undefined); // Deselect if already selected
    } else {
      onGenreChange(genre);
    }
  };

  const handleThreatLevelSelect = (threatLevel: string) => {
    if (selectedThreatLevel === threatLevel) {
      onThreatLevelChange(undefined); // Deselect if already selected
    } else {
      onThreatLevelChange(threatLevel);
    }
  };

  const clearAllFilters = () => {
    onGenreChange(undefined);
    onThreatLevelChange(undefined);
  };

  const activeFiltersCount = (selectedGenre ? 1 : 0) + (selectedThreatLevel ? 1 : 0);

  return (
    <div className="relative">
      {/* Filter Toggle Button */}
      <button
        onClick={toggleFilter}
        className={`
          flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200
          ${isFilterOpen 
            ? 'bg-blue-600 text-white' 
            : 'bg-black bg-opacity-50 text-white hover:bg-opacity-70'
          }
        `}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.207A1 1 0 013 6.5V4z" />
        </svg>
        <span>Filters</span>
        {activeFiltersCount > 0 && (
          <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
            {activeFiltersCount}
          </span>
        )}
      </button>

      {/* Filter Panel */}
      <AnimatePresence>
        {isFilterOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 mt-2 w-80 bg-black bg-opacity-90 backdrop-blur-sm rounded-lg border border-gray-700 shadow-xl z-50"
          >
            <div className="p-4">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-semibold">Filter Story Worlds</h3>
                {activeFiltersCount > 0 && (
                  <button
                    onClick={clearAllFilters}
                    className="text-red-400 hover:text-red-300 text-sm underline"
                  >
                    Clear All
                  </button>
                )}
              </div>

              {/* Genre Filter */}
              <div className="mb-6">
                <h4 className="text-gray-300 text-sm font-medium mb-3">Genre</h4>
                <div className="grid grid-cols-2 gap-2">
                  {availableGenres.map((genre) => (
                    <button
                      key={genre}
                      onClick={() => handleGenreSelect(genre)}
                      className={`
                        px-3 py-2 rounded-md text-sm transition-all duration-200
                        ${selectedGenre === genre
                          ? 'bg-blue-600 text-white shadow-md'
                          : 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white'
                        }
                      `}
                    >
                      {genre}
                    </button>
                  ))}
                </div>
              </div>

              {/* Threat Level Filter */}
              <div className="mb-4">
                <h4 className="text-gray-300 text-sm font-medium mb-3">Threat Level</h4>
                <div className="grid grid-cols-2 gap-2">
                  {availableThreatLevels.map((level) => (
                    <button
                      key={level}
                      onClick={() => handleThreatLevelSelect(level)}
                      className={`
                        px-3 py-2 rounded-md text-sm transition-all duration-200 flex items-center justify-center space-x-2
                        ${selectedThreatLevel === level
                          ? 'bg-red-600 text-white shadow-md'
                          : 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white'
                        }
                      `}
                    >
                      <span className={`w-2 h-2 rounded-full ${
                        level === 'Low' ? 'bg-green-400' :
                        level === 'Medium' ? 'bg-yellow-400' :
                        level === 'High' ? 'bg-orange-400' :
                        'bg-red-400'
                      }`}></span>
                      <span>{level}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Active Filters Summary */}
              {activeFiltersCount > 0 && (
                <div className="pt-3 border-t border-gray-700">
                  <div className="text-xs text-gray-400 mb-2">Active Filters:</div>
                  <div className="flex flex-wrap gap-2">
                    {selectedGenre && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-600 text-white">
                        {selectedGenre}
                        <button
                          onClick={() => onGenreChange(undefined)}
                          className="ml-1 hover:text-gray-300"
                        >
                          ×
                        </button>
                      </span>
                    )}
                    {selectedThreatLevel && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-600 text-white">
                        {selectedThreatLevel}
                        <button
                          onClick={() => onThreatLevelChange(undefined)}
                          className="ml-1 hover:text-gray-300"
                        >
                          ×
                        </button>
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default GenreFilter;
