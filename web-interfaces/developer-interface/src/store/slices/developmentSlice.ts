import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface BuildStatus {
  interfaceId: string;
  status: 'idle' | 'building' | 'success' | 'error';
  buildTime: number;
  errors: string[];
  warnings: string[];
  lastBuild: string;
}

export interface LiveReloadEvent {
  interfaceId: string;
  timestamp: string;
  changes: string[];
  buildTime: number;
  status: 'reloading' | 'completed' | 'failed';
}

interface DevelopmentState {
  // Build monitoring
  buildStatuses: { [interfaceId: string]: BuildStatus };
  isMonitoringBuilds: boolean;

  // Live reload
  liveReloadEvents: LiveReloadEvent[];
  isLiveReloadEnabled: boolean;

  // Development server status
  devServerStatus: {
    [interfaceId: string]: {
      isRunning: boolean;
      port: number;
      lastStarted: string;
      restartCount: number;
    };
  };

  // Hot module replacement
  hmrStatus: {
    enabled: boolean;
    lastUpdate: string;
    updateCount: number;
    failedUpdates: string[];
  };

  // Environment info
  environmentInfo: {
    nodeVersion: string;
    npmVersion: string;
    reactVersion: string;
    buildTool: string;
    isDevelopment: boolean;
  };
}

const initialState: DevelopmentState = {
  buildStatuses: {},
  isMonitoringBuilds: true,

  liveReloadEvents: [],
  isLiveReloadEnabled: true,

  devServerStatus: {},

  hmrStatus: {
    enabled: true,
    lastUpdate: '',
    updateCount: 0,
    failedUpdates: [],
  },

  environmentInfo: {
    nodeVersion: '',
    npmVersion: '',
    reactVersion: '',
    buildTool: 'vite',
    isDevelopment: process.env.NODE_ENV === 'development',
  },
};

const developmentSlice = createSlice({
  name: 'development',
  initialState,
  reducers: {
    // Build status management
    updateBuildStatus: (state, action: PayloadAction<BuildStatus>) => {
      state.buildStatuses[action.payload.interfaceId] = action.payload;
    },

    setBuildMonitoring: (state, action: PayloadAction<boolean>) => {
      state.isMonitoringBuilds = action.payload;
    },

    clearBuildStatuses: (state) => {
      state.buildStatuses = {};
    },

    // Live reload events
    addLiveReloadEvent: (state, action: PayloadAction<LiveReloadEvent>) => {
      state.liveReloadEvents.unshift(action.payload);

      // Keep only last 50 events
      if (state.liveReloadEvents.length > 50) {
        state.liveReloadEvents = state.liveReloadEvents.slice(0, 50);
      }
    },

    setLiveReloadEnabled: (state, action: PayloadAction<boolean>) => {
      state.isLiveReloadEnabled = action.payload;
    },

    clearLiveReloadEvents: (state) => {
      state.liveReloadEvents = [];
    },

    // Dev server status
    updateDevServerStatus: (state, action: PayloadAction<{
      interfaceId: string;
      isRunning: boolean;
      port?: number;
      lastStarted?: string;
      restartCount?: number;
    }>) => {
      const { interfaceId, ...updates } = action.payload;

      if (!state.devServerStatus[interfaceId]) {
        state.devServerStatus[interfaceId] = {
          isRunning: false,
          port: 3000,
          lastStarted: '',
          restartCount: 0,
        };
      }

      state.devServerStatus[interfaceId] = {
        ...state.devServerStatus[interfaceId],
        ...updates,
      };

      if (updates.isRunning && updates.lastStarted) {
        state.devServerStatus[interfaceId].restartCount += 1;
      }
    },

    // HMR status
    updateHMRStatus: (state, action: PayloadAction<Partial<DevelopmentState['hmrStatus']>>) => {
      state.hmrStatus = { ...state.hmrStatus, ...action.payload };

      if (action.payload.lastUpdate) {
        state.hmrStatus.updateCount += 1;
      }
    },

    addHMRFailure: (state, action: PayloadAction<string>) => {
      state.hmrStatus.failedUpdates.unshift(action.payload);

      // Keep only last 10 failures
      if (state.hmrStatus.failedUpdates.length > 10) {
        state.hmrStatus.failedUpdates = state.hmrStatus.failedUpdates.slice(0, 10);
      }
    },

    clearHMRFailures: (state) => {
      state.hmrStatus.failedUpdates = [];
    },

    // Environment info
    setEnvironmentInfo: (state, action: PayloadAction<Partial<DevelopmentState['environmentInfo']>>) => {
      state.environmentInfo = { ...state.environmentInfo, ...action.payload };
    },

    // Utility actions
    resetDevelopmentState: (state) => {
      state.buildStatuses = {};
      state.liveReloadEvents = [];
      state.devServerStatus = {};
      state.hmrStatus = {
        enabled: true,
        lastUpdate: '',
        updateCount: 0,
        failedUpdates: [],
      };
    },
  },
});

export const {
  updateBuildStatus,
  setBuildMonitoring,
  clearBuildStatuses,
  addLiveReloadEvent,
  setLiveReloadEnabled,
  clearLiveReloadEvents,
  updateDevServerStatus,
  updateHMRStatus,
  addHMRFailure,
  clearHMRFailures,
  setEnvironmentInfo,
  resetDevelopmentState,
} = developmentSlice.actions;

export default developmentSlice.reducer;
