import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown for TTA E2E tests...');
  
  try {
    // Clean up authentication state
    const authStatePath = path.join(__dirname, 'auth-state.json');
    if (fs.existsSync(authStatePath)) {
      fs.unlinkSync(authStatePath);
      console.log('🗑️ Cleaned up authentication state');
    }
    
    // Clean up any temporary test data
    await cleanupTestData();
    
    console.log('✅ Global teardown complete');
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error to avoid failing the test run
  }
}

async function cleanupTestData() {
  // Clean up any test data that might have been created
  // This could include test characters, sessions, etc.
  console.log('🧹 Cleaning up test data...');
  
  // Add cleanup logic here if needed
  // For example, API calls to delete test data
}

export default globalTeardown;
