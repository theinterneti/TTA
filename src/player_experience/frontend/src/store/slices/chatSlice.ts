import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { conversationAPI } from '../../services/api';
import { getErrorMessage } from '../../utils/errorHandling';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    therapeutic_technique?: string;
    safety_level?: 'safe' | 'caution' | 'crisis';
    interactive_elements?: {
      buttons?: Array<{
        id: string;
        text: string;
        action: string;
      }>;
      guided_exercise?: {
        type: string;
        instructions: string;
        steps: string[];
      };
    };
  };
}

interface ChatSession {
  session_id: string;
  character_id: string;
  world_id: string;
  messages: ChatMessage[];
  is_active: boolean;
  created_at: string;
  last_activity: string;
}

interface ChatState {
  currentSession: ChatSession | null;
  sessions: ChatSession[];
  isConnected: boolean;
  isTyping: boolean;
  connectionError: string | null;
  messageHistory: ChatMessage[];
  isLoadingHistory: boolean;
  historyError: string | null;
}

const initialState: ChatState = {
  currentSession: null,
  sessions: [],
  isConnected: false,
  isTyping: false,
  connectionError: null,
  messageHistory: [],
  isLoadingHistory: false,
  historyError: null,
};

// Async thunks
export const loadConversationHistory = createAsyncThunk(
  'chat/loadHistory',
  async ({ sessionId, limit = 50 }: { sessionId: string; limit?: number }) => {
    const response = await conversationAPI.getHistory(sessionId, limit);
    return response;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setCurrentSession: (state, action: PayloadAction<ChatSession>) => {
      state.currentSession = action.payload;
      state.messageHistory = action.payload.messages;
    },
    clearCurrentSession: (state) => {
      state.currentSession = null;
      state.messageHistory = [];
    },
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messageHistory.push(action.payload);
      if (state.currentSession) {
        state.currentSession.messages.push(action.payload);
        state.currentSession.last_activity = new Date().toISOString();
      }
    },
    updateMessage: (state, action: PayloadAction<{ id: string; updates: Partial<ChatMessage> }>) => {
      const { id, updates } = action.payload;
      const messageIndex = state.messageHistory.findIndex(msg => msg.id === id);
      if (messageIndex !== -1) {
        state.messageHistory[messageIndex] = { ...state.messageHistory[messageIndex], ...updates };
      }
      if (state.currentSession) {
        const sessionMessageIndex = state.currentSession.messages.findIndex(msg => msg.id === id);
        if (sessionMessageIndex !== -1) {
          state.currentSession.messages[sessionMessageIndex] = {
            ...state.currentSession.messages[sessionMessageIndex],
            ...updates
          };
        }
      }
    },
    setConnectionStatus: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
      if (action.payload) {
        state.connectionError = null;
      }
    },
    setConnectionError: (state, action: PayloadAction<string>) => {
      state.connectionError = action.payload;
      state.isConnected = false;
    },
    setTypingStatus: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload;
    },
    addSession: (state, action: PayloadAction<ChatSession>) => {
      const existingIndex = state.sessions.findIndex(s => s.session_id === action.payload.session_id);
      if (existingIndex !== -1) {
        state.sessions[existingIndex] = action.payload;
      } else {
        state.sessions.push(action.payload);
      }
    },
    updateSession: (state, action: PayloadAction<{ sessionId: string; updates: Partial<ChatSession> }>) => {
      const { sessionId, updates } = action.payload;
      const sessionIndex = state.sessions.findIndex(s => s.session_id === sessionId);
      if (sessionIndex !== -1) {
        state.sessions[sessionIndex] = { ...state.sessions[sessionIndex], ...updates };
      }
      if (state.currentSession?.session_id === sessionId) {
        state.currentSession = { ...state.currentSession, ...updates };
      }
    },
    clearMessages: (state) => {
      state.messageHistory = [];
      if (state.currentSession) {
        state.currentSession.messages = [];
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadConversationHistory.pending, (state) => {
        state.isLoadingHistory = true;
        state.historyError = null;
      })
      .addCase(loadConversationHistory.fulfilled, (state, action) => {
        state.isLoadingHistory = false;

        // Transform API response to chat messages
        const messages = action.payload.messages.map((msg: any) => ({
          id: msg.timestamp, // Use timestamp as ID if no ID provided
          type: msg.role as 'user' | 'assistant' | 'system',
          content: msg.content,
          timestamp: msg.timestamp,
          metadata: msg.metadata,
        }));

        state.messageHistory = messages;

        // Update current session if it matches
        if (state.currentSession && state.currentSession.session_id === action.payload.session_id) {
          state.currentSession.messages = messages;
          state.currentSession.last_activity = action.payload.last_activity;
        }
      })
      .addCase(loadConversationHistory.rejected, (state, action) => {
        state.isLoadingHistory = false;
        state.historyError = getErrorMessage(action.error, 'Load conversation history');
      });
  },
});

export const {
  setCurrentSession,
  clearCurrentSession,
  addMessage,
  updateMessage,
  setConnectionStatus,
  setConnectionError,
  setTypingStatus,
  addSession,
  updateSession,
  clearMessages,
} = chatSlice.actions;

export default chatSlice.reducer;