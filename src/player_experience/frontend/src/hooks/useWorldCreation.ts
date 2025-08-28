import { useState, useCallback } from 'react';
import { nexusAPI } from '../services/api';
import { useAuthGuard } from './useAuthGuard';

export interface WorldCreationData {
  world_title: string;
  world_genre: string;
  description: string;
  difficulty_level: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  threat_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  therapeutic_focus: string[];
  tags: string[];
  estimated_duration: number;
  max_players: number;
  is_public: boolean;
}

export interface WorldCreationResult {
  world_id: string;
  world_title: string;
  status: 'created' | 'pending' | 'failed';
  message?: string;
}

export interface UseWorldCreationOptions {
  onSuccess?: (result: WorldCreationResult) => void;
  onError?: (error: Error) => void;
  validateBeforeSubmit?: boolean;
}

export interface UseWorldCreationResult {
  createWorld: (data: WorldCreationData) => Promise<WorldCreationResult>;
  isCreating: boolean;
  error: string | null;
  lastCreatedWorld: WorldCreationResult | null;
  clearError: () => void;
  validateWorldData: (data: Partial<WorldCreationData>) => Record<string, string>;
}

/**
 * Custom hook for managing world creation workflow
 * 
 * Features:
 * - World creation with API integration
 * - Form validation
 * - Error handling
 * - Success callbacks
 * - Authentication checks
 */
export const useWorldCreation = (options: UseWorldCreationOptions = {}): UseWorldCreationResult => {
  const {
    onSuccess,
    onError,
    validateBeforeSubmit = true,
  } = options;

  const { isAuthenticated } = useAuthGuard({ autoRedirect: false });
  
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastCreatedWorld, setLastCreatedWorld] = useState<WorldCreationResult | null>(null);

  /**
   * Validate world creation data
   */
  const validateWorldData = useCallback((data: Partial<WorldCreationData>): Record<string, string> => {
    const errors: Record<string, string> = {};

    // Title validation
    if (!data.world_title?.trim()) {
      errors.world_title = 'World title is required';
    } else if (data.world_title.length < 3) {
      errors.world_title = 'World title must be at least 3 characters';
    } else if (data.world_title.length > 100) {
      errors.world_title = 'World title must be less than 100 characters';
    }

    // Genre validation
    if (!data.world_genre) {
      errors.world_genre = 'Genre is required';
    }

    // Description validation
    if (!data.description?.trim()) {
      errors.description = 'Description is required';
    } else if (data.description.length < 20) {
      errors.description = 'Description must be at least 20 characters';
    } else if (data.description.length > 1000) {
      errors.description = 'Description must be less than 1000 characters';
    }

    // Therapeutic focus validation
    if (!data.therapeutic_focus || data.therapeutic_focus.length === 0) {
      errors.therapeutic_focus = 'At least one therapeutic focus is required';
    }

    // Duration validation
    if (data.estimated_duration !== undefined) {
      if (data.estimated_duration < 5) {
        errors.estimated_duration = 'Duration must be at least 5 minutes';
      } else if (data.estimated_duration > 300) {
        errors.estimated_duration = 'Duration must be less than 300 minutes';
      }
    }

    // Max players validation
    if (data.max_players !== undefined) {
      if (data.max_players < 1) {
        errors.max_players = 'Must allow at least 1 player';
      } else if (data.max_players > 10) {
        errors.max_players = 'Maximum 10 players allowed';
      }
    }

    return errors;
  }, []);

  /**
   * Create a new world
   */
  const createWorld = useCallback(async (data: WorldCreationData): Promise<WorldCreationResult> => {
    try {
      setIsCreating(true);
      setError(null);

      // Check authentication
      if (!isAuthenticated) {
        throw new Error('You must be logged in to create a world');
      }

      // Validate data if required
      if (validateBeforeSubmit) {
        const validationErrors = validateWorldData(data);
        if (Object.keys(validationErrors).length > 0) {
          const errorMessage = Object.values(validationErrors)[0];
          throw new Error(`Validation failed: ${errorMessage}`);
        }
      }

      // Prepare data for API
      const worldData = {
        ...data,
        // Ensure arrays are properly formatted
        therapeutic_focus: Array.isArray(data.therapeutic_focus) ? data.therapeutic_focus : [],
        tags: Array.isArray(data.tags) ? data.tags : [],
      };

      // Call API
      const response = await nexusAPI.createWorld(worldData);
      
      const result: WorldCreationResult = {
        world_id: response.world_id || response.id,
        world_title: data.world_title,
        status: 'created',
        message: response.message || 'World created successfully',
      };

      setLastCreatedWorld(result);
      onSuccess?.(result);
      
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to create world';
      setError(errorMessage);
      
      const result: WorldCreationResult = {
        world_id: '',
        world_title: data.world_title,
        status: 'failed',
        message: errorMessage,
      };

      onError?.(err);
      throw err;
    } finally {
      setIsCreating(false);
    }
  }, [isAuthenticated, validateBeforeSubmit, validateWorldData, onSuccess, onError]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    createWorld,
    isCreating,
    error,
    lastCreatedWorld,
    clearError,
    validateWorldData,
  };
};

/**
 * Hook for world creation with automatic navigation
 */
export const useWorldCreationWithNavigation = (
  onNavigateToWorld?: (worldId: string) => void
) => {
  const worldCreation = useWorldCreation({
    onSuccess: (result) => {
      if (result.status === 'created' && onNavigateToWorld) {
        onNavigateToWorld(result.world_id);
      }
    },
  });

  return worldCreation;
};

/**
 * Hook for batch world creation (for templates or bulk operations)
 */
export const useBatchWorldCreation = () => {
  const [batchResults, setBatchResults] = useState<WorldCreationResult[]>([]);
  const [batchProgress, setBatchProgress] = useState({ current: 0, total: 0 });
  const [isBatchCreating, setIsBatchCreating] = useState(false);

  const createWorldsBatch = useCallback(async (worldsData: WorldCreationData[]) => {
    setIsBatchCreating(true);
    setBatchResults([]);
    setBatchProgress({ current: 0, total: worldsData.length });

    const results: WorldCreationResult[] = [];

    for (let i = 0; i < worldsData.length; i++) {
      try {
        setBatchProgress({ current: i + 1, total: worldsData.length });
        
        const response = await nexusAPI.createWorld(worldsData[i]);
        
        const result: WorldCreationResult = {
          world_id: response.world_id || response.id,
          world_title: worldsData[i].world_title,
          status: 'created',
          message: 'World created successfully',
        };
        
        results.push(result);
      } catch (err: any) {
        const result: WorldCreationResult = {
          world_id: '',
          world_title: worldsData[i].world_title,
          status: 'failed',
          message: err.message || 'Failed to create world',
        };
        
        results.push(result);
      }
    }

    setBatchResults(results);
    setIsBatchCreating(false);
    
    return results;
  }, []);

  return {
    createWorldsBatch,
    batchResults,
    batchProgress,
    isBatchCreating,
  };
};

export default useWorldCreation;
