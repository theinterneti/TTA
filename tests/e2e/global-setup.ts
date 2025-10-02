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
    await page.waitForSelector('[data-testid="login-form"], [data-testid="dashboard"]', { 
      timeout: 60000 
    });
    
    console.log('✅ Application is ready for testing');

    // Create test user session if needed
    await setupTestUser(page);
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await context.close();
    await browser.close();
  }
}

async function setupTestUser(page: any) {
  try {
    // Check if we're on login page
    const loginForm = await page.locator('[data-testid="login-form"]').count();
    
    if (loginForm > 0) {
      console.log('🔐 Setting up test user authentication...');
      
      // Login with test credentials
      await page.fill('input[name="username"]', 'testuser');
      await page.fill('input[name="password"]', 'testpass');
      await page.click('button[type="submit"]');
      
      // Wait for successful login
      await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });
      
      // Save authentication state
      await page.context().storageState({ path: 'tests/e2e/auth-state.json' });
      
      console.log('✅ Test user authentication setup complete');
    }
  } catch (error) {
    console.log('ℹ️ Test user setup skipped (may not be needed):', error.message);
  }
}

export default globalSetup;
