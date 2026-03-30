// Logseq: [[TTA.dev/Agent_orchestration/Realtime/Client_utils]]
/**
 * WebSocket client utilities for TTA Agent Orchestration real-time communication.
 *
 * Provides automatic reconnection, heartbeat handling, and event management
 * for WebSocket connections to the agent orchestration system.
 */

class TTAWebSocketClient {
  constructor(url, options = {}) {
    this.url = url;
    this.options = {
      token: null,
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      connectionTimeout: 60000,
      debug: false,
      ...options,
    };

    this.ws = null;
    this.reconnectAttempts = 0;
    this.isConnecting = false;
    this.isAuthenticated = false;
    this.connectionId = null;
    this.userId = null;

    // Event handlers
    this.eventHandlers = new Map();
    this.subscriptions = new Set();

    // Heartbeat tracking
    this.lastPingTime = 0;
    this.lastPongTime = 0;
    this.heartbeatTimer = null;
    this.connectionTimer = null;

    // Auto-connect if token provided
    if (this.options.token) {
      this.connect();
    }
  }

  /**
   * Connect to the WebSocket server
   */
  async connect() {
    if (
      this.isConnecting ||
      (this.ws && this.ws.readyState === WebSocket.OPEN)
    ) {
      return;
    }

    this.isConnecting = true;
    this.log("Connecting to WebSocket...");

    try {
      // Build WebSocket URL with token
      const wsUrl = new URL(this.url);
      if (this.options.token) {
        wsUrl.searchParams.set("token", this.options.token);
      }

      this.ws = new WebSocket(wsUrl.toString());
      this.setupEventHandlers();

      // Set connection timeout
      this.connectionTimer = setTimeout(() => {
        if (this.ws.readyState !== WebSocket.OPEN) {
          this.log("Connection timeout");
          this.ws.close();
          this.handleReconnect();
        }
      }, this.options.connectionTimeout);
    } catch (error) {
      this.log("Connection error:", error);
      this.isConnecting = false;
      this.handleReconnect();
    }
  }

  /**
   * Setup WebSocket event handlers
   */
  setupEventHandlers() {
    this.ws.onopen = (event) => {
      this.log("WebSocket connected");
      this.isConnecting = false;
      this.reconnectAttempts = 0;

      if (this.connectionTimer) {
        clearTimeout(this.connectionTimer);
        this.connectionTimer = null;
      }

      // Start heartbeat
      this.startHeartbeat();

      // Emit connection event
      this.emit("connected", { event });
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        this.log("Error parsing message:", error);
      }
    };

    this.ws.onclose = (event) => {
      this.log("WebSocket closed:", event.code, event.reason);
      this.isConnecting = false;
      this.isAuthenticated = false;
      this.connectionId = null;

      this.stopHeartbeat();

      // Emit disconnection event
      this.emit("disconnected", { event });

      // Handle reconnection
      if (event.code !== 1000) {
        // Not a normal closure
        this.handleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      this.log("WebSocket error:", error);
      this.emit("error", { error });
    };
  }

  /**
   * Handle incoming messages
   */
  handleMessage(data) {
    const { event_type, event_id, source, timestamp } = data;

    // Handle connection status events
    if (event_type === "connection_status") {
      this.handleConnectionStatus(data);
    }
    // Handle heartbeat events
    else if (event_type === "heartbeat") {
      this.handleHeartbeat(data);
    }
    // Handle other events
    else {
      this.emit(event_type, data);
      this.emit("message", data);
    }

    this.log("Received message:", event_type, data);
  }

  /**
   * Handle connection status messages
   */
  handleConnectionStatus(data) {
    const status = data.data?.status;

    if (status === "authenticated") {
      this.isAuthenticated = true;
      this.connectionId = data.data?.connection_id;
      this.userId = data.data?.user_id;
      this.log("Authenticated successfully");
      this.emit("authenticated", data);

      // Restore subscriptions
      this.restoreSubscriptions();
    } else if (status === "subscribed") {
      this.log("Subscription confirmed:", data.data);
      this.emit("subscribed", data);
    }
  }

  /**
   * Handle heartbeat messages
   */
  handleHeartbeat(data) {
    const heartbeatType = data.data?.type;

    if (heartbeatType === "ping") {
      // Respond to ping with pong
      this.sendPong(data.data?.ping_id);
    } else if (heartbeatType === "pong") {
      this.lastPongTime = Date.now();
    } else {
      // Regular heartbeat
      this.lastPongTime = Date.now();
    }
  }

  /**
   * Send pong response to ping
   */
  sendPong(pingId) {
    this.send({
      type: "pong",
      ping_id: pingId,
      timestamp: Date.now(),
    });
  }

  /**
   * Start heartbeat monitoring
   */
  startHeartbeat() {
    this.stopHeartbeat();

    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        // Send ping
        this.lastPingTime = Date.now();
        this.send({
          type: "ping",
          timestamp: this.lastPingTime,
        });

        // Check for missed pongs
        const timeSinceLastPong = Date.now() - this.lastPongTime;
        if (timeSinceLastPong > this.options.heartbeatInterval * 3) {
          this.log("Heartbeat timeout, reconnecting...");
          this.ws.close();
        }
      }
    }, this.options.heartbeatInterval);
  }

  /**
   * Stop heartbeat monitoring
   */
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  /**
   * Handle reconnection logic
   */
  handleReconnect() {
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
      this.log("Max reconnection attempts reached");
      this.emit("reconnect_failed");
      return;
    }

    this.reconnectAttempts++;
    const delay =
      this.options.reconnectInterval *
      Math.pow(1.5, this.reconnectAttempts - 1);

    this.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    this.emit("reconnecting", { attempt: this.reconnectAttempts, delay });

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Subscribe to event types
   */
  subscribe(eventTypes, filters = {}) {
    if (!Array.isArray(eventTypes)) {
      eventTypes = [eventTypes];
    }

    eventTypes.forEach((type) => this.subscriptions.add(type));

    const subscription = {
      type: "subscribe",
      subscription: {
        event_types: eventTypes,
        filters: filters,
      },
    };

    this.send(subscription);
  }

  /**
   * Subscribe to events for a specific agent
   */
  subscribeToAgent(agentId) {
    this.send({
      type: "subscribe_agent",
      agent_id: agentId,
    });
  }

  /**
   * Unsubscribe from events for a specific agent
   */
  unsubscribeFromAgent(agentId) {
    this.send({
      type: "unsubscribe_agent",
      agent_id: agentId,
    });
  }

  /**
   * Update event filters
   */
  updateFilters(filters) {
    this.send({
      type: "update_filters",
      filters: filters,
    });
  }

  /**
   * Subscribe to workflow progress events
   */
  subscribeToWorkflowProgress(workflowTypes = [], userIds = []) {
    const filters = {};
    if (workflowTypes.length > 0) {
      filters.workflow_types = workflowTypes;
    }
    if (userIds.length > 0) {
      filters.user_ids = userIds;
    }

    this.subscribe(["workflow_progress"], filters);
  }

  /**
   * Subscribe to agent status events with filtering
   */
  subscribeToAgentStatus(
    agentTypes = [],
    minProgress = null,
    maxProgress = null
  ) {
    const filters = {};
    if (agentTypes.length > 0) {
      filters.agent_types = agentTypes;
    }
    if (minProgress !== null) {
      filters.min_progress = minProgress;
    }
    if (maxProgress !== null) {
      filters.max_progress = maxProgress;
    }

    this.subscribe(["agent_status"], filters);
  }

  /**
   * Subscribe to system metrics (requires appropriate permissions)
   */
  subscribeToSystemMetrics() {
    this.subscribe(["system_metrics"]);
  }

  /**
   * Subscribe to progressive feedback for specific operations
   */
  subscribeToProgressiveFeedback(operationTypes = [], userIds = []) {
    const filters = {};
    if (operationTypes.length > 0) {
      filters.operation_types = operationTypes;
    }
    if (userIds.length > 0) {
      filters.user_ids = userIds;
    }

    this.subscribe(["progressive_feedback"], filters);
  }

  /**
   * Unsubscribe from event types
   */
  unsubscribe(eventTypes) {
    if (!Array.isArray(eventTypes)) {
      eventTypes = [eventTypes];
    }

    eventTypes.forEach((type) => this.subscriptions.delete(type));

    this.send({
      type: "unsubscribe",
      event_types: eventTypes,
    });
  }

  /**
   * Restore subscriptions after reconnection
   */
  restoreSubscriptions() {
    if (this.subscriptions.size > 0) {
      this.subscribe(Array.from(this.subscriptions));
    }
  }

  /**
   * Send message to server
   */
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
      return true;
    }
    return false;
  }

  /**
   * Add event listener
   */
  on(event, handler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event).push(handler);
  }

  /**
   * Remove event listener
   */
  off(event, handler) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event);
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Emit event to listeners
   */
  emit(event, data) {
    if (this.eventHandlers.has(event)) {
      this.eventHandlers.get(event).forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          this.log("Error in event handler:", error);
        }
      });
    }
  }

  /**
   * Close connection
   */
  close() {
    this.stopHeartbeat();

    if (this.connectionTimer) {
      clearTimeout(this.connectionTimer);
      this.connectionTimer = null;
    }

    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
    }
  }

  /**
   * Get connection status
   */
  getStatus() {
    return {
      connected: this.ws && this.ws.readyState === WebSocket.OPEN,
      authenticated: this.isAuthenticated,
      connectionId: this.connectionId,
      userId: this.userId,
      reconnectAttempts: this.reconnectAttempts,
      subscriptions: Array.from(this.subscriptions),
      lastPingTime: this.lastPingTime,
      lastPongTime: this.lastPongTime,
    };
  }

  /**
   * Log debug messages
   */
  log(...args) {
    if (this.options.debug) {
      console.log("[TTAWebSocket]", ...args);
    }
  }
}

// Export for use in browser or Node.js
if (typeof module !== "undefined" && module.exports) {
  module.exports = TTAWebSocketClient;
} else if (typeof window !== "undefined") {
  window.TTAWebSocketClient = TTAWebSocketClient;
}
