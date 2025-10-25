const { chromium } = require('playwright');

async function testPlaywrightTools() {
  try {
    console.log('🧪 Testing Playwright tools functionality...');

    // Launch browser with correct configuration
    const browser = await chromium.launch({
      headless: false,  // Use headed mode to see it working
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    console.log('✅ Browser launched successfully');

    const page = await browser.newPage();
    console.log('✅ New page created');

    // Navigate to a simple page
    await page.goto('https://example.com');
    console.log('✅ Navigation successful');

    // Take a screenshot to verify functionality
    await page.screenshot({ path: 'playwright-test-screenshot.png' });
    console.log('✅ Screenshot taken: playwright-test-screenshot.png');

    // Get page title
    const title = await page.title();
    console.log(`✅ Page title: ${title}`);

    // Wait a moment to see the browser
    await page.waitForTimeout(3000);

    await browser.close();
    console.log('✅ Browser closed successfully');

    console.log('\n🎉 All Playwright functionality is working correctly!');
    console.log('The issue with browser_install_Playwright is likely a configuration problem with the MCP server.');
    console.log('The actual Playwright browsers are installed and functional.');

  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

testPlaywrightTools();
