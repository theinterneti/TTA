import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface NetworkEvent {
  id: string;
  url: string;
  method: string;
  duration: number;
  status: number;
  timestamp: string;
  requestHeaders?: Record<string, string>;
  responseHeaders?: Record<string, string>;
  requestBody?: any;
  responseBody?: any;
}

export interface ErrorEvent {
  id: string;
  message: string;
  stack?: string;
  context: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface ConsoleLog {
  id: string;
  level: 'log' | 'warn' | 'error' | 'info' | 'debug';
  message: string;
  timestamp: string;
  source?: string;
}

export interface PerformanceMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  timestamp: string;
  interfaceId?: string;
}

export interface MemoryUsage {
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
  timestamp: string;
}

export interface ComponentRenderInfo {
  componentName: string;
  renderCount: number;
  averageRenderTime: number;
  lastRenderTime: string;
  props?: any;
  state?: any;
}

interface DebugState {
  // Network monitoring
  networkEvents: NetworkEvent[];
  networkFilters: {
    method: string[];
    status: string[];
    url: string;
  };

  // Error tracking
  errorEvents: ErrorEvent[];
  errorFilters: {
    severity: string[];
    context: string;
  };

  // Console logs
  consoleLogs: ConsoleLog[];
  consoleFilters: {
    level: string[];
    source: string;
  };

  // Performance monitoring
  performanceMetrics: PerformanceMetric[];
  memoryUsage: MemoryUsage[];
  componentRenderInfo: ComponentRenderInfo[];

  // Debug tools state
  isDebugPanelOpen: boolean;
  activeDebugTab: 'network' | 'errors' | 'console' | 'performance' | 'components';
  isRecording: boolean;

  // WebSocket connection status
  webSocketConnections: {
    [serviceId: string]: {
      status: 'connected' | 'disconnected' | 'connecting' | 'error';
      lastConnected?: string;
      reconnectAttempts: number;
    };
  };
}

const initialState: DebugState = {
  networkEvents: [],
  networkFilters: {
    method: [],
    status: [],
    url: '',
  },

  errorEvents: [],
  errorFilters: {
    severity: [],
    context: '',
  },

  consoleLogs: [],
  consoleFilters: {
    level: [],
    source: '',
  },

  performanceMetrics: [],
  memoryUsage: [],
  componentRenderInfo: [],

  isDebugPanelOpen: false,
  activeDebugTab: 'network',
  isRecording: true,

  webSocketConnections: {},
};

const debugSlice = createSlice({
  name: 'debug',
  initialState,
  reducers: {
    // Network events
    addNetworkEvent: (state, action: PayloadAction<Omit<NetworkEvent, 'id'>>) => {
      const event: NetworkEvent = {
        ...action.payload,
        id: `net_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      state.networkEvents.unshift(event);

      // Keep only last 100 events
      if (state.networkEvents.length > 100) {
        state.networkEvents = state.networkEvents.slice(0, 100);
      }
    },

    setNetworkFilters: (state, action: PayloadAction<Partial<DebugState['networkFilters']>>) => {
      state.networkFilters = { ...state.networkFilters, ...action.payload };
    },

    clearNetworkEvents: (state) => {
      state.networkEvents = [];
    },

    // Error events
    addErrorEvent: (state, action: PayloadAction<Omit<ErrorEvent, 'id'>>) => {
      const event: ErrorEvent = {
        ...action.payload,
        id: `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      state.errorEvents.unshift(event);

      // Keep only last 50 errors
      if (state.errorEvents.length > 50) {
        state.errorEvents = state.errorEvents.slice(0, 50);
      }
    },

    setErrorFilters: (state, action: PayloadAction<Partial<DebugState['errorFilters']>>) => {
      state.errorFilters = { ...state.errorFilters, ...action.payload };
    },

    clearErrorEvents: (state) => {
      state.errorEvents = [];
    },

    // Console logs
    addConsoleLog: (state, action: PayloadAction<Omit<ConsoleLog, 'id'>>) => {
      const log: ConsoleLog = {
        ...action.payload,
        id: `log_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      state.consoleLogs.unshift(log);

      // Keep only last 200 logs
      if (state.consoleLogs.length > 200) {
        state.consoleLogs = state.consoleLogs.slice(0, 200);
      }
    },

    setConsoleFilters: (state, action: PayloadAction<Partial<DebugState['consoleFilters']>>) => {
      state.consoleFilters = { ...state.consoleFilters, ...action.payload };
    },

    clearConsoleLogs: (state) => {
      state.consoleLogs = [];
    },

    // Performance metrics
    addPerformanceMetric: (state, action: PayloadAction<Omit<PerformanceMetric, 'id'>>) => {
      const metric: PerformanceMetric = {
        ...action.payload,
        id: `perf_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      state.performanceMetrics.unshift(metric);

      // Keep only last 100 metrics
      if (state.performanceMetrics.length > 100) {
        state.performanceMetrics = state.performanceMetrics.slice(0, 100);
      }
    },

    addMemoryUsage: (state, action: PayloadAction<MemoryUsage>) => {
      state.memoryUsage.unshift(action.payload);

      // Keep only last 50 memory snapshots
      if (state.memoryUsage.length > 50) {
        state.memoryUsage = state.memoryUsage.slice(0, 50);
      }
    },

    updateComponentRenderInfo: (state, action: PayloadAction<ComponentRenderInfo>) => {
      const index = state.componentRenderInfo.findIndex(
        info => info.componentName === action.payload.componentName
      );

      if (index >= 0) {
        state.componentRenderInfo[index] = action.payload;
      } else {
        state.componentRenderInfo.push(action.payload);
      }
    },

    // Debug panel state
    setDebugPanelOpen: (state, action: PayloadAction<boolean>) => {
      state.isDebugPanelOpen = action.payload;
    },

    setActiveDebugTab: (state, action: PayloadAction<DebugState['activeDebugTab']>) => {
      state.activeDebugTab = action.payload;
    },

    setRecording: (state, action: PayloadAction<boolean>) => {
      state.isRecording = action.payload;
    },

    // WebSocket connections
    updateWebSocketConnection: (state, action: PayloadAction<{
      serviceId: string;
      status: DebugState['webSocketConnections'][string]['status'];
      reconnectAttempts?: number;
    }>) => {
      const { serviceId, status, reconnectAttempts } = action.payload;

      if (!state.webSocketConnections[serviceId]) {
        state.webSocketConnections[serviceId] = {
          status,
          reconnectAttempts: reconnectAttempts || 0,
        };
      } else {
        state.webSocketConnections[serviceId].status = status;
        if (reconnectAttempts !== undefined) {
          state.webSocketConnections[serviceId].reconnectAttempts = reconnectAttempts;
        }
      }

      if (status === 'connected') {
        state.webSocketConnections[serviceId].lastConnected = new Date().toISOString();
        state.webSocketConnections[serviceId].reconnectAttempts = 0;
      }
    },

    // Clear all debug data
    clearAllDebugData: (state) => {
      state.networkEvents = [];
      state.errorEvents = [];
      state.consoleLogs = [];
      state.performanceMetrics = [];
      state.memoryUsage = [];
      state.componentRenderInfo = [];
    },
  },
});

export const {
  addNetworkEvent,
  setNetworkFilters,
  clearNetworkEvents,
  addErrorEvent,
  setErrorFilters,
  clearErrorEvents,
  addConsoleLog,
  setConsoleFilters,
  clearConsoleLogs,
  addPerformanceMetric,
  addMemoryUsage,
  updateComponentRenderInfo,
  setDebugPanelOpen,
  setActiveDebugTab,
  setRecording,
  updateWebSocketConnection,
  clearAllDebugData,
} = debugSlice.actions;

export default debugSlice.reducer;
