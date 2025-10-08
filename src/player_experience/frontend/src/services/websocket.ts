import {
    addMessage,
    setConnectionError,
    setConnectionStatus,
    setTypingStatus
} from '../store/slices/chatSlice';
import { store } from '../store/store';
import secureStorage from '../utils/secureStorage';
import { realTimeTherapeuticMonitor } from './realTimeTherapeuticMonitor';

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10; // Increased from 5
  private reconnectDelay = 1000;
  private currentSessionId: string | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private heartbeatInterval = 30000; // 30 seconds
  private lastHeartbeat: number = 0;
  private isIntentionalDisconnect = false;
  private messageQueue: any[] = []; // Queue messages when disconnected

  private validateConnectionPrerequisites(): { isValid: boolean; error: string } {
    const token = secureStorage.getToken();
    if (!token) {
      return { isValid: false, error: 'Authentication token not found' };
    }

    const state = store.getState();
    const isAuthenticated = state.auth?.isAuthenticated;
    if (!isAuthenticated) {
      return { isValid: false, error: 'User not authenticated' };
    }

    const playerId = state.player?.profile?.player_id;
    if (!playerId) {
      return { isValid: false, error: 'Player profile not loaded' };
    }

    return { isValid: true, error: '' };
  }

  connect(sessionId?: string): void {
    // Validate prerequisites before attempting connection
    const prerequisites = this.validateConnectionPrerequisites();
    if (!prerequisites.isValid) {
      store.dispatch(setConnectionError(prerequisites.error));
      console.warn('WebSocket connection prerequisites not met:', prerequisites.error);
      return;
    }

    const token = secureStorage.getToken()!; // Safe to use ! after validation
    this.currentSessionId = sessionId || null;

    // Convert HTTP URL to WebSocket URL with fallback
    const apiUrl = process.env.REACT_APP_API_URL ||
                   process.env.VITE_API_BASE_URL ||
                   'http://localhost:8080';
    const wsUrl = apiUrl.replace(/^http/, 'ws') + '/ws/chat';

    console.log('WebSocket connecting to:', wsUrl); // Debug log

    // Add authentication token as query parameter
    const url = new URL(wsUrl);
    url.searchParams.set('token', token);
    if (sessionId) {
      url.searchParams.set('session_id', sessionId);
    }

    // Add player ID for preferences
    const state = store.getState();
    const playerId = state.player?.profile?.player_id!; // Safe after validation
    url.searchParams.set('player_id', playerId);

    // Enable typing indicators
    url.searchParams.set('typing', '1');

    console.log('WebSocket full URL:', url.toString()); // Debug log

    this.socket = new WebSocket(url.toString());
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      store.dispatch(setConnectionStatus(true));
      store.dispatch(setConnectionError(null));
      this.reconnectAttempts = 0;
      this.isIntentionalDisconnect = false;

      // Start heartbeat
      this.startHeartbeat();

      // Flush message queue
      this.flushMessageQueue();
    };

    this.socket.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      store.dispatch(setConnectionStatus(false));

      // Stop heartbeat
      this.stopHeartbeat();

      // Don't reconnect if it was intentional
      if (this.isIntentionalDisconnect) {
        console.log('Intentional disconnect, not reconnecting');
        return;
      }

      // Don't reconnect if it was a policy violation (auth error)
      if (event.code === 1008) {
        store.dispatch(setConnectionError('Authentication failed. Please log in again.'));
        return;
      }

      // Don't reconnect on normal closure
      if (event.code === 1000) {
        console.log('Normal closure, not reconnecting');
        return;
      }

      this.handleReconnection();
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      store.dispatch(setConnectionError('WebSocket connection error'));
      this.handleReconnection();
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Handle pong response
        if (data.type === 'pong') {
          this.lastHeartbeat = Date.now();
          return;
        }

        // Handle different message types from backend
        if (data.type === 'event' && data.event_type === 'typing') {
          const isTyping = data.content?.status === 'start';
          store.dispatch(setTypingStatus(isTyping));
          return;
        }

        // Handle regular messages
        const message = {
          id: data.id || `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          type: data.role === 'user' ? 'user' : data.role === 'system' ? 'system' : 'assistant',
          content: typeof data.content === 'string' ? data.content : data.content?.text || '',
          timestamp: data.timestamp || new Date().toISOString(),
          metadata: data.metadata,
        };

        store.dispatch(addMessage(message));

        // Enhanced real-time therapeutic monitoring
        if (message.type === 'user' && this.currentSessionId) {
          this.analyzeUserMessage(message.content, data.metadata || {});
        }

        // Handle crisis alerts
        if (data.metadata?.safety?.crisis) {
          this.handleCrisisAlert(data);
        }

        // Handle therapeutic monitoring data
        if (data.type === 'monitoring_update') {
          this.handleMonitoringUpdate(data);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }

  private handleReconnection(): void {
    // Clear any existing reconnect timer
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      store.dispatch(setConnectionError('Connection lost. Please refresh the page to reconnect.'));
      return;
    }

    this.reconnectAttempts++;
    // Exponential backoff with jitter
    const baseDelay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    const jitter = Math.random() * 1000; // Add up to 1 second of jitter
    const delay = Math.min(baseDelay + jitter, 30000); // Cap at 30 seconds

    store.dispatch(setConnectionError(`Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`));

    this.reconnectTimer = setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect(this.currentSessionId || undefined);
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.lastHeartbeat = Date.now();

    this.heartbeatTimer = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        try {
          this.socket.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));

          // Check if we've received a response recently
          const timeSinceLastHeartbeat = Date.now() - this.lastHeartbeat;
          if (timeSinceLastHeartbeat > this.heartbeatInterval * 2) {
            console.warn('Heartbeat timeout, connection may be stale');
            this.socket.close();
          }
        } catch (error) {
          console.error('Failed to send heartbeat:', error);
        }
      }
    }, this.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private flushMessageQueue(): void {
    if (this.messageQueue.length === 0) return;

    console.log(`Flushing ${this.messageQueue.length} queued messages`);

    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        try {
          this.socket.send(JSON.stringify(message));
        } catch (error) {
          console.error('Failed to send queued message:', error);
          // Re-queue if send fails
          this.messageQueue.unshift(message);
          break;
        }
      }
    }
  }

  private handleCrisisAlert(data: any): void {
    // Show immediate crisis support resources
    const crisisMessage = {
      id: `crisis_${Date.now()}`,
      type: 'system' as const,
      content: 'Crisis support resources are available. Please reach out for help if needed.',
      timestamp: new Date().toISOString(),
      metadata: {
        safety_level: 'crisis' as const,
        interactive_elements: {
          buttons: data.crisis_resources?.map((resource: any, index: number) => ({
            id: `crisis_${index}`,
            text: resource.name,
            action: `open_resource:${resource.url}`,
          })) || [],
        },
      },
    };

    store.dispatch(addMessage(crisisMessage));
  }

  /**
   * Analyze user message for real-time therapeutic monitoring
   */
  private async analyzeUserMessage(content: string, metadata: any): Promise<void> {
    if (!this.currentSessionId) return;

    try {
      const state = store.getState();
      const userId = state.player?.profile?.player_id;
      const therapeuticGoals = state.therapeuticGoals?.selected || [];

      if (userId) {
        // Analyze the message with real-time monitoring
        await realTimeTherapeuticMonitor.analyzeUserInput(
          this.currentSessionId,
          content,
          {
            messageLength: content.length,
            responseTime: metadata.responseTime,
            therapeuticGoalsProgress: metadata.therapeuticProgress,
            socialSupport: metadata.socialSupport,
            timestamp: Date.now()
          }
        );
      }
    } catch (error) {
      console.error('Error analyzing user message for monitoring:', error);
    }
  }

  /**
   * Handle monitoring updates from backend
   */
  private handleMonitoringUpdate(data: any): void {
    try {
      if (data.session_id && data.monitoring_data) {
        // Forward monitoring data to the real-time monitor
        const callback = realTimeTherapeuticMonitor['monitoringCallbacks']?.get(data.session_id);
        if (callback) {
          callback(data.monitoring_data);
        }
      }
    } catch (error) {
      console.error('Error handling monitoring update:', error);
    }
  }

  sendMessage(content: string, metadata?: any): void {
    const message = {
      type: 'user_message',
      content: { text: content },
      timestamp: new Date().toISOString(),
      session_id: this.currentSessionId,
      metadata: metadata || {},
    };

    // Add user message to store immediately
    const userMessage = {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: 'user' as const,
      content,
      timestamp: message.timestamp,
    };

    store.dispatch(addMessage(userMessage));

    // Send to server or queue if disconnected
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, queueing message');
      this.messageQueue.push(message);

      // Attempt to reconnect if not already trying
      if (this.reconnectAttempts === 0) {
        store.dispatch(setConnectionError('Connection lost, attempting to reconnect...'));
        this.handleReconnection();
      }
      return;
    }

    try {
      this.socket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send message:', error);
      this.messageQueue.push(message);
      store.dispatch(setConnectionError('Failed to send message, will retry'));
    }
  }

  sendInteractionResponse(messageId: string, action: string): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      store.dispatch(setConnectionError('Not connected to chat server'));
      return;
    }

    const message = {
      type: 'interaction',
      content: {
        message_id: messageId,
        action: action
      },
      timestamp: new Date().toISOString(),
      session_id: this.currentSessionId,
      metadata: {},
    };

    this.socket.send(JSON.stringify(message));
  }

  sendFeedback(messageId: string, feedback: 'helpful' | 'not_helpful', comment?: string): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      store.dispatch(setConnectionError('Not connected to chat server'));
      return;
    }

    const message = {
      type: 'feedback',
      content: {
        message_id: messageId,
        feedback: feedback,
        comment: comment
      },
      timestamp: new Date().toISOString(),
      session_id: this.currentSessionId,
      metadata: {},
    };

    this.socket.send(JSON.stringify(message));
  }

  disconnect(): void {
    this.isIntentionalDisconnect = true;

    // Clear timers
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.stopHeartbeat();

    if (this.socket) {
      this.socket.close(1000, 'Client disconnect');
      this.socket = null;
      store.dispatch(setConnectionStatus(false));
    }

    // Clear message queue
    this.messageQueue = [];
    this.reconnectAttempts = 0;
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN || false;
  }

  canConnect(): boolean {
    return this.validateConnectionPrerequisites().isValid;
  }

  getConnectionStatus(): { canConnect: boolean; isConnected: boolean; error?: string } {
    const prerequisites = this.validateConnectionPrerequisites();
    return {
      canConnect: prerequisites.isValid,
      isConnected: this.isConnected(),
      error: prerequisites.isValid ? undefined : prerequisites.error
    };
  }

  /**
   * Handle page visibility changes
   * Reconnect when page becomes visible if connection was lost
   */
  handleVisibilityChange(): void {
    if (document.visibilityState === 'visible') {
      // Page became visible
      if (!this.isConnected() && !this.isIntentionalDisconnect && this.currentSessionId) {
        console.log('Page visible, checking connection...');

        // Reset reconnect attempts for fresh start
        this.reconnectAttempts = 0;

        // Attempt to reconnect
        this.connect(this.currentSessionId);
      }
    }
  }

  /**
   * Initialize visibility change listener
   */
  initializeVisibilityListener(): void {
    document.addEventListener('visibilitychange', () => {
      this.handleVisibilityChange();
    });
  }
}

const websocketService = new WebSocketService();

// Initialize visibility listener
websocketService.initializeVisibilityListener();

export { websocketService };
export default websocketService;
