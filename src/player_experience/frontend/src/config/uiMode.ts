// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Config/Uimode]]
/**
 * UI Mode Configuration
 *
 * Manages the entertainment vs clinical interface modes for different user types
 */

import { UIMode } from '../services/terminologyTranslation';

export interface UIModeConfig {
  defaultMode: UIMode;
  allowModeToggle: boolean;
  userRoleDefaults: Record<string, UIMode>;
  featureFlags: {
    entertainmentMode: boolean;
    clinicalMode: boolean;
    modeToggleUI: boolean;
  };
}

/**
 * Default UI mode configuration
 */
export const DEFAULT_UI_MODE_CONFIG: UIModeConfig = {
  // Default to entertainment mode for better user engagement
  defaultMode: UIMode.ENTERTAINMENT,

  // Allow users to toggle between modes
  allowModeToggle: true,

  // Default modes based on user roles
  userRoleDefaults: {
    'player': UIMode.ENTERTAINMENT,
    'patient': UIMode.ENTERTAINMENT, // Patients also get entertainment mode
    'clinician': UIMode.CLINICAL,
    'therapist': UIMode.CLINICAL,
    'admin': UIMode.CLINICAL,
    'researcher': UIMode.CLINICAL,
    'caregiver': UIMode.ENTERTAINMENT, // Caregivers might prefer entertainment mode
  },

  // Feature flags for different modes
  featureFlags: {
    entertainmentMode: true,
    clinicalMode: true,
    modeToggleUI: true,
  }
};

/**
 * Environment-based configuration overrides
 */
export const getUIModeConfig = (): UIModeConfig => {
  const config = { ...DEFAULT_UI_MODE_CONFIG };

  // Override with environment variables if available
  if (process.env.REACT_APP_DEFAULT_UI_MODE) {
    const envMode = process.env.REACT_APP_DEFAULT_UI_MODE.toLowerCase();
    if (envMode === 'entertainment' || envMode === 'clinical') {
      config.defaultMode = envMode as UIMode;
    }
  }

  if (process.env.REACT_APP_ALLOW_MODE_TOGGLE) {
    config.allowModeToggle = process.env.REACT_APP_ALLOW_MODE_TOGGLE === 'true';
  }

  if (process.env.REACT_APP_ENTERTAINMENT_MODE_ENABLED) {
    config.featureFlags.entertainmentMode = process.env.REACT_APP_ENTERTAINMENT_MODE_ENABLED === 'true';
  }

  if (process.env.REACT_APP_CLINICAL_MODE_ENABLED) {
    config.featureFlags.clinicalMode = process.env.REACT_APP_CLINICAL_MODE_ENABLED === 'true';
  }

  return config;
};

/**
 * Determine UI mode based on user context
 */
export const determineUIMode = (userRole?: string, userPreference?: UIMode): UIMode => {
  const config = getUIModeConfig();

  // User preference takes precedence
  if (userPreference && config.allowModeToggle) {
    return userPreference;
  }

  // Role-based default
  if (userRole && config.userRoleDefaults[userRole]) {
    return config.userRoleDefaults[userRole];
  }

  // System default
  return config.defaultMode;
};

/**
 * Entertainment mode theme configuration
 */
export const ENTERTAINMENT_THEME = {
  colors: {
    primary: '#4F46E5', // Adventure purple
    secondary: '#059669', // Quest green
    accent: '#DC2626', // Emergency red
    background: '#F8FAFC',
    surface: '#FFFFFF',
    text: '#1F2937',
    textSecondary: '#6B7280',
  },

  iconography: {
    session: '🎮',
    progress: '⭐',
    achievement: '🏆',
    character: '👤',
    world: '🌍',
    settings: '⚙️',
    help: '❓',
    emergency: '🚨',
  },

  terminology: {
    brandName: 'Adventure Platform',
    tagline: 'Your Personal Story Adventure',
    welcomeMessage: 'Welcome to your interactive story experience!',
  }
};

/**
 * Clinical mode theme configuration
 */
export const CLINICAL_THEME = {
  colors: {
    primary: '#2563EB', // Medical blue
    secondary: '#059669', // Health green
    accent: '#DC2626', // Alert red
    background: '#F9FAFB',
    surface: '#FFFFFF',
    text: '#111827',
    textSecondary: '#4B5563',
  },

  iconography: {
    session: '🏥',
    progress: '📊',
    achievement: '✅',
    character: '👤',
    world: '🏥',
    settings: '⚙️',
    help: '❓',
    emergency: '🚨',
  },

  terminology: {
    brandName: 'TTA Therapeutic Platform',
    tagline: 'Evidence-Based Therapeutic Gaming',
    welcomeMessage: 'Welcome to your therapeutic journey.',
  }
};

/**
 * Get theme configuration based on UI mode
 */
export const getThemeConfig = (mode: UIMode) => {
  return mode === UIMode.ENTERTAINMENT ? ENTERTAINMENT_THEME : CLINICAL_THEME;
};

/**
 * Local storage keys for UI mode persistence
 */
export const UI_MODE_STORAGE_KEYS = {
  MODE_PREFERENCE: 'tta_ui_mode_preference',
  USER_ROLE: 'tta_user_role',
  THEME_PREFERENCE: 'tta_theme_preference',
} as const;

/**
 * Utility functions for UI mode management
 */
export const UIModeUtils = {
  /**
   * Save user's UI mode preference to local storage
   */
  saveUserPreference: (mode: UIMode): void => {
    localStorage.setItem(UI_MODE_STORAGE_KEYS.MODE_PREFERENCE, mode);
  },

  /**
   * Load user's UI mode preference from local storage
   */
  loadUserPreference: (): UIMode | null => {
    const saved = localStorage.getItem(UI_MODE_STORAGE_KEYS.MODE_PREFERENCE);
    return saved as UIMode || null;
  },

  /**
   * Clear user's UI mode preference
   */
  clearUserPreference: (): void => {
    localStorage.removeItem(UI_MODE_STORAGE_KEYS.MODE_PREFERENCE);
  },

  /**
   * Check if entertainment mode is available
   */
  isEntertainmentModeAvailable: (): boolean => {
    const config = getUIModeConfig();
    return config.featureFlags.entertainmentMode;
  },

  /**
   * Check if clinical mode is available
   */
  isClinicalModeAvailable: (): boolean => {
    const config = getUIModeConfig();
    return config.featureFlags.clinicalMode;
  },

  /**
   * Check if mode toggle UI should be shown
   */
  shouldShowModeToggle: (): boolean => {
    const config = getUIModeConfig();
    return config.allowModeToggle && config.featureFlags.modeToggleUI;
  }
};

export default getUIModeConfig;
