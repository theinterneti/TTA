import React, { useState } from 'react';

interface InteractiveButtonProps {
  id: string;
  text: string;
  action: string;
  variant?: 'primary' | 'secondary' | 'therapeutic' | 'crisis' | 'success';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  disabled?: boolean;
  loading?: boolean;
  onClick: (id: string, action: string) => void;
  metadata?: {
    therapeutic_technique?: string;
    safety_level?: 'safe' | 'caution' | 'crisis';
    expected_outcome?: string;
    confidence_level?: number; // 0-1
  };
}

const InteractiveButton: React.FC<InteractiveButtonProps> = ({
  id,
  text,
  action,
  variant = 'primary',
  size = 'md',
  icon,
  disabled = false,
  loading = false,
  onClick,
  metadata,
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          base: 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600',
          pressed: 'bg-blue-800 scale-95',
          disabled: 'bg-gray-300 text-gray-500 cursor-not-allowed',
        };
      case 'secondary':
        return {
          base: 'bg-gray-100 hover:bg-gray-200 text-gray-900 border-gray-300',
          pressed: 'bg-gray-300 scale-95',
          disabled: 'bg-gray-50 text-gray-400 cursor-not-allowed',
        };
      case 'therapeutic':
        return {
          base: 'bg-green-600 hover:bg-green-700 text-white border-green-600',
          pressed: 'bg-green-800 scale-95',
          disabled: 'bg-gray-300 text-gray-500 cursor-not-allowed',
        };
      case 'crisis':
        return {
          base: 'bg-red-600 hover:bg-red-700 text-white border-red-600',
          pressed: 'bg-red-800 scale-95',
          disabled: 'bg-gray-300 text-gray-500 cursor-not-allowed',
        };
      case 'success':
        return {
          base: 'bg-emerald-600 hover:bg-emerald-700 text-white border-emerald-600',
          pressed: 'bg-emerald-800 scale-95',
          disabled: 'bg-gray-300 text-gray-500 cursor-not-allowed',
        };
      default:
        return {
          base: 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600',
          pressed: 'bg-blue-800 scale-95',
          disabled: 'bg-gray-300 text-gray-500 cursor-not-allowed',
        };
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return 'px-3 py-1.5 text-xs';
      case 'md':
        return 'px-4 py-2 text-sm';
      case 'lg':
        return 'px-6 py-3 text-base';
      default:
        return 'px-4 py-2 text-sm';
    }
  };

  const getSafetyIndicator = () => {
    if (!metadata?.safety_level) return null;

    switch (metadata.safety_level) {
      case 'crisis':
        return (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white">
            <div className="w-full h-full bg-red-500 rounded-full animate-ping" />
          </div>
        );
      case 'caution':
        return (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-500 rounded-full border-2 border-white" />
        );
      case 'safe':
        return (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white" />
        );
      default:
        return null;
    }
  };

  const getConfidenceBar = () => {
    if (!metadata?.confidence_level) return null;

    const confidence = Math.round(metadata.confidence_level * 100);
    const getConfidenceColor = () => {
      if (confidence >= 80) return 'bg-green-500';
      if (confidence >= 60) return 'bg-yellow-500';
      return 'bg-red-500';
    };

    return (
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200 rounded-b">
        <div 
          className={`h-full rounded-b transition-all duration-300 ${getConfidenceColor()}`}
          style={{ width: `${confidence}%` }}
        />
      </div>
    );
  };

  const handleClick = () => {
    if (disabled || loading) return;
    
    setIsPressed(true);
    setTimeout(() => setIsPressed(false), 150);
    onClick(id, action);
  };

  const handleMouseDown = () => {
    if (!disabled && !loading) {
      setIsPressed(true);
    }
  };

  const handleMouseUp = () => {
    setIsPressed(false);
  };

  const styles = getVariantStyles();
  const sizeStyles = getSizeStyles();

  return (
    <div className="relative inline-block">
      <button
        onClick={handleClick}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={(e) => {
          handleMouseUp(e);
          setShowTooltip(false);
        }}
        onMouseEnter={() => setShowTooltip(true)}
        disabled={disabled || loading}
        className={`
          relative w-full text-left border rounded-lg font-medium transition-all duration-200 
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          touch-manipulation select-none
          ${sizeStyles}
          ${disabled || loading 
            ? styles.disabled 
            : isPressed 
              ? styles.pressed 
              : styles.base
          }
          ${loading ? 'cursor-wait' : disabled ? 'cursor-not-allowed' : 'cursor-pointer'}
          min-h-[44px] min-w-[44px] // Minimum touch target size
        `}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {icon && (
              <span className={`${loading ? 'animate-spin' : ''}`}>
                {loading ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                ) : (
                  icon
                )}
              </span>
            )}
            <span>{text}</span>
          </div>

          {/* Therapeutic technique indicator */}
          {metadata?.therapeutic_technique && (
            <span className="text-xs opacity-75 bg-white bg-opacity-20 px-2 py-1 rounded-full">
              {metadata.therapeutic_technique}
            </span>
          )}
        </div>

        {/* Safety indicator */}
        {getSafetyIndicator()}

        {/* Confidence bar */}
        {getConfidenceBar()}
      </button>

      {/* Tooltip */}
      {showTooltip && (metadata?.expected_outcome || metadata?.confidence_level) && (
        <div className="absolute z-10 bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg max-w-xs">
          <div className="text-center">
            {metadata.expected_outcome && (
              <p className="mb-1">{metadata.expected_outcome}</p>
            )}
            {metadata.confidence_level && (
              <p className="text-gray-300">
                Confidence: {Math.round(metadata.confidence_level * 100)}%
              </p>
            )}
          </div>
          {/* Tooltip arrow */}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
        </div>
      )}

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-50 rounded-lg flex items-center justify-center">
          <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
};

export default InteractiveButton;