import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

// Therapeutic theme types
export type TherapeuticTheme = 'calm' | 'warm' | 'nature' | 'clinical' | 'high-contrast' | 'dark';

export type ColorMode = 'light' | 'dark' | 'auto';

export type FontSize = 'small' | 'medium' | 'large' | 'extra-large';

export type MotionPreference = 'full' | 'reduced' | 'none';

// WCAG 2.1 AA compliant color schemes
export interface TherapeuticColorScheme {
  // Primary colors
  primary: {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;
  };

  // Secondary colors
  secondary: {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;
  };

  // Semantic colors
  success: string;
  warning: string;
  error: string;
  info: string;

  // Background colors
  background: {
    primary: string;
    secondary: string;
    tertiary: string;
    overlay: string;
  };

  // Text colors (WCAG AA compliant)
  text: {
    primary: string;
    secondary: string;
    tertiary: string;
    inverse: string;
    link: string;
    linkHover: string;
  };

  // Border colors
  border: {
    light: string;
    medium: string;
    dark: string;
    focus: string;
  };
}

// Therapeutic color schemes
const THERAPEUTIC_COLOR_SCHEMES: Record<TherapeuticTheme, TherapeuticColorScheme> = {
  calm: {
    primary: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e',
    },
    secondary: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a',
    },
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    background: {
      primary: '#ffffff',
      secondary: '#f8fafc',
      tertiary: '#f1f5f9',
      overlay: 'rgba(0, 0, 0, 0.5)',
    },
    text: {
      primary: '#1e293b',
      secondary: '#475569',
      tertiary: '#64748b',
      inverse: '#ffffff',
      link: '#0ea5e9',
      linkHover: '#0284c7',
    },
    border: {
      light: '#e2e8f0',
      medium: '#cbd5e1',
      dark: '#94a3b8',
      focus: '#0ea5e9',
    },
  },

  warm: {
    primary: {
      50: '#fef7ed',
      100: '#fdedd3',
      200: '#fed7aa',
      300: '#fdba74',
      400: '#fb923c',
      500: '#f97316',
      600: '#ea580c',
      700: '#c2410c',
      800: '#9a3412',
      900: '#7c2d12',
    },
    secondary: {
      50: '#fefaf0',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f',
    },
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    background: {
      primary: '#ffffff',
      secondary: '#fefaf0',
      tertiary: '#fef7ed',
      overlay: 'rgba(0, 0, 0, 0.5)',
    },
    text: {
      primary: '#7c2d12',
      secondary: '#9a3412',
      tertiary: '#c2410c',
      inverse: '#ffffff',
      link: '#ea580c',
      linkHover: '#c2410c',
    },
    border: {
      light: '#fde68a',
      medium: '#fcd34d',
      dark: '#f59e0b',
      focus: '#ea580c',
    },
  },

  nature: {
    primary: {
      50: '#f0fdf4',
      100: '#dcfce7',
      200: '#bbf7d0',
      300: '#86efac',
      400: '#4ade80',
      500: '#22c55e',
      600: '#16a34a',
      700: '#15803d',
      800: '#166534',
      900: '#14532d',
    },
    secondary: {
      50: '#f7fee7',
      100: '#ecfccb',
      200: '#d9f99d',
      300: '#bef264',
      400: '#a3e635',
      500: '#84cc16',
      600: '#65a30d',
      700: '#4d7c0f',
      800: '#3f6212',
      900: '#365314',
    },
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    background: {
      primary: '#ffffff',
      secondary: '#f7fee7',
      tertiary: '#f0fdf4',
      overlay: 'rgba(0, 0, 0, 0.5)',
    },
    text: {
      primary: '#14532d',
      secondary: '#166534',
      tertiary: '#15803d',
      inverse: '#ffffff',
      link: '#16a34a',
      linkHover: '#15803d',
    },
    border: {
      light: '#d9f99d',
      medium: '#bef264',
      dark: '#84cc16',
      focus: '#16a34a',
    },
  },

  clinical: {
    primary: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a',
    },
    secondary: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
    },
    success: '#059669',
    warning: '#d97706',
    error: '#dc2626',
    info: '#2563eb',
    background: {
      primary: '#ffffff',
      secondary: '#f9fafb',
      tertiary: '#f3f4f6',
      overlay: 'rgba(0, 0, 0, 0.5)',
    },
    text: {
      primary: '#111827',
      secondary: '#374151',
      tertiary: '#6b7280',
      inverse: '#ffffff',
      link: '#2563eb',
      linkHover: '#1d4ed8',
    },
    border: {
      light: '#e5e7eb',
      medium: '#d1d5db',
      dark: '#9ca3af',
      focus: '#2563eb',
    },
  },

  'high-contrast': {
    primary: {
      50: '#ffffff',
      100: '#f5f5f5',
      200: '#e5e5e5',
      300: '#d4d4d4',
      400: '#a3a3a3',
      500: '#737373',
      600: '#525252',
      700: '#404040',
      800: '#262626',
      900: '#171717',
    },
    secondary: {
      50: '#fafafa',
      100: '#f4f4f5',
      200: '#e4e4e7',
      300: '#d4d4d8',
      400: '#a1a1aa',
      500: '#71717a',
      600: '#52525b',
      700: '#3f3f46',
      800: '#27272a',
      900: '#18181b',
    },
    success: '#16a34a',
    warning: '#ca8a04',
    error: '#dc2626',
    info: '#2563eb',
    background: {
      primary: '#ffffff',
      secondary: '#000000',
      tertiary: '#f5f5f5',
      overlay: 'rgba(0, 0, 0, 0.8)',
    },
    text: {
      primary: '#000000',
      secondary: '#262626',
      tertiary: '#404040',
      inverse: '#ffffff',
      link: '#0000ee',
      linkHover: '#0000cc',
    },
    border: {
      light: '#000000',
      medium: '#404040',
      dark: '#000000',
      focus: '#0000ee',
    },
  },

  dark: {
    primary: {
      50: '#1e293b',
      100: '#334155',
      200: '#475569',
      300: '#64748b',
      400: '#94a3b8',
      500: '#cbd5e1',
      600: '#e2e8f0',
      700: '#f1f5f9',
      800: '#f8fafc',
      900: '#ffffff',
    },
    secondary: {
      50: '#111827',
      100: '#1f2937',
      200: '#374151',
      300: '#4b5563',
      400: '#6b7280',
      500: '#9ca3af',
      600: '#d1d5db',
      700: '#e5e7eb',
      800: '#f3f4f6',
      900: '#f9fafb',
    },
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    background: {
      primary: '#0f172a',
      secondary: '#1e293b',
      tertiary: '#334155',
      overlay: 'rgba(0, 0, 0, 0.8)',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#e2e8f0',
      tertiary: '#cbd5e1',
      inverse: '#0f172a',
      link: '#60a5fa',
      linkHover: '#93c5fd',
    },
    border: {
      light: '#334155',
      medium: '#475569',
      dark: '#64748b',
      focus: '#60a5fa',
    },
  },
};

// Theme context type
interface TherapeuticThemeContextType {
  // Current theme settings
  theme: TherapeuticTheme;
  colorMode: ColorMode;
  fontSize: FontSize;
  motionPreference: MotionPreference;

  // Theme setters
  setTheme: (theme: TherapeuticTheme) => void;
  setColorMode: (mode: ColorMode) => void;
  setFontSize: (size: FontSize) => void;
  setMotionPreference: (preference: MotionPreference) => void;

  // Current color scheme
  colors: TherapeuticColorScheme;

  // Accessibility helpers
  isHighContrast: boolean;
  isDarkMode: boolean;
  isReducedMotion: boolean;

  // CSS custom properties
  cssVariables: Record<string, string>;
}

const TherapeuticThemeContext = createContext<TherapeuticThemeContextType | undefined>(undefined);

export const useTherapeuticTheme = () => {
  const context = useContext(TherapeuticThemeContext);
  if (context === undefined) {
    throw new Error('useTherapeuticTheme must be used within a TherapeuticThemeProvider');
  }
  return context;
};

interface TherapeuticThemeProviderProps {
  children: ReactNode;
  defaultTheme?: TherapeuticTheme;
  defaultColorMode?: ColorMode;
  defaultFontSize?: FontSize;
  defaultMotionPreference?: MotionPreference;
  persistPreferences?: boolean;
}

export const TherapeuticThemeProvider: React.FC<TherapeuticThemeProviderProps> = ({
  children,
  defaultTheme = 'calm',
  defaultColorMode = 'auto',
  defaultFontSize = 'medium',
  defaultMotionPreference = 'full',
  persistPreferences = true,
}) => {
  // Load preferences from localStorage if persistence is enabled
  const getStoredPreference = (key: string, defaultValue: any) => {
    if (!persistPreferences || typeof window === 'undefined') {
      return defaultValue;
    }

    try {
      const stored = localStorage.getItem(`tta-theme-${key}`);
      return stored ? JSON.parse(stored) : defaultValue;
    } catch {
      return defaultValue;
    }
  };

  const [theme, setThemeState] = useState<TherapeuticTheme>(
    () => getStoredPreference('theme', defaultTheme)
  );
  const [colorMode, setColorModeState] = useState<ColorMode>(
    () => getStoredPreference('colorMode', defaultColorMode)
  );
  const [fontSize, setFontSizeState] = useState<FontSize>(
    () => getStoredPreference('fontSize', defaultFontSize)
  );
  const [motionPreference, setMotionPreferenceState] = useState<MotionPreference>(
    () => getStoredPreference('motionPreference', defaultMotionPreference)
  );

  // Persist preferences to localStorage
  const persistPreference = (key: string, value: any) => {
    if (persistPreferences && typeof window !== 'undefined') {
      try {
        localStorage.setItem(`tta-theme-${key}`, JSON.stringify(value));
      } catch (error) {
        console.warn('Failed to persist theme preference:', error);
      }
    }
  };

  // Theme setters with persistence
  const setTheme = (newTheme: TherapeuticTheme) => {
    setThemeState(newTheme);
    persistPreference('theme', newTheme);
  };

  const setColorMode = (newMode: ColorMode) => {
    setColorModeState(newMode);
    persistPreference('colorMode', newMode);
  };

  const setFontSize = (newSize: FontSize) => {
    setFontSizeState(newSize);
    persistPreference('fontSize', newSize);
  };

  const setMotionPreference = (newPreference: MotionPreference) => {
    setMotionPreferenceState(newPreference);
    persistPreference('motionPreference', newPreference);
  };

  // Determine effective color mode
  const [effectiveColorMode, setEffectiveColorMode] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    if (colorMode === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      setEffectiveColorMode(mediaQuery.matches ? 'dark' : 'light');

      const handleChange = (e: MediaQueryListEvent) => {
        setEffectiveColorMode(e.matches ? 'dark' : 'light');
      };

      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      setEffectiveColorMode(colorMode);
    }
  }, [colorMode]);

  // Get current color scheme
  const colors = THERAPEUTIC_COLOR_SCHEMES[theme];

  // Accessibility flags
  const isHighContrast = theme === 'high-contrast';
  const isDarkMode = effectiveColorMode === 'dark' || theme === 'dark';
  const isReducedMotion = motionPreference === 'reduced' || motionPreference === 'none';

  // Generate CSS custom properties
  const cssVariables = React.useMemo(() => {
    const vars: Record<string, string> = {};

    // Primary colors
    Object.entries(colors.primary).forEach(([key, value]) => {
      vars[`--color-primary-${key}`] = value;
    });

    // Secondary colors
    Object.entries(colors.secondary).forEach(([key, value]) => {
      vars[`--color-secondary-${key}`] = value;
    });

    // Semantic colors
    vars['--color-success'] = colors.success;
    vars['--color-warning'] = colors.warning;
    vars['--color-error'] = colors.error;
    vars['--color-info'] = colors.info;

    // Background colors
    Object.entries(colors.background).forEach(([key, value]) => {
      vars[`--color-bg-${key}`] = value;
    });

    // Text colors
    Object.entries(colors.text).forEach(([key, value]) => {
      vars[`--color-text-${key}`] = value;
    });

    // Border colors
    Object.entries(colors.border).forEach(([key, value]) => {
      vars[`--color-border-${key}`] = value;
    });

    // Font size
    const fontSizeMap = {
      small: '14px',
      medium: '16px',
      large: '18px',
      'extra-large': '20px',
    };
    vars['--font-size-base'] = fontSizeMap[fontSize];

    return vars;
  }, [colors, fontSize]);

  // Apply CSS variables to document root
  useEffect(() => {
    const root = document.documentElement;
    Object.entries(cssVariables).forEach(([property, value]) => {
      root.style.setProperty(property, value);
    });

    // Apply theme classes
    root.className = root.className
      .split(' ')
      .filter(cls => !cls.startsWith('theme-') && !cls.startsWith('font-') && !cls.startsWith('motion-'))
      .concat([
        `theme-${theme}`,
        `font-${fontSize}`,
        `motion-${motionPreference}`,
        isDarkMode ? 'dark' : 'light',
        isHighContrast ? 'high-contrast' : '',
      ])
      .filter(Boolean)
      .join(' ');

    return () => {
      // Cleanup on unmount
      Object.keys(cssVariables).forEach(property => {
        root.style.removeProperty(property);
      });
    };
  }, [cssVariables, theme, fontSize, motionPreference, isDarkMode, isHighContrast]);

  const value: TherapeuticThemeContextType = {
    theme,
    colorMode,
    fontSize,
    motionPreference,
    setTheme,
    setColorMode,
    setFontSize,
    setMotionPreference,
    colors,
    isHighContrast,
    isDarkMode,
    isReducedMotion,
    cssVariables,
  };

  return (
    <TherapeuticThemeContext.Provider value={value}>
      {children}
    </TherapeuticThemeContext.Provider>
  );
};

// Theme Selector Component
export const ThemeSelector: React.FC<{
  className?: string;
  showLabels?: boolean;
}> = ({ className = '', showLabels = true }) => {
  const { theme, setTheme, colorMode, setColorMode, fontSize, setFontSize } = useTherapeuticTheme();

  const themeOptions: { value: TherapeuticTheme; label: string; description: string }[] = [
    { value: 'calm', label: 'Calm', description: 'Soothing blues and soft tones' },
    { value: 'warm', label: 'Warm', description: 'Comforting oranges and yellows' },
    { value: 'nature', label: 'Nature', description: 'Refreshing greens and earth tones' },
    { value: 'clinical', label: 'Clinical', description: 'Professional grays and neutrals' },
    { value: 'high-contrast', label: 'High Contrast', description: 'Maximum accessibility contrast' },
    { value: 'dark', label: 'Dark', description: 'Dark mode for low-light environments' },
  ];

  const colorModeOptions: { value: ColorMode; label: string }[] = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'auto', label: 'Auto' },
  ];

  const fontSizeOptions: { value: FontSize; label: string }[] = [
    { value: 'small', label: 'Small' },
    { value: 'medium', label: 'Medium' },
    { value: 'large', label: 'Large' },
    { value: 'extra-large', label: 'Extra Large' },
  ];

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Theme Selection */}
      <div>
        {showLabels && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Therapeutic Theme
          </label>
        )}
        <div className="grid grid-cols-2 gap-2">
          {themeOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setTheme(option.value)}
              className={`p-3 text-left border rounded-lg transition-colors ${
                theme === option.value
                  ? 'border-blue-500 bg-blue-50 text-blue-900'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
              title={option.description}
            >
              <div className="font-medium text-sm">{option.label}</div>
              <div className="text-xs text-gray-500 mt-1">{option.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Color Mode Selection */}
      <div>
        {showLabels && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Color Mode
          </label>
        )}
        <div className="flex space-x-2">
          {colorModeOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setColorMode(option.value)}
              className={`px-3 py-2 text-sm border rounded-md transition-colors ${
                colorMode === option.value
                  ? 'border-blue-500 bg-blue-50 text-blue-900'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Font Size Selection */}
      <div>
        {showLabels && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Font Size
          </label>
        )}
        <div className="flex space-x-2">
          {fontSizeOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setFontSize(option.value)}
              className={`px-3 py-2 text-sm border rounded-md transition-colors ${
                fontSize === option.value
                  ? 'border-blue-500 bg-blue-50 text-blue-900'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TherapeuticThemeProvider;
