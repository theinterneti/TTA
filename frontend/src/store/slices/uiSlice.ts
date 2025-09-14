import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

export interface UISettings {
  theme: 'light' | 'dark' | 'auto';
  fontSize: 'small' | 'medium' | 'large';
  animations: boolean;
  soundEnabled: boolean;
  notifications: boolean;
}

export interface TherapeuticSettings {
  difficultyLevel: 'easy' | 'medium' | 'hard';
  sessionDuration: number;
  reminderFrequency: 'daily' | 'weekly' | 'monthly';
  privacyMode: boolean;
}

interface UIState {
  uiSettings: UISettings;
  therapeuticSettings: TherapeuticSettings;
  loading: boolean;
  error: string | null;
  sidebarOpen: boolean;
  currentPage: string;
}

const initialState: UIState = {
  uiSettings: {
    theme: 'light',
    fontSize: 'medium',
    animations: true,
    soundEnabled: true,
    notifications: true,
  },
  therapeuticSettings: {
    difficultyLevel: 'medium',
    sessionDuration: 30,
    reminderFrequency: 'daily',
    privacyMode: false,
  },
  loading: false,
  error: null,
  sidebarOpen: false,
  currentPage: 'dashboard',
};

// Async thunks with mock data
export const fetchSettings = createAsyncThunk(
  'ui/fetchSettings',
  async (playerId: string) => {
    // Mock settings data
    return {
      uiSettings: initialState.uiSettings,
      therapeuticSettings: initialState.therapeuticSettings,
    };
  }
);

export const updateUISettings = createAsyncThunk(
  'ui/updateUISettings',
  async (settings: Partial<UISettings>) => {
    // Mock update
    return settings;
  }
);

export const updateTherapeuticSettings = createAsyncThunk(
  'ui/updateTherapeuticSettings',
  async (settings: Partial<TherapeuticSettings>) => {
    // Mock update
    return settings;
  }
);

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    setCurrentPage: (state, action: PayloadAction<string>) => {
      state.currentPage = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch settings
      .addCase(fetchSettings.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSettings.fulfilled, (state, action) => {
        state.loading = false;
        state.uiSettings = action.payload.uiSettings;
        state.therapeuticSettings = action.payload.therapeuticSettings;
      })
      .addCase(fetchSettings.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch settings';
      })
      // Update UI settings
      .addCase(updateUISettings.fulfilled, (state, action) => {
        state.uiSettings = { ...state.uiSettings, ...action.payload };
      })
      // Update therapeutic settings
      .addCase(updateTherapeuticSettings.fulfilled, (state, action) => {
        state.therapeuticSettings = { ...state.therapeuticSettings, ...action.payload };
      });
  },
});

export const { toggleSidebar, setSidebarOpen, setCurrentPage, clearError } = uiSlice.actions;
export default uiSlice.reducer;
