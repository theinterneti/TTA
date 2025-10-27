import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { DashboardPage } from '../page-objects/DashboardPage';
import { CharacterManagementPage } from '../page-objects/CharacterManagementPage';
import { ChatPage } from '../page-objects/ChatPage';
import { SettingsPage } from '../page-objects/SettingsPage';
import { testUsers } from '../fixtures/test-data';
import { setMobileViewport, setTabletViewport, setDesktopViewport } from '../utils/test-helpers';

test.describe('Responsive Design', () => {
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

  test.describe('Mobile Devices (375x667)', () => {
    test.beforeEach(async ({ page }) => {
      await setMobileViewport(page);
    });

    test('login page should work on mobile', async () => {
      await loginPage.goto();
      await loginPage.checkMobileLayout();
      await loginPage.expectLoginFormVisible();

      // Form should be properly sized
      const formBox = await loginPage.loginForm.boundingBox();
      expect(formBox?.width).toBeLessThan(400);
    });

    test('dashboard should adapt to mobile', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();
      await dashboardPage.checkMobileLayout();

      // Sections should stack vertically
      const quickActions = await dashboardPage.quickActionsSection.boundingBox();
      const characters = await dashboardPage.charactersSection.boundingBox();

      if (quickActions && characters) {
        expect(characters.y).toBeGreaterThan(quickActions.y + quickActions.height);
      }
    });

    test('character management should work on mobile', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.expectPageLoaded();
      await characterPage.checkMobileLayout();

      // Should automatically use list view on mobile
      const gridContainer = await characterPage.characterGrid.boundingBox();
      expect(gridContainer?.width).toBeLessThan(400);
    });

    test('character creation form should adapt to mobile', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.clickCreateCharacter();

      // Form should be properly sized for mobile
      const formBox = await characterPage.characterForm.boundingBox();
      expect(formBox?.width).toBeLessThan(400);

      // Form elements should stack vertically
      const nameInput = await characterPage.nameInput.boundingBox();
      const descriptionInput = await characterPage.descriptionInput.boundingBox();

      if (nameInput && descriptionInput) {
        expect(descriptionInput.y).toBeGreaterThan(nameInput.y + nameInput.height);
      }
    });

    test('chat interface should work on mobile', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await chatPage.goto();
      await chatPage.expectChatLoaded();
      await chatPage.checkMobileLayout();

      // Chat should take full screen
      const chatBox = await chatPage.chatContainer.boundingBox();
      expect(chatBox?.width).toBeLessThan(400);

      // Input should be properly sized
      const inputBox = await chatPage.messageInput.boundingBox();
      expect(inputBox?.width).toBeLessThan(350);
    });

    test('settings should work on mobile', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await settingsPage.goto();
      await settingsPage.expectPageLoaded();

      // Tabs should be scrollable on mobile
      const tabsBox = await settingsPage.tabNavigation.boundingBox();
      expect(tabsBox?.width).toBeLessThan(400);

      // Form elements should stack vertically
      await settingsPage.goToTherapeuticTab();
      const formElements = page.locator('input, select, textarea');

      if (await formElements.count() >= 2) {
        const first = await formElements.first().boundingBox();
        const second = await formElements.nth(1).boundingBox();

        if (first && second) {
          expect(second.y).toBeGreaterThan(first.y + first.height);
        }
      }
    });

    test('should handle virtual keyboard on mobile', async ({ page }) => {
      await loginPage.goto();
      await loginPage.usernameInput.focus();

      // Should maintain usability with virtual keyboard
      await expect(loginPage.usernameInput).toBeFocused();
      await expect(loginPage.loginButton).toBeVisible();
    });

    test('should support touch interactions', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Buttons should be large enough for touch
      const buttonBox = await dashboardPage.createCharacterButton.boundingBox();
      expect(buttonBox?.height).toBeGreaterThanOrEqual(44); // iOS minimum touch target
      expect(buttonBox?.width).toBeGreaterThanOrEqual(44);
    });
  });

  test.describe('Tablet Devices (768x1024)', () => {
    test.beforeEach(async ({ page }) => {
      await setTabletViewport(page);
    });

    test('login page should work on tablet', async () => {
      await loginPage.goto();
      await loginPage.expectLoginFormVisible();

      // Form should be centered and appropriately sized
      const formBox = await loginPage.loginForm.boundingBox();
      expect(formBox?.width).toBeLessThan(600);
      expect(formBox?.width).toBeGreaterThan(300);
    });

    test('dashboard should adapt to tablet', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Should use tablet-optimized layout
      await dashboardPage.expectQuickActionsVisible();
      await dashboardPage.expectCharactersSection();
    });

    test('character management should use grid on tablet', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.expectPageLoaded();

      // Should use grid layout on tablet
      const gridContainer = await characterPage.characterGrid.boundingBox();
      expect(gridContainer?.width).toBeGreaterThan(400);
      expect(gridContainer?.width).toBeLessThan(800);
    });

    test('chat interface should use tablet layout', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await chatPage.goto();
      await chatPage.expectChatLoaded();

      // Should have appropriate sizing for tablet
      const chatBox = await chatPage.chatContainer.boundingBox();
      expect(chatBox?.width).toBeGreaterThan(400);
      expect(chatBox?.width).toBeLessThan(800);
    });

    test('settings should show all tabs on tablet', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await settingsPage.goto();
      await settingsPage.expectPageLoaded();

      // All tabs should be visible without scrolling
      await expect(settingsPage.therapeuticTab).toBeVisible();
      await expect(settingsPage.modelsTab).toBeVisible();
      await expect(settingsPage.privacyTab).toBeVisible();
      await expect(settingsPage.notificationsTab).toBeVisible();
    });
  });

  test.describe('Desktop Devices (1280x720)', () => {
    test.beforeEach(async ({ page }) => {
      await setDesktopViewport(page);
    });

    test('login page should work on desktop', async () => {
      await loginPage.goto();
      await loginPage.expectLoginFormVisible();

      // Form should be centered with appropriate max-width
      const formBox = await loginPage.loginForm.boundingBox();
      expect(formBox?.width).toBeLessThan(500);
    });

    test('dashboard should use full desktop layout', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Should use multi-column layout
      await dashboardPage.expectQuickActionsVisible();
      await dashboardPage.expectCharactersSection();
      await dashboardPage.expectRecentSessions();
    });

    test('character management should use full grid', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.expectPageLoaded();

      // Should use full grid layout
      const gridContainer = await characterPage.characterGrid.boundingBox();
      expect(gridContainer?.width).toBeGreaterThan(800);
    });

    test('chat interface should use desktop layout', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await chatPage.goto();
      await chatPage.expectChatLoaded();

      // Should have sidebar or additional panels on desktop
      const chatBox = await chatPage.chatContainer.boundingBox();
      expect(chatBox?.width).toBeGreaterThan(800);
    });

    test('settings should show all content without scrolling', async () => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await settingsPage.goto();
      await settingsPage.expectPageLoaded();

      // All tabs should be visible
      const tabs = [
        settingsPage.therapeuticTab,
        settingsPage.modelsTab,
        settingsPage.privacyTab,
        settingsPage.notificationsTab,
        settingsPage.accessibilityTab,
        settingsPage.crisisTab,
      ];

      for (const tab of tabs) {
        await expect(tab).toBeVisible();
      }
    });
  });

  test.describe('Breakpoint Transitions', () => {
    test('should transition smoothly between breakpoints', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Start at desktop
      await setDesktopViewport(page);
      await dashboardPage.expectDashboardLoaded();

      // Transition to tablet
      await setTabletViewport(page);
      await dashboardPage.expectDashboardLoaded();

      // Transition to mobile
      await setMobileViewport(page);
      await dashboardPage.expectDashboardLoaded();
    });

    test('should maintain functionality across breakpoints', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();

      // Test functionality at different breakpoints
      const viewports = [
        { width: 1280, height: 720 }, // Desktop
        { width: 768, height: 1024 },  // Tablet
        { width: 375, height: 667 },   // Mobile
      ];

      for (const viewport of viewports) {
        await page.setViewportSize(viewport);
        await characterPage.expectPageLoaded();

        // Core functionality should work at all breakpoints
        await expect(characterPage.createCharacterButton).toBeVisible();
        await expect(characterPage.createCharacterButton).toBeEnabled();
      }
    });
  });

  test.describe('Content Reflow', () => {
    test('should reflow content appropriately', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Test at 320px width (minimum mobile width)
      await page.setViewportSize({ width: 320, height: 568 });
      await dashboardPage.expectDashboardLoaded();

      // Content should still be accessible
      await expect(dashboardPage.createCharacterButton).toBeVisible();
      await expect(dashboardPage.exploreWorldsButton).toBeVisible();
    });

    test('should handle long content gracefully', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await chatPage.goto();
      await chatPage.expectChatLoaded();

      // Send a very long message
      const longMessage = 'This is a very long message that should wrap properly on all screen sizes. '.repeat(20);
      await chatPage.sendMessage(longMessage);

      // Test at different viewport sizes
      const viewports = [
        { width: 320, height: 568 },
        { width: 768, height: 1024 },
        { width: 1280, height: 720 },
      ];

      for (const viewport of viewports) {
        await page.setViewportSize(viewport);
        await chatPage.expectMessageSent(longMessage);

        // Message should be visible and properly wrapped
        const messageElement = chatPage.userMessages.filter({ hasText: longMessage });
        await expect(messageElement).toBeVisible();
      }
    });
  });

  test.describe('Orientation Changes', () => {
    test('should handle portrait to landscape transition', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await dashboardPage.expectDashboardLoaded();

      // Start in portrait
      await page.setViewportSize({ width: 375, height: 667 });
      await dashboardPage.expectDashboardLoaded();

      // Switch to landscape
      await page.setViewportSize({ width: 667, height: 375 });
      await dashboardPage.expectDashboardLoaded();

      // Interface should adapt to landscape
      await expect(dashboardPage.createCharacterButton).toBeVisible();
    });

    test('should maintain state during orientation changes', async ({ page }) => {
      await loginPage.goto();
      await loginPage.login(testUsers.default);
      await characterPage.goto();
      await characterPage.clickCreateCharacter();

      // Fill form in portrait
      await page.setViewportSize({ width: 375, height: 667 });
      await characterPage.nameInput.fill('Test Character');

      // Switch to landscape
      await page.setViewportSize({ width: 667, height: 375 });

      // Form data should be preserved
      await expect(characterPage.nameInput).toHaveValue('Test Character');
      await expect(characterPage.characterForm).toBeVisible();
    });
  });

  test.describe('Performance on Different Devices', () => {
    test('should load quickly on mobile', async ({ page }) => {
      await setMobileViewport(page);

      const startTime = Date.now();
      await loginPage.goto();
      await loginPage.expectLoginFormVisible();
      const loadTime = Date.now() - startTime;

      // Should load within reasonable time on mobile
      expect(loadTime).toBeLessThan(5000);
    });

    test('should be responsive to interactions on mobile', async ({ page }) => {
      await setMobileViewport(page);
      await loginPage.goto();

      const startTime = Date.now();
      await loginPage.usernameInput.click();
      await loginPage.usernameInput.fill('test');
      const interactionTime = Date.now() - startTime;

      // Interactions should be responsive
      expect(interactionTime).toBeLessThan(1000);
    });
  });

  test.describe('Cross-Device Consistency', () => {
    test('should maintain visual consistency across devices', async ({ page }) => {
      await loginPage.goto();

      // Test visual consistency at different sizes
      const viewports = [
        { width: 375, height: 667, name: 'mobile' },
        { width: 768, height: 1024, name: 'tablet' },
        { width: 1280, height: 720, name: 'desktop' },
      ];

      for (const viewport of viewports) {
        await page.setViewportSize(viewport);
        await loginPage.expectLoginFormVisible();

        // Take screenshot for visual comparison
        await expect(page).toHaveScreenshot(`login-${viewport.name}.png`);
      }
    });

    test('should maintain functional consistency across devices', async ({ page }) => {
      const testFlow = async () => {
        await loginPage.goto();
        await loginPage.login(testUsers.default);
        await dashboardPage.expectDashboardLoaded();
        await characterPage.goto();
        await characterPage.expectPageLoaded();
      };

      // Test the same flow on different devices
      const viewports = [
        { width: 375, height: 667 },
        { width: 768, height: 1024 },
        { width: 1280, height: 720 },
      ];

      for (const viewport of viewports) {
        await page.setViewportSize(viewport);
        await testFlow();
      }
    });
  });
});
