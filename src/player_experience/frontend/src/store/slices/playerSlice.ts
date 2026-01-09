// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Store/Slices/Playerslice]]
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { playerAPI } from '../../services/api';

interface PlayerProfile {
  player_id: string;
  username: string;
  email: string;
  created_at: string;
  therapeutic_preferences: {
    intensity_level: 'LOW' | 'MEDIUM' | 'HIGH';
    preferred_approaches: string[];
    trigger_warnings: string[];
    comfort_topics: string[];
    avoid_topics: string[];
  };
  privacy_settings: {
    data_sharing_consent: boolean;
    research_participation: boolean;
    contact_preferences: string[];
  };
  characters: string[];
  active_sessions: Record<string, string>;
}

interface PlayerDashboard {
  player_id: string;
  active_characters: any[];
  recent_sessions: any[];
  progress_highlights: any[];
  recommendations: any[];
  upcoming_milestones: any[];
}

interface PlayerState {
  profile: PlayerProfile | null;
  dashboard: PlayerDashboard | null;
  isLoading: boolean;
  error: string | null;
}

// Initialize from localStorage
const getInitialProfile = (): PlayerProfile | null => {
  const profileStr = localStorage.getItem('player_profile');
  if (profileStr) {
    try {
      return JSON.parse(profileStr);
    } catch {
      return null;
    }
  }
  return null;
};

const initialState: PlayerState = {
  profile: getInitialProfile(),
  dashboard: null,
  isLoading: false,
  error: null,
};

export const fetchPlayerProfile = createAsyncThunk(
  'player/fetchProfile',
  async (playerId: string) => {
    const response = await playerAPI.getProfile(playerId);
    return response;
  }
);

export const fetchPlayerDashboard = createAsyncThunk(
  'player/fetchDashboard',
  async (playerId: string) => {
    const response = await playerAPI.getDashboard(playerId);
    return response;
  }
);

export const updatePlayerProfile = createAsyncThunk(
  'player/updateProfile',
  async ({ playerId, updates }: { playerId: string; updates: Partial<PlayerProfile> }) => {
    const response = await playerAPI.updateProfile(playerId, updates);
    return response;
  }
);

const playerSlice = createSlice({
  name: 'player',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    updateTherapeuticPreferences: (state, action: PayloadAction<any>) => {
      if (state.profile) {
        state.profile.therapeutic_preferences = {
          ...state.profile.therapeutic_preferences,
          ...action.payload,
        };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPlayerProfile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPlayerProfile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.profile = action.payload;
      })
      .addCase(fetchPlayerProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch profile';
      })
      .addCase(fetchPlayerDashboard.fulfilled, (state, action) => {
        state.dashboard = action.payload;
      })
      .addCase(updatePlayerProfile.fulfilled, (state, action) => {
        state.profile = action.payload;
      });
  },
});

export const { clearError, updateTherapeuticPreferences } = playerSlice.actions;
export default playerSlice.reducer;
