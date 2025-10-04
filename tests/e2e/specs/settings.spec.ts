import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { SettingsPage } from '../page-objects/SettingsPage';
import { testUsers, testSettings } from '../fixtures/test-data';

test.describe('Settings Management', () => {
  let loginPage: LoginPage;
  let settingsPage: SettingsPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    settingsPage = new SettingsPage(page);
    
    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
    await settingsPage.goto();
    await settingsPage.expectPageLoaded();
  });

  test.describe('Settings Page Layout', () => {
    test('should display settings interface correctly', async () => {
      await settingsPage.expectPageLoaded();
      await expect(settingsPage.tabNavigation).toBeVisible();
      await expect(settingsPage.therapeuticTab).toBeVisible();
      await expect(settingsPage.modelsTab).toBeVisible();
      await expect(settingsPage.privacyTab).toBeVisible();
    });

    test('should show all settings tabs', async () => {
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

    test('should activate therapeutic tab by default', async () => {
      await settingsPage.expectTabActive('therapeutic');
    });
  });

  test.describe('Tab Navigation', () => {
    test('should navigate between tabs', async () => {
      await settingsPage.goToPrivacyTab();
      await settingsPage.expectTabActive('privacy');
      
      await settingsPage.goToNotificationsTab();
      await settingsPage.expectTabActive('notifications');
      
      await settingsPage.goToAccessibilityTab();
      await settingsPage.expectTabActive('accessibility');
    });

    test('should navigate tabs with keyboard', async () => {
      await settingsPage.navigateTabsWithKeyboard();
    });

    test('should warn about unsaved changes when switching tabs', async () => {
      await settingsPage.goToTherapeuticTab();
      await settingsPage.intensitySelect.selectOption('HIGH');
      
      await settingsPage.goToPrivacyTab();
      await settingsPage.expectUnsavedChanges();
    });
  });

  test.describe('Therapeutic Settings', () => {
    test('should update therapeutic preferences', async ({ page }) => {
      await page.route('**/players/*/settings/therapeutic', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true }),
        });
      });
      
      await settingsPage.updateTherapeuticSettings({
        intensity: 'HIGH',
        approaches: ['CBT', 'Mindfulness'],
        triggerWarnings: ['Violence', 'Abandonment'],
        comfortTopics: ['Nature', 'Animals'],
        avoidTopics: ['Death', 'Abuse'],
      });
      
      await settingsPage.saveSettings();
      await settingsPage.expectSettingsSaved();
    });

    test('should validate therapeutic settings', async () => {
      await settingsPage.goToTherapeuticTab();
      await settingsPage.intensitySelect.selectOption('');
      await settingsPage.saveSettings();
      
      await settingsPage.expectErrorMessage();
    });

    test('should update crisis contact information', async ({ page }) => {
      await page.route('**/players/*/settings/therapeutic', route => {
        route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
      });
      
      await settingsPage.updateTherapeuticSettings({
        crisisContact: 'Emergency: 911\nTherapist: Dr. Smith (555) 123-4567',
      });
      
      await settingsPage.saveSettings();
      await settingsPage.expectSettingsSaved();
    });
  });

  test.describe('Privacy Settings', () => {
    test('should update privacy preferences', async ({ page }) => {
      await page.route('**/players/*/settings/privacy', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true }),
        });
      });
      
      await settingsPage.updatePrivacySettings({
        dataSharing: false,
        researchParticipation: true,
        contactPreferences: ['email'],
        dataRetention: 365,
      });
      
      await settingsPage.saveSettings();
      await settingsPage.expectSettingsSaved();
    });

    test('should export user data', async ({ page }) => {
      await page.route('**/players/*/data/export', route => {
        route.fulfill({
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            'Content-Disposition': 'attachment; filename="user-data.json"',
          },
          body: JSON.stringify({ user_data: 'exported' }),
        });
      });
      
      const download = await settingsPage.exportData();
      expect(download.suggestedFilename()).toContain('user-data');
    });

    test('should delete all user data', async ({ page }) => {
      await page.route('**/players/*/data', route => {
        if (route.request().method() === 'DELETE') {
          route.fulfill({ status: 204 });
        } else {
          route.continue();
        }
      });
      
      await settingsPage.deleteAllData();
      
      // Should show confirmation
      const confirmationMessage = settingsPage.page.locator('[data-testid="delete-confirmation"]');
      await expect(confirmationMessage).toBeVisible();
    });
  });

  test.describe('Notification Settings', () => {
    test('should update notification preferences', async ({ page }) => {
      await page.route('**/players/*/settings/notifications', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true }),
        });
      });
      
      await settingsPage.updateNotificationSettings({
        sessionReminders: true,
        progressUpdates: true,
        milestones: true,
        crisisAlerts: true,
        email: true,
        push: false,
      });
      
      await settingsPage.saveSettings();
      await settingsPage.expectSettingsSaved();
    });

    test('should require crisis alerts to be enabled', async () => {
      await settingsPage.goToNotificationsTab();
      await settingsPage.crisisAlertsToggle.uncheck();
      
      // Should show warning about disabling crisis alerts
      const warningMessage = settingsPage.page.locator('[data-testid="crisis-warning"]');
      await expect(warningMessage).toBeVisible();
    });
  });

  test.describe('Accessibility Settings', () => {
    test('should update accessibility preferences', async ({ page }) => {
      await page.route('**/players/*/settings/accessibility', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true }),
        });
      });
      
      await settingsPage.updateAccessibilitySettings({
        highContrast: true,
        largeText: true,
        screenReader: true,
        reducedMotion: false,
        keyboardNavigation: true,
      });
      
      await settingsPage.saveSettings();
      await settingsPage.expectSettingsSaved();
    });

    test('should apply accessibility changes immediately', async () => {
      await settingsPage.goToAccessibilityTab();
      await settingsPage.highContrastToggle.check();
      
      // Should apply high contrast mode immediately
      await expect(settingsPage.page.locator('body')).toHaveClass(/high-contrast/);
    });

    test('should apply large text setting', async () => {
      await settingsPage.goToAccessibilityTab();
      await settingsPage.largeTextToggle.check();
      
      // Should apply large text immediately
      await expect(settingsPage.page.locator('body')).toHaveClass(/large-text/);
    });
  });

  test.describe('AI Models Settings', () => {
    test('should display model management interface', async () => {
      await settingsPage.goToModelsTab();
      await expect(settingsPage.modelSelector).toBeVisible();
      await expect(settingsPage.freeModelsFilter).toBeVisible();
    });

    test('should filter free models only', async ({ page }) => {
      await page.route('**/api/v1/models/free', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            { model_id: 'free-model-1', name: 'Free Model 1', is_free: true },
            { model_id: 'free-model-2', name: 'Free Model 2', is_free: true },
          ]),
        });
      });
      
      await settingsPage.goToModelsTab();
      await settingsPage.freeModelsFilter.check();
      
      // Should show only free models
      const modelCards = settingsPage.page.locator('[data-testid="model-card"]');
      await expect(modelCards).toHaveCount(2);
    });

    test('should adjust cost threshold', async () => {
      await settingsPage.goToModelsTab();
      await settingsPage.costThresholdSlider.fill('0.005');
      
      // Should update model recommendations based on cost
      const affordableModels = settingsPage.page.locator('[data-testid="affordable-models"]');
      await expect(affordableModels).toBeVisible();
    });
  });

  test.describe('Settings Persistence', () => {
    test('should save settings changes', async ({ page }) => {
      await page.route('**/players/*/settings/**', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true }),
        });
      });
      
      await settingsPage.goToTherapeuticTab();
      await settingsPage.intensitySelect.selectOption('HIGH');
      await settingsPage.saveSettings();
      
      await settingsPage.expectSettingsSaved();
    });

    test('should persist settings across sessions', async ({ page }) => {
      // Update settings
      await page.route('**/players/*/settings/**', route => {
        route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
      });
      
      await settingsPage.goToAccessibilityTab();
      await settingsPage.largeTextToggle.check();
      await settingsPage.saveSettings();
      
      // Reload page
      await page.reload();
      await settingsPage.expectPageLoaded();
      await settingsPage.goToAccessibilityTab();
      
      // Settings should be persisted
      await expect(settingsPage.largeTextToggle).toBeChecked();
    });

    test('should warn about unsaved changes', async () => {
      await settingsPage.goToTherapeuticTab();
      await settingsPage.intensitySelect.selectOption('HIGH');
      
      await settingsPage.expectUnsavedChanges();
    });

    test('should discard unsaved changes', async ({ page }) => {
      await settingsPage.goToTherapeuticTab();
      await settingsPage.intensitySelect.selectOption('HIGH');
      await settingsPage.expectUnsavedChanges();
      
      // Navigate away and discard changes
      await page.reload();
      await settingsPage.expectPageLoaded();
      
      // Changes should be discarded
      await expect(settingsPage.intensitySelect).not.toHaveValue('HIGH');
    });
  });

  test.describe('Accessibility', () => {
    test('should be accessible with keyboard navigation', async () => {
      await settingsPage.navigateTabsWithKeyboard();
    });

    test('should meet accessibility standards', async () => {
      await settingsPage.checkAccessibility();
    });

    test('should have proper ARIA labels', async () => {
      await settingsPage.goToTherapeuticTab();
      await expect(settingsPage.intensitySelect).toHaveAttribute('aria-label');
      
      await settingsPage.goToNotificationsTab();
      await expect(settingsPage.sessionRemindersToggle).toHaveRole('switch');
    });

    test('should support screen readers', async () => {
      await expect(settingsPage.tabNavigation).toHaveRole('tablist');
      await expect(settingsPage.therapeuticTab).toHaveRole('tab');
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile devices', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await settingsPage.expectPageLoaded();
      
      // Tabs should be scrollable on mobile
      const tabsBox = await settingsPage.tabNavigation.boundingBox();
      expect(tabsBox?.width).toBeLessThan(400);
    });

    test('should stack form elements on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await settingsPage.goToTherapeuticTab();
      
      // Form elements should stack vertically
      const formElements = settingsPage.page.locator('input, select, textarea');
      const firstElement = await formElements.first().boundingBox();
      const secondElement = await formElements.nth(1).boundingBox();
      
      if (firstElement && secondElement) {
        expect(secondElement.y).toBeGreaterThan(firstElement.y + firstElement.height);
      }
    });
  });

  test.describe('Error Handling', () => {
    test('should handle save errors gracefully', async ({ page }) => {
      await page.route('**/players/*/settings/**', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Failed to save settings' }),
        });
      });
      
      await settingsPage.goToTherapeuticTab();
      await settingsPage.intensitySelect.selectOption('HIGH');
      await settingsPage.saveSettings();
      
      await settingsPage.expectErrorMessage('Failed to save settings');
    });

    test('should handle network errors', async ({ page }) => {
      await page.route('**/players/*/settings/**', route => {
        route.abort('failed');
      });
      
      await settingsPage.goToTherapeuticTab();
      await settingsPage.intensitySelect.selectOption('HIGH');
      await settingsPage.saveSettings();
      
      await settingsPage.expectErrorMessage();
    });

    test('should retry failed saves', async ({ page }) => {
      let attemptCount = 0;
      await page.route('**/players/*/settings/**', route => {
        attemptCount++;
        if (attemptCount === 1) {
          route.fulfill({ status: 500 });
        } else {
          route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
        }
      });
      
      await settingsPage.goToTherapeuticTab();
      await settingsPage.intensitySelect.selectOption('HIGH');
      await settingsPage.saveSettings();
      
      // Should eventually succeed
      await settingsPage.expectSettingsSaved();
    });
  });
});
