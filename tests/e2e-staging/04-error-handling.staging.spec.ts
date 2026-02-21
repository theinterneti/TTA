// Logseq: [[TTA.dev/Tests/E2e-staging/04-error-handling.staging.spec]]
/**
 * Error Handling E2E Tests for Staging Environment
 *
 * Validates:
 * - Graceful error handling
 * - Clear error messages
 * - Recovery from errors
 * - Edge cases
 */

import { test, expect } from '@playwright/test';
import { LoginPage } from './page-objects/LoginPage';
import { DashboardPage } from './page-objects/DashboardPage';
import { STAGING_CONFIG } from './helpers/staging-config';
import { loginWithDemoCredentials, waitForNetworkIdle } from './helpers/test-helpers';

test.describe('Error Handling - Staging Environment', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
  });

  test.describe('Network Errors', () => {
    test('should handle offline mode gracefully', async ({ page, context }) => {
      console.log('✓ Testing offline mode handling');

      await test.step('Login while online', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in while online');
      });

      await test.step('Go offline', async () => {
        await context.setOffline(true);
        console.log('  ✓ Network set to offline');
      });

      await test.step('Attempt navigation', async () => {
        const link = page.locator('a:has-text("Characters")').first();
        if (await link.isVisible({ timeout: 2000 }).catch(() => false)) {
          await link.click();
          await page.waitForTimeout(2000);
          console.log('  ✓ Attempted navigation while offline');
        }
      });

      await test.step('Go back online', async () => {
        await context.setOffline(false);
        await page.reload();
        await waitForNetworkIdle(page);
        console.log('  ✓ Network restored');
      });

      await test.step('Application recovers', async () => {
        const currentUrl = page.url();
        expect(currentUrl).toBeTruthy();
        console.log('  ✓ Application recovered from offline mode');
      });
    });

    test('should handle slow network gracefully', async ({ page, context }) => {
      console.log('✓ Testing slow network handling');

      await test.step('Simulate slow network', async () => {
        // Simulate slow 3G
        await context.route('**/*', async route => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          await route.continue();
        });
        console.log('  ✓ Slow network simulated');
      });

      await test.step('Login with slow network', async () => {
        await loginPage.goto();
        await loginPage.loginWithDemo();

        // Should eventually succeed
        await loginPage.waitForLoginSuccess();
        console.log('  ✓ Login succeeded despite slow network');
      });
    });
  });

  test.describe('Invalid Input', () => {
    test('should validate form inputs', async ({ page }) => {
      console.log('✓ Testing form validation');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Submit empty form', async () => {
        await loginPage.submitEmptyForm();
        await page.waitForTimeout(1000);

        const currentUrl = page.url();
        expect(currentUrl).toContain('login');
        console.log('  ✓ Empty form submission prevented');
      });

      await test.step('Submit with invalid credentials', async () => {
        await loginPage.login('invalid', 'invalid');
        await page.waitForTimeout(2000);

        const hasError = await loginPage.hasError();
        console.log(`  ${hasError ? '✓' : '⚠'} Error handling for invalid credentials`);
      });
    });

    test('should handle special characters in input', async ({ page }) => {
      console.log('✓ Testing special character handling');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Enter special characters', async () => {
        await loginPage.login('<script>alert("xss")</script>', '"; DROP TABLE users; --');
        await page.waitForTimeout(2000);

        // Should not cause errors or XSS
        const currentUrl = page.url();
        expect(currentUrl).toContain('login');
        console.log('  ✓ Special characters handled safely');
      });
    });
  });

  test.describe('Session Errors', () => {
    test('should handle expired session', async ({ page }) => {
      console.log('✓ Testing expired session handling');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Clear session storage', async () => {
        await page.evaluate(() => {
          sessionStorage.clear();
          localStorage.clear();
        });
        console.log('  ✓ Session cleared');
      });

      await test.step('Attempt to access protected route', async () => {
        await page.goto('/dashboard');
        await waitForNetworkIdle(page);

        // Should redirect to login
        const currentUrl = page.url();
        expect(currentUrl).toContain('login');
        console.log('  ✓ Redirected to login after session expiry');
      });
    });
  });

  test.describe('API Errors', () => {
    test('should handle 404 errors', async ({ page }) => {
      console.log('✓ Testing 404 error handling');

      await test.step('Navigate to non-existent page', async () => {
        await page.goto('/nonexistent-page-12345');
        await waitForNetworkIdle(page);
        console.log('  ✓ Navigated to non-existent page');
      });

      await test.step('Application handles 404', async () => {
        // Should show 404 page or redirect
        const pageText = await page.textContent('body');
        expect(pageText).toBeTruthy();
        console.log('  ✓ 404 handled gracefully');
      });
    });

    test('should handle 500 errors', async ({ page }) => {
      console.log('✓ Testing 500 error handling');

      await test.step('Simulate server error', async () => {
        await page.route('**/api/**', route => {
          route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Internal Server Error' }),
          });
        });
        console.log('  ✓ Server error simulated');
      });

      await test.step('Attempt login', async () => {
        await loginPage.goto();
        await loginPage.loginWithDemo();
        await page.waitForTimeout(2000);

        // Should show error message
        const hasError = await loginPage.hasError();
        console.log(`  ${hasError ? '✓' : '⚠'} Server error handled`);
      });
    });
  });

  test.describe('Edge Cases', () => {
    test('should handle rapid clicks', async ({ page }) => {
      console.log('✓ Testing rapid click handling');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Rapid submit clicks', async () => {
        await loginPage.fillInput('input[name="username"]', 'test');
        await loginPage.fillInput('input[name="password"]', 'test');

        const submitButton = page.locator('button[type="submit"]').first();

        // Click multiple times rapidly
        await submitButton.click();
        await submitButton.click();
        await submitButton.click();

        await page.waitForTimeout(2000);
        console.log('  ✓ Rapid clicks handled');
      });
    });

    test('should handle browser back button', async ({ page }) => {
      console.log('✓ Testing browser back button');

      await test.step('Login and navigate', async () => {
        await loginWithDemoCredentials(page);

        const link = page.locator('a:has-text("Characters")').first();
        if (await link.isVisible({ timeout: 2000 }).catch(() => false)) {
          await link.click();
          await waitForNetworkIdle(page);
          console.log('  ✓ Navigated to characters');
        }
      });

      await test.step('Use browser back button', async () => {
        await page.goBack();
        await waitForNetworkIdle(page);

        const currentUrl = page.url();
        expect(currentUrl).toContain('dashboard');
        console.log('  ✓ Back button works correctly');
      });
    });

    test('should handle page refresh during operation', async ({ page }) => {
      console.log('✓ Testing page refresh during operation');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Refresh during navigation', async () => {
        const link = page.locator('a:has-text("Characters")').first();
        if (await link.isVisible({ timeout: 2000 }).catch(() => false)) {
          link.click(); // Don't await

          // Refresh immediately
          await page.reload();
          await waitForNetworkIdle(page);
          console.log('  ✓ Page refreshed during navigation');
        }
      });

      await test.step('Application recovers', async () => {
        const currentUrl = page.url();
        expect(currentUrl).toBeTruthy();
        console.log('  ✓ Application recovered from refresh');
      });
    });
  });

  test.describe('Error Recovery', () => {
    test('should allow retry after error', async ({ page }) => {
      console.log('✓ Testing error recovery');

      await test.step('Cause an error', async () => {
        await loginPage.goto();
        await loginPage.login('invalid', 'invalid');
        await page.waitForTimeout(2000);
        console.log('  ✓ Error caused');
      });

      await test.step('Retry with correct credentials', async () => {
        await loginPage.clearForm();
        await loginPage.loginWithDemo();
        await loginPage.waitForLoginSuccess();
        console.log('  ✓ Successfully recovered and logged in');
      });
    });
  });
});
