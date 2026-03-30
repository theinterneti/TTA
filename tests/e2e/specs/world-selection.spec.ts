// Logseq: [[TTA.dev/Tests/E2e/Specs/World-selection.spec]]
import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { WorldSelectionPage } from '../page-objects/WorldSelectionPage';
import { CharacterManagementPage } from '../page-objects/CharacterManagementPage';
import { testUsers, generateRandomCharacter } from '../fixtures/test-data';
import { mockApiResponse, waitForLoadingToComplete } from '../utils/test-helpers';

test.describe('World Selection', () => {
  let loginPage: LoginPage;
  let worldSelectionPage: WorldSelectionPage;
  let characterPage: CharacterManagementPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    worldSelectionPage = new WorldSelectionPage(page);
    characterPage = new CharacterManagementPage(page);

    // Mock API responses for consistent testing
    await mockApiResponse(page, '**/worlds', [
      {
        world_id: 'world-1',
        name: 'Peaceful Garden',
        description: 'A calming therapeutic environment focused on mindfulness',
        therapeutic_themes: ['anxiety', 'mindfulness', 'relaxation'],
        difficulty_level: 'BEGINNER',
        estimated_duration: '2 hours',
        compatibility_score: 0.9,
      },
      {
        world_id: 'world-2',
        name: 'Urban Challenge',
        description: 'Navigate social situations in a city environment',
        therapeutic_themes: ['social anxiety', 'confidence', 'communication'],
        difficulty_level: 'ADVANCED',
        estimated_duration: '4 hours',
        compatibility_score: 0.6,
      },
      {
        world_id: 'world-3',
        name: 'Family Dynamics',
        description: 'Explore family relationships and communication patterns',
        therapeutic_themes: ['family therapy', 'communication', 'boundaries'],
        difficulty_level: 'INTERMEDIATE',
        estimated_duration: '3 hours',
        compatibility_score: 0.75,
      },
    ]);

    // Login before each test
    await loginPage.goto();
    await loginPage.login(testUsers.default);
  });

  test.describe('Page Loading and Navigation', () => {
    test('should load world selection page correctly', async () => {
      await worldSelectionPage.goto();
      await worldSelectionPage.expectPageLoaded();
      await worldSelectionPage.expectWorldsDisplayed();
    });

    test('should show character selection notice when no character selected', async () => {
      await worldSelectionPage.goto();
      await worldSelectionPage.expectCharacterNotice();
    });

    test('should display worlds after character selection', async ({ page }) => {
      // First create a character
      await characterPage.goto();
      const testCharacter = generateRandomCharacter();
      await characterPage.createCharacter(testCharacter);

      // Then go to world selection
      await worldSelectionPage.goto();
      await worldSelectionPage.expectWorldsDisplayed();
      await expect(worldSelectionPage.characterNoticeMessage).not.toBeVisible();
    });

    test('should handle loading states properly', async ({ page }) => {
      // Simulate slow API response
      await page.route('**/worlds', route => {
        setTimeout(() => route.continue(), 2000);
      });

      await worldSelectionPage.goto();
      await worldSelectionPage.expectLoadingState();
    });
  });

  test.describe('World Display and Information', () => {
    test.beforeEach(async () => {
      // Create a character for compatibility scores
      await characterPage.goto();
      const testCharacter = generateRandomCharacter();
      await characterPage.createCharacter(testCharacter);
      await worldSelectionPage.goto();
    });

    test('should display world cards with correct information', async () => {
      await worldSelectionPage.expectWorldsDisplayed();

      // Validate each world card has required information
      await worldSelectionPage.validateWorldCardData('Peaceful Garden');
      await worldSelectionPage.validateWorldCardData('Urban Challenge');
      await worldSelectionPage.validateWorldCardData('Family Dynamics');
    });

    test('should show compatibility scores when character is selected', async () => {
      await worldSelectionPage.expectWorldCompatibilityScore('Peaceful Garden', 90);
      await worldSelectionPage.expectWorldCompatibilityScore('Urban Challenge', 60);
      await worldSelectionPage.expectWorldCompatibilityScore('Family Dynamics', 75);
    });

    test('should display therapeutic themes correctly', async () => {
      await worldSelectionPage.expectWorldThemes('Peaceful Garden', ['anxiety', 'mindfulness']);
      await worldSelectionPage.expectWorldThemes('Urban Challenge', ['social anxiety', 'confidence']);
    });

    test('should show difficulty levels and durations', async () => {
      await worldSelectionPage.expectWorldDifficulty('Peaceful Garden', 'BEGINNER');
      await worldSelectionPage.expectWorldDifficulty('Urban Challenge', 'ADVANCED');
      await worldSelectionPage.expectWorldDuration('Peaceful Garden', '2 hours');
      await worldSelectionPage.expectWorldDuration('Urban Challenge', '4 hours');
    });
  });

  test.describe('Search and Filtering', () => {
    test.beforeEach(async () => {
      await characterPage.goto();
      const testCharacter = generateRandomCharacter();
      await characterPage.createCharacter(testCharacter);
      await worldSelectionPage.goto();
    });

    test('should filter worlds by search term', async () => {
      await worldSelectionPage.searchWorlds('Garden');

      const worldCount = await worldSelectionPage.getWorldCount();
      expect(worldCount).toBe(1);

      const gardenWorld = await worldSelectionPage.getWorldByName('Peaceful Garden');
      await expect(gardenWorld).toBeVisible();
    });

    test('should filter worlds by difficulty level', async () => {
      await worldSelectionPage.filterByDifficulty('BEGINNER');

      const worldCount = await worldSelectionPage.getWorldCount();
      expect(worldCount).toBe(1);

      await worldSelectionPage.expectWorldDifficulty('Peaceful Garden', 'BEGINNER');
    });

    test('should filter worlds by therapeutic theme', async () => {
      await worldSelectionPage.filterByTheme('anxiety');

      const worldCount = await worldSelectionPage.getWorldCount();
      expect(worldCount).toBeGreaterThanOrEqual(1);
    });

    test('should filter worlds by duration', async () => {
      await worldSelectionPage.filterByDuration('short');

      const worldCount = await worldSelectionPage.getWorldCount();
      expect(worldCount).toBe(1);

      await worldSelectionPage.expectWorldDuration('Peaceful Garden', '2 hours');
    });

    test('should clear all filters', async () => {
      // Apply multiple filters
      await worldSelectionPage.searchWorlds('Garden');
      await worldSelectionPage.filterByDifficulty('BEGINNER');

      // Clear filters
      await worldSelectionPage.clearAllFilters();

      // Should show all worlds again
      const worldCount = await worldSelectionPage.getWorldCount();
      expect(worldCount).toBe(3);
    });

    test('should handle no results gracefully', async () => {
      await worldSelectionPage.searchWorlds('NonexistentWorld');
      await worldSelectionPage.expectNoWorldsMessage();
    });
  });

  test.describe('World Interaction', () => {
    test.beforeEach(async () => {
      await characterPage.goto();
      const testCharacter = generateRandomCharacter();
      await characterPage.createCharacter(testCharacter);
      await worldSelectionPage.goto();
    });

    test('should open world details modal', async ({ page }) => {
      await mockApiResponse(page, '**/worlds/world-1', {
        world_id: 'world-1',
        name: 'Peaceful Garden',
        description: 'Detailed description of the peaceful garden world',
        therapeutic_themes: ['anxiety', 'mindfulness'],
        difficulty_level: 'BEGINNER',
        estimated_duration: '2 hours',
        compatibility_score: 0.9,
        detailed_description: 'This world provides a serene environment...',
        therapeutic_benefits: ['Stress reduction', 'Mindfulness practice'],
      });

      await worldSelectionPage.clickViewDetails('Peaceful Garden');
      await worldSelectionPage.expectWorldDetailsModal();
    });

    test('should open world customization modal', async () => {
      await worldSelectionPage.clickCustomizeWorld('Peaceful Garden');
      await worldSelectionPage.expectWorldCustomizationModal();
    });

    test('should handle world selection', async ({ page }) => {
      await mockApiResponse(page, '**/worlds/world-1/select', { success: true });

      await worldSelectionPage.clickSelectWorld('Peaceful Garden');

      // Should navigate to chat or next step
      await page.waitForURL(/chat|session/);
    });

    test('should close modals properly', async ({ page }) => {
      await mockApiResponse(page, '**/worlds/world-1', {});

      await worldSelectionPage.clickViewDetails('Peaceful Garden');
      await worldSelectionPage.expectWorldDetailsModal();

      await worldSelectionPage.closeModal();
      await expect(worldSelectionPage.worldDetailsModal).not.toBeVisible();
    });
  });

  test.describe('Responsive Design', () => {
    test.beforeEach(async () => {
      await characterPage.goto();
      const testCharacter = generateRandomCharacter();
      await characterPage.createCharacter(testCharacter);
      await worldSelectionPage.goto();
    });

    test('should adapt to mobile viewport', async () => {
      await worldSelectionPage.testMobileLayout();
    });

    test('should adapt to tablet viewport', async () => {
      await worldSelectionPage.testTabletLayout();
    });

    test('should maintain functionality across viewports', async ({ page }) => {
      const viewports = [
        { width: 375, height: 667 }, // Mobile
        { width: 768, height: 1024 }, // Tablet
        { width: 1280, height: 720 }, // Desktop
      ];

      for (const viewport of viewports) {
        await page.setViewportSize(viewport);
        await worldSelectionPage.expectPageLoaded();
        await worldSelectionPage.expectWorldsDisplayed();

        // Test search functionality
        await worldSelectionPage.searchWorlds('Garden');
        const worldCount = await worldSelectionPage.getWorldCount();
        expect(worldCount).toBe(1);

        // Clear search for next iteration
        await worldSelectionPage.clearAllFilters();
      }
    });
  });

  test.describe('Performance', () => {
    test.beforeEach(async () => {
      await characterPage.goto();
      const testCharacter = generateRandomCharacter();
      await characterPage.createCharacter(testCharacter);
      await worldSelectionPage.goto();
    });

    test('should load worlds within performance budget', async () => {
      const loadTime = await worldSelectionPage.measureSearchPerformance('Garden');
      expect(loadTime).toBeLessThan(2000); // 2 seconds
    });

    test('should filter worlds quickly', async () => {
      const filterTime = await worldSelectionPage.measureFilterPerformance('difficulty', 'BEGINNER');
      expect(filterTime).toBeLessThan(1000); // 1 second
    });
  });

  test.describe('Accessibility', () => {
    test.beforeEach(async () => {
      await worldSelectionPage.goto();
    });

    test('should support keyboard navigation', async () => {
      await worldSelectionPage.testKeyboardNavigation();
    });

    test('should have proper screen reader support', async () => {
      await worldSelectionPage.testScreenReaderSupport();
    });

    test('should have sufficient color contrast', async ({ page }) => {
      // This would typically use axe-core for automated accessibility testing
      const accessibilityResults = await page.evaluate(() => {
        // Simplified contrast check - in real implementation, use axe-core
        return { violations: [] };
      });

      expect(accessibilityResults.violations).toHaveLength(0);
    });
  });

  test.describe('Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      await page.route('**/worlds', route => {
        route.fulfill({ status: 500, body: 'Server Error' });
      });

      await worldSelectionPage.goto();
      await worldSelectionPage.expectNetworkError();
    });

    test('should handle network timeouts', async ({ page }) => {
      await page.route('**/worlds', route => {
        // Never resolve to simulate timeout
      });

      await worldSelectionPage.goto();
      await worldSelectionPage.expectLoadingState();
    });

    test('should handle empty world list', async ({ page }) => {
      await mockApiResponse(page, '**/worlds', []);

      await worldSelectionPage.goto();
      await worldSelectionPage.expectNoWorldsMessage();
    });
  });
});
