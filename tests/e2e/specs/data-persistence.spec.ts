import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { DashboardPage } from '../page-objects/DashboardPage';
import { CharacterManagementPage } from '../page-objects/CharacterManagementPage';
import { PreferencesPage } from '../page-objects/PreferencesPage';
import { ChatPage } from '../page-objects/ChatPage';
import { testUsers, generateRandomCharacter } from '../fixtures/test-data';
import { mockApiResponse, clearLocalStorage, clearSessionStorage } from '../utils/test-helpers';

test.describe('Data Persistence', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;
  let characterPage: CharacterManagementPage;
  let preferencesPage: PreferencesPage;
  let chatPage: ChatPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    characterPage = new CharacterManagementPage(page);
    preferencesPage = new PreferencesPage(page);
    chatPage = new ChatPage(page);

    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
  });

  test.describe('Session Persistence', () => {
    test('should maintain user session across page refreshes', async ({ page }) => {
      await dashboardPage.goto();
      await dashboardPage.expectDashboardLoaded();
      
      // Refresh the page
      await page.reload();
      
      // Should still be logged in
      await dashboardPage.expectDashboardLoaded();
      await expect(page).not.toHaveURL(/login|auth/);
    });

    test('should maintain user session across browser tabs', async ({ context }) => {
      await dashboardPage.goto();
      await dashboardPage.expectDashboardLoaded();
      
      // Open new tab
      const newTab = await context.newPage();
      await newTab.goto('/dashboard');
      
      // Should be logged in on new tab
      const newDashboardPage = new DashboardPage(newTab);
      await newDashboardPage.expectDashboardLoaded();
      
      await newTab.close();
    });

    test('should handle session expiration gracefully', async ({ page }) => {
      await dashboardPage.goto();
      
      // Mock session expiration
      await mockApiResponse(page, '**/auth/verify', { valid: false }, 401);
      
      // Try to perform an action that requires authentication
      await dashboardPage.navigateToCharacters();
      
      // Should redirect to login
      await expect(page).toHaveURL(/login|auth/);
      await expect(page.locator('text=Session expired, text=Please log in again')).toBeVisible();
    });

    test('should restore session after temporary network issues', async ({ page }) => {
      await dashboardPage.goto();
      await dashboardPage.expectDashboardLoaded();
      
      // Simulate temporary network failure
      await page.route('**/api/**', route => {
        route.fulfill({ status: 500 });
      });
      
      // Try to navigate
      await dashboardPage.navigateToCharacters();
      
      // Should show error but maintain session
      await expect(page.locator('text=Network error')).toBeVisible();
      
      // Restore network
      await page.unroute('**/api/**');
      await page.reload();
      
      // Should still be logged in
      await dashboardPage.expectDashboardLoaded();
    });
  });

  test.describe('Form Data Persistence', () => {
    test('should save form data during character creation', async ({ page }) => {
      await characterPage.goto();
      await characterPage.clickCreateCharacter();
      
      // Fill form partially
      const testCharacter = generateRandomCharacter();
      await characterPage.nameInput.fill(testCharacter.name);
      await characterPage.descriptionInput.fill(testCharacter.appearance.description);
      
      // Navigate away without saving
      await dashboardPage.goto();
      
      // Return to character creation
      await characterPage.goto();
      await characterPage.clickCreateCharacter();
      
      // Form data should be restored
      await expect(characterPage.nameInput).toHaveValue(testCharacter.name);
      await expect(characterPage.descriptionInput).toHaveValue(testCharacter.appearance.description);
    });

    test('should save preferences changes locally before server sync', async ({ page }) => {
      await preferencesPage.goto();
      
      // Make changes
      await preferencesPage.setIntensityLevel(8);
      await preferencesPage.clickTab('character');
      await preferencesPage.setCharacterName('TestCharacter');
      
      // Simulate network failure before saving
      await page.route('**/players/*/preferences', route => {
        route.fulfill({ status: 500 });
      });
      
      // Try to save (will fail)
      await preferencesPage.savePreferences();
      
      // Refresh page
      await page.reload();
      
      // Changes should be preserved locally
      await preferencesPage.expectIntensityLevel(8);
      await preferencesPage.clickTab('character');
      await preferencesPage.expectCharacterName('TestCharacter');
      
      // Should show unsaved changes indicator
      await preferencesPage.expectUnsavedChangesWarning();
    });

    test('should handle form auto-save functionality', async ({ page }) => {
      await characterPage.goto();
      await characterPage.clickCreateCharacter();
      
      const testCharacter = generateRandomCharacter();
      
      // Enable auto-save mock
      await mockApiResponse(page, '**/players/*/characters/draft', {
        draft_id: 'draft-1',
        saved_at: new Date().toISOString(),
      }, 200, 'POST');
      
      // Fill form
      await characterPage.nameInput.fill(testCharacter.name);
      
      // Wait for auto-save
      await page.waitForTimeout(2000);
      
      // Should show auto-save indicator
      await expect(page.locator('text=Auto-saved, text=Draft saved')).toBeVisible();
    });

    test('should restore draft data on form reload', async ({ page }) => {
      // Mock existing draft
      await mockApiResponse(page, '**/players/*/characters/draft', {
        draft_id: 'draft-1',
        name: 'Draft Character',
        description: 'Draft description',
        created_at: new Date().toISOString(),
      });
      
      await characterPage.goto();
      await characterPage.clickCreateCharacter();
      
      // Should show draft restoration option
      await expect(page.locator('text=Restore draft, text=Continue editing')).toBeVisible();
      
      // Click restore
      await page.locator('button:has-text("Restore draft")').click();
      
      // Form should be populated with draft data
      await expect(characterPage.nameInput).toHaveValue('Draft Character');
      await expect(characterPage.descriptionInput).toHaveValue('Draft description');
    });
  });

  test.describe('Chat History Persistence', () => {
    test('should persist chat messages across sessions', async ({ page }) => {
      await chatPage.goto();
      await chatPage.expectChatLoaded();
      
      // Send a message
      await mockApiResponse(page, '**/chat/send', {
        message_id: 'msg-1',
        response: 'Test response',
      }, 200, 'POST');
      
      await chatPage.sendMessage('Hello, this is a test message');
      await chatPage.expectMessageDisplayed('Hello, this is a test message');
      
      // Refresh page
      await page.reload();
      await chatPage.expectChatLoaded();
      
      // Message should still be visible
      await chatPage.expectMessageDisplayed('Hello, this is a test message');
    });

    test('should handle chat history pagination', async ({ page }) => {
      // Mock chat history with pagination
      await mockApiResponse(page, '**/chat/history', {
        messages: Array.from({ length: 20 }, (_, i) => ({
          message_id: `msg-${i}`,
          content: `Message ${i}`,
          timestamp: new Date().toISOString(),
          sender: i % 2 === 0 ? 'user' : 'assistant',
        })),
        has_more: true,
        next_cursor: 'cursor-1',
      });
      
      await chatPage.goto();
      await chatPage.expectChatLoaded();
      
      // Should show recent messages
      await chatPage.expectMessageDisplayed('Message 19');
      
      // Load more messages
      await chatPage.loadMoreMessages();
      
      // Should show older messages
      await chatPage.expectMessageDisplayed('Message 0');
    });

    test('should sync chat state across multiple tabs', async ({ context, page }) => {
      await chatPage.goto();
      await chatPage.expectChatLoaded();
      
      // Send message in first tab
      await mockApiResponse(page, '**/chat/send', {
        message_id: 'msg-1',
        response: 'Response from tab 1',
      }, 200, 'POST');
      
      await chatPage.sendMessage('Message from tab 1');
      
      // Open second tab
      const secondTab = await context.newPage();
      const secondChatPage = new ChatPage(secondTab);
      await secondChatPage.goto();
      await secondChatPage.expectChatLoaded();
      
      // Should see message from first tab
      await secondChatPage.expectMessageDisplayed('Message from tab 1');
      
      await secondTab.close();
    });

    test('should handle offline message queuing', async ({ page }) => {
      await chatPage.goto();
      await chatPage.expectChatLoaded();
      
      // Go offline
      await page.context().setOffline(true);
      
      // Try to send message
      await chatPage.sendMessage('Offline message');
      
      // Should show queued message indicator
      await expect(page.locator('text=Queued, text=Pending')).toBeVisible();
      
      // Go back online
      await page.context().setOffline(false);
      
      // Mock successful send
      await mockApiResponse(page, '**/chat/send', {
        message_id: 'msg-offline',
        response: 'Message sent successfully',
      }, 200, 'POST');
      
      // Message should be sent automatically
      await expect(page.locator('text=Sent, text=Delivered')).toBeVisible();
    });
  });

  test.describe('User Preferences Persistence', () => {
    test('should persist UI preferences across sessions', async ({ page }) => {
      await dashboardPage.goto();
      
      // Change UI preferences (e.g., theme, layout)
      await dashboardPage.openUserMenu();
      await page.locator('button:has-text("Dark Mode")').click();
      
      // Refresh page
      await page.reload();
      
      // Dark mode should be maintained
      await expect(page.locator('body')).toHaveClass(/dark-mode|dark-theme/);
    });

    test('should persist filter and sort preferences', async ({ page }) => {
      await characterPage.goto();
      
      // Set filters
      await characterPage.filterByType('PROTAGONIST');
      await characterPage.sortBy('name');
      
      // Navigate away and back
      await dashboardPage.goto();
      await characterPage.goto();
      
      // Filters should be maintained
      await expect(characterPage.typeFilter).toHaveValue('PROTAGONIST');
      await expect(characterPage.sortSelect).toHaveValue('name');
    });

    test('should persist language preferences', async ({ page }) => {
      await dashboardPage.goto();
      
      // Change language
      await dashboardPage.openUserMenu();
      await page.locator('select[name="language"]').selectOption('es');
      
      // Refresh page
      await page.reload();
      
      // Language should be maintained
      await expect(page.locator('html')).toHaveAttribute('lang', 'es');
    });

    test('should sync preferences across devices', async ({ page }) => {
      await preferencesPage.goto();
      
      // Change preferences
      await preferencesPage.setIntensityLevel(9);
      await preferencesPage.savePreferences();
      
      // Mock sync to server
      await mockApiResponse(page, '**/players/*/preferences/sync', {
        synced_at: new Date().toISOString(),
        devices_updated: 2,
      }, 200, 'POST');
      
      // Should show sync confirmation
      await expect(page.locator('text=Synced across devices')).toBeVisible();
    });
  });

  test.describe('Local Storage Management', () => {
    test('should handle localStorage quota exceeded', async ({ page }) => {
      // Fill localStorage to capacity
      await page.evaluate(() => {
        try {
          const largeData = 'x'.repeat(5 * 1024 * 1024); // 5MB
          for (let i = 0; i < 10; i++) {
            localStorage.setItem(`large-item-${i}`, largeData);
          }
        } catch (e) {
          // Expected to fail due to quota
        }
      });
      
      await characterPage.goto();
      await characterPage.clickCreateCharacter();
      
      const testCharacter = generateRandomCharacter();
      await characterPage.nameInput.fill(testCharacter.name);
      
      // Should handle storage quota gracefully
      await expect(page.locator('text=Storage full, text=Unable to save locally')).toBeVisible();
    });

    test('should clean up old data automatically', async ({ page }) => {
      // Add old data to localStorage
      await page.evaluate(() => {
        const oldDate = new Date();
        oldDate.setDate(oldDate.getDate() - 30); // 30 days ago
        
        localStorage.setItem('old-draft-1', JSON.stringify({
          data: 'old draft data',
          timestamp: oldDate.toISOString(),
        }));
        
        localStorage.setItem('recent-draft-1', JSON.stringify({
          data: 'recent draft data',
          timestamp: new Date().toISOString(),
        }));
      });
      
      await dashboardPage.goto();
      
      // Should clean up old data
      const oldData = await page.evaluate(() => localStorage.getItem('old-draft-1'));
      const recentData = await page.evaluate(() => localStorage.getItem('recent-draft-1'));
      
      expect(oldData).toBeNull();
      expect(recentData).not.toBeNull();
    });

    test('should handle localStorage unavailability', async ({ page }) => {
      // Mock localStorage being unavailable
      await page.addInitScript(() => {
        Object.defineProperty(window, 'localStorage', {
          value: {
            getItem: () => { throw new Error('localStorage unavailable'); },
            setItem: () => { throw new Error('localStorage unavailable'); },
            removeItem: () => { throw new Error('localStorage unavailable'); },
            clear: () => { throw new Error('localStorage unavailable'); },
            length: 0,
            key: () => null,
          },
          writable: false,
        });
      });
      
      await dashboardPage.goto();
      
      // Should handle gracefully
      await dashboardPage.expectDashboardLoaded();
      await expect(page.locator('text=Local storage unavailable')).toBeVisible();
    });

    test('should migrate data between versions', async ({ page }) => {
      // Add old version data
      await page.evaluate(() => {
        localStorage.setItem('app-version', '1.0.0');
        localStorage.setItem('user-preferences', JSON.stringify({
          theme: 'dark',
          language: 'en',
        }));
      });
      
      await dashboardPage.goto();
      
      // Should migrate to new version format
      const newVersion = await page.evaluate(() => localStorage.getItem('app-version'));
      const migratedPrefs = await page.evaluate(() => 
        JSON.parse(localStorage.getItem('user-preferences-v2') || '{}')
      );
      
      expect(newVersion).not.toBe('1.0.0');
      expect(migratedPrefs).toHaveProperty('theme', 'dark');
    });
  });

  test.describe('Data Synchronization', () => {
    test('should handle conflicts between local and server data', async ({ page }) => {
      // Set up conflict scenario
      await preferencesPage.goto();
      
      // Make local changes
      await preferencesPage.setIntensityLevel(7);
      
      // Mock server having different data
      await mockApiResponse(page, '**/players/*/preferences', {
        intensity_level: 5,
        updated_at: new Date().toISOString(),
      });
      
      // Try to save
      await preferencesPage.savePreferences();
      
      // Should show conflict resolution dialog
      await expect(page.locator('text=Data conflict, text=Choose version')).toBeVisible();
      
      // Should provide options to resolve
      await expect(page.locator('button:has-text("Use Local"), button:has-text("Use Server")')).toBeVisible();
    });

    test('should handle optimistic updates', async ({ page }) => {
      await characterPage.goto();
      
      const testCharacter = generateRandomCharacter();
      
      // Mock slow server response
      await page.route('**/players/*/characters', route => {
        setTimeout(() => {
          route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              character_id: 'new-char-1',
              ...JSON.parse(route.request().postData() || '{}'),
            }),
          });
        }, 2000);
      });
      
      await characterPage.createCharacter(testCharacter);
      
      // Should show character immediately (optimistic update)
      await characterPage.expectCharacterCreated(testCharacter.name);
      
      // Should show pending indicator
      await expect(page.locator('text=Saving, text=Pending')).toBeVisible();
      
      // After server response, should show confirmed
      await expect(page.locator('text=Saved, text=Confirmed')).toBeVisible();
    });

    test('should handle sync failures gracefully', async ({ page }) => {
      await preferencesPage.goto();
      
      // Make changes
      await preferencesPage.setIntensityLevel(8);
      
      // Mock sync failure
      await mockApiResponse(page, '**/players/*/preferences', {
        error: 'Sync failed',
      }, 500, 'PUT');
      
      await preferencesPage.savePreferences();
      
      // Should show sync failure message
      await expect(page.locator('text=Sync failed, text=Changes saved locally')).toBeVisible();
      
      // Should provide retry option
      await expect(page.locator('button:has-text("Retry Sync")')).toBeVisible();
    });

    test('should batch multiple changes for efficiency', async ({ page }) => {
      await preferencesPage.goto();
      
      let requestCount = 0;
      await page.route('**/players/*/preferences', route => {
        requestCount++;
        route.continue();
      });
      
      // Make multiple rapid changes
      await preferencesPage.setIntensityLevel(6);
      await preferencesPage.clickTab('character');
      await preferencesPage.setCharacterName('BatchTest');
      await preferencesPage.clickTab('approach');
      await preferencesPage.selectTherapeuticApproach('CBT');
      
      // Wait for batching
      await page.waitForTimeout(1000);
      
      // Should batch requests instead of sending individually
      expect(requestCount).toBeLessThan(3); // Should be batched
    });
  });
});
