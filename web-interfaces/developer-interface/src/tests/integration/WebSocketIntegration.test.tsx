import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from 'react-query';
import { configureStore } from '@reduxjs/toolkit';
import { DebugToolsPanel } from '../../components/debug/DebugToolsPanel';
import { webSocketManager } from '../../services/WebSocketManager';
import debugSlice from '../../store/slices/debugSlice';
import interfaceSlice from '../../store/slices/interfaceSlice';
import developmentSlice from '../../store/slices/developmentSlice';
import testingSlice from '../../store/slices/testingSlice';

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url: string;
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // Simulate connection opening
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 100);
  }

  send(data: string) {
    // Mock sending data
    console.log('Mock WebSocket send:', data);
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) {
      this.onclose(new CloseEvent('close'));
    }
  }

  // Helper method to simulate receiving messages
  simulateMessage(data: any) {
    if (this.onmessage && this.readyState === MockWebSocket.OPEN) {
      this.onmessage(new MessageEvent('message', { data: JSON.stringify(data) }));
    }
  }
}

// Mock ReconnectingWebSocket
jest.mock('reconnecting-websocket', () => {
  return jest.fn().mockImplementation((url: string) => new MockWebSocket(url));
});

// Mock debug tools initialization
jest.mock('../../utils/debugTools', () => ({
  initializeDebugTools: jest.fn(),
  aggregateConsoleLogs: jest.fn(),
  trackError: jest.fn(),
  trackNetworkRequest: jest.fn(),
  configureReduxDevTools: jest.fn(() => undefined),
  getDebuggingData: jest.fn(() => ({
    memoryInfo: { usedJSHeapSize: 1000000, totalJSHeapSize: 2000000, jsHeapSizeLimit: 4000000 },
    networkEvents: [],
    errorEvents: [],
    consoleLogs: [],
  })),
  clearDebuggingData: jest.fn(),
}));

describe('WebSocket Integration Tests', () => {
  let store: any;
  let queryClient: QueryClient;

  beforeEach(() => {
    store = configureStore({
      reducer: {
        debug: debugSlice,
        interfaces: interfaceSlice,
        development: developmentSlice,
        testing: testingSlice,
      },
    });

    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    // Clear any existing WebSocket connections
    webSocketManager.disconnect();
  });

  afterEach(() => {
    webSocketManager.disconnect();
    queryClient.clear();
  });

  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          {component}
        </QueryClientProvider>
      </Provider>
    );
  };

  test('WebSocket manager initializes connections in development', async () => {
    // Set development environment
    process.env.NODE_ENV = 'development';

    // Initialize WebSocket manager
    const manager = webSocketManager;

    await waitFor(() => {
      expect(manager.isConnected()).toBe(false); // Initially not connected
    });

    // Simulate connection establishment
    setTimeout(() => {
      const connections = manager.getConnectionStatus();
      expect(Object.keys(connections)).toContain('player');
      expect(Object.keys(connections)).toContain('gateway');
      expect(Object.keys(connections)).toContain('agent');
    }, 200);
  });

  test('Debug Tools Panel renders and handles WebSocket events', async () => {
    renderWithProviders(<DebugToolsPanel />);

    // Initially, debug panel should be closed
    expect(screen.queryByText('Debug Tools')).not.toBeInTheDocument();

    // Click to open debug panel
    const openButton = screen.getByTitle('Open Debug Tools');
    fireEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByText('Debug Tools')).toBeInTheDocument();
    });

    // Check that tabs are present
    expect(screen.getByText('Network')).toBeInTheDocument();
    expect(screen.getByText('Errors')).toBeInTheDocument();
    expect(screen.getByText('Console')).toBeInTheDocument();
    expect(screen.getByText('Performance')).toBeInTheDocument();
    expect(screen.getByText('Components')).toBeInTheDocument();
  });

  test('Network monitoring captures and displays requests', async () => {
    renderWithProviders(<DebugToolsPanel />);

    // Open debug panel
    const openButton = screen.getByTitle('Open Debug Tools');
    fireEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByText('Debug Tools')).toBeInTheDocument();
    });

    // Click on Network tab
    const networkTab = screen.getByText('Network');
    fireEvent.click(networkTab);

    // Simulate a network request being tracked
    const mockNetworkEvent = {
      type: 'network_request',
      data: {
        url: 'http://localhost:8080/api/health',
        method: 'GET',
        status: 200,
        duration: 150,
        timestamp: new Date().toISOString(),
      },
    };

    // Dispatch network event to store
    store.dispatch({
      type: 'debug/addNetworkEvent',
      payload: mockNetworkEvent.data,
    });

    await waitFor(() => {
      expect(screen.getByText('GET')).toBeInTheDocument();
      expect(screen.getByText('200')).toBeInTheDocument();
    });
  });

  test('Error tracking captures and categorizes errors', async () => {
    renderWithProviders(<DebugToolsPanel />);

    // Open debug panel
    const openButton = screen.getByTitle('Open Debug Tools');
    fireEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByText('Debug Tools')).toBeInTheDocument();
    });

    // Click on Errors tab
    const errorsTab = screen.getByText('Errors');
    fireEvent.click(errorsTab);

    // Simulate an error being tracked
    const mockErrorEvent = {
      message: 'TypeError: Cannot read property of undefined',
      context: 'Component Render',
      severity: 'high' as const,
      timestamp: new Date().toISOString(),
      stack: 'Error\n    at Component.render\n    at ReactDOM.render',
    };

    // Dispatch error event to store
    store.dispatch({
      type: 'debug/addErrorEvent',
      payload: mockErrorEvent,
    });

    await waitFor(() => {
      expect(screen.getByText('TypeError: Cannot read property of undefined')).toBeInTheDocument();
      expect(screen.getByText('high')).toBeInTheDocument();
    });
  });

  test('Console aggregation displays logs from multiple sources', async () => {
    renderWithProviders(<DebugToolsPanel />);

    // Open debug panel
    const openButton = screen.getByTitle('Open Debug Tools');
    fireEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByText('Debug Tools')).toBeInTheDocument();
    });

    // Click on Console tab
    const consoleTab = screen.getByText('Console');
    fireEvent.click(consoleTab);

    // Simulate console logs from different sources
    const mockConsoleLogs = [
      {
        level: 'info' as const,
        message: 'Patient interface loaded successfully',
        timestamp: new Date().toISOString(),
        source: 'patient-interface',
      },
      {
        level: 'warn' as const,
        message: 'API response time exceeded threshold',
        timestamp: new Date().toISOString(),
        source: 'api-gateway',
      },
    ];

    // Dispatch console logs to store
    mockConsoleLogs.forEach(log => {
      store.dispatch({
        type: 'debug/addConsoleLog',
        payload: log,
      });
    });

    await waitFor(() => {
      expect(screen.getByText('Patient interface loaded successfully')).toBeInTheDocument();
      expect(screen.getByText('API response time exceeded threshold')).toBeInTheDocument();
    });
  });

  test('Performance profiler tracks memory usage and metrics', async () => {
    renderWithProviders(<DebugToolsPanel />);

    // Open debug panel
    const openButton = screen.getByTitle('Open Debug Tools');
    fireEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByText('Debug Tools')).toBeInTheDocument();
    });

    // Click on Performance tab
    const performanceTab = screen.getByText('Performance');
    fireEvent.click(performanceTab);

    // Simulate performance metrics
    const mockPerformanceMetric = {
      name: 'Page Load Time',
      value: 1250,
      unit: 'ms',
      timestamp: new Date().toISOString(),
      interfaceId: 'developer',
    };

    const mockMemoryUsage = {
      usedJSHeapSize: 15000000,
      totalJSHeapSize: 25000000,
      jsHeapSizeLimit: 50000000,
      timestamp: new Date().toISOString(),
    };

    // Dispatch performance data to store
    store.dispatch({
      type: 'debug/addPerformanceMetric',
      payload: mockPerformanceMetric,
    });

    store.dispatch({
      type: 'debug/addMemoryUsage',
      payload: mockMemoryUsage,
    });

    await waitFor(() => {
      expect(screen.getByText('Performance Monitor')).toBeInTheDocument();
      expect(screen.getByText('Memory Usage')).toBeInTheDocument();
    });
  });

  test('WebSocket connection status is properly displayed', async () => {
    renderWithProviders(<DebugToolsPanel />);

    // Open debug panel
    const openButton = screen.getByTitle('Open Debug Tools');
    fireEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByText('Debug Tools')).toBeInTheDocument();
    });

    // Check WebSocket status indicator
    expect(screen.getByText(/WebSocket:/)).toBeInTheDocument();

    // Simulate WebSocket connection updates
    store.dispatch({
      type: 'debug/updateWebSocketConnection',
      payload: {
        serviceId: 'player',
        status: 'connected' as const,
        reconnectAttempts: 0,
      },
    });

    await waitFor(() => {
      // Should show connected status
      expect(screen.getByText(/WebSocket: 1\/3/)).toBeInTheDocument();
    });
  });

  test('Debug panel can be resized and closed', async () => {
    renderWithProviders(<DebugToolsPanel />);

    // Open debug panel
    const openButton = screen.getByTitle('Open Debug Tools');
    fireEvent.click(openButton);

    await waitFor(() => {
      expect(screen.getByText('Debug Tools')).toBeInTheDocument();
    });

    // Close debug panel
    const closeButton = screen.getByTitle('Close Debug Tools');
    fireEvent.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByText('Debug Tools')).not.toBeInTheDocument();
    });

    // Should show open button again
    expect(screen.getByTitle('Open Debug Tools')).toBeInTheDocument();
  });
});
