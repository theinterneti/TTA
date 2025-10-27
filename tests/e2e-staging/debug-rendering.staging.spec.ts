import { test, expect } from '@playwright/test';

test.describe('Debug Frontend Rendering', () => {
  test('Check what is actually rendered', async ({ page }) => {
    const consoleMessages: string[] = [];
    const pageErrors: string[] = [];

    // Capture console messages
    page.on('console', msg => {
      const text = msg.text();
      consoleMessages.push(`[${msg.type()}] ${text}`);
      console.log(`BROWSER CONSOLE [${msg.type()}]:`, text);
    });

    // Capture page errors
    page.on('pageerror', error => {
      pageErrors.push(error.message);
      console.log('PAGE ERROR:', error.message);
      console.log('Stack:', error.stack);
    });

    console.log('\n=== Navigating to http://localhost:3001/ ===');
    await page.goto('http://localhost:3001/', { waitUntil: 'networkidle', timeout: 30000 });

    // Wait for React to potentially mount
    await page.waitForTimeout(5000);

    console.log('\n=== Checking DOM ===');

    // Check root div
    const rootDiv = page.locator('#root');
    const rootExists = await rootDiv.count() > 0;
    console.log('Root div exists:', rootExists);

    if (rootExists) {
      const rootHTML = await rootDiv.innerHTML();
      console.log('Root HTML length:', rootHTML.length);
      console.log('Root HTML content:', rootHTML.substring(0, 1000));
    }

    // Check for any visible elements
    const bodyText = await page.locator('body').textContent();
    console.log('\nBody text content:', bodyText);

    // Check for buttons
    const buttonCount = await page.locator('button').count();
    console.log('\nNumber of buttons:', buttonCount);

    // Check for inputs
    const inputCount = await page.locator('input').count();
    console.log('Number of inputs:', inputCount);

    // Check for any divs
    const divCount = await page.locator('div').count();
    console.log('Number of divs:', divCount);

    // Get all text on page
    const allText = await page.evaluate(() => document.body.innerText);
    console.log('\nAll visible text on page:', allText);

    // Check if React rendered anything
    const hasReactContent = await page.evaluate(() => {
      const root = document.getElementById('root');
      return {
        rootExists: !!root,
        rootHasChildren: root ? root.children.length > 0 : false,
        rootChildCount: root ? root.children.length : 0,
        rootInnerHTML: root ? root.innerHTML.substring(0, 500) : 'NO ROOT',
      };
    });
    console.log('\nReact mount status:', JSON.stringify(hasReactContent, null, 2));

    // Take screenshot
    await page.screenshot({ path: 'test-results-staging/debug-rendering.png', fullPage: true });
    console.log('\nScreenshot saved to test-results-staging/debug-rendering.png');

    // Print console messages
    console.log('\n=== Console Messages ===');
    consoleMessages.forEach(msg => console.log(msg));

    // Print page errors
    console.log('\n=== Page Errors ===');
    if (pageErrors.length > 0) {
      pageErrors.forEach(err => console.log(err));
    } else {
      console.log('No page errors');
    }

    // Fail the test if no React content
    expect(hasReactContent.rootHasChildren, 'React should have rendered content').toBe(true);
  });
});
