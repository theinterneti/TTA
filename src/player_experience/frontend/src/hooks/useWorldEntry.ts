import { useCallback, useState, useEffect } from "react";
import { nexusAPI } from "../services/api";
import { useAuthGuard } from "./useAuthGuard";

export interface WorldEntryData {
  character_id?: string;
  entry_preferences?: {
    difficulty_adjustment?: "easier" | "normal" | "harder";
    therapeutic_focus?: string[];
    session_duration?: number;
    privacy_mode?: boolean;
  };
  custom_parameters?: Record<string, any>;
}

export interface WorldEntryResponse {
  session_id: string;
  world_id: string;
  character_id?: string;
  entry_point: string;
  session_config: {
    difficulty_level: string;
    therapeutic_focus: string[];
    estimated_duration: number;
    privacy_mode: boolean;
  };
  initial_state: {
    location: string;
    narrative_context: string;
    available_actions: string[];
  };
  status: "ready" | "pending" | "error";
  message?: string;
}

export interface UseWorldEntryOptions {
  onSuccess?: (response: WorldEntryResponse) => void;
  onError?: (error: Error) => void;
  autoNavigate?: boolean;
}

export interface UseWorldEntryResult {
  enterWorld: (
    worldId: string,
    entryData?: WorldEntryData
  ) => Promise<WorldEntryResponse>;
  entering: boolean;
  error: string | null;
  lastEntryResponse: WorldEntryResponse | null;
  clearError: () => void;
}

/**
 * Custom hook for managing world entry functionality
 *
 * Features:
 * - World entry with customizable preferences
 * - Session management
 * - Error handling
 * - Authentication checks
 * - Success/error callbacks
 */
export const useWorldEntry = (
  options: UseWorldEntryOptions = {}
): UseWorldEntryResult => {
  const { onSuccess, onError, autoNavigate = false } = options;

  const { isAuthenticated } = useAuthGuard({ autoRedirect: false });

  const [entering, setEntering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastEntryResponse, setLastEntryResponse] =
    useState<WorldEntryResponse | null>(null);

  /**
   * Enter a world with optional entry data
   */
  const enterWorld = useCallback(
    async (
      worldId: string,
      entryData: WorldEntryData = {}
    ): Promise<WorldEntryResponse> => {
      try {
        setEntering(true);
        setError(null);

        // Check authentication
        if (!isAuthenticated) {
          throw new Error("You must be logged in to enter a world");
        }

        // Validate worldId
        if (!worldId || typeof worldId !== "string") {
          throw new Error("Invalid world ID provided");
        }

        // Prepare entry data with defaults
        const preparedEntryData: WorldEntryData = {
          entry_preferences: {
            difficulty_adjustment: "normal",
            therapeutic_focus: [],
            session_duration: 30,
            privacy_mode: false,
            ...entryData.entry_preferences,
          },
          ...entryData,
        };

        // Call API
        const response = await nexusAPI.enterWorld(worldId, preparedEntryData);

        // Validate response
        if (!response || typeof response !== "object") {
          throw new Error("Invalid response from server");
        }

        // Ensure required fields are present
        const responseData = response as any;
        const entryResponse: WorldEntryResponse = {
          session_id: responseData.session_id || "",
          world_id: worldId,
          character_id: responseData.character_id,
          entry_point: responseData.entry_point || "default",
          session_config: {
            difficulty_level:
              responseData.session_config?.difficulty_level || "normal",
            therapeutic_focus:
              responseData.session_config?.therapeutic_focus || [],
            estimated_duration:
              responseData.session_config?.estimated_duration || 30,
            privacy_mode: responseData.session_config?.privacy_mode || false,
          },
          initial_state: {
            location: responseData.initial_state?.location || "Starting Area",
            narrative_context:
              responseData.initial_state?.narrative_context ||
              "Welcome to the world!",
            available_actions:
              responseData.initial_state?.available_actions || [],
          },
          status: responseData.status || "ready",
          message: responseData.message,
        };

        setLastEntryResponse(entryResponse);
        onSuccess?.(entryResponse);

        // Auto-navigate if enabled
        if (autoNavigate && entryResponse.status === "ready") {
          // This would typically navigate to the game session
          console.log("Auto-navigating to session:", entryResponse.session_id);
        }

        return entryResponse;
      } catch (err: any) {
        const errorMessage = err.message || "Failed to enter world";
        setError(errorMessage);
        onError?.(err);
        throw err;
      } finally {
        setEntering(false);
      }
    },
    [isAuthenticated, onSuccess, onError, autoNavigate]
  );

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    enterWorld,
    entering,
    error,
    lastEntryResponse,
    clearError,
  };
};

/**
 * Hook for managing multiple world entries (batch entry)
 */
export const useBatchWorldEntry = () => {
  const [batchResults, setBatchResults] = useState<
    Array<{
      worldId: string;
      status: "pending" | "success" | "error";
      response?: WorldEntryResponse;
      error?: string;
    }>
  >([]);
  const [batchProgress, setBatchProgress] = useState({ current: 0, total: 0 });
  const [isBatchEntering, setIsBatchEntering] = useState(false);

  const enterWorldsBatch = useCallback(
    async (entries: Array<{ worldId: string; entryData?: WorldEntryData }>) => {
      setIsBatchEntering(true);
      setBatchResults([]);
      setBatchProgress({ current: 0, total: entries.length });

      const results: typeof batchResults = [];

      for (let i = 0; i < entries.length; i++) {
        const { worldId, entryData } = entries[i];

        setBatchProgress({ current: i + 1, total: entries.length });

        try {
          const response = await nexusAPI.enterWorld(worldId, entryData || {});

          results.push({
            worldId,
            status: "success",
            response: response as any,
          });
        } catch (err: any) {
          results.push({
            worldId,
            status: "error",
            error: err.message || "Failed to enter world",
          });
        }
      }

      setBatchResults(results);
      setIsBatchEntering(false);

      return results;
    },
    []
  );

  return {
    enterWorldsBatch,
    batchResults,
    batchProgress,
    isBatchEntering,
  };
};

/**
 * Hook for managing world entry history
 */
export const useWorldEntryHistory = () => {
  const [entryHistory, setEntryHistory] = useState<
    Array<{
      id: string;
      worldId: string;
      worldTitle: string;
      enteredAt: string;
      sessionId: string;
      duration?: number;
      completed: boolean;
    }>
  >([]);

  const addToHistory = useCallback(
    (entry: { worldId: string; worldTitle: string; sessionId: string }) => {
      const historyEntry = {
        id: Date.now().toString(),
        ...entry,
        enteredAt: new Date().toISOString(),
        completed: false,
      };

      setEntryHistory((prev) => [historyEntry, ...prev.slice(0, 49)]); // Keep last 50 entries

      // Save to localStorage
      try {
        const updated = [historyEntry, ...entryHistory.slice(0, 49)];
        localStorage.setItem(
          "tta_world_entry_history",
          JSON.stringify(updated)
        );
      } catch (error) {
        console.error("Failed to save entry history to localStorage:", error);
      }
    },
    [entryHistory]
  );

  const markCompleted = useCallback((sessionId: string, duration?: number) => {
    setEntryHistory((prev) => {
      const updated = prev.map((entry) =>
        entry.sessionId === sessionId
          ? { ...entry, completed: true, duration }
          : entry
      );

      // Update localStorage
      try {
        localStorage.setItem(
          "tta_world_entry_history",
          JSON.stringify(updated)
        );
      } catch (error) {
        console.error("Failed to update entry history in localStorage:", error);
      }

      return updated;
    });
  }, []);

  const clearHistory = useCallback(() => {
    setEntryHistory([]);
    try {
      localStorage.removeItem("tta_world_entry_history");
    } catch (error) {
      console.error("Failed to clear entry history from localStorage:", error);
    }
  }, []);

  // Load history from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem("tta_world_entry_history");
      if (saved) {
        setEntryHistory(JSON.parse(saved));
      }
    } catch (error) {
      console.error("Failed to load entry history from localStorage:", error);
    }
  }, []);

  return {
    entryHistory,
    addToHistory,
    markCompleted,
    clearHistory,
  };
};

export default useWorldEntry;
