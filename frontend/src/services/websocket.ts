/**
 * TTA WebSocket Client Service
 *
 * Provides real-time communication for therapeutic gaming sessions
 * including chat, crisis detection, and session updates.
 */

import { io, Socket } from 'socket.io-client';
import { ChatMessage, TherapeuticContext } from '../types/therapeutic';

export interface WebSocketEvents {
  // Chat Events
  'chat:message': (message: ChatMessage) => void;
  'chat:typing': (data: { userId: string; isTyping: boolean }) => void;
  'chat:user_joined': (data: { userId: string; username: string }) => void;
  'chat:user_left': (data: { userId: string; username: string }) => void;

  // Session Events
  'session:started': (data: { sessionId: string }) => void;
  'session:paused': (data: { sessionId: string }) => void;
  'session:resumed': (data: { sessionId: string }) => void;
  'session:ended': (data: { sessionId: string }) => void;
  'session:progress_update': (data: { sessionId: string; progress: any }) => void;

  // Therapeutic Events
  'therapeutic:milestone_achieved': (data: { milestoneId: string; description: string }) => void;
  'therapeutic:crisis_detected': (data: { level: 'low' | 'medium' | 'high'; context: string }) => void;
  'therapeutic:support_needed': (data: { type: string; urgency: 'low' | 'medium' | 'high' }) => void;
  'therapeutic:goal_progress': (data: { goalId: string; progress: number }) => void;

  // System Events
  'system:notification': (data: { type: string; message: string }) => void;
  'system:error': (data: { error: string; code?: string }) => void;
  'system:reconnected': () => void;
  'system:disconnected': () => void;
}

class TTAWebSocketClient {
  private socket: Socket | null = null;
  private baseURL: string;
  private currentSessionId: string | null = null;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private eventListeners: Map<string, Function[]> = new Map();

  constructor(baseURL: string = 'http://localhost:8080') {
    this.baseURL = baseURL;
  }

  /**
   * Connect to the WebSocket server
   */
  connect(sessionId?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const token = localStorage.getItem('tta_access_token');

        this.socket = io(`${this.baseURL}/ws/chat`, {
          auth: {
            token: token
          },
          query: {
            sessionId: sessionId || ''
          },
          transports: ['websocket', 'polling'],
          timeout: 10000,
          reconnection: true,
          reconnectionAttempts: this.maxReconnectAttempts,
          reconnectionDelay: 1000,
          reconnectionDelayMax: 5000,
        });

        this.currentSessionId = sessionId || null;

        // Connection event handlers
        this.socket.on('connect', () => {
          console.log('✅ Connected to TTA WebSocket server');
          this.reconnectAttempts = 0;
          this.emit('system:reconnected');
          resolve();
        });

        this.socket.on('disconnect', (reason) => {
          console.log('❌ Disconnected from TTA WebSocket server:', reason);
          this.emit('system:disconnected');
        });

        this.socket.on('connect_error', (error) => {
          console.error('🔌 WebSocket connection error:', error);
          this.reconnectAttempts++;

          if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            reject(new Error(`Failed to connect after ${this.maxReconnectAttempts} attempts`));
          }
        });

        // Set up event forwarding
        this.setupEventForwarding();

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.currentSessionId = null;
      console.log('🔌 Disconnected from TTA WebSocket server');
    }
  }

  /**
   * Join a therapeutic session
   */
  joinSession(sessionId: string): void {
    if (this.socket && this.socket.connected) {
      this.socket.emit('session:join', { sessionId });
      this.currentSessionId = sessionId;
      console.log(`🎮 Joined therapeutic session: ${sessionId}`);
    }
  }

  /**
   * Leave the current therapeutic session
   */
  leaveSession(): void {
    if (this.socket && this.socket.connected && this.currentSessionId) {
      this.socket.emit('session:leave', { sessionId: this.currentSessionId });
      console.log(`🚪 Left therapeutic session: ${this.currentSessionId}`);
      this.currentSessionId = null;
    }
  }

  /**
   * Send a chat message
   */
  sendMessage(content: string, therapeuticContext?: TherapeuticContext): void {
    if (this.socket && this.socket.connected && this.currentSessionId) {
      const message = {
        sessionId: this.currentSessionId,
        content,
        therapeuticContext,
        timestamp: new Date().toISOString(),
        messageType: 'text' as const
      };

      this.socket.emit('chat:send_message', message);
      console.log('💬 Sent message:', content.substring(0, 50) + '...');
    }
  }

  /**
   * Send typing indicator
   */
  sendTyping(isTyping: boolean): void {
    if (this.socket && this.socket.connected && this.currentSessionId) {
      this.socket.emit('chat:typing', {
        sessionId: this.currentSessionId,
        isTyping
      });
    }
  }

  /**
   * Report a crisis or request support
   */
  reportCrisis(level: 'low' | 'medium' | 'high', context: string): void {
    if (this.socket && this.socket.connected && this.currentSessionId) {
      this.socket.emit('therapeutic:crisis_report', {
        sessionId: this.currentSessionId,
        level,
        context,
        timestamp: new Date().toISOString()
      });
      console.log(`🚨 Crisis reported: ${level} level`);
    }
  }

  /**
   * Update session progress
   */
  updateProgress(progress: any): void {
    if (this.socket && this.socket.connected && this.currentSessionId) {
      this.socket.emit('session:update_progress', {
        sessionId: this.currentSessionId,
        progress,
        timestamp: new Date().toISOString()
      });
    }
  }

  /**
   * Set up event forwarding from socket to local event system
   */
  private setupEventForwarding(): void {
    if (!this.socket) return;

    // Chat events
    this.socket.on('chat:message', (message: ChatMessage) => {
      this.emit('chat:message', message);
    });

    this.socket.on('chat:typing', (data) => {
      this.emit('chat:typing', data);
    });

    this.socket.on('chat:user_joined', (data) => {
      this.emit('chat:user_joined', data);
    });

    this.socket.on('chat:user_left', (data) => {
      this.emit('chat:user_left', data);
    });

    // Session events
    this.socket.on('session:started', (data) => {
      this.emit('session:started', data);
    });

    this.socket.on('session:paused', (data) => {
      this.emit('session:paused', data);
    });

    this.socket.on('session:resumed', (data) => {
      this.emit('session:resumed', data);
    });

    this.socket.on('session:ended', (data) => {
      this.emit('session:ended', data);
    });

    this.socket.on('session:progress_update', (data) => {
      this.emit('session:progress_update', data);
    });

    // Therapeutic events
    this.socket.on('therapeutic:milestone_achieved', (data) => {
      this.emit('therapeutic:milestone_achieved', data);
    });

    this.socket.on('therapeutic:crisis_detected', (data) => {
      this.emit('therapeutic:crisis_detected', data);
    });

    this.socket.on('therapeutic:support_needed', (data) => {
      this.emit('therapeutic:support_needed', data);
    });

    this.socket.on('therapeutic:goal_progress', (data) => {
      this.emit('therapeutic:goal_progress', data);
    });

    // System events
    this.socket.on('system:notification', (data) => {
      this.emit('system:notification', data);
    });

    this.socket.on('system:error', (data) => {
      this.emit('system:error', data);
    });
  }

  /**
   * Add event listener
   */
  on<K extends keyof WebSocketEvents>(event: K, listener: WebSocketEvents[K]): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(listener);
  }

  /**
   * Remove event listener
   */
  off<K extends keyof WebSocketEvents>(event: K, listener: WebSocketEvents[K]): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * Emit event to local listeners
   */
  private emit(event: string, ...args: any[]): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(...args);
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error);
        }
      });
    }
  }

  /**
   * Get connection status
   */
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  /**
   * Get current session ID
   */
  getCurrentSessionId(): string | null {
    return this.currentSessionId;
  }

  /**
   * Get socket instance (for advanced usage)
   */
  getSocket(): Socket | null {
    return this.socket;
  }
}

// Create and export a singleton instance
export const ttaWebSocket = new TTAWebSocketClient();
export default ttaWebSocket;
