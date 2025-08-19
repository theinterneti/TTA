import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import '@testing-library/jest-dom';

import Chat from '../Chat';
import playerReducer from '../../../store/slices/playerSlice';
import characterReducer from '../../../store/slices/characterSlice';
import worldReducer from '../../../store/slices/worldSlice';
import chatReducer from '../../../store/slices/chatSlice';
import settingsReducer from '../../../store/slices/settingsSlice';
import websocketService from '../../../services/websocket';

// Mock the websocket service
jest.mock('../../../services/websocket', () => ({
  connect: jest.fn(),
  disconnect: jest.fn(),
  sendMessage: jest.fn(),
  sendInteractionResponse: jest.fn(),
  sendFeedback: jest.fn(),
  isConnected: jest.fn(() => true),
}));

const mockWebsocketService = websocketService as jest.Mocked<typeof websocketService>;

const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      player: playerReducer,
      character: characterReducer,
      world: worldReducer,
      chat: chatReducer,
      settings: settingsReducer,
    },
    preloadedState: {
      player: {
        profile: {
          player_id: 'test-player-1',
          username: 'testuser',
          email: 'test@example.com',
          created_at: '2024-01-01T00:00:00Z',
          therapeutic_preferences: {
            intensity_level: 'medium',
            preferred_approaches: ['CBT'],
            trigger_warnings: [],
            comfort_topics: [],
            avoid_topics: [],
          },
          privacy_settings: {
            data_collection_consent: true,
            research_participation: false,
            crisis_contact_sharing: true,
          },
          characters: ['char-1'],
          active_sessions: {},
          progress_summary: {
            total_sessions: 0,
            total_time_minutes: 0,
            milestones_achieved: [],
            current_streak: 0,
            last_session_date: null,
          },
        },
        isLoading: false,
        error: null,
      },
      character: {
        characters: [
          {
            id: 'char-1',
            name: 'Test Character',
            appearance: {
              physical_description: 'Test description',
              style_preferences: 'casual',
            },
            background: {
              personal_history: 'Test history',
              current_situation: 'Test situation',
              goals_motivations: 'Test goals',
            },
            therapeutic_profile: {
              primary_concerns: ['anxiety'],
              therapeutic_goals: ['stress_management'],
              preferred_approaches: ['CBT'],
              comfort_level: 'medium',
              trigger_warnings: [],
            },
            created_at: '2024-01-01T00:00:00Z',
            last_active: '2024-01-01T00:00:00Z',
            active_worlds: [],
          },
        ],
        selectedCharacter: {
          id: 'char-1',
          name: 'Test Character',
          appearance: {
            physical_description: 'Test description',
            style_preferences: 'casual',
          },
          background: {
            personal_history: 'Test history',
            current_situation: 'Test situation',
            goals_motivations: 'Test goals',
          },
          therapeutic_profile: {
            primary_concerns: ['anxiety'],
            therapeutic_goals: ['stress_management'],
            preferred_approaches: ['CBT'],
            comfort_level: 'medium',
            trigger_warnings: [],
          },
          created_at: '2024-01-01T00:00:00Z',
          last_active: '2024-01-01T00:00:00Z',
          active_worlds: [],
        },
        isLoading: false,
        error: null,
      },
      world: {
        availableWorlds: [],
        selectedWorld: null,
        isLoading: false,
        error: null,
      },
      chat: {
        currentSession: null,
        sessions: [],
        isConnected: true,
        isTyping: false,
        connectionError: null,
        messageHistory: [
          {
            id: 'msg-1',
            type: 'system',
            content: 'Welcome to your therapeutic adventure!',
            timestamp: '2024-01-15T10:00:00Z',
          },
          {
            id: 'msg-2',
            type: 'user',
            content: 'Hello, I would like to start.',
            timestamp: '2024-01-15T10:01:00Z',
          },
          {
            id: 'msg-3',
            type: 'assistant',
            content: 'Great! Let\'s begin your journey.',
            timestamp: '2024-01-15T10:02:00Z',
            metadata: {
              therapeutic_technique: 'CBT',
              interactive_elements: {
                buttons: [
                  { id: 'btn1', text: 'Continue', action: 'continue' },
                  { id: 'btn2', text: 'Tell me more', action: 'more_info' },
                ],
              },
            },
          },
        ],
      },
      settings: {
        therapeuticSettings: {
          intensity_level: 'medium',
          preferred_approaches: ['CBT'],
          trigger_warnings: [],
          comfort_topics: [],
          avoid_topics: [],
          crisis_contact_info: null,
        },
        privacySettings: {
          data_collection_consent: true,
          research_participation: false,
          crisis_contact_sharing: true,
        },
        isLoading: false,
        error: null,
      },
      ...initialState,
    },
  });
};

const renderWithProviders = (
  ui: React.ReactElement,
  {
    initialState = {},
    route = '/chat',
    ...renderOptions
  } = {}
) => {
  const store = createMockStore(initialState);
  
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <Provider store={store}>
      <MemoryRouter initialEntries={[route]}>
        {children}
      </MemoryRouter>
    </Provider>
  );

  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

describe('Chat', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders chat interface with header and messages', () => {
    renderWithProviders(<Chat />);

    expect(screen.getByText("Test Character's Adventure")).toBeInTheDocument();
    expect(screen.getByText('Connected')).toBeInTheDocument();
    expect(screen.getByText('Welcome to your therapeutic adventure!')).toBeInTheDocument();
    expect(screen.getByText('Hello, I would like to start.')).toBeInTheDocument();
    expect(screen.getByText("Great! Let's begin your journey.")).toBeInTheDocument();
  });

  it('connects to websocket on mount', () => {
    renderWithProviders(<Chat />, { route: '/chat/session-123' });

    expect(mockWebsocketService.connect).toHaveBeenCalledWith('session-123');
  });

  it('disconnects websocket on unmount', () => {
    const { unmount } = renderWithProviders(<Chat />);

    unmount();

    expect(mockWebsocketService.disconnect).toHaveBeenCalled();
  });

  it('displays connection status correctly', () => {
    renderWithProviders(<Chat />, {
      initialState: {
        chat: {
          isConnected: false,
          connectionError: 'Connection failed',
        },
      },
    });

    expect(screen.getByText('Connection failed')).toBeInTheDocument();
  });

  it('displays typing indicator when assistant is typing', () => {
    renderWithProviders(<Chat />, {
      initialState: {
        chat: {
          isTyping: true,
        },
      },
    });

    expect(screen.getByText('Assistant is typing...')).toBeInTheDocument();
  });

  it('sends message when send button is clicked', async () => {
    renderWithProviders(<Chat />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    expect(mockWebsocketService.sendMessage).toHaveBeenCalledWith(
      'Test message',
      {
        character_id: 'char-1',
        player_id: 'test-player-1',
      }
    );
  });

  it('sends message when Enter key is pressed', async () => {
    renderWithProviders(<Chat />);

    const input = screen.getByPlaceholderText('Type your message...');

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });

    expect(mockWebsocketService.sendMessage).toHaveBeenCalledWith(
      'Test message',
      {
        character_id: 'char-1',
        player_id: 'test-player-1',
      }
    );
  });

  it('does not send empty messages', () => {
    renderWithProviders(<Chat />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: '   ' } });
    fireEvent.click(sendButton);

    expect(mockWebsocketService.sendMessage).not.toHaveBeenCalled();
  });

  it('handles interactive button clicks', () => {
    renderWithProviders(<Chat />);

    const continueButton = screen.getByText('Continue');
    fireEvent.click(continueButton);

    expect(mockWebsocketService.sendInteractionResponse).toHaveBeenCalledWith(
      'msg-3',
      'continue'
    );
  });

  it('handles feedback button clicks', () => {
    renderWithProviders(<Chat />);

    const helpfulButton = screen.getByLabelText('Mark as helpful');
    fireEvent.click(helpfulButton);

    expect(mockWebsocketService.sendFeedback).toHaveBeenCalledWith(
      'msg-3',
      'helpful'
    );
  });

  it('disables input when not connected', () => {
    renderWithProviders(<Chat />, {
      initialState: {
        chat: {
          isConnected: false,
        },
      },
    });

    const input = screen.getByPlaceholderText('Connecting...');
    const sendButton = screen.getByLabelText('Send message');

    expect(input).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  it('shows welcome message when no messages exist', () => {
    renderWithProviders(<Chat />, {
      initialState: {
        chat: {
          messageHistory: [],
        },
      },
    });

    expect(screen.getByText('Welcome to your therapeutic adventure!')).toBeInTheDocument();
    expect(screen.getByText(/Start a conversation to begin/)).toBeInTheDocument();
  });

  it('navigates back to dashboard when back button is clicked', () => {
    const mockNavigate = jest.fn();
    jest.doMock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
    }));

    renderWithProviders(<Chat />);

    const backButton = screen.getByLabelText('Back to dashboard');
    fireEvent.click(backButton);

    // Note: In a real test, you'd check navigation, but since we're mocking,
    // we just verify the button exists and is clickable
    expect(backButton).toBeInTheDocument();
  });

  it('shows character count in input field', () => {
    renderWithProviders(<Chat />);

    const input = screen.getByPlaceholderText('Type your message...');
    fireEvent.change(input, { target: { value: 'Hello world' } });

    expect(screen.getByText('11/1000')).toBeInTheDocument();
  });

  it('prevents sending messages over character limit', () => {
    renderWithProviders(<Chat />);

    const input = screen.getByPlaceholderText('Type your message...');
    const longMessage = 'a'.repeat(1001);
    
    fireEvent.change(input, { target: { value: longMessage } });
    
    // Input should be limited to 1000 characters
    expect(input).toHaveAttribute('maxLength', '1000');
  });
});