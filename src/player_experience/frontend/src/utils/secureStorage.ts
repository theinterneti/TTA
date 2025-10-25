/**
 * Secure token storage utility
 *
 * Implements secure token storage using httpOnly cookies (server-side) and
 * in-memory storage (client-side) instead of localStorage to prevent XSS attacks.
 *
 * Security considerations:
 * - Tokens are never stored in localStorage (vulnerable to XSS)
 * - Access tokens stored in memory (cleared on page refresh)
 * - Refresh tokens handled via httpOnly cookies (server-side only)
 * - Session persistence via secure server-side session management
 */

interface TokenData {
  accessToken: string;
  expiresAt: number;
  refreshToken?: string; // Only for reference, actual refresh token in httpOnly cookie
}

class SecureStorage {
  private tokenData: TokenData | null = null;
  private refreshTimer: NodeJS.Timeout | null = null;
  private readonly TOKEN_REFRESH_BUFFER = 5 * 60 * 1000; // Refresh 5 minutes before expiry

  /**
   * Store access token in memory
   */
  setToken(accessToken: string, expiresIn: number = 3600): void {
    const expiresAt = Date.now() + (expiresIn * 1000);

    this.tokenData = {
      accessToken,
      expiresAt,
    };

    // Schedule automatic token refresh
    this.scheduleTokenRefresh(expiresAt);
  }

  /**
   * Get current access token
   */
  getToken(): string | null {
    if (!this.tokenData) {
      return null;
    }

    // Check if token is expired
    if (Date.now() >= this.tokenData.expiresAt) {
      this.clearToken();
      return null;
    }

    return this.tokenData.accessToken;
  }

  /**
   * Check if token exists and is valid
   */
  hasValidToken(): boolean {
    return this.getToken() !== null;
  }

  /**
   * Clear token from memory
   */
  clearToken(): void {
    this.tokenData = null;

    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  /**
   * Schedule automatic token refresh
   */
  private scheduleTokenRefresh(expiresAt: number): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
    }

    const refreshTime = expiresAt - Date.now() - this.TOKEN_REFRESH_BUFFER;

    if (refreshTime > 0) {
      this.refreshTimer = setTimeout(() => {
        this.triggerTokenRefresh();
      }, refreshTime);
    }
  }

  /**
   * Trigger token refresh callback
   * This should be connected to the auth slice's refresh action
   */
  private async triggerTokenRefresh(): Promise<void> {
    try {
      // Dispatch refresh token action
      // This will be implemented in the auth slice
      const event = new CustomEvent('token-refresh-needed');
      window.dispatchEvent(event);
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearToken();
    }
  }

  /**
   * Get time until token expiry (in milliseconds)
   */
  getTimeUntilExpiry(): number | null {
    if (!this.tokenData) {
      return null;
    }

    return Math.max(0, this.tokenData.expiresAt - Date.now());
  }

  /**
   * Check if token needs refresh soon
   */
  needsRefresh(): boolean {
    const timeUntilExpiry = this.getTimeUntilExpiry();

    if (timeUntilExpiry === null) {
      return false;
    }

    return timeUntilExpiry < this.TOKEN_REFRESH_BUFFER;
  }
}

// Singleton instance
const secureStorage = new SecureStorage();

export default secureStorage;

/**
 * Session persistence utility
 *
 * Manages session state persistence using sessionStorage for temporary data
 * and server-side session management for critical data.
 */

interface SessionData {
  sessionId: string;
  userId: string;
  lastActivity: number;
}

class SessionManager {
  private readonly SESSION_KEY = 'tta_session_data';
  private readonly SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes

  /**
   * Store session data
   */
  setSession(sessionData: SessionData): void {
    try {
      sessionStorage.setItem(this.SESSION_KEY, JSON.stringify({
        ...sessionData,
        lastActivity: Date.now(),
      }));
    } catch (error) {
      console.error('Failed to store session data:', error);
    }
  }

  /**
   * Get session data
   */
  getSession(): SessionData | null {
    try {
      const data = sessionStorage.getItem(this.SESSION_KEY);

      if (!data) {
        return null;
      }

      const sessionData: SessionData = JSON.parse(data);

      // Check if session has expired
      if (Date.now() - sessionData.lastActivity > this.SESSION_TIMEOUT) {
        this.clearSession();
        return null;
      }

      // Update last activity
      this.updateLastActivity();

      return sessionData;
    } catch (error) {
      console.error('Failed to retrieve session data:', error);
      return null;
    }
  }

  /**
   * Update last activity timestamp
   */
  updateLastActivity(): void {
    const session = this.getSession();

    if (session) {
      session.lastActivity = Date.now();
      sessionStorage.setItem(this.SESSION_KEY, JSON.stringify(session));
    }
  }

  /**
   * Clear session data
   */
  clearSession(): void {
    sessionStorage.removeItem(this.SESSION_KEY);
  }

  /**
   * Check if session is valid
   */
  hasValidSession(): boolean {
    return this.getSession() !== null;
  }
}

export const sessionManager = new SessionManager();

/**
 * Migration utility to move from localStorage to secure storage
 */
export const migrateFromLocalStorage = (): void => {
  try {
    // Check if there's an existing token in localStorage
    const oldToken = localStorage.getItem('token');

    if (oldToken) {
      console.warn('Found token in localStorage. This is insecure and will be migrated.');

      // Store in secure storage (will be cleared on page refresh, requiring re-login)
      // This is intentional for security
      secureStorage.setToken(oldToken);

      // Remove from localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('refreshToken');

      console.info('Token migrated to secure storage. You may need to log in again after page refresh.');
    }
  } catch (error) {
    console.error('Failed to migrate from localStorage:', error);
  }
};

/**
 * Initialize secure storage on app load
 */
export const initializeSecureStorage = (): void => {
  // Migrate any existing localStorage tokens
  migrateFromLocalStorage();

  // Set up token refresh listener
  window.addEventListener('token-refresh-needed', async () => {
    // This will be handled by the auth slice
    console.info('Token refresh needed');
  });

  // Set up activity tracking for session management
  const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart'];

  activityEvents.forEach(event => {
    window.addEventListener(event, () => {
      sessionManager.updateLastActivity();
    }, { passive: true });
  });
};
