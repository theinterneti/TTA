/**
 * UI Mode Hook
 *
 * React hook for managing UI mode state and initialization
 */

import { useEffect, useState } from 'react';
import { UIMode, TerminologyTranslationService } from '../services/terminologyTranslation';
import { determineUIMode, UIModeUtils } from '../config/uiMode';

interface UseUIModeOptions {
  userRole?: string;
  autoInitialize?: boolean;
}

interface UseUIModeReturn {
  currentMode: UIMode;
  isEntertainmentMode: boolean;
  isClinicalMode: boolean;
  setMode: (mode: UIMode) => void;
  toggleMode: () => void;
  isLoading: boolean;
  error: string | null;
}

/**
 * Hook for managing UI mode state and providing mode-related utilities
 */
export const useUIMode = (options: UseUIModeOptions = {}): UseUIModeReturn => {
  const { userRole, autoInitialize = true } = options;

  const [currentMode, setCurrentMode] = useState<UIMode>(UIMode.ENTERTAINMENT);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize UI mode on hook mount
  useEffect(() => {
    if (!autoInitialize) {
      setIsLoading(false);
      return;
    }

    const initializeMode = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Get translation service instance
        const translationService = TerminologyTranslationService.getInstance();

        // Check for saved user preference
        const savedPreference = UIModeUtils.loadUserPreference();

        // Determine the appropriate mode
        const determinedMode = determineUIMode(userRole, savedPreference);

        // Set the mode in the translation service
        translationService.setMode(determinedMode);
        setCurrentMode(determinedMode);

        // Save the preference if it wasn't already saved
        if (!savedPreference) {
          UIModeUtils.saveUserPreference(determinedMode);
        }

      } catch (err) {
        console.error('Failed to initialize UI mode:', err);
        setError('Failed to initialize interface mode');

        // Fallback to entertainment mode
        const translationService = TerminologyTranslationService.getInstance();
        translationService.setMode(UIMode.ENTERTAINMENT);
        setCurrentMode(UIMode.ENTERTAINMENT);

      } finally {
        setIsLoading(false);
      }
    };

    initializeMode();
  }, [userRole, autoInitialize]);

  // Set mode function
  const setMode = (mode: UIMode) => {
    try {
      const translationService = TerminologyTranslationService.getInstance();
      translationService.setMode(mode);
      setCurrentMode(mode);
      UIModeUtils.saveUserPreference(mode);
      setError(null);
    } catch (err) {
      console.error('Failed to set UI mode:', err);
      setError('Failed to change interface mode');
    }
  };

  // Toggle between modes
  const toggleMode = () => {
    const newMode = currentMode === UIMode.ENTERTAINMENT ? UIMode.CLINICAL : UIMode.ENTERTAINMENT;
    setMode(newMode);
  };

  return {
    currentMode,
    isEntertainmentMode: currentMode === UIMode.ENTERTAINMENT,
    isClinicalMode: currentMode === UIMode.CLINICAL,
    setMode,
    toggleMode,
    isLoading,
    error
  };
};

/**
 * Hook specifically for entertainment mode initialization
 * Ensures the app starts in entertainment mode for player users
 */
export const useEntertainmentMode = () => {
  const { currentMode, setMode, isLoading } = useUIMode({
    userRole: 'player',
    autoInitialize: true
  });

  // Force entertainment mode for player users
  useEffect(() => {
    if (!isLoading && currentMode !== UIMode.ENTERTAINMENT) {
      setMode(UIMode.ENTERTAINMENT);
    }
  }, [currentMode, setMode, isLoading]);

  return {
    isReady: !isLoading && currentMode === UIMode.ENTERTAINMENT,
    isLoading
  };
};

/**
 * Hook for components that need to react to mode changes
 */
export const useUIModeListener = (callback: (mode: UIMode) => void) => {
  const { currentMode } = useUIMode();

  useEffect(() => {
    callback(currentMode);
  }, [currentMode, callback]);
};

/**
 * Hook for getting mode-specific configuration
 */
export const useModeConfig = () => {
  const { currentMode, isEntertainmentMode, isClinicalMode } = useUIMode();

  const getConfig = () => {
    if (isEntertainmentMode) {
      return {
        brandName: 'Adventure Platform',
        tagline: 'Your Personal Story Experience',
        primaryColor: '#4F46E5', // Adventure purple
        iconSet: 'gaming',
        terminology: 'entertainment'
      };
    } else {
      return {
        brandName: 'TTA Therapeutic Platform',
        tagline: 'Evidence-Based Therapeutic Gaming',
        primaryColor: '#2563EB', // Medical blue
        iconSet: 'clinical',
        terminology: 'clinical'
      };
    }
  };

  return {
    currentMode,
    isEntertainmentMode,
    isClinicalMode,
    config: getConfig()
  };
};

export default useUIMode;
