/**
 * WebSocket Service for Conversational Character Creation
 * 
 * This service manages WebSocket connections specifically for the conversational
 * character creation process, handling real-time communication between the
 * frontend and the conversational character creation backend.
 */

import { store } from '../store/store';
import {
  setConnectionStatus,
  setTypingStatus,
  setConversationId,
  addMessage,
  updateProgress,
  setCreatedCharacter,
  handleWebSocketMessage,
  resetConversation
} from '../store/slices/conversationalCharacterSlice';

export interface ConversationMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: any;
}

class ConversationalWebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private conversationId: string | null = null;
  private playerId: string | null = null;

  constructor() {
    this.setupEventListeners();
  }

  /**
   * Connect to the conversational character creation WebSocket
   */
  async connect(playerId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.playerId = playerId;
        const token = localStorage.getItem('token');
        
        if (!token) {
          const error = 'Authentication token not found';
          store.dispatch(setConnectionStatus({ connected: false, error }));
          reject(new Error(error));
          return;
        }

        // Create WebSocket URL
        const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const wsUrl = baseUrl.replace(/^http/, 'ws') + '/ws/conversational-character-creation';
        
        const url = new URL(wsUrl);
        url.searchParams.set('token', token);

        this.socket = new WebSocket(url.toString());
        this.setupSocketEventHandlers(resolve, reject);
        
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Connection failed';
        store.dispatch(setConnectionStatus({ connected: false, error: errorMessage }));
        reject(error);
      }
    });
  }

  /**
   * Setup WebSocket event handlers
   */
  private setupSocketEventHandlers(resolve: () => void, reject: (error: Error) => void): void {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log('Connected to conversational character creation WebSocket');
      store.dispatch(setConnectionStatus({ connected: true }));
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      
      // Automatically start conversation
      this.startConversation();
      resolve();
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.socket.onclose = (event) => {
      console.log('WebSocket connection closed:', event.code, event.reason);
      store.dispatch(setConnectionStatus({ connected: false }));
      this.stopHeartbeat();
      
      // Attempt reconnection if not a normal closure
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.attemptReconnection();
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      store.dispatch(setConnectionStatus({ 
        connected: false, 
        error: 'Connection error occurred' 
      }));
      reject(new Error('WebSocket connection failed'));
    };
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(data: any): void {
    // Dispatch to Redux store for centralized handling
    store.dispatch(handleWebSocketMessage(data));

    // Handle specific message types that need additional processing
    switch (data.type) {
      case 'conversation_started':
        this.conversationId = data.conversation_id;
        store.dispatch(setConversationId(data.conversation_id));
        break;

      case 'assistant_message':
        // Stop typing indicator when assistant message arrives
        store.dispatch(setTypingStatus(false));
        break;

      case 'conversation_completed':
        // Handle successful character creation
        if (data.character_preview?.character_id) {
          store.dispatch(setCreatedCharacter({
            characterId: data.character_preview.character_id,
            preview: data.character_preview
          }));
        }
        break;

      case 'error':
        console.error('Server error:', data.error_message);
        break;

      default:
        console.log('Unhandled message type:', data.type);
    }
  }

  /**
   * Start a new conversation
   */
  private startConversation(): void {
    if (!this.socket || !this.playerId) return;

    const message = {
      type: 'start_conversation',
      player_id: this.playerId,
      metadata: {
        source: 'conversational_ui',
        timestamp: new Date().toISOString()
      }
    };

    this.sendMessage(message);
  }

  /**
   * Send a user response
   */
  sendUserResponse(content: string): void {
    if (!this.socket || !this.conversationId) {
      console.error('Cannot send message: not connected or no active conversation');
      return;
    }

    // Add user message to store immediately for UI responsiveness
    const userMessage: ConversationMessage = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString()
    };

    store.dispatch(addMessage(userMessage));
    store.dispatch(setTypingStatus(true));

    // Send to server
    const message = {
      type: 'user_response',
      conversation_id: this.conversationId,
      content: content.trim(),
      timestamp: new Date().toISOString(),
      metadata: {
        source: 'user_input'
      }
    };

    this.sendMessage(message);
  }

  /**
   * Pause the current conversation
   */
  pauseConversation(): void {
    if (!this.socket || !this.conversationId) return;

    const message = {
      type: 'pause_conversation',
      conversation_id: this.conversationId,
      timestamp: new Date().toISOString()
    };

    this.sendMessage(message);
  }

  /**
   * Resume a paused conversation
   */
  resumeConversation(): void {
    if (!this.socket || !this.conversationId) return;

    const message = {
      type: 'resume_conversation',
      conversation_id: this.conversationId,
      timestamp: new Date().toISOString()
    };

    this.sendMessage(message);
  }

  /**
   * Abandon the current conversation
   */
  abandonConversation(): void {
    if (!this.socket || !this.conversationId) return;

    const message = {
      type: 'abandon_conversation',
      conversation_id: this.conversationId,
      timestamp: new Date().toISOString()
    };

    this.sendMessage(message);
    
    // Reset local state
    this.conversationId = null;
    store.dispatch(resetConversation());
  }

  /**
   * Send a message through the WebSocket
   */
  private sendMessage(message: any): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('Cannot send message: WebSocket not connected');
      return;
    }

    try {
      this.socket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
    }
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(): void {
    this.stopHeartbeat();
    
    if (this.socket) {
      this.socket.close(1000, 'Client disconnect');
      this.socket = null;
    }
    
    this.conversationId = null;
    this.playerId = null;
    store.dispatch(setConnectionStatus({ connected: false }));
  }

  /**
   * Attempt to reconnect to WebSocket
   */
  private attemptReconnection(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      store.dispatch(setConnectionStatus({ 
        connected: false, 
        error: 'Connection lost. Please refresh the page.' 
      }));
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`);
    
    setTimeout(() => {
      if (this.playerId) {
        this.connect(this.playerId).catch(error => {
          console.error('Reconnection failed:', error);
        });
      }
    }, delay);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.sendMessage({ type: 'ping', timestamp: new Date().toISOString() });
      }
    }, 30000); // Send ping every 30 seconds
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Setup global event listeners
   */
  private setupEventListeners(): void {
    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        // Page is hidden, pause heartbeat
        this.stopHeartbeat();
      } else {
        // Page is visible, resume heartbeat
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          this.startHeartbeat();
        }
      }
    });

    // Handle page unload
    window.addEventListener('beforeunload', () => {
      this.disconnect();
    });
  }

  /**
   * Get current connection status
   */
  isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }

  /**
   * Get current conversation ID
   */
  getConversationId(): string | null {
    return this.conversationId;
  }
}

// Export singleton instance
export const conversationalWebSocketService = new ConversationalWebSocketService();
export default conversationalWebSocketService;
