// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Store/Slices/Worldslice]]
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { worldAPI } from '../../services/api';

interface WorldSummary {
  world_id: string;
  name: string;
  description: string;
  therapeutic_themes: string[];
  difficulty_level: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  estimated_duration: string;
  compatibility_score: number;
  preview_image?: string;
}

interface WorldDetails extends WorldSummary {
  detailed_description: string;
  therapeutic_approaches: string[];
  prerequisites: string[];
  customizable_parameters: {
    therapeutic_intensity: boolean;
    narrative_style: boolean;
    pacing: boolean;
    interaction_frequency: boolean;
  };
}

interface CompatibilityReport {
  compatibility_score: number;
  strengths: string[];
  concerns: string[];
  recommendations: string[];
}

interface WorldParameters {
  therapeutic_intensity: 'LOW' | 'MEDIUM' | 'HIGH';
  narrative_style: 'GUIDED' | 'EXPLORATORY' | 'STRUCTURED';
  pacing: 'SLOW' | 'MODERATE' | 'FAST';
  interaction_frequency: 'MINIMAL' | 'REGULAR' | 'FREQUENT';
}

interface WorldState {
  availableWorlds: WorldSummary[];
  selectedWorld: WorldDetails | null;
  worldParameters: WorldParameters | null;
  isLoading: boolean;
  error: string | null;
  filters: {
    difficulty: string[];
    themes: string[];
    duration: string;
  };
}

const initialState: WorldState = {
  availableWorlds: [],
  selectedWorld: null,
  worldParameters: null,
  isLoading: false,
  error: null,
  filters: {
    difficulty: [],
    themes: [],
    duration: '',
  },
};

export const fetchAvailableWorlds = createAsyncThunk(
  'world/fetchAvailableWorlds',
  async (playerId: string) => {
    const response = await worldAPI.getAvailableWorlds(playerId);
    return response;
  }
);

export const fetchWorldDetails = createAsyncThunk(
  'world/fetchWorldDetails',
  async (worldId: string) => {
    const response = await worldAPI.getWorldDetails(worldId);
    return response;
  }
);

export const checkWorldCompatibility = createAsyncThunk(
  'world/checkCompatibility',
  async ({ characterId, worldId }: { characterId: string; worldId: string }) => {
    const response = await worldAPI.checkCompatibility(characterId, worldId);
    return { worldId, ...(response as any) };
  }
);

export const initializeCharacterInWorld = createAsyncThunk(
  'world/initializeCharacterInWorld',
  async ({ characterId, worldId, parameters }: {
    characterId: string;
    worldId: string;
    parameters: WorldParameters
  }) => {
    const response = await worldAPI.initializeCharacterInWorld(characterId, worldId, parameters);
    return response;
  }
);

const worldSlice = createSlice({
  name: 'world',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setSelectedWorld: (state, action: PayloadAction<WorldDetails>) => {
      state.selectedWorld = action.payload;
    },
    clearSelectedWorld: (state) => {
      state.selectedWorld = null;
      state.worldParameters = null;
    },
    setWorldParameters: (state, action: PayloadAction<WorldParameters>) => {
      state.worldParameters = action.payload;
    },
    updateFilters: (state, action: PayloadAction<Partial<typeof initialState.filters>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {
        difficulty: [],
        themes: [],
        duration: '',
      };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAvailableWorlds.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAvailableWorlds.fulfilled, (state, action) => {
        state.isLoading = false;
        state.availableWorlds = action.payload;
      })
      .addCase(fetchAvailableWorlds.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch worlds';
      })
      .addCase(fetchWorldDetails.fulfilled, (state, action) => {
        state.selectedWorld = action.payload;
      })
      .addCase(checkWorldCompatibility.fulfilled, (state, action) => {
        const { worldId, compatibility_score } = action.payload;

        // Update the selected world if it matches
        if (state.selectedWorld && state.selectedWorld.world_id === worldId) {
          state.selectedWorld.compatibility_score = compatibility_score;
        }

        // Update the world in the available worlds list
        const worldIndex = state.availableWorlds.findIndex(w => w.world_id === worldId);
        if (worldIndex !== -1) {
          state.availableWorlds[worldIndex].compatibility_score = compatibility_score;
        }
      });
  },
});

export const {
  clearError,
  setSelectedWorld,
  clearSelectedWorld,
  setWorldParameters,
  updateFilters,
  clearFilters
} = worldSlice.actions;
export default worldSlice.reducer;
