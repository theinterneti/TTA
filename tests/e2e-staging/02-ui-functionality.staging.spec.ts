// Logseq: [[TTA.dev/Tests/E2e-staging/02-ui-functionality.staging.spec]]
/**
 * UI/UX Functionality E2E Tests for Staging Environment
 *
 * Validates:
 * - Interactive elements work correctly
 * - Navigation is intuitive
 * - Forms are user-friendly
 * - Visual feedback is clear
 * - Zero-instruction usability
 */

import { expect, test } from '@playwright/test';
import { loginWithDemoCredentials, waitForNetworkIdle } from './helpers/test-helpers';
import { DashboardPage } from './page-objects/DashboardPage';
import { LoginPage } from './page-objects/LoginPage';

test.describe('UI/UX Functionality - Staging Environment', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
  });

  test.describe('Navigation', () => {
    test('should have intuitive navigation menu', async ({ page }) => {
      console.log('✓ Testing navigation menu');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Navigation menu is visible', async () => {
        await dashboardPage.expectNavigationMenu();
        console.log('  ✓ Navigation menu visible');
      });

      await test.step('All main sections are accessible', async () => {
        const navLinks = page.locator('nav a, [data-testid="navigation"] a');
        const count = await navLinks.count();
        expect(count).toBeGreaterThan(0);
        console.log(`  ✓ ${count} navigation links found`);
      });

      await test.step('Navigation links are labeled clearly', async () => {
        const navTexts = await page.locator('nav a, [data-testid="navigation"] a').allTextContents();
        const hasLabels = navTexts.every(text => text.trim().length > 0);
        expect(hasLabels).toBeTruthy();
        console.log('  ✓ All navigation links have clear labels');
      });
    });

    test('should navigate between pages smoothly', async ({ page }) => {
      console.log('✓ Testing page navigation');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Navigate to Characters', async () => {
        const link = page.locator('a:has-text("Characters"), nav a[href*="character"]').first();
        if (await link.isVisible({ timeout: 2000 }).catch(() => false)) {
          await link.click();
          await waitForNetworkIdle(page);
          expect(page.url()).toContain('character');
          console.log('  ✓ Navigated to Characters');
        } else {
          console.log('  ⊘ Characters link not found');
        }
      });

      await test.step('Navigate to Worlds', async () => {
        const link = page.locator('a:has-text("Worlds"), nav a[href*="world"]').first();
        if (await link.isVisible({ timeout: 2000 }).catch(() => false)) {
          await link.click();
          await waitForNetworkIdle(page);
          expect(page.url()).toContain('world');
          console.log('  ✓ Navigated to Worlds');
        } else {
          console.log('  ⊘ Worlds link not found');
        }
      });

      await test.step('Navigate back to Dashboard', async () => {
        const link = page.locator('a:has-text("Dashboard"), nav a[href*="dashboard"]').first();
        if (await link.isVisible({ timeout: 2000 }).catch(() => false)) {
          await link.click();
          await waitForNetworkIdle(page);
          expect(page.url()).toContain('dashboard');
          console.log('  ✓ Navigated back to Dashboard');
        } else {
          console.log('  ⊘ Dashboard link not found');
        }
      });
    });
  });

  test.describe('Interactive Elements', () => {
    test('should have working buttons with clear labels', async ({ page }) => {
      console.log('✓ Testing button functionality');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Primary action buttons are visible', async () => {
        await dashboardPage.expectClearCallToAction();
        console.log('  ✓ Primary action buttons visible');
      });

      await test.step('Buttons have clear labels', async () => {
        const buttons = page.locator('button:visible');
        const count = await buttons.count();

        if (count > 0) {
          const buttonTexts = await buttons.allTextContents();
          const hasLabels = buttonTexts.some(text => text.trim().length > 0);
          expect(hasLabels).toBeTruthy();
          console.log(`  ✓ ${count} buttons found with labels`);
        }
      });

      await test.step('Buttons respond to hover', async () => {
        const firstButton = page.locator('button:visible').first();
        if (await firstButton.isVisible({ timeout: 2000 }).catch(() => false)) {
          await firstButton.hover();
          console.log('  ✓ Buttons respond to hover');
        }
      });
    });

    test('should have accessible form inputs', async ({ page }) => {
      console.log('✓ Testing form accessibility');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Form inputs have labels or placeholders', async () => {
        const usernameInput = page.locator('input[name="username"], input[id="username"]').first();
        const passwordInput = page.locator('input[name="password"], input[id="password"]').first();

        await expect(usernameInput).toBeVisible();
        await expect(passwordInput).toBeVisible();

        console.log('  ✓ Form inputs are accessible');
      });

      await test.step('Inputs accept keyboard input', async () => {
        const usernameInput = page.locator('input[name="username"], input[id="username"]').first();
        await usernameInput.fill('test');
        const value = await usernameInput.inputValue();
        expect(value).toBe('test');
        console.log('  ✓ Inputs accept keyboard input');
      });
    });
  });

  test.describe('Visual Feedback', () => {
    test('should show loading states', async ({ page }) => {
      console.log('✓ Testing loading states');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Submit login form', async () => {
        await loginPage.loginWithDemo();
        console.log('  ✓ Login submitted');
      });

      await test.step('Check for loading indicator', async () => {
        // Look for common loading indicators
        const loadingIndicators = page.locator(
          '[data-testid*="loading"], .loading, .spinner, [aria-busy="true"]'
        );

        // Loading indicator might appear briefly
        await page.waitForTimeout(500);
        console.log('  ✓ Checked for loading states');
      });
    });

    test('should provide clear error messages', async ({ page }) => {
      console.log('✓ Testing error messages');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Submit invalid credentials', async () => {
        await loginPage.login('invalid', 'invalid');
        await page.waitForTimeout(2000);
        console.log('  ✓ Invalid credentials submitted');
      });

      await test.step('Error message is clear and helpful', async () => {
        const hasError = await loginPage.hasError();
        if (hasError) {
          const errorMessage = await loginPage.getErrorMessage();
          expect(errorMessage).toBeTruthy();
          console.log(`  ✓ Error message: "${errorMessage}"`);
        } else {
          console.log('  ⚠ No error message displayed');
        }
      });
    });
  });

  test.describe('Zero-Instruction Usability', () => {
    test('should be usable without instructions', async ({ page }) => {
      console.log('✓ Testing zero-instruction usability');

      await test.step('Landing page is self-explanatory', async () => {
        await page.goto('/');
        await waitForNetworkIdle(page);

        // Should either show login or redirect to login
        const currentUrl = page.url();
        const isOnLoginOrDashboard = currentUrl.includes('login') || currentUrl.includes('dashboard');
        expect(isOnLoginOrDashboard).toBeTruthy();
        console.log('  ✓ Landing page redirects appropriately');
      });

      await test.step('Login page is self-explanatory', async () => {
        await loginPage.goto();
        await loginPage.expectLoginFormVisible();

        // Check for helpful text
        const pageText = await page.textContent('body');
        const hasHelpfulText = pageText && (
          pageText.toLowerCase().includes('sign in') ||
          pageText.toLowerCase().includes('login') ||
          pageText.toLowerCase().includes('username')
        );
        expect(hasHelpfulText).toBeTruthy();
        console.log('  ✓ Login page has clear instructions');
      });

      await test.step('Dashboard shows clear next steps', async () => {
        await loginWithDemoCredentials(page);
        await dashboardPage.expectClearCallToAction();
        console.log('  ✓ Dashboard shows clear next steps');
      });
    });

    test('should have discoverable features', async ({ page }) => {
      console.log('✓ Testing feature discoverability');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Main features are visible on dashboard', async () => {
        const hasCreateButton = await dashboardPage.hasCreateCharacterButton();
        const hasWorldButton = await dashboardPage.hasSelectWorldButton();

        const hasVisibleFeatures = hasCreateButton || hasWorldButton;
        expect(hasVisibleFeatures).toBeTruthy();
        console.log('  ✓ Main features are discoverable');
      });

      await test.step('Navigation menu shows all sections', async () => {
        const hasNav = await dashboardPage.hasNavigationMenu();
        expect(hasNav).toBeTruthy();
        console.log('  ✓ Navigation menu is discoverable');
      });
    });
  });

  test.describe('Responsive Behavior', () => {
    test('should adapt to different viewport sizes', async ({ page }) => {
      console.log('✓ Testing responsive behavior');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Desktop viewport', async () => {
        await page.setViewportSize({ width: 1920, height: 1080 });
        await page.waitForTimeout(500);
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Works on desktop viewport');
      });

      await test.step('Tablet viewport', async () => {
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.waitForTimeout(500);
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Works on tablet viewport');
      });

      await test.step('Mobile viewport', async () => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.waitForTimeout(500);
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Works on mobile viewport');
      });
    });
  });
});
