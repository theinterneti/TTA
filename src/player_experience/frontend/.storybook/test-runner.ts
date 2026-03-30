// Logseq: [[TTA.dev/Player_experience/Frontend/.storybook/Test-runner]]
import type { TestRunnerConfig } from '@storybook/test-runner';
import { getStoryContext } from '@storybook/test-runner';

const config: TestRunnerConfig = {
  setup() {
    // Global setup for visual regression tests
    console.log('Setting up visual regression testing environment...');
  },

  async preVisit(page, context) {
    // Configure page for consistent visual testing
    await page.setViewportSize({ width: 1200, height: 800 });

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

    // Wait for fonts to load
    await page.waitForLoadState('networkidle');

    // Additional wait for component stabilization
    await page.waitForTimeout(500);
  },

  async postVisit(page, context) {
    const storyContext = await getStoryContext(page, context);

    // Skip visual regression for certain stories
    const skipVisualRegression = storyContext.parameters?.visualRegression?.disable;
    if (skipVisualRegression) {
      return;
    }

    // Take screenshot for visual regression testing
    const screenshotPath = `visual-regression/${context.id}.png`;

    // Get the story element for focused screenshots
    const storyElement = page.locator('#storybook-root');

    await expect(storyElement).toHaveScreenshot(screenshotPath, {
      // Configure screenshot options for consistency
      fullPage: false,
      animations: 'disabled',
      caret: 'hide',
      scale: 'css',
      mode: 'css',
      threshold: 0.2, // Allow 20% pixel difference threshold
      maxDiffPixels: 1000, // Maximum different pixels allowed
    });
  },

  // Configure test timeout
  testTimeout: 60000,
};

export default config;
