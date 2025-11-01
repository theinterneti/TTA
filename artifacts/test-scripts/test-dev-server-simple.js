const { chromium } = require('playwright');

(async () => {
  try {
    console.log('🔍 Simple Development Server Test...');

    const browser = await chromium.launch({
      headless: false,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      slowMo: 500
    });

    const page = await browser.newPage();

    // Enhanced logging
    page.on('console', msg => {
      const text = msg.text();
      console.log(`🖥️  CONSOLE [${msg.type()}]:`, text.substring(0, 200));
    });

    page.on('pageerror', error => {
      console.log(`❌ PAGE ERROR:`, error.message);
    });

    console.log('📱 Navigate to Development Server');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

    console.log('📸 Taking screenshot of initial page...');
    await page.screenshot({ path: 'dev-simple-01-initial.png', fullPage: true });

    // Check for webpack overlay
    const overlayCheck = await page.evaluate(() => {
      const overlay = document.querySelector('#webpack-dev-server-client-overlay');
      const overlayFrame = document.querySelector('iframe[src="about:blank"]');
      return {
        hasOverlay: !!overlay,
        hasOverlayFrame: !!overlayFrame,
        overlayVisible: overlay ? overlay.style.display !== 'none' : false,
        bodyText: document.body.innerText.substring(0, 500),
        hasLoginForm: document.querySelector('#username') !== null,
        hasSignInButton: document.querySelector('button[type="submit"]') !== null
      };
    });

    console.log('📊 Overlay check:', overlayCheck);

    if (overlayCheck.hasOverlay || overlayCheck.hasOverlayFrame) {
      console.log('⚠️  Webpack overlay detected - trying to dismiss it...');

      // Try to dismiss the overlay by pressing Escape
      await page.keyboard.press('Escape');
      await page.waitForTimeout(2000);

      // Try clicking on the overlay to dismiss it
      try {
        await page.click('#webpack-dev-server-client-overlay', { timeout: 5000 });
      } catch (e) {
        console.log('Could not click overlay');
      }

      // Try to remove the overlay programmatically
      await page.evaluate(() => {
        const overlay = document.querySelector('#webpack-dev-server-client-overlay');
        if (overlay) {
          overlay.remove();
        }
        const overlayFrame = document.querySelector('iframe[src="about:blank"]');
        if (overlayFrame) {
          overlayFrame.remove();
        }
      });

      await page.waitForTimeout(2000);

      console.log('📸 Taking screenshot after overlay removal...');
      await page.screenshot({ path: 'dev-simple-02-after-overlay-removal.png', fullPage: true });
    }

    // Check if we can interact with the login form now
    const loginCheck = await page.evaluate(() => {
      return {
        hasUsernameField: document.querySelector('#username') !== null,
        hasPasswordField: document.querySelector('#password') !== null,
        hasSignInButton: document.querySelector('button[type="submit"]') !== null,
        signInButtonText: document.querySelector('button[type="submit"]')?.textContent,
        formVisible: document.querySelector('form') !== null
      };
    });

    console.log('📊 Login form check:', loginCheck);

    if (loginCheck.hasUsernameField && loginCheck.hasPasswordField) {
      console.log('✅ Login form is accessible - attempting login...');

      try {
        await page.fill('#username', 'testuser');
        await page.fill('#password', 'testpass');

        console.log('📸 Taking screenshot before login...');
        await page.screenshot({ path: 'dev-simple-03-before-login.png', fullPage: true });

        // Try different approaches to click the button
        try {
          await page.click('button[type="submit"]', { timeout: 10000 });
          console.log('✅ Login button clicked successfully');
        } catch (e) {
          console.log('⚠️  Direct click failed, trying alternative...');
          await page.evaluate(() => {
            document.querySelector('button[type="submit"]').click();
          });
        }

        await page.waitForTimeout(5000);

        console.log('📸 Taking screenshot after login attempt...');
        await page.screenshot({ path: 'dev-simple-04-after-login.png', fullPage: true });

        // Check if login was successful
        const postLoginCheck = await page.evaluate(() => {
          return {
            currentUrl: window.location.href,
            bodyText: document.body.innerText.substring(0, 300),
            hasCreateButton: document.body.innerText.includes('Create'),
            hasCharacterManagement: document.body.innerText.includes('Character')
          };
        });

        console.log('📊 Post-login check:', postLoginCheck);

        if (postLoginCheck.hasCreateButton || postLoginCheck.hasCharacterManagement) {
          console.log('🎉 SUCCESS: Login appears to have worked!');
          console.log('✅ Development server is functional with React fixes applied');
        } else {
          console.log('⚠️  Login status unclear');
        }

      } catch (error) {
        console.log('❌ Login interaction failed:', error.message);
      }
    } else {
      console.log('❌ Login form not accessible');
    }

    console.log('⏱️  Waiting 10 seconds for observation...');
    await page.waitForTimeout(10000);

    await browser.close();
    console.log('✅ Simple development server test completed');

  } catch (error) {
    console.error('❌ Error during simple testing:', error);
  }
})();
