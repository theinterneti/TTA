import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { characterAPI } from '../../services/api';

interface Character {
  character_id: string;
  player_id: string;
  name: string;
  appearance: {
    description: string;
    avatar_url?: string;
  };
  background: {
    story: string;
    personality_traits: string[];
    goals: string[];
  };
  therapeutic_profile: {
    comfort_level: number;
    preferred_intensity: 'LOW' | 'MEDIUM' | 'HIGH';
    therapeutic_goals: string[];
  };
  created_at: string;
  last_active: string;
  active_worlds: string[];
}

interface CharacterCreationData {
  name: string;
  appearance: {
    description: string;
  };
  background: {
    story: string;
    personality_traits: string[];
    goals: string[];
  };
  therapeutic_profile: {
    comfort_level: number;
    preferred_intensity: 'LOW' | 'MEDIUM' | 'HIGH';
    therapeutic_goals: string[];
  };
}

interface CharacterState {
  characters: Character[];
  selectedCharacter: Character | null;
  isLoading: boolean;
  error: string | null;
  creationInProgress: boolean;
}

const initialState: CharacterState = {
  characters: [],
  selectedCharacter: null,
  isLoading: false,
  error: null,
  creationInProgress: false,
};

export const fetchCharacters = createAsyncThunk(
  'character/fetchCharacters',
  async (playerId: string) => {
    const response = await characterAPI.getCharacters(playerId);
    return response;
  }
);

export const createCharacter = createAsyncThunk(
  'character/createCharacter',
  async ({ playerId, characterData }: { playerId: string; characterData: CharacterCreationData }) => {
    const response = await characterAPI.createCharacter(playerId, characterData);
    return response;
  }
);

export const updateCharacter = createAsyncThunk(
  'character/updateCharacter',
  async ({ characterId, updates }: { characterId: string; updates: Partial<Character> }) => {
    const response = await characterAPI.updateCharacter(characterId, updates);
    return response;
  }
);

export const deleteCharacter = createAsyncThunk(
  'character/deleteCharacter',
  async (characterId: string) => {
    await characterAPI.deleteCharacter(characterId);
    return characterId;
  }
);

const characterSlice = createSlice({
  name: 'character',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    selectCharacter: (state, action: PayloadAction<Character>) => {
      state.selectedCharacter = action.payload;
    },
    clearSelectedCharacter: (state) => {
      state.selectedCharacter = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCharacters.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCharacters.fulfilled, (state, action) => {
        state.isLoading = false;
        state.characters = action.payload;
      })
      .addCase(fetchCharacters.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch characters';
      })
      .addCase(createCharacter.pending, (state) => {
        state.creationInProgress = true;
        state.error = null;
      })
      .addCase(createCharacter.fulfilled, (state, action) => {
        state.creationInProgress = false;
        state.characters.push(action.payload);
      })
      .addCase(createCharacter.rejected, (state, action) => {
        state.creationInProgress = false;
        state.error = action.error.message || 'Failed to create character';
      })
      .addCase(updateCharacter.fulfilled, (state, action) => {
        const index = state.characters.findIndex(c => c.character_id === action.payload.character_id);
        if (index !== -1) {
          state.characters[index] = action.payload;
        }
        if (state.selectedCharacter?.character_id === action.payload.character_id) {
          state.selectedCharacter = action.payload;
        }
      })
      .addCase(deleteCharacter.fulfilled, (state, action) => {
        state.characters = state.characters.filter(c => c.character_id !== action.payload);
        if (state.selectedCharacter?.character_id === action.payload) {
          state.selectedCharacter = null;
        }
      });
  },
});

export const { clearError, selectCharacter, clearSelectedCharacter } = characterSlice.actions;
export default characterSlice.reducer;
