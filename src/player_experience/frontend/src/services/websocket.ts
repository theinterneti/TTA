import { store } from "../store/store";
import {
  setConnectionStatus,
  setConnectionError,
  addMessage,
  setTypingStatus,
} from "../store/slices/chatSlice";

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private currentSessionId: string | null = null;

  connect(sessionId?: string, playerId?: string): void {
    const token = localStorage.getItem("token");

    if (!token) {
      store.dispatch(setConnectionError("Authentication token not found"));
      return;
    }

    this.currentSessionId = sessionId || null;

    // Get player ID from token or parameter
    const currentPlayerId =
      playerId || this.getPlayerIdFromToken(token) || "default_player";

    if (!sessionId) {
      store.dispatch(
        setConnectionError("Session ID is required for gameplay connection")
      );
      return;
    }

    // Convert HTTP URL to WebSocket URL with path parameters
    const baseUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";
    const wsUrl =
      baseUrl.replace(/^http/, "ws") +
      `/ws/gameplay/${currentPlayerId}/${sessionId}`;

    // Add authentication token as query parameter
    const url = new URL(wsUrl);
    url.searchParams.set("token", token);
    // Enable typing indicators
    url.searchParams.set("typing", "1");

    this.socket = new WebSocket(url.toString());
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log("WebSocket connected");
      store.dispatch(setConnectionStatus(true));
      this.reconnectAttempts = 0;
    };

    this.socket.onclose = (event) => {
      console.log("WebSocket disconnected:", event.code, event.reason);
      store.dispatch(setConnectionStatus(false));

      // Don't reconnect if it was a policy violation (auth error)
      if (event.code === 1008) {
        store.dispatch(setConnectionError("Authentication failed"));
        return;
      }

      this.handleReconnection();
    };

    this.socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      store.dispatch(setConnectionError("WebSocket connection error"));
      this.handleReconnection();
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Handle different message types from backend
        if (data.type === "event" && data.event_type === "typing") {
          const isTyping = data.content?.status === "start";
          store.dispatch(setTypingStatus(isTyping));
          return;
        }

        // Handle gameplay-specific message types
        if (data.type === "narrative_response") {
          const message = {
            id:
              data.id ||
              `narrative_${Date.now()}_${Math.random()
                .toString(36)
                .substr(2, 9)}`,
            type: "assistant" as const,
            content: data.content?.text || "",
            timestamp: data.timestamp || new Date().toISOString(),
            metadata: {
              ...data.metadata,
              scene_updates: data.content?.scene_updates,
              therapeutic_elements: data.content?.therapeutic_elements,
              response_type: data.metadata?.response_type,
            },
          };
          store.dispatch(addMessage(message));
          return;
        }

        if (data.type === "choice_request") {
          const message = {
            id:
              data.id ||
              `choice_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: "assistant" as const,
            content: data.content?.prompt || "",
            timestamp: data.timestamp || new Date().toISOString(),
            metadata: {
              ...data.metadata,
              interactive_elements: {
                buttons:
                  data.content?.choices?.map((choice: any, index: number) => ({
                    id: choice.id || `choice_${index}`,
                    text: choice.text,
                    action: `select_choice:${choice.id}`,
                  })) || [],
              },
            },
          };
          store.dispatch(addMessage(message));
          return;
        }

        // Handle regular messages (fallback for compatibility)
        const messageType: "user" | "system" | "assistant" =
          data.role === "user"
            ? "user"
            : data.role === "system"
            ? "system"
            : "assistant";

        const message = {
          id:
            data.id ||
            `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          type: messageType,
          content:
            typeof data.content === "string"
              ? data.content
              : data.content?.text || "",
          timestamp: data.timestamp || new Date().toISOString(),
          metadata: data.metadata,
        };

        store.dispatch(addMessage(message));

        // Handle crisis alerts
        if (data.metadata?.safety?.crisis) {
          this.handleCrisisAlert(data);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };
  }

  private getPlayerIdFromToken(token: string): string | null {
    try {
      // Decode JWT token to extract player ID
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.player_id || payload.sub || null;
    } catch (error) {
      console.error("Failed to decode token:", error);
      return null;
    }
  }

  private handleReconnection(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      store.dispatch(
        setConnectionError("Maximum reconnection attempts reached")
      );
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    setTimeout(() => {
      console.log(
        `Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
      );
      this.connect(this.currentSessionId || undefined);
    }, delay);
  }

  private handleCrisisAlert(data: any): void {
    // Show immediate crisis support resources
    const crisisMessage = {
      id: `crisis_${Date.now()}`,
      type: "system" as const,
      content:
        "Crisis support resources are available. Please reach out for help if needed.",
      timestamp: new Date().toISOString(),
      metadata: {
        safety_level: "crisis" as const,
        interactive_elements: {
          buttons:
            data.crisis_resources?.map((resource: any, index: number) => ({
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
      store.dispatch(setConnectionError("Not connected to gameplay server"));
      return;
    }

    const message = {
      type: "player_input",
      content: {
        text: content,
        input_type: "narrative_action",
      },
      timestamp: new Date().toISOString(),
      session_id: this.currentSessionId,
      metadata: metadata || {},
    };

    // Add user message to store immediately
    const userMessage = {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: "user" as const,
      content,
      timestamp: message.timestamp,
    };

    store.dispatch(addMessage(userMessage));

    // Send to server
    this.socket.send(JSON.stringify(message));
  }

  sendInteractionResponse(messageId: string, action: string): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      store.dispatch(setConnectionError("Not connected to chat server"));
      return;
    }

    const message = {
      type: "interaction",
      content: {
        message_id: messageId,
        action: action,
      },
      timestamp: new Date().toISOString(),
      session_id: this.currentSessionId,
      metadata: {},
    };

    this.socket.send(JSON.stringify(message));
  }

  sendFeedback(
    messageId: string,
    feedback: "helpful" | "not_helpful",
    comment?: string
  ): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      store.dispatch(setConnectionError("Not connected to chat server"));
      return;
    }

    const message = {
      type: "feedback",
      content: {
        message_id: messageId,
        feedback: feedback,
        comment: comment,
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
