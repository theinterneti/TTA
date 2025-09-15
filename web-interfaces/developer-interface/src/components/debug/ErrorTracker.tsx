import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { useAppSelector, useAppDispatch } from '../../store/store';
import { setErrorFilters, clearErrorEvents } from '../../store/slices/debugSlice';

export const ErrorTracker: React.FC = () => {
  const dispatch = useAppDispatch();
  const { errorEvents, errorFilters } = useAppSelector(state => state.debug);
  const [selectedError, setSelectedError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredErrors = useMemo(() => {
    return errorEvents.filter(error => {
      // Severity filter
      if (errorFilters.severity.length > 0 && !errorFilters.severity.includes(error.severity)) {
        return false;
      }

      // Context filter
      if (errorFilters.context && !error.context.toLowerCase().includes(errorFilters.context.toLowerCase())) {
        return false;
      }

      // Search term
      if (searchTerm && !error.message.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }

      return true;
    });
  }, [errorEvents, errorFilters, searchTerm]);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircleIcon className="h-4 w-4 text-red-600" />;
      case 'high':
        return <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />;
      case 'medium':
        return <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500" />;
      case 'low':
        return <InformationCircleIcon className="h-4 w-4 text-blue-500" />;
      default:
        return <InformationCircleIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-red-50 text-red-700 border-red-100';
      case 'medium':
        return 'bg-yellow-50 text-yellow-700 border-yellow-100';
      case 'low':
        return 'bg-blue-50 text-blue-700 border-blue-100';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-100';
    }
  };

  const selectedErrorData = selectedError ? errorEvents.find(e => e.id === selectedError) : null;

  const errorsByContext = useMemo(() => {
    const contexts: { [key: string]: number } = {};
    errorEvents.forEach(error => {
      contexts[error.context] = (contexts[error.context] || 0) + 1;
    });
    return contexts;
  }, [errorEvents]);

  const errorsBySeverity = useMemo(() => {
    const severities: { [key: string]: number } = {};
    errorEvents.forEach(error => {
      severities[error.severity] = (severities[error.severity] || 0) + 1;
    });
    return severities;
  }, [errorEvents]);

  return (
    <div className="h-full flex">
      {/* Errors List */}
      <div className="flex-1 flex flex-col">
        {/* Filters and Search */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-4 mb-3">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search error messages..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="flex items-center space-x-2">
              <FunnelIcon className="h-4 w-4 text-gray-400" />
              <select
                value=""
                onChange={(e) => {
                  if (e.target.value) {
                    dispatch(setErrorFilters({
                      severity: [...errorFilters.severity, e.target.value]
                    }));
                  }
                }}
                className="text-sm border border-gray-300 rounded-md px-2 py-1"
              >
                <option value="">Severity</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>

              <button
                onClick={() => dispatch(clearErrorEvents())}
                className="text-sm px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Error Statistics */}
          <div className="grid grid-cols-2 gap-4 mb-3">
            <div>
              <h4 className="text-xs font-medium text-gray-700 mb-1">By Severity</h4>
              <div className="flex flex-wrap gap-1">
                {Object.entries(errorsBySeverity).map(([severity, count]) => (
                  <span
                    key={severity}
                    className={`inline-flex items-center px-2 py-1 text-xs rounded-full ${getSeverityColor(severity)}`}
                  >
                    {severity}: {count}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-xs font-medium text-gray-700 mb-1">By Context</h4>
              <div className="flex flex-wrap gap-1">
                {Object.entries(errorsByContext).slice(0, 3).map(([context, count]) => (
                  <span
                    key={context}
                    className="inline-flex items-center px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full"
                  >
                    {context}: {count}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Active Filters */}
          {errorFilters.severity.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {errorFilters.severity.map(severity => (
                <span
                  key={severity}
                  className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
                >
                  {severity}
                  <button
                    onClick={() => dispatch(setErrorFilters({
                      severity: errorFilters.severity.filter(s => s !== severity)
                    }))}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Errors List */}
        <div className="flex-1 overflow-auto">
          <div className="divide-y divide-gray-100">
            {filteredErrors.map((error) => (
              <motion.div
                key={error.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className={`p-4 hover:bg-gray-50 cursor-pointer ${
                  selectedError === error.id ? 'bg-blue-50 border-l-2 border-blue-500' : ''
                }`}
                onClick={() => setSelectedError(error.id)}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {getSeverityIcon(error.severity)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full ${getSeverityColor(error.severity)}`}>
                        {error.severity}
                      </span>
                      <span className="text-xs text-gray-500">{error.context}</span>
                      <span className="text-xs text-gray-400">
                        {new Date(error.timestamp).toLocaleTimeString()}
                      </span>
                    </div>

                    <p className="text-sm text-gray-900 font-medium mb-1 truncate">
                      {error.message}
                    </p>

                    {error.stack && (
                      <p className="text-xs text-gray-600 font-mono truncate">
                        {error.stack.split('\n')[1]?.trim()}
                      </p>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {filteredErrors.length === 0 && (
            <div className="flex items-center justify-center h-32 text-gray-500">
              {errorEvents.length === 0 ? 'No errors recorded' : 'No errors match the current filters'}
            </div>
          )}
        </div>
      </div>

      {/* Error Details */}
      {selectedErrorData && (
        <div className="w-96 border-l border-gray-200 bg-gray-50 overflow-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Error Details</h3>
              <button
                onClick={() => setSelectedError(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              {/* Error Info */}
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  {getSeverityIcon(selectedErrorData.severity)}
                  <span className={`inline-flex items-center px-2 py-1 text-sm font-medium rounded-full ${getSeverityColor(selectedErrorData.severity)}`}>
                    {selectedErrorData.severity}
                  </span>
                </div>

                <div className="space-y-2 text-sm">
                  <div><span className="text-gray-600">Context:</span> {selectedErrorData.context}</div>
                  <div><span className="text-gray-600">Time:</span> {new Date(selectedErrorData.timestamp).toLocaleString()}</div>
                </div>
              </div>

              {/* Error Message */}
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Message</h4>
                <div className="bg-white p-3 rounded border text-sm">
                  {selectedErrorData.message}
                </div>
              </div>

              {/* Stack Trace */}
              {selectedErrorData.stack && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Stack Trace</h4>
                  <pre className="text-xs bg-white p-3 rounded border overflow-auto max-h-64 font-mono">
                    {selectedErrorData.stack}
                  </pre>
                </div>
              )}

              {/* Debugging Tips */}
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Debugging Tips</h4>
                <div className="space-y-2">
                  {selectedErrorData.severity === 'critical' && (
                    <div className="p-2 bg-red-50 rounded border border-red-200">
                      <div className="text-sm text-red-800">
                        <div className="font-medium">Critical Error</div>
                        <div>This error may cause application instability. Investigate immediately.</div>
                      </div>
                    </div>
                  )}

                  {selectedErrorData.message.includes('TypeError') && (
                    <div className="p-2 bg-blue-50 rounded border border-blue-200">
                      <div className="text-sm text-blue-800">
                        <div className="font-medium">Type Error</div>
                        <div>Check for undefined variables or incorrect property access.</div>
                      </div>
                    </div>
                  )}

                  {selectedErrorData.message.includes('Network') && (
                    <div className="p-2 bg-yellow-50 rounded border border-yellow-200">
                      <div className="text-sm text-yellow-800">
                        <div className="font-medium">Network Error</div>
                        <div>Check API endpoints and network connectivity.</div>
                      </div>
                    </div>
                  )}

                  <div className="p-2 bg-gray-50 rounded border border-gray-200">
                    <div className="text-sm text-gray-700">
                      <div className="font-medium">General Tips</div>
                      <ul className="list-disc list-inside mt-1 space-y-1">
                        <li>Check the browser console for additional context</li>
                        <li>Verify component props and state</li>
                        <li>Review recent code changes</li>
                        <li>Test in different browsers if UI-related</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
