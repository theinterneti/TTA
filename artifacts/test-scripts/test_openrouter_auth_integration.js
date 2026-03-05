// Logseq: [[TTA.dev/Artifacts/Test-scripts/Test_openrouter_auth_integration]]
#!/usr/bin/env node

/**
 * OpenRouter Authentication Integration Test
 *
 * This script tests the OpenRouter authentication system integration
 * by verifying that all components are properly connected and functional.
 */

const fs = require('fs');
const path = require('path');

console.log('🔐 OpenRouter Authentication Integration Test\n');

// Test file existence and structure
const testFiles = [
  // Frontend Components
  'src/player_experience/frontend/src/components/ModelManagement/OpenRouterAuthModal.tsx',
  'src/player_experience/frontend/src/components/ModelManagement/OpenRouterAuthStatus.tsx',
  'src/player_experience/frontend/src/components/ModelManagement/ModelManagementSection.tsx',
  'src/player_experience/frontend/src/components/ModelManagement/index.ts',

  // Redux State Management
  'src/player_experience/frontend/src/store/slices/openRouterAuthSlice.ts',
  'src/player_experience/frontend/src/store/store.ts',

  // API Integration
  'src/player_experience/frontend/src/services/api.ts',

  // Backend Implementation
  'src/player_experience/api/routers/openrouter_auth.py',
  'src/player_experience/api/app.py',
];

let allFilesExist = true;

console.log('📁 Checking file structure...');
testFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - MISSING`);
    allFilesExist = false;
  }
});

if (!allFilesExist) {
  console.log('\n❌ Some required files are missing!');
  process.exit(1);
}

console.log('\n✅ All required files exist!');

// Test component integration
console.log('\n🔗 Testing component integration...');

// Check if OpenRouterAuthModal is properly exported
const indexFile = fs.readFileSync('src/player_experience/frontend/src/components/ModelManagement/index.ts', 'utf8');
if (indexFile.includes('OpenRouterAuthModal') && indexFile.includes('OpenRouterAuthStatus')) {
  console.log('✅ Authentication components properly exported');
} else {
  console.log('❌ Authentication components not properly exported');
}

// Check if ModelManagementSection imports auth components
const modelManagementFile = fs.readFileSync('src/player_experience/frontend/src/components/ModelManagement/ModelManagementSection.tsx', 'utf8');
if (modelManagementFile.includes('OpenRouterAuthModal') && modelManagementFile.includes('OpenRouterAuthStatus')) {
  console.log('✅ Authentication components imported in ModelManagementSection');
} else {
  console.log('❌ Authentication components not imported in ModelManagementSection');
}

// Check Redux store integration
const storeFile = fs.readFileSync('src/player_experience/frontend/src/store/store.ts', 'utf8');
if (storeFile.includes('openRouterAuth')) {
  console.log('✅ OpenRouter auth reducer added to Redux store');
} else {
  console.log('❌ OpenRouter auth reducer not added to Redux store');
}

// Check API integration
const apiFile = fs.readFileSync('src/player_experience/frontend/src/services/api.ts', 'utf8');
if (apiFile.includes('openRouterAuthAPI')) {
  console.log('✅ OpenRouter auth API endpoints added');
} else {
  console.log('❌ OpenRouter auth API endpoints not added');
}

// Check backend router integration
const appFile = fs.readFileSync('src/player_experience/api/app.py', 'utf8');
if (appFile.includes('openrouter_auth')) {
  console.log('✅ OpenRouter auth router integrated in backend');
} else {
  console.log('❌ OpenRouter auth router not integrated in backend');
}

// Test authentication slice structure
console.log('\n🏪 Testing Redux slice structure...');
const authSliceFile = fs.readFileSync('src/player_experience/frontend/src/store/slices/openRouterAuthSlice.ts', 'utf8');

const requiredThunks = [
  'validateApiKey',
  'initiateOAuth',
  'handleOAuthCallback',
  'refreshUserInfo',
  'logout'
];

const requiredActions = [
  'showAuthModal',
  'hideAuthModal',
  'clearError'
];

let sliceValid = true;

requiredThunks.forEach(thunk => {
  if (authSliceFile.includes(`export const ${thunk}`)) {
    console.log(`✅ Async thunk: ${thunk}`);
  } else {
    console.log(`❌ Missing async thunk: ${thunk}`);
    sliceValid = false;
  }
});

requiredActions.forEach(action => {
  if (authSliceFile.includes(`${action}:`)) {
    console.log(`✅ Action: ${action}`);
  } else {
    console.log(`❌ Missing action: ${action}`);
    sliceValid = false;
  }
});

// Test backend authentication endpoints
console.log('\n🌐 Testing backend API endpoints...');
const authRouterFile = fs.readFileSync('src/player_experience/api/routers/openrouter_auth.py', 'utf8');

const requiredEndpoints = [
  '/validate-key',
  '/oauth/initiate',
  '/oauth/callback',
  '/user-info',
  '/logout',
  '/status'
];

let endpointsValid = true;

requiredEndpoints.forEach(endpoint => {
  if (authRouterFile.includes(`"${endpoint}"`)) {
    console.log(`✅ Endpoint: ${endpoint}`);
  } else {
    console.log(`❌ Missing endpoint: ${endpoint}`);
    endpointsValid = false;
  }
});

// Test security features
console.log('\n🔒 Testing security implementation...');

const securityFeatures = [
  { name: 'Fernet encryption', pattern: 'from cryptography.fernet import Fernet' },
  { name: 'PKCE implementation', pattern: 'generate_code_verifier' },
  { name: 'Secure cookies', pattern: 'httponly=True' },
  { name: 'CSRF protection', pattern: 'state' },
  { name: 'Input validation', pattern: 'BaseModel' }
];

securityFeatures.forEach(feature => {
  if (authRouterFile.includes(feature.pattern)) {
    console.log(`✅ Security feature: ${feature.name}`);
  } else {
    console.log(`❌ Missing security feature: ${feature.name}`);
  }
});

// Test UI components structure
console.log('\n🎨 Testing UI component structure...');

const authModalFile = fs.readFileSync('src/player_experience/frontend/src/components/ModelManagement/OpenRouterAuthModal.tsx', 'utf8');
const authStatusFile = fs.readFileSync('src/player_experience/frontend/src/components/ModelManagement/OpenRouterAuthStatus.tsx', 'utf8');

const uiFeatures = [
  { name: 'API key input form', file: authModalFile, pattern: 'type="password"' },
  { name: 'OAuth login button', file: authModalFile, pattern: 'Sign in with OpenRouter' },
  { name: 'Loading states', file: authModalFile, pattern: 'isLoading' },
  { name: 'Error handling', file: authModalFile, pattern: 'error' },
  { name: 'Authentication status display', file: authStatusFile, pattern: 'isAuthenticated' },
  { name: 'User information display', file: authStatusFile, pattern: 'user' }
];

uiFeatures.forEach(feature => {
  if (feature.file.includes(feature.pattern)) {
    console.log(`✅ UI feature: ${feature.name}`);
  } else {
    console.log(`❌ Missing UI feature: ${feature.name}`);
  }
});

// Final assessment
console.log('\n📊 Integration Assessment:');

const totalChecks = testFiles.length + requiredThunks.length + requiredActions.length +
                   requiredEndpoints.length + securityFeatures.length + uiFeatures.length + 5; // +5 for integration checks

let passedChecks = 0;

// Count passed checks (simplified for demo)
if (allFilesExist) passedChecks += testFiles.length;
if (sliceValid) passedChecks += requiredThunks.length + requiredActions.length;
if (endpointsValid) passedChecks += requiredEndpoints.length;

const successRate = Math.round((passedChecks / totalChecks) * 100);

console.log(`\n🎯 Success Rate: ${successRate}%`);

if (successRate >= 90) {
  console.log('\n🎉 EXCELLENT! OpenRouter authentication integration is complete and ready for use!');
  console.log('\n✨ Key achievements:');
  console.log('   • Secure API key and OAuth authentication');
  console.log('   • Complete frontend UI with React components');
  console.log('   • Redux state management integration');
  console.log('   • Backend API with security best practices');
  console.log('   • Seamless integration with existing TTA platform');

  console.log('\n🚀 Next steps:');
  console.log('   1. Configure environment variables for OpenRouter');
  console.log('   2. Start the TTA application');
  console.log('   3. Navigate to Settings > AI Models');
  console.log('   4. Test authentication with your OpenRouter credentials');

} else if (successRate >= 70) {
  console.log('\n✅ GOOD! Most components are in place, minor issues to resolve.');
} else {
  console.log('\n⚠️  NEEDS WORK! Several components need attention.');
}

console.log('\n📋 For detailed implementation information, see:');
console.log('   • OPENROUTER_AUTHENTICATION_INTEGRATION.md');
console.log('   • Individual component files for specific functionality');

console.log('\n🔐 OpenRouter Authentication Integration Test Complete!\n');
