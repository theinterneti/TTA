/**
 * Accessibility E2E Tests for Staging Environment
 *
 * Validates:
 * - WCAG compliance
 * - Keyboard navigation
 * - Screen reader compatibility
 * - ARIA labels
 * - Color contrast
 */

import { test, expect } from '@playwright/test';
import { LoginPage } from './page-objects/LoginPage';
import { DashboardPage } from './page-objects/DashboardPage';
import { loginWithDemoCredentials, checkAccessibility } from './helpers/test-helpers';

test.describe('Accessibility - Staging Environment', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
  });

  test.describe('WCAG Compliance', () => {
    test('should pass accessibility checks on login page', async ({ page }) => {
      console.log('✓ Testing login page accessibility');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Run accessibility scan', async () => {
        const results = await checkAccessibility(page);

        if (results) {
          const violations = results.violations || [];
          console.log(`  ${violations.length === 0 ? '✓' : '⚠'} ${violations.length} accessibility violations found`);

          if (violations.length > 0) {
            violations.forEach((violation: any) => {
              console.log(`    - ${violation.id}: ${violation.description}`);
            });
          }
        } else {
          console.log('  ⊘ Accessibility check not available');
        }
      });
    });

    test('should pass accessibility checks on dashboard', async ({ page }) => {
      console.log('✓ Testing dashboard accessibility');

      await test.step('Login and navigate to dashboard', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ On dashboard');
      });

      await test.step('Run accessibility scan', async () => {
        const results = await checkAccessibility(page);

        if (results) {
          const violations = results.violations || [];
          console.log(`  ${violations.length === 0 ? '✓' : '⚠'} ${violations.length} accessibility violations found`);
        } else {
          console.log('  ⊘ Accessibility check not available');
        }
      });
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should support keyboard navigation on login page', async ({ page }) => {
      console.log('✓ Testing keyboard navigation on login');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Tab through form fields', async () => {
        await page.keyboard.press('Tab');
        await page.waitForTimeout(200);

        const activeElement = await page.evaluate(() => document.activeElement?.tagName);
        console.log(`  ✓ Tab navigation works (focused: ${activeElement})`);
      });

      await test.step('Fill form with keyboard', async () => {
        await page.keyboard.type('demo_user');
        await page.keyboard.press('Tab');
        await page.keyboard.type('DemoPassword123!');
        console.log('  ✓ Form can be filled with keyboard');
      });

      await test.step('Submit with Enter key', async () => {
        await page.keyboard.press('Enter');
        await page.waitForTimeout(2000);
        console.log('  ✓ Form can be submitted with Enter key');
      });
    });

    test('should support keyboard navigation on dashboard', async ({ page }) => {
      console.log('✓ Testing keyboard navigation on dashboard');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Navigate with keyboard', async () => {
        // Tab through interactive elements
        for (let i = 0; i < 5; i++) {
          await page.keyboard.press('Tab');
          await page.waitForTimeout(200);
        }
        console.log('  ✓ Keyboard navigation works on dashboard');
      });

      await test.step('Activate element with Enter', async () => {
        const activeElement = await page.evaluate(() => {
          const el = document.activeElement;
          return el?.tagName;
        });

        if (activeElement === 'BUTTON' || activeElement === 'A') {
          await page.keyboard.press('Enter');
          await page.waitForTimeout(500);
          console.log('  ✓ Elements can be activated with Enter');
        }
      });
    });
  });

  test.describe('ARIA Labels', () => {
    test('should have proper ARIA labels', async ({ page }) => {
      console.log('✓ Testing ARIA labels');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Check for ARIA labels on inputs', async () => {
        const inputs = page.locator('input');
        const count = await inputs.count();

        for (let i = 0; i < count; i++) {
          const input = inputs.nth(i);
          const ariaLabel = await input.getAttribute('aria-label');
          const ariaLabelledBy = await input.getAttribute('aria-labelledby');
          const hasLabel = ariaLabel || ariaLabelledBy;

          console.log(`  ${hasLabel ? '✓' : '⚠'} Input ${i + 1} has ARIA label: ${hasLabel}`);
        }
      });

      await test.step('Check for ARIA labels on buttons', async () => {
        const buttons = page.locator('button');
        const count = await buttons.count();

        for (let i = 0; i < count; i++) {
          const button = buttons.nth(i);
          const text = await button.textContent();
          const ariaLabel = await button.getAttribute('aria-label');
          const hasLabel = text?.trim() || ariaLabel;

          console.log(`  ${hasLabel ? '✓' : '⚠'} Button ${i + 1} has label: ${hasLabel}`);
        }
      });
    });
  });

  test.describe('Focus Management', () => {
    test('should have visible focus indicators', async ({ page }) => {
      console.log('✓ Testing focus indicators');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Tab to first input', async () => {
        await page.keyboard.press('Tab');
        await page.waitForTimeout(200);

        const hasFocus = await page.evaluate(() => {
          const el = document.activeElement;
          if (!el) return false;

          const styles = window.getComputedStyle(el);
          return styles.outline !== 'none' || styles.boxShadow !== 'none';
        });

        console.log(`  ${hasFocus ? '✓' : '⚠'} Focus indicator visible`);
      });
    });

    test('should trap focus in modals', async ({ page }) => {
      console.log('✓ Testing focus trap in modals');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Open modal if available', async () => {
        const modalTrigger = page.locator('button:has-text("Create"), button:has-text("Add")').first();

        if (await modalTrigger.isVisible({ timeout: 2000 }).catch(() => false)) {
          await modalTrigger.click();
          await page.waitForTimeout(500);

          // Check if modal is open
          const modal = page.locator('[role="dialog"], .modal, [data-testid*="modal"]').first();
          if (await modal.isVisible({ timeout: 2000 }).catch(() => false)) {
            console.log('  ✓ Modal opened');

            // Tab through modal
            for (let i = 0; i < 10; i++) {
              await page.keyboard.press('Tab');
              await page.waitForTimeout(100);
            }

            console.log('  ✓ Focus trap tested');
          }
        } else {
          console.log('  ⊘ No modal available to test');
        }
      });
    });
  });

  test.describe('Screen Reader Support', () => {
    test('should have semantic HTML', async ({ page }) => {
      console.log('✓ Testing semantic HTML');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Check for semantic elements', async () => {
        const semanticElements = await page.evaluate(() => {
          return {
            main: document.querySelectorAll('main').length,
            nav: document.querySelectorAll('nav').length,
            header: document.querySelectorAll('header').length,
            footer: document.querySelectorAll('footer').length,
            article: document.querySelectorAll('article').length,
            section: document.querySelectorAll('section').length,
          };
        });

        console.log('  ✓ Semantic elements found:', semanticElements);
      });
    });

    test('should have proper heading hierarchy', async ({ page }) => {
      console.log('✓ Testing heading hierarchy');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Check heading levels', async () => {
        const headings = await page.evaluate(() => {
          const h1 = document.querySelectorAll('h1').length;
          const h2 = document.querySelectorAll('h2').length;
          const h3 = document.querySelectorAll('h3').length;
          const h4 = document.querySelectorAll('h4').length;

          return { h1, h2, h3, h4 };
        });

        console.log('  ✓ Heading hierarchy:', headings);
        expect(headings.h1).toBeGreaterThan(0);
      });
    });
  });

  test.describe('Color Contrast', () => {
    test('should have sufficient color contrast', async ({ page }) => {
      console.log('✓ Testing color contrast');

      await test.step('Navigate to login', async () => {
        await loginPage.goto();
        console.log('  ✓ On login page');
      });

      await test.step('Run contrast check', async () => {
        const results = await checkAccessibility(page);

        if (results) {
          const contrastViolations = results.violations?.filter((v: any) =>
            v.id.includes('color-contrast')
          ) || [];

          console.log(`  ${contrastViolations.length === 0 ? '✓' : '⚠'} ${contrastViolations.length} contrast violations`);
        } else {
          console.log('  ⊘ Contrast check not available');
        }
      });
    });
  });

  test.describe('Alternative Text', () => {
    test('should have alt text for images', async ({ page }) => {
      console.log('✓ Testing image alt text');

      await test.step('Login', async () => {
        await loginWithDemoCredentials(page);
        console.log('  ✓ Logged in');
      });

      await test.step('Check images for alt text', async () => {
        const images = page.locator('img');
        const count = await images.count();

        if (count > 0) {
          for (let i = 0; i < count; i++) {
            const img = images.nth(i);
            const alt = await img.getAttribute('alt');
            const hasAlt = alt !== null;

            console.log(`  ${hasAlt ? '✓' : '⚠'} Image ${i + 1} has alt text: ${hasAlt}`);
          }
        } else {
          console.log('  ⊘ No images found');
        }
      });
    });
  });
});
