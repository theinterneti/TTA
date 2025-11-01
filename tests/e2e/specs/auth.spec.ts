import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { DashboardPage } from '../page-objects/DashboardPage';
import { testUsers } from '../fixtures/test-data';

test.describe('Authentication Flow', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
  });

  test.describe('Login Page', () => {
    test('should display login form correctly', async () => {
      await loginPage.goto();
      await loginPage.expectLoginFormVisible();
      await loginPage.expectWelcomeMessage();
    });

    test('should show validation errors for empty fields', async () => {
      await loginPage.goto();
      await loginPage.expectUsernameRequired();
      await loginPage.expectPasswordRequired();
    });

    test('should show error for invalid credentials', async () => {
      await loginPage.goto();
      await loginPage.expectInvalidCredentials();
    });

    test('should successfully login with valid credentials', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await loginPage.expectLoginSuccess();

      // Should redirect to dashboard
      await dashboardPage.expectDashboardLoaded();
    });

    test('should mask password input', async () => {
      await loginPage.goto();
      await loginPage.checkPasswordMasking();
    });

    test('should not expose password in URL', async () => {
      await loginPage.goto();
      await loginPage.checkNoPasswordInUrl();
    });

    test('should handle loading state during login', async () => {
      await loginPage.goto();
      await loginPage.fillUsername(testUsers.default.username);
      await loginPage.fillPassword(testUsers.default.password);
      await loginPage.clickLogin();

      // Should show loading state briefly
      await loginPage.expectLoadingState();
    });
  });

  test.describe('Authentication State', () => {
    test('should redirect unauthenticated users to login', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForURL(/login|auth/);
      await loginPage.expectLoginFormVisible();
    });

    test('should maintain session after page refresh', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Refresh page
      await dashboardPage.page.reload();
      await dashboardPage.expectDashboardLoaded();
    });

    test('should logout successfully', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      await dashboardPage.logout();
      await loginPage.expectLoginFormVisible();
    });

    test('should clear session data on logout', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      await dashboardPage.logout();

      // Try to access protected route
      await dashboardPage.goto();
      await loginPage.expectLoginFormVisible();
    });
  });

  test.describe('Accessibility', () => {
    test('should be accessible with keyboard navigation', async () => {
      await loginPage.goto();
      await loginPage.navigateWithKeyboard();
    });

    test('should meet accessibility standards', async () => {
      await loginPage.goto();
      await loginPage.checkAccessibility();
    });

    test('should have proper ARIA labels', async () => {
      await loginPage.goto();
      await expect(loginPage.usernameInput).toHaveAttribute('aria-label');
      await expect(loginPage.passwordInput).toHaveAttribute('aria-label');
    });

    test('should support screen readers', async () => {
      await loginPage.goto();
      await expect(loginPage.loginForm).toHaveRole('form');
      await expect(loginPage.loginButton).toHaveRole('button');
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile devices', async () => {
      await loginPage.goto();
      await loginPage.checkMobileLayout();
    });

    test('should adapt to different screen sizes', async ({ page }) => {
      await loginPage.goto();

      // Test tablet size
      await page.setViewportSize({ width: 768, height: 1024 });
      await loginPage.expectLoginFormVisible();

      // Test desktop size
      await page.setViewportSize({ width: 1920, height: 1080 });
      await loginPage.expectLoginFormVisible();
    });
  });

  test.describe('Performance', () => {
    test('should login within acceptable time', async () => {
      await loginPage.goto();
      const loginTime = await loginPage.measureLoginTime();
      expect(loginTime).toBeLessThan(5000);
    });

    test('should load login page quickly', async ({ page }) => {
      const startTime = Date.now();
      await loginPage.goto();
      await loginPage.expectLoginFormVisible();
      const loadTime = Date.now() - startTime;

      expect(loadTime).toBeLessThan(3000);
    });
  });

  test.describe('Security', () => {
    test('should prevent multiple rapid login attempts', async () => {
      await loginPage.goto();

      // Attempt multiple failed logins
      for (let i = 0; i < 5; i++) {
        await loginPage.login({ username: 'invalid', password: 'invalid', email: '' });
        await loginPage.expectErrorMessage();
      }

      // Should show rate limiting message
      const rateLimitMessage = loginPage.page.locator('[data-testid="rate-limit"], .rate-limit');
      await expect(rateLimitMessage).toBeVisible();
    });

    test('should clear form data on navigation away', async ({ page }) => {
      await loginPage.goto();
      await loginPage.fillUsername('testuser');
      await loginPage.fillPassword('testpass');

      // Navigate away and back
      await page.goto('/');
      await loginPage.goto();

      // Form should be cleared
      await expect(loginPage.usernameInput).toHaveValue('');
      await expect(loginPage.passwordInput).toHaveValue('');
    });
  });

  test.describe('Error Handling', () => {
    test('should handle network errors gracefully', async ({ page }) => {
      await loginPage.goto();

      // Mock network failure
      await page.route('**/auth/login', route => {
        route.abort('failed');
      });

      await loginPage.login(testUsers.default);
      await loginPage.expectErrorMessage();
    });

    test('should handle server errors gracefully', async ({ page }) => {
      await loginPage.goto();

      // Mock server error
      await page.route('**/auth/login', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal server error' }),
        });
      });

      await loginPage.login(testUsers.default);
      await loginPage.expectErrorMessage();
    });

    test('should recover from temporary failures', async ({ page }) => {
      await loginPage.goto();

      let attemptCount = 0;
      await page.route('**/auth/login', route => {
        attemptCount++;
        if (attemptCount === 1) {
          // First attempt fails
          route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Temporary error' }),
          });
        } else {
          // Second attempt succeeds
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              token: 'mock-token',
              user: { id: '1', username: 'testuser', email: 'test@example.com' }
            }),
          });
        }
      });

      // First attempt should fail
      await loginPage.login(testUsers.default);
      await loginPage.expectErrorMessage();

      // Second attempt should succeed
      await loginPage.login(testUsers.default);
      await loginPage.expectLoginSuccess();
    });
  });

  test.describe('Visual Regression', () => {
    test('should match login page screenshot', async ({ page }) => {
      await loginPage.goto();
      await expect(page).toHaveScreenshot('login-page.png');
    });

    test('should match error state screenshot', async ({ page }) => {
      await loginPage.goto();
      await loginPage.expectInvalidCredentials();
      await expect(page).toHaveScreenshot('login-error.png');
    });
  });
});
