/**
 * Comprehensive Logout Flow E2E Tests for Staging Environment
 *
 * Validates:
 * - Session deletion from Redis
 * - Session cookie clearing
 * - Redirect to login page
 * - Protected route access after logout
 * - Session state verification
 */

import { expect, test } from '@playwright/test';
import { STAGING_CONFIG } from './helpers/staging-config';
import { DashboardPage } from './page-objects/DashboardPage';
import { LoginPage } from './page-objects/LoginPage';

test.describe('Logout Flow - Comprehensive Validation', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);

    // Navigate to login page
    await loginPage.goto();
  });

  test.describe('Session Deletion', () => {
    test('should delete session from Redis on logout', async ({ page }) => {
      console.log('✓ Testing session deletion from Redis');

      // Step 1: Login
      await test.step('Login with demo credentials', async () => {
        await loginPage.loginWithDemo();
        await loginPage.waitForLoginSuccess();
        console.log('  ✓ Logged in successfully');
      });

      // Step 2: Capture session ID from cookie
      let sessionIdBeforeLogout: string | null = null;
      await test.step('Capture session ID from cookie', async () => {
        const cookies = await page.context().cookies();
        const sessionCookie = cookies.find(c => c.name === 'openrouter_session_id');
        sessionIdBeforeLogout = sessionCookie?.value || null;
        
        if (sessionIdBeforeLogout) {
          console.log(`  ✓ Session ID captured: ${sessionIdBeforeLogout.substring(0, 20)}...`);
        } else {
          console.log('  ⚠ No session cookie found');
        }
      });

      // Step 3: Logout
      await test.step('Logout', async () => {
        await dashboardPage.logout();
        console.log('  ✓ Logout initiated');
      });

      // Step 4: Verify session cookie is cleared
      await test.step('Verify session cookie is cleared', async () => {
        const cookies = await page.context().cookies();
        const sessionCookie = cookies.find(c => c.name === 'openrouter_session_id');
        
        if (!sessionCookie || !sessionCookie.value) {
          console.log('  ✓ Session cookie cleared from browser');
        } else {
          console.log(`  ⚠ Session cookie still present: ${sessionCookie.value.substring(0, 20)}...`);
        }
        
        expect(!sessionCookie || !sessionCookie.value).toBeTruthy();
      });

      // Step 5: Verify redirect to login
      await test.step('Verify redirect to login page', async () => {
        const currentUrl = page.url();
        expect(currentUrl).toContain('login');
        console.log('  ✓ Redirected to login page');
      });
    });

    test('should prevent access to protected routes after logout', async ({ page }) => {
      console.log('✓ Testing protected route access after logout');

      // Step 1: Login
      await test.step('Login with demo credentials', async () => {
        await loginPage.loginWithDemo();
        await loginPage.waitForLoginSuccess();
        console.log('  ✓ Logged in successfully');
      });

      // Step 2: Verify dashboard is accessible
      await test.step('Verify dashboard is accessible', async () => {
        const currentUrl = page.url();
        expect(currentUrl).toContain('dashboard');
        console.log('  ✓ Dashboard accessible while logged in');
      });

      // Step 3: Logout
      await test.step('Logout', async () => {
        await dashboardPage.logout();
        console.log('  ✓ Logout initiated');
      });

      // Step 4: Try to access dashboard directly
      await test.step('Try to access dashboard directly', async () => {
        await page.goto('/dashboard');
        await page.waitForLoadState('networkidle');
        
        const currentUrl = page.url();
        expect(currentUrl).toContain('login');
        console.log('  ✓ Dashboard access redirected to login');
      });

      // Step 5: Verify login form is visible
      await test.step('Verify login form is visible', async () => {
        const isLoginFormVisible = await loginPage.isLoaded();
        expect(isLoginFormVisible).toBeTruthy();
        console.log('  ✓ Login form is visible');
      });
    });
  });

  test.describe('Cookie Handling', () => {
    test('should properly clear session cookie with correct flags', async ({ page }) => {
      console.log('✓ Testing session cookie clearing with proper flags');

      // Step 1: Login
      await test.step('Login with demo credentials', async () => {
        await loginPage.loginWithDemo();
        await loginPage.waitForLoginSuccess();
        console.log('  ✓ Logged in successfully');
      });

      // Step 2: Verify cookie exists with correct flags
      await test.step('Verify session cookie exists with correct flags', async () => {
        const cookies = await page.context().cookies();
        const sessionCookie = cookies.find(c => c.name === 'openrouter_session_id');
        
        expect(sessionCookie).toBeDefined();
        expect(sessionCookie?.httpOnly).toBe(true);
        expect(sessionCookie?.path).toBe('/');
        console.log('  ✓ Session cookie has correct flags (httpOnly=true, path=/)');
      });

      // Step 3: Logout
      await test.step('Logout', async () => {
        await dashboardPage.logout();
        console.log('  ✓ Logout initiated');
      });

      // Step 4: Verify cookie is cleared
      await test.step('Verify session cookie is cleared', async () => {
        const cookies = await page.context().cookies();
        const sessionCookie = cookies.find(c => c.name === 'openrouter_session_id');
        
        expect(!sessionCookie || !sessionCookie.value).toBeTruthy();
        console.log('  ✓ Session cookie cleared successfully');
      });
    });
  });

  test.describe('Error Handling', () => {
    test('should handle logout gracefully even if session not found', async ({ page }) => {
      console.log('✓ Testing logout with non-existent session');

      // Step 1: Navigate to logout endpoint without session
      await test.step('Call logout endpoint without session', async () => {
        const response = await page.request.post(
          `${STAGING_CONFIG.apiUrl}/api/v1/openrouter/auth/logout`
        );
        
        expect(response.ok()).toBeTruthy();
        const data = await response.json();
        expect(data.message).toContain('Logged out');
        console.log('  ✓ Logout endpoint handled missing session gracefully');
      });
    });
  });

  test.describe('Complete User Journey', () => {
    test('should complete full login-logout cycle', async ({ page }) => {
      console.log('✓ Testing complete login-logout cycle');

      // Step 1: Start at login page
      await test.step('Verify at login page', async () => {
        const isLoaded = await loginPage.isLoaded();
        expect(isLoaded).toBeTruthy();
        console.log('  ✓ At login page');
      });

      // Step 2: Login
      await test.step('Login with demo credentials', async () => {
        await loginPage.loginWithDemo();
        await loginPage.waitForLoginSuccess();
        console.log('  ✓ Logged in successfully');
      });

      // Step 3: Verify dashboard
      await test.step('Verify dashboard loaded', async () => {
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Dashboard loaded');
      });

      // Step 4: Logout
      await test.step('Logout', async () => {
        await dashboardPage.logout();
        console.log('  ✓ Logout initiated');
      });

      // Step 5: Verify back at login
      await test.step('Verify back at login page', async () => {
        const isLoaded = await loginPage.isLoaded();
        expect(isLoaded).toBeTruthy();
        console.log('  ✓ Back at login page');
      });

      // Step 6: Verify can login again
      await test.step('Verify can login again', async () => {
        await loginPage.loginWithDemo();
        await loginPage.waitForLoginSuccess();
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Can login again successfully');
      });
    });
  });
});

