// Logseq: [[TTA.dev/Tests/E2e/Specs/Accessibility.spec]]
import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { DashboardPage } from '../page-objects/DashboardPage';
import { CharacterManagementPage } from '../page-objects/CharacterManagementPage';
import { ChatPage } from '../page-objects/ChatPage';
import { SettingsPage } from '../page-objects/SettingsPage';
import { testUsers } from '../fixtures/test-data';
import { checkBasicAccessibility, testKeyboardNavigation } from '../utils/test-helpers';

test.describe('Accessibility Compliance', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;
  let characterPage: CharacterManagementPage;
  let chatPage: ChatPage;
  let settingsPage: SettingsPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    characterPage = new CharacterManagementPage(page);
    chatPage = new ChatPage(page);
    settingsPage = new SettingsPage(page);
  });

  test.describe('WCAG 2.1 AA Compliance', () => {
    test('login page should meet accessibility standards', async () => {
      await loginPage.goto();
      await checkBasicAccessibility(loginPage.page);
      await loginPage.checkAccessibility();
    });

    test('dashboard should meet accessibility standards', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      await checkBasicAccessibility(dashboardPage.page);
      await dashboardPage.checkAccessibility();
    });

    test('character management should meet accessibility standards', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.expectPageLoaded();

      await checkBasicAccessibility(characterPage.page);
      await characterPage.checkAccessibility();
    });

    test('chat interface should meet accessibility standards', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await chatPage.goto();
      await chatPage.expectChatLoaded();

      await checkBasicAccessibility(chatPage.page);
      await chatPage.checkAccessibility();
    });

    test('settings page should meet accessibility standards', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await settingsPage.goto();
      await settingsPage.expectPageLoaded();

      await checkBasicAccessibility(settingsPage.page);
      await settingsPage.checkAccessibility();
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should navigate login form with keyboard', async () => {
      await loginPage.goto();
      await loginPage.navigateWithKeyboard();
    });

    test('should navigate dashboard with keyboard', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();
      await dashboardPage.navigateWithKeyboard();
    });

    test('should navigate character form with keyboard', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.expectPageLoaded();
      await characterPage.navigateFormWithKeyboard();
    });

    test('should navigate chat interface with keyboard', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await chatPage.goto();
      await chatPage.expectChatLoaded();
      await chatPage.navigateWithKeyboard();
    });

    test('should navigate settings tabs with keyboard', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await settingsPage.goto();
      await settingsPage.expectPageLoaded();
      await settingsPage.navigateTabsWithKeyboard();
    });

    test('should support tab trapping in modals', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.clickCreateCharacter();

      // Test tab trapping within modal
      const modalElements = [
        'input[name="name"]',
        'textarea[name="description"]',
        'textarea[name="story"]',
        'button[type="submit"]',
        'button:has-text("Cancel")',
      ];

      await testKeyboardNavigation(page, modalElements);
    });
  });

  test.describe('Screen Reader Support', () => {
    test('should have proper ARIA labels and roles', async ({ page }) => {
      await loginPage.goto();

      // Check form accessibility
      await expect(loginPage.loginForm).toHaveRole('form');
      await expect(loginPage.usernameInput).toHaveAttribute('aria-label');
      await expect(loginPage.passwordInput).toHaveAttribute('aria-label');
      await expect(loginPage.loginButton).toHaveRole('button');
    });

    test('should have proper heading hierarchy', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Check heading structure
      const h1 = page.locator('h1');
      const h2 = page.locator('h2');
      const h3 = page.locator('h3');

      await expect(h1).toHaveCount(1); // Should have exactly one h1

      if (await h2.count() > 0) {
        await expect(h2.first()).toBeVisible();
      }

      if (await h3.count() > 0) {
        await expect(h3.first()).toBeVisible();
      }
    });

    test('should have proper landmark regions', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Check for landmark regions
      await expect(page.locator('main, [role="main"]')).toBeVisible();
      await expect(page.locator('nav, [role="navigation"]')).toBeVisible();

      // Check for complementary regions if present
      const complementary = page.locator('[role="complementary"]');
      if (await complementary.count() > 0) {
        await expect(complementary.first()).toBeVisible();
      }
    });

    test('should announce dynamic content changes', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await chatPage.goto();
      await chatPage.expectChatLoaded();

      // Check for live regions
      const liveRegions = page.locator('[aria-live]');
      await expect(liveRegions.first()).toBeVisible();

      // Check for status announcements
      const statusRegions = page.locator('[role="status"]');
      if (await statusRegions.count() > 0) {
        await expect(statusRegions.first()).toBeVisible();
      }
    });

    test('should have descriptive link text', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Check that links have descriptive text
      const links = page.locator('a');
      const linkCount = await links.count();

      for (let i = 0; i < linkCount; i++) {
        const link = links.nth(i);
        const text = await link.textContent();
        const ariaLabel = await link.getAttribute('aria-label');

        // Link should have either text content or aria-label
        expect(text || ariaLabel).toBeTruthy();

        // Avoid generic link text
        if (text) {
          expect(text.toLowerCase()).not.toMatch(/^(click here|read more|link)$/);
        }
      }
    });
  });

  test.describe('Focus Management', () => {
    test('should manage focus properly in modals', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();

      // Open modal
      await characterPage.createCharacterButton.click();

      // Focus should move to modal
      const firstInput = page.locator('input[name="name"]');
      await expect(firstInput).toBeFocused();

      // Close modal
      const cancelButton = page.locator('button:has-text("Cancel")');
      await cancelButton.click();

      // Focus should return to trigger button
      await expect(characterPage.createCharacterButton).toBeFocused();
    });

    test('should maintain focus visibility', async ({ page }) => {
      await loginPage.goto();

      // Check that focused elements have visible focus indicators
      await loginPage.usernameInput.focus();

      // Should have focus styles (outline, box-shadow, etc.)
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toHaveCSS('outline-width', /[1-9]/);
    });

    test('should skip to main content', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Check for skip links
      const skipLink = page.locator('a[href="#main"], a[href="#content"]').first();
      await expect(skipLink).toBeVisible();

      // Test skip link functionality
      await skipLink.click();
      const mainContent = page.locator('#main, #content, main').first();
      await expect(mainContent).toBeFocused();
    });
  });

  test.describe('Color and Contrast', () => {
    test('should have sufficient color contrast', async ({ page }) => {
      await loginPage.goto();

      // Check that text has sufficient contrast
      // This is a basic check - in practice, you'd use tools like axe-core
      const textElements = page.locator('p, span, label, button');
      const elementCount = await textElements.count();

      for (let i = 0; i < Math.min(elementCount, 10); i++) {
        const element = textElements.nth(i);
        const color = await element.evaluate(el => getComputedStyle(el).color);
        const backgroundColor = await element.evaluate(el => getComputedStyle(el).backgroundColor);

        // Basic check that colors are defined
        expect(color).toBeTruthy();
        expect(backgroundColor).toBeTruthy();
      }
    });

    test('should work with high contrast mode', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await settingsPage.goto();

      // Enable high contrast mode
      await settingsPage.goToAccessibilityTab();
      await settingsPage.highContrastToggle.check();

      // Check that high contrast styles are applied
      await expect(page.locator('body')).toHaveClass(/high-contrast/);

      // Interface should still be usable
      await settingsPage.expectPageLoaded();
    });

    test('should not rely solely on color for information', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await chatPage.goto();
      await chatPage.expectChatLoaded();

      // Check that error states have more than just color
      await chatPage.sendMessage('');

      // Error should be indicated by text, icons, or other visual cues
      const errorElements = page.locator('.error, [data-testid="error"]');
      if (await errorElements.count() > 0) {
        const errorText = await errorElements.first().textContent();
        expect(errorText).toBeTruthy();
      }
    });
  });

  test.describe('Text and Typography', () => {
    test('should support large text setting', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await settingsPage.goto();

      // Enable large text
      await settingsPage.goToAccessibilityTab();
      await settingsPage.largeTextToggle.check();

      // Check that large text styles are applied
      await expect(page.locator('body')).toHaveClass(/large-text/);

      // Text should be larger
      const textElement = page.locator('p, span').first();
      const fontSize = await textElement.evaluate(el => getComputedStyle(el).fontSize);
      expect(parseInt(fontSize)).toBeGreaterThan(14);
    });

    test('should be readable at 200% zoom', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Simulate 200% zoom
      await page.setViewportSize({ width: 640, height: 360 });

      // Content should still be accessible
      await dashboardPage.expectDashboardLoaded();
      await expect(dashboardPage.createCharacterButton).toBeVisible();
    });

    test('should handle text spacing adjustments', async ({ page }) => {
      await loginPage.goto();

      // Inject CSS to increase text spacing (WCAG requirement)
      await page.addStyleTag({
        content: `
          * {
            line-height: 1.5 !important;
            letter-spacing: 0.12em !important;
            word-spacing: 0.16em !important;
          }
          p {
            margin-bottom: 2em !important;
          }
        `
      });

      // Interface should still be usable
      await loginPage.expectLoginFormVisible();
      await expect(loginPage.usernameInput).toBeVisible();
      await expect(loginPage.passwordInput).toBeVisible();
    });
  });

  test.describe('Motion and Animation', () => {
    test('should respect reduced motion preference', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await settingsPage.goto();

      // Enable reduced motion
      await settingsPage.goToAccessibilityTab();
      await settingsPage.reducedMotionToggle.check();

      // Check that reduced motion styles are applied
      await expect(page.locator('body')).toHaveClass(/reduced-motion/);

      // Animations should be disabled or reduced
      const animatedElements = page.locator('[class*="animate"], [class*="transition"]');
      if (await animatedElements.count() > 0) {
        const animationDuration = await animatedElements.first().evaluate(el =>
          getComputedStyle(el).animationDuration
        );
        // Should be very short or none
        expect(animationDuration).toMatch(/^(0s|0\.01s)$/);
      }
    });

    test('should not cause seizures with flashing content', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await chatPage.goto();
      await chatPage.expectChatLoaded();

      // Check that there are no rapidly flashing elements
      // This is a basic check - in practice, you'd need more sophisticated testing
      const flashingElements = page.locator('[class*="flash"], [class*="blink"]');
      await expect(flashingElements).toHaveCount(0);
    });
  });

  test.describe('Form Accessibility', () => {
    test('should have proper form labels', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.clickCreateCharacter();

      // Check that all form inputs have labels
      const inputs = page.locator('input, textarea, select');
      const inputCount = await inputs.count();

      for (let i = 0; i < inputCount; i++) {
        const input = inputs.nth(i);
        const id = await input.getAttribute('id');
        const ariaLabel = await input.getAttribute('aria-label');
        const ariaLabelledBy = await input.getAttribute('aria-labelledby');

        if (id) {
          // Should have associated label
          const label = page.locator(`label[for="${id}"]`);
          const hasLabel = await label.count() > 0;

          // Should have either label, aria-label, or aria-labelledby
          expect(hasLabel || ariaLabel || ariaLabelledBy).toBeTruthy();
        }
      }
    });

    test('should provide clear error messages', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.clickCreateCharacter();

      // Submit form without required fields
      await characterPage.saveCharacterButton.click();

      // Should show clear error messages
      const errorMessages = page.locator('.error, [data-testid="error"]');
      if (await errorMessages.count() > 0) {
        const errorText = await errorMessages.first().textContent();
        expect(errorText).toBeTruthy();
        expect(errorText?.length).toBeGreaterThan(5); // Should be descriptive
      }
    });

    test('should associate errors with form fields', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.clickCreateCharacter();

      // Submit form without required fields
      await characterPage.saveCharacterButton.click();

      // Check that errors are properly associated with fields
      const nameInput = page.locator('input[name="name"]');
      const ariaDescribedBy = await nameInput.getAttribute('aria-describedby');

      if (ariaDescribedBy) {
        const errorElement = page.locator(`#${ariaDescribedBy}`);
        await expect(errorElement).toBeVisible();
      }
    });
  });
});
