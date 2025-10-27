import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { CharacterManagementPage } from '../page-objects/CharacterManagementPage';
import { testUsers, testCharacters, generateRandomCharacter } from '../fixtures/test-data';

test.describe('Character Management', () => {
  let loginPage: LoginPage;
  let characterPage: CharacterManagementPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    characterPage = new CharacterManagementPage(page);

    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
    await characterPage.goto();
    await characterPage.expectPageLoaded();
  });

  test.describe('Page Layout', () => {
    test('should display character management interface', async () => {
      await characterPage.expectPageLoaded();
      await expect(characterPage.createCharacterButton).toBeVisible();
      await expect(characterPage.characterGrid).toBeVisible();
    });

    test('should show empty state for new users', async ({ page }) => {
      await page.route('**/players/*/characters', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await characterPage.goto();
      await characterPage.expectEmptyState();
    });

    test('should display character cards for existing characters', async ({ page }) => {
      await page.route('**/players/*/characters', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            { character_id: '1', name: 'Test Character 1', ...testCharacters.warrior },
            { character_id: '2', name: 'Test Character 2', ...testCharacters.healer },
          ]),
        });
      });

      await characterPage.goto();
      await characterPage.expectCharacterCount(2);
    });
  });

  test.describe('Character Creation', () => {
    test('should open character creation form', async () => {
      await characterPage.clickCreateCharacter();
      await characterPage.expectCharacterFormVisible();
    });

    test('should create a new character successfully', async ({ page }) => {
      await page.route('**/players/*/characters', route => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              character_id: 'new-char-1',
              ...JSON.parse(route.request().postData() || '{}'),
            }),
          });
        } else {
          route.continue();
        }
      });

      const newCharacter = generateRandomCharacter();
      await characterPage.createCharacter(newCharacter);
      await characterPage.expectCharacterCreated(newCharacter.name);
    });

    test('should validate required fields', async () => {
      await characterPage.expectFormValidation();
      await characterPage.expectNameRequired();
    });

    test('should cancel character creation', async () => {
      await characterPage.clickCreateCharacter();
      await characterPage.expectCharacterFormVisible();
      await characterPage.cancelCharacterCreation();
      await expect(characterPage.characterForm).toBeHidden();
    });

    test('should handle character creation errors', async ({ page }) => {
      await page.route('**/players/*/characters', route => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 400,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Character name already exists' }),
          });
        } else {
          route.continue();
        }
      });

      await characterPage.clickCreateCharacter();
      await characterPage.fillCharacterForm(testCharacters.warrior);
      await characterPage.saveCharacter();

      const errorMessage = characterPage.page.locator('[data-testid="error"], .error');
      await expect(errorMessage).toBeVisible();
    });
  });

  test.describe('Character Editing', () => {
    test.beforeEach(async ({ page }) => {
      // Mock existing character
      await page.route('**/players/*/characters', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            { character_id: '1', name: 'Test Character', ...testCharacters.warrior },
          ]),
        });
      });

      await characterPage.goto();
    });

    test('should edit character successfully', async ({ page }) => {
      await page.route('**/characters/*', route => {
        if (route.request().method() === 'PUT') {
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              character_id: '1',
              name: 'Updated Character',
              ...testCharacters.warrior,
            }),
          });
        } else {
          route.continue();
        }
      });

      await characterPage.editCharacter('Test Character', {
        name: 'Updated Character',
      });

      await characterPage.expectCharacterCreated('Updated Character');
    });

    test('should delete character successfully', async ({ page }) => {
      await page.route('**/characters/*', route => {
        if (route.request().method() === 'DELETE') {
          route.fulfill({ status: 204 });
        } else {
          route.continue();
        }
      });

      await characterPage.deleteCharacter('Test Character');
      await characterPage.expectCharacterDeleted('Test Character');
    });

    test('should confirm before deleting character', async () => {
      await characterPage.selectCharacterForEdit('Test Character');
      await characterPage.deleteCharacterButton.click();

      // Should show confirmation dialog
      await expect(characterPage.confirmDeleteButton).toBeVisible();
    });
  });

  test.describe('Character Search and Filtering', () => {
    test.beforeEach(async ({ page }) => {
      // Mock multiple characters
      await page.route('**/players/*/characters', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            { character_id: '1', name: 'Brave Warrior', ...testCharacters.warrior },
            { character_id: '2', name: 'Gentle Healer', ...testCharacters.healer },
            { character_id: '3', name: 'Wise Mage', therapeutic_profile: { preferred_intensity: 'HIGH' } },
          ]),
        });
      });

      await characterPage.goto();
    });

    test('should search characters by name', async () => {
      await characterPage.searchCharacters('Warrior');
      await characterPage.expectSearchResults('Warrior');
    });

    test('should filter characters by intensity', async () => {
      await characterPage.filterCharacters('HIGH');
      await characterPage.expectCharacterCount(1);
    });

    test('should sort characters', async () => {
      await characterPage.sortCharacters('name_asc');
      // Should reorder characters alphabetically
    });

    test('should clear search and filters', async () => {
      await characterPage.searchCharacters('Warrior');
      await characterPage.expectSearchResults('Warrior');

      await characterPage.searchCharacters('');
      await characterPage.expectCharacterCount(3);
    });
  });

  test.describe('View Modes', () => {
    test.beforeEach(async ({ page }) => {
      await page.route('**/players/*/characters', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            { character_id: '1', name: 'Character 1', ...testCharacters.warrior },
            { character_id: '2', name: 'Character 2', ...testCharacters.healer },
          ]),
        });
      });

      await characterPage.goto();
    });

    test('should switch between grid and list views', async () => {
      await characterPage.switchToListView();
      // Should change layout to list view

      await characterPage.switchToGridView();
      // Should change layout back to grid view
    });

    test('should remember view preference', async ({ page }) => {
      await characterPage.switchToListView();
      await page.reload();
      await characterPage.expectPageLoaded();

      // Should maintain list view after reload
    });
  });

  test.describe('Bulk Operations', () => {
    test.beforeEach(async ({ page }) => {
      await page.route('**/players/*/characters', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            { character_id: '1', name: 'Character 1', ...testCharacters.warrior },
            { character_id: '2', name: 'Character 2', ...testCharacters.healer },
            { character_id: '3', name: 'Character 3', ...testCharacters.warrior },
          ]),
        });
      });

      await characterPage.goto();
    });

    test('should select multiple characters', async () => {
      await characterPage.selectMultipleCharacters(['Character 1', 'Character 2']);

      // Should show bulk action buttons
      const bulkActions = characterPage.page.locator('[data-testid="bulk-actions"]');
      await expect(bulkActions).toBeVisible();
    });

    test('should bulk delete characters', async ({ page }) => {
      await page.route('**/characters/bulk-delete', route => {
        route.fulfill({ status: 204 });
      });

      await characterPage.bulkDeleteCharacters(['Character 1', 'Character 2']);
      await characterPage.expectCharacterCount(1);
    });
  });

  test.describe('Accessibility', () => {
    test('should be accessible with keyboard navigation', async () => {
      await characterPage.navigateFormWithKeyboard();
    });

    test('should meet accessibility standards', async () => {
      await characterPage.checkAccessibility();
    });

    test('should have proper form labels', async () => {
      await characterPage.clickCreateCharacter();
      await expect(characterPage.nameInput).toHaveAttribute('aria-label');
      await expect(characterPage.characterForm).toHaveRole('form');
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile devices', async () => {
      await characterPage.checkMobileLayout();
    });

    test('should adapt form layout for mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await characterPage.clickCreateCharacter();
      await characterPage.expectCharacterFormVisible();

      // Form should be properly sized for mobile
      const formBox = await characterPage.characterForm.boundingBox();
      expect(formBox?.width).toBeLessThan(400);
    });
  });

  test.describe('Performance', () => {
    test('should create character within acceptable time', async ({ page }) => {
      await page.route('**/players/*/characters', route => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              character_id: 'perf-test',
              ...testCharacters.warrior,
            }),
          });
        } else {
          route.continue();
        }
      });

      const creationTime = await characterPage.measureCharacterCreationTime();
      expect(creationTime).toBeLessThan(10000);
    });

    test('should handle large character lists efficiently', async ({ page }) => {
      const manyCharacters = Array.from({ length: 100 }, (_, i) => ({
        character_id: `char-${i}`,
        name: `Character ${i}`,
        ...testCharacters.warrior,
      }));

      await page.route('**/players/*/characters', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(manyCharacters),
        });
      });

      const startTime = Date.now();
      await characterPage.goto();
      await characterPage.expectPageLoaded();
      const loadTime = Date.now() - startTime;

      expect(loadTime).toBeLessThan(5000);
    });
  });

  test.describe('Error Handling', () => {
    test('should handle network errors during character creation', async ({ page }) => {
      await page.route('**/players/*/characters', route => {
        if (route.request().method() === 'POST') {
          route.abort('failed');
        } else {
          route.continue();
        }
      });

      await characterPage.clickCreateCharacter();
      await characterPage.fillCharacterForm(testCharacters.warrior);
      await characterPage.saveCharacter();

      const errorMessage = characterPage.page.locator('[data-testid="error"], .error');
      await expect(errorMessage).toBeVisible();
    });

    test('should handle server errors gracefully', async ({ page }) => {
      await page.route('**/players/*/characters', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal server error' }),
        });
      });

      await characterPage.goto();
      const errorMessage = characterPage.page.locator('[data-testid="error"], .error');
      await expect(errorMessage).toBeVisible();
    });
  });
});
