import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface AuthTestResult {
  id: string;
  role: 'patient' | 'clinician' | 'admin' | 'stakeholder' | 'developer';
  interfaceId: string;
  success: boolean;
  timestamp: string;
  duration: number;
  error?: string;
  tokenValid: boolean;
  permissions: string[];
}

export interface APITestResult {
  id: string;
  endpoint: string;
  method: string;
  status: number;
  responseTime: number;
  timestamp: string;
  success: boolean;
  error?: string;
  requestBody?: any;
  responseBody?: any;
}

export interface AccessibilityTestResult {
  id: string;
  interfaceId: string;
  violations: {
    id: string;
    impact: 'minor' | 'moderate' | 'serious' | 'critical';
    description: string;
    help: string;
    helpUrl: string;
    nodes: number;
  }[];
  passes: number;
  incomplete: number;
  timestamp: string;
  score: number; // 0-100
}

interface TestingState {
  // Authentication testing
  authTests: AuthTestResult[];
  currentAuthRole: string | null;
  authTokens: { [role: string]: string };

  // API testing
  apiTests: APITestResult[];
  apiEndpoints: {
    name: string;
    url: string;
    method: string;
    headers?: Record<string, string>;
    body?: any;
  }[];

  // Accessibility testing
  accessibilityTests: AccessibilityTestResult[];
  accessibilitySettings: {
    includeRules: string[];
    excludeRules: string[];
    level: 'A' | 'AA' | 'AAA';
    tags: string[];
  };

  // Performance testing
  performanceTests: {
    id: string;
    interfaceId: string;
    metrics: {
      loadTime: number;
      firstContentfulPaint: number;
      largestContentfulPaint: number;
      cumulativeLayoutShift: number;
      firstInputDelay: number;
    };
    timestamp: string;
    score: number;
  }[];

  // Test automation
  isRunningTests: boolean;
  testQueue: string[];
  testResults: { [testId: string]: any };
}

const initialState: TestingState = {
  authTests: [],
  currentAuthRole: null,
  authTokens: {},

  apiTests: [],
  apiEndpoints: [
    {
      name: 'Health Check',
      url: '/health',
      method: 'GET',
    },
    {
      name: 'User Profile',
      url: '/api/user/profile',
      method: 'GET',
      headers: { 'Authorization': 'Bearer {token}' },
    },
    {
      name: 'Create Session',
      url: '/api/sessions',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: { type: 'therapeutic' },
    },
  ],

  accessibilityTests: [],
  accessibilitySettings: {
    includeRules: [],
    excludeRules: [],
    level: 'AA',
    tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
  },

  performanceTests: [],

  isRunningTests: false,
  testQueue: [],
  testResults: {},
};

const testingSlice = createSlice({
  name: 'testing',
  initialState,
  reducers: {
    // Authentication testing
    addAuthTest: (state, action: PayloadAction<Omit<AuthTestResult, 'id'>>) => {
      const test: AuthTestResult = {
        ...action.payload,
        id: `auth_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      state.authTests.unshift(test);

      // Keep only last 50 tests
      if (state.authTests.length > 50) {
        state.authTests = state.authTests.slice(0, 50);
      }
    },

    setCurrentAuthRole: (state, action: PayloadAction<string | null>) => {
      state.currentAuthRole = action.payload;
    },

    setAuthToken: (state, action: PayloadAction<{ role: string; token: string }>) => {
      state.authTokens[action.payload.role] = action.payload.token;
    },

    clearAuthTokens: (state) => {
      state.authTokens = {};
    },

    // API testing
    addAPITest: (state, action: PayloadAction<Omit<APITestResult, 'id'>>) => {
      const test: APITestResult = {
        ...action.payload,
        id: `api_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      state.apiTests.unshift(test);

      // Keep only last 100 tests
      if (state.apiTests.length > 100) {
        state.apiTests = state.apiTests.slice(0, 100);
      }
    },

    addAPIEndpoint: (state, action: PayloadAction<TestingState['apiEndpoints'][0]>) => {
      state.apiEndpoints.push(action.payload);
    },

    updateAPIEndpoint: (state, action: PayloadAction<{ index: number; endpoint: TestingState['apiEndpoints'][0] }>) => {
      state.apiEndpoints[action.payload.index] = action.payload.endpoint;
    },

    removeAPIEndpoint: (state, action: PayloadAction<number>) => {
      state.apiEndpoints.splice(action.payload, 1);
    },

    // Accessibility testing
    addAccessibilityTest: (state, action: PayloadAction<Omit<AccessibilityTestResult, 'id'>>) => {
      const test: AccessibilityTestResult = {
        ...action.payload,
        id: `a11y_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      state.accessibilityTests.unshift(test);

      // Keep only last 20 tests
      if (state.accessibilityTests.length > 20) {
        state.accessibilityTests = state.accessibilityTests.slice(0, 20);
      }
    },

    updateAccessibilitySettings: (state, action: PayloadAction<Partial<TestingState['accessibilitySettings']>>) => {
      state.accessibilitySettings = { ...state.accessibilitySettings, ...action.payload };
    },

    // Performance testing
    addPerformanceTest: (state, action: PayloadAction<Omit<TestingState['performanceTests'][0], 'id'>>) => {
      const test = {
        ...action.payload,
        id: `perf_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      state.performanceTests.unshift(test);

      // Keep only last 30 tests
      if (state.performanceTests.length > 30) {
        state.performanceTests = state.performanceTests.slice(0, 30);
      }
    },

    // Test automation
    setRunningTests: (state, action: PayloadAction<boolean>) => {
      state.isRunningTests = action.payload;
    },

    addToTestQueue: (state, action: PayloadAction<string>) => {
      state.testQueue.push(action.payload);
    },

    removeFromTestQueue: (state, action: PayloadAction<string>) => {
      state.testQueue = state.testQueue.filter(id => id !== action.payload);
    },

    clearTestQueue: (state) => {
      state.testQueue = [];
    },

    setTestResult: (state, action: PayloadAction<{ testId: string; result: any }>) => {
      state.testResults[action.payload.testId] = action.payload.result;
    },

    // Utility actions
    clearAllTests: (state) => {
      state.authTests = [];
      state.apiTests = [];
      state.accessibilityTests = [];
      state.performanceTests = [];
      state.testResults = {};
    },

    clearAuthTests: (state) => {
      state.authTests = [];
    },

    clearAPITests: (state) => {
      state.apiTests = [];
    },

    clearAccessibilityTests: (state) => {
      state.accessibilityTests = [];
    },

    clearPerformanceTests: (state) => {
      state.performanceTests = [];
    },
  },
});

export const {
  addAuthTest,
  setCurrentAuthRole,
  setAuthToken,
  clearAuthTokens,
  addAPITest,
  addAPIEndpoint,
  updateAPIEndpoint,
  removeAPIEndpoint,
  addAccessibilityTest,
  updateAccessibilitySettings,
  addPerformanceTest,
  setRunningTests,
  addToTestQueue,
  removeFromTestQueue,
  clearTestQueue,
  setTestResult,
  clearAllTests,
  clearAuthTests,
  clearAPITests,
  clearAccessibilityTests,
  clearPerformanceTests,
} = testingSlice.actions;

export default testingSlice.reducer;
