import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  FunnelIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { useAppSelector, useAppDispatch } from '../../store/store';
import { setNetworkFilters, clearNetworkEvents } from '../../store/slices/debugSlice';

export const NetworkMonitor: React.FC = () => {
  const dispatch = useAppDispatch();
  const { networkEvents, networkFilters } = useAppSelector(state => state.debug);
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredEvents = useMemo(() => {
    return networkEvents.filter(event => {
      // Method filter
      if (networkFilters.method.length > 0 && !networkFilters.method.includes(event.method)) {
        return false;
      }

      // Status filter
      if (networkFilters.status.length > 0) {
        const statusRange = event.status.toString().charAt(0) + 'xx';
        if (!networkFilters.status.includes(statusRange) && !networkFilters.status.includes(event.status.toString())) {
          return false;
        }
      }

      // URL filter
      if (networkFilters.url && !event.url.toLowerCase().includes(networkFilters.url.toLowerCase())) {
        return false;
      }

      // Search term
      if (searchTerm && !event.url.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }

      return true;
    });
  }, [networkEvents, networkFilters, searchTerm]);

  const getStatusIcon = (status: number) => {
    if (status >= 200 && status < 300) {
      return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
    } else if (status >= 400 && status < 500) {
      return <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500" />;
    } else if (status >= 500) {
      return <XCircleIcon className="h-4 w-4 text-red-500" />;
    }
    return <ClockIcon className="h-4 w-4 text-gray-400" />;
  };

  const getStatusColor = (status: number) => {
    if (status >= 200 && status < 300) return 'text-green-600';
    if (status >= 400 && status < 500) return 'text-yellow-600';
    if (status >= 500) return 'text-red-600';
    return 'text-gray-600';
  };

  const getMethodColor = (method: string) => {
    switch (method.toUpperCase()) {
      case 'GET': return 'bg-blue-100 text-blue-800';
      case 'POST': return 'bg-green-100 text-green-800';
      case 'PUT': return 'bg-yellow-100 text-yellow-800';
      case 'DELETE': return 'bg-red-100 text-red-800';
      case 'PATCH': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const selectedEventData = selectedEvent ? networkEvents.find(e => e.id === selectedEvent) : null;

  return (
    <div className="h-full flex">
      {/* Events List */}
      <div className="flex-1 flex flex-col">
        {/* Filters and Search */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search URLs..."
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
                    dispatch(setNetworkFilters({
                      method: [...networkFilters.method, e.target.value]
                    }));
                  }
                }}
                className="text-sm border border-gray-300 rounded-md px-2 py-1"
              >
                <option value="">Method</option>
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
                <option value="PATCH">PATCH</option>
              </select>

              <select
                value=""
                onChange={(e) => {
                  if (e.target.value) {
                    dispatch(setNetworkFilters({
                      status: [...networkFilters.status, e.target.value]
                    }));
                  }
                }}
                className="text-sm border border-gray-300 rounded-md px-2 py-1"
              >
                <option value="">Status</option>
                <option value="2xx">2xx</option>
                <option value="3xx">3xx</option>
                <option value="4xx">4xx</option>
                <option value="5xx">5xx</option>
              </select>

              <button
                onClick={() => dispatch(clearNetworkEvents())}
                className="text-sm px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Active Filters */}
          {(networkFilters.method.length > 0 || networkFilters.status.length > 0) && (
            <div className="mt-2 flex flex-wrap gap-2">
              {networkFilters.method.map(method => (
                <span
                  key={method}
                  className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
                >
                  {method}
                  <button
                    onClick={() => dispatch(setNetworkFilters({
                      method: networkFilters.method.filter(m => m !== method)
                    }))}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
              {networkFilters.status.map(status => (
                <span
                  key={status}
                  className="inline-flex items-center px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full"
                >
                  {status}
                  <button
                    onClick={() => dispatch(setNetworkFilters({
                      status: networkFilters.status.filter(s => s !== status)
                    }))}
                    className="ml-1 text-green-600 hover:text-green-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Events Table */}
        <div className="flex-1 overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-700">Method</th>
                <th className="px-4 py-2 text-left font-medium text-gray-700">URL</th>
                <th className="px-4 py-2 text-left font-medium text-gray-700">Status</th>
                <th className="px-4 py-2 text-left font-medium text-gray-700">Time</th>
                <th className="px-4 py-2 text-left font-medium text-gray-700">Duration</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((event) => (
                <motion.tr
                  key={event.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className={`border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                    selectedEvent === event.id ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => setSelectedEvent(event.id)}
                >
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getMethodColor(event.method)}`}>
                      {event.method}
                    </span>
                  </td>
                  <td className="px-4 py-2 font-mono text-xs truncate max-w-xs" title={event.url}>
                    {event.url}
                  </td>
                  <td className="px-4 py-2">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(event.status)}
                      <span className={`font-medium ${getStatusColor(event.status)}`}>
                        {event.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-2 text-gray-600">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="px-4 py-2 text-gray-600">
                    {event.duration}ms
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>

          {filteredEvents.length === 0 && (
            <div className="flex items-center justify-center h-32 text-gray-500">
              No network events found
            </div>
          )}
        </div>
      </div>

      {/* Event Details */}
      {selectedEventData && (
        <div className="w-96 border-l border-gray-200 bg-gray-50 overflow-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Request Details</h3>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">General</h4>
                <div className="space-y-1 text-sm">
                  <div><span className="text-gray-600">URL:</span> <code className="text-xs">{selectedEventData.url}</code></div>
                  <div><span className="text-gray-600">Method:</span> {selectedEventData.method}</div>
                  <div><span className="text-gray-600">Status:</span> {selectedEventData.status}</div>
                  <div><span className="text-gray-600">Duration:</span> {selectedEventData.duration}ms</div>
                  <div><span className="text-gray-600">Time:</span> {new Date(selectedEventData.timestamp).toLocaleString()}</div>
                </div>
              </div>

              {selectedEventData.requestHeaders && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Request Headers</h4>
                  <pre className="text-xs bg-white p-2 rounded border overflow-auto max-h-32">
                    {JSON.stringify(selectedEventData.requestHeaders, null, 2)}
                  </pre>
                </div>
              )}

              {selectedEventData.responseHeaders && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Response Headers</h4>
                  <pre className="text-xs bg-white p-2 rounded border overflow-auto max-h-32">
                    {JSON.stringify(selectedEventData.responseHeaders, null, 2)}
                  </pre>
                </div>
              )}

              {selectedEventData.requestBody && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Request Body</h4>
                  <pre className="text-xs bg-white p-2 rounded border overflow-auto max-h-32">
                    {typeof selectedEventData.requestBody === 'string'
                      ? selectedEventData.requestBody
                      : JSON.stringify(selectedEventData.requestBody, null, 2)
                    }
                  </pre>
                </div>
              )}

              {selectedEventData.responseBody && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Response Body</h4>
                  <pre className="text-xs bg-white p-2 rounded border overflow-auto max-h-32">
                    {typeof selectedEventData.responseBody === 'string'
                      ? selectedEventData.responseBody
                      : JSON.stringify(selectedEventData.responseBody, null, 2)
                    }
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
