const { chromium } = require('playwright');

(async () => {
  try {
    console.log('🎭 Testing character creation flow...');

    const browser = await chromium.launch({
      headless: false,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      slowMo: 1000
    });

    const page = await browser.newPage();

    // Enhanced logging
    page.on('console', msg => {
      console.log(`🖥️  CONSOLE [${msg.type()}]:`, msg.text());
    });

    page.on('pageerror', error => {
      console.log(`❌ PAGE ERROR:`, error.message);
    });

    page.on('request', request => {
      if (request.url().includes('localhost:8080')) {
        console.log(`🌐 API REQUEST: ${request.method()} ${request.url()}`);
      }
    });

    page.on('response', response => {
      if (response.url().includes('localhost:8080')) {
        console.log(`📡 API RESPONSE: ${response.status()} ${response.url()}`);
      }
    });

    console.log('📱 Step 1: Navigate and Login');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

    // Login first
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'testpass');
    await page.click('button:has-text("Sign in")');
    await page.waitForTimeout(3000);

    console.log('📸 Taking screenshot after login...');
    await page.screenshot({ path: 'char-01-after-login.png', fullPage: true });

    console.log('🎭 Step 2: Find Character Creation Button');

    // Look for character creation buttons
    const characterButtons = await page.$$('button');
    let characterButtonFound = false;

    for (let i = 0; i < characterButtons.length; i++) {
      const button = characterButtons[i];
      const buttonText = await button.textContent();
      const isVisible = await button.isVisible();
      const isEnabled = await button.isEnabled();

      console.log(`🔘 Button ${i + 1}: "${buttonText}" (visible: ${isVisible}, enabled: ${isEnabled})`);

      if (buttonText && isVisible && isEnabled && (
        buttonText.toLowerCase().includes('create') && buttonText.toLowerCase().includes('character')
      )) {
        console.log(`🎯 Found character creation button: "${buttonText}"`);

        console.log('🖱️  Clicking character creation button...');
        await button.click();
        await page.waitForTimeout(3000);

        console.log('📸 Taking screenshot after clicking character button...');
        await page.screenshot({ path: 'char-02-after-char-button.png', fullPage: true });

        characterButtonFound = true;
        break;
      }
    }

    if (!characterButtonFound) {
      console.log('⚠️  No character creation button found, checking navigation...');

      // Try clicking on Characters navigation
      const navLinks = await page.$$('a, [role="button"]');
      for (const link of navLinks) {
        const linkText = await link.textContent();
        if (linkText && linkText.toLowerCase().includes('character')) {
          console.log(`🔗 Clicking navigation link: "${linkText}"`);
          await link.click();
          await page.waitForTimeout(2000);
          break;
        }
      }
    }

    console.log('🎭 Step 3: Test Character Creation Form');

    // Look for character creation form
    const formElements = await page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll('input, textarea')).map(input => ({
        type: input.type,
        name: input.name,
        id: input.id,
        placeholder: input.placeholder,
        tagName: input.tagName.toLowerCase(),
        visible: input.offsetParent !== null
      }));

      const buttons = Array.from(document.querySelectorAll('button')).map(btn => ({
        text: btn.textContent?.trim(),
        type: btn.type,
        disabled: btn.disabled,
        visible: btn.offsetParent !== null
      }));

      return { inputs, buttons };
    });

    console.log('📝 Form elements found:');
    console.log('  Inputs:', formElements.inputs);
    console.log('  Buttons:', formElements.buttons);

    // Try to fill character creation form
    const visibleInputs = formElements.inputs.filter(input => input.visible);

    if (visibleInputs.length > 0) {
      console.log('📝 Filling character creation form...');

      // Fill name field
      const nameInput = visibleInputs.find(input =>
        input.name?.toLowerCase().includes('name') ||
        input.placeholder?.toLowerCase().includes('name') ||
        input.id?.toLowerCase().includes('name')
      );

      if (nameInput) {
        const selector = nameInput.id ? `#${nameInput.id}` :
                        nameInput.name ? `[name="${nameInput.name}"]` :
                        'input[type="text"]:visible';

        console.log(`📝 Filling name field with selector: ${selector}`);
        try {
          await page.fill(selector, 'Test Character');
          console.log('✅ Name field filled successfully');
        } catch (error) {
          console.log(`❌ Error filling name field: ${error.message}`);
        }
      }

      // Fill description field
      const descInput = visibleInputs.find(input =>
        input.name?.toLowerCase().includes('description') ||
        input.placeholder?.toLowerCase().includes('description') ||
        input.tagName === 'textarea'
      );

      if (descInput) {
        const selector = descInput.id ? `#${descInput.id}` :
                        descInput.name ? `[name="${descInput.name}"]` :
                        'textarea:visible';

        console.log(`📝 Filling description field with selector: ${selector}`);
        try {
          await page.fill(selector, 'A test character created for debugging the TTA system');
          console.log('✅ Description field filled successfully');
        } catch (error) {
          console.log(`❌ Error filling description field: ${error.message}`);
        }
      }

      console.log('📸 Taking screenshot after filling form...');
      await page.screenshot({ path: 'char-03-form-filled.png', fullPage: true });

      // Try to submit the form
      const submitButtons = formElements.buttons.filter(btn =>
        btn.visible && !btn.disabled && (
          btn.text?.toLowerCase().includes('create') ||
          btn.text?.toLowerCase().includes('add') ||
          btn.text?.toLowerCase().includes('save') ||
          btn.text?.toLowerCase().includes('submit') ||
          btn.type === 'submit'
        )
      );

      if (submitButtons.length > 0) {
        const submitButton = submitButtons[0];
        console.log(`🖱️  Clicking submit button: "${submitButton.text}"`);

        try {
          await page.click(`button:has-text("${submitButton.text}")`);
          await page.waitForTimeout(5000);

          console.log('📸 Taking screenshot after form submission...');
          await page.screenshot({ path: 'char-04-after-submit.png', fullPage: true });

          // Check for success/error messages
          const result = await page.evaluate(() => {
            const bodyText = document.body.innerText.toLowerCase();
            return {
              hasSuccess: bodyText.includes('success') || bodyText.includes('created'),
              hasError: bodyText.includes('error') || bodyText.includes('failed'),
              currentUrl: window.location.href,
              characterCount: document.body.innerText.match(/\d+/g) || []
            };
          });

          console.log('📊 Form submission result:', result);

        } catch (error) {
          console.log(`❌ Error clicking submit button: ${error.message}`);
        }
      } else {
        console.log('⚠️  No submit button found');
      }

    } else {
      console.log('⚠️  No visible input fields found for character creation');
    }

    console.log('🎭 Step 4: Test API Integration');

    // Test character API directly
    const apiTest = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8080/characters', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: 'Direct API Test Character',
            description: 'Created via direct API call from browser'
          })
        });
        const data = await response.json();
        return { success: true, status: response.status, data };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });

    console.log('🔌 Direct API test result:', apiTest);

    console.log('📸 Taking final screenshot...');
    await page.screenshot({ path: 'char-05-final.png', fullPage: true });

    console.log('⏱️  Waiting 10 seconds for final observation...');
    await page.waitForTimeout(10000);

    await browser.close();
    console.log('✅ Character creation test completed');

  } catch (error) {
    console.error('❌ Error during character creation test:', error);
  }
})();
