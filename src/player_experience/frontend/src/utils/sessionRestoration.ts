/**
 * Session Restoration Utility
 * 
 * Handles restoration of user session state after page refresh or navigation.
 * Integrates with secure storage and Redux store to maintain application state.
 */

import { store } from '../store/store';
import secureStorage, { sessionManager } from './secureStorage';
import { setUser } from '../store/slices/authSlice';
import { loadConversationHistory, setCurrentSession } from '../store/slices/chatSlice';
import { authAPI, conversationAPI } from '../services/api';

interface SessionRestorationResult {
  success: boolean;
  restored: {
    auth: boolean;
    session: boolean;
    conversation: boolean;
  };
  errors: string[];
}

/**
 * Restore complete application session
 */
export async function restoreSession(): Promise<SessionRestorationResult> {
  const result: SessionRestorationResult = {
    success: false,
    restored: {
      auth: false,
      session: false,
      conversation: false,
    },
    errors: [],
  };

  try {
    // Step 1: Restore authentication
    const authRestored = await restoreAuthentication();
    result.restored.auth = authRestored;

    if (!authRestored) {
      result.errors.push('Authentication could not be restored');
      return result;
    }

    // Step 2: Restore session data
    const sessionRestored = await restoreSessionData();
    result.restored.session = sessionRestored;

    // Step 3: Restore conversation if session exists
    if (sessionRestored) {
      const conversationRestored = await restoreConversation();
      result.restored.conversation = conversationRestored;
    }

    result.success = result.restored.auth && result.restored.session;
    
  } catch (error) {
    console.error('Session restoration failed:', error);
    result.errors.push(error instanceof Error ? error.message : 'Unknown error');
  }

  return result;
}

/**
 * Restore authentication state
 */
async function restoreAuthentication(): Promise<boolean> {
  try {
    // Check if we have a valid token
    const token = secureStorage.getToken();
    
    if (!token) {
      console.info('No token found, user needs to log in');
      return false;
    }

    // Verify token with backend
    try {
      const response = await authAPI.verifyToken(token);
      
      if (response && response.user) {
        // Update Redux store with user info
        store.dispatch(setUser(response.user));
        console.info('Authentication restored successfully');
        return true;
      }
    } catch (error) {
      console.warn('Token verification failed:', error);
      
      // Try to refresh token
      try {
        const refreshResponse = await authAPI.refreshToken();
        
        if (refreshResponse && refreshResponse.access_token) {
          secureStorage.setToken(
            refreshResponse.access_token,
            refreshResponse.expires_in || 3600
          );
          
          if (refreshResponse.user) {
            store.dispatch(setUser(refreshResponse.user));
          }
          
          console.info('Token refreshed successfully');
          return true;
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
      }
    }

    // Clear invalid token
    secureStorage.clearToken();
    return false;
    
  } catch (error) {
    console.error('Authentication restoration error:', error);
    return false;
  }
}

/**
 * Restore session data from sessionStorage
 */
async function restoreSessionData(): Promise<boolean> {
  try {
    const session = sessionManager.getSession();
    
    if (!session) {
      console.info('No session data found');
      return false;
    }

    console.info('Session data restored:', {
      sessionId: session.sessionId,
      userId: session.userId,
    });

    return true;
    
  } catch (error) {
    console.error('Session data restoration error:', error);
    return false;
  }
}

/**
 * Restore conversation history for active session
 */
async function restoreConversation(): Promise<boolean> {
  try {
    const session = sessionManager.getSession();
    
    if (!session || !session.sessionId) {
      return false;
    }

    // Get current chat state
    const state = store.getState();
    const currentSession = state.chat?.currentSession;

    // If we have a current session, load its history
    const sessionId = currentSession?.session_id || session.sessionId;

    try {
      // Dispatch async action to load conversation history
      await store.dispatch(loadConversationHistory({ sessionId, limit: 100 })).unwrap();
      
      console.info('Conversation history restored for session:', sessionId);
      return true;
      
    } catch (error) {
      console.warn('Failed to load conversation history:', error);
      // Not a critical error - user can continue without history
      return false;
    }
    
  } catch (error) {
    console.error('Conversation restoration error:', error);
    return false;
  }
}

/**
 * Save current session state before navigation/refresh
 */
export function saveSessionState(): void {
  try {
    const state = store.getState();
    
    // Update session activity
    sessionManager.updateLastActivity();

    // Save current session ID if exists
    if (state.chat?.currentSession) {
      const session = sessionManager.getSession();
      if (session) {
        sessionManager.setSession({
          ...session,
          sessionId: state.chat.currentSession.session_id,
        });
      }
    }

    console.info('Session state saved');
    
  } catch (error) {
    console.error('Failed to save session state:', error);
  }
}

/**
 * Clear all session data
 */
export function clearSessionState(): void {
  try {
    secureStorage.clearToken();
    sessionManager.clearSession();
    console.info('Session state cleared');
  } catch (error) {
    console.error('Failed to clear session state:', error);
  }
}

/**
 * Initialize session restoration on app load
 */
export function initializeSessionRestoration(): void {
  // Restore session on app load
  restoreSession().then((result) => {
    if (result.success) {
      console.info('Session restored successfully:', result.restored);
    } else {
      console.info('Session restoration incomplete:', result.restored, result.errors);
    }
  });

  // Save session state before page unload
  window.addEventListener('beforeunload', () => {
    saveSessionState();
  });

  // Save session state on visibility change (mobile/tab switching)
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      saveSessionState();
    }
  });

  // Periodic session state save (every 30 seconds)
  setInterval(() => {
    saveSessionState();
  }, 30000);
}

