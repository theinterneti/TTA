/**
 * Debug Logout Flow - Detailed Logging and Network Inspection
 *
 * This test provides detailed logging of the logout flow including:
 * - Network request/response inspection
 * - Cookie state before/after logout
 * - Session state verification
 * - Error tracking
 */

import { expect, test } from '@playwright/test';
import { STAGING_CONFIG } from './helpers/staging-config';
import { DashboardPage } from './page-objects/DashboardPage';
import { LoginPage } from './page-objects/LoginPage';

test.describe('Debug: Logout Flow with Detailed Logging', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);

    // Set up network logging
    page.on('request', request => {
      if (request.url().includes('/logout') || request.url().includes('/auth/status')) {
        console.log(`\n📤 REQUEST: ${request.method()} ${request.url()}`);
        console.log(`   Headers: ${JSON.stringify(request.headers(), null, 2)}`);
      }
    });

    page.on('response', async response => {
      if (response.url().includes('/logout') || response.url().includes('/auth/status')) {
        console.log(`\n📥 RESPONSE: ${response.status()} ${response.url()}`);
        console.log(`   Headers: ${JSON.stringify(response.headers(), null, 2)}`);
        try {
          const body = await response.json();
          console.log(`   Body: ${JSON.stringify(body, null, 2)}`);
        } catch (e) {
          console.log('   (Could not parse response body)');
        }
      }
    });

    // Navigate to login page
    await loginPage.goto();
  });

  test('should log detailed logout flow', async ({ page }) => {
    console.log('\n=== LOGOUT DEBUG TEST START ===\n');

    // Step 1: Login
    console.log('📍 STEP 1: Login');
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();
    console.log('✓ Login successful\n');

    // Step 2: Inspect cookies before logout
    console.log('📍 STEP 2: Inspect cookies before logout');
    let cookies = await page.context().cookies();
    console.log(`Total cookies: ${cookies.length}`);
    cookies.forEach(cookie => {
      console.log(`  - ${cookie.name}: ${cookie.value.substring(0, 30)}...`);
      console.log(`    path: ${cookie.path}, domain: ${cookie.domain}, httpOnly: ${cookie.httpOnly}, secure: ${cookie.secure}`);
    });
    const sessionCookieBefore = cookies.find(c => c.name === 'openrouter_session_id');
    console.log(`Session cookie before logout: ${sessionCookieBefore ? 'PRESENT' : 'MISSING'}\n`);

    // Step 3: Check auth status before logout
    console.log('📍 STEP 3: Check auth status before logout');
    const statusBefore = await page.request.get(
      `${STAGING_CONFIG.apiUrl}/api/v1/openrouter/auth/status`
    );
    const statusDataBefore = await statusBefore.json();
    console.log(`Auth status: ${JSON.stringify(statusDataBefore, null, 2)}\n`);

    // Step 4: Perform logout
    console.log('📍 STEP 4: Perform logout');
    const logoutResponse = await page.request.post(
      `${STAGING_CONFIG.apiUrl}/api/v1/openrouter/auth/logout`
    );
    console.log(`Logout response status: ${logoutResponse.status()}`);
    const logoutData = await logoutResponse.json();
    console.log(`Logout response body: ${JSON.stringify(logoutData, null, 2)}\n`);

    // Step 5: Inspect cookies after logout
    console.log('📍 STEP 5: Inspect cookies after logout');
    cookies = await page.context().cookies();
    console.log(`Total cookies: ${cookies.length}`);
    cookies.forEach(cookie => {
      console.log(`  - ${cookie.name}: ${cookie.value.substring(0, 30)}...`);
      console.log(`    path: ${cookie.path}, domain: ${cookie.domain}, httpOnly: ${cookie.httpOnly}, secure: ${cookie.secure}`);
    });
    const sessionCookieAfter = cookies.find(c => c.name === 'openrouter_session_id');
    console.log(`Session cookie after logout: ${sessionCookieAfter ? 'PRESENT' : 'MISSING'}\n`);

    // Step 6: Check auth status after logout
    console.log('📍 STEP 6: Check auth status after logout');
    const statusAfter = await page.request.get(
      `${STAGING_CONFIG.apiUrl}/api/v1/openrouter/auth/status`
    );
    const statusDataAfter = await statusAfter.json();
    console.log(`Auth status: ${JSON.stringify(statusDataAfter, null, 2)}\n`);

    // Step 7: Verify logout was successful
    console.log('📍 STEP 7: Verify logout was successful');
    expect(sessionCookieAfter).toBeUndefined();
    expect(statusDataAfter.authenticated).toBe(false);
    console.log('✓ Logout verification passed\n');

    // Step 8: Try to access protected route
    console.log('📍 STEP 8: Try to access protected route');
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    const currentUrl = page.url();
    console.log(`Current URL after accessing /dashboard: ${currentUrl}`);
    expect(currentUrl).toContain('login');
    console.log('✓ Protected route access redirected to login\n');

    console.log('=== LOGOUT DEBUG TEST END ===\n');
  });

  test('should verify session deletion from backend', async ({ page }) => {
    console.log('\n=== SESSION DELETION VERIFICATION TEST START ===\n');

    // Step 1: Login
    console.log('📍 STEP 1: Login');
    await loginPage.loginWithDemo();
    await loginPage.waitForLoginSuccess();
    console.log('✓ Login successful\n');

    // Step 2: Get session ID
    console.log('📍 STEP 2: Get session ID');
    const cookies = await page.context().cookies();
    const sessionCookie = cookies.find(c => c.name === 'openrouter_session_id');
    const sessionId = sessionCookie?.value;
    console.log(`Session ID: ${sessionId?.substring(0, 30)}...\n`);

    // Step 3: Verify session exists
    console.log('📍 STEP 3: Verify session exists (via auth status)');
    const statusBefore = await page.request.get(
      `${STAGING_CONFIG.apiUrl}/api/v1/openrouter/auth/status`
    );
    const statusDataBefore = await statusBefore.json();
    console.log(`Authenticated: ${statusDataBefore.authenticated}`);
    console.log(`Auth method: ${statusDataBefore.auth_method}\n`);

    // Step 4: Logout
    console.log('📍 STEP 4: Logout');
    await dashboardPage.logout();
    console.log('✓ Logout initiated\n');

    // Step 5: Verify session is deleted
    console.log('📍 STEP 5: Verify session is deleted (via auth status)');
    const statusAfter = await page.request.get(
      `${STAGING_CONFIG.apiUrl}/api/v1/openrouter/auth/status`
    );
    const statusDataAfter = await statusAfter.json();
    console.log(`Authenticated: ${statusDataAfter.authenticated}`);
    console.log(`Auth method: ${statusDataAfter.auth_method}`);
    console.log(`User: ${statusDataAfter.user}\n`);

    // Step 6: Verify
    expect(statusDataAfter.authenticated).toBe(false);
    console.log('✓ Session successfully deleted from backend\n');

    console.log('=== SESSION DELETION VERIFICATION TEST END ===\n');
  });
});

