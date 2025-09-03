import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface InterfacePreviewProps {
  interface: {
    id: string;
    name: string;
    description: string;
    port: number;
    url: string;
    directUrl: string;
    icon: React.ComponentType<any>;
    color: string;
    status: 'healthy' | 'unhealthy' | 'unknown';
    features: string[];
    technology: string[];
  };
  onError?: () => void;
}

export const InterfacePreview: React.FC<InterfacePreviewProps> = ({
  interface: interface_,
  onError
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [iframeKey, setIframeKey] = useState(0);

  const handleIframeLoad = () => {
    setIsLoading(false);
    setHasError(false);
  };

  const handleIframeError = () => {
    setIsLoading(false);
    setHasError(true);
    onError?.();
  };

  const refreshPreview = () => {
    setIsLoading(true);
    setHasError(false);
    setIframeKey(prev => prev + 1);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  useEffect(() => {
    // Reset loading state when interface changes
    setIsLoading(true);
    setHasError(false);
    setIframeKey(prev => prev + 1);
  }, [interface_.id]);

  if (hasError) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center"
      >
        <div className="flex flex-col items-center space-y-4">
          <div className="p-3 bg-red-100 rounded-full">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Preview Unavailable
            </h3>
            <p className="text-gray-600 mb-4">
              Unable to load preview for {interface_.name}. The interface may not be running or accessible.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={refreshPreview}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Retry
              </button>
              <button
                onClick={() => window.open(interface_.directUrl, '_blank')}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                Open Direct
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden ${
        isFullscreen ? 'fixed inset-4 z-50' : ''
      }`}
    >
      {/* Preview Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-3">
          <div className={`p-1.5 rounded ${interface_.color}`}>
            <interface_.icon className="h-4 w-4 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-900">{interface_.name}</h3>
            <p className="text-xs text-gray-600">{interface_.directUrl}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {isLoading && (
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent" />
              <span>Loading...</span>
            </div>
          )}

          <button
            onClick={refreshPreview}
            className="p-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
            title="Refresh preview"
          >
            <ArrowPathIcon className="h-4 w-4" />
          </button>

          <button
            onClick={toggleFullscreen}
            className="p-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
            title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          >
            {isFullscreen ? (
              <ArrowsPointingInIcon className="h-4 w-4" />
            ) : (
              <ArrowsPointingOutIcon className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Preview Content */}
      <div className={`relative ${isFullscreen ? 'h-full' : 'h-96 md:h-[600px]'}`}>
        <iframe
          key={iframeKey}
          src={interface_.directUrl}
          className="w-full h-full border-0"
          title={`${interface_.name} Preview`}
          onLoad={handleIframeLoad}
          onError={handleIframeError}
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox"
        />

        {/* Loading Overlay */}
        {isLoading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
            <div className="flex flex-col items-center space-y-3">
              <div className="animate-spin rounded-full h-8 w-8 border-3 border-blue-600 border-t-transparent" />
              <p className="text-sm text-gray-600">Loading {interface_.name}...</p>
            </div>
          </div>
        )}
      </div>

      {/* Preview Footer */}
      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-600">Status:</span>
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                interface_.status === 'healthy' ? 'bg-green-100 text-green-800' :
                interface_.status === 'unhealthy' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {interface_.status}
              </span>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-600">Port:</span>
              <code className="text-xs font-mono bg-gray-200 px-1.5 py-0.5 rounded">
                {interface_.port}
              </code>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-600">
              Preview may not reflect real-time changes
            </span>
            <button
              onClick={() => window.open(interface_.directUrl, '_blank')}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium"
            >
              Open in new tab →
            </button>
          </div>
        </div>
      </div>

      {/* Fullscreen Backdrop */}
      {isFullscreen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={toggleFullscreen}
        />
      )}
    </motion.div>
  );
};
