import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import WorldSelection from '../WorldSelection';
import worldReducer from '../../../store/slices/worldSlice';
import characterReducer from '../../../store/slices/characterSlice';
import playerReducer from '../../../store/slices/playerSlice';

// Mock the API
jest.mock('../../../services/api', () => ({
  worldAPI: {
    getAvailableWorlds: jest.fn(),
    getWorldDetails: jest.fn(),
    checkCompatibility: jest.fn(),
  },
}));

// Mock the modal components
jest.mock('../../../components/World/WorldDetailsModal', () => {
  return function MockWorldDetailsModal({ isOpen, onClose }: any) {
    return isOpen ? (
      <div data-testid="world-details-modal">
        <button onClick={onClose}>Close Modal</button>
      </div>
    ) : null;
  };
});

jest.mock('../../../components/World/WorldCustomizationModal', () => {
  return function MockWorldCustomizationModal({ isOpen, onClose, onConfirm }: any) {
    return isOpen ? (
      <div data-testid="world-customization-modal">
        <button onClick={onClose}>Close Modal</button>
        <button onClick={() => onConfirm({ therapeutic_intensity: 'MEDIUM' })}>
          Confirm
        </button>
      </div>
    ) : null;
  };
});

const mockWorlds = [
  {
    world_id: 'world-1',
    name: 'Peaceful Garden',
    description: 'A calming therapeutic environment focused on mindfulness',
    therapeutic_themes: ['anxiety', 'mindfulness'],
    difficulty_level: 'BEGINNER' as const,
    estimated_duration: '2-3 hours',
    compatibility_score: 0.9,
  },
  {
    world_id: 'world-2',
    name: 'Urban Challenge',
    description: 'Navigate social situations in a city environment',
    therapeutic_themes: ['social anxiety', 'confidence'],
    difficulty_level: 'ADVANCED' as const,
    estimated_duration: '4-6 hours',
    compatibility_score: 0.6,
  },
  {
    world_id: 'world-3',
    name: 'Family Dynamics',
    description: 'Explore family relationships and communication',
    therapeutic_themes: ['relationships', 'communication'],
    difficulty_level: 'INTERMEDIATE' as const,
    estimated_duration: '3-4 hours',
    compatibility_score: 0.75,
  },
];

const mockStore = configureStore({
  reducer: {
    world: worldReducer,
    character: characterReducer,
    player: playerReducer,
  },
  preloadedState: {
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
    character: {
      characters: [],
      selectedCharacter: {
        character_id: 'char-1',
        name: 'Test Character',
        therapeutic_profile: {
          preferred_intensity: 'MEDIUM' as const,
        },
      },
      isLoading: false,
      error: null,
    },
    player: {
      profile: {
        player_id: 'player-1',
        username: 'testuser',
      },
      isLoading: false,
      error: null,
    },
  },
});

const renderWithProvider = (store = mockStore) => {
  return render(
    <Provider store={store}>
      <WorldSelection />
    </Provider>
  );
};

describe('WorldSelection', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders world selection page correctly', () => {
    renderWithProvider();

    expect(screen.getByText('World Selection')).toBeInTheDocument();
    expect(screen.getByText(/Choose therapeutic environments/)).toBeInTheDocument();
  });

  it('displays available worlds', () => {
    renderWithProvider();

    expect(screen.getByText('Peaceful Garden')).toBeInTheDocument();
    expect(screen.getByText('Urban Challenge')).toBeInTheDocument();
    expect(screen.getByText('Family Dynamics')).toBeInTheDocument();
  });

  it('shows world count in header', () => {
    renderWithProvider();

    expect(screen.getByText('Browse Worlds (3 available)')).toBeInTheDocument();
  });

  it('displays compatibility scores when character is selected', () => {
    renderWithProvider();

    expect(screen.getByText('90% match')).toBeInTheDocument();
    expect(screen.getByText('60% match')).toBeInTheDocument();
    expect(screen.getByText('75% match')).toBeInTheDocument();
  });

  it('shows character selection notice when no character is selected', () => {
    const storeWithoutCharacter = configureStore({
      reducer: {
        world: worldReducer,
        character: characterReducer,
        player: playerReducer,
      },
      preloadedState: {
        ...mockStore.getState(),
        character: {
          characters: [],
          selectedCharacter: null,
          isLoading: false,
          error: null,
        },
      },
    });

    renderWithProvider(storeWithoutCharacter);

    expect(screen.getByText(/Please select a character first/)).toBeInTheDocument();
  });

  it('filters worlds by search term', () => {
    renderWithProvider();

    const searchInput = screen.getByPlaceholderText(/Search worlds/);
    fireEvent.change(searchInput, { target: { value: 'garden' } });

    expect(screen.getByText('Peaceful Garden')).toBeInTheDocument();
    expect(screen.queryByText('Urban Challenge')).not.toBeInTheDocument();
    expect(screen.queryByText('Family Dynamics')).not.toBeInTheDocument();
  });

  it('filters worlds by difficulty level', () => {
    renderWithProvider();

    const difficultySelect = screen.getByDisplayValue('All Levels');
    fireEvent.change(difficultySelect, { target: { value: 'BEGINNER' } });

    expect(screen.getByText('Peaceful Garden')).toBeInTheDocument();
    expect(screen.queryByText('Urban Challenge')).not.toBeInTheDocument();
    expect(screen.queryByText('Family Dynamics')).not.toBeInTheDocument();
  });

  it('filters worlds by therapeutic theme', () => {
    renderWithProvider();

    const themeSelect = screen.getByDisplayValue('All Themes');
    fireEvent.change(themeSelect, { target: { value: 'anxiety' } });

    expect(screen.getByText('Peaceful Garden')).toBeInTheDocument();
    expect(screen.queryByText('Family Dynamics')).not.toBeInTheDocument();
  });

  it('clears all filters when clear button is clicked', () => {
    renderWithProvider();

    // Apply some filters
    const searchInput = screen.getByPlaceholderText(/Search worlds/);
    fireEvent.change(searchInput, { target: { value: 'garden' } });

    const difficultySelect = screen.getByDisplayValue('All Levels');
    fireEvent.change(difficultySelect, { target: { value: 'BEGINNER' } });

    // Clear filters
    const clearButton = screen.getByText('Clear all filters');
    fireEvent.click(clearButton);

    // All worlds should be visible again
    expect(screen.getByText('Peaceful Garden')).toBeInTheDocument();
    expect(screen.getByText('Urban Challenge')).toBeInTheDocument();
    expect(screen.getByText('Family Dynamics')).toBeInTheDocument();

    // Search input should be cleared
    expect(searchInput).toHaveValue('');
  });

  it('opens world details modal when view details is clicked', () => {
    renderWithProvider();

    const viewDetailsButton = screen.getAllByText('View Details')[0];
    fireEvent.click(viewDetailsButton);

    expect(screen.getByTestId('world-details-modal')).toBeInTheDocument();
  });

  it('opens world customization modal when customize is clicked', () => {
    renderWithProvider();

    const customizeButton = screen.getAllByText('Customize')[0];
    fireEvent.click(customizeButton);

    expect(screen.getByTestId('world-customization-modal')).toBeInTheDocument();
  });

  it('disables customize and select buttons when no character is selected', () => {
    const storeWithoutCharacter = configureStore({
      reducer: {
        world: worldReducer,
        character: characterReducer,
        player: playerReducer,
      },
      preloadedState: {
        ...mockStore.getState(),
        character: {
          characters: [],
          selectedCharacter: null,
          isLoading: false,
          error: null,
        },
      },
    });

    renderWithProvider(storeWithoutCharacter);

    const customizeButtons = screen.getAllByText('Customize');
    const selectButtons = screen.getAllByText('Select World');

    customizeButtons.forEach(button => {
      expect(button).toBeDisabled();
    });

    selectButtons.forEach(button => {
      expect(button).toBeDisabled();
    });
  });

  it('shows loading state', () => {
    const loadingStore = configureStore({
      reducer: {
        world: worldReducer,
        character: characterReducer,
        player: playerReducer,
      },
      preloadedState: {
        ...mockStore.getState(),
        world: {
          ...mockStore.getState().world,
          isLoading: true,
        },
      },
    });

    renderWithProvider(loadingStore);

    expect(screen.getByText('Loading worlds...')).toBeInTheDocument();
  });

  it('shows empty state when no worlds are available', () => {
    const emptyStore = configureStore({
      reducer: {
        world: worldReducer,
        character: characterReducer,
        player: playerReducer,
      },
      preloadedState: {
        ...mockStore.getState(),
        world: {
          ...mockStore.getState().world,
          availableWorlds: [],
        },
      },
    });

    renderWithProvider(emptyStore);

    expect(screen.getByText('No worlds available')).toBeInTheDocument();
  });

  it('shows filtered empty state when no worlds match filters', () => {
    renderWithProvider();

    const searchInput = screen.getByPlaceholderText(/Search worlds/);
    fireEvent.change(searchInput, { target: { value: 'nonexistent' } });

    expect(screen.getByText('No worlds match your filters')).toBeInTheDocument();
    expect(screen.getByText(/Try adjusting your search criteria/)).toBeInTheDocument();
  });

  it('sorts worlds by compatibility score when character is selected', () => {
    renderWithProvider();

    const worldCards = screen.getAllByText(/% match/);
    const compatibilityScores = worldCards.map(card => 
      parseInt(card.textContent?.match(/(\d+)%/)?.[1] || '0')
    );

    // Should be sorted in descending order: 90%, 75%, 60%
    expect(compatibilityScores).toEqual([90, 75, 60]);
  });

  it('displays world themes with truncation', () => {
    renderWithProvider();

    expect(screen.getByText('anxiety')).toBeInTheDocument();
    expect(screen.getByText('mindfulness')).toBeInTheDocument();
    expect(screen.getByText('social anxiety')).toBeInTheDocument();
  });

  it('displays difficulty level badges with correct styling', () => {
    renderWithProvider();

    const beginnerBadge = screen.getByText('BEGINNER');
    const intermediateBadge = screen.getByText('INTERMEDIATE');
    const advancedBadge = screen.getByText('ADVANCED');

    expect(beginnerBadge).toHaveClass('bg-green-100', 'text-green-600');
    expect(intermediateBadge).toHaveClass('bg-yellow-100', 'text-yellow-600');
    expect(advancedBadge).toHaveClass('bg-red-100', 'text-red-600');
  });

  it('closes modals correctly', () => {
    renderWithProvider();

    // Open details modal
    const viewDetailsButton = screen.getAllByText('View Details')[0];
    fireEvent.click(viewDetailsButton);

    expect(screen.getByTestId('world-details-modal')).toBeInTheDocument();

    // Close modal
    const closeButton = screen.getByText('Close Modal');
    fireEvent.click(closeButton);

    expect(screen.queryByTestId('world-details-modal')).not.toBeInTheDocument();
  });

  it('handles customization modal confirmation', () => {
    renderWithProvider();

    // Open customization modal
    const customizeButton = screen.getAllByText('Customize')[0];
    fireEvent.click(customizeButton);

    expect(screen.getByTestId('world-customization-modal')).toBeInTheDocument();

    // Confirm customization
    const confirmButton = screen.getByText('Confirm');
    fireEvent.click(confirmButton);

    expect(screen.queryByTestId('world-customization-modal')).not.toBeInTheDocument();
  });
});