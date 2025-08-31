/**
 * Debug utilities for tracking infinite re-render loops
 */
import React from "react";

// Redux action logger middleware
export const actionLogger = (store: any) => (next: any) => (action: any) => {
  const timestamp = new Date().toISOString();
  console.log(`🚀 Redux Action: ${action.type}`, {
    timestamp,
    payload: action.payload,
    meta: action.meta,
  });

  const result = next(action);

  // Log state after action
  const state = store.getState();
  console.log(`📊 State after ${action.type}:`, {
    player: {
      profile: state.player?.profile?.player_id,
      isLoading: state.player?.isLoading,
    },
    character: {
      charactersCount: state.character?.characters?.length || 0,
      creationInProgress: state.character?.creationInProgress,
      error: state.character?.error,
    },
    auth: {
      isAuthenticated: state.auth?.isAuthenticated,
      userId: state.auth?.user?.user_id,
    },
  });

  return result;
};

// Component render tracker
export const useRenderTracker = (componentName: string) => {
  const renderCount = React.useRef(0);
  renderCount.current += 1;

  console.log(`🔄 ${componentName} render #${renderCount.current}`, {
    timestamp: new Date().toISOString(),
  });

  return renderCount.current;
};

// Detect infinite loops
let actionCounts: { [key: string]: number } = {};
let lastResetTime = Date.now();

export const detectInfiniteLoop = (
  actionType: string,
  threshold = 10,
  timeWindow = 5000
) => {
  const now = Date.now();

  // Reset counts every time window
  if (now - lastResetTime > timeWindow) {
    actionCounts = {};
    lastResetTime = now;
  }

  actionCounts[actionType] = (actionCounts[actionType] || 0) + 1;

  if (actionCounts[actionType] > threshold) {
    console.error(
      `🚨 INFINITE LOOP DETECTED: ${actionType} dispatched ${actionCounts[actionType]} times in ${timeWindow}ms`
    );
    console.error("Action counts:", actionCounts);

    // Optionally throw error to break the loop
    // throw new Error(`Infinite loop detected for action: ${actionType}`);
  }
};

// Enhanced action logger with loop detection
export const enhancedActionLogger =
  (store: any) => (next: any) => (action: any) => {
    const timestamp = new Date().toISOString();

    // Detect potential infinite loops
    detectInfiniteLoop(action.type);

    console.log(`🚀 Redux Action: ${action.type}`, {
      timestamp,
      payload: action.payload,
      meta: action.meta,
    });

    const result = next(action);

    // Log state after action
    const state = store.getState();
    console.log(`📊 State after ${action.type}:`, {
      player: {
        profile: state.player?.profile?.player_id,
        isLoading: state.player?.isLoading,
      },
      character: {
        charactersCount: state.character?.characters?.length || 0,
        creationInProgress: state.character?.creationInProgress,
        error: state.character?.error,
      },
      auth: {
        isAuthenticated: state.auth?.isAuthenticated,
        userId: state.auth?.user?.user_id,
      },
    });

    return result;
  };
