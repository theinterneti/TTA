import { configureStore, createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { 
  TherapeuticSession, 
  PatientProfile, 
  ProgressMetrics, 
  TherapeuticIntervention,
  ClinicalDashboardData,
  ClinicalAlert 
} from '../types/therapeutic';

// Async thunks for API calls
export const fetchPatientProfile = createAsyncThunk(
  'therapeutic/fetchPatientProfile',
  async (patientId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/patients/${patientId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch patient profile');
      }
      return await response.json() as PatientProfile;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

export const startTherapeuticSession = createAsyncThunk(
  'therapeutic/startSession',
  async (sessionData: Partial<TherapeuticSession>, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sessionData),
      });
      if (!response.ok) {
        throw new Error('Failed to start session');
      }
      return await response.json() as TherapeuticSession;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

export const updateProgressMetrics = createAsyncThunk(
  'therapeutic/updateProgress',
  async ({ sessionId, metrics }: { sessionId: string; metrics: Partial<ProgressMetrics> }, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/sessions/${sessionId}/progress`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metrics),
      });
      if (!response.ok) {
        throw new Error('Failed to update progress');
      }
      return await response.json() as ProgressMetrics;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

export const triggerIntervention = createAsyncThunk(
  'therapeutic/triggerIntervention',
  async (intervention: Partial<TherapeuticIntervention>, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/interventions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(intervention),
      });
      if (!response.ok) {
        throw new Error('Failed to trigger intervention');
      }
      return await response.json() as TherapeuticIntervention;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

export const fetchClinicalDashboard = createAsyncThunk(
  'therapeutic/fetchClinicalDashboard',
  async (clinicianId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/clinical/dashboard/${clinicianId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch clinical dashboard');
      }
      return await response.json() as ClinicalDashboardData;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

// Therapeutic slice
interface TherapeuticState {
  currentSession: TherapeuticSession | null;
  patientProfile: PatientProfile | null;
  progressMetrics: ProgressMetrics | null;
  activeInterventions: TherapeuticIntervention[];
  clinicalDashboard: ClinicalDashboardData | null;
  alerts: ClinicalAlert[];
  loading: {
    profile: boolean;
    session: boolean;
    progress: boolean;
    intervention: boolean;
    dashboard: boolean;
  };
  error: {
    profile: string | null;
    session: string | null;
    progress: string | null;
    intervention: string | null;
    dashboard: string | null;
  };
  featureFlags: {
    aiNarrativeEnhancement: boolean;
    livingWorldsSystem: boolean;
    advancedTherapeuticGaming: boolean;
    realTimeClinicalMonitoring: boolean;
  };
}

const initialState: TherapeuticState = {
  currentSession: null,
  patientProfile: null,
  progressMetrics: null,
  activeInterventions: [],
  clinicalDashboard: null,
  alerts: [],
  loading: {
    profile: false,
    session: false,
    progress: false,
    intervention: false,
    dashboard: false,
  },
  error: {
    profile: null,
    session: null,
    progress: null,
    intervention: null,
    dashboard: null,
  },
  featureFlags: {
    aiNarrativeEnhancement: true,
    livingWorldsSystem: true,
    advancedTherapeuticGaming: false,
    realTimeClinicalMonitoring: true,
  },
};

const therapeuticSlice = createSlice({
  name: 'therapeutic',
  initialState,
  reducers: {
    clearSession: (state) => {
      state.currentSession = null;
      state.progressMetrics = null;
      state.activeInterventions = [];
    },
    addAlert: (state, action: PayloadAction<ClinicalAlert>) => {
      state.alerts.unshift(action.payload);
    },
    acknowledgeAlert: (state, action: PayloadAction<string>) => {
      const alert = state.alerts.find(a => a.id === action.payload);
      if (alert) {
        alert.acknowledged = true;
      }
    },
    removeAlert: (state, action: PayloadAction<string>) => {
      state.alerts = state.alerts.filter(a => a.id !== action.payload);
    },
    updateFeatureFlag: (state, action: PayloadAction<{ flag: keyof TherapeuticState['featureFlags']; value: boolean }>) => {
      state.featureFlags[action.payload.flag] = action.payload.value;
    },
    updateSessionStatus: (state, action: PayloadAction<TherapeuticSession['status']>) => {
      if (state.currentSession) {
        state.currentSession.status = action.payload;
      }
    },
  },
  extraReducers: (builder) => {
    // Patient profile
    builder
      .addCase(fetchPatientProfile.pending, (state) => {
        state.loading.profile = true;
        state.error.profile = null;
      })
      .addCase(fetchPatientProfile.fulfilled, (state, action) => {
        state.loading.profile = false;
        state.patientProfile = action.payload;
      })
      .addCase(fetchPatientProfile.rejected, (state, action) => {
        state.loading.profile = false;
        state.error.profile = action.payload as string;
      })
    
    // Session management
      .addCase(startTherapeuticSession.pending, (state) => {
        state.loading.session = true;
        state.error.session = null;
      })
      .addCase(startTherapeuticSession.fulfilled, (state, action) => {
        state.loading.session = false;
        state.currentSession = action.payload;
      })
      .addCase(startTherapeuticSession.rejected, (state, action) => {
        state.loading.session = false;
        state.error.session = action.payload as string;
      })
    
    // Progress metrics
      .addCase(updateProgressMetrics.pending, (state) => {
        state.loading.progress = true;
        state.error.progress = null;
      })
      .addCase(updateProgressMetrics.fulfilled, (state, action) => {
        state.loading.progress = false;
        state.progressMetrics = action.payload;
      })
      .addCase(updateProgressMetrics.rejected, (state, action) => {
        state.loading.progress = false;
        state.error.progress = action.payload as string;
      })
    
    // Interventions
      .addCase(triggerIntervention.pending, (state) => {
        state.loading.intervention = true;
        state.error.intervention = null;
      })
      .addCase(triggerIntervention.fulfilled, (state, action) => {
        state.loading.intervention = false;
        state.activeInterventions.push(action.payload);
      })
      .addCase(triggerIntervention.rejected, (state, action) => {
        state.loading.intervention = false;
        state.error.intervention = action.payload as string;
      })
    
    // Clinical dashboard
      .addCase(fetchClinicalDashboard.pending, (state) => {
        state.loading.dashboard = true;
        state.error.dashboard = null;
      })
      .addCase(fetchClinicalDashboard.fulfilled, (state, action) => {
        state.loading.dashboard = false;
        state.clinicalDashboard = action.payload;
        state.alerts = action.payload.alerts;
      })
      .addCase(fetchClinicalDashboard.rejected, (state, action) => {
        state.loading.dashboard = false;
        state.error.dashboard = action.payload as string;
      });
  },
});

export const { 
  clearSession, 
  addAlert, 
  acknowledgeAlert, 
  removeAlert, 
  updateFeatureFlag, 
  updateSessionStatus 
} = therapeuticSlice.actions;

export const therapeuticReducer = therapeuticSlice.reducer;

// Store configuration
export const store = configureStore({
  reducer: {
    therapeutic: therapeuticReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['therapeutic/fetchPatientProfile/fulfilled'],
        ignoredPaths: ['therapeutic.currentSession.startTime', 'therapeutic.patientProfile.therapeuticHistory.clinicalNotes'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
