import React, { useState, useEffect, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { nexusAPI } from "../../services/api";
import { WorldCard } from "../World";
import { useDebounce } from "../../hooks/useDebounce";

export interface WorldSearchFilters {
  genre?: string;
  threat_level?: string;
  difficulty_level?: string;
  therapeutic_focus?: string[];
  min_rating?: number;
  max_duration?: number;
  is_public?: boolean;
  tags?: string[];
}

export interface WorldSearchResult {
  world_id: string;
  world_title: string;
  world_genre: string;
  world_rating: number;
  threat_level?: string;
  difficulty_level?: string;
  therapeutic_focus?: string[];
  tags?: string[];
  description?: string;
  estimated_duration?: number;
  player_count?: number;
  created_by?: string;
  last_updated?: string;
}

export interface WorldSearchResponse {
  results: WorldSearchResult[];
  total_count: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

interface WorldSearchProps {
  onWorldSelect?: (worldId: string) => void;
  initialFilters?: WorldSearchFilters;
  className?: string;
}

const GENRES = [
  "Fantasy",
  "Sci-Fi",
  "Mystery",
  "Adventure",
  "Horror",
  "Romance",
  "Thriller",
  "Drama",
  "Comedy",
  "Historical",
  "Psychological",
  "Educational",
];

const THREAT_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const DIFFICULTY_LEVELS = ["BEGINNER", "INTERMEDIATE", "ADVANCED"];

const THERAPEUTIC_FOCUSES = [
  "Anxiety Management",
  "Depression Support",
  "Trauma Recovery",
  "Social Skills",
  "Emotional Regulation",
  "Self-Esteem",
  "Grief Processing",
  "Addiction Recovery",
  "Relationship Building",
  "Stress Management",
  "Mindfulness",
  "Communication Skills",
];

const WorldSearch: React.FC<WorldSearchProps> = ({
  onWorldSelect,
  initialFilters = {},
  className = "",
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState<WorldSearchFilters>(initialFilters);
  const [results, setResults] = useState<WorldSearchResult[]>([]);
  const [searchResponse, setSearchResponse] =
    useState<WorldSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  const searchParams = useMemo(
    () => ({
      q: debouncedSearchQuery,
      page: currentPage,
      per_page: 12,
      ...filters,
    }),
    [debouncedSearchQuery, currentPage, filters]
  );

  const performSearch = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = (await nexusAPI.searchWorlds(searchParams)) as any;

      setSearchResponse(response);
      setResults(response.results || []);
    } catch (err: any) {
      console.error("Search failed:", err);
      setError(err.message || "Search failed. Please try again.");
      setResults([]);
      setSearchResponse(null);
    } finally {
      setLoading(false);
    }
  }, [searchParams]);

  useEffect(() => {
    if (debouncedSearchQuery || Object.keys(filters).length > 0) {
      performSearch();
    } else {
      setResults([]);
      setSearchResponse(null);
    }
  }, [debouncedSearchQuery, filters, currentPage, performSearch]);

  const handleFilterChange = (key: keyof WorldSearchFilters, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  const handleTherapeuticFocusToggle = (focus: string) => {
    const current = filters.therapeutic_focus || [];
    const updated = current.includes(focus)
      ? current.filter((f) => f !== focus)
      : [...current, focus];

    handleFilterChange("therapeutic_focus", updated);
  };

  const clearFilters = () => {
    setFilters({});
    setSearchQuery("");
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const activeFiltersCount = Object.keys(filters).reduce((count, key) => {
    const value = filters[key as keyof WorldSearchFilters];
    if (Array.isArray(value)) {
      return count + (value.length > 0 ? 1 : 0);
    }
    return (
      count + (value !== undefined && value !== null && value !== "" ? 1 : 0)
    );
  }, 0);

  return (
    <div className={`bg-white rounded-lg shadow-md ${className}`}>
      {/* Search Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search worlds by title, description, or tags..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg
                className="h-5 w-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>

          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              showFilters
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.207A1 1 0 013 6.5V4z"
              />
            </svg>
            <span>Filters</span>
            {activeFiltersCount > 0 && (
              <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
                {activeFiltersCount}
              </span>
            )}
          </button>
        </div>

        {/* Search Results Summary */}
        {searchResponse && (
          <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
            <div>
              Showing {results.length} of {searchResponse.total_count} worlds
              {searchQuery && <span> for "{searchQuery}"</span>}
            </div>
            {activeFiltersCount > 0 && (
              <button
                onClick={clearFilters}
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Clear all filters
              </button>
            )}
          </div>
        )}
      </div>

      {/* Advanced Filters */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-b border-gray-200 overflow-hidden"
          >
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Genre Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Genre
                  </label>
                  <select
                    value={filters.genre || ""}
                    onChange={(e) =>
                      handleFilterChange("genre", e.target.value || undefined)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Genres</option>
                    {GENRES.map((genre) => (
                      <option key={genre} value={genre}>
                        {genre}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Threat Level Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Threat Level
                  </label>
                  <select
                    value={filters.threat_level || ""}
                    onChange={(e) =>
                      handleFilterChange(
                        "threat_level",
                        e.target.value || undefined
                      )
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Levels</option>
                    {THREAT_LEVELS.map((level) => (
                      <option key={level} value={level}>
                        {level}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Difficulty Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Difficulty
                  </label>
                  <select
                    value={filters.difficulty_level || ""}
                    onChange={(e) =>
                      handleFilterChange(
                        "difficulty_level",
                        e.target.value || undefined
                      )
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Difficulties</option>
                    {DIFFICULTY_LEVELS.map((level) => (
                      <option key={level} value={level}>
                        {level}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Rating and Duration Filters */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Rating: {filters.min_rating || 0}/5
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="5"
                    step="0.5"
                    value={filters.min_rating || 0}
                    onChange={(e) =>
                      handleFilterChange(
                        "min_rating",
                        parseFloat(e.target.value) || undefined
                      )
                    }
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Duration: {filters.max_duration || 300} minutes
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="300"
                    step="5"
                    value={filters.max_duration || 300}
                    onChange={(e) =>
                      handleFilterChange(
                        "max_duration",
                        parseInt(e.target.value) || undefined
                      )
                    }
                    className="w-full"
                  />
                </div>
              </div>

              {/* Therapeutic Focus */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Therapeutic Focus Areas
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-32 overflow-y-auto">
                  {THERAPEUTIC_FOCUSES.map((focus) => (
                    <label
                      key={focus}
                      className="flex items-center space-x-2 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={(filters.therapeutic_focus || []).includes(
                          focus
                        )}
                        onChange={() => handleTherapeuticFocusToggle(focus)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{focus}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Public Worlds Toggle */}
              <div>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.is_public === true}
                    onChange={(e) =>
                      handleFilterChange(
                        "is_public",
                        e.target.checked ? true : undefined
                      )
                    }
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">
                    Show only public worlds
                  </span>
                </label>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Search Results */}
      <div className="p-6">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Searching worlds...</span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex items-center">
              <div className="text-red-500 mr-3">⚠️</div>
              <div>
                <h3 className="text-sm font-medium text-red-800">
                  Search Error
                </h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {!loading &&
          !error &&
          results.length === 0 &&
          (searchQuery || activeFiltersCount > 0) && (
            <div className="text-center py-12">
              <div className="text-gray-400 text-4xl mb-4">🔍</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No worlds found
              </h3>
              <p className="text-gray-600 mb-4">
                Try adjusting your search terms or filters to find more worlds.
              </p>
              <button
                onClick={clearFilters}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Clear all filters
              </button>
            </div>
          )}

        {!loading && !error && results.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.map((world) => (
                <WorldCard
                  key={world.world_id}
                  worldId={world.world_id}
                  onEnterWorld={onWorldSelect}
                  variant="compact"
                  className="h-full"
                />
              ))}
            </div>

            {/* Pagination */}
            {searchResponse && searchResponse.total_pages > 1 && (
              <div className="flex items-center justify-center space-x-2 mt-8">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={!searchResponse.has_prev}
                  className="px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Previous
                </button>

                <div className="flex space-x-1">
                  {Array.from(
                    { length: Math.min(5, searchResponse.total_pages) },
                    (_, i) => {
                      const page = i + 1;
                      return (
                        <button
                          key={page}
                          onClick={() => handlePageChange(page)}
                          className={`px-3 py-2 border rounded-md ${
                            page === currentPage
                              ? "bg-blue-600 text-white border-blue-600"
                              : "border-gray-300 hover:bg-gray-50"
                          }`}
                        >
                          {page}
                        </button>
                      );
                    }
                  )}
                </div>

                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={!searchResponse.has_next}
                  className="px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default WorldSearch;
