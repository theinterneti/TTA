import { defineConfig, devices } from '@playwright/test';

/**
 * Quick validation config without global setup
 */
export default defineConfig({
  testDir: './',
  testMatch: ['quick-validation.spec.ts', 'e2e-validation.spec.ts'],
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: 'list',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },

  outputDir: 'test-results/',
});
