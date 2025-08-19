import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import CharacterCard from '../CharacterCard';
import characterReducer from '../../../store/slices/characterSlice';

const mockCharacter = {
  character_id: '1',
  player_id: 'player1',
  name: 'Test Character',
  appearance: {
    description: 'A brave adventurer with kind eyes',
  },
  background: {
    story: 'Born in a small village...',
    personality_traits: ['Brave', 'Kind', 'Curious'],
    goals: ['Find inner peace', 'Help others'],
  },
  therapeutic_profile: {
    comfort_level: 7,
    preferred_intensity: 'MEDIUM' as const,
    therapeutic_goals: ['Anxiety management', 'Self-confidence'],
  },
  created_at: '2024-01-01T00:00:00Z',
  last_active: '2024-01-02T00:00:00Z',
  active_worlds: ['world1', 'world2'],
};

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

describe('CharacterCard', () => {
  const mockOnEdit = jest.fn();

  beforeEach(() => {
    mockOnEdit.mockClear();
  });

  test('renders character information correctly', () => {
    renderWithProvider(
      <CharacterCard
        character={mockCharacter}
        isSelected={false}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.getByText('Test Character')).toBeInTheDocument();
    expect(screen.getByText('A brave adventurer with kind eyes')).toBeInTheDocument();
    expect(screen.getByText('7/10')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // Active worlds count
    expect(screen.getByText('MEDIUM Intensity')).toBeInTheDocument();
  });

  test('displays personality traits', () => {
    renderWithProvider(
      <CharacterCard
        character={mockCharacter}
        isSelected={false}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.getByText('Brave')).toBeInTheDocument();
    expect(screen.getByText('Kind')).toBeInTheDocument();
    expect(screen.getByText('Curious')).toBeInTheDocument();
  });

  test('displays therapeutic goals', () => {
    renderWithProvider(
      <CharacterCard
        character={mockCharacter}
        isSelected={false}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.getByText('Anxiety management')).toBeInTheDocument();
    expect(screen.getByText('Self-confidence')).toBeInTheDocument();
  });

  test('shows selected state correctly', () => {
    renderWithProvider(
      <CharacterCard
        character={mockCharacter}
        isSelected={true}
        onEdit={mockOnEdit}
      />
    );

    const card = screen.getByRole('button');
    expect(card).toHaveClass('ring-2', 'ring-primary-500', 'bg-primary-50');
  });

  test('calls onEdit when edit button is clicked', () => {
    renderWithProvider(
      <CharacterCard
        character={mockCharacter}
        isSelected={false}
        onEdit={mockOnEdit}
      />
    );

    const editButton = screen.getByText('Edit Details');
    fireEvent.click(editButton);

    expect(mockOnEdit).toHaveBeenCalledWith(mockCharacter);
  });

  test('shows delete confirmation when delete is clicked', () => {
    renderWithProvider(
      <CharacterCard
        character={mockCharacter}
        isSelected={false}
        onEdit={mockOnEdit}
      />
    );

    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);

    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Confirm')).toBeInTheDocument();
  });

  test('displays correct intensity color', () => {
    const highIntensityCharacter = {
      ...mockCharacter,
      therapeutic_profile: {
        ...mockCharacter.therapeutic_profile,
        preferred_intensity: 'HIGH' as const,
      },
    };

    renderWithProvider(
      <CharacterCard
        character={highIntensityCharacter}
        isSelected={false}
        onEdit={mockOnEdit}
      />
    );

    const intensityBadge = screen.getByText('HIGH Intensity');
    expect(intensityBadge).toHaveClass('bg-red-100', 'text-red-600');
  });

  test('truncates long trait lists', () => {
    const characterWithManyTraits = {
      ...mockCharacter,
      background: {
        ...mockCharacter.background,
        personality_traits: ['Trait1', 'Trait2', 'Trait3', 'Trait4', 'Trait5'],
      },
    };

    renderWithProvider(
      <CharacterCard
        character={characterWithManyTraits}
        isSelected={false}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.getByText('+2 more')).toBeInTheDocument();
  });

  test('formats dates correctly', () => {
    renderWithProvider(
      <CharacterCard
        character={mockCharacter}
        isSelected={false}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.getByText('Created Jan 1, 2024')).toBeInTheDocument();
  });
});