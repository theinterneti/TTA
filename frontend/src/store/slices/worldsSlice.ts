import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

export interface World {
  id: string;
  name: string;
  description: string;
  theme: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  therapeuticFocus: string[];
  isAvailable: boolean;
  createdAt: string;
}

interface WorldsState {
  availableWorlds: World[];
  selectedWorld: World | null;
  loading: boolean;
  error: string | null;
}

const initialState: WorldsState = {
  availableWorlds: [],
  selectedWorld: null,
  loading: false,
  error: null,
};

// Async thunks with mock data
export const fetchAvailableWorlds = createAsyncThunk(
  'worlds/fetchAvailableWorlds',
  async (playerId: string) => {
    // Mock data
    const mockWorlds: World[] = [
      {
        id: '1',
        name: 'Peaceful Garden',
        description: 'A serene environment for relaxation and mindfulness',
        theme: 'Nature',
        difficulty: 'beginner',
        therapeuticFocus: ['Anxiety reduction', 'Mindfulness'],
        isAvailable: true,
        createdAt: new Date().toISOString(),
      },
      {
        id: '2',
        name: 'Adventure Valley',
        description: 'An exciting world for building confidence and courage',
        theme: 'Adventure',
        difficulty: 'intermediate',
        therapeuticFocus: ['Confidence building', 'Problem solving'],
        isAvailable: true,
        createdAt: new Date().toISOString(),
      },
    ];
    return mockWorlds;
  }
);

export const fetchWorldDetails = createAsyncThunk(
  'worlds/fetchWorldDetails',
  async (worldId: string) => {
    // Mock world details
    const mockWorld: World = {
      id: worldId,
      name: 'Sample World',
      description: 'A therapeutic world for growth and healing',
      theme: 'Fantasy',
      difficulty: 'beginner',
      therapeuticFocus: ['Self-discovery', 'Emotional regulation'],
      isAvailable: true,
      createdAt: new Date().toISOString(),
    };
    return mockWorld;
  }
);

const worldsSlice = createSlice({
  name: 'worlds',
  initialState,
  reducers: {
    setSelectedWorld: (state, action: PayloadAction<World | null>) => {
      state.selectedWorld = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch available worlds
      .addCase(fetchAvailableWorlds.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAvailableWorlds.fulfilled, (state, action) => {
        state.loading = false;
        state.availableWorlds = action.payload;
      })
      .addCase(fetchAvailableWorlds.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch worlds';
      })
      // Fetch world details
      .addCase(fetchWorldDetails.fulfilled, (state, action) => {
        state.selectedWorld = action.payload;
      });
  },
});

export const { setSelectedWorld, clearError } = worldsSlice.actions;
export default worldsSlice.reducer;
