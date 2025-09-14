import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

export interface TherapeuticSession {
  id: string;
  title: string;
  description: string;
  status: 'scheduled' | 'active' | 'completed' | 'cancelled';
  startTime: string;
  endTime?: string;
  characterId?: string;
  worldId?: string;
  therapeuticGoals: string[];
  progress: {
    milestones: string[];
    notes: string;
    rating?: number;
  };
  createdAt: string;
  updatedAt: string;
}

interface SessionsState {
  sessions: TherapeuticSession[];
  currentSession: TherapeuticSession | null;
  loading: boolean;
  error: string | null;
}

const initialState: SessionsState = {
  sessions: [],
  currentSession: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchSessions = createAsyncThunk(
  'sessions/fetchSessions',
  async () => {
    // In a real app, this would make an API call
    const mockSessions: TherapeuticSession[] = [
      {
        id: '1',
        title: 'Introduction Session',
        description: 'Getting started with therapeutic gaming',
        status: 'completed',
        startTime: new Date(Date.now() - 86400000).toISOString(),
        endTime: new Date(Date.now() - 82800000).toISOString(),
        therapeuticGoals: ['Build rapport', 'Assess baseline'],
        progress: {
          milestones: ['Completed introduction'],
          notes: 'Good initial engagement',
          rating: 4,
        },
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        updatedAt: new Date(Date.now() - 82800000).toISOString(),
      },
    ];
    return mockSessions;
  }
);

export const createSession = createAsyncThunk(
  'sessions/createSession',
  async (sessionData: Partial<TherapeuticSession>) => {
    // In a real app, this would make an API call
    const newSession: TherapeuticSession = {
      id: Date.now().toString(),
      title: sessionData.title || 'New Session',
      description: sessionData.description || '',
      status: 'scheduled',
      startTime: sessionData.startTime || new Date().toISOString(),
      therapeuticGoals: sessionData.therapeuticGoals || [],
      progress: {
        milestones: [],
        notes: '',
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...sessionData,
    };
    return newSession;
  }
);

export const updateSession = createAsyncThunk(
  'sessions/updateSession',
  async ({ id, updates }: { id: string; updates: Partial<TherapeuticSession> }) => {
    // In a real app, this would make an API call
    return { id, updates };
  }
);

export const startSession = createAsyncThunk(
  'sessions/startSession',
  async (sessionId: string) => {
    // In a real app, this would make an API call
    return {
      id: sessionId,
      updates: {
        status: 'active' as const,
        startTime: new Date().toISOString(),
      },
    };
  }
);

export const endSession = createAsyncThunk(
  'sessions/endSession',
  async ({ sessionId, progress }: { sessionId: string; progress: TherapeuticSession['progress'] }) => {
    // In a real app, this would make an API call
    return {
      id: sessionId,
      updates: {
        status: 'completed' as const,
        endTime: new Date().toISOString(),
        progress,
        updatedAt: new Date().toISOString(),
      },
    };
  }
);

const sessionsSlice = createSlice({
  name: 'sessions',
  initialState,
  reducers: {
    setCurrentSession: (state, action: PayloadAction<TherapeuticSession | null>) => {
      state.currentSession = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateSessionProgress: (state, action: PayloadAction<{ sessionId: string; progress: Partial<TherapeuticSession['progress']> }>) => {
      const { sessionId, progress } = action.payload;
      const session = state.sessions.find(s => s.id === sessionId);
      if (session) {
        session.progress = { ...session.progress, ...progress };
        session.updatedAt = new Date().toISOString();
      }
      if (state.currentSession?.id === sessionId) {
        state.currentSession.progress = { ...state.currentSession.progress, ...progress };
        state.currentSession.updatedAt = new Date().toISOString();
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch sessions
      .addCase(fetchSessions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSessions.fulfilled, (state, action) => {
        state.loading = false;
        state.sessions = action.payload;
      })
      .addCase(fetchSessions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch sessions';
      })
      // Create session
      .addCase(createSession.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createSession.fulfilled, (state, action) => {
        state.loading = false;
        state.sessions.push(action.payload);
      })
      .addCase(createSession.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create session';
      })
      // Update session
      .addCase(updateSession.fulfilled, (state, action) => {
        const { id, updates } = action.payload;
        const sessionIndex = state.sessions.findIndex(s => s.id === id);
        if (sessionIndex !== -1) {
          state.sessions[sessionIndex] = { ...state.sessions[sessionIndex], ...updates };
        }
        if (state.currentSession?.id === id) {
          state.currentSession = { ...state.currentSession, ...updates };
        }
      })
      // Start session
      .addCase(startSession.fulfilled, (state, action) => {
        const { id, updates } = action.payload;
        const sessionIndex = state.sessions.findIndex(s => s.id === id);
        if (sessionIndex !== -1) {
          state.sessions[sessionIndex] = { ...state.sessions[sessionIndex], ...updates };
        }
        if (state.currentSession?.id === id) {
          state.currentSession = { ...state.currentSession, ...updates };
        }
      })
      // End session
      .addCase(endSession.fulfilled, (state, action) => {
        const { id, updates } = action.payload;
        const sessionIndex = state.sessions.findIndex(s => s.id === id);
        if (sessionIndex !== -1) {
          state.sessions[sessionIndex] = { ...state.sessions[sessionIndex], ...updates };
        }
        if (state.currentSession?.id === id) {
          state.currentSession = { ...state.currentSession, ...updates };
        }
      });
  },
});

export const { setCurrentSession, clearError, updateSessionProgress } = sessionsSlice.actions;

export default sessionsSlice.reducer;
