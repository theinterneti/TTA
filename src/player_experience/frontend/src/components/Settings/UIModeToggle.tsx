/**
 * UI Mode Toggle Component
 *
 * Allows users to switch between Entertainment and Clinical interface modes
 */

import React, { useState, useEffect } from 'react';
import { useTranslation, UIMode } from '../../services/terminologyTranslation';
import { UIModeUtils } from '../../config/uiMode';

interface UIModeToggleProps {
  className?: string;
  showLabels?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const UIModeToggle: React.FC<UIModeToggleProps> = ({
  className = '',
  showLabels = true,
  size = 'md'
}) => {
  const { getMode, setMode, isEntertainmentMode } = useTranslation();
  const [currentMode, setCurrentMode] = useState<UIMode>(getMode());
  const [isToggling, setIsToggling] = useState(false);

  // Load user preference on component mount
  useEffect(() => {
    const savedPreference = UIModeUtils.loadUserPreference();
    if (savedPreference) {
      setMode(savedPreference);
      setCurrentMode(savedPreference);
    }
  }, [setMode]);

  const handleModeToggle = async () => {
    if (isToggling) return;

    setIsToggling(true);

    try {
      const newMode = currentMode === UIMode.ENTERTAINMENT ? UIMode.CLINICAL : UIMode.ENTERTAINMENT;

      // Update the translation service
      setMode(newMode);
      setCurrentMode(newMode);

      // Save user preference
      UIModeUtils.saveUserPreference(newMode);

      // Optional: Trigger a page refresh to update all components
      // This ensures all components re-render with the new mode
      setTimeout(() => {
        window.location.reload();
      }, 300);

    } catch (error) {
      console.error('Failed to toggle UI mode:', error);
    } finally {
      setIsToggling(false);
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'w-12 h-6';
      case 'lg':
        return 'w-16 h-8';
      default:
        return 'w-14 h-7';
    }
  };

  const getToggleClasses = () => {
    const baseClasses = 'relative inline-flex items-center rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2';
    const sizeClasses = getSizeClasses();
    const colorClasses = isEntertainmentMode()
      ? 'bg-purple-600 hover:bg-purple-700'
      : 'bg-blue-600 hover:bg-blue-700';

    return `${baseClasses} ${sizeClasses} ${colorClasses}`;
  };

  const getKnobClasses = () => {
    const baseClasses = 'inline-block rounded-full bg-white shadow transform transition-transform duration-300';
    const sizeClasses = size === 'sm' ? 'w-5 h-5' : size === 'lg' ? 'w-7 h-7' : 'w-6 h-6';
    const positionClasses = isEntertainmentMode()
      ? (size === 'sm' ? 'translate-x-6' : size === 'lg' ? 'translate-x-8' : 'translate-x-7')
      : 'translate-x-1';

    return `${baseClasses} ${sizeClasses} ${positionClasses}`;
  };

  if (!UIModeUtils.shouldShowModeToggle()) {
    return null;
  }

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {showLabels && (
        <div className="flex items-center space-x-2 text-sm">
          <span className={`transition-colors duration-200 ${
            !isEntertainmentMode() ? 'text-blue-600 font-medium' : 'text-gray-500'
          }`}>
            Clinical
          </span>
        </div>
      )}

      <button
        type="button"
        onClick={handleModeToggle}
        disabled={isToggling}
        className={getToggleClasses()}
        aria-pressed={isEntertainmentMode()}
        aria-label={`Switch to ${isEntertainmentMode() ? 'clinical' : 'entertainment'} mode`}
      >
        <span className={getKnobClasses()}>
          {isToggling && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-3 h-3 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin"></div>
            </div>
          )}
        </span>
      </button>

      {showLabels && (
        <div className="flex items-center space-x-2 text-sm">
          <span className={`transition-colors duration-200 ${
            isEntertainmentMode() ? 'text-purple-600 font-medium' : 'text-gray-500'
          }`}>
            Adventure
          </span>
        </div>
      )}
    </div>
  );
};

/**
 * Compact version for use in headers or toolbars
 */
export const CompactUIModeToggle: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <UIModeToggle
      className={className}
      showLabels={false}
      size="sm"
    />
  );
};

/**
 * Full-featured version for settings pages
 */
export const FullUIModeToggle: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { isEntertainmentMode } = useTranslation();

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Interface Style
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Choose how you'd like the interface to be presented. Adventure mode uses
            gaming language and focuses on storytelling, while Clinical mode uses
            professional therapeutic terminology.
          </p>

          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                !isEntertainmentMode() ? 'bg-blue-500' : 'bg-gray-300'
              }`}></div>
              <div>
                <p className="font-medium text-gray-900">Clinical Mode</p>
                <p className="text-sm text-gray-600">Professional therapeutic interface with clinical terminology</p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                isEntertainmentMode() ? 'bg-purple-500' : 'bg-gray-300'
              }`}></div>
              <div>
                <p className="font-medium text-gray-900">Adventure Mode</p>
                <p className="text-sm text-gray-600">Gaming-focused interface with storytelling language</p>
              </div>
            </div>
          </div>
        </div>

        <div className="ml-6">
          <UIModeToggle size="lg" />
        </div>
      </div>
    </div>
  );
};

export default UIModeToggle;
