const { chromium } = require('playwright');

(async () => {
  try {
    console.log('🚀 Starting complete TTA user flow testing...');
    
    const browser = await chromium.launch({ 
      headless: false,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      slowMo: 500
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
        if (request.method() === 'POST') {
          console.log(`📤 POST DATA:`, request.postData());
        }
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('localhost:8080')) {
        console.log(`📡 API RESPONSE: ${response.status()} ${response.url()}`);
      }
    });
    
    console.log('📱 Navigating to frontend...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    
    console.log('📸 Taking initial screenshot...');
    await page.screenshot({ path: 'flow-01-initial.png', fullPage: true });
    
    // Step 1: Test Authentication
    console.log('🔐 Step 1: Testing Authentication');
    
    // Fill in login credentials
    console.log('📝 Filling login form...');
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'testpass');
    
    console.log('📸 Taking screenshot before login...');
    await page.screenshot({ path: 'flow-02-before-login.png', fullPage: true });
    
    // Click sign in
    console.log('🖱️  Clicking Sign In button...');
    await page.click('button:has-text("Sign in")');
    
    // Wait for response
    await page.waitForTimeout(3000);
    
    console.log('📸 Taking screenshot after login attempt...');
    await page.screenshot({ path: 'flow-03-after-login.png', fullPage: true });
    
    // Check if we're still on login page or moved to main app
    const currentUrl = page.url();
    console.log('🔗 Current URL after login:', currentUrl);
    
    // Look for main app elements
    const mainAppElements = await page.evaluate(() => {
      const elements = {
        hasCharacterSection: !!document.querySelector('[data-testid="character-section"], .character, [class*="character"]'),
        hasDashboard: !!document.querySelector('[data-testid="dashboard"], .dashboard, [class*="dashboard"]'),
        hasNavigation: !!document.querySelector('nav, [role="navigation"]'),
        hasCreateButton: !!document.querySelector('button:has-text("Create"), button:has-text("Add"), button:has-text("New")'),
        allButtons: Array.from(document.querySelectorAll('button')).map(btn => btn.textContent?.trim()).filter(Boolean),
        allHeadings: Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => h.textContent?.trim()).filter(Boolean)
      };
      return elements;
    });
    
    console.log('🎯 Main app elements found:', mainAppElements);
    
    // Step 2: Navigate to Character Creation
    console.log('🎭 Step 2: Testing Character Creation Navigation');
    
    // Look for character-related navigation or buttons
    const characterButtons = await page.$$('button, a, [role="button"]');
    let characterCreationFound = false;
    
    for (let i = 0; i < characterButtons.length; i++) {
      const element = characterButtons[i];
      const text = await element.textContent();
      const isVisible = await element.isVisible();
      
      if (text && isVisible && (
        text.toLowerCase().includes('character') ||
        text.toLowerCase().includes('create') ||
        text.toLowerCase().includes('new') ||
        text.toLowerCase().includes('add')
      )) {
        console.log(`🎯 Found potential character creation element: "${text}"`);
        
        try {
          console.log('🖱️  Clicking character creation element...');
          await element.click();
          await page.waitForTimeout(2000);
          
          console.log('📸 Taking screenshot after character navigation...');
          await page.screenshot({ path: `flow-04-character-nav-${i}.png`, fullPage: true });
          
          characterCreationFound = true;
          break;
        } catch (error) {
          console.log(`❌ Error clicking element: ${error.message}`);
        }
      }
    }
    
    if (!characterCreationFound) {
      console.log('⚠️  No character creation navigation found, checking current page for forms...');
    }
    
    // Step 3: Test Character Creation Form
    console.log('🎭 Step 3: Testing Character Creation Form');
    
    // Look for character creation form elements
    const formElements = await page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll('input[type="text"], input[name*="name"], textarea')).map(input => ({
        type: input.type,
        name: input.name,
        id: input.id,
        placeholder: input.placeholder,
        visible: input.offsetParent !== null
      }));
      
      const submitButtons = Array.from(document.querySelectorAll('button[type="submit"], button:has-text("Create"), button:has-text("Add"), button:has-text("Save")')).map(btn => ({
        text: btn.textContent?.trim(),
        type: btn.type,
        disabled: btn.disabled,
        visible: btn.offsetParent !== null
      }));
      
      return { inputs, submitButtons };
    });
    
    console.log('📝 Form elements found:', formElements);
    
    // Try to fill character creation form
    if (formElements.inputs.length > 0) {
      console.log('📝 Attempting to fill character creation form...');
      
      // Fill name field
      const nameInput = formElements.inputs.find(input => 
        input.name?.toLowerCase().includes('name') || 
        input.placeholder?.toLowerCase().includes('name') ||
        input.id?.toLowerCase().includes('name')
      );
      
      if (nameInput) {
        const selector = nameInput.id ? `#${nameInput.id}` : 
                        nameInput.name ? `[name="${nameInput.name}"]` : 
                        'input[type="text"]';
        
        console.log(`📝 Filling name field with selector: ${selector}`);
        await page.fill(selector, 'Test Character');
        await page.waitForTimeout(1000);
      }
      
      // Fill description if available
      const descInput = formElements.inputs.find(input => 
        input.name?.toLowerCase().includes('description') || 
        input.placeholder?.toLowerCase().includes('description')
      );
      
      if (descInput) {
        const selector = descInput.id ? `#${descInput.id}` : `[name="${descInput.name}"]`;
        console.log(`📝 Filling description field with selector: ${selector}`);
        await page.fill(selector, 'A test character for debugging purposes');
        await page.waitForTimeout(1000);
      }
      
      console.log('📸 Taking screenshot after filling form...');
      await page.screenshot({ path: 'flow-05-form-filled.png', fullPage: true });
      
      // Try to submit the form
      if (formElements.submitButtons.length > 0) {
        const submitButton = formElements.submitButtons.find(btn => !btn.disabled && btn.visible);
        
        if (submitButton) {
          console.log(`🖱️  Clicking submit button: "${submitButton.text}"`);
          await page.click(`button:has-text("${submitButton.text}")`);
          await page.waitForTimeout(3000);
          
          console.log('📸 Taking screenshot after form submission...');
          await page.screenshot({ path: 'flow-06-after-submit.png', fullPage: true });
        }
      }
    }
    
    // Step 4: Test API Integration
    console.log('🔌 Step 4: Testing API Integration');
    
    const apiTests = await page.evaluate(async () => {
      const results = {};
      
      // Test health endpoint
      try {
        const healthResponse = await fetch('http://localhost:8080/health');
        results.health = {
          success: true,
          status: healthResponse.status,
          data: await healthResponse.json()
        };
      } catch (error) {
        results.health = { success: false, error: error.message };
      }
      
      // Test character creation
      try {
        const charResponse = await fetch('http://localhost:8080/characters', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: 'API Test Character',
            description: 'Created via API test'
          })
        });
        results.characterCreate = {
          success: true,
          status: charResponse.status,
          data: await charResponse.json()
        };
      } catch (error) {
        results.characterCreate = { success: false, error: error.message };
      }
      
      // Test character listing
      try {
        const listResponse = await fetch('http://localhost:8080/characters');
        results.characterList = {
          success: true,
          status: listResponse.status,
          data: await listResponse.json()
        };
      } catch (error) {
        results.characterList = { success: false, error: error.message };
      }
      
      return results;
    });
    
    console.log('🔌 API test results:', JSON.stringify(apiTests, null, 2));
    
    console.log('📸 Taking final screenshot...');
    await page.screenshot({ path: 'flow-07-final.png', fullPage: true });
    
    console.log('⏱️  Waiting 5 seconds for final observation...');
    await page.waitForTimeout(5000);
    
    await browser.close();
    console.log('✅ Complete flow testing finished');
    
  } catch (error) {
    console.error('❌ Error during complete flow testing:', error);
  }
})();
