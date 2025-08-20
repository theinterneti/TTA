import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import CharacterCreationForm from '../CharacterCreationForm';
import characterReducer from '../../../store/slices/characterSlice';
import playerReducer from '../../../store/slices/playerSlice';

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

// Mock the API calls
jest.mock('../../../store/slices/characterSlice', () => ({
  ...jest.requireActual('../../../store/slices/characterSlice'),
  createCharacter: jest.fn(() => ({
    type: 'character/createCharacter/fulfilled',
    payload: {
      character_id: '1',
      name: 'Test Character',
    },
  })),
}));

describe('CharacterCreationForm', () => {
  const mockOnClose = jest.fn();
  const mockOnSuccess = jest.fn();

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
        characters: [],
        active_sessions: {},
      },
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
  };

  beforeEach(() => {
    mockOnClose.mockClear();
    mockOnSuccess.mockClear();
  });

  test('renders character creation form', () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    expect(screen.getByText('Create New Character')).toBeInTheDocument();
    expect(screen.getByText('Basic Info')).toBeInTheDocument();
    expect(screen.getByText('Background')).toBeInTheDocument();
    expect(screen.getByText('Therapeutic')).toBeInTheDocument();
  });

  test('shows step 1 form initially', () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    expect(screen.getByText('Basic Information')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter your character\'s name')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Describe your character's appearance/)).toBeInTheDocument();
  });

  test('validates required fields in step 1', async () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText('Character name is required')).toBeInTheDocument();
      expect(screen.getByText('Character appearance description is required')).toBeInTheDocument();
    });
  });

  test('progresses to step 2 when step 1 is valid', async () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    // Fill in step 1
    const nameInput = screen.getByPlaceholderText('Enter your character\'s name');
    const descriptionInput = screen.getByPlaceholderText(/Describe your character's appearance/);
    
    fireEvent.change(nameInput, { target: { value: 'Test Character' } });
    fireEvent.change(descriptionInput, { target: { value: 'A brave adventurer' } });

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText('Background & Personality')).toBeInTheDocument();
    });
  });

  test('allows adding personality traits', async () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    // Navigate to step 2
    const nameInput = screen.getByPlaceholderText('Enter your character\'s name');
    const descriptionInput = screen.getByPlaceholderText(/Describe your character's appearance/);
    
    fireEvent.change(nameInput, { target: { value: 'Test Character' } });
    fireEvent.change(descriptionInput, { target: { value: 'A brave adventurer' } });

    fireEvent.click(screen.getByText('Next'));

    await waitFor(() => {
      expect(screen.getByText('Background & Personality')).toBeInTheDocument();
    });

    // Add a personality trait
    const traitInput = screen.getByPlaceholderText('Add a personality trait');
    fireEvent.change(traitInput, { target: { value: 'Brave' } });
    fireEvent.click(screen.getAllByText('Add')[0]);

    expect(screen.getByText('Brave')).toBeInTheDocument();
  });

  test('allows removing personality traits', async () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    // Navigate to step 2 and add a trait
    const nameInput = screen.getByPlaceholderText('Enter your character\'s name');
    const descriptionInput = screen.getByPlaceholderText(/Describe your character's appearance/);
    
    fireEvent.change(nameInput, { target: { value: 'Test Character' } });
    fireEvent.change(descriptionInput, { target: { value: 'A brave adventurer' } });
    fireEvent.click(screen.getByText('Next'));

    await waitFor(() => {
      const traitInput = screen.getByPlaceholderText('Add a personality trait');
      fireEvent.change(traitInput, { target: { value: 'Brave' } });
      fireEvent.click(screen.getAllByText('Add')[0]);
    });

    // Remove the trait
    const removeButton = screen.getByText('×');
    fireEvent.click(removeButton);

    expect(screen.queryByText('Brave')).not.toBeInTheDocument();
  });

  test('shows character preview', () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    const nameInput = screen.getByPlaceholderText('Enter your character\'s name');
    fireEvent.change(nameInput, { target: { value: 'Test Character' } });

    expect(screen.getByText('Preview')).toBeInTheDocument();
    expect(screen.getByText('Test Character')).toBeInTheDocument();
  });

  test('calls onClose when cancel is clicked', () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  test('calls onClose when X button is clicked', () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    const closeButton = screen.getByRole('button', { name: '' }); // X button has no text
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  test('validates character name length', async () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    const nameInput = screen.getByPlaceholderText('Enter your character\'s name');
    fireEvent.change(nameInput, { target: { value: 'A'.repeat(51) } }); // 51 characters

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText('Character name must be 50 characters or less')).toBeInTheDocument();
    });
  });

  test('shows character count', () => {
    renderWithProvider(
      <CharacterCreationForm onClose={mockOnClose} onSuccess={mockOnSuccess} />,
      { initialState: mockInitialState }
    );

    const nameInput = screen.getByPlaceholderText('Enter your character\'s name');
    fireEvent.change(nameInput, { target: { value: 'Test' } });

    expect(screen.getByText('4/50 characters')).toBeInTheDocument();
  });
});