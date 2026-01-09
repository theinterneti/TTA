// Logseq: [[TTA.dev/Tests/E2e/Specs/Dashboard.spec]]
import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { DashboardPage } from '../page-objects/DashboardPage';
import { testUsers } from '../fixtures/test-data';

test.describe('Dashboard', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);

    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
    await dashboardPage.expectDashboardLoaded();
  });

  test.describe('Dashboard Layout', () => {
    test('should display all main sections', async () => {
      await dashboardPage.expectDashboardLoaded();
      await dashboardPage.expectQuickActionsVisible();
      await dashboardPage.expectCharactersSection();
      await dashboardPage.expectRecentSessions();
      await dashboardPage.expectProgressSection();
    });

    test('should show welcome message with username', async () => {
      await dashboardPage.expectWelcomeMessage(testUsers.default.username);
    });

    test('should display quick action buttons', async () => {
      await expect(dashboardPage.createCharacterButton).toBeVisible();
      await expect(dashboardPage.exploreWorldsButton).toBeVisible();
      await expect(dashboardPage.continueSessionButton).toBeVisible();
    });
  });

  test.describe('New User Experience', () => {
    test('should show getting started content for new users', async ({ page }) => {
      // Mock empty user data
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [],
            recent_sessions: [],
            progress: null,
          }),
        });
      });

      await dashboardPage.goto();
      await dashboardPage.expectNewUserExperience();
    });

    test('should emphasize character creation for new users', async ({ page }) => {
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [],
            recent_sessions: [],
            progress: null,
          }),
        });
      });

      await dashboardPage.goto();
      await expect(dashboardPage.createCharacterButton).toContainText(/create.*first|get started/i);
    });

    test('should disable continue session for new users', async ({ page }) => {
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [],
            recent_sessions: [],
            progress: null,
          }),
        });
      });

      await dashboardPage.goto();
      await expect(dashboardPage.continueSessionButton).toBeDisabled();
    });
  });

  test.describe('Returning User Experience', () => {
    test('should show user content for returning users', async ({ page }) => {
      // Mock user with data
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [
              { id: '1', name: 'Test Character', last_active: '2024-01-01' }
            ],
            recent_sessions: [
              { id: '1', character_name: 'Test Character', world_name: 'Test World', last_activity: '2024-01-01' }
            ],
            progress: { level: 5, experience: 1250 },
          }),
        });
      });

      await dashboardPage.goto();
      await dashboardPage.expectReturningUserExperience();
    });

    test('should enable continue session for users with sessions', async ({ page }) => {
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [{ id: '1', name: 'Test Character' }],
            recent_sessions: [{ id: '1', character_name: 'Test Character' }],
            progress: {},
          }),
        });
      });

      await dashboardPage.goto();
      await expect(dashboardPage.continueSessionButton).toBeEnabled();
    });
  });

  test.describe('Navigation', () => {
    test('should navigate to character management', async () => {
      await dashboardPage.createNewCharacter();
      await expect(dashboardPage.page).toHaveURL(/characters/);
    });

    test('should navigate to world exploration', async () => {
      await dashboardPage.exploreWorlds();
      await expect(dashboardPage.page).toHaveURL(/worlds/);
    });

    test('should navigate to settings', async () => {
      await dashboardPage.goToSettings();
      await expect(dashboardPage.page).toHaveURL(/settings/);
    });

    test('should continue last session', async ({ page }) => {
      // Mock user with active session
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [{ id: '1', name: 'Test Character' }],
            recent_sessions: [{ id: 'session1', character_name: 'Test Character' }],
            progress: {},
          }),
        });
      });

      await dashboardPage.goto();
      await dashboardPage.continueLastSession();
      await expect(dashboardPage.page).toHaveURL(/chat/);
    });
  });

  test.describe('Character Management', () => {
    test('should display character cards', async ({ page }) => {
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [
              { id: '1', name: 'Warrior', last_active: '2024-01-01' },
              { id: '2', name: 'Healer', last_active: '2024-01-02' },
            ],
            recent_sessions: [],
            progress: {},
          }),
        });
      });

      await dashboardPage.goto();
      await dashboardPage.expectCharacterCount(2);
    });

    test('should allow character selection', async ({ page }) => {
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [
              { id: '1', name: 'Test Character', last_active: '2024-01-01' }
            ],
            recent_sessions: [],
            progress: {},
          }),
        });
      });

      await dashboardPage.goto();
      await dashboardPage.selectCharacter('Test Character');
      // Should navigate to character details or start session
    });
  });

  test.describe('Session Management', () => {
    test('should display recent sessions', async ({ page }) => {
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [],
            recent_sessions: [
              { id: '1', character_name: 'Warrior', world_name: 'Forest', last_activity: '2024-01-01' },
              { id: '2', character_name: 'Healer', world_name: 'Village', last_activity: '2024-01-02' },
            ],
            progress: {},
          }),
        });
      });

      await dashboardPage.goto();
      await dashboardPage.expectSessionCount(2);
    });

    test('should allow session selection', async ({ page }) => {
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [],
            recent_sessions: [
              { id: '1', character_name: 'Test Character', world_name: 'Test World' }
            ],
            progress: {},
          }),
        });
      });

      await dashboardPage.goto();
      await dashboardPage.selectRecentSession('Test Character');
      // Should navigate to chat session
    });
  });

  test.describe('Data Refresh', () => {
    test('should refresh dashboard data', async () => {
      await dashboardPage.refreshDashboard();
      await dashboardPage.expectDashboardLoaded();
    });

    test('should show updated data after refresh', async ({ page }) => {
      let requestCount = 0;
      await page.route('**/players/*/dashboard', route => {
        requestCount++;
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [],
            recent_sessions: [],
            progress: {},
            last_updated: new Date().toISOString(),
          }),
        });
      });

      await dashboardPage.goto();
      await dashboardPage.refreshDashboard();

      expect(requestCount).toBeGreaterThan(1);
    });
  });

  test.describe('Accessibility', () => {
    test('should be accessible with keyboard navigation', async () => {
      await dashboardPage.navigateWithKeyboard();
    });

    test('should meet accessibility standards', async () => {
      await dashboardPage.checkAccessibility();
    });

    test('should have proper heading hierarchy', async () => {
      const headings = dashboardPage.page.locator('h1, h2, h3, h4, h5, h6');
      await expect(headings.first()).toHaveRole('heading');
    });

    test('should support screen readers', async () => {
      await expect(dashboardPage.createCharacterButton).toHaveRole('button');
      await expect(dashboardPage.exploreWorldsButton).toHaveRole('button');
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile devices', async () => {
      await dashboardPage.checkMobileLayout();
    });

    test('should stack sections vertically on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await dashboardPage.expectDashboardLoaded();

      // Check that sections are stacked
      const quickActions = await dashboardPage.quickActionsSection.boundingBox();
      const characters = await dashboardPage.charactersSection.boundingBox();

      if (quickActions && characters) {
        expect(characters.y).toBeGreaterThan(quickActions.y + quickActions.height);
      }
    });

    test('should adapt to tablet size', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await dashboardPage.expectDashboardLoaded();
      await dashboardPage.expectQuickActionsVisible();
    });
  });

  test.describe('Performance', () => {
    test('should load dashboard quickly', async () => {
      const loadTime = await dashboardPage.measureDashboardLoadTime();
      expect(loadTime).toBeLessThan(3000);
    });

    test('should handle large amounts of data', async ({ page }) => {
      // Mock large dataset
      const characters = Array.from({ length: 50 }, (_, i) => ({
        id: `char-${i}`,
        name: `Character ${i}`,
        last_active: '2024-01-01',
      }));

      const sessions = Array.from({ length: 100 }, (_, i) => ({
        id: `session-${i}`,
        character_name: `Character ${i % 10}`,
        world_name: `World ${i % 5}`,
        last_activity: '2024-01-01',
      }));

      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters,
            recent_sessions: sessions,
            progress: {},
          }),
        });
      });

      const startTime = Date.now();
      await dashboardPage.goto();
      await dashboardPage.expectDashboardLoaded();
      const loadTime = Date.now() - startTime;

      expect(loadTime).toBeLessThan(5000);
    });
  });

  test.describe('Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal server error' }),
        });
      });

      await dashboardPage.goto();
      const errorMessage = dashboardPage.page.locator('[data-testid="error"], .error');
      await expect(errorMessage).toBeVisible();
    });

    test('should show empty states appropriately', async ({ page }) => {
      await page.route('**/players/*/dashboard', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            characters: [],
            recent_sessions: [],
            progress: null,
          }),
        });
      });

      await dashboardPage.goto();
      await dashboardPage.expectCharactersSection(false);
      await dashboardPage.expectRecentSessions(false);
    });
  });
});
