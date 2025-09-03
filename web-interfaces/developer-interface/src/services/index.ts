/**
 * Enhanced Debug Tools Services Export
 *
 * Centralized export for all enhanced debugging services to ensure
 * proper initialization order and dependency management.
 */

// Core debug tools services
export { webSocketManager } from './WebSocketManager';
export { performanceBaselineManager } from './PerformanceBaselineManager';
export { customEventManager } from './CustomEventManager';
export { collaborativeDebugManager } from './CollaborativeDebugManager';
export { reactDevToolsBridge } from './ReactDevToolsBridge';
export { ciPipelineIntegration } from './CIPipelineIntegration';

// Type exports
export type {
  WebSocketConnection,
  MonitoringEvent,
  DevEvent
} from './WebSocketManager';

export type {
  PerformanceMetric,
  PerformanceBaseline,
  PerformanceRegression,
  PerformanceTrend,
  PerformanceAlert
} from './PerformanceBaselineManager';

export type {
  CustomEventDefinition,
  CustomEventInstance,
  EventFilter
} from './CustomEventManager';

export type {
  DebugSession,
  DebugParticipant,
  DebugAnnotation,
  DebugNote,
  DebugBookmark,
  SessionInvitation
} from './CollaborativeDebugManager';

export type {
  CITestRun,
  CITestResult,
  CIPerformanceMetric,
  CIDebugData,
  CIRegression,
  CIArtifact,
  CIReport
} from './CIPipelineIntegration';

/**
 * Initialize all enhanced debug tools services
 * Call this function during application startup
 */
export const initializeAllDebugServices = async (): Promise<void> => {
  try {
    console.log('🚀 Initializing enhanced debug tools services...');

    // Initialize WebSocket manager first (other services depend on it)
    const wsEndpoints = process.env.TTA_WEBSOCKET_ENDPOINTS?.split(',') || [
      'ws://localhost:8080/ws/monitoring',
      'ws://localhost:8000/ws/monitoring',
      'ws://localhost:8503/ws/monitoring'
    ];

    for (const endpoint of wsEndpoints) {
      try {
        await webSocketManager.connect(endpoint.trim());
        console.log(`✅ Connected to ${endpoint}`);
      } catch (error) {
        console.warn(`⚠️ Failed to connect to ${endpoint}:`, error);
      }
    }

    // Initialize performance baseline manager
    if (process.env.TTA_PERFORMANCE_BASELINE !== 'false') {
      performanceBaselineManager.startRecording();
      console.log('✅ Performance baseline recording started');
    }

    // Initialize custom event manager (already initialized via constructor)
    console.log('✅ Custom event manager initialized');

    // Initialize collaborative debug manager (already initialized via constructor)
    console.log('✅ Collaborative debug manager initialized');

    // Initialize React DevTools bridge (already initialized via constructor)
    if (reactDevToolsBridge.isDevToolsConnected()) {
      console.log('✅ React DevTools integration active');
    } else {
      console.log('ℹ️ React DevTools not detected (will retry automatically)');
    }

    // Initialize CI/CD integration if in CI environment
    if (process.env.TTA_CI_INTEGRATION === 'true') {
      const buildId = process.env.GITHUB_RUN_ID || process.env.BUILD_ID || 'local';
      const branch = process.env.GITHUB_REF_NAME || process.env.BRANCH_NAME || 'unknown';
      const commit = process.env.GITHUB_SHA || process.env.COMMIT_SHA || 'unknown';
      const author = process.env.GITHUB_ACTOR || process.env.BUILD_USER || 'unknown';

      ciPipelineIntegration.startTestRun(buildId, branch, commit, author);
      console.log('✅ CI/CD integration initialized');
    }

    console.log('🎉 All enhanced debug tools services initialized successfully');
  } catch (error) {
    console.error('❌ Failed to initialize debug tools services:', error);
    throw error;
  }
};

/**
 * Cleanup all debug services
 * Call this function during application shutdown
 */
export const cleanupAllDebugServices = (): void => {
  try {
    console.log('🧹 Cleaning up debug tools services...');

    // Stop performance baseline recording
    performanceBaselineManager.stopRecording();

    // Disconnect WebSocket connections
    webSocketManager.disconnectAll();

    // Leave any active collaborative sessions
    if (collaborativeDebugManager.getCurrentSession()) {
      collaborativeDebugManager.leaveSession();
    }

    // Dispose of React DevTools bridge
    reactDevToolsBridge.dispose();

    // Finish any active CI test runs
    if (ciPipelineIntegration.getCurrentTestRun()) {
      ciPipelineIntegration.finishTestRun('cancelled');
    }

    // Dispose of custom event manager
    customEventManager.dispose();

    console.log('✅ Debug tools services cleanup completed');
  } catch (error) {
    console.error('❌ Error during debug tools cleanup:', error);
  }
};

/**
 * Get status of all debug services
 */
export const getDebugServicesStatus = () => {
  return {
    webSocket: {
      connected: webSocketManager.getConnectedEndpoints().length,
      total: webSocketManager.getAllConnections().length,
      status: webSocketManager.getConnectionStatus()
    },
    performanceBaseline: {
      recording: performanceBaselineManager.isRecording(),
      baselines: performanceBaselineManager.getAllBaselines().length,
      regressions: performanceBaselineManager.getRegressions().length
    },
    customEvents: {
      definitions: customEventManager.getEventDefinitions().length,
      instances: customEventManager.getEventInstances().length,
      statistics: customEventManager.getEventStatistics()
    },
    collaborative: {
      currentSession: collaborativeDebugManager.getCurrentSession()?.id || null,
      activeSessions: collaborativeDebugManager.getActiveSessions().length,
      invitations: collaborativeDebugManager.getInvitations().length
    },
    reactDevTools: {
      connected: reactDevToolsBridge.isDevToolsConnected(),
      capabilities: reactDevToolsBridge.getDevToolsCapabilities()
    },
    ciIntegration: {
      active: ciPipelineIntegration.isRecordingActive(),
      currentRun: ciPipelineIntegration.getCurrentTestRun()?.id || null,
      totalRuns: ciPipelineIntegration.getAllTestRuns().length
    }
  };
};

// Auto-initialize services when module is imported in development
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  // Delay initialization to allow other modules to load
  setTimeout(() => {
    if (process.env.TTA_DEBUG_MODE !== 'false') {
      initializeAllDebugServices().catch(console.error);
    }
  }, 1000);
}

// Cleanup on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', cleanupAllDebugServices);
}
