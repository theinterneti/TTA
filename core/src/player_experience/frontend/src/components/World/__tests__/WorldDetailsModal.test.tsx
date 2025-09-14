import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import WorldDetailsModal from '../WorldDetailsModal';
import worldReducer from '../../../store/slices/worldSlice';
import characterReducer from '../../../store/slices/characterSlice';

// Mock the API
jest.mock('../../../services/api', () => ({
  worldAPI: {
    checkCompatibility: jest.fn(),
  },
}));

const mockStore = configureStore({
  reducer: {
    world: worldReducer,
    character: characterReducer,
  },
  preloadedState: {
    world: {
      availableWorlds: [],
      selectedWorld: {
        world_id: 'world-1',
        name: 'Test World',
        description: 'A test world for therapeutic adventures',
        detailed_description: 'This is a detailed description of the test world with comprehensive therapeutic elements.',
        therapeutic_themes: ['anxiety', 'self-esteem'],
        therapeutic_approaches: ['CBT', 'Mindfulness'],
        difficulty_level: 'INTERMEDIATE' as const,
        estimated_duration: '3-4 hours',
        compatibility_score: 0.85,
        prerequisites: ['Basic therapeutic readiness'],
        customizable_parameters: {
          therapeutic_intensity: true,
          narrative_style: true,
          pacing: true,
          interaction_frequency: false,
        },
      },
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
  },
});

const defaultProps = {
  worldId: 'world-1',
  isOpen: true,
  onClose: jest.fn(),
  onCustomize: jest.fn(),
};

const renderWithProvider = (props = {}) => {
  return render(
    <Provider store={mockStore}>
      <WorldDetailsModal {...defaultProps} {...props} />
    </Provider>
  );
};

describe('WorldDetailsModal', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders world details correctly', () => {
    renderWithProvider();

    expect(screen.getByText('Test World')).toBeInTheDocument();
    expect(screen.getByText('INTERMEDIATE')).toBeInTheDocument();
    expect(screen.getByText('3-4 hours')).toBeInTheDocument();
    expect(screen.getByText('85% - Excellent Match')).toBeInTheDocument();
  });

  it('displays detailed description', () => {
    renderWithProvider();

    expect(screen.getByText(/This is a detailed description/)).toBeInTheDocument();
  });

  it('shows therapeutic themes', () => {
    renderWithProvider();

    expect(screen.getByText('anxiety')).toBeInTheDocument();
    expect(screen.getByText('self-esteem')).toBeInTheDocument();
  });

  it('displays therapeutic approaches', () => {
    renderWithProvider();

    expect(screen.getByText('CBT')).toBeInTheDocument();
    expect(screen.getByText('Mindfulness')).toBeInTheDocument();
  });

  it('shows prerequisites when available', () => {
    renderWithProvider();

    expect(screen.getByText('Prerequisites')).toBeInTheDocument();
    expect(screen.getByText('Basic therapeutic readiness')).toBeInTheDocument();
  });

  it('displays customization options', () => {
    renderWithProvider();

    expect(screen.getByText('Customization Options')).toBeInTheDocument();
    expect(screen.getByText('Therapeutic Intensity')).toBeInTheDocument();
    expect(screen.getByText('Narrative Style')).toBeInTheDocument();
    expect(screen.getByText('Pacing')).toBeInTheDocument();
    expect(screen.getByText('Interaction Frequency')).toBeInTheDocument();
  });

  it('shows compatibility analysis when character is selected', () => {
    renderWithProvider();

    expect(screen.getByText('Compatibility Analysis')).toBeInTheDocument();
    expect(screen.getByText('Overall Compatibility')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = jest.fn();
    renderWithProvider({ onClose });

    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onCustomize when customize button is clicked', () => {
    const onCustomize = jest.fn();
    renderWithProvider({ onCustomize });

    const customizeButton = screen.getByText('Customize Parameters');
    fireEvent.click(customizeButton);

    expect(onCustomize).toHaveBeenCalledTimes(1);
  });

  it('disables buttons when no character is selected', () => {
    const storeWithoutCharacter = configureStore({
      reducer: {
        world: worldReducer,
        character: characterReducer,
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

    render(
      <Provider store={storeWithoutCharacter}>
        <WorldDetailsModal {...defaultProps} />
      </Provider>
    );

    const customizeButton = screen.getByText('Customize Parameters');
    const selectButton = screen.getByText('Select This World');

    expect(customizeButton).toBeDisabled();
    expect(selectButton).toBeDisabled();
  });

  it('does not render when isOpen is false', () => {
    renderWithProvider({ isOpen: false });

    expect(screen.queryByText('Test World')).not.toBeInTheDocument();
  });

  it('does not render when selectedWorld is null', () => {
    const storeWithoutWorld = configureStore({
      reducer: {
        world: worldReducer,
        character: characterReducer,
      },
      preloadedState: {
        ...mockStore.getState(),
        world: {
          ...mockStore.getState().world,
          selectedWorld: null,
        },
      },
    });

    render(
      <Provider store={storeWithoutWorld}>
        <WorldDetailsModal {...defaultProps} />
      </Provider>
    );

    expect(screen.queryByText('Test World')).not.toBeInTheDocument();
  });

  it('displays correct compatibility color and text', () => {
    // Test excellent match (>= 0.8)
    renderWithProvider();
    expect(screen.getByText('Excellent Match')).toBeInTheDocument();

    // Test good match (>= 0.6)
    const storeWithGoodMatch = configureStore({
      reducer: {
        world: worldReducer,
        character: characterReducer,
      },
      preloadedState: {
        ...mockStore.getState(),
        world: {
          ...mockStore.getState().world,
          selectedWorld: {
            ...mockStore.getState().world.selectedWorld!,
            compatibility_score: 0.7,
          },
        },
      },
    });

    render(
      <Provider store={storeWithGoodMatch}>
        <WorldDetailsModal {...defaultProps} />
      </Provider>
    );

    expect(screen.getByText('Good Match')).toBeInTheDocument();
  });

  it('handles missing optional fields gracefully', () => {
    const storeWithMinimalWorld = configureStore({
      reducer: {
        world: worldReducer,
        character: characterReducer,
      },
      preloadedState: {
        ...mockStore.getState(),
        world: {
          ...mockStore.getState().world,
          selectedWorld: {
            world_id: 'world-1',
            name: 'Minimal World',
            description: 'A minimal world',
            therapeutic_themes: ['anxiety'],
            difficulty_level: 'BEGINNER' as const,
            estimated_duration: '1 hour',
            compatibility_score: 0.5,
            detailed_description: '',
            therapeutic_approaches: [],
            prerequisites: [],
            customizable_parameters: {
              therapeutic_intensity: false,
              narrative_style: false,
              pacing: false,
              interaction_frequency: false,
            },
          },
        },
      },
    });

    render(
      <Provider store={storeWithMinimalWorld}>
        <WorldDetailsModal {...defaultProps} />
      </Provider>
    );

    expect(screen.getByText('Minimal World')).toBeInTheDocument();
    expect(screen.queryByText('Prerequisites')).not.toBeInTheDocument();
  });
});
