// Logseq: [[TTA.dev/Tests/E2e/Specs/Error-handling.spec]]
import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { DashboardPage } from '../page-objects/DashboardPage';
import { CharacterManagementPage } from '../page-objects/CharacterManagementPage';
import { ChatPage } from '../page-objects/ChatPage';
import { WorldSelectionPage } from '../page-objects/WorldSelectionPage';
import { PreferencesPage } from '../page-objects/PreferencesPage';
import { testUsers, generateRandomCharacter } from '../fixtures/test-data';
import { mockApiResponse, mockNetworkFailure, mockApiError } from '../utils/test-helpers';

test.describe('Error Handling', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;
  let characterPage: CharacterManagementPage;
  let chatPage: ChatPage;
  let worldSelectionPage: WorldSelectionPage;
  let preferencesPage: PreferencesPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    characterPage = new CharacterManagementPage(page);
    chatPage = new ChatPage(page);
    worldSelectionPage = new WorldSelectionPage(page);
    preferencesPage = new PreferencesPage(page);

    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
  });

  test.describe('Network Errors', () => {
    test('should handle complete network failure gracefully', async ({ page }) => {
      await mockNetworkFailure(page, '**/*');

      await dashboardPage.goto();

      // Should show network error message
      await expect(page.locator('text=Network error, text=Connection failed, text=Offline')).toBeVisible();

      // Should provide retry mechanism
      await expect(page.locator('button:has-text("Retry"), button:has-text("Try Again")')).toBeVisible();
    });

    test('should handle API server errors (5xx)', async ({ page }) => {
      await mockApiError(page, '**/players/**', 500);

      await dashboardPage.goto();

      // Should show server error message
      await expect(page.locator('text=Server error, text=Something went wrong')).toBeVisible();

      // Should not expose technical details to user
      await expect(page.locator('text=500, text=Internal Server Error')).not.toBeVisible();
    });

    test('should handle API client errors (4xx)', async ({ page }) => {
      await mockApiError(page, '**/players/**', 404);

      await dashboardPage.goto();

      // Should show appropriate user-friendly message
      await expect(page.locator('text=Not found, text=Data not available')).toBeVisible();
    });

    test('should handle authentication errors', async ({ page }) => {
      await mockApiError(page, '**/auth/**', 401);

      await dashboardPage.goto();

      // Should redirect to login or show auth error
      await expect(page).toHaveURL(/login|auth/);
      await expect(page.locator('text=Session expired, text=Please log in')).toBeVisible();
    });

    test('should handle authorization errors', async ({ page }) => {
      await mockApiError(page, '**/players/**', 403);

      await dashboardPage.goto();

      // Should show access denied message
      await expect(page.locator('text=Access denied, text=Not authorized')).toBeVisible();
    });

    test('should handle timeout errors', async ({ page }) => {
      // Simulate timeout by never resolving requests
      await page.route('**/players/**', route => {
        // Never resolve to simulate timeout
      });

      await dashboardPage.goto();

      // Should show loading state initially, then timeout message
      await expect(page.locator('.loading, .spinner')).toBeVisible();

      // After timeout period, should show timeout message
      await page.waitForTimeout(10000); // Wait for timeout
      await expect(page.locator('text=Request timeout, text=Taking longer than expected')).toBeVisible();
    });

    test('should handle intermittent network issues', async ({ page }) => {
      let requestCount = 0;

      await page.route('**/players/**', route => {
        requestCount++;
        if (requestCount <= 2) {
          // Fail first two requests
          route.fulfill({ status: 500 });
        } else {
          // Succeed on third request
          route.continue();
        }
      });

      await dashboardPage.goto();

      // Should eventually succeed after retries
      await dashboardPage.expectDashboardLoaded();
    });
  });

  test.describe('Form Validation Errors', () => {
    test('should handle character creation validation errors', async ({ page }) => {
      await characterPage.goto();
      await characterPage.clickCreateCharacter();

      // Try to submit empty form
      await characterPage.submitCharacterForm();

      // Should show validation errors
      await expect(page.locator('text=Name is required')).toBeVisible();
      await expect(page.locator('text=Description is required')).toBeVisible();
    });

    test('should handle preferences validation errors', async ({ page }) => {
      await preferencesPage.goto();

      // Set invalid values
      await preferencesPage.clickTab('character');
      await preferencesPage.setCharacterName(''); // Empty name

      await preferencesPage.savePreferences();

      // Should show validation errors
      await expect(page.locator('text=Character name is required')).toBeVisible();
    });

    test('should handle real-time validation', async ({ page }) => {
      await characterPage.goto();
      await characterPage.clickCreateCharacter();

      // Enter invalid data
      await characterPage.nameInput.fill('A'); // Too short
      await characterPage.nameInput.blur();

      // Should show real-time validation
      await expect(page.locator('text=Name must be at least 2 characters')).toBeVisible();
    });

    test('should handle server-side validation errors', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/characters', {
        error: 'Character name already exists',
        field: 'name',
      }, 400, 'POST');

      await characterPage.goto();
      const testCharacter = generateRandomCharacter();
      await characterPage.createCharacter(testCharacter);

      // Should show server validation error
      await expect(page.locator('text=Character name already exists')).toBeVisible();
    });
  });

  test.describe('WebSocket Errors', () => {
    test('should handle WebSocket connection failures', async ({ page }) => {
      // Mock WebSocket connection failure
      await page.addInitScript(() => {
        const originalWebSocket = window.WebSocket;
        window.WebSocket = class extends originalWebSocket {
          constructor(url: string | URL, protocols?: string | string[]) {
            super(url, protocols);
            setTimeout(() => {
              this.dispatchEvent(new Event('error'));
            }, 100);
          }
        };
      });

      await chatPage.goto();

      // Should show WebSocket connection error
      await expect(page.locator('text=Connection failed, text=Chat unavailable')).toBeVisible();

      // Should provide reconnection option
      await expect(page.locator('button:has-text("Reconnect")')).toBeVisible();
    });

    test('should handle WebSocket disconnections', async ({ page }) => {
      await chatPage.goto();
      await chatPage.expectChatLoaded();

      // Simulate WebSocket disconnection
      await page.evaluate(() => {
        const wsEvent = new Event('close');
        (window as any).chatWebSocket?.dispatchEvent(wsEvent);
      });

      // Should show disconnection message
      await expect(page.locator('text=Connection lost, text=Reconnecting')).toBeVisible();

      // Should attempt automatic reconnection
      await expect(page.locator('text=Reconnected, text=Connection restored')).toBeVisible();
    });

    test('should handle message sending failures', async ({ page }) => {
      await chatPage.goto();
      await chatPage.expectChatLoaded();

      // Mock message sending failure
      await mockApiError(page, '**/chat/send', 500);

      await chatPage.sendMessage('Test message');

      // Should show message sending error
      await expect(page.locator('text=Failed to send message')).toBeVisible();

      // Should provide retry option
      await expect(page.locator('button:has-text("Retry")')).toBeVisible();
    });
  });

  test.describe('Data Loading Errors', () => {
    test('should handle empty data states', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/characters', []);

      await characterPage.goto();

      // Should show empty state message
      await expect(page.locator('text=No characters yet, text=Create your first character')).toBeVisible();

      // Should provide action to create first item
      await expect(page.locator('button:has-text("Create Character")')).toBeVisible();
    });

    test('should handle corrupted data', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/characters', 'invalid json');

      await characterPage.goto();

      // Should show data error message
      await expect(page.locator('text=Data error, text=Unable to load')).toBeVisible();
    });

    test('should handle partial data loading failures', async ({ page }) => {
      // Mock successful main data but failed secondary data
      await mockApiResponse(page, '**/players/*/characters', [
        { character_id: 'char-1', name: 'Test Character' }
      ]);
      await mockApiError(page, '**/characters/*/details', 500);

      await characterPage.goto();

      // Should show main data but indicate secondary data failed
      await expect(page.locator('text=Test Character')).toBeVisible();
      await expect(page.locator('text=Some details unavailable')).toBeVisible();
    });
  });

  test.describe('User Input Errors', () => {
    test('should handle invalid file uploads', async ({ page }) => {
      await preferencesPage.goto();
      await preferencesPage.clickImport();

      // Try to upload invalid file type
      const invalidFile = await page.locator('input[type="file"]');
      await invalidFile.setInputFiles({
        name: 'test.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('invalid content'),
      });

      // Should show file type error
      await expect(page.locator('text=Invalid file type, text=Please select a JSON file')).toBeVisible();
    });

    test('should handle malformed file content', async ({ page }) => {
      await preferencesPage.goto();
      await preferencesPage.clickImport();

      // Upload file with invalid JSON
      const invalidJsonFile = await page.locator('input[type="file"]');
      await invalidJsonFile.setInputFiles({
        name: 'preferences.json',
        mimeType: 'application/json',
        buffer: Buffer.from('{ invalid json }'),
      });

      await preferencesPage.importConfirmButton.click();

      // Should show parsing error
      await expect(page.locator('text=Invalid file format, text=Unable to parse')).toBeVisible();
    });

    test('should handle extremely long input', async ({ page }) => {
      await characterPage.goto();
      await characterPage.clickCreateCharacter();

      // Enter extremely long text
      const longText = 'A'.repeat(10000);
      await characterPage.nameInput.fill(longText);

      // Should handle gracefully (truncate or show error)
      await expect(page.locator('text=Input too long, text=Maximum length exceeded')).toBeVisible();
    });

    test('should handle special characters and XSS attempts', async ({ page }) => {
      await characterPage.goto();
      await characterPage.clickCreateCharacter();

      // Try to enter script tag
      const xssAttempt = '<script>alert("xss")</script>';
      await characterPage.nameInput.fill(xssAttempt);
      await characterPage.submitCharacterForm();

      // Should sanitize input and not execute script
      await expect(page.locator('script')).toHaveCount(0);

      // Should show sanitized or rejected input message
      await expect(page.locator('text=Invalid characters, text=Special characters not allowed')).toBeVisible();
    });
  });

  test.describe('Browser Compatibility Errors', () => {
    test('should handle unsupported browser features', async ({ page }) => {
      // Mock missing WebSocket support
      await page.addInitScript(() => {
        delete (window as any).WebSocket;
      });

      await chatPage.goto();

      // Should show browser compatibility message
      await expect(page.locator('text=Browser not supported, text=Please update your browser')).toBeVisible();
    });

    test('should handle localStorage unavailability', async ({ page }) => {
      // Mock localStorage being unavailable
      await page.addInitScript(() => {
        Object.defineProperty(window, 'localStorage', {
          value: null,
          writable: false,
        });
      });

      await dashboardPage.goto();

      // Should handle gracefully and show warning
      await expect(page.locator('text=Storage unavailable, text=Some features may not work')).toBeVisible();
    });

    test('should handle JavaScript disabled scenarios', async ({ page }) => {
      // This test would typically be run with JavaScript disabled
      // For now, we'll test that critical content is available without JS

      await page.goto('/dashboard');

      // Should show basic content even without JavaScript
      await expect(page.locator('h1, h2, main')).toBeVisible();

      // Should show noscript message
      await expect(page.locator('noscript')).toBeVisible();
    });
  });

  test.describe('Recovery Mechanisms', () => {
    test('should provide retry mechanisms for failed operations', async ({ page }) => {
      await mockApiError(page, '**/players/*/characters', 500);

      await characterPage.goto();

      // Should show retry button
      const retryButton = page.locator('button:has-text("Retry"), button:has-text("Try Again")');
      await expect(retryButton).toBeVisible();

      // Mock successful retry
      await mockApiResponse(page, '**/players/*/characters', []);

      await retryButton.click();

      // Should succeed on retry
      await characterPage.expectCharacterListLoaded();
    });

    test('should provide fallback content for failed components', async ({ page }) => {
      await mockApiError(page, '**/players/*/progress', 500);

      await dashboardPage.goto();

      // Should show fallback content instead of broken component
      await expect(page.locator('text=Progress data unavailable')).toBeVisible();
      await expect(page.locator('text=Try refreshing the page')).toBeVisible();
    });

    test('should maintain user session during errors', async ({ page }) => {
      await dashboardPage.goto();

      // Simulate temporary network error
      await mockNetworkFailure(page, '**/api/**');

      // Try to navigate
      await dashboardPage.navigateToCharacters();

      // Should show error but maintain session
      await expect(page.locator('text=Network error')).toBeVisible();

      // Restore network
      await page.unroute('**/api/**');

      // Should be able to continue without re-login
      await page.reload();
      await dashboardPage.expectDashboardLoaded();
    });

    test('should provide graceful degradation', async ({ page }) => {
      // Mock advanced features failing
      await mockApiError(page, '**/ai/**', 503);

      await chatPage.goto();

      // Should still allow basic chat functionality
      await expect(page.locator('textarea, input[type="text"]')).toBeVisible();

      // Should show degraded mode message
      await expect(page.locator('text=Advanced features unavailable, text=Basic mode')).toBeVisible();
    });

    test('should handle progressive enhancement failures', async ({ page }) => {
      // Mock enhanced features failing to load
      await page.route('**/enhanced-features.js', route => {
        route.fulfill({ status: 404 });
      });

      await dashboardPage.goto();

      // Should still provide basic functionality
      await dashboardPage.expectDashboardLoaded();

      // Enhanced features should degrade gracefully
      await expect(page.locator('text=Some features may be limited')).toBeVisible();
    });
  });

  test.describe('Error Reporting and Logging', () => {
    test('should log errors for debugging', async ({ page }) => {
      const consoleErrors: string[] = [];

      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });

      await mockApiError(page, '**/players/**', 500);
      await dashboardPage.goto();

      // Should log error details for debugging
      expect(consoleErrors.some(error => error.includes('API Error'))).toBe(true);
    });

    test('should not expose sensitive information in errors', async ({ page }) => {
      await mockApiError(page, '**/players/**', 500);
      await dashboardPage.goto();

      // Should not show sensitive technical details
      await expect(page.locator('text=stack trace, text=database, text=server path')).not.toBeVisible();

      // Should show user-friendly error messages
      await expect(page.locator('text=Something went wrong, text=Please try again')).toBeVisible();
    });

    test('should provide error reporting mechanism', async ({ page }) => {
      await mockApiError(page, '**/players/**', 500);
      await dashboardPage.goto();

      // Should provide way to report error
      await expect(page.locator('button:has-text("Report Issue"), a:has-text("Contact Support")')).toBeVisible();
    });
  });
});
