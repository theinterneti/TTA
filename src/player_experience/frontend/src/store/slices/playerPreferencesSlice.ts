import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import {
  PlayerPreferences,
  DEFAULT_PREFERENCES,
  PreferenceValidationResult,
  PreferencePreviewContext
} from '../../types/preferences';
import { preferencesAPI } from '../../services/api';

interface PlayerPreferencesState {
  preferences: PlayerPreferences | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  hasUnsavedChanges: boolean;
  validationResult: PreferenceValidationResult | null;
  previewContext: PreferencePreviewContext | null;
  isPreviewLoading: boolean;
}

const initialState: PlayerPreferencesState = {
  preferences: null,
  isLoading: false,
  isSaving: false,
  error: null,
  hasUnsavedChanges: false,
  validationResult: null,
  previewContext: null,
  isPreviewLoading: false,
};

// Async thunks for API operations
export const fetchPlayerPreferences = createAsyncThunk(
  'playerPreferences/fetch',
  async (playerId: string) => {
    const response = await preferencesAPI.getPreferences(playerId);
    return response;
  }
);

export const savePlayerPreferences = createAsyncThunk(
  'playerPreferences/save',
  async ({ playerId, preferences }: { playerId: string; preferences: Partial<PlayerPreferences> }) => {
    const response = await preferencesAPI.updatePreferences(playerId, preferences);
    return response;
  }
);

export const createPlayerPreferences = createAsyncThunk(
  'playerPreferences/create',
  async (playerId: string) => {
    const newPreferences: PlayerPreferences = {
      ...DEFAULT_PREFERENCES,
      player_id: playerId,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    const response = await preferencesAPI.createPreferences(newPreferences);
    return response;
  }
);

export const generatePreferencePreview = createAsyncThunk(
  'playerPreferences/generatePreview',
  async ({ preferences, testMessage }: { preferences: PlayerPreferences; testMessage: string }) => {
    const response = await preferencesAPI.generatePreview(preferences, testMessage);
    return response;
  }
);

export const validatePreferences = createAsyncThunk(
  'playerPreferences/validate',
  async (preferences: Partial<PlayerPreferences>) => {
    const response = await preferencesAPI.validatePreferences(preferences);
    return response;
  }
);

export const exportPreferences = createAsyncThunk(
  'playerPreferences/export',
  async (playerId: string) => {
    const response = await preferencesAPI.exportPreferences(playerId);
    return response;
  }
);

export const importPreferences = createAsyncThunk(
  'playerPreferences/import',
  async ({ playerId, preferencesData }: { playerId: string; preferencesData: any }) => {
    const response = await preferencesAPI.importPreferences(playerId, preferencesData);
    return response;
  }
);

const playerPreferencesSlice = createSlice({
  name: 'playerPreferences',
  initialState,
  reducers: {
    // Local preference updates (before saving)
    updatePreferencesLocal: (state, action: PayloadAction<Partial<PlayerPreferences>>) => {
      if (state.preferences) {
        state.preferences = {
          ...state.preferences,
          ...action.payload,
          updated_at: new Date().toISOString(),
          version: state.preferences.version + 1,
        };
        state.hasUnsavedChanges = true;
        state.validationResult = null; // Clear previous validation
      }
    },

    // Update specific preference fields
    updateIntensityLevel: (state, action: PayloadAction<PlayerPreferences['intensity_level']>) => {
      if (state.preferences) {
        state.preferences.intensity_level = action.payload;
        state.preferences.updated_at = new Date().toISOString();
        state.hasUnsavedChanges = true;
      }
    },

    updateTherapeuticApproaches: (state, action: PayloadAction<PlayerPreferences['preferred_approaches']>) => {
      if (state.preferences) {
        state.preferences.preferred_approaches = action.payload;
        state.preferences.updated_at = new Date().toISOString();
        state.hasUnsavedChanges = true;
      }
    },

    updateConversationStyle: (state, action: PayloadAction<PlayerPreferences['conversation_style']>) => {
      if (state.preferences) {
        state.preferences.conversation_style = action.payload;
        state.preferences.updated_at = new Date().toISOString();
        state.hasUnsavedChanges = true;
      }
    },

    updateTherapeuticGoals: (state, action: PayloadAction<string[]>) => {
      if (state.preferences) {
        state.preferences.therapeutic_goals = action.payload;
        state.preferences.updated_at = new Date().toISOString();
        state.hasUnsavedChanges = true;
      }
    },

    updateCharacterCustomization: (state, action: PayloadAction<{
      character_name?: string;
      preferred_setting?: PlayerPreferences['preferred_setting'];
    }>) => {
      if (state.preferences) {
        if (action.payload.character_name !== undefined) {
          state.preferences.character_name = action.payload.character_name;
        }
        if (action.payload.preferred_setting !== undefined) {
          state.preferences.preferred_setting = action.payload.preferred_setting;
        }
        state.preferences.updated_at = new Date().toISOString();
        state.hasUnsavedChanges = true;
      }
    },

    updateTopicPreferences: (state, action: PayloadAction<{
      comfort_topics?: string[];
      trigger_topics?: string[];
      avoid_topics?: string[];
    }>) => {
      if (state.preferences) {
        if (action.payload.comfort_topics !== undefined) {
          state.preferences.comfort_topics = action.payload.comfort_topics;
        }
        if (action.payload.trigger_topics !== undefined) {
          state.preferences.trigger_topics = action.payload.trigger_topics;
        }
        if (action.payload.avoid_topics !== undefined) {
          state.preferences.avoid_topics = action.payload.avoid_topics;
        }
        state.preferences.updated_at = new Date().toISOString();
        state.hasUnsavedChanges = true;
      }
    },

    // Clear unsaved changes flag
    markChangesSaved: (state) => {
      state.hasUnsavedChanges = false;
    },

    // Clear error state
    clearError: (state) => {
      state.error = null;
    },

    // Clear validation result
    clearValidation: (state) => {
      state.validationResult = null;
    },

    // Clear preview context
    clearPreview: (state) => {
      state.previewContext = null;
    },

    // Reset to initial state
    resetPreferences: (state) => {
      return initialState;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch preferences
      .addCase(fetchPlayerPreferences.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPlayerPreferences.fulfilled, (state, action) => {
        state.isLoading = false;
        state.preferences = action.payload;
        state.hasUnsavedChanges = false;
      })
      .addCase(fetchPlayerPreferences.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch preferences';
      })

      // Save preferences
      .addCase(savePlayerPreferences.pending, (state) => {
        state.isSaving = true;
        state.error = null;
      })
      .addCase(savePlayerPreferences.fulfilled, (state, action) => {
        state.isSaving = false;
        state.preferences = action.payload;
        state.hasUnsavedChanges = false;
      })
      .addCase(savePlayerPreferences.rejected, (state, action) => {
        state.isSaving = false;
        state.error = action.error.message || 'Failed to save preferences';
      })

      // Create preferences
      .addCase(createPlayerPreferences.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createPlayerPreferences.fulfilled, (state, action) => {
        state.isLoading = false;
        state.preferences = action.payload;
        state.hasUnsavedChanges = false;
      })
      .addCase(createPlayerPreferences.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to create preferences';
      })

      // Generate preview
      .addCase(generatePreferencePreview.pending, (state) => {
        state.isPreviewLoading = true;
      })
      .addCase(generatePreferencePreview.fulfilled, (state, action) => {
        state.isPreviewLoading = false;
        state.previewContext = action.payload;
      })
      .addCase(generatePreferencePreview.rejected, (state, action) => {
        state.isPreviewLoading = false;
        state.error = action.error.message || 'Failed to generate preview';
      })

      // Validate preferences
      .addCase(validatePreferences.fulfilled, (state, action) => {
        state.validationResult = action.payload;
      })
      .addCase(validatePreferences.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to validate preferences';
      })

      // Export preferences
      .addCase(exportPreferences.fulfilled, (state, action) => {
        // Trigger download of exported data
        const blob = new Blob([JSON.stringify(action.payload, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tta-preferences-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      })
      .addCase(exportPreferences.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to export preferences';
      })

      // Import preferences
      .addCase(importPreferences.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(importPreferences.fulfilled, (state, action) => {
        state.isLoading = false;
        state.preferences = action.payload;
        state.hasUnsavedChanges = false;
      })
      .addCase(importPreferences.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to import preferences';
      });
  },
});

export const {
  updatePreferencesLocal,
  updateIntensityLevel,
  updateTherapeuticApproaches,
  updateConversationStyle,
  updateTherapeuticGoals,
  updateCharacterCustomization,
  updateTopicPreferences,
  markChangesSaved,
  clearError,
  clearValidation,
  clearPreview,
  resetPreferences,
} = playerPreferencesSlice.actions;

export default playerPreferencesSlice.reducer;
