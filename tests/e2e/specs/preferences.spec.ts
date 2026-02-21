// Logseq: [[TTA.dev/Tests/E2e/Specs/Preferences.spec]]
import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { PreferencesPage } from '../page-objects/PreferencesPage';
import { testUsers } from '../fixtures/test-data';
import { mockApiResponse, createTempFile, deleteTempFile } from '../utils/test-helpers';

test.describe('Preferences Management', () => {
  let loginPage: LoginPage;
  let preferencesPage: PreferencesPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    preferencesPage = new PreferencesPage(page);

    // Mock API responses for preferences
    await mockApiResponse(page, '**/players/*/preferences', {
      player_id: 'test-player-1',
      intensity_level: 'MEDIUM',
      preferred_approaches: ['CBT', 'MINDFULNESS'],
      conversation_style: 'SUPPORTIVE',
      therapeutic_goals: ['stress_management', 'anxiety_reduction'],
      character_name: 'Alex',
      preferred_setting: 'NATURE',
      comfort_topics: ['work', 'relationships'],
      trigger_topics: ['trauma', 'loss'],
      avoid_topics: ['violence'],
    });

    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
  });

  test.describe('Page Loading and Navigation', () => {
    test('should load preferences page correctly', async () => {
      await preferencesPage.goto();
      await preferencesPage.expectPageLoaded();
    });

    test('should show loading state while fetching preferences', async ({ page }) => {
      await page.route('**/players/*/preferences', route => {
        setTimeout(() => route.continue(), 2000);
      });

      await preferencesPage.goto();
      await preferencesPage.expectLoadingState();
    });

    test('should handle missing player profile', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/preferences', null, 404);

      await preferencesPage.goto();
      await expect(page.locator('text=Player Profile Required')).toBeVisible();
    });
  });

  test.describe('Intensity Level Configuration', () => {
    test.beforeEach(async () => {
      await preferencesPage.goto();
      await preferencesPage.clickTab('intensity');
    });

    test('should set intensity level using slider', async () => {
      await preferencesPage.setIntensityLevel(7);
      await preferencesPage.expectIntensityLevel(7);
    });

    test('should show intensity level labels', async () => {
      await expect(preferencesPage.intensityLabels).toBeVisible();
    });

    test('should update intensity value display', async () => {
      await preferencesPage.setIntensityLevel(5);
      await expect(preferencesPage.intensityValue).toContainText('5');
    });

    test('should validate intensity level bounds', async () => {
      await preferencesPage.setIntensityLevel(11); // Above max
      await preferencesPage.expectIntensityLevel(10); // Should clamp to max

      await preferencesPage.setIntensityLevel(-1); // Below min
      await preferencesPage.expectIntensityLevel(1); // Should clamp to min
    });
  });

  test.describe('Therapeutic Approach Configuration', () => {
    test.beforeEach(async () => {
      await preferencesPage.goto();
      await preferencesPage.clickTab('approach');
    });

    test('should select multiple therapeutic approaches', async () => {
      await preferencesPage.selectTherapeuticApproach('CBT');
      await preferencesPage.selectTherapeuticApproach('MINDFULNESS');
      await preferencesPage.selectTherapeuticApproach('DBT');

      await preferencesPage.expectApproachSelected('CBT');
      await preferencesPage.expectApproachSelected('MINDFULNESS');
      await preferencesPage.expectApproachSelected('DBT');
    });

    test('should unselect therapeutic approaches', async () => {
      await preferencesPage.selectTherapeuticApproach('CBT');
      await preferencesPage.expectApproachSelected('CBT');

      await preferencesPage.unselectTherapeuticApproach('CBT');
      await expect(preferencesPage.cbtCheckbox).not.toBeChecked();
    });

    test('should require at least one approach', async () => {
      // Unselect all approaches
      await preferencesPage.unselectTherapeuticApproach('CBT');
      await preferencesPage.unselectTherapeuticApproach('MINDFULNESS');

      await preferencesPage.savePreferences();
      await preferencesPage.expectValidationErrors();
    });
  });

  test.describe('Conversation Style Configuration', () => {
    test.beforeEach(async () => {
      await preferencesPage.goto();
      await preferencesPage.clickTab('conversation');
    });

    test('should select conversation style', async () => {
      await preferencesPage.selectConversationStyle('SUPPORTIVE');
      await preferencesPage.expectConversationStyle('SUPPORTIVE');

      await preferencesPage.selectConversationStyle('CHALLENGING');
      await preferencesPage.expectConversationStyle('CHALLENGING');

      await preferencesPage.selectConversationStyle('NEUTRAL');
      await preferencesPage.expectConversationStyle('NEUTRAL');
    });

    test('should allow only one conversation style', async () => {
      await preferencesPage.selectConversationStyle('SUPPORTIVE');
      await preferencesPage.selectConversationStyle('CHALLENGING');

      // Only challenging should be selected
      await preferencesPage.expectConversationStyle('CHALLENGING');
      await expect(preferencesPage.supportiveRadio).not.toBeChecked();
    });
  });

  test.describe('Therapeutic Goals Configuration', () => {
    test.beforeEach(async () => {
      await preferencesPage.goto();
      await preferencesPage.clickTab('goals');
    });

    test('should add therapeutic goals', async () => {
      await preferencesPage.addTherapeuticGoal('stress_management');
      await preferencesPage.expectGoalSelected('stress_management');

      await preferencesPage.addTherapeuticGoal('anxiety_reduction');
      await preferencesPage.expectGoalSelected('anxiety_reduction');
    });

    test('should remove therapeutic goals', async () => {
      await preferencesPage.addTherapeuticGoal('stress_management');
      await preferencesPage.expectGoalSelected('stress_management');

      await preferencesPage.removeTherapeuticGoal('stress_management');
      await expect(preferencesPage.selectedGoals.locator('text=stress_management')).not.toBeVisible();
    });

    test('should show goal suggestions', async () => {
      await preferencesPage.goalsInput.focus();
      await expect(preferencesPage.goalsSuggestions).toBeVisible();
    });
  });

  test.describe('Character Customization', () => {
    test.beforeEach(async () => {
      await preferencesPage.goto();
      await preferencesPage.clickTab('character');
    });

    test('should set character name', async () => {
      await preferencesPage.setCharacterName('TestCharacter');
      await preferencesPage.expectCharacterName('TestCharacter');
    });

    test('should set preferred setting', async () => {
      await preferencesPage.setPreferredSetting('URBAN');
      await expect(preferencesPage.preferredSettingSelect).toHaveValue('URBAN');
    });

    test('should validate character name length', async () => {
      await preferencesPage.setCharacterName('A'); // Too short
      await preferencesPage.savePreferences();
      await preferencesPage.expectValidationErrors();

      await preferencesPage.setCharacterName('A'.repeat(51)); // Too long
      await preferencesPage.savePreferences();
      await preferencesPage.expectValidationErrors();
    });
  });

  test.describe('Topic Preferences', () => {
    test.beforeEach(async () => {
      await preferencesPage.goto();
      await preferencesPage.clickTab('topics');
    });

    test('should set comfort topics', async () => {
      await preferencesPage.setComfortTopics(['work', 'relationships', 'hobbies']);
      await expect(preferencesPage.comfortTopicsInput).toHaveValue('work, relationships, hobbies');
    });

    test('should set trigger topics', async () => {
      await preferencesPage.setTriggerTopics(['trauma', 'loss']);
      await expect(preferencesPage.triggerTopicsInput).toHaveValue('trauma, loss');
    });

    test('should set avoid topics', async () => {
      await preferencesPage.setAvoidTopics(['violence', 'abuse']);
      await expect(preferencesPage.avoidTopicsInput).toHaveValue('violence, abuse');
    });

    test('should prevent overlap between comfort and avoid topics', async () => {
      await preferencesPage.setComfortTopics(['work']);
      await preferencesPage.setAvoidTopics(['work']);

      await preferencesPage.savePreferences();
      await preferencesPage.expectValidationErrors();
    });
  });

  test.describe('Save and Validation', () => {
    test.beforeEach(async () => {
      await preferencesPage.goto();
    });

    test('should save preferences successfully', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/preferences', { success: true }, 200, 'PUT');

      await preferencesPage.setIntensityLevel(6);
      await preferencesPage.savePreferences();

      await expect(page.locator('text=Preferences saved')).toBeVisible();
    });

    test('should show unsaved changes warning', async () => {
      await preferencesPage.setIntensityLevel(8);
      await preferencesPage.expectUnsavedChangesWarning();
    });

    test('should handle save errors', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/preferences', { error: 'Save failed' }, 500, 'PUT');

      await preferencesPage.setIntensityLevel(6);
      await preferencesPage.savePreferences();

      await preferencesPage.expectErrorMessage('Save failed');
    });

    test('should measure save performance', async ({ page }) => {
      await mockApiResponse(page, '**/players/*/preferences', { success: true }, 200, 'PUT');

      const saveTime = await preferencesPage.measureSavePerformance();
      expect(saveTime).toBeLessThan(3000); // 3 seconds
    });
  });

  test.describe('Import/Export Functionality', () => {
    test.beforeEach(async () => {
      await preferencesPage.goto();
    });

    test('should export preferences', async ({ page }) => {
      const downloadPromise = page.waitForEvent('download');
      await preferencesPage.clickExport();
      const download = await downloadPromise;

      expect(download.suggestedFilename()).toContain('preferences');
      expect(download.suggestedFilename()).toContain('.json');
    });

    test('should import preferences from file', async ({ page }) => {
      const testPreferences = {
        intensity_level: 'HIGH',
        preferred_approaches: ['DBT'],
        conversation_style: 'CHALLENGING',
      };

      const tempFile = await createTempFile(JSON.stringify(testPreferences), 'preferences.json');

      try {
        await mockApiResponse(page, '**/players/*/preferences/import', { success: true }, 200, 'POST');

        await preferencesPage.importPreferences(tempFile);

        await expect(page.locator('text=Preferences imported')).toBeVisible();
      } finally {
        await deleteTempFile(tempFile);
      }
    });

    test('should handle invalid import file', async () => {
      const tempFile = await createTempFile('invalid json', 'invalid.json');

      try {
        await preferencesPage.clickImport();
        await preferencesPage.fileInput.setInputFiles(tempFile);
        await preferencesPage.importConfirmButton.click();

        await expect(preferencesPage.page.locator('text=Failed to import')).toBeVisible();
      } finally {
        await deleteTempFile(tempFile);
      }
    });
  });

  test.describe('Reset Functionality', () => {
    test.beforeEach(async () => {
      await preferencesPage.goto();
    });

    test('should reset preferences to defaults', async ({ page }) => {
      // Make some changes
      await preferencesPage.setIntensityLevel(8);
      await preferencesPage.clickTab('approach');
      await preferencesPage.selectTherapeuticApproach('DBT');

      // Reset preferences
      await mockApiResponse(page, '**/players/*/preferences/reset', { success: true }, 200, 'POST');

      await preferencesPage.clickReset();
      await preferencesPage.confirmReset();

      await expect(page.locator('text=Preferences reset')).toBeVisible();
    });

    test('should cancel reset operation', async () => {
      await preferencesPage.clickReset();
      await preferencesPage.cancelModal();

      await expect(preferencesPage.resetModal).not.toBeVisible();
    });
  });

  test.describe('Accessibility', () => {
    test.beforeEach(async () => {
      await preferencesPage.goto();
    });

    test('should support keyboard navigation', async () => {
      await preferencesPage.testKeyboardNavigation();
    });

    test('should have proper screen reader support', async () => {
      await preferencesPage.testScreenReaderSupport();
    });

    test('should have proper focus management', async () => {
      await preferencesPage.clickTab('intensity');
      await expect(preferencesPage.intensitySlider).toBeFocused();
    });
  });

  test.describe('Responsive Design', () => {
    test('should adapt to mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await preferencesPage.goto();
      await preferencesPage.expectPageLoaded();

      // Test tab navigation on mobile
      await preferencesPage.clickTab('intensity');
      await preferencesPage.setIntensityLevel(7);
      await preferencesPage.expectIntensityLevel(7);
    });

    test('should adapt to tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await preferencesPage.goto();
      await preferencesPage.expectPageLoaded();

      // Test form functionality on tablet
      await preferencesPage.clickTab('approach');
      await preferencesPage.selectTherapeuticApproach('CBT');
      await preferencesPage.expectApproachSelected('CBT');
    });
  });

  test.describe('Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      await page.route('**/players/*/preferences', route => {
        route.fulfill({ status: 500, body: 'Server Error' });
      });

      await preferencesPage.goto();
      await preferencesPage.expectErrorMessage('Server Error');
    });

    test('should handle network timeouts', async ({ page }) => {
      await page.route('**/players/*/preferences', route => {
        // Never resolve to simulate timeout
      });

      await preferencesPage.goto();
      await preferencesPage.expectLoadingState();
    });

    test('should validate required fields', async () => {
      await preferencesPage.goto();

      // Clear required fields
      await preferencesPage.clickTab('character');
      await preferencesPage.setCharacterName('');

      await preferencesPage.savePreferences();
      await preferencesPage.expectValidationErrors();
    });
  });
});
