const { chromium } = require('playwright');

(async () => {
  try {
    console.log('Launching browser...');
    const browser = await chromium.launch({ 
      headless: false,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    console.log('Creating new page...');
    const page = await browser.newPage();
    
    console.log('Navigating to localhost:3000...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    
    console.log('Page title:', await page.title());
    console.log('Page URL:', page.url());
    
    // Take a screenshot
    await page.screenshot({ path: 'frontend-screenshot.png' });
    console.log('Screenshot saved as frontend-screenshot.png');
    
    // Wait a bit to see the page
    await page.waitForTimeout(5000);
    
    await browser.close();
    console.log('Browser closed successfully');
  } catch (error) {
    console.error('Error:', error);
  }
})();
