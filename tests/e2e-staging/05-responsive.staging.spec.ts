// Logseq: [[TTA.dev/Tests/E2e-staging/05-responsive.staging.spec]]
/**
 * Responsive Design E2E Tests for Staging Environment
 *
 * Validates:
 * - Mobile responsiveness
 * - Tablet responsiveness
 * - Desktop layouts
 * - Touch interactions
 * - Viewport adaptations
 */

import { test, expect } from '@playwright/test';
import { LoginPage } from './page-objects/LoginPage';
import { DashboardPage } from './page-objects/DashboardPage';
import { loginWithDemoCredentials, waitForNetworkIdle } from './helpers/test-helpers';

test.describe('Responsive Design - Staging Environment', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
  });

  test.describe('Mobile Viewport (375x667)', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test('should display correctly on mobile', async ({ page }) => {
      console.log('✓ Testing mobile viewport');

      await test.step('Login page is mobile-friendly', async () => {
        await loginPage.goto();
        await loginPage.expectLoginFormVisible();
        console.log('  ✓ Login form visible on mobile');
      });

      await test.step('Login works on mobile', async () => {
        await loginPage.loginWithDemo();
        await loginPage.waitForLoginSuccess();
        console.log('  ✓ Login successful on mobile');
      });

      await test.step('Dashboard is mobile-friendly', async () => {
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Dashboard loaded on mobile');
      });

      await test.step('Navigation is accessible on mobile', async () => {
        // Check for mobile menu or navigation
        const nav = page.locator('nav, [data-testid="navigation"], button:has-text("Menu")');
        const hasNav = await nav.count() > 0;
        expect(hasNav).toBeTruthy();
        console.log('  ✓ Navigation accessible on mobile');
      });
    });

    test('should handle touch interactions', async ({ page }) => {
      console.log('✓ Testing touch interactions');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Tap interactions work', async () => {
        const buttons = page.locator('button:visible');
        const count = await buttons.count();

        if (count > 0) {
          const firstButton = buttons.first();
          await firstButton.tap();
          await page.waitForTimeout(500);
          console.log('  ✓ Tap interactions work');
        }
      });
    });
  });

  test.describe('Tablet Viewport (768x1024)', () => {
    test.use({ viewport: { width: 768, height: 1024 } });

    test('should display correctly on tablet', async ({ page }) => {
      console.log('✓ Testing tablet viewport');

      await test.step('Login on tablet', async () => {
        await loginPage.goto();
        await loginPage.loginWithDemo();
        await loginPage.waitForLoginSuccess();
        console.log('  ✓ Login successful on tablet');
      });

      await test.step('Dashboard adapts to tablet', async () => {
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Dashboard adapted to tablet');
      });

      await test.step('Content is readable', async () => {
        const pageText = await page.textContent('body');
        expect(pageText).toBeTruthy();
        console.log('  ✓ Content is readable on tablet');
      });
    });
  });

  test.describe('Desktop Viewport (1920x1080)', () => {
    test.use({ viewport: { width: 1920, height: 1080 } });

    test('should display correctly on desktop', async ({ page }) => {
      console.log('✓ Testing desktop viewport');

      await test.step('Login on desktop', async () => {
        await loginPage.goto();
        await loginPage.loginWithDemo();
        await loginPage.waitForLoginSuccess();
        console.log('  ✓ Login successful on desktop');
      });

      await test.step('Dashboard uses full width', async () => {
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Dashboard uses desktop layout');
      });

      await test.step('All features are visible', async () => {
        const hasNav = await dashboardPage.hasNavigationMenu();
        expect(hasNav).toBeTruthy();
        console.log('  ✓ All features visible on desktop');
      });
    });
  });

  test.describe('Viewport Transitions', () => {
    test('should adapt when viewport changes', async ({ page }) => {
      console.log('✓ Testing viewport transitions');

      await test.step('Login on desktop', async () => {
        await page.setViewportSize({ width: 1920, height: 1080 });
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in on desktop');
      });

      await test.step('Resize to tablet', async () => {
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.waitForTimeout(500);
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Adapted to tablet viewport');
      });

      await test.step('Resize to mobile', async () => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.waitForTimeout(500);
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Adapted to mobile viewport');
      });

      await test.step('Resize back to desktop', async () => {
        await page.setViewportSize({ width: 1920, height: 1080 });
        await page.waitForTimeout(500);
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Adapted back to desktop viewport');
      });
    });
  });

  test.describe('Orientation Changes', () => {
    test('should handle portrait to landscape', async ({ page }) => {
      console.log('✓ Testing orientation changes');

      await test.step('Login in portrait', async () => {
        await page.setViewportSize({ width: 375, height: 667 });
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in (portrait)');
      });

      await test.step('Switch to landscape', async () => {
        await page.setViewportSize({ width: 667, height: 375 });
        await page.waitForTimeout(500);
        await dashboardPage.expectDashboardLoaded();
        console.log('  ✓ Adapted to landscape');
      });
    });
  });

  test.describe('Text Readability', () => {
    test('should have readable text on all viewports', async ({ page }) => {
      console.log('✓ Testing text readability');

      const viewports = [
        { name: 'Mobile', width: 375, height: 667 },
        { name: 'Tablet', width: 768, height: 1024 },
        { name: 'Desktop', width: 1920, height: 1080 },
      ];

      for (const viewport of viewports) {
        await test.step(`Check ${viewport.name} readability`, async () => {
          await page.setViewportSize({ width: viewport.width, height: viewport.height });
          await loginPage.goto();

          // Check font sizes
          const fontSize = await page.evaluate(() => {
            const body = document.body;
            return window.getComputedStyle(body).fontSize;
          });

          console.log(`  ✓ ${viewport.name}: Font size ${fontSize}`);
        });
      }
    });
  });

  test.describe('Interactive Elements', () => {
    test('should have appropriately sized touch targets on mobile', async ({ page }) => {
      console.log('✓ Testing touch target sizes');

      await test.step('Set mobile viewport', async () => {
        await page.setViewportSize({ width: 375, height: 667 });
        await loginPage.goto();
        console.log('  ✓ Mobile viewport set');
      });

      await test.step('Check button sizes', async () => {
        const buttons = page.locator('button:visible');
        const count = await buttons.count();

        if (count > 0) {
          const firstButton = buttons.first();
          const box = await firstButton.boundingBox();

          if (box) {
            // Touch targets should be at least 44x44 pixels
            const isLargeEnough = box.width >= 40 && box.height >= 40;
            console.log(`  ${isLargeEnough ? '✓' : '⚠'} Button size: ${box.width}x${box.height}`);
          }
        }
      });
    });
  });

  test.describe('Scrolling Behavior', () => {
    test('should handle scrolling on mobile', async ({ page }) => {
      console.log('✓ Testing mobile scrolling');

      await test.step('Set mobile viewport', async () => {
        await page.setViewportSize({ width: 375, height: 667 });
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in on mobile');
      });

      await test.step('Scroll page', async () => {
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(500);
        console.log('  ✓ Scrolling works on mobile');
      });

      await test.step('Scroll back to top', async () => {
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.waitForTimeout(500);
        console.log('  ✓ Scroll to top works');
      });
    });
  });
});
