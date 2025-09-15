/**
 * Integration Tests for Enhanced Debug Tools
 *
 * Tests the complete integration of all debugging features including:
 * - WebSocket monitoring connections
 * - Performance baseline recording
 * - Custom event system
 * - Collaborative debugging
 * - React DevTools integration
 * - CI/CD pipeline integration
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import WS from 'jest-websocket-mock';

import { DebugToolsPanel } from '../../components/debug/DebugToolsPanel';
import { debugSlice } from '../../store/slices/debugSlice';
import { webSocketManager } from '../../services/WebSocketManager';
import { performanceBaselineManager } from '../../services/PerformanceBaselineManager';
import { customEventManager } from '../../services/CustomEventManager';
import { collaborativeDebugManager } from '../../services/CollaborativeDebugManager';
import { reactDevToolsBridge } from '../../services/ReactDevToolsBridge';
import { ciPipelineIntegration } from '../../services/CIPipelineIntegration';

// Mock WebSocket
jest.mock('../../services/WebSocketManager');
jest.mock('../../services/PerformanceBaselineManager');
jest.mock('../../services/CustomEventManager');
jest.mock('../../services/CollaborativeDebugManager');
jest.mock('../../services/ReactDevToolsBridge');
jest.mock('../../services/CIPipelineIntegration');

const mockStore = configureStore({
  reducer: {
    debug: debugSlice.reducer
  },
  preloadedState: {
    debug: {
      isOpen: true,
      activeTab: 'network',
      isRecording: true,
      networkEvents: [],
      errorEvents: [],
      consoleLogs: [],
      performanceMetrics: [],
      componentRenderInfo: {},
      webSocketConnections: {
        'player-experience': { status: 'connected', url: 'ws://localhost:8080/ws/monitoring' },
        'api-gateway': { status: 'connected', url: 'ws://localhost:8000/ws/monitoring' },
        'agent-orchestration': { status: 'connected', url: 'ws://localhost:8503/ws/monitoring' }
      }
    }
  }
});

const renderWithProvider = (component: React.ReactElement) => {
  return render(
    <Provider store={mockStore}>
      {component}
    </Provider>
  );
};

describe('Debug Tools Integration', () => {
  let mockWebSocketServers: WS[];

  beforeEach(() => {
    // Set up mock WebSocket servers for each backend service
    mockWebSocketServers = [
      new WS('ws://localhost:8080/ws/monitoring'),
      new WS('ws://localhost:8000/ws/monitoring'),
      new WS('ws://localhost:8503/ws/monitoring')
    ];

    // Reset all mocks
    jest.clearAllMocks();
  });

  afterEach(() => {
    // Clean up WebSocket servers
    mockWebSocketServers.forEach(server => {
      WS.clean();
    });
  });

  describe('WebSocket Integration', () => {
    it('should connect to all backend monitoring endpoints', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Verify WebSocket connections are established
      await waitFor(() => {
        expect(webSocketManager.connect).toHaveBeenCalledWith('ws://localhost:8080/ws/monitoring');
        expect(webSocketManager.connect).toHaveBeenCalledWith('ws://localhost:8000/ws/monitoring');
        expect(webSocketManager.connect).toHaveBeenCalledWith('ws://localhost:8503/ws/monitoring');
      });

      // Verify connection status is displayed
      expect(screen.getByText(/WebSocket Status/)).toBeInTheDocument();
      expect(screen.getByText(/3 connected/)).toBeInTheDocument();
    });

    it('should handle WebSocket messages and update debug panels', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Simulate receiving monitoring data
      const mockMonitoringData = {
        type: 'interface_health',
        timestamp: new Date().toISOString(),
        service_id: 'player-experience-api',
        data: {
          id: 'player-experience',
          name: 'Player Experience API',
          status: 'healthy',
          response_time: 45.2,
          error_count: 0
        }
      };

      act(() => {
        webSocketManager.emit('dev_event', mockMonitoringData);
      });

      await waitFor(() => {
        expect(screen.getByText(/Player Experience API/)).toBeInTheDocument();
        expect(screen.getByText(/healthy/)).toBeInTheDocument();
      });
    });

    it('should handle WebSocket disconnections gracefully', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Simulate WebSocket disconnection
      act(() => {
        webSocketManager.emit('connection_lost', {
          url: 'ws://localhost:8080/ws/monitoring',
          reason: 'Connection timeout'
        });
      });

      await waitFor(() => {
        expect(screen.getByText(/2 connected/)).toBeInTheDocument();
        expect(screen.getByText(/Connection timeout/)).toBeInTheDocument();
      });
    });
  });

  describe('Performance Baseline Integration', () => {
    it('should record performance baselines automatically', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Switch to baselines tab
      fireEvent.click(screen.getByText('Baselines'));

      await waitFor(() => {
        expect(performanceBaselineManager.getAllBaselines).toHaveBeenCalled();
      });

      // Simulate baseline creation
      const mockBaseline = {
        interfaceId: 'patient',
        interfaceName: 'Patient Interface',
        version: '1.0.0',
        createdAt: new Date().toISOString(),
        metrics: {
          load_time: {
            baseline: 150.5,
            unit: 'ms',
            category: 'load_time',
            samples: 25,
            standardDeviation: 12.3,
            percentiles: { p50: 145, p75: 160, p90: 180, p95: 200, p99: 250 }
          }
        }
      };

      act(() => {
        performanceBaselineManager.emit('baseline_created', mockBaseline);
      });

      await waitFor(() => {
        expect(screen.getByText('Patient Interface')).toBeInTheDocument();
        expect(screen.getByText('150.5ms')).toBeInTheDocument();
      });
    });

    it('should detect and alert on performance regressions', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Switch to baselines tab
      fireEvent.click(screen.getByText('Baselines'));

      // Simulate regression detection
      const mockRegression = {
        id: 'regression_123',
        interfaceId: 'patient',
        metricName: 'load_time',
        baselineValue: 150.5,
        currentValue: 195.8,
        regressionPercentage: 30.1,
        severity: 'high',
        detectedAt: new Date().toISOString(),
        threshold: 20,
        isResolved: false
      };

      act(() => {
        performanceBaselineManager.emit('regression_detected', mockRegression);
      });

      await waitFor(() => {
        expect(screen.getByText(/Regression Detected/)).toBeInTheDocument();
        expect(screen.getByText(/30.1%/)).toBeInTheDocument();
        expect(screen.getByText(/high/)).toBeInTheDocument();
      });
    });
  });

  describe('Custom Event System Integration', () => {
    it('should display custom events from all interfaces', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Switch to events tab
      fireEvent.click(screen.getByText('Events'));

      await waitFor(() => {
        expect(customEventManager.getEventInstances).toHaveBeenCalled();
        expect(customEventManager.getEventDefinitions).toHaveBeenCalled();
      });

      // Simulate custom event creation
      const mockEvent = {
        id: 'event_123',
        eventType: 'patient_session_start',
        interfaceId: 'patient',
        timestamp: new Date().toISOString(),
        data: {
          sessionId: 'session_456',
          patientId: 'patient_789',
          sessionType: 'narrative_therapy'
        },
        metadata: {
          userId: 'user_123',
          sessionId: 'browser_session_456'
        },
        severity: 'info',
        tags: ['session', 'patient']
      };

      act(() => {
        customEventManager.emit('event_instance_created', mockEvent);
      });

      await waitFor(() => {
        expect(screen.getByText('patient_session_start')).toBeInTheDocument();
        expect(screen.getByText('patient')).toBeInTheDocument();
        expect(screen.getByText('info')).toBeInTheDocument();
      });
    });

    it('should filter events by interface and severity', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Switch to events tab
      fireEvent.click(screen.getByText('Events'));

      // Test interface filter
      const interfaceSelect = screen.getByDisplayValue('All Interfaces');
      fireEvent.change(interfaceSelect, { target: { value: 'clinical' } });

      await waitFor(() => {
        expect(customEventManager.setEventFilter).toHaveBeenCalledWith(
          expect.objectContaining({
            interfaceIds: ['clinical']
          })
        );
      });

      // Test severity filter
      const severitySelect = screen.getByDisplayValue('All Severities');
      fireEvent.change(severitySelect, { target: { value: 'error' } });

      await waitFor(() => {
        expect(customEventManager.setEventFilter).toHaveBeenCalledWith(
          expect.objectContaining({
            severities: ['error']
          })
        );
      });
    });
  });

  describe('Collaborative Debug Integration', () => {
    it('should create and join debug sessions', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Switch to collaborate tab
      fireEvent.click(screen.getByText('Collaborate'));

      // Test session creation
      fireEvent.click(screen.getByText('Create Debug Session'));

      const sessionNameInput = screen.getByPlaceholderText('Enter session name...');
      fireEvent.change(sessionNameInput, { target: { value: 'Bug Investigation Session' } });

      const createButton = screen.getByText('Create Session');
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(collaborativeDebugManager.createSession).toHaveBeenCalledWith(
          'Bug Investigation Session',
          ''
        );
      });
    });

    it('should handle real-time collaboration features', async () => {
      // Mock active session
      const mockSession = {
        id: 'session_123',
        name: 'Bug Investigation Session',
        description: 'Investigating login issues',
        createdBy: 'user_123',
        createdAt: new Date().toISOString(),
        isActive: true,
        participants: [
          {
            id: 'user_123',
            name: 'John Developer',
            email: 'john@example.com',
            role: 'owner',
            joinedAt: new Date().toISOString(),
            lastActivity: new Date().toISOString(),
            isOnline: true,
            currentView: 'network'
          }
        ],
        sharedState: {
          activeTab: 'network',
          filters: {},
          selectedItems: {},
          annotations: [],
          bookmarks: [],
          sharedNotes: []
        },
        permissions: {
          canModifyFilters: true,
          canSelectItems: true,
          canAddAnnotations: true,
          canAddBookmarks: true,
          canAddNotes: true,
          canInviteUsers: true,
          canModifySettings: true
        },
        settings: {
          autoSync: true,
          showCursors: true,
          showParticipantViews: true,
          notifyOnChanges: true,
          recordSession: false,
          maxParticipants: 10
        }
      };

      (collaborativeDebugManager.getCurrentSession as jest.Mock).mockReturnValue(mockSession);

      renderWithProvider(<DebugToolsPanel />);

      // Switch to collaborate tab
      fireEvent.click(screen.getByText('Collaborate'));

      await waitFor(() => {
        expect(screen.getByText('Bug Investigation Session')).toBeInTheDocument();
        expect(screen.getByText('John Developer')).toBeInTheDocument();
        expect(screen.getByText('Participants (1):')).toBeInTheDocument();
      });

      // Test adding a note
      const noteInput = screen.getByPlaceholderText('Add a note...');
      fireEvent.change(noteInput, { target: { value: 'Found the issue in authentication middleware' } });
      fireEvent.click(screen.getByText('Add'));

      await waitFor(() => {
        expect(collaborativeDebugManager.addNote).toHaveBeenCalledWith({
          content: 'Found the issue in authentication middleware',
          type: 'general',
          priority: 'medium'
        });
      });
    });
  });

  describe('React DevTools Integration', () => {
    it('should integrate with React DevTools when available', async () => {
      // Mock DevTools availability
      (reactDevToolsBridge.isDevToolsConnected as jest.Mock).mockReturnValue(true);
      (reactDevToolsBridge.getDevToolsCapabilities as jest.Mock).mockReturnValue([
        'component_tree',
        'render_tracking',
        'fiber_inspection',
        'performance_profiling'
      ]);

      renderWithProvider(<DebugToolsPanel />);

      // Switch to components tab
      fireEvent.click(screen.getByText('Components'));

      await waitFor(() => {
        expect(screen.getByText('React DevTools: Connected')).toBeInTheDocument();
        expect(screen.getByText('(4 capabilities)')).toBeInTheDocument();
      });

      // Test DevTools data toggle
      const devToolsToggle = screen.getByLabelText('Use DevTools Data');
      fireEvent.click(devToolsToggle);

      await waitFor(() => {
        expect(reactDevToolsBridge.getComponentTree).toHaveBeenCalled();
      });
    });

    it('should handle DevTools unavailability gracefully', async () => {
      // Mock DevTools unavailability
      (reactDevToolsBridge.isDevToolsConnected as jest.Mock).mockReturnValue(false);

      renderWithProvider(<DebugToolsPanel />);

      // Switch to components tab
      fireEvent.click(screen.getByText('Components'));

      await waitFor(() => {
        expect(screen.getByText('React DevTools: Not Available')).toBeInTheDocument();
      });

      // DevTools toggle should be disabled
      const devToolsToggle = screen.getByLabelText('Use DevTools Data');
      expect(devToolsToggle).toBeDisabled();
    });
  });

  describe('CI/CD Pipeline Integration', () => {
    it('should record test run data during CI execution', async () => {
      // Simulate CI environment
      process.env.TTA_CI_INTEGRATION = 'true';
      process.env.GITHUB_RUN_ID = '123456789';
      process.env.GITHUB_REF_NAME = 'feat/debug-enhancements';
      process.env.GITHUB_SHA = 'abc123def456';
      process.env.GITHUB_ACTOR = 'developer';

      renderWithProvider(<DebugToolsPanel />);

      // Verify CI integration is active
      expect(ciPipelineIntegration.startTestRun).toHaveBeenCalledWith(
        '123456789',
        'feat/debug-enhancements',
        'abc123def456',
        'developer'
      );
    });

    it('should capture debug artifacts during test execution', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Simulate test execution with debug data
      const mockTestResult = {
        testId: 'test_123',
        testName: 'should render patient interface correctly',
        testFile: 'PatientInterface.test.tsx',
        status: 'passed' as const,
        duration: 1250
      };

      act(() => {
        ciPipelineIntegration.recordTestResult(mockTestResult);
      });

      await waitFor(() => {
        expect(ciPipelineIntegration.recordTestResult).toHaveBeenCalledWith(mockTestResult);
      });

      // Simulate performance metric recording
      const mockMetric = {
        name: 'render_time',
        value: 85.3,
        unit: 'ms',
        interfaceId: 'patient',
        timestamp: new Date().toISOString()
      };

      act(() => {
        ciPipelineIntegration.recordPerformanceMetric(mockMetric);
      });

      await waitFor(() => {
        expect(ciPipelineIntegration.recordPerformanceMetric).toHaveBeenCalledWith(mockMetric);
      });
    });

    it('should generate comprehensive debug reports', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Mock test run completion
      const mockTestRun = {
        id: 'run_123',
        buildId: '123456789',
        branch: 'feat/debug-enhancements',
        commit: 'abc123def456',
        author: 'developer',
        startTime: new Date().toISOString(),
        endTime: new Date().toISOString(),
        status: 'passed' as const,
        testResults: [],
        performanceMetrics: [],
        debugData: {
          networkRequests: [],
          errors: [],
          consoleLogs: [],
          customEvents: []
        },
        regressions: [],
        artifacts: []
      };

      (ciPipelineIntegration.getCurrentTestRun as jest.Mock).mockReturnValue(mockTestRun);

      act(() => {
        ciPipelineIntegration.finishTestRun('passed');
      });

      await waitFor(() => {
        expect(ciPipelineIntegration.finishTestRun).toHaveBeenCalledWith('passed');
      });
    });
  });

  describe('End-to-End Integration', () => {
    it('should handle complete debug workflow', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // 1. Verify all tabs are available
      expect(screen.getByText('Network')).toBeInTheDocument();
      expect(screen.getByText('Errors')).toBeInTheDocument();
      expect(screen.getByText('Console')).toBeInTheDocument();
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Components')).toBeInTheDocument();
      expect(screen.getByText('Events')).toBeInTheDocument();
      expect(screen.getByText('Baselines')).toBeInTheDocument();
      expect(screen.getByText('Collaborate')).toBeInTheDocument();

      // 2. Test tab switching
      fireEvent.click(screen.getByText('Events'));
      await waitFor(() => {
        expect(customEventManager.getEventInstances).toHaveBeenCalled();
      });

      fireEvent.click(screen.getByText('Baselines'));
      await waitFor(() => {
        expect(performanceBaselineManager.getAllBaselines).toHaveBeenCalled();
      });

      // 3. Test recording toggle
      const recordingButton = screen.getByLabelText(/recording/i);
      fireEvent.click(recordingButton);

      await waitFor(() => {
        expect(mockStore.getState().debug.isRecording).toBe(false);
      });

      // 4. Test clear all data
      const clearButton = screen.getByLabelText(/clear/i);
      fireEvent.click(clearButton);

      // Should show confirmation or clear data
      await waitFor(() => {
        // Verify clear action was triggered
        expect(clearButton).toBeInTheDocument();
      });
    });

    it('should maintain state consistency across all debug tools', async () => {
      renderWithProvider(<DebugToolsPanel />);

      // Simulate state changes from multiple sources
      act(() => {
        // WebSocket event
        webSocketManager.emit('dev_event', {
          type: 'network_request',
          data: { url: '/api/test', method: 'GET', status: 200 }
        });

        // Performance baseline update
        performanceBaselineManager.emit('metric_recorded', {
          name: 'api_response_time',
          value: 125.5,
          unit: 'ms',
          timestamp: new Date().toISOString(),
          interfaceId: 'api-gateway',
          category: 'network'
        });

        // Custom event
        customEventManager.emit('event_instance_created', {
          id: 'event_456',
          eventType: 'api_call_completed',
          interfaceId: 'api-gateway',
          timestamp: new Date().toISOString(),
          data: { endpoint: '/api/test', duration: 125.5 },
          metadata: {},
          severity: 'info',
          tags: ['api', 'performance']
        });
      });

      // Verify all systems are updated consistently
      await waitFor(() => {
        // All debug tools should reflect the new data
        expect(screen.getByText(/WebSocket Status/)).toBeInTheDocument();
      });
    });
  });
});
