// Logseq: [[TTA.dev/Player_experience/Frontend/Tests/Visual-regression/Global-setup]]
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🎨 Setting up visual regression testing environment...');

  // Launch browser for setup
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Wait for Storybook to be ready
    console.log('⏳ Waiting for Storybook to be ready...');
    await page.goto('http://localhost:6007');

    // Wait for Storybook to fully load - try multiple selectors
    try {
      await page.waitForSelector('#storybook-explorer-tree', { timeout: 15000 });
    } catch {
      try {
        await page.waitForSelector('[data-testid="sidebar-container"]', { timeout: 15000 });
      } catch {
        // Fallback: wait for any story link to appear
        await page.waitForSelector('a[href*="story"]', { timeout: 15000 });
      }
    }

    // Verify TherapeuticGoalsSelector stories are available
    const storiesExist = await page.locator('text=TherapeuticGoalsSelector').isVisible();
    if (!storiesExist) {
      console.warn('⚠️  TherapeuticGoalsSelector stories not immediately visible, but continuing...');
    }

    console.log('✅ Storybook is ready for visual regression testing');

    // Pre-warm the browser cache by visiting key stories
    const storiesToPrewarm = [
      '/story/components-playerpreferences-therapeuticgoalsselector--default',
      '/story/components-playerpreferences-therapeuticgoalsselector--with-selected-goals',
      '/story/components-playerpreferences-therapeuticgoalsselector--with-custom-entries',
    ];

    for (const story of storiesToPrewarm) {
      try {
        await page.goto(`http://localhost:6007/iframe.html?id=${story.replace('/story/', '')}`);
        await page.waitForLoadState('networkidle');
        console.log(`✅ Pre-warmed story: ${story}`);
      } catch (error) {
        console.warn(`⚠️  Could not pre-warm story ${story}:`, error);
      }
    }

  } catch (error) {
    console.error('❌ Failed to setup visual regression testing environment:', error);
    throw error;
  } finally {
    await browser.close();
  }

  console.log('🎨 Visual regression testing environment setup complete!');
}

export default globalSetup;
