/**
 * Comprehensive TTA Web Application Validation Tests
 * 
 * Tests all critical fixes and improvements:
 * - Character creation (no 422 errors)
 * - Authentication & session persistence
 * - Therapeutic AI chat system
 * - Error handling
 * - Overall system stability
 */

import { test, expect, Page } from '@playwright/test';

// Test configuration
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

// Test credentials
const TEST_USER = {
  username: 'test_user_validation',
  password: 'TestPassword123!',
  email: 'validation@test.com'
};

// Helper function to wait for network idle
async function waitForNetworkIdle(page: Page, timeout = 2000) {
  await page.waitForLoadState('networkidle', { timeout });
}

// Helper function to take screenshot on failure
async function captureOnFailure(page: Page, testName: string) {
  try {
    await page.screenshot({ 
      path: `test-results/failure-${testName}-${Date.now()}.png`,
      fullPage: true 
    });
  } catch (error) {
    console.error('Failed to capture screenshot:', error);
  }
}

test.describe('TTA Comprehensive Validation Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Set longer timeout for complex operations
    test.setTimeout(120000);
    
    // Navigate to application
    await page.goto(BASE_URL);
    await waitForNetworkIdle(page);
  });

  test.describe('1. Authentication & Session Persistence', () => {
    
    test('should login successfully and store token securely', async ({ page }) => {
      console.log('Testing login flow...');
      
      // Navigate to login page
      await page.goto(`${BASE_URL}/login`);
      await waitForNetworkIdle(page);
      
      // Fill in login form
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      
      // Submit login
      await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
      
      // Wait for navigation or success indicator
      await page.waitForTimeout(2000);
      
      // Verify we're logged in (check for dashboard or user menu)
      const isLoggedIn = await page.locator('text=/dashboard|profile|logout/i').first().isVisible()
        .catch(() => false);
      
      if (!isLoggedIn) {
        await captureOnFailure(page, 'login-failed');
      }
      
      expect(isLoggedIn).toBeTruthy();
      
      // Verify token is NOT in localStorage (should be in memory)
      const localStorageToken = await page.evaluate(() => {
        return localStorage.getItem('token') || localStorage.getItem('access_token');
      });
      
      expect(localStorageToken).toBeNull();
      console.log('✅ Token not in localStorage (secure storage confirmed)');
    });

    test('should persist session across page refresh', async ({ page }) => {
      console.log('Testing session persistence...');
      
      // Login first
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(2000);
      
      // Refresh the page
      await page.reload();
      await waitForNetworkIdle(page);
      
      // Verify still logged in
      const isStillLoggedIn = await page.locator('text=/dashboard|profile|logout/i').first().isVisible()
        .catch(() => false);
      
      expect(isStillLoggedIn).toBeTruthy();
      console.log('✅ Session persisted across page refresh');
    });

    test('should logout and clear session properly', async ({ page }) => {
      console.log('Testing logout flow...');
      
      // Login first
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(2000);
      
      // Logout
      await page.click('button:has-text("Logout"), a:has-text("Logout"), [aria-label="Logout"]');
      await page.waitForTimeout(1000);
      
      // Verify redirected to login
      const isOnLoginPage = await page.locator('input[type="password"]').isVisible()
        .catch(() => false);
      
      expect(isOnLoginPage).toBeTruthy();
      console.log('✅ Logout successful');
    });
  });

  test.describe('2. Character Creation Flow', () => {
    
    test.beforeEach(async ({ page }) => {
      // Login before character creation tests
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(2000);
    });

    test('should create character without 422 errors', async ({ page }) => {
      console.log('Testing character creation...');
      
      // Navigate to character creation
      await page.goto(`${BASE_URL}/characters/create`);
      await waitForNetworkIdle(page);
      
      // Fill in character name
      const characterName = `TestChar_${Date.now()}`;
      await page.fill('input[name="name"], input[placeholder*="name" i]', characterName);
      
      // Fill in appearance fields
      await page.selectOption('select[name="age_range"], select:has(option:has-text("adult"))', 'adult');
      await page.fill('textarea[name="physical_description"], textarea[placeholder*="appearance" i]', 
        'A brave character with kind eyes');
      
      // Fill in personality traits (array field)
      const traitsInput = page.locator('input[name="personality_traits"], input[placeholder*="trait" i]').first();
      if (await traitsInput.isVisible()) {
        await traitsInput.fill('brave');
        await page.keyboard.press('Enter');
        await traitsInput.fill('compassionate');
        await page.keyboard.press('Enter');
      }
      
      // Fill in backstory
      await page.fill('textarea[name="backstory"], textarea[placeholder*="story" i]', 
        'A character on a journey of self-discovery');
      
      // Fill in therapeutic profile
      await page.fill('input[name="primary_concerns"], input[placeholder*="concern" i]', 'anxiety');
      await page.keyboard.press('Enter');
      
      // Submit form
      const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Submit")');
      await submitButton.click();
      
      // Wait for response
      await page.waitForTimeout(3000);
      
      // Check for success (no 422 error)
      const hasError = await page.locator('text=/422|unprocessable|validation error/i').isVisible()
        .catch(() => false);
      
      if (hasError) {
        await captureOnFailure(page, 'character-creation-422-error');
        const errorText = await page.locator('text=/error/i').first().textContent();
        console.error('Character creation error:', errorText);
      }
      
      expect(hasError).toBeFalsy();
      
      // Verify success message or redirect
      const hasSuccess = await page.locator('text=/success|created|character/i').isVisible({ timeout: 5000 })
        .catch(() => false);
      
      expect(hasSuccess).toBeTruthy();
      console.log('✅ Character created successfully without 422 errors');
    });

    test('should display validation errors for invalid input', async ({ page }) => {
      console.log('Testing character creation validation...');
      
      await page.goto(`${BASE_URL}/characters/create`);
      await waitForNetworkIdle(page);
      
      // Try to submit empty form
      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();
      
      // Should show validation errors
      const hasValidationError = await page.locator('text=/required|invalid|must/i').isVisible({ timeout: 2000 })
        .catch(() => false);
      
      expect(hasValidationError).toBeTruthy();
      console.log('✅ Validation errors displayed correctly');
    });
  });

  test.describe('3. Therapeutic AI Chat System', () => {
    
    test.beforeEach(async ({ page }) => {
      // Login before chat tests
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"], input[type="text"]', TEST_USER.username);
      await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(2000);
    });

    test('should send message and receive AI response (not echo)', async ({ page }) => {
      console.log('Testing therapeutic AI chat...');
      
      // Navigate to chat
      await page.goto(`${BASE_URL}/chat`);
      await waitForNetworkIdle(page);
      
      // Wait for WebSocket connection
      await page.waitForTimeout(2000);
      
      // Send a test message
      const testMessage = `Hello, I'm feeling anxious today. ${Date.now()}`;
      const messageInput = page.locator('input[type="text"], textarea').last();
      await messageInput.fill(testMessage);
      
      const sendButton = page.locator('button:has-text("Send"), button[type="submit"]').last();
      await sendButton.click();
      
      // Wait for AI response
      await page.waitForTimeout(5000);
      
      // Check that response is NOT just an echo
      const messages = await page.locator('[class*="message"], [class*="chat"]').allTextContents();
      const hasNonEchoResponse = messages.some(msg => 
        msg.length > 0 && 
        msg !== testMessage &&
        !msg.includes('echo') &&
        msg.length > 20 // AI responses should be substantial
      );
      
      if (!hasNonEchoResponse) {
        await captureOnFailure(page, 'ai-response-echo-only');
      }
      
      expect(hasNonEchoResponse).toBeTruthy();
      console.log('✅ AI response received (not echo)');
    });

    test('should show progressive feedback during AI processing', async ({ page }) => {
      console.log('Testing progressive feedback...');
      
      await page.goto(`${BASE_URL}/chat`);
      await page.waitForTimeout(2000);
      
      // Send message
      const messageInput = page.locator('input[type="text"], textarea').last();
      await messageInput.fill('Tell me about coping strategies');
      
      const sendButton = page.locator('button:has-text("Send")').last();
      await sendButton.click();
      
      // Check for typing indicator or loading state
      const hasProgressIndicator = await page.locator('text=/typing|processing|thinking|analyzing/i, [class*="loading"], [class*="typing"]')
        .isVisible({ timeout: 2000 })
        .catch(() => false);
      
      expect(hasProgressIndicator).toBeTruthy();
      console.log('✅ Progressive feedback indicators working');
    });
  });

  test.describe('4. Error Handling', () => {
    
    test('should display user-friendly error messages', async ({ page }) => {
      console.log('Testing error handling...');
      
      // Try to access protected route without auth
      await page.goto(`${BASE_URL}/characters`);
      await waitForNetworkIdle(page);
      
      // Should show friendly error or redirect to login
      const hasObjectError = await page.locator('text="[object Object]"').isVisible({ timeout: 1000 })
        .catch(() => false);
      
      expect(hasObjectError).toBeFalsy();
      console.log('✅ No "[object Object]" error displays');
    });

    test('should handle network errors gracefully', async ({ page }) => {
      console.log('Testing network error handling...');
      
      // Simulate offline
      await page.context().setOffline(true);
      
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', TEST_USER.username);
      await page.fill('input[name="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      
      await page.waitForTimeout(2000);
      
      // Should show network error message
      const hasNetworkError = await page.locator('text=/network|connection|offline/i').isVisible({ timeout: 2000 })
        .catch(() => false);
      
      // Restore online
      await page.context().setOffline(false);
      
      expect(hasNetworkError).toBeTruthy();
      console.log('✅ Network errors handled gracefully');
    });
  });

  test.describe('5. Overall System Stability', () => {
    
    test('should complete full user journey without errors', async ({ page }) => {
      console.log('Testing complete user journey...');
      
      // Monitor console errors
      const consoleErrors: string[] = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });
      
      // 1. Login
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="username"]', TEST_USER.username);
      await page.fill('input[name="password"]', TEST_USER.password);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(2000);
      
      // 2. Navigate to dashboard
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForNetworkIdle(page);
      
      // 3. View characters
      await page.goto(`${BASE_URL}/characters`);
      await waitForNetworkIdle(page);
      
      // 4. Navigate to chat
      await page.goto(`${BASE_URL}/chat`);
      await waitForNetworkIdle(page);
      
      // Check for critical console errors
      const criticalErrors = consoleErrors.filter(err => 
        !err.includes('Warning') && 
        !err.includes('DevTools') &&
        !err.includes('favicon')
      );
      
      if (criticalErrors.length > 0) {
        console.error('Console errors detected:', criticalErrors);
      }
      
      expect(criticalErrors.length).toBe(0);
      console.log('✅ Complete user journey successful without critical errors');
    });
  });
});

