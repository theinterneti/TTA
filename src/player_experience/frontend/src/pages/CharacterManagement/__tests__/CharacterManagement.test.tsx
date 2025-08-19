import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import CharacterManagement from '../CharacterManagement';
import characterReducer from '../../../store/slices/characterSlice';
import playerReducer from '../../../store/slices/playerSlice';

const mockCharacters = [
  {
    character_id: '1',
    player_id: 'player1',
    name: 'Test Character',
    appearance: {
      description: 'A brave adventurer',
    },
    background: {
      story: 'Born in a village',
      personality_traits: ['Brave', 'Kind'],
      goals: ['Find peace'],
    },
    therapeutic_profile: {
      comfort_level: 7,
      preferred_intensity: 'MEDIUM' as const,
      therapeutic_goals: ['Anxiety management'],
    },
    created_at: '2024-01-01T00:00:00Z',
    last_active: '2024-01-02T00:00:00Z',
    active_worlds: ['world1'],
  },
];

const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      character: characterReducer,
      player: playerReducer,
    },
    preloadedState: initialState,
  });
};

const renderWithProvider = (
  ui: React.ReactElement,
  { initialState = {}, store = createMockStore(initialState) } = {}
) => {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <Provider store={store}>{children}</Provider>
  );
  return render(ui, { wrapper: Wrapper });
};

// Mock the character components to avoid complex form testing
jest.mock('../../../components/Character/CharacterCreationForm', () => {
  return function MockCharacterCreationForm({ onClose, onSuccess }: any) {
    return (
      <div data-testid="character-creation-form">
        <button onClick={onClose}>Close</button>
        <button onClick={onSuccess}>Success</button>
      </div>
    );
  };
});

jest.mock('../../../components/Character/CharacterEditForm', () => {
  return function MockCharacterEditForm({ onClose, onSuccess }: any) {
    return (
      <div data-testid="character-edit-form">
        <button onClick={onClose}>Close</button>
        <button onClick={onSuccess}>Success</button>
      </div>
    );
  };
});

describe('CharacterManagement', () => {
  const mockInitialState = {
    player: {
      profile: {
        player_id: 'player1',
        username: 'testuser',
        email: 'test@example.com',
        created_at: '2024-01-01T00:00:00Z',
        therapeutic_preferences: {
          intensity_level: 'MEDIUM' as const,
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
        characters: ['1'],
        active_sessions: {},
      },
      dashboard: null,
      isLoading: false,
      error: null,
    },
    character: {
      characters: mockCharacters,
      selectedCharacter: null,
      isLoading: false,
      error: null,
      creationInProgress: false,
    },
  };

  test('renders character management page with characters', () => {
    renderWithProvider(<CharacterManagement />, { initialState: mockInitialState });

    expect(screen.getByText('Character Management')).toBeInTheDocument();
    expect(screen.getByText('Create and manage your therapeutic adventure characters')).toBeInTheDocument();
    expect(screen.getByText('Test Character')).toBeInTheDocument();
  });

  test('shows character limit information', () => {
    renderWithProvider(<CharacterManagement />, { initialState: mockInitialState });

    expect(screen.getByText(/You have 1 of 5 characters/)).toBeInTheDocument();
  });

  test('shows create character button', () => {
    renderWithProvider(<CharacterManagement />, { initialState: mockInitialState });

    expect(screen.getByText('Create Character')).toBeInTheDocument();
  });

  test('disables create button when at character limit', () => {
    const stateWithMaxCharacters = {
      ...mockInitialState,
      character: {
        ...mockInitialState.character,
        characters: Array(5).fill(null).map((_, i) => ({
          ...mockCharacters[0],
          character_id: `${i + 1}`,
          name: `Character ${i + 1}`,
        })),
      },
    };

    renderWithProvider(<CharacterManagement />, { initialState: stateWithMaxCharacters });

    const createButton = screen.getByText('Create Character');
    expect(createButton).toBeDisabled();
  });

  test('opens character creation form when create button is clicked', () => {
    renderWithProvider(<CharacterManagement />, { initialState: mockInitialState });

    const createButton = screen.getByText('Create Character');
    fireEvent.click(createButton);

    expect(screen.getByTestId('character-creation-form')).toBeInTheDocument();
  });

  test('closes character creation form', () => {
    renderWithProvider(<CharacterManagement />, { initialState: mockInitialState });

    const createButton = screen.getByText('Create Character');
    fireEvent.click(createButton);

    const closeButton = screen.getByText('Close');
    fireEvent.click(closeButton);

    expect(screen.queryByTestId('character-creation-form')).not.toBeInTheDocument();
  });

  test('shows empty state when no characters exist', () => {
    const emptyState = {
      ...mockInitialState,
      character: {
        ...mockInitialState.character,
        characters: [],
      },
    };

    renderWithProvider(<CharacterManagement />, { initialState: emptyState });

    expect(screen.getByText('No characters yet')).toBeInTheDocument();
    expect(screen.getByText('Create your first character to begin your therapeutic journey')).toBeInTheDocument();
  });

  test('shows loading state', () => {
    const loadingState = {
      ...mockInitialState,
      character: {
        ...mockInitialState.character,
        isLoading: true,
      },
    };

    renderWithProvider(<CharacterManagement />, { initialState: loadingState });

    expect(screen.getByText('Loading characters...')).toBeInTheDocument();
  });

  test('shows error state', () => {
    const errorState = {
      ...mockInitialState,
      character: {
        ...mockInitialState.character,
        error: 'Failed to load characters',
      },
    };

    renderWithProvider(<CharacterManagement />, { initialState: errorState });

    expect(screen.getByText('Failed to load characters')).toBeInTheDocument();
  });

  test('toggles between grid and list view', () => {
    renderWithProvider(<CharacterManagement />, { initialState: mockInitialState });

    // Should start in grid view
    const container = screen.getByText('Test Character').closest('.grid');
    expect(container).toHaveClass('grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-3');

    // Click list view button
    const listViewButton = screen.getAllByRole('button').find(button => 
      button.querySelector('svg')?.querySelector('path')?.getAttribute('d')?.includes('M4 6h16M4 10h16M4 14h16M4 18h16')
    );
    
    if (listViewButton) {
      fireEvent.click(listViewButton);
      
      // Should now be in list view
      const listContainer = screen.getByText('Test Character').closest('.space-y-4');
      expect(listContainer).toBeInTheDocument();
    }
  });

  test('opens edit form when character edit is triggered', async () => {
    renderWithProvider(<CharacterManagement />, { initialState: mockInitialState });

    // Find and click the edit button (this would be in the CharacterCard component)
    // Since we're testing the integration, we need to simulate the edit action
    const editButton = screen.getByText('Edit Details');
    fireEvent.click(editButton);

    await waitFor(() => {
      expect(screen.getByTestId('character-edit-form')).toBeInTheDocument();
    });
  });

  test('handles character creation success', () => {
    renderWithProvider(<CharacterManagement />, { initialState: mockInitialState });

    const createButton = screen.getByText('Create Character');
    fireEvent.click(createButton);

    const successButton = screen.getByText('Success');
    fireEvent.click(successButton);

    // Form should close after success
    expect(screen.queryByTestId('character-creation-form')).not.toBeInTheDocument();
  });
});