import { defineConfig, devices } from '@playwright/test';

/**
 * Visual Regression Testing Configuration for TherapeuticGoalsSelector
 * This configuration is specifically designed for visual regression testing
 * of Storybook stories with consistent screenshot comparison.
 */
export default defineConfig({
  testDir: './tests/visual-regression',
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only for flaky visual tests
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests on CI for consistent screenshots
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter configuration for visual regression
  reporter: [
    ['html', { outputFolder: 'visual-regression-report' }],
    ['json', { outputFile: 'visual-regression-results/results.json' }],
  ],

  // Global test configuration
  use: {
    // Base URL for Storybook
    baseURL: 'http://localhost:6007',
    
    // Collect trace on failure for debugging
    trace: 'on-first-retry',
    
    // Take screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video recording for debugging
    video: 'retain-on-failure',
    
    // Configure for consistent visual testing
    viewport: { width: 1200, height: 800 },
    
    // Ignore HTTPS errors for local development
    ignoreHTTPSErrors: true,
    
    // Set user agent for consistency
    userAgent: 'Visual-Regression-Test-Agent',
  },

  // Configure expect for visual comparisons
  expect: {
    // Threshold for visual comparisons (0.2 = 20% difference allowed)
    toHaveScreenshot: { 
      threshold: 0.2,
      maxDiffPixels: 1000,
      animations: 'disabled',
      caret: 'hide',
      scale: 'css',
      mode: 'css',
    },
    
    // Timeout for expect assertions
    timeout: 10000,
  },

  // Test projects for different viewports and browsers
  projects: [
    {
      name: 'Desktop Chrome',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1200, height: 800 },
      },
    },
    
    {
      name: 'Desktop Firefox',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1200, height: 800 },
      },
    },
    
    {
      name: 'Desktop Safari',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1200, height: 800 },
      },
    },
    
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
      },
    },
    
    {
      name: 'Mobile Safari',
      use: { 
        ...devices['iPhone 12'],
      },
    },
    
    {
      name: 'Tablet',
      use: { 
        ...devices['iPad Pro'],
      },
    },
  ],

  // Output directory for test artifacts
  outputDir: 'visual-regression-results/',
  
  // Test timeout
  timeout: 30 * 1000,
  
  // Global setup and teardown
  globalSetup: require.resolve('./tests/visual-regression/global-setup.ts'),
  
  // Web server configuration for Storybook
  webServer: {
    command: 'npm run storybook',
    url: 'http://localhost:6007',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
