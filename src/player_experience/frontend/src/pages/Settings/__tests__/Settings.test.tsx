import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import Settings from '../Settings';
import settingsReducer from '../../../store/slices/settingsSlice';
import playerReducer from '../../../store/slices/playerSlice';

// Mock the API
jest.mock('../../../services/api', () => ({
  settingsAPI: {
    getSettings: jest.fn(),
    updateTherapeuticSettings: jest.fn(),
    updatePrivacySettings: jest.fn(),
    exportPlayerData: jest.fn(),
    deletePlayerData: jest.fn(),
  },
}));

// Mock the settings section components
jest.mock('../../../components/Settings/TherapeuticSettingsSection', () => {
  return function MockTherapeuticSettingsSection({ settings, onUpdate }: any) {
    return (
      <div data-testid="therapeutic-settings">
        <button onClick={() => onUpdate({ intensity_level: 'HIGH' })}>
          Update Intensity
        </button>
        <span>Intensity: {settings.intensity_level}</span>
      </div>
    );
  };
});

jest.mock('../../../components/Settings/PrivacySettingsSection', () => {
  return function MockPrivacySettingsSection({ settings, onUpdate }: any) {
    return (
      <div data-testid="privacy-settings">
        <button onClick={() => onUpdate({ research_participation: !settings.research_participation })}>
          Toggle Research
        </button>
        <span>Research: {settings.research_participation.toString()}</span>
      </div>
    );
  };
});

jest.mock('../../../components/Settings/CrisisSupportSection', () => {
  return function MockCrisisSupportSection() {
    return <div data-testid="crisis-support">Crisis Support</div>;
  };
});

const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      settings: settingsReducer,
      player: playerReducer,
    },
    preloadedState: {
      settings: {
        therapeutic: {
          intensity_level: 'MEDIUM',
          preferred_approaches: ['CBT'],
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
      },
      player: {
        profile: {
          player_id: 'test-player',
          username: 'testuser',
          email: 'test@example.com',
          created_at: '2024-01-01',
          therapeutic_preferences: {
            intensity_level: 'MEDIUM',
            preferred_approaches: [],
            trigger_warnings: [],
            comfort_topics: [],
            avoid_topics: [],
          },
          privacy_settings: {
            data_sharing_consent: false,
            research_participation: false,
            contact_preferences: [],
          },
          characters: [],
          active_sessions: {},
        },
        dashboard: null,
        isLoading: false,
        error: null,
      },
      ...initialState,
    },
  });
};

describe('Settings', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders settings page with tabs', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Therapeutic')).toBeInTheDocument();
    expect(screen.getByText('Privacy & Data')).toBeInTheDocument();
    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('Accessibility')).toBeInTheDocument();
    expect(screen.getByText('Crisis Support')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    const store = createMockStore({
      settings: {
        therapeutic: {},
        privacy: {},
        notifications: {},
        accessibility: {},
        isLoading: true,
        error: null,
        hasUnsavedChanges: false,
      },
    });
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    expect(screen.getByText('Loading settings...')).toBeInTheDocument();
  });

  it('displays error message when there is an error', () => {
    const store = createMockStore({
      settings: {
        therapeutic: {},
        privacy: {},
        notifications: {},
        accessibility: {},
        isLoading: false,
        error: 'Failed to load settings',
        hasUnsavedChanges: false,
      },
    });
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    expect(screen.getByText('Failed to load settings')).toBeInTheDocument();
  });

  it('shows unsaved changes indicator', () => {
    const store = createMockStore({
      settings: {
        therapeutic: {},
        privacy: {},
        notifications: {},
        accessibility: {},
        isLoading: false,
        error: null,
        hasUnsavedChanges: true,
      },
    });
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    expect(screen.getByText('Unsaved changes')).toBeInTheDocument();
    expect(screen.getByText('Save Changes')).toBeInTheDocument();
  });

  it('switches between tabs', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Default tab should be therapeutic
    expect(screen.getByTestId('therapeutic-settings')).toBeInTheDocument();

    // Switch to privacy tab
    fireEvent.click(screen.getByText('Privacy & Data'));
    expect(screen.getByTestId('privacy-settings')).toBeInTheDocument();
    expect(screen.queryByTestId('therapeutic-settings')).not.toBeInTheDocument();

    // Switch to crisis support tab
    fireEvent.click(screen.getByText('Crisis Support'));
    expect(screen.getByTestId('crisis-support')).toBeInTheDocument();
  });

  it('handles notification settings toggle', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Switch to notifications tab
    fireEvent.click(screen.getByText('Notifications'));

    // Find and toggle a notification setting
    const sessionRemindersToggle = screen.getByRole('checkbox', { name: /session reminders/i });
    expect(sessionRemindersToggle).toBeChecked();

    fireEvent.click(sessionRemindersToggle);
    expect(sessionRemindersToggle).not.toBeChecked();
  });

  it('handles accessibility settings toggle', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Switch to accessibility tab
    fireEvent.click(screen.getByText('Accessibility'));

    // Find and toggle an accessibility setting
    const highContrastToggle = screen.getByRole('checkbox', { name: /high contrast/i });
    expect(highContrastToggle).not.toBeChecked();

    fireEvent.click(highContrastToggle);
    expect(highContrastToggle).toBeChecked();
  });

  it('prevents tab switching with unsaved changes', () => {
    const store = createMockStore({
      settings: {
        therapeutic: {},
        privacy: {},
        notifications: {},
        accessibility: {},
        isLoading: false,
        error: null,
        hasUnsavedChanges: true,
      },
    });
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Try to switch tabs with unsaved changes
    fireEvent.click(screen.getByText('Privacy & Data'));

    // Should show warning modal
    expect(screen.getByText('Unsaved Changes')).toBeInTheDocument();
    expect(screen.getByText('You have unsaved changes. What would you like to do?')).toBeInTheDocument();
  });

  it('handles save changes from unsaved warning modal', async () => {
    const store = createMockStore({
      settings: {
        therapeutic: {},
        privacy: {},
        notifications: {},
        accessibility: {},
        isLoading: false,
        error: null,
        hasUnsavedChanges: true,
      },
    });
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Try to switch tabs with unsaved changes
    fireEvent.click(screen.getByText('Privacy & Data'));

    // Click save changes in modal
    fireEvent.click(screen.getByText('Save Changes'));

    // Modal should close
    await waitFor(() => {
      expect(screen.queryByText('Unsaved Changes')).not.toBeInTheDocument();
    });
  });

  it('handles discard changes from unsaved warning modal', async () => {
    const store = createMockStore({
      settings: {
        therapeutic: {},
        privacy: {},
        notifications: {},
        accessibility: {},
        isLoading: false,
        error: null,
        hasUnsavedChanges: true,
      },
    });
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Try to switch tabs with unsaved changes
    fireEvent.click(screen.getByText('Privacy & Data'));

    // Click discard changes in modal
    fireEvent.click(screen.getByText('Discard Changes'));

    // Modal should close
    await waitFor(() => {
      expect(screen.queryByText('Unsaved Changes')).not.toBeInTheDocument();
    });
  });

  it('updates therapeutic settings through child component', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Should show current intensity
    expect(screen.getByText('Intensity: MEDIUM')).toBeInTheDocument();

    // Update intensity through child component
    fireEvent.click(screen.getByText('Update Intensity'));

    // Should show updated intensity
    expect(screen.getByText('Intensity: HIGH')).toBeInTheDocument();
  });

  it('updates privacy settings through child component', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Switch to privacy tab
    fireEvent.click(screen.getByText('Privacy & Data'));

    // Should show current research participation
    expect(screen.getByText('Research: false')).toBeInTheDocument();

    // Update research participation through child component
    fireEvent.click(screen.getByText('Toggle Research'));

    // Should show updated research participation
    expect(screen.getByText('Research: true')).toBeInTheDocument();
  });

  it('handles save settings action', async () => {
    const store = createMockStore({
      settings: {
        therapeutic: {},
        privacy: {},
        notifications: {},
        accessibility: {},
        isLoading: false,
        error: null,
        hasUnsavedChanges: true,
      },
    });
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Click save changes button
    fireEvent.click(screen.getByText('Save Changes'));

    // Should dispatch save actions
    await waitFor(() => {
      // The unsaved changes indicator should disappear
      expect(screen.queryByText('Unsaved changes')).not.toBeInTheDocument();
    });
  });

  it('renders all notification options', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Switch to notifications tab
    fireEvent.click(screen.getByText('Notifications'));

    expect(screen.getByText('Session Reminders')).toBeInTheDocument();
    expect(screen.getByText('Progress Updates')).toBeInTheDocument();
    expect(screen.getByText('Milestone Celebrations')).toBeInTheDocument();
    expect(screen.getByText('Crisis Support Alerts')).toBeInTheDocument();
    expect(screen.getByText('Email Notifications')).toBeInTheDocument();
    expect(screen.getByText('Push Notifications')).toBeInTheDocument();
  });

  it('renders all accessibility options', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <Settings />
      </Provider>
    );

    // Switch to accessibility tab
    fireEvent.click(screen.getByText('Accessibility'));

    expect(screen.getByText('High Contrast Mode')).toBeInTheDocument();
    expect(screen.getByText('Large Text')).toBeInTheDocument();
    expect(screen.getByText('Screen Reader Optimization')).toBeInTheDocument();
    expect(screen.getByText('Reduced Motion')).toBeInTheDocument();
    expect(screen.getByText('Enhanced Keyboard Navigation')).toBeInTheDocument();
  });
});