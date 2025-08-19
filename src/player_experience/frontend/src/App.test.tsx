import React from 'react';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import App from './App';
import authReducer from './store/slices/authSlice';
import playerReducer from './store/slices/playerSlice';
import characterReducer from './store/slices/characterSlice';
import worldReducer from './store/slices/worldSlice';
import chatReducer from './store/slices/chatSlice';
import settingsReducer from './store/slices/settingsSlice';

// Mock store for testing
const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: authReducer,
      player: playerReducer,
      character: characterReducer,
      world: worldReducer,
      chat: chatReducer,
      settings: settingsReducer,
    },
    preloadedState: initialState,
  });
};

const renderWithProviders = (
  ui: React.ReactElement,
  {
    initialState = {},
    store = createMockStore(initialState),
    ...renderOptions
  } = {}
) => {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <Provider store={store}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </Provider>
  );

  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
};

describe('App Component', () => {
  test('renders login page when not authenticated', () => {
    const initialState = {
      auth: {
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      },
    };

    renderWithProviders(<App />, { initialState });
    
    expect(screen.getByText('Welcome to TTA')).toBeInTheDocument();
    expect(screen.getByText('Therapeutic Text Adventure Platform')).toBeInTheDocument();
  });

  test('renders main app when authenticated', () => {
    const initialState = {
      auth: {
        user: { id: '1', username: 'testuser', email: 'test@example.com' },
        token: 'mock-token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
      },
      player: {
        profile: null,
        dashboard: null,
        isLoading: false,
        error: null,
      },
      character: {
        characters: [],
        selectedCharacter: null,
        isLoading: false,
        error: null,
        creationInProgress: false,
      },
      world: {
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
      },
      chat: {
        currentSession: null,
        sessions: [],
        isConnected: false,
        isTyping: false,
        connectionError: null,
        messageHistory: [],
      },
      settings: {
        therapeutic: {
          intensity_level: 'MEDIUM' as const,
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
      },
    };

    renderWithProviders(<App />, { initialState });
    
    // Should redirect to dashboard and show the main layout
    expect(screen.getByText('TTA')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });
});