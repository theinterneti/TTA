import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

// Types for conversational character creation
interface ConversationMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    stage?: string;
    prompt_id?: string;
    context_text?: string;
    follow_up_prompts?: string[];
    progress?: ConversationProgress;
    character_preview?: any;
    crisis_level?: string;
    resources?: Array<{ name: string; contact: string }>;
  };
}

interface ConversationProgress {
  current_stage: string;
  progress_percentage: number;
  completed_stages: string[];
}

interface ConversationState {
  // Connection state
  isConnected: boolean;
  connectionError: string | null;
  isTyping: boolean;
  
  // Conversation state
  conversationId: string | null;
  isConversationActive: boolean;
  messages: ConversationMessage[];
  progress: ConversationProgress;
  
  // Character creation state
  isCreating: boolean;
  creationError: string | null;
  createdCharacterId: string | null;
  characterPreview: any | null;
  
  // UI state
  isPaused: boolean;
  showProgress: boolean;
}

const initialState: ConversationState = {
  // Connection state
  isConnected: false,
  connectionError: null,
  isTyping: false,
  
  // Conversation state
  conversationId: null,
  isConversationActive: false,
  messages: [],
  progress: {
    current_stage: 'welcome',
    progress_percentage: 0,
    completed_stages: []
  },
  
  // Character creation state
  isCreating: false,
  creationError: null,
  createdCharacterId: null,
  characterPreview: null,
  
  // UI state
  isPaused: false,
  showProgress: true
};

// Async thunks for API calls
export const startConversationalCharacterCreation = createAsyncThunk(
  'conversationalCharacter/start',
  async (playerId: string, { rejectWithValue }) => {
    try {
      // This would typically make an API call to start the conversation
      // For now, we'll simulate the WebSocket connection initiation
      return { playerId };
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to start conversation');
    }
  }
);

export const pauseConversation = createAsyncThunk(
  'conversationalCharacter/pause',
  async (conversationId: string, { rejectWithValue }) => {
    try {
      // API call to pause conversation
      const response = await fetch(`/api/conversations/${conversationId}/pause`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to pause conversation');
      }
      
      return { conversationId };
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to pause conversation');
    }
  }
);

export const resumeConversation = createAsyncThunk(
  'conversationalCharacter/resume',
  async (conversationId: string, { rejectWithValue }) => {
    try {
      // API call to resume conversation
      const response = await fetch(`/api/conversations/${conversationId}/resume`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to resume conversation');
      }
      
      return { conversationId };
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to resume conversation');
    }
  }
);

export const abandonConversation = createAsyncThunk(
  'conversationalCharacter/abandon',
  async (conversationId: string, { rejectWithValue }) => {
    try {
      // API call to abandon conversation
      const response = await fetch(`/api/conversations/${conversationId}/abandon`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to abandon conversation');
      }
      
      return { conversationId };
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to abandon conversation');
    }
  }
);

const conversationalCharacterSlice = createSlice({
  name: 'conversationalCharacter',
  initialState,
  reducers: {
    // Connection management
    setConnectionStatus: (state, action: PayloadAction<{ connected: boolean; error?: string }>) => {
      state.isConnected = action.payload.connected;
      state.connectionError = action.payload.error || null;
    },
    
    setTypingStatus: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload;
    },
    
    // Conversation management
    setConversationId: (state, action: PayloadAction<string>) => {
      state.conversationId = action.payload;
      state.isConversationActive = true;
    },
    
    setConversationActive: (state, action: PayloadAction<boolean>) => {
      state.isConversationActive = action.payload;
    },
    
    addMessage: (state, action: PayloadAction<ConversationMessage>) => {
      state.messages.push(action.payload);
      
      // Update progress if included in message metadata
      if (action.payload.metadata?.progress) {
        state.progress = action.payload.metadata.progress;
      }
      
      // Update character preview if included
      if (action.payload.metadata?.character_preview) {
        state.characterPreview = action.payload.metadata.character_preview;
      }
    },
    
    updateProgress: (state, action: PayloadAction<ConversationProgress>) => {
      state.progress = action.payload;
    },
    
    // Character creation management
    setCreating: (state, action: PayloadAction<boolean>) => {
      state.isCreating = action.payload;
      if (action.payload) {
        state.creationError = null;
      }
    },
    
    setCreationError: (state, action: PayloadAction<string>) => {
      state.creationError = action.payload;
      state.isCreating = false;
    },
    
    setCreatedCharacter: (state, action: PayloadAction<{ characterId: string; preview: any }>) => {
      state.createdCharacterId = action.payload.characterId;
      state.characterPreview = action.payload.preview;
      state.isCreating = false;
      state.isConversationActive = false;
    },
    
    // UI state management
    setPaused: (state, action: PayloadAction<boolean>) => {
      state.isPaused = action.payload;
    },
    
    setShowProgress: (state, action: PayloadAction<boolean>) => {
      state.showProgress = action.payload;
    },
    
    // Reset state
    resetConversation: (state) => {
      state.conversationId = null;
      state.isConversationActive = false;
      state.messages = [];
      state.progress = {
        current_stage: 'welcome',
        progress_percentage: 0,
        completed_stages: []
      };
      state.isPaused = false;
      state.creationError = null;
      state.characterPreview = null;
    },
    
    resetAll: () => initialState,
    
    // Handle WebSocket messages
    handleWebSocketMessage: (state, action: PayloadAction<any>) => {
      const data = action.payload;
      
      switch (data.type) {
        case 'conversation_started':
          state.conversationId = data.conversation_id;
          state.isConversationActive = true;
          break;
          
        case 'assistant_message':
          const assistantMessage: ConversationMessage = {
            id: data.message_id || `assistant_${Date.now()}`,
            type: 'assistant',
            content: data.content,
            timestamp: data.timestamp || new Date().toISOString(),
            metadata: {
              stage: data.stage,
              prompt_id: data.prompt_id,
              context_text: data.context_text,
              follow_up_prompts: data.follow_up_prompts
            }
          };
          state.messages.push(assistantMessage);
          state.isTyping = false;
          break;
          
        case 'progress_update':
          state.progress = data.progress;
          break;
          
        case 'conversation_completed':
          const completionMessage: ConversationMessage = {
            id: `completion_${Date.now()}`,
            type: 'system',
            content: 'Congratulations! Your therapeutic companion has been created successfully.',
            timestamp: new Date().toISOString(),
            metadata: {
              character_preview: data.character_preview
            }
          };
          state.messages.push(completionMessage);
          state.isConversationActive = false;
          state.createdCharacterId = data.character_preview?.character_id;
          state.characterPreview = data.character_preview;
          break;
          
        case 'validation_error':
          const errorMessage: ConversationMessage = {
            id: `error_${Date.now()}`,
            type: 'system',
            content: data.error_message,
            timestamp: new Date().toISOString()
          };
          state.messages.push(errorMessage);
          break;
          
        case 'crisis_detected':
          const crisisMessage: ConversationMessage = {
            id: `crisis_${Date.now()}`,
            type: 'system',
            content: data.support_message,
            timestamp: new Date().toISOString(),
            metadata: {
              crisis_level: data.crisis_level,
              resources: data.resources
            }
          };
          state.messages.push(crisisMessage);
          break;
          
        case 'conversation_paused':
          state.isPaused = true;
          state.isConversationActive = false;
          break;
          
        case 'error':
          state.connectionError = data.error_message;
          break;
      }
    }
  },
  
  extraReducers: (builder) => {
    // Start conversation
    builder
      .addCase(startConversationalCharacterCreation.pending, (state) => {
        state.isCreating = true;
        state.creationError = null;
      })
      .addCase(startConversationalCharacterCreation.fulfilled, (state) => {
        state.isCreating = false;
      })
      .addCase(startConversationalCharacterCreation.rejected, (state, action) => {
        state.isCreating = false;
        state.creationError = action.payload as string;
      });
    
    // Pause conversation
    builder
      .addCase(pauseConversation.fulfilled, (state) => {
        state.isPaused = true;
        state.isConversationActive = false;
      })
      .addCase(pauseConversation.rejected, (state, action) => {
        state.connectionError = action.payload as string;
      });
    
    // Resume conversation
    builder
      .addCase(resumeConversation.fulfilled, (state) => {
        state.isPaused = false;
        state.isConversationActive = true;
      })
      .addCase(resumeConversation.rejected, (state, action) => {
        state.connectionError = action.payload as string;
      });
    
    // Abandon conversation
    builder
      .addCase(abandonConversation.fulfilled, (state) => {
        state.conversationId = null;
        state.isConversationActive = false;
        state.isPaused = false;
        state.messages = [];
        state.progress = initialState.progress;
      })
      .addCase(abandonConversation.rejected, (state, action) => {
        state.connectionError = action.payload as string;
      });
  }
});

export const {
  setConnectionStatus,
  setTypingStatus,
  setConversationId,
  setConversationActive,
  addMessage,
  updateProgress,
  setCreating,
  setCreationError,
  setCreatedCharacter,
  setPaused,
  setShowProgress,
  resetConversation,
  resetAll,
  handleWebSocketMessage
} = conversationalCharacterSlice.actions;

export default conversationalCharacterSlice.reducer;

// Selectors
export const selectConversationState = (state: { conversationalCharacter: ConversationState }) => 
  state.conversationalCharacter;

export const selectIsConnected = (state: { conversationalCharacter: ConversationState }) => 
  state.conversationalCharacter.isConnected;

export const selectMessages = (state: { conversationalCharacter: ConversationState }) => 
  state.conversationalCharacter.messages;

export const selectProgress = (state: { conversationalCharacter: ConversationState }) => 
  state.conversationalCharacter.progress;

export const selectIsConversationActive = (state: { conversationalCharacter: ConversationState }) => 
  state.conversationalCharacter.isConversationActive;

export const selectCharacterPreview = (state: { conversationalCharacter: ConversationState }) => 
  state.conversationalCharacter.characterPreview;
