import { useState, useEffect, useCallback, useRef } from 'react';
import { nexusAPI } from '../services/api';
import { useDebounce } from './useDebounce';

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

export interface UseWorldSearchOptions {
  debounceDelay?: number;
  defaultPerPage?: number;
  autoSearch?: boolean;
  onError?: (error: Error) => void;
  onSuccess?: (response: WorldSearchResponse) => void;
}

export interface UseWorldSearchResult {
  // Search state
  query: string;
  setQuery: (query: string) => void;
  filters: WorldSearchFilters;
  setFilters: (filters: WorldSearchFilters) => void;
  updateFilter: (key: keyof WorldSearchFilters, value: any) => void;
  clearFilters: () => void;
  
  // Results state
  results: WorldSearchResult[];
  searchResponse: WorldSearchResponse | null;
  loading: boolean;
  error: string | null;
  
  // Pagination
  currentPage: number;
  setCurrentPage: (page: number) => void;
  
  // Actions
  search: () => Promise<void>;
  clearError: () => void;
  
  // Computed values
  hasResults: boolean;
  totalResults: number;
  activeFiltersCount: number;
}

/**
 * Custom hook for managing world search functionality
 * 
 * Features:
 * - Debounced search queries
 * - Advanced filtering
 * - Pagination support
 * - Error handling
 * - Loading states
 */
export const useWorldSearch = (options: UseWorldSearchOptions = {}): UseWorldSearchResult => {
  const {
    debounceDelay = 300,
    defaultPerPage = 12,
    autoSearch = true,
    onError,
    onSuccess,
  } = options;

  // Search state
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<WorldSearchFilters>({});
  const [currentPage, setCurrentPage] = useState(1);
  
  // Results state
  const [results, setResults] = useState<WorldSearchResult[]>([]);
  const [searchResponse, setSearchResponse] = useState<WorldSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Debounced query
  const debouncedQuery = useDebounce(query, debounceDelay);
  
  // Abort controller for cancelling requests
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Update a specific filter
   */
  const updateFilter = useCallback((key: keyof WorldSearchFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
    setCurrentPage(1); // Reset to first page when filters change
  }, []);

  /**
   * Clear all filters and query
   */
  const clearFilters = useCallback(() => {
    setFilters({});
    setQuery('');
    setCurrentPage(1);
  }, []);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Perform search with current parameters
   */
  const search = useCallback(async () => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    try {
      setLoading(true);
      setError(null);

      // Build search parameters
      const searchParams = {
        q: debouncedQuery,
        page: currentPage,
        per_page: defaultPerPage,
        ...filters,
      };

      // Remove empty/undefined values
      const cleanParams = Object.entries(searchParams).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value) && value.length === 0) {
            return acc;
          }
          acc[key] = value;
        }
        return acc;
      }, {} as any);

      const response = await nexusAPI.searchWorlds(cleanParams);
      
      if (abortControllerRef.current?.signal.aborted) {
        return;
      }

      setSearchResponse(response);
      setResults(response.results || []);
      onSuccess?.(response);
    } catch (err: any) {
      if (abortControllerRef.current?.signal.aborted) {
        return;
      }
      
      const errorMessage = err.message || 'Search failed. Please try again.';
      setError(errorMessage);
      setResults([]);
      setSearchResponse(null);
      onError?.(err);
      console.error('World search failed:', err);
    } finally {
      if (!abortControllerRef.current?.signal.aborted) {
        setLoading(false);
      }
    }
  }, [debouncedQuery, currentPage, defaultPerPage, filters, onSuccess, onError]);

  /**
   * Auto-search when parameters change
   */
  useEffect(() => {
    if (autoSearch && (debouncedQuery || Object.keys(filters).length > 0)) {
      search();
    } else if (autoSearch && !debouncedQuery && Object.keys(filters).length === 0) {
      // Clear results when no query or filters
      setResults([]);
      setSearchResponse(null);
    }
  }, [debouncedQuery, filters, currentPage, autoSearch, search]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Computed values
  const hasResults = results.length > 0;
  const totalResults = searchResponse?.total_count || 0;
  const activeFiltersCount = Object.keys(filters).reduce((count, key) => {
    const value = filters[key as keyof WorldSearchFilters];
    if (Array.isArray(value)) {
      return count + (value.length > 0 ? 1 : 0);
    }
    return count + (value !== undefined && value !== null && value !== '' ? 1 : 0);
  }, 0);

  return {
    // Search state
    query,
    setQuery,
    filters,
    setFilters,
    updateFilter,
    clearFilters,
    
    // Results state
    results,
    searchResponse,
    loading,
    error,
    
    // Pagination
    currentPage,
    setCurrentPage,
    
    // Actions
    search,
    clearError,
    
    // Computed values
    hasResults,
    totalResults,
    activeFiltersCount,
  };
};

/**
 * Hook for saved searches functionality
 */
export const useSavedSearches = () => {
  const [savedSearches, setSavedSearches] = useState<Array<{
    id: string;
    name: string;
    query: string;
    filters: WorldSearchFilters;
    created_at: string;
  }>>([]);

  const saveSearch = useCallback((name: string, query: string, filters: WorldSearchFilters) => {
    const newSearch = {
      id: Date.now().toString(),
      name,
      query,
      filters,
      created_at: new Date().toISOString(),
    };
    
    setSavedSearches(prev => [newSearch, ...prev]);
    
    // Save to localStorage
    try {
      const updated = [newSearch, ...savedSearches];
      localStorage.setItem('tta_saved_searches', JSON.stringify(updated));
    } catch (error) {
      console.error('Failed to save search to localStorage:', error);
    }
  }, [savedSearches]);

  const loadSearch = useCallback((searchId: string) => {
    return savedSearches.find(search => search.id === searchId);
  }, [savedSearches]);

  const deleteSearch = useCallback((searchId: string) => {
    setSavedSearches(prev => {
      const updated = prev.filter(search => search.id !== searchId);
      
      // Update localStorage
      try {
        localStorage.setItem('tta_saved_searches', JSON.stringify(updated));
      } catch (error) {
        console.error('Failed to update saved searches in localStorage:', error);
      }
      
      return updated;
    });
  }, []);

  // Load saved searches from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('tta_saved_searches');
      if (saved) {
        setSavedSearches(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Failed to load saved searches from localStorage:', error);
    }
  }, []);

  return {
    savedSearches,
    saveSearch,
    loadSearch,
    deleteSearch,
  };
};

export default useWorldSearch;
