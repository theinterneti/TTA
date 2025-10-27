import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import CharacterSelector from '../CharacterSelector';
import characterReducer from '../../../store/slices/characterSlice';

const mockCharacters = [
  {
    character_id: '1',
    player_id: 'player1',
    name: 'Character One',
    appearance: { description: 'First character' },
    background: {
      story: 'Story one',
      personality_traits: ['Brave'],
      goals: ['Goal one'],
    },
    therapeutic_profile: {
      comfort_level: 5,
      preferred_intensity: 'LOW' as const,
      therapeutic_goals: ['Goal one'],
    },
    created_at: '2024-01-01T00:00:00Z',
    last_active: '2024-01-01T00:00:00Z',
    active_worlds: ['world1'],
  },
  {
    character_id: '2',
    player_id: 'player1',
    name: 'Character Two',
    appearance: { description: 'Second character' },
    background: {
      story: 'Story two',
      personality_traits: ['Kind'],
      goals: ['Goal two'],
    },
    therapeutic_profile: {
      comfort_level: 8,
      preferred_intensity: 'HIGH' as const,
      therapeutic_goals: ['Goal two'],
    },
    created_at: '2024-01-02T00:00:00Z',
    last_active: '2024-01-02T00:00:00Z',
    active_worlds: [],
  },
];

const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      character: characterReducer,
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

describe('CharacterSelector', () => {
  const mockOnSelect = jest.fn();
  const mockOnCreateNew = jest.fn();

  beforeEach(() => {
    mockOnSelect.mockClear();
    mockOnCreateNew.mockClear();
  });

  describe('Compact Mode', () => {
    test('renders compact selector with no character selected', () => {
      const initialState = {
        character: {
          characters: mockCharacters,
          selectedCharacter: null,
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={true}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      expect(screen.getByText('Select Character')).toBeInTheDocument();
    });

    test('renders compact selector with selected character', () => {
      const initialState = {
        character: {
          characters: mockCharacters,
          selectedCharacter: mockCharacters[0],
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={true}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      expect(screen.getByText('Character One')).toBeInTheDocument();
    });

    test('opens dropdown when clicked', () => {
      const initialState = {
        character: {
          characters: mockCharacters,
          selectedCharacter: null,
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={true}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(screen.getByText('Character One')).toBeInTheDocument();
      expect(screen.getByText('Character Two')).toBeInTheDocument();
    });

    test('calls onSelect when character is selected from dropdown', () => {
      const initialState = {
        character: {
          characters: mockCharacters,
          selectedCharacter: null,
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={true}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      const characterButton = screen.getByText('Character One');
      fireEvent.click(characterButton);

      expect(mockOnSelect).toHaveBeenCalledWith(mockCharacters[0]);
    });

    test('shows create new button in dropdown', () => {
      const initialState = {
        character: {
          characters: mockCharacters,
          selectedCharacter: null,
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={true}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(screen.getByText('Create New Character')).toBeInTheDocument();
    });
  });

  describe('Full Mode', () => {
    test('renders full character selection interface', () => {
      const initialState = {
        character: {
          characters: mockCharacters,
          selectedCharacter: null,
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={false}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      expect(screen.getByText('Select Character')).toBeInTheDocument();
      expect(screen.getByText('Character One')).toBeInTheDocument();
      expect(screen.getByText('Character Two')).toBeInTheDocument();
    });

    test('shows empty state when no characters exist', () => {
      const initialState = {
        character: {
          characters: [],
          selectedCharacter: null,
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={false}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      expect(screen.getByText('No characters yet')).toBeInTheDocument();
      expect(screen.getByText('Create your first character to begin your therapeutic journey')).toBeInTheDocument();
    });

    test('calls onSelect when character is clicked', () => {
      const initialState = {
        character: {
          characters: mockCharacters,
          selectedCharacter: null,
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={false}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      const characterButton = screen.getByText('Character One').closest('button');
      fireEvent.click(characterButton!);

      expect(mockOnSelect).toHaveBeenCalledWith(mockCharacters[0]);
    });

    test('shows selected character with visual indicator', () => {
      const initialState = {
        character: {
          characters: mockCharacters,
          selectedCharacter: mockCharacters[0],
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={false}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      const selectedCharacterButton = screen.getByText('Character One').closest('button');
      expect(selectedCharacterButton).toHaveClass('border-primary-500', 'bg-primary-50');
    });

    test('displays character details correctly', () => {
      const initialState = {
        character: {
          characters: mockCharacters,
          selectedCharacter: null,
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={false}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      expect(screen.getByText('LOW intensity')).toBeInTheDocument();
      expect(screen.getByText('HIGH intensity')).toBeInTheDocument();
      expect(screen.getByText('Comfort: 5/10')).toBeInTheDocument();
      expect(screen.getByText('Comfort: 8/10')).toBeInTheDocument();
    });

    test('hides create button when showCreateButton is false', () => {
      const initialState = {
        character: {
          characters: mockCharacters,
          selectedCharacter: null,
          isLoading: false,
          error: null,
          creationInProgress: false,
        },
      };

      renderWithProvider(
        <CharacterSelector
          compact={false}
          showCreateButton={false}
          onSelect={mockOnSelect}
          onCreateNew={mockOnCreateNew}
        />,
        { initialState }
      );

      expect(screen.queryByText('Create New')).not.toBeInTheDocument();
    });
  });

  test('shows loading state', () => {
    const initialState = {
      character: {
        characters: [],
        selectedCharacter: null,
        isLoading: true,
        error: null,
        creationInProgress: false,
      },
    };

    renderWithProvider(
      <CharacterSelector
        compact={false}
        onSelect={mockOnSelect}
        onCreateNew={mockOnCreateNew}
      />,
      { initialState }
    );

    expect(screen.getByText('Loading characters...')).toBeInTheDocument();
  });
});
