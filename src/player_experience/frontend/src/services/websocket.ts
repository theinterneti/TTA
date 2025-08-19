import { store } from '../store/store';
import { 
  setConnectionStatus, 
  setConnectionError, 
  addMessage, 
  setTypingStatus 
} from '../store/slices/chatSlice';

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private currentSessionId: string | null = null;

  connect(sessionId?: string): void {
    const token = localStorage.getItem('token');
    
    if (!token) {
      store.dispatch(setConnectionError('Authentication token not found'));
      return;
    }

    this.currentSessionId = sessionId || null;
    
    // Convert HTTP URL to WebSocket URL
    const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const wsUrl = baseUrl.replace(/^http/, 'ws') + '/ws/chat';
    
    // Add authentication token as query parameter
    const url = new URL(wsUrl);
    url.searchParams.set('token', token);
    if (sessionId) {
      url.searchParams.set('session_id', sessionId);
    }
    // Enable typing indicators
    url.searchParams.set('typing', '1');

    this.socket = new WebSocket(url.toString());
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      store.dispatch(setConnectionStatus(true));
      this.reconnectAttempts = 0;
    };

    this.socket.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      store.dispatch(setConnectionStatus(false));
      
      // Don't reconnect if it was a policy violation (auth error)
      if (event.code === 1008) {
        store.dispatch(setConnectionError('Authentication failed'));
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

        // Handle crisis alerts
        if (data.metadata?.safety?.crisis) {
          this.handleCrisisAlert(data);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }

  private handleReconnection(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      store.dispatch(setConnectionError('Maximum reconnection attempts reached'));
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect(this.currentSessionId || undefined);
    }, delay);
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

  sendMessage(content: string, metadata?: any): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      store.dispatch(setConnectionError('Not connected to chat server'));
      return;
    }

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

    // Send to server
    this.socket.send(JSON.stringify(message));
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
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      store.dispatch(setConnectionStatus(false));
    }
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN || false;
  }
}

export const websocketService = new WebSocketService();
export default websocketService;