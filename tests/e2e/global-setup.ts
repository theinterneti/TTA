// Logseq: [[TTA.dev/Tests/E2e/Global-setup]]
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup for TTA E2E tests...');

  // Launch browser for setup
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Wait for the application to be ready
    console.log('⏳ Waiting for application to be ready...');
    await page.goto(config.projects[0].use.baseURL || 'http://localhost:3000');

    // Wait for the app to load (look for the login form or authenticated state)
    // Use flexible selectors that work with actual DOM structure
    await page.waitForSelector('input[name="username"], input[type="text"][placeholder*="Username"], [data-testid="dashboard"]', {
      timeout: 60000
    });

    console.log('✅ Application is ready for testing');

    // Create test user session if needed
    await setupTestUser(page);

  } catch (error) {
    console.error('❌ Global setup failed:', error);
    console.error('Error details:', error.message);
    throw error;
  } finally {
    await context.close();
    await browser.close();
  }
}

async function setupTestUser(page: any) {
  try {
    // Check if we're on login page by looking for username input
    const usernameInput = await page.locator('input[name="username"]').count();

    if (usernameInput > 0) {
      console.log('🔐 Setting up test user authentication...');

      // Login with test credentials
      await page.fill('input[name="username"]', 'testuser');
      await page.fill('input[name="password"]', 'testpass');
      await page.click('button[type="submit"]');

      // Wait for successful login - look for dashboard or main content
      await page.waitForSelector('nav, [role="navigation"], main', { timeout: 10000 });

      // Save authentication state
      await page.context().storageState({ path: 'tests/e2e/auth-state.json' });

      console.log('✅ Test user authentication setup complete');
    }
  } catch (error) {
    console.log('ℹ️ Test user setup skipped (may not be needed):', error.message);
  }
}

export default globalSetup;
