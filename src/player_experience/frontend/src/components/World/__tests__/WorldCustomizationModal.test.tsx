import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import WorldCustomizationModal from '../WorldCustomizationModal';
import worldReducer from '../../../store/slices/worldSlice';
import characterReducer from '../../../store/slices/characterSlice';

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
        detailed_description: 'Detailed description',
        therapeutic_themes: ['anxiety', 'self-esteem'],
        therapeutic_approaches: ['CBT'],
        difficulty_level: 'INTERMEDIATE' as const,
        estimated_duration: '3-4 hours',
        compatibility_score: 0.85,
        prerequisites: [],
        customizable_parameters: {
          therapeutic_intensity: true,
          narrative_style: true,
          pacing: true,
          interaction_frequency: true,
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
          preferred_intensity: 'HIGH' as const,
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
  onConfirm: jest.fn(),
};

const renderWithProvider = (props = {}) => {
  return render(
    <Provider store={mockStore}>
      <WorldCustomizationModal {...defaultProps} {...props} />
    </Provider>
  );
};

describe('WorldCustomizationModal', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders customization modal correctly', () => {
    renderWithProvider();

    expect(screen.getByText('Customize World Parameters')).toBeInTheDocument();
    expect(screen.getByText('Test World')).toBeInTheDocument();
  });

  it('displays character context when character is selected', () => {
    renderWithProvider();

    expect(screen.getByText('Customizing for Test Character')).toBeInTheDocument();
  });

  it('shows all parameter categories', () => {
    renderWithProvider();

    expect(screen.getByText('Therapeutic Intensity')).toBeInTheDocument();
    expect(screen.getByText('Narrative Style')).toBeInTheDocument();
    expect(screen.getByText('Pacing')).toBeInTheDocument();
    expect(screen.getByText('Interaction Frequency')).toBeInTheDocument();
  });

  it('displays therapeutic intensity options', () => {
    renderWithProvider();

    expect(screen.getByText('LOW')).toBeInTheDocument();
    expect(screen.getByText('MEDIUM')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
  });

  it('displays narrative style options', () => {
    renderWithProvider();

    expect(screen.getByText('GUIDED')).toBeInTheDocument();
    expect(screen.getByText('EXPLORATORY')).toBeInTheDocument();
    expect(screen.getByText('STRUCTURED')).toBeInTheDocument();
  });

  it('displays pacing options', () => {
    renderWithProvider();

    expect(screen.getByText('SLOW')).toBeInTheDocument();
    expect(screen.getByText('MODERATE')).toBeInTheDocument();
    expect(screen.getByText('FAST')).toBeInTheDocument();
  });

  it('displays interaction frequency options', () => {
    renderWithProvider();

    expect(screen.getByText('MINIMAL')).toBeInTheDocument();
    expect(screen.getByText('REGULAR')).toBeInTheDocument();
    expect(screen.getByText('FREQUENT')).toBeInTheDocument();
  });

  it('shows recommended values based on character profile', () => {
    renderWithProvider();

    expect(screen.getByText('Recommended: HIGH')).toBeInTheDocument();
  });

  it('allows parameter selection', () => {
    renderWithProvider();

    const highIntensityButton = screen.getByRole('button', { name: /HIGH.*Intensive therapeutic focus/ });
    fireEvent.click(highIntensityButton);

    expect(highIntensityButton).toHaveClass('border-primary-500');
  });

  it('calls onConfirm with selected parameters', () => {
    const onConfirm = jest.fn();
    renderWithProvider({ onConfirm });

    // Select some parameters
    const highIntensityButton = screen.getByRole('button', { name: /HIGH.*Intensive therapeutic focus/ });
    fireEvent.click(highIntensityButton);

    const exploratoryStyleButton = screen.getByRole('button', { name: /EXPLORATORY.*Open-ended exploration/ });
    fireEvent.click(exploratoryStyleButton);

    const confirmButton = screen.getByText('Confirm & Select World');
    fireEvent.click(confirmButton);

    expect(onConfirm).toHaveBeenCalledWith({
      therapeutic_intensity: 'HIGH',
      narrative_style: 'EXPLORATORY',
      pacing: 'MODERATE',
      interaction_frequency: 'REGULAR',
    });
  });

  it('calls onClose when cancel button is clicked', () => {
    const onClose = jest.fn();
    renderWithProvider({ onClose });

    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('resets to recommended values when reset button is clicked', () => {
    renderWithProvider();

    // First change a parameter
    const lowIntensityButton = screen.getByRole('button', { name: /LOW.*Gentle therapeutic guidance/ });
    fireEvent.click(lowIntensityButton);

    // Then reset
    const resetButton = screen.getByText('Reset to Recommended');
    fireEvent.click(resetButton);

    // Should be back to HIGH (recommended for this character)
    const highIntensityButton = screen.getByRole('button', { name: /HIGH.*Intensive therapeutic focus/ });
    expect(highIntensityButton).toHaveClass('border-primary-500');
  });

  it('shows and hides preview correctly', () => {
    renderWithProvider();

    const showPreviewButton = screen.getByText('Show Preview');
    fireEvent.click(showPreviewButton);

    expect(screen.getByText(/This world will be customized with/)).toBeInTheDocument();

    const hidePreviewButton = screen.getByText('Hide Preview');
    fireEvent.click(hidePreviewButton);

    expect(screen.queryByText(/This world will be customized with/)).not.toBeInTheDocument();
  });

  it('disables non-customizable parameters', () => {
    const storeWithLimitedCustomization = configureStore({
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
            customizable_parameters: {
              therapeutic_intensity: true,
              narrative_style: false,
              pacing: false,
              interaction_frequency: true,
            },
          },
        },
      },
    });

    render(
      <Provider store={storeWithLimitedCustomization}>
        <WorldCustomizationModal {...defaultProps} />
      </Provider>
    );

    // Therapeutic intensity should be enabled
    const highIntensityButton = screen.getByRole('button', { name: /HIGH.*Intensive therapeutic focus/ });
    expect(highIntensityButton).not.toBeDisabled();

    // Narrative style should be disabled
    const guidedStyleButton = screen.getByRole('button', { name: /GUIDED.*Clear direction/ });
    expect(guidedStyleButton).toBeDisabled();
  });

  it('does not render when isOpen is false', () => {
    renderWithProvider({ isOpen: false });

    expect(screen.queryByText('Customize World Parameters')).not.toBeInTheDocument();
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
        <WorldCustomizationModal {...defaultProps} />
      </Provider>
    );

    expect(screen.queryByText('Customize World Parameters')).not.toBeInTheDocument();
  });

  it('sets default parameters based on character preferences', async () => {
    renderWithProvider();

    // The HIGH intensity button should be selected by default based on character preference
    await waitFor(() => {
      const highIntensityButton = screen.getByRole('button', { name: /HIGH.*Intensive therapeutic focus/ });
      expect(highIntensityButton).toHaveClass('border-primary-500');
    });
  });

  it('generates correct preview text', () => {
    renderWithProvider();

    const showPreviewButton = screen.getByText('Show Preview');
    fireEvent.click(showPreviewButton);

    expect(screen.getByText(/medium therapeutic intensity.*guided narrative approach.*moderate pace.*regular therapeutic interactions/)).toBeInTheDocument();
  });

  it('handles character without therapeutic profile', () => {
    const storeWithoutProfile = configureStore({
      reducer: {
        world: worldReducer,
        character: characterReducer,
      },
      preloadedState: {
        ...mockStore.getState(),
        character: {
          characters: [],
          selectedCharacter: {
            character_id: 'char-1',
            name: 'Test Character',
            therapeutic_profile: null,
          },
          isLoading: false,
          error: null,
        },
      },
    });

    render(
      <Provider store={storeWithoutProfile}>
        <WorldCustomizationModal {...defaultProps} />
      </Provider>
    );

    expect(screen.getByText('Customize World Parameters')).toBeInTheDocument();
    // Should still render without crashing
  });
});
