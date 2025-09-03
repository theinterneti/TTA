import React, { useState, useMemo, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  DocumentTextIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline';
import { useAppSelector, useAppDispatch } from '../../store/store';
import { setConsoleFilters, clearConsoleLogs } from '../../store/slices/debugSlice';

export const ConsoleAggregator: React.FC = () => {
  const dispatch = useAppDispatch();
  const { consoleLogs, consoleFilters } = useAppSelector(state => state.debug);
  const [searchTerm, setSearchTerm] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const filteredLogs = useMemo(() => {
    return consoleLogs.filter(log => {
      // Level filter
      if (consoleFilters.level.length > 0 && !consoleFilters.level.includes(log.level)) {
        return false;
      }

      // Source filter
      if (consoleFilters.source && log.source && !log.source.toLowerCase().includes(consoleFilters.source.toLowerCase())) {
        return false;
      }

      // Search term
      if (searchTerm && !log.message.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }

      return true;
    });
  }, [consoleLogs, consoleFilters, searchTerm]);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [filteredLogs, autoScroll]);

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'error':
        return <XCircleIcon className="h-4 w-4 text-red-500" />;
      case 'warn':
        return <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500" />;
      case 'info':
        return <InformationCircleIcon className="h-4 w-4 text-blue-500" />;
      case 'debug':
        return <DocumentTextIcon className="h-4 w-4 text-purple-500" />;
      default:
        return <DocumentTextIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-red-700 bg-red-50 border-l-red-500';
      case 'warn':
        return 'text-yellow-700 bg-yellow-50 border-l-yellow-500';
      case 'info':
        return 'text-blue-700 bg-blue-50 border-l-blue-500';
      case 'debug':
        return 'text-purple-700 bg-purple-50 border-l-purple-500';
      default:
        return 'text-gray-700 bg-gray-50 border-l-gray-500';
    }
  };

  const logsByLevel = useMemo(() => {
    const levels: { [key: string]: number } = {};
    consoleLogs.forEach(log => {
      levels[log.level] = (levels[log.level] || 0) + 1;
    });
    return levels;
  }, [consoleLogs]);

  const formatMessage = (message: string) => {
    // Simple formatting for common patterns
    try {
      // Try to parse as JSON for better formatting
      const parsed = JSON.parse(message);
      return JSON.stringify(parsed, null, 2);
    } catch {
      // Return as-is if not JSON
      return message;
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Filters and Controls */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-4 mb-3">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search console logs..."
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
                  dispatch(setConsoleFilters({
                    level: [...consoleFilters.level, e.target.value]
                  }));
                }
              }}
              className="text-sm border border-gray-300 rounded-md px-2 py-1"
            >
              <option value="">Level</option>
              <option value="log">Log</option>
              <option value="info">Info</option>
              <option value="warn">Warn</option>
              <option value="error">Error</option>
              <option value="debug">Debug</option>
            </select>

            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span>Auto-scroll</span>
            </label>

            <button
              onClick={() => dispatch(clearConsoleLogs())}
              className="text-sm px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Log Statistics */}
        <div className="flex items-center space-x-4 mb-3">
          <span className="text-sm text-gray-600">Total: {consoleLogs.length}</span>
          {Object.entries(logsByLevel).map(([level, count]) => (
            <div key={level} className="flex items-center space-x-1">
              {getLevelIcon(level)}
              <span className="text-sm text-gray-600">{count}</span>
            </div>
          ))}
        </div>

        {/* Active Filters */}
        {consoleFilters.level.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {consoleFilters.level.map(level => (
              <span
                key={level}
                className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
              >
                {level}
                <button
                  onClick={() => dispatch(setConsoleFilters({
                    level: consoleFilters.level.filter(l => l !== level)
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

      {/* Console Logs */}
      <div className="flex-1 overflow-auto font-mono text-sm">
        {filteredLogs.map((log) => (
          <motion.div
            key={log.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`border-l-2 px-4 py-2 ${getLevelColor(log.level)}`}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-0.5">
                {getLevelIcon(log.level)}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-xs font-medium uppercase tracking-wide">
                    {log.level}
                  </span>
                  {log.source && (
                    <span className="text-xs text-gray-500">
                      [{log.source}]
                    </span>
                  )}
                  <span className="text-xs text-gray-400">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <div className="text-sm">
                  <pre className="whitespace-pre-wrap break-words">
                    {formatMessage(log.message)}
                  </pre>
                </div>
              </div>
            </div>
          </motion.div>
        ))}

        {filteredLogs.length === 0 && (
          <div className="flex items-center justify-center h-32 text-gray-500">
            {consoleLogs.length === 0 ? 'No console logs recorded' : 'No logs match the current filters'}
          </div>
        )}

        <div ref={logsEndRef} />
      </div>

      {/* Auto-scroll indicator */}
      {!autoScroll && (
        <div className="absolute bottom-4 right-4">
          <button
            onClick={() => {
              setAutoScroll(true);
              logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors"
          >
            <ArrowDownIcon className="h-4 w-4" />
            <span className="text-sm">Scroll to bottom</span>
          </button>
        </div>
      )}
    </div>
  );
};
