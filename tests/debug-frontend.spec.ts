// Logseq: [[TTA.dev/Tests/Debug-frontend.spec]]
import { test, expect } from '@playwright/test';

test('Debug frontend rendering', async ({ page }) => {
  // Enable console logging
  page.on('console', msg => console.log('BROWSER:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));

  console.log('Navigating to http://localhost:3001/');
  await page.goto('http://localhost:3001/', { waitUntil: 'networkidle' });

  // Wait a bit for React to mount
  await page.waitForTimeout(3000);

  // Check if root div exists
  const rootDiv = await page.locator('#root');
  console.log('Root div exists:', await rootDiv.count() > 0);

  // Get the HTML content of root
  const rootHTML = await rootDiv.innerHTML().catch(() => 'ERROR');
  console.log('Root HTML length:', rootHTML.length);
  console.log('Root HTML preview:', rootHTML.substring(0, 500));

  // Check for any visible text
  const bodyText = await page.locator('body').textContent();
  console.log('Body text:', bodyText);

  // Check for React app mounting
  const hasReactApp = await page.evaluate(() => {
    const root = document.getElementById('root');
    return {
      rootExists: !!root,
      rootHasChildren: root ? root.children.length > 0 : false,
      rootHTML: root ? root.innerHTML.substring(0, 200) : 'NO ROOT',
    };
  });
  console.log('React app status:', JSON.stringify(hasReactApp, null, 2));

  // Check for any buttons
  const buttons = await page.locator('button').count();
  console.log('Number of buttons found:', buttons);

  // Check for any inputs
  const inputs = await page.locator('input').count();
  console.log('Number of inputs found:', inputs);

  // Take a screenshot
  await page.screenshot({ path: 'debug-frontend.png', fullPage: true });
  console.log('Screenshot saved to debug-frontend.png');
});
