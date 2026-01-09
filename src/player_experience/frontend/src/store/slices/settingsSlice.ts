// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Store/Slices/Settingsslice]]
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { settingsAPI } from '../../services/api';

interface TherapeuticSettings {
  intensity_level: 'LOW' | 'MEDIUM' | 'HIGH';
  preferred_approaches: string[];
  trigger_warnings: string[];
  comfort_topics: string[];
  avoid_topics: string[];
  crisis_contact_info?: {
    emergency_contact: string;
    therapist_contact?: string;
    preferred_crisis_resources: string[];
  };
}

interface PrivacySettings {
  data_sharing_consent: boolean;
  research_participation: boolean;
  contact_preferences: string[];
  data_retention_period: number;
  anonymize_data: boolean;
}

interface NotificationSettings {
  session_reminders: boolean;
  progress_updates: boolean;
  milestone_celebrations: boolean;
  crisis_alerts: boolean;
  email_notifications: boolean;
  push_notifications: boolean;
}

interface AccessibilitySettings {
  high_contrast: boolean;
  large_text: boolean;
  screen_reader_optimized: boolean;
  reduced_motion: boolean;
  keyboard_navigation: boolean;
}

interface SettingsState {
  therapeutic: TherapeuticSettings;
  privacy: PrivacySettings;
  notifications: NotificationSettings;
  accessibility: AccessibilitySettings;
  isLoading: boolean;
  error: string | null;
  hasUnsavedChanges: boolean;
}

const initialState: SettingsState = {
  therapeutic: {
    intensity_level: 'MEDIUM',
    preferred_approaches: [],
    trigger_warnings: [],
    comfort_topics: [],
    avoid_topics: [],
  },
  privacy: {
    data_sharing_consent: false,
    research_participation: false,
    contact_preferences: [],
    data_retention_period: 365,
    anonymize_data: true,
  },
  notifications: {
    session_reminders: true,
    progress_updates: true,
    milestone_celebrations: true,
    crisis_alerts: true,
    email_notifications: true,
    push_notifications: false,
  },
  accessibility: {
    high_contrast: false,
    large_text: false,
    screen_reader_optimized: false,
    reduced_motion: false,
    keyboard_navigation: false,
  },
  isLoading: false,
  error: null,
  hasUnsavedChanges: false,
};

export const fetchSettings = createAsyncThunk(
  'settings/fetchSettings',
  async (playerId: string) => {
    const response = await settingsAPI.getSettings(playerId);
    return response;
  }
);

export const updateTherapeuticSettings = createAsyncThunk(
  'settings/updateTherapeutic',
  async ({ playerId, settings }: { playerId: string; settings: Partial<TherapeuticSettings> }) => {
    const response = await settingsAPI.updateTherapeuticSettings(playerId, settings);
    return response;
  }
);

export const updatePrivacySettings = createAsyncThunk(
  'settings/updatePrivacy',
  async ({ playerId, settings }: { playerId: string; settings: Partial<PrivacySettings> }) => {
    const response = await settingsAPI.updatePrivacySettings(playerId, settings);
    return response;
  }
);

export const updateNotificationSettings = createAsyncThunk(
  'settings/updateNotifications',
  async ({ playerId, settings }: { playerId: string; settings: Partial<NotificationSettings> }) => {
    const response = await settingsAPI.updateNotificationSettings(playerId, settings);
    return response;
  }
);

export const updateAccessibilitySettings = createAsyncThunk(
  'settings/updateAccessibility',
  async ({ playerId, settings }: { playerId: string; settings: Partial<AccessibilitySettings> }) => {
    const response = await settingsAPI.updateAccessibilitySettings(playerId, settings);
    return response;
  }
);

export const exportPlayerData = createAsyncThunk(
  'settings/exportData',
  async (playerId: string) => {
    const response = await settingsAPI.exportPlayerData(playerId);
    return response;
  }
);

export const deletePlayerData = createAsyncThunk(
  'settings/deleteData',
  async (playerId: string) => {
    const response = await settingsAPI.deletePlayerData(playerId);
    return response;
  }
);

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    updateTherapeuticLocal: (state, action: PayloadAction<Partial<TherapeuticSettings>>) => {
      state.therapeutic = { ...state.therapeutic, ...action.payload };
      state.hasUnsavedChanges = true;
    },
    updatePrivacyLocal: (state, action: PayloadAction<Partial<PrivacySettings>>) => {
      state.privacy = { ...state.privacy, ...action.payload };
      state.hasUnsavedChanges = true;
    },
    updateNotificationsLocal: (state, action: PayloadAction<Partial<NotificationSettings>>) => {
      state.notifications = { ...state.notifications, ...action.payload };
      state.hasUnsavedChanges = true;
    },
    updateAccessibilityLocal: (state, action: PayloadAction<Partial<AccessibilitySettings>>) => {
      state.accessibility = { ...state.accessibility, ...action.payload };
      state.hasUnsavedChanges = true;
    },
    markChangesSaved: (state) => {
      state.hasUnsavedChanges = false;
    },
    resetToDefaults: (state) => {
      return { ...initialState, isLoading: state.isLoading, error: state.error };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSettings.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchSettings.fulfilled, (state, action) => {
        state.isLoading = false;
        state.therapeutic = action.payload.therapeutic;
        state.privacy = action.payload.privacy;
        state.notifications = action.payload.notifications;
        state.accessibility = action.payload.accessibility;
        state.hasUnsavedChanges = false;
      })
      .addCase(fetchSettings.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch settings';
      })
      .addCase(updateTherapeuticSettings.fulfilled, (state, action) => {
        state.therapeutic = action.payload;
        state.hasUnsavedChanges = false;
      })
      .addCase(updatePrivacySettings.fulfilled, (state, action) => {
        state.privacy = action.payload;
        state.hasUnsavedChanges = false;
      })
      .addCase(updateNotificationSettings.fulfilled, (state, action) => {
        state.notifications = action.payload;
        state.hasUnsavedChanges = false;
      })
      .addCase(updateAccessibilitySettings.fulfilled, (state, action) => {
        state.accessibility = action.payload;
        state.hasUnsavedChanges = false;
      });
  },
});

export const {
  clearError,
  updateTherapeuticLocal,
  updatePrivacyLocal,
  updateNotificationsLocal,
  updateAccessibilityLocal,
  markChangesSaved,
  resetToDefaults,
} = settingsSlice.actions;

export default settingsSlice.reducer;
