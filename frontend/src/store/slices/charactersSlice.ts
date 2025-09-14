import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

export interface Character {
  id: string;
  name: string;
  description: string;
  archetype: string;
  traits: string[];
  backstory: string;
  therapeuticGoals: string[];
  createdAt: string;
  updatedAt: string;
}

interface CharactersState {
  characters: Character[];
  selectedCharacter: Character | null;
  loading: boolean;
  error: string | null;
}

const initialState: CharactersState = {
  characters: [],
  selectedCharacter: null,
  loading: false,
  error: null,
};

// Async thunks with mock data
export const fetchCharacters = createAsyncThunk(
  'characters/fetchCharacters',
  async (playerId: string) => {
    // Mock data for now
    const mockCharacters: Character[] = [
      {
        id: '1',
        name: 'Alex the Explorer',
        description: 'A curious adventurer who helps players discover new perspectives',
        archetype: 'Explorer',
        traits: ['Curious', 'Brave', 'Empathetic'],
        backstory: 'Alex grew up in a small town but always dreamed of seeing the world...',
        therapeuticGoals: ['Build confidence', 'Encourage exploration'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];
    return mockCharacters;
  }
);

export const createCharacter = createAsyncThunk(
  'characters/createCharacter',
  async (characterData: Omit<Character, 'id' | 'createdAt' | 'updatedAt'>) => {
    // Mock creation
    const newCharacter: Character = {
      id: Date.now().toString(),
      ...characterData,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    return newCharacter;
  }
);

export const updateCharacter = createAsyncThunk(
  'characters/updateCharacter',
  async ({ characterId, updates }: { characterId: string; updates: Partial<Character> }) => {
    // Mock update
    return { characterId, updates: { ...updates, updatedAt: new Date().toISOString() } };
  }
);

export const deleteCharacter = createAsyncThunk(
  'characters/deleteCharacter',
  async (characterId: string) => {
    // Mock deletion
    return characterId;
  }
);

const charactersSlice = createSlice({
  name: 'characters',
  initialState,
  reducers: {
    setSelectedCharacter: (state, action: PayloadAction<Character | null>) => {
      state.selectedCharacter = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch characters
      .addCase(fetchCharacters.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCharacters.fulfilled, (state, action) => {
        state.loading = false;
        state.characters = action.payload;
      })
      .addCase(fetchCharacters.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch characters';
      })
      // Create character
      .addCase(createCharacter.fulfilled, (state, action) => {
        state.characters.push(action.payload);
      })
      // Update character
      .addCase(updateCharacter.fulfilled, (state, action) => {
        const { characterId, updates } = action.payload;
        const index = state.characters.findIndex(c => c.id === characterId);
        if (index !== -1) {
          state.characters[index] = { ...state.characters[index], ...updates };
        }
      })
      // Delete character
      .addCase(deleteCharacter.fulfilled, (state, action) => {
        state.characters = state.characters.filter(c => c.id !== action.payload);
        if (state.selectedCharacter?.id === action.payload) {
          state.selectedCharacter = null;
        }
      });
  },
});

export const { setSelectedCharacter, clearError } = charactersSlice.actions;
export default charactersSlice.reducer;
