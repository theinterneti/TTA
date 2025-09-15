import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';

// Accessibility preference types
export type ScreenReaderMode = 'auto' | 'enabled' | 'disabled';
export type KeyboardNavigationMode = 'standard' | 'enhanced' | 'custom';
export type FocusIndicatorStyle = 'default' | 'high-contrast' | 'therapeutic';
export type AnnouncementLevel = 'minimal' | 'standard' | 'verbose';

// Accessibility settings interface
export interface AccessibilitySettings {
  screenReader: {
    mode: ScreenReaderMode;
    announcePageChanges: boolean;
    announceFormErrors: boolean;
    announceStatusUpdates: boolean;
    verboseDescriptions: boolean;
  };
  keyboard: {
    navigationMode: KeyboardNavigationMode;
    skipLinks: boolean;
    focusTrapping: boolean;
    customShortcuts: boolean;
  };
  visual: {
    focusIndicatorStyle: FocusIndicatorStyle;
    reducedMotion: boolean;
    highContrast: boolean;
    largeText: boolean;
  };
  audio: {
    soundEffects: boolean;
    voiceAnnouncements: boolean;
    audioDescriptions: boolean;
  };
  interaction: {
    clickDelay: number; // milliseconds
    hoverDelay: number; // milliseconds
    autoplayMedia: boolean;
    stickyFocus: boolean;
  };
}

// Default accessibility settings
const DEFAULT_ACCESSIBILITY_SETTINGS: AccessibilitySettings = {
  screenReader: {
    mode: 'auto',
    announcePageChanges: true,
    announceFormErrors: true,
    announceStatusUpdates: true,
    verboseDescriptions: false,
  },
  keyboard: {
    navigationMode: 'standard',
    skipLinks: true,
    focusTrapping: true,
    customShortcuts: false,
  },
  visual: {
    focusIndicatorStyle: 'default',
    reducedMotion: false,
    highContrast: false,
    largeText: false,
  },
  audio: {
    soundEffects: true,
    voiceAnnouncements: false,
    audioDescriptions: false,
  },
  interaction: {
    clickDelay: 0,
    hoverDelay: 300,
    autoplayMedia: false,
    stickyFocus: false,
  },
};

// Accessibility context type
interface AccessibilityContextType {
  // Settings
  settings: AccessibilitySettings;
  updateSettings: (updates: Partial<AccessibilitySettings>) => void;
  resetSettings: () => void;

  // Screen reader support
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
  announcePageChange: (title: string, description?: string) => void;
  announceError: (error: string, field?: string) => void;
  announceStatus: (status: string, type?: 'success' | 'warning' | 'error' | 'info') => void;

  // Keyboard navigation
  focusElement: (selector: string) => boolean;
  trapFocus: (container: HTMLElement) => () => void;
  createSkipLink: (target: string, label: string) => void;

  // ARIA helpers
  generateAriaLabel: (base: string, context?: string) => string;
  generateAriaDescription: (description: string, verbose?: boolean) => string;

  // Accessibility state
  isScreenReaderActive: boolean;
  isKeyboardUser: boolean;
  isHighContrastMode: boolean;
  isReducedMotionMode: boolean;

  // Compliance checking
  checkWCAGCompliance: (element: HTMLElement) => AccessibilityIssue[];
  validateForm: (form: HTMLFormElement) => FormAccessibilityReport;
}

// Accessibility issue types
export interface AccessibilityIssue {
  type: 'error' | 'warning' | 'info';
  rule: string;
  description: string;
  element: string;
  suggestion: string;
}

// Form accessibility report
export interface FormAccessibilityReport {
  isAccessible: boolean;
  issues: AccessibilityIssue[];
  score: number; // 0-100
  recommendations: string[];
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (context === undefined) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

interface AccessibilityProviderProps {
  children: ReactNode;
  persistSettings?: boolean;
  enableAutoDetection?: boolean;
  therapeuticMode?: boolean;
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({
  children,
  persistSettings = true,
  enableAutoDetection = true,
  therapeuticMode = true,
}) => {
  // Load settings from localStorage if persistence is enabled
  const getStoredSettings = (): AccessibilitySettings => {
    if (!persistSettings || typeof window === 'undefined') {
      return DEFAULT_ACCESSIBILITY_SETTINGS;
    }

    try {
      const stored = localStorage.getItem('tta-accessibility-settings');
      return stored ? { ...DEFAULT_ACCESSIBILITY_SETTINGS, ...JSON.parse(stored) } : DEFAULT_ACCESSIBILITY_SETTINGS;
    } catch {
      return DEFAULT_ACCESSIBILITY_SETTINGS;
    }
  };

  const [settings, setSettings] = useState<AccessibilitySettings>(getStoredSettings);
  const [isScreenReaderActive, setIsScreenReaderActive] = useState(false);
  const [isKeyboardUser, setIsKeyboardUser] = useState(false);
  const [isHighContrastMode, setIsHighContrastMode] = useState(false);
  const [isReducedMotionMode, setIsReducedMotionMode] = useState(false);

  // Persist settings to localStorage
  const persistSettingsToStorage = (newSettings: AccessibilitySettings) => {
    if (persistSettings && typeof window !== 'undefined') {
      try {
        localStorage.setItem('tta-accessibility-settings', JSON.stringify(newSettings));
      } catch (error) {
        console.warn('Failed to persist accessibility settings:', error);
      }
    }
  };

  // Update settings
  const updateSettings = useCallback((updates: Partial<AccessibilitySettings>) => {
    setSettings(prev => {
      const newSettings = { ...prev, ...updates };
      persistSettingsToStorage(newSettings);
      return newSettings;
    });
  }, []);

  // Reset settings to defaults
  const resetSettings = useCallback(() => {
    setSettings(DEFAULT_ACCESSIBILITY_SETTINGS);
    persistSettingsToStorage(DEFAULT_ACCESSIBILITY_SETTINGS);
  }, []);

  // Auto-detect accessibility preferences
  useEffect(() => {
    if (!enableAutoDetection) return;

    // Detect screen reader
    const detectScreenReader = () => {
      // Check for common screen reader indicators
      const hasScreenReader = !!(
        window.navigator.userAgent.match(/NVDA|JAWS|VoiceOver|TalkBack|Dragon/i) ||
        window.speechSynthesis ||
        document.querySelector('[aria-live]')
      );
      setIsScreenReaderActive(hasScreenReader);
    };

    // Detect keyboard navigation
    const detectKeyboardUser = () => {
      let keyboardDetected = false;

      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Tab' && !keyboardDetected) {
          keyboardDetected = true;
          setIsKeyboardUser(true);
          document.removeEventListener('keydown', handleKeyDown);
        }
      };

      const handleMouseDown = () => {
        if (keyboardDetected) {
          setIsKeyboardUser(false);
          keyboardDetected = false;
        }
      };

      document.addEventListener('keydown', handleKeyDown);
      document.addEventListener('mousedown', handleMouseDown);

      return () => {
        document.removeEventListener('keydown', handleKeyDown);
        document.removeEventListener('mousedown', handleMouseDown);
      };
    };

    // Detect system preferences
    const detectSystemPreferences = () => {
      // High contrast mode
      const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
      setIsHighContrastMode(highContrastQuery.matches);
      highContrastQuery.addEventListener('change', (e) => setIsHighContrastMode(e.matches));

      // Reduced motion
      const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      setIsReducedMotionMode(reducedMotionQuery.matches);
      reducedMotionQuery.addEventListener('change', (e) => setIsReducedMotionMode(e.matches));

      return () => {
        highContrastQuery.removeEventListener('change', (e) => setIsHighContrastMode(e.matches));
        reducedMotionQuery.removeEventListener('change', (e) => setIsReducedMotionMode(e.matches));
      };
    };

    detectScreenReader();
    const cleanupKeyboard = detectKeyboardUser();
    const cleanupSystem = detectSystemPreferences();

    return () => {
      cleanupKeyboard();
      cleanupSystem();
    };
  }, [enableAutoDetection]);

  // Screen reader announcement functions
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (!settings.screenReader.announceStatusUpdates) return;

    // Create or update live region
    let liveRegion = document.getElementById('tta-live-region');
    if (!liveRegion) {
      liveRegion = document.createElement('div');
      liveRegion.id = 'tta-live-region';
      liveRegion.setAttribute('aria-live', priority);
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.style.position = 'absolute';
      liveRegion.style.left = '-10000px';
      liveRegion.style.width = '1px';
      liveRegion.style.height = '1px';
      liveRegion.style.overflow = 'hidden';
      document.body.appendChild(liveRegion);
    }

    // Update the live region
    liveRegion.textContent = message;

    // Clear after announcement
    setTimeout(() => {
      if (liveRegion) {
        liveRegion.textContent = '';
      }
    }, 1000);
  }, [settings.screenReader.announceStatusUpdates]);

  const announcePageChange = useCallback((title: string, description?: string) => {
    if (!settings.screenReader.announcePageChanges) return;

    const message = description
      ? `Page changed to ${title}. ${description}`
      : `Page changed to ${title}`;
    announce(message, 'assertive');
  }, [settings.screenReader.announcePageChanges, announce]);

  const announceError = useCallback((error: string, field?: string) => {
    if (!settings.screenReader.announceFormErrors) return;

    const message = field
      ? `Error in ${field}: ${error}`
      : `Error: ${error}`;
    announce(message, 'assertive');
  }, [settings.screenReader.announceFormErrors, announce]);

  const announceStatus = useCallback((
    status: string,
    type: 'success' | 'warning' | 'error' | 'info' = 'info'
  ) => {
    if (!settings.screenReader.announceStatusUpdates) return;

    const prefix = therapeuticMode ? 'Therapeutic system: ' : '';
    const message = `${prefix}${type}: ${status}`;
    announce(message, type === 'error' ? 'assertive' : 'polite');
  }, [settings.screenReader.announceStatusUpdates, announce, therapeuticMode]);

  // Keyboard navigation helpers
  const focusElement = useCallback((selector: string): boolean => {
    try {
      const element = document.querySelector(selector) as HTMLElement;
      if (element && typeof element.focus === 'function') {
        element.focus();
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }, []);

  const trapFocus = useCallback((container: HTMLElement) => {
    if (!settings.keyboard.focusTrapping) return () => {};

    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    container.addEventListener('keydown', handleKeyDown);

    // Focus first element
    if (firstElement) {
      firstElement.focus();
    }

    return () => {
      container.removeEventListener('keydown', handleKeyDown);
    };
  }, [settings.keyboard.focusTrapping]);

  const createSkipLink = useCallback((target: string, label: string) => {
    if (!settings.keyboard.skipLinks) return;

    const skipLink = document.createElement('a');
    skipLink.href = `#${target}`;
    skipLink.textContent = label;
    skipLink.className = 'skip-link';
    skipLink.style.position = 'absolute';
    skipLink.style.top = '-40px';
    skipLink.style.left = '6px';
    skipLink.style.background = '#000';
    skipLink.style.color = '#fff';
    skipLink.style.padding = '8px';
    skipLink.style.textDecoration = 'none';
    skipLink.style.zIndex = '1000';

    skipLink.addEventListener('focus', () => {
      skipLink.style.top = '6px';
    });

    skipLink.addEventListener('blur', () => {
      skipLink.style.top = '-40px';
    });

    document.body.insertBefore(skipLink, document.body.firstChild);
  }, [settings.keyboard.skipLinks]);

  // ARIA helpers
  const generateAriaLabel = useCallback((base: string, context?: string): string => {
    if (!context) return base;

    const verbose = settings.screenReader.verboseDescriptions;
    return verbose ? `${base} - ${context}` : base;
  }, [settings.screenReader.verboseDescriptions]);

  const generateAriaDescription = useCallback((description: string, verbose?: boolean): string => {
    const useVerbose = verbose !== undefined ? verbose : settings.screenReader.verboseDescriptions;

    if (therapeuticMode && useVerbose) {
      return `Therapeutic interface: ${description}`;
    }

    return description;
  }, [settings.screenReader.verboseDescriptions, therapeuticMode]);

  // WCAG compliance checking (basic implementation)
  const checkWCAGCompliance = useCallback((element: HTMLElement): AccessibilityIssue[] => {
    const issues: AccessibilityIssue[] = [];

    // Check for missing alt text on images
    const images = element.querySelectorAll('img');
    images.forEach((img, index) => {
      if (!img.alt && !img.getAttribute('aria-label')) {
        issues.push({
          type: 'error',
          rule: 'WCAG 1.1.1',
          description: 'Image missing alternative text',
          element: `img[${index}]`,
          suggestion: 'Add alt attribute or aria-label to describe the image',
        });
      }
    });

    // Check for missing form labels
    const inputs = element.querySelectorAll('input, select, textarea');
    inputs.forEach((input, index) => {
      const hasLabel = input.getAttribute('aria-label') ||
                      input.getAttribute('aria-labelledby') ||
                      element.querySelector(`label[for="${input.id}"]`);

      if (!hasLabel) {
        issues.push({
          type: 'error',
          rule: 'WCAG 3.3.2',
          description: 'Form control missing label',
          element: `${input.tagName.toLowerCase()}[${index}]`,
          suggestion: 'Add a label element or aria-label attribute',
        });
      }
    });

    // Check color contrast (simplified)
    const textElements = element.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6');
    textElements.forEach((el, index) => {
      const styles = window.getComputedStyle(el);
      const color = styles.color;
      const backgroundColor = styles.backgroundColor;

      // This is a simplified check - in production, you'd use a proper contrast ratio calculator
      if (color === backgroundColor) {
        issues.push({
          type: 'warning',
          rule: 'WCAG 1.4.3',
          description: 'Potential color contrast issue',
          element: `${el.tagName.toLowerCase()}[${index}]`,
          suggestion: 'Ensure sufficient color contrast between text and background',
        });
      }
    });

    return issues;
  }, []);

  const validateForm = useCallback((form: HTMLFormElement): FormAccessibilityReport => {
    const issues = checkWCAGCompliance(form);
    const errorCount = issues.filter(issue => issue.type === 'error').length;
    const warningCount = issues.filter(issue => issue.type === 'warning').length;

    const score = Math.max(0, 100 - (errorCount * 20) - (warningCount * 5));
    const isAccessible = errorCount === 0;

    const recommendations = [
      'Ensure all form controls have labels',
      'Provide clear error messages',
      'Use fieldsets for related form controls',
      'Ensure keyboard navigation works properly',
    ];

    return {
      isAccessible,
      issues,
      score,
      recommendations,
    };
  }, [checkWCAGCompliance]);

  const value: AccessibilityContextType = {
    settings,
    updateSettings,
    resetSettings,
    announce,
    announcePageChange,
    announceError,
    announceStatus,
    focusElement,
    trapFocus,
    createSkipLink,
    generateAriaLabel,
    generateAriaDescription,
    isScreenReaderActive,
    isKeyboardUser,
    isHighContrastMode,
    isReducedMotionMode,
    checkWCAGCompliance,
    validateForm,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
};

export default AccessibilityProvider;
