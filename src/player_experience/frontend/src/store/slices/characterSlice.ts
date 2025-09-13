import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { characterAPI } from "../../services/api";

interface Character {
  character_id: string;
  player_id: string;
  name: string;
  appearance: {
    description: string; // Required for backward compatibility
    physical_description?: string;
    age_range?: string;
    gender_identity?: string;
    clothing_style?: string;
    distinctive_features?: string[];
    avatar_url?: string;
  };
  background: {
    name?: string;
    story: string; // Required for backward compatibility
    backstory?: string;
    personality_traits: string[];
    goals: string[]; // Required for backward compatibility
    life_goals?: string[];
  };
  therapeutic_profile: {
    comfort_level: number; // Required for backward compatibility
    primary_concerns?: string[];
    preferred_intensity: "LOW" | "MEDIUM" | "HIGH";
    therapeutic_goals: string[]; // Keep simple for backward compatibility
    comfort_zones?: string[];
    readiness_level?: number;
  };
  created_at: string;
  last_active: string;
  active_worlds: string[];
}

interface CharacterCreationData {
  name: string;
  appearance: {
    physical_description: string;
    age_range?: string;
    gender_identity?: string;
    clothing_style?: string;
    distinctive_features?: string[];
  };
  background: {
    name: string;
    backstory: string;
    personality_traits: string[];
    life_goals: string[];
  };
  therapeutic_profile: {
    primary_concerns: string[];
    preferred_intensity: "LOW" | "MEDIUM" | "HIGH";
    therapeutic_goals?: string[]; // Make optional to match form data
    comfort_zones?: string[]; // Make optional to match form data
    readiness_level: number;
    comfort_level: number; // Add for backward compatibility
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
  "character/fetchCharacters",
  async (playerId: string) => {
    const response = await characterAPI.getCharacters(playerId);
    return response;
  }
);

export const createCharacter = createAsyncThunk(
  "character/createCharacter",
  async ({
    playerId,
    characterData,
  }: {
    playerId: string;
    characterData: CharacterCreationData;
  }) => {
    const response = await characterAPI.createCharacter(
      playerId,
      characterData
    );
    return response;
  }
);

export const updateCharacter = createAsyncThunk(
  "character/updateCharacter",
  async ({
    characterId,
    updates,
  }: {
    characterId: string;
    updates: Partial<Character>;
  }) => {
    const response = await characterAPI.updateCharacter(characterId, updates);
    return response;
  }
);

export const deleteCharacter = createAsyncThunk(
  "character/deleteCharacter",
  async (characterId: string) => {
    await characterAPI.deleteCharacter(characterId);
    return characterId;
  }
);

const characterSlice = createSlice({
  name: "character",
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
        state.characters = action.payload as any;
      })
      .addCase(fetchCharacters.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || "Failed to fetch characters";
      })
      .addCase(createCharacter.pending, (state) => {
        state.creationInProgress = true;
        state.error = null;
      })
      .addCase(createCharacter.fulfilled, (state, action) => {
        state.creationInProgress = false;
        state.characters.push(action.payload as any);
      })
      .addCase(createCharacter.rejected, (state, action) => {
        state.creationInProgress = false;
        state.error = action.error.message || "Failed to create character";
      })
      .addCase(updateCharacter.fulfilled, (state, action) => {
        const payload = action.payload as any;
        const index = state.characters.findIndex(
          (c) => c.character_id === payload.character_id
        );
        if (index !== -1) {
          state.characters[index] = payload;
        }
        if (state.selectedCharacter?.character_id === payload.character_id) {
          state.selectedCharacter = payload;
        }
      })
      .addCase(deleteCharacter.fulfilled, (state, action) => {
        state.characters = state.characters.filter(
          (c) => c.character_id !== action.payload
        );
        if (state.selectedCharacter?.character_id === action.payload) {
          state.selectedCharacter = null;
        }
      });
  },
});

export const { clearError, selectCharacter, clearSelectedCharacter } =
  characterSlice.actions;
export default characterSlice.reducer;
