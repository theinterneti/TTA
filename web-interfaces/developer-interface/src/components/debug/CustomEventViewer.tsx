import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  CubeIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  TagIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  CheckCircleIcon,
  PlusIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { customEventManager, CustomEventInstance, CustomEventDefinition, EventFilter } from '../../services/CustomEventManager';

export const CustomEventViewer: React.FC = () => {
  const [eventInstances, setEventInstances] = useState<CustomEventInstance[]>([]);
  const [eventDefinitions, setEventDefinitions] = useState<CustomEventDefinition[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<CustomEventInstance | null>(null);
  const [filter, setFilter] = useState<EventFilter>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [showDefinitions, setShowDefinitions] = useState(false);

  useEffect(() => {
    // Load initial data
    loadEventData();

    // Set up event listeners
    const handleEventCreated = (event: CustomEventInstance) => {
      setEventInstances(prev => [event, ...prev.slice(0, 999)]);
    };

    const handleDefinitionRegistered = (definition: CustomEventDefinition) => {
      setEventDefinitions(prev => [...prev, definition]);
    };

    customEventManager.on('event_instance_created', handleEventCreated);
    customEventManager.on('event_definition_registered', handleDefinitionRegistered);

    return () => {
      customEventManager.off('event_instance_created', handleEventCreated);
      customEventManager.off('event_definition_registered', handleDefinitionRegistered);
    };
  }, []);

  const loadEventData = () => {
    setEventInstances(customEventManager.getEventInstances());
    setEventDefinitions(customEventManager.getEventDefinitions());
  };

  const filteredEvents = useMemo(() => {
    const currentFilter: EventFilter = {
      ...filter,
      searchTerm: searchTerm || undefined
    };

    return customEventManager.getEventInstances(currentFilter);
  }, [eventInstances, filter, searchTerm]);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircleIcon className="h-4 w-4 text-red-600" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500" />;
      case 'info':
      default:
        return <InformationCircleIcon className="h-4 w-4 text-blue-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'error':
        return 'bg-red-50 text-red-700 border-red-100';
      case 'warning':
        return 'bg-yellow-50 text-yellow-700 border-yellow-100';
      case 'info':
      default:
        return 'bg-blue-50 text-blue-700 border-blue-100';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'user_interaction':
        return 'bg-green-100 text-green-800';
      case 'system_state':
        return 'bg-purple-100 text-purple-800';
      case 'performance':
        return 'bg-orange-100 text-orange-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'business_logic':
        return 'bg-indigo-100 text-indigo-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getInterfaceColor = (interfaceId: string) => {
    const colors = {
      'patient': 'bg-blue-100 text-blue-800',
      'clinical': 'bg-green-100 text-green-800',
      'admin': 'bg-red-100 text-red-800',
      'public': 'bg-yellow-100 text-yellow-800',
      'stakeholder': 'bg-purple-100 text-purple-800',
      'api-docs': 'bg-indigo-100 text-indigo-800',
      'developer': 'bg-gray-100 text-gray-800'
    };
    return colors[interfaceId as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const updateFilter = (key: keyof EventFilter, value: any) => {
    const newFilter = { ...filter, [key]: value };
    setFilter(newFilter);
    customEventManager.setEventFilter(newFilter);
  };

  const clearFilters = () => {
    setFilter({});
    setSearchTerm('');
    customEventManager.setEventFilter({});
  };

  const statistics = customEventManager.getEventStatistics();

  return (
    <div className="h-full flex">
      {/* Events List */}
      <div className="flex-1 flex flex-col">
        {/* Header and Filters */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <CubeIcon className="h-5 w-5 text-gray-700" />
              <h3 className="font-semibold text-gray-900">Custom Events</h3>
              <span className="text-sm text-gray-500">({filteredEvents.length})</span>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowDefinitions(!showDefinitions)}
                className={`text-sm px-3 py-1 rounded-md transition-colors ${
                  showDefinitions
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <EyeIcon className="h-4 w-4 inline mr-1" />
                Definitions
              </button>

              <button
                onClick={clearFilters}
                className="text-sm px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="flex items-center space-x-4 mb-3">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search events..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <select
              value={filter.interfaceIds?.[0] || ''}
              onChange={(e) => updateFilter('interfaceIds', e.target.value ? [e.target.value] : undefined)}
              className="text-sm border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Interfaces</option>
              <option value="patient">Patient</option>
              <option value="clinical">Clinical</option>
              <option value="admin">Admin</option>
              <option value="public">Public</option>
              <option value="stakeholder">Stakeholder</option>
              <option value="api-docs">API Docs</option>
              <option value="developer">Developer</option>
            </select>

            <select
              value={filter.severities?.[0] || ''}
              onChange={(e) => updateFilter('severities', e.target.value ? [e.target.value] : undefined)}
              className="text-sm border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Severities</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-4 gap-4 text-sm">
            <div className="text-center">
              <div className="font-semibold text-gray-900">{statistics.totalEvents}</div>
              <div className="text-gray-600">Total Events</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-gray-900">{statistics.recentEvents}</div>
              <div className="text-gray-600">Last Hour</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-gray-900">{Object.keys(statistics.eventsByInterface).length}</div>
              <div className="text-gray-600">Interfaces</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-gray-900">{Object.keys(statistics.eventsByType).length}</div>
              <div className="text-gray-600">Event Types</div>
            </div>
          </div>
        </div>

        {/* Event Definitions Panel */}
        {showDefinitions && (
          <div className="border-b border-gray-200 bg-gray-50 p-4">
            <h4 className="font-medium text-gray-900 mb-3">Event Definitions ({eventDefinitions.length})</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-48 overflow-auto">
              {eventDefinitions.map(definition => (
                <div
                  key={definition.eventType}
                  className="bg-white p-3 rounded-lg border border-gray-200 text-sm"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">{definition.name}</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${getInterfaceColor(definition.interfaceId)}`}>
                      {definition.interfaceId}
                    </span>
                  </div>
                  <div className="text-gray-600 text-xs mb-2">{definition.description}</div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${getCategoryColor(definition.category)}`}>
                      {definition.category}
                    </span>
                    <span className="text-xs text-gray-500">
                      {Object.keys(definition.schema).length} fields
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Events List */}
        <div className="flex-1 overflow-auto">
          <div className="divide-y divide-gray-100">
            {filteredEvents.map((event) => {
              const definition = eventDefinitions.find(def => def.eventType === event.eventType);

              return (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className={`p-4 hover:bg-gray-50 cursor-pointer ${
                    selectedEvent?.id === event.id ? 'bg-blue-50 border-l-2 border-blue-500' : ''
                  }`}
                  onClick={() => setSelectedEvent(event)}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-0.5">
                      {getSeverityIcon(event.severity)}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-medium text-gray-900">
                          {definition?.name || event.eventType}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${getInterfaceColor(event.interfaceId)}`}>
                          {event.interfaceId}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${getSeverityColor(event.severity)}`}>
                          {event.severity}
                        </span>
                      </div>

                      <div className="text-sm text-gray-600 mb-2">
                        {definition?.description || 'Custom application event'}
                      </div>

                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <div className="flex items-center space-x-1">
                          <ClockIcon className="h-3 w-3" />
                          <span>{new Date(event.timestamp).toLocaleString()}</span>
                        </div>

                        {event.tags.length > 0 && (
                          <div className="flex items-center space-x-1">
                            <TagIcon className="h-3 w-3" />
                            <span>{event.tags.join(', ')}</span>
                          </div>
                        )}

                        <span>{Object.keys(event.data).length} data fields</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {filteredEvents.length === 0 && (
            <div className="flex items-center justify-center h-32 text-gray-500">
              {eventInstances.length === 0 ? 'No custom events recorded' : 'No events match the current filters'}
            </div>
          )}
        </div>
      </div>

      {/* Event Details */}
      {selectedEvent && (
        <div className="w-96 border-l border-gray-200 bg-gray-50 overflow-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Event Details</h3>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              {/* Basic Info */}
              <div>
                <h4 className="font-medium text-gray-700 mb-2">General</h4>
                <div className="space-y-1 text-sm">
                  <div><span className="text-gray-600">Event Type:</span> {selectedEvent.eventType}</div>
                  <div><span className="text-gray-600">Interface:</span> {selectedEvent.interfaceId}</div>
                  <div><span className="text-gray-600">Severity:</span> {selectedEvent.severity}</div>
                  <div><span className="text-gray-600">Timestamp:</span> {new Date(selectedEvent.timestamp).toLocaleString()}</div>
                  <div><span className="text-gray-600">ID:</span> <code className="text-xs">{selectedEvent.id}</code></div>
                </div>
              </div>

              {/* Event Data */}
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Event Data</h4>
                <pre className="text-xs bg-white p-3 rounded border overflow-auto max-h-48">
                  {JSON.stringify(selectedEvent.data, null, 2)}
                </pre>
              </div>

              {/* Metadata */}
              {Object.keys(selectedEvent.metadata).length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Metadata</h4>
                  <pre className="text-xs bg-white p-3 rounded border overflow-auto max-h-32">
                    {JSON.stringify(selectedEvent.metadata, null, 2)}
                  </pre>
                </div>
              )}

              {/* Tags */}
              {selectedEvent.tags.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-1">
                    {selectedEvent.tags.map(tag => (
                      <span
                        key={tag}
                        className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Event Definition */}
              {(() => {
                const definition = eventDefinitions.find(def => def.eventType === selectedEvent.eventType);
                return definition ? (
                  <div>
                    <h4 className="font-medium text-gray-700 mb-2">Event Definition</h4>
                    <div className="bg-white p-3 rounded border text-sm">
                      <div className="mb-2">
                        <span className="font-medium">{definition.name}</span>
                        <span className={`ml-2 px-2 py-1 text-xs rounded-full ${getCategoryColor(definition.category)}`}>
                          {definition.category}
                        </span>
                      </div>
                      <div className="text-gray-600 text-xs mb-2">{definition.description}</div>
                      <div className="text-xs text-gray-500">
                        Schema: {Object.keys(definition.schema).length} fields
                      </div>
                    </div>
                  </div>
                ) : null;
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
