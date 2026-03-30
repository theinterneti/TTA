// Logseq: [[TTA.dev/Tests/E2e-staging/Helpers/Staging-config]]
/**
 * Centralized Configuration for Staging E2E Tests
 *
 * This file provides a single source of truth for all staging environment
 * configuration, making it easy to update URLs, timeouts, and test data.
 */

export const STAGING_CONFIG = {
  // Environment URLs
  frontend: {
    url: process.env.STAGING_BASE_URL || 'http://localhost:3001',
    timeout: 30000,
  },
  api: {
    url: process.env.STAGING_API_URL || 'http://localhost:8081',
    timeout: 15000,
  },

  // Database connections
  databases: {
    redis: {
      url: process.env.REDIS_URL || 'redis://localhost:6380',
      host: 'localhost',
      port: 6380,
    },
    neo4j: {
      uri: process.env.NEO4J_URI || 'bolt://localhost:7688',
      host: 'localhost',
      port: 7688,
    },
    postgresql: {
      url: process.env.DATABASE_URL || 'postgresql://localhost:5433/tta_staging',
      host: 'localhost',
      port: 5433,
    },
  },

  // OAuth configuration
  oauth: {
    useMock: process.env.USE_MOCK_OAUTH !== 'false',
    clientId: process.env.OPENROUTER_CLIENT_ID || '',
    redirectUri: process.env.OPENROUTER_REDIRECT_URI || 'http://localhost:3001/auth/callback',
  },

  // Test timeouts
  timeouts: {
    short: 5000,
    medium: 10000,
    long: 30000,
    veryLong: 60000,
    aiResponse: 20000,
  },

  // Test data
  testUsers: {
    demo: {
      username: 'demo_user',
      password: 'DemoPassword123!',
      email: 'demo@test.tta',
    },
    staging: {
      username: 'staging_test_user',
      password: 'StagingPassword123!',
      email: 'staging@test.tta',
    },
  },

  // Test characters
  testCharacters: {
    default: {
      name: 'Aria Stormwind',
      appearance: {
        description: 'A brave adventurer with flowing silver hair and piercing blue eyes.',
      },
      background: {
        story: 'A wanderer seeking peace and understanding through collaborative storytelling.',
        personality_traits: ['brave', 'compassionate', 'curious'],
        goals: ['find inner peace', 'help others', 'explore new worlds'],
      },
      therapeutic_profile: {
        comfort_level: 7,
        preferred_intensity: 'MEDIUM',
        therapeutic_goals: ['emotional awareness', 'social connection'],
      },
    },
  },

  // Performance budgets
  performance: {
    pageLoad: 3000, // 3 seconds
    apiResponse: 1000, // 1 second
    aiResponse: 15000, // 15 seconds
    navigation: 2000, // 2 seconds
  },

  // Feature flags
  features: {
    enableAccessibilityTests: true,
    enablePerformanceTests: true,
    enableCrossBrowserTests: true,
    enableMobileTests: true,
  },
};

/**
 * Get the full URL for a frontend route
 */
export function getFrontendUrl(path: string = ''): string {
  const baseUrl = STAGING_CONFIG.frontend.url;
  return path ? `${baseUrl}${path.startsWith('/') ? path : `/${path}`}` : baseUrl;
}

/**
 * Get the full URL for an API endpoint
 */
export function getApiUrl(endpoint: string = ''): string {
  const baseUrl = STAGING_CONFIG.api.url;
  return endpoint ? `${baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}` : baseUrl;
}

/**
 * Check if we're running in CI environment
 */
export function isCI(): boolean {
  return !!process.env.CI;
}

/**
 * Get retry count based on environment
 */
export function getRetryCount(): number {
  return isCI() ? 2 : 1;
}

/**
 * Get worker count based on environment
 */
export function getWorkerCount(): number {
  return isCI() ? 1 : 1; // Always 1 for staging to avoid conflicts
}
