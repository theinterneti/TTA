// Logseq: [[TTA.dev/Player_experience/Frontend/Tests/Visual-regression/Therapeuticgoalsselector.visual.spec]]
import { test, expect } from '@playwright/test';

/**
 * Visual Regression Tests for TherapeuticGoalsSelector Component
 *
 * These tests ensure visual consistency across different states, viewports,
 * and user interactions for the TherapeuticGoalsSelector component.
 */

// Test configuration
const STORYBOOK_BASE = 'http://localhost:6007/iframe.html?id=';
const COMPONENT_STORIES = {
  default: 'components-playerpreferences-therapeuticgoalsselector--default',
  withSelectedGoals: 'components-playerpreferences-therapeuticgoalsselector--with-selected-goals',
  withSelectedConcerns: 'components-playerpreferences-therapeuticgoalsselector--with-selected-concerns',
  withCustomEntries: 'components-playerpreferences-therapeuticgoalsselector--with-custom-entries',
  maximumSelections: 'components-playerpreferences-therapeuticgoalsselector--maximum-selections',
  playground: 'components-playerpreferences-therapeuticgoalsselector--playground',
};

// Helper function to prepare page for visual testing
async function preparePageForVisualTesting(page: any) {
  // Disable animations for consistent screenshots
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-delay: -1ms !important;
        animation-duration: 1ms !important;
        animation-iteration-count: 1 !important;
        background-attachment: initial !important;
        scroll-behavior: auto !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
    `,
  });

  // Wait for fonts and images to load
  await page.waitForLoadState('networkidle');

  // Additional stabilization wait
  await page.waitForTimeout(1000);
}

test.describe('TherapeuticGoalsSelector - Visual Regression Tests', () => {

  test.describe('Component States', () => {

    test('should render default state consistently', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.default}`);
      await preparePageForVisualTesting(page);

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-default.png');
    });

    test('should render with selected goals consistently', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.withSelectedGoals}`);
      await preparePageForVisualTesting(page);

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-with-selected-goals.png');
    });

    test('should render with selected concerns consistently', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.withSelectedConcerns}`);
      await preparePageForVisualTesting(page);

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-with-selected-concerns.png');
    });

    test('should render with custom entries consistently', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.withCustomEntries}`);
      await preparePageForVisualTesting(page);

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-with-custom-entries.png');
    });

    test('should render maximum selections consistently', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.maximumSelections}`);
      await preparePageForVisualTesting(page);

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-maximum-selections.png');
    });
  });

  test.describe('Interactive States', () => {

    test('should render hover states consistently', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.default}`);
      await preparePageForVisualTesting(page);

      // Hover over a goal checkbox
      const firstGoal = page.locator('input[type="checkbox"]').first();
      await firstGoal.hover();

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-hover-state.png');
    });

    test('should render focus states consistently', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.default}`);
      await preparePageForVisualTesting(page);

      // Focus on the first tab
      const goalsTab = page.locator('button[role="tab"]').first();
      await goalsTab.focus();

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-focus-state.png');
    });

    test('should render concerns tab consistently', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.default}`);
      await preparePageForVisualTesting(page);

      // Click on concerns tab
      const concernsTab = page.locator('button[role="tab"]', { hasText: 'Primary Concerns' });
      await concernsTab.click();
      await page.waitForTimeout(500);

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-concerns-tab.png');
    });
  });

  test.describe('Responsive Design', () => {

    test('should render consistently on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.default}`);
      await preparePageForVisualTesting(page);

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-mobile.png');
    });

    test('should render consistently on tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 }); // iPad
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.default}`);
      await preparePageForVisualTesting(page);

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-tablet.png');
    });

    test('should render consistently on large desktop viewport', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 }); // Large desktop
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.default}`);
      await preparePageForVisualTesting(page);

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-large-desktop.png');
    });
  });

  test.describe('Error States and Edge Cases', () => {

    test('should render empty state consistently', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.playground}`);
      await preparePageForVisualTesting(page);

      // Clear all selections using Storybook controls if available
      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-empty-state.png');
    });
  });

  test.describe('Goal Suggestion System - Visual Tests', () => {

    test('should render AI-powered suggestions section', async ({ page }) => {
      // Navigate to a story that shows suggestions (we'll need to create this)
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.playground}`);
      await preparePageForVisualTesting(page);

      // Simulate selecting primary concerns to trigger suggestions
      // First switch to concerns tab
      await page.click('button[role="tab"]:has-text("Primary Concerns")');

      // Select a concern to trigger suggestions
      await page.click('text="Work stress"');

      // Switch back to goals tab to see suggestions
      await page.click('button[role="tab"]:has-text("Therapeutic Goals")');

      // Wait for suggestions to appear
      await page.waitForSelector('text="🤖 AI-Powered Goal Suggestions"', { timeout: 5000 });

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('therapeutic-goals-selector-with-suggestions.png');
    });

    test('should render suggestion strength indicators', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.playground}`);
      await preparePageForVisualTesting(page);

      // Trigger suggestions
      await page.click('button[role="tab"]:has-text("Primary Concerns")');
      await page.click('text="Work stress"');
      await page.click('button[role="tab"]:has-text("Therapeutic Goals")');

      await page.waitForSelector('text="🤖 AI-Powered Goal Suggestions"', { timeout: 5000 });

      // Focus on the suggestion section
      const suggestionSection = page.locator('text="🤖 AI-Powered Goal Suggestions"').locator('..');
      await expect(suggestionSection).toHaveScreenshot('suggestion-strength-indicators.png');
    });

    test('should render individual suggestion cards', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.playground}`);
      await preparePageForVisualTesting(page);

      // Trigger suggestions
      await page.click('button[role="tab"]:has-text("Primary Concerns")');
      await page.click('text="Social anxiety"');
      await page.click('button[role="tab"]:has-text("Therapeutic Goals")');

      await page.waitForSelector('text="🤖 AI-Powered Goal Suggestions"', { timeout: 5000 });

      // Focus on individual suggestion cards
      const suggestionCards = page.locator('[class*="grid-cols-1 md:grid-cols-2"] > div');
      await expect(suggestionCards.first()).toHaveScreenshot('individual-suggestion-card.png');
    });

    test('should render applied suggestions state', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.playground}`);
      await preparePageForVisualTesting(page);

      // Trigger suggestions
      await page.click('button[role="tab"]:has-text("Primary Concerns")');
      await page.click('text="Work stress"');
      await page.click('button[role="tab"]:has-text("Therapeutic Goals")');

      await page.waitForSelector('text="🤖 AI-Powered Goal Suggestions"', { timeout: 5000 });

      // Apply a suggestion
      await page.click('button:has-text("Add"):first');

      // Wait for state update
      await page.waitForTimeout(500);

      const component = page.locator('#storybook-root');
      await expect(component).toHaveScreenshot('suggestions-with-applied-goals.png');
    });

    test('should render suggestions across different viewports', async ({ page }) => {
      const viewports = [
        { name: 'mobile', width: 375, height: 667 },
        { name: 'tablet', width: 768, height: 1024 },
        { name: 'desktop', width: 1200, height: 800 }
      ];

      for (const viewport of viewports) {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.playground}`);
        await preparePageForVisualTesting(page);

        // Trigger suggestions
        await page.click('button[role="tab"]:has-text("Primary Concerns")');
        await page.click('text="Work stress"');
        await page.click('button[role="tab"]:has-text("Therapeutic Goals")');

        await page.waitForSelector('text="🤖 AI-Powered Goal Suggestions"', { timeout: 5000 });

        const component = page.locator('#storybook-root');
        await expect(component).toHaveScreenshot(`suggestions-${viewport.name}-viewport.png`);
      }
    });

    test('should render hover states for suggestion buttons', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.playground}`);
      await preparePageForVisualTesting(page);

      // Trigger suggestions
      await page.click('button[role="tab"]:has-text("Primary Concerns")');
      await page.click('text="Work stress"');
      await page.click('button[role="tab"]:has-text("Therapeutic Goals")');

      await page.waitForSelector('text="🤖 AI-Powered Goal Suggestions"', { timeout: 5000 });

      // Hover over Add button
      const addButton = page.locator('button:has-text("Add"):first');
      await addButton.hover();

      const suggestionSection = page.locator('text="🤖 AI-Powered Goal Suggestions"').locator('..');
      await expect(suggestionSection).toHaveScreenshot('suggestion-button-hover-state.png');
    });

    test('should render focus states for suggestion buttons', async ({ page }) => {
      await page.goto(`${STORYBOOK_BASE}${COMPONENT_STORIES.playground}`);
      await preparePageForVisualTesting(page);

      // Trigger suggestions
      await page.click('button[role="tab"]:has-text("Primary Concerns")');
      await page.click('text="Work stress"');
      await page.click('button[role="tab"]:has-text("Therapeutic Goals")');

      await page.waitForSelector('text="🤖 AI-Powered Goal Suggestions"', { timeout: 5000 });

      // Focus Add button using keyboard
      await page.keyboard.press('Tab');
      const addButton = page.locator('button:has-text("Add"):first');
      await addButton.focus();

      const suggestionSection = page.locator('text="🤖 AI-Powered Goal Suggestions"').locator('..');
      await expect(suggestionSection).toHaveScreenshot('suggestion-button-focus-state.png');
    });
  });
});
