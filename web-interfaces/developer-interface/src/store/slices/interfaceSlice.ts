import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface InterfaceStatus {
  id: string;
  name: string;
  port: number;
  status: 'healthy' | 'unhealthy' | 'unknown';
  lastCheck: string;
  responseTime: number;
  errorCount: number;
}

interface InterfaceState {
  interfaces: InterfaceStatus[];
  selectedInterface: string | null;
  isMonitoring: boolean;
  lastUpdate: string;
}

const initialState: InterfaceState = {
  interfaces: [
    {
      id: 'patient',
      name: 'Patient Interface',
      port: 3000,
      status: 'healthy',
      lastCheck: new Date().toISOString(),
      responseTime: 120,
      errorCount: 0
    },
    {
      id: 'clinical',
      name: 'Clinical Dashboard',
      port: 3001,
      status: 'healthy',
      lastCheck: new Date().toISOString(),
      responseTime: 95,
      errorCount: 0
    },
    {
      id: 'admin',
      name: 'Admin Interface',
      port: 3002,
      status: 'healthy',
      lastCheck: new Date().toISOString(),
      responseTime: 110,
      errorCount: 0
    },
    {
      id: 'public',
      name: 'Public Portal',
      port: 3003,
      status: 'healthy',
      lastCheck: new Date().toISOString(),
      responseTime: 85,
      errorCount: 0
    },
    {
      id: 'stakeholder',
      name: 'Stakeholder Dashboard',
      port: 3004,
      status: 'unhealthy',
      lastCheck: new Date().toISOString(),
      responseTime: 0,
      errorCount: 2
    },
    {
      id: 'api-docs',
      name: 'API Documentation',
      port: 3005,
      status: 'healthy',
      lastCheck: new Date().toISOString(),
      responseTime: 75,
      errorCount: 0
    },
    {
      id: 'developer',
      name: 'Developer Interface',
      port: 3006,
      status: 'healthy',
      lastCheck: new Date().toISOString(),
      responseTime: 105,
      errorCount: 0
    }
  ],
  selectedInterface: null,
  isMonitoring: true,
  lastUpdate: new Date().toISOString()
};

const interfaceSlice = createSlice({
  name: 'interfaces',
  initialState,
  reducers: {
    updateInterfaceStatus: (state, action: PayloadAction<Partial<InterfaceStatus> & { id: string }>) => {
      const index = state.interfaces.findIndex(i => i.id === action.payload.id);
      if (index !== -1) {
        state.interfaces[index] = { ...state.interfaces[index], ...action.payload };
      }
      state.lastUpdate = new Date().toISOString();
    },
    updateAllInterfaceStatuses: (state, action: PayloadAction<Partial<InterfaceStatus>[]>) => {
      action.payload.forEach(update => {
        const index = state.interfaces.findIndex(i => i.id === update.id);
        if (index !== -1) {
          state.interfaces[index] = { ...state.interfaces[index], ...update };
        }
      });
      state.lastUpdate = new Date().toISOString();
    },
    setSelectedInterface: (state, action: PayloadAction<string | null>) => {
      state.selectedInterface = action.payload;
    },
    toggleMonitoring: (state) => {
      state.isMonitoring = !state.isMonitoring;
    },
    setMonitoring: (state, action: PayloadAction<boolean>) => {
      state.isMonitoring = action.payload;
    }
  }
});

export const {
  updateInterfaceStatus,
  updateAllInterfaceStatuses,
  setSelectedInterface,
  toggleMonitoring,
  setMonitoring
} = interfaceSlice.actions;

export default interfaceSlice.reducer;
