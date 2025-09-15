/**
 * Custom Event Type Support System
 *
 * Extends the WebSocket event system to support application-specific debug events
 * that individual TTA interfaces can define for specialized debugging needs.
 */

import { EventEmitter } from 'events';
import { webSocketManager } from './WebSocketManager';

export interface CustomEventDefinition {
  eventType: string;
  interfaceId: string;
  name: string;
  description: string;
  schema: {
    [key: string]: {
      type: 'string' | 'number' | 'boolean' | 'object' | 'array';
      required: boolean;
      description: string;
      validation?: {
        min?: number;
        max?: number;
        pattern?: string;
        enum?: any[];
      };
    };
  };
  category: 'user_interaction' | 'system_state' | 'performance' | 'error' | 'business_logic' | 'custom';
  severity: 'info' | 'warning' | 'error' | 'critical';
  createdAt: string;
  version: string;
}

export interface CustomEventInstance {
  id: string;
  eventType: string;
  interfaceId: string;
  timestamp: string;
  data: any;
  metadata: {
    userId?: string;
    sessionId?: string;
    userAgent?: string;
    url?: string;
    context?: any;
  };
  severity: 'info' | 'warning' | 'error' | 'critical';
  tags: string[];
}

export interface EventFilter {
  interfaceIds?: string[];
  eventTypes?: string[];
  categories?: string[];
  severities?: string[];
  timeRange?: {
    start: string;
    end: string;
  };
  tags?: string[];
  searchTerm?: string;
}

export class CustomEventManager extends EventEmitter {
  private eventDefinitions: Map<string, CustomEventDefinition> = new Map();
  private eventInstances: CustomEventInstance[] = [];
  private eventFilters: EventFilter = {};
  private maxStoredEvents: number = 1000;

  // Predefined event definitions for each TTA interface
  private predefinedEvents: CustomEventDefinition[] = [
    // Patient Interface Events
    {
      eventType: 'patient_session_start',
      interfaceId: 'patient',
      name: 'Patient Session Started',
      description: 'Triggered when a patient starts a new therapeutic session',
      schema: {
        sessionId: { type: 'string', required: true, description: 'Unique session identifier' },
        patientId: { type: 'string', required: true, description: 'Patient identifier' },
        sessionType: { type: 'string', required: true, description: 'Type of therapeutic session' },
        difficulty: { type: 'string', required: false, description: 'Session difficulty level' }
      },
      category: 'user_interaction',
      severity: 'info',
      createdAt: new Date().toISOString(),
      version: '1.0.0'
    },
    {
      eventType: 'patient_choice_made',
      interfaceId: 'patient',
      name: 'Patient Choice Made',
      description: 'Triggered when a patient makes a choice in the therapeutic narrative',
      schema: {
        choiceId: { type: 'string', required: true, description: 'Choice identifier' },
        choiceText: { type: 'string', required: true, description: 'Text of the choice made' },
        responseTime: { type: 'number', required: true, description: 'Time taken to make choice (ms)' },
        emotionalState: { type: 'string', required: false, description: 'Detected emotional state' }
      },
      category: 'user_interaction',
      severity: 'info',
      createdAt: new Date().toISOString(),
      version: '1.0.0'
    },

    // Clinical Dashboard Events
    {
      eventType: 'clinician_patient_review',
      interfaceId: 'clinical',
      name: 'Clinician Patient Review',
      description: 'Triggered when a clinician reviews patient progress',
      schema: {
        clinicianId: { type: 'string', required: true, description: 'Clinician identifier' },
        patientId: { type: 'string', required: true, description: 'Patient being reviewed' },
        reviewType: { type: 'string', required: true, description: 'Type of review conducted' },
        findings: { type: 'array', required: false, description: 'Clinical findings' },
        recommendations: { type: 'array', required: false, description: 'Treatment recommendations' }
      },
      category: 'business_logic',
      severity: 'info',
      createdAt: new Date().toISOString(),
      version: '1.0.0'
    },
    {
      eventType: 'clinical_alert_triggered',
      interfaceId: 'clinical',
      name: 'Clinical Alert Triggered',
      description: 'Triggered when a clinical alert is generated for patient safety',
      schema: {
        alertType: { type: 'string', required: true, description: 'Type of clinical alert' },
        patientId: { type: 'string', required: true, description: 'Patient associated with alert' },
        severity: { type: 'string', required: true, description: 'Alert severity level' },
        triggerCondition: { type: 'string', required: true, description: 'Condition that triggered alert' },
        autoResolved: { type: 'boolean', required: false, description: 'Whether alert was auto-resolved' }
      },
      category: 'error',
      severity: 'critical',
      createdAt: new Date().toISOString(),
      version: '1.0.0'
    },

    // Admin Interface Events
    {
      eventType: 'admin_user_management',
      interfaceId: 'admin',
      name: 'Admin User Management Action',
      description: 'Triggered when admin performs user management actions',
      schema: {
        adminId: { type: 'string', required: true, description: 'Administrator identifier' },
        action: { type: 'string', required: true, description: 'Action performed' },
        targetUserId: { type: 'string', required: true, description: 'User being managed' },
        changes: { type: 'object', required: false, description: 'Changes made to user' },
        reason: { type: 'string', required: false, description: 'Reason for action' }
      },
      category: 'system_state',
      severity: 'warning',
      createdAt: new Date().toISOString(),
      version: '1.0.0'
    },
    {
      eventType: 'admin_system_config_change',
      interfaceId: 'admin',
      name: 'System Configuration Change',
      description: 'Triggered when admin changes system configuration',
      schema: {
        adminId: { type: 'string', required: true, description: 'Administrator identifier' },
        configSection: { type: 'string', required: true, description: 'Configuration section modified' },
        oldValue: { type: 'string', required: false, description: 'Previous configuration value' },
        newValue: { type: 'string', required: true, description: 'New configuration value' },
        impact: { type: 'string', required: false, description: 'Expected impact of change' }
      },
      category: 'system_state',
      severity: 'warning',
      createdAt: new Date().toISOString(),
      version: '1.0.0'
    },

    // Public Portal Events
    {
      eventType: 'public_resource_access',
      interfaceId: 'public',
      name: 'Public Resource Accessed',
      description: 'Triggered when public resources are accessed',
      schema: {
        resourceType: { type: 'string', required: true, description: 'Type of resource accessed' },
        resourceId: { type: 'string', required: true, description: 'Resource identifier' },
        visitorId: { type: 'string', required: false, description: 'Anonymous visitor identifier' },
        referrer: { type: 'string', required: false, description: 'Referrer URL' },
        duration: { type: 'number', required: false, description: 'Time spent on resource (ms)' }
      },
      category: 'user_interaction',
      severity: 'info',
      createdAt: new Date().toISOString(),
      version: '1.0.0'
    },

    // Stakeholder Dashboard Events
    {
      eventType: 'stakeholder_report_generated',
      interfaceId: 'stakeholder',
      name: 'Stakeholder Report Generated',
      description: 'Triggered when stakeholder reports are generated',
      schema: {
        reportType: { type: 'string', required: true, description: 'Type of report generated' },
        stakeholderId: { type: 'string', required: true, description: 'Stakeholder identifier' },
        dateRange: { type: 'object', required: true, description: 'Report date range' },
        metrics: { type: 'array', required: true, description: 'Metrics included in report' },
        exportFormat: { type: 'string', required: false, description: 'Export format requested' }
      },
      category: 'business_logic',
      severity: 'info',
      createdAt: new Date().toISOString(),
      version: '1.0.0'
    },

    // API Documentation Events
    {
      eventType: 'api_docs_endpoint_tested',
      interfaceId: 'api-docs',
      name: 'API Endpoint Tested',
      description: 'Triggered when API endpoints are tested through documentation',
      schema: {
        endpoint: { type: 'string', required: true, description: 'API endpoint tested' },
        method: { type: 'string', required: true, description: 'HTTP method used' },
        statusCode: { type: 'number', required: true, description: 'Response status code' },
        responseTime: { type: 'number', required: true, description: 'Response time (ms)' },
        userId: { type: 'string', required: false, description: 'User who tested endpoint' }
      },
      category: 'performance',
      severity: 'info',
      createdAt: new Date().toISOString(),
      version: '1.0.0'
    },

    // Developer Interface Events
    {
      eventType: 'dev_debug_session_start',
      interfaceId: 'developer',
      name: 'Debug Session Started',
      description: 'Triggered when developer starts a debug session',
      schema: {
        developerId: { type: 'string', required: true, description: 'Developer identifier' },
        debugType: { type: 'string', required: true, description: 'Type of debugging session' },
        targetInterface: { type: 'string', required: false, description: 'Interface being debugged' },
        tools: { type: 'array', required: false, description: 'Debug tools being used' }
      },
      category: 'system_state',
      severity: 'info',
      createdAt: new Date().toISOString(),
      version: '1.0.0'
    }
  ];

  constructor() {
    super();
    this.initializePredefinedEvents();
    this.setupWebSocketListeners();
  }

  private initializePredefinedEvents(): void {
    this.predefinedEvents.forEach(eventDef => {
      this.eventDefinitions.set(eventDef.eventType, eventDef);
    });
    console.log(`📋 Initialized ${this.predefinedEvents.length} predefined custom events`);
  }

  private setupWebSocketListeners(): void {
    // Listen for custom events from WebSocket connections
    webSocketManager.on('dev_event', (event) => {
      if (event.type.startsWith('custom_')) {
        this.handleCustomEvent(event);
      }
    });

    webSocketManager.on('message', (event) => {
      if (event.type === 'custom_event') {
        this.handleCustomEvent(event);
      }
    });
  }

  private handleCustomEvent(event: any): void {
    try {
      const customEvent = this.createEventInstance(
        event.data.eventType,
        event.interfaceId,
        event.data.data,
        event.data.metadata || {},
        event.data.severity || 'info',
        event.data.tags || []
      );

      if (customEvent) {
        this.emit('custom_event_received', customEvent);
      }
    } catch (error) {
      console.error('Error handling custom event:', error);
    }
  }

  public registerEventDefinition(definition: CustomEventDefinition): void {
    // Validate event definition
    if (!this.validateEventDefinition(definition)) {
      throw new Error('Invalid event definition');
    }

    this.eventDefinitions.set(definition.eventType, definition);
    this.emit('event_definition_registered', definition);
    console.log(`📋 Registered custom event: ${definition.eventType} for ${definition.interfaceId}`);
  }

  private validateEventDefinition(definition: CustomEventDefinition): boolean {
    // Basic validation
    if (!definition.eventType || !definition.interfaceId || !definition.name) {
      return false;
    }

    // Validate schema
    if (!definition.schema || typeof definition.schema !== 'object') {
      return false;
    }

    // Validate schema properties
    for (const [key, prop] of Object.entries(definition.schema)) {
      if (!prop.type || !['string', 'number', 'boolean', 'object', 'array'].includes(prop.type)) {
        return false;
      }
    }

    return true;
  }

  public createEventInstance(
    eventType: string,
    interfaceId: string,
    data: any,
    metadata: any = {},
    severity: 'info' | 'warning' | 'error' | 'critical' = 'info',
    tags: string[] = []
  ): CustomEventInstance | null {
    const definition = this.eventDefinitions.get(eventType);
    if (!definition) {
      console.warn(`Unknown custom event type: ${eventType}`);
      return null;
    }

    // Validate event data against schema
    if (!this.validateEventData(data, definition.schema)) {
      console.error(`Invalid data for event type: ${eventType}`);
      return null;
    }

    const eventInstance: CustomEventInstance = {
      id: `custom_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      eventType,
      interfaceId,
      timestamp: new Date().toISOString(),
      data,
      metadata: {
        ...metadata,
        userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
        url: typeof window !== 'undefined' ? window.location.href : undefined
      },
      severity,
      tags
    };

    // Store event instance
    this.eventInstances.unshift(eventInstance);

    // Limit stored events
    if (this.eventInstances.length > this.maxStoredEvents) {
      this.eventInstances = this.eventInstances.slice(0, this.maxStoredEvents);
    }

    this.emit('event_instance_created', eventInstance);
    return eventInstance;
  }

  private validateEventData(data: any, schema: CustomEventDefinition['schema']): boolean {
    for (const [key, prop] of Object.entries(schema)) {
      if (prop.required && !(key in data)) {
        return false;
      }

      if (key in data) {
        const value = data[key];

        // Type validation
        switch (prop.type) {
          case 'string':
            if (typeof value !== 'string') return false;
            break;
          case 'number':
            if (typeof value !== 'number') return false;
            break;
          case 'boolean':
            if (typeof value !== 'boolean') return false;
            break;
          case 'object':
            if (typeof value !== 'object' || Array.isArray(value)) return false;
            break;
          case 'array':
            if (!Array.isArray(value)) return false;
            break;
        }

        // Additional validation
        if (prop.validation) {
          if (prop.validation.min !== undefined && value < prop.validation.min) return false;
          if (prop.validation.max !== undefined && value > prop.validation.max) return false;
          if (prop.validation.pattern && !new RegExp(prop.validation.pattern).test(value)) return false;
          if (prop.validation.enum && !prop.validation.enum.includes(value)) return false;
        }
      }
    }

    return true;
  }

  public getEventDefinitions(interfaceId?: string): CustomEventDefinition[] {
    const definitions = Array.from(this.eventDefinitions.values());
    return interfaceId ? definitions.filter(def => def.interfaceId === interfaceId) : definitions;
  }

  public getEventInstances(filter?: EventFilter): CustomEventInstance[] {
    let filtered = [...this.eventInstances];

    if (filter) {
      if (filter.interfaceIds?.length) {
        filtered = filtered.filter(event => filter.interfaceIds!.includes(event.interfaceId));
      }

      if (filter.eventTypes?.length) {
        filtered = filtered.filter(event => filter.eventTypes!.includes(event.eventType));
      }

      if (filter.categories?.length) {
        filtered = filtered.filter(event => {
          const definition = this.eventDefinitions.get(event.eventType);
          return definition && filter.categories!.includes(definition.category);
        });
      }

      if (filter.severities?.length) {
        filtered = filtered.filter(event => filter.severities!.includes(event.severity));
      }

      if (filter.timeRange) {
        const start = new Date(filter.timeRange.start);
        const end = new Date(filter.timeRange.end);
        filtered = filtered.filter(event => {
          const eventTime = new Date(event.timestamp);
          return eventTime >= start && eventTime <= end;
        });
      }

      if (filter.tags?.length) {
        filtered = filtered.filter(event =>
          filter.tags!.some(tag => event.tags.includes(tag))
        );
      }

      if (filter.searchTerm) {
        const searchLower = filter.searchTerm.toLowerCase();
        filtered = filtered.filter(event =>
          event.eventType.toLowerCase().includes(searchLower) ||
          JSON.stringify(event.data).toLowerCase().includes(searchLower)
        );
      }
    }

    return filtered;
  }

  public setEventFilter(filter: EventFilter): void {
    this.eventFilters = filter;
    this.emit('filter_changed', filter);
  }

  public getEventFilter(): EventFilter {
    return this.eventFilters;
  }

  public broadcastCustomEvent(eventType: string, interfaceId: string, data: any, metadata?: any): void {
    // Create event instance
    const eventInstance = this.createEventInstance(eventType, interfaceId, data, metadata);

    if (eventInstance) {
      // Broadcast via WebSocket if available
      webSocketManager.emit('custom_event_broadcast', {
        type: 'custom_event',
        eventType,
        interfaceId,
        data: eventInstance,
        timestamp: new Date().toISOString()
      });
    }
  }

  public getEventStatistics(): {
    totalEvents: number;
    eventsByInterface: { [interfaceId: string]: number };
    eventsByType: { [eventType: string]: number };
    eventsBySeverity: { [severity: string]: number };
    recentEvents: number;
  } {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);

    const eventsByInterface: { [interfaceId: string]: number } = {};
    const eventsByType: { [eventType: string]: number } = {};
    const eventsBySeverity: { [severity: string]: number } = {};
    let recentEvents = 0;

    this.eventInstances.forEach(event => {
      eventsByInterface[event.interfaceId] = (eventsByInterface[event.interfaceId] || 0) + 1;
      eventsByType[event.eventType] = (eventsByType[event.eventType] || 0) + 1;
      eventsBySeverity[event.severity] = (eventsBySeverity[event.severity] || 0) + 1;

      if (new Date(event.timestamp) >= oneHourAgo) {
        recentEvents++;
      }
    });

    return {
      totalEvents: this.eventInstances.length,
      eventsByInterface,
      eventsByType,
      eventsBySeverity,
      recentEvents
    };
  }

  public clearEvents(interfaceId?: string): void {
    if (interfaceId) {
      this.eventInstances = this.eventInstances.filter(event => event.interfaceId !== interfaceId);
    } else {
      this.eventInstances = [];
    }
    this.emit('events_cleared', { interfaceId });
  }

  public dispose(): void {
    this.removeAllListeners();
    this.eventInstances = [];
    this.eventDefinitions.clear();
  }
}

// Singleton instance
export const customEventManager = new CustomEventManager();
