import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import WorldSelection from '../../../pages/WorldSelection/WorldSelection';
import worldReducer from '../../../store/slices/worldSlice';
import characterReducer from '../../../store/slices/characterSlice';
import playerReducer from '../../../store/slices/playerSlice';

// Mock the API calls
jest.mock('../../../services/api', () => ({
  worldAPI: {
    getAvailableWorlds: jest.fn().mockResolvedValue([]),
    getWorldDetails: jest.fn().mockResolvedValue({}),
    checkCompatibility: jest.fn().mockResolvedValue({ compatibility_score: 0.8 }),
  },
}));

// Mock the modal components to avoid complex rendering
jest.mock('../../../components/World/WorldDetailsModal', () => {
  return function MockWorldDetailsModal() {
    return <div data-testid="world-details-modal">World Details Modal</div>;
  };
});

jest.mock('../../../components/World/WorldCustomizationModal', () => {
  return function MockWorldCustomizationModal() {
    return <div data-testid="world-customization-modal">World Customization Modal</div>;
  };
});

const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      world: worldReducer,
      character: characterReducer,
      player: playerReducer,
    },
    preloadedState: {
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
      character: {
        characters: [],
        selectedCharacter: null,
        isLoading: false,
        error: null,
        creationInProgress: false,
      },
      player: {
        profile: {
          player_id: 'test-player',
          username: 'testuser',
          email: 'test@example.com',
          created_at: '2024-01-01',
          therapeutic_preferences: {
            intensity_level: 'MEDIUM' as const,
            preferred_approaches: [],
            trigger_warnings: [],
            comfort_topics: [],
            avoid_topics: [],
          },
          privacy_settings: {
            data_sharing_consent: true,
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

describe('WorldSelection Integration', () => {
  it('renders the world selection page', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <WorldSelection />
      </Provider>
    );

    expect(screen.getByText('World Selection')).toBeInTheDocument();
    expect(screen.getByText(/Choose therapeutic environments/)).toBeInTheDocument();
  });

  it('shows character selection notice when no character is selected', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <WorldSelection />
      </Provider>
    );

    expect(screen.getByText(/Please select a character first/)).toBeInTheDocument();
  });

  it('displays search and filter controls', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <WorldSelection />
      </Provider>
    );

    expect(screen.getByPlaceholderText(/Search worlds/)).toBeInTheDocument();
    expect(screen.getByDisplayValue('All Levels')).toBeInTheDocument();
    expect(screen.getByDisplayValue('All Themes')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Any Duration')).toBeInTheDocument();
  });

  it('shows empty state when no worlds are available', () => {
    const store = createMockStore();
    
    render(
      <Provider store={store}>
        <WorldSelection />
      </Provider>
    );

    expect(screen.getByText('No worlds available')).toBeInTheDocument();
  });

  it('displays worlds when available', () => {
    const mockWorlds = [
      {
        world_id: 'world-1',
        name: 'Test World',
        description: 'A test world',
        therapeutic_themes: ['anxiety'],
        difficulty_level: 'BEGINNER' as const,
        estimated_duration: '2 hours',
        compatibility_score: 0.8,
      },
    ];

    const store = createMockStore({
      world: {
        availableWorlds: mockWorlds,
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
    });
    
    render(
      <Provider store={store}>
        <WorldSelection />
      </Provider>
    );

    expect(screen.getByText('Test World')).toBeInTheDocument();
    expect(screen.getByText('A test world')).toBeInTheDocument();
    expect(screen.getByText('anxiety')).toBeInTheDocument();
  });

  it('allows filtering by search term', () => {
    const mockWorlds = [
      {
        world_id: 'world-1',
        name: 'Peaceful Garden',
        description: 'A calming environment',
        therapeutic_themes: ['anxiety'],
        difficulty_level: 'BEGINNER' as const,
        estimated_duration: '2 hours',
        compatibility_score: 0.8,
      },
      {
        world_id: 'world-2',
        name: 'Urban Challenge',
        description: 'A challenging city environment',
        therapeutic_themes: ['confidence'],
        difficulty_level: 'ADVANCED' as const,
        estimated_duration: '4 hours',
        compatibility_score: 0.6,
      },
    ];

    const store = createMockStore({
      world: {
        availableWorlds: mockWorlds,
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
    });
    
    render(
      <Provider store={store}>
        <WorldSelection />
      </Provider>
    );

    // Initially both worlds should be visible
    expect(screen.getByText('Peaceful Garden')).toBeInTheDocument();
    expect(screen.getByText('Urban Challenge')).toBeInTheDocument();

    // Filter by search term
    const searchInput = screen.getByPlaceholderText(/Search worlds/);
    fireEvent.change(searchInput, { target: { value: 'garden' } });

    // Only the matching world should be visible
    expect(screen.getByText('Peaceful Garden')).toBeInTheDocument();
    expect(screen.queryByText('Urban Challenge')).not.toBeInTheDocument();
  });

  it('shows loading state', () => {
    const store = createMockStore({
      world: {
        availableWorlds: [],
        selectedWorld: null,
        worldParameters: null,
        isLoading: true,
        error: null,
        filters: {
          difficulty: [],
          themes: [],
          duration: '',
        },
      },
    });
    
    render(
      <Provider store={store}>
        <WorldSelection />
      </Provider>
    );

    expect(screen.getByText('Loading worlds...')).toBeInTheDocument();
  });
});