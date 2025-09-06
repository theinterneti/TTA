import { useState, useEffect, useCallback, useRef } from "react";
import { useAuthGuard } from "./useAuthGuard";

export interface RealTimeUpdate {
  type: "world_stats" | "narrative_strength" | "player_count" | "system_status";
  data: any;
  timestamp: string;
  source: "websocket" | "polling";
}

export interface WorldStatistics {
  world_id: string;
  active_players: number;
  completion_rate: number;
  average_session_duration: number;
  narrative_strength: number;
  last_updated: string;
}

export interface UseRealTimeUpdatesOptions {
  enableWebSocket?: boolean;
  enablePolling?: boolean;
  pollingInterval?: number;
  reconnectAttempts?: number;
  reconnectDelay?: number;
  onUpdate?: (update: RealTimeUpdate) => void;
  onError?: (error: Error) => void;
  onConnectionChange?: (connected: boolean) => void;
}

export interface UseRealTimeUpdatesResult {
  isConnected: boolean;
  lastUpdate: RealTimeUpdate | null;
  worldStats: Map<string, WorldStatistics>;
  globalStats: {
    totalPlayers: number;
    activeWorlds: number;
    narrativeStrength: number;
    systemHealth: string;
  } | null;
  connectionType: "websocket" | "polling" | "none";
  error: string | null;
  reconnect: () => void;
  clearError: () => void;
}

/**
 * Custom hook for managing real-time updates via WebSocket and polling
 *
 * Features:
 * - WebSocket connection with automatic reconnection
 * - Fallback to polling if WebSocket fails
 * - Real-time world statistics updates
 * - Global narrative strength monitoring
 * - Connection status tracking
 * - Error handling and recovery
 */
export const useRealTimeUpdates = (
  options: UseRealTimeUpdatesOptions = {}
): UseRealTimeUpdatesResult => {
  const {
    enableWebSocket = true,
    enablePolling = true,
    pollingInterval = 30000, // 30 seconds
    reconnectAttempts = 5,
    reconnectDelay = 2000,
    onUpdate,
    onError,
    onConnectionChange,
  } = options;

  const { isAuthenticated } = useAuthGuard({ autoRedirect: false });

  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<RealTimeUpdate | null>(null);
  const [worldStats, setWorldStats] = useState<Map<string, WorldStatistics>>(
    new Map()
  );
  const [globalStats, setGlobalStats] = useState<{
    totalPlayers: number;
    activeWorlds: number;
    narrativeStrength: number;
    systemHealth: string;
  } | null>(null);
  const [connectionType, setConnectionType] = useState<
    "websocket" | "polling" | "none"
  >("none");
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectCountRef = useRef(0);
  const mountedRef = useRef(true);

  /**
   * Process incoming real-time update
   */
  const processUpdate = useCallback(
    (update: RealTimeUpdate) => {
      if (!mountedRef.current) return;

      setLastUpdate(update);

      switch (update.type) {
        case "world_stats":
          if (update.data.world_id) {
            setWorldStats((prev) => {
              const newMap = new Map(prev);
              newMap.set(update.data.world_id, update.data);
              return newMap;
            });
          }
          break;

        case "narrative_strength":
        case "player_count":
        case "system_status":
          setGlobalStats((prev) => ({
            ...prev,
            ...update.data,
          }));
          break;
      }

      onUpdate?.(update);
    },
    [onUpdate]
  );

  /**
   * Polling functions - defined before useEffect to avoid hoisting issues
   */
  const fetchUpdates = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      const response = await fetch("/api/nexus/status", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      const update: RealTimeUpdate = {
        type: "system_status",
        data,
        timestamp: new Date().toISOString(),
        source: "polling",
      };

      processUpdate(update);

      if (!isConnected) {
        setIsConnected(true);
        onConnectionChange?.(true);
      }

      setError(null);
    } catch (err: any) {
      console.error("Polling update failed:", err);
      setError(err.message);
      onError?.(err);

      if (isConnected) {
        setIsConnected(false);
        onConnectionChange?.(false);
      }
    }
  }, [
    isAuthenticated,
    isConnected,
    processUpdate,
    onConnectionChange,
    onError,
  ]);

  const startPolling = useCallback(() => {
    if (!enablePolling || pollingIntervalRef.current) return;

    // Initial fetch
    fetchUpdates();

    // Set up interval
    pollingIntervalRef.current = setInterval(fetchUpdates, pollingInterval);
  }, [enablePolling, fetchUpdates, pollingInterval]);

  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  /**
   * WebSocket connection management
   */
  const connectWebSocket = useCallback(() => {
    if (!enableWebSocket || !isAuthenticated) return;

    try {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/updates`;

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        if (!mountedRef.current) return;

        console.log("WebSocket connected for real-time updates");
        setIsConnected(true);
        setConnectionType("websocket");
        setError(null);
        reconnectCountRef.current = 0;
        onConnectionChange?.(true);
      };

      wsRef.current.onmessage = (event) => {
        if (!mountedRef.current) return;

        try {
          const update: RealTimeUpdate = {
            ...JSON.parse(event.data),
            source: "websocket",
            timestamp: new Date().toISOString(),
          };
          processUpdate(update);
        } catch (err) {
          console.error("Failed to parse WebSocket message:", err);
        }
      };

      wsRef.current.onclose = (event) => {
        if (!mountedRef.current) return;

        console.log("WebSocket disconnected:", event.code, event.reason);
        setIsConnected(false);
        onConnectionChange?.(false);

        // Attempt reconnection if not a clean close
        if (
          event.code !== 1000 &&
          reconnectCountRef.current < reconnectAttempts
        ) {
          reconnectCountRef.current++;
          const delay =
            reconnectDelay * Math.pow(2, reconnectCountRef.current - 1);

          console.log(
            `Attempting WebSocket reconnection ${reconnectCountRef.current}/${reconnectAttempts} in ${delay}ms`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              connectWebSocket();
            }
          }, delay);
        } else if (enablePolling) {
          // Fallback to polling
          console.log("WebSocket reconnection failed, falling back to polling");
          setConnectionType("polling");
          startPolling();
        } else {
          setConnectionType("none");
        }
      };

      wsRef.current.onerror = (error) => {
        if (!mountedRef.current) return;

        console.error("WebSocket error:", error);
        const errorMessage = "WebSocket connection failed";
        setError(errorMessage);
        onError?.(new Error(errorMessage));
      };
    } catch (err: any) {
      console.error("Failed to create WebSocket connection:", err);
      setError(err.message);
      onError?.(err);

      if (enablePolling) {
        setConnectionType("polling");
        startPolling();
      }
    }
  }, [
    enableWebSocket,
    isAuthenticated,
    reconnectAttempts,
    reconnectDelay,
    enablePolling,
    onConnectionChange,
    onError,
    processUpdate,
    startPolling,
  ]);

  // fetchUpdates function moved above to avoid hoisting issues

  // Polling functions moved above to avoid hoisting issues

  /**
   * Manual reconnection
   */
  const reconnect = useCallback(() => {
    setError(null);
    reconnectCountRef.current = 0;

    // Close existing connections
    if (wsRef.current) {
      wsRef.current.close();
    }
    stopPolling();

    // Clear reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    // Start fresh connection
    if (enableWebSocket) {
      connectWebSocket();
    } else if (enablePolling) {
      setConnectionType("polling");
      startPolling();
    }
  }, [
    enableWebSocket,
    enablePolling,
    connectWebSocket,
    startPolling,
    stopPolling,
  ]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Initialize connections
   */
  useEffect(() => {
    if (!isAuthenticated) {
      setIsConnected(false);
      setConnectionType("none");
      return;
    }

    if (enableWebSocket) {
      connectWebSocket();
    } else if (enablePolling) {
      setConnectionType("polling");
      startPolling();
    }

    return () => {
      mountedRef.current = false;

      if (wsRef.current) {
        wsRef.current.close();
      }

      stopPolling();

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [
    isAuthenticated,
    enableWebSocket,
    enablePolling,
    connectWebSocket,
    startPolling,
    stopPolling,
  ]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return {
    isConnected,
    lastUpdate,
    worldStats,
    globalStats,
    connectionType,
    error,
    reconnect,
    clearError,
  };
};

/**
 * Simplified hook for world-specific real-time updates
 */
export const useWorldRealTimeUpdates = (worldId: string) => {
  const { worldStats, isConnected, error } = useRealTimeUpdates({
    enableWebSocket: true,
    enablePolling: true,
    pollingInterval: 15000, // More frequent for specific world
  });

  return {
    worldStats: worldStats.get(worldId) || null,
    isConnected,
    error,
  };
};

export default useRealTimeUpdates;
