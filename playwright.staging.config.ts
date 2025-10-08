import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for TTA Staging Environment
 *
 * This configuration is specifically designed for validating the staging
 * environment with real systems (Redis, Neo4j, PostgreSQL) and OAuth flow.
 *
 * Staging Environment:
 * - Frontend: http://localhost:3001
 * - API: http://localhost:8081
 * - Redis: localhost:6380
 * - Neo4j: localhost:7688
 * - PostgreSQL: localhost:5433
 */
export default defineConfig({
  testDir: './tests/e2e-staging',

  // Test file patterns
  testMatch: ['**/*.staging.spec.ts'],

  // Run tests sequentially for staging validation
  fullyParallel: false,

  // Fail fast on CI
  forbidOnly: !!process.env.CI,

  // Retry failed tests once in staging
  retries: process.env.CI ? 2 : 1,

  // Single worker for staging to avoid conflicts
  workers: 1,

  // Comprehensive reporting
  reporter: [
    ['html', { outputFolder: 'playwright-staging-report', open: 'never' }],
    ['json', { outputFile: 'test-results-staging/results.json' }],
    ['junit', { outputFile: 'test-results-staging/results.xml' }],
    ['list'],
  ],

  // Global test configuration
  use: {
    // Staging base URL
    baseURL: process.env.STAGING_BASE_URL || 'http://localhost:3001',

    // Trace on first retry for debugging
    trace: 'on-first-retry',

    // Screenshots on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'retain-on-failure',

    // Longer timeouts for staging (real systems)
    actionTimeout: 15000,
    navigationTimeout: 30000,

    // Ignore HTTPS errors for local staging
    ignoreHTTPSErrors: true,

    // Viewport
    viewport: { width: 1280, height: 720 },

    // User agent
    userAgent: 'TTA-Staging-Validation-Agent',
  },

  // Test timeout (5 minutes for complete user journey)
  timeout: 5 * 60 * 1000,

  // Expect timeout
  expect: {
    timeout: 10000,
  },

  // Output directory
  outputDir: 'test-results-staging/',

  // Global setup and teardown
  globalSetup: require.resolve('./tests/e2e-staging/global-setup.ts'),
  globalTeardown: require.resolve('./tests/e2e-staging/global-teardown.ts'),

  // Projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Enable permissions for OAuth
        permissions: ['clipboard-read', 'clipboard-write'],
      },
    },

    // Uncomment for cross-browser testing
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    // Mobile testing
    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 5'],
        permissions: ['clipboard-read', 'clipboard-write'],
      },
    },
  ],

  // Web server configuration (optional - assumes staging is already running)
  // Uncomment if you want Playwright to start staging automatically
  // webServer: {
  //   command: 'docker-compose -f docker-compose.staging-homelab.yml up',
  //   url: 'http://localhost:3001',
  //   reuseExistingServer: true,
  //   timeout: 120 * 1000,
  // },
});
