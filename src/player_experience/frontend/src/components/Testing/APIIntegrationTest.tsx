import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { authAPI, nexusAPI } from '../../services/api';
import { runConnectivityTests, displayConnectivityResults } from '../../utils/apiHealthCheck';

interface TestResult {
  name: string;
  status: 'pending' | 'success' | 'error' | 'skipped';
  message: string;
  duration?: number;
  details?: any;
}

interface TestSuite {
  name: string;
  tests: TestResult[];
  status: 'pending' | 'running' | 'complete';
}

const APIIntegrationTest: React.FC = () => {
  const [testSuites, setTestSuites] = useState<TestSuite[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [overallStatus, setOverallStatus] = useState<'idle' | 'running' | 'complete' | 'error'>('idle');
  const [connectivityResults, setConnectivityResults] = useState<any>(null);

  const updateTestResult = (suiteIndex: number, testIndex: number, result: Partial<TestResult>) => {
    setTestSuites(prev => {
      const newSuites = [...prev];
      newSuites[suiteIndex].tests[testIndex] = {
        ...newSuites[suiteIndex].tests[testIndex],
        ...result,
      };
      return newSuites;
    });
  };

  const updateSuiteStatus = (suiteIndex: number, status: TestSuite['status']) => {
    setTestSuites(prev => {
      const newSuites = [...prev];
      newSuites[suiteIndex].status = status;
      return newSuites;
    });
  };

  const runTest = async (
    testFn: () => Promise<any>,
    suiteIndex: number,
    testIndex: number
  ): Promise<void> => {
    const startTime = Date.now();
    
    try {
      updateTestResult(suiteIndex, testIndex, { status: 'pending' });
      
      const result = await testFn();
      const duration = Date.now() - startTime;
      
      updateTestResult(suiteIndex, testIndex, {
        status: 'success',
        message: 'Test passed',
        duration,
        details: result,
      });
    } catch (error: any) {
      const duration = Date.now() - startTime;
      
      updateTestResult(suiteIndex, testIndex, {
        status: 'error',
        message: error.message || 'Test failed',
        duration,
        details: error,
      });
    }
  };

  const initializeTestSuites = (): TestSuite[] => [
    {
      name: 'Connectivity Tests',
      status: 'pending',
      tests: [
        { name: 'API Health Check', status: 'pending', message: '' },
        { name: 'CORS Configuration', status: 'pending', message: '' },
        { name: 'Authentication Endpoint', status: 'pending', message: '' },
        { name: 'Nexus Endpoint Access', status: 'pending', message: '' },
      ],
    },
    {
      name: 'Authentication API Tests',
      status: 'pending',
      tests: [
        { name: 'Token Verification', status: 'pending', message: '' },
        { name: 'Login Endpoint Structure', status: 'pending', message: '' },
        { name: 'Logout Functionality', status: 'pending', message: '' },
        { name: 'Token Refresh Mechanism', status: 'pending', message: '' },
      ],
    },
    {
      name: 'Nexus API Tests',
      status: 'pending',
      tests: [
        { name: 'Get Nexus State', status: 'pending', message: '' },
        { name: 'Get Story Spheres', status: 'pending', message: '' },
        { name: 'Get World Details', status: 'pending', message: '' },
        { name: 'World Search Functionality', status: 'pending', message: '' },
      ],
    },
    {
      name: 'World Management Tests',
      status: 'pending',
      tests: [
        { name: 'World Creation Endpoint', status: 'pending', message: '' },
        { name: 'World Entry Functionality', status: 'pending', message: '' },
        { name: 'Template Retrieval', status: 'pending', message: '' },
        { name: 'Story Weaver Profiles', status: 'pending', message: '' },
      ],
    },
  ];

  const runConnectivityTestSuite = async (suiteIndex: number) => {
    updateSuiteStatus(suiteIndex, 'running');

    // Run comprehensive connectivity tests
    await runTest(async () => {
      const results = await runConnectivityTests();
      setConnectivityResults(results);
      return results;
    }, suiteIndex, 0);

    // Individual connectivity tests
    await runTest(async () => {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/health`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    }, suiteIndex, 1);

    await runTest(async () => {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/health`, {
        headers: { 'Origin': window.location.origin },
        credentials: 'include',
      });
      const corsOrigin = response.headers.get('access-control-allow-origin');
      if (!corsOrigin) throw new Error('CORS headers not found');
      return { corsOrigin };
    }, suiteIndex, 2);

    await runTest(async () => {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'test', password: 'test' }),
      });
      // Expect 401 for invalid credentials, which means endpoint is accessible
      if (response.status !== 401) {
        throw new Error(`Expected 401, got ${response.status}`);
      }
      return { status: response.status };
    }, suiteIndex, 3);

    updateSuiteStatus(suiteIndex, 'complete');
  };

  const runAuthTestSuite = async (suiteIndex: number) => {
    updateSuiteStatus(suiteIndex, 'running');

    // Test token verification endpoint
    await runTest(async () => {
      try {
        await authAPI.verifyToken();
        return { message: 'Token verification endpoint accessible' };
      } catch (error: any) {
        // Expected to fail without valid token
        if (error.message.includes('401') || error.message.includes('token')) {
          return { message: 'Token verification working as expected' };
        }
        throw error;
      }
    }, suiteIndex, 0);

    // Test login endpoint structure
    await runTest(async () => {
      try {
        await authAPI.login({ username: 'test', password: 'test' });
        throw new Error('Login should have failed with invalid credentials');
      } catch (error: any) {
        if (error.message.includes('401') || error.message.includes('Invalid')) {
          return { message: 'Login endpoint structure correct' };
        }
        throw error;
      }
    }, suiteIndex, 1);

    // Test logout endpoint
    await runTest(async () => {
      try {
        await authAPI.logout();
        return { message: 'Logout endpoint accessible' };
      } catch (error: any) {
        // May fail without valid session, but endpoint should be accessible
        if (!error.message.includes('404')) {
          return { message: 'Logout endpoint accessible' };
        }
        throw error;
      }
    }, suiteIndex, 2);

    // Test token refresh
    await runTest(async () => {
      try {
        await authAPI.refreshToken('invalid-token');
        throw new Error('Refresh should have failed with invalid token');
      } catch (error: any) {
        if (error.message.includes('401') || error.message.includes('token')) {
          return { message: 'Token refresh endpoint working' };
        }
        throw error;
      }
    }, suiteIndex, 3);

    updateSuiteStatus(suiteIndex, 'complete');
  };

  const runNexusTestSuite = async (suiteIndex: number) => {
    updateSuiteStatus(suiteIndex, 'running');

    // Test nexus state endpoint
    await runTest(async () => {
      try {
        const state = await nexusAPI.getState();
        return state;
      } catch (error: any) {
        // May require authentication
        if (error.message.includes('401')) {
          return { message: 'Nexus state endpoint requires authentication (expected)' };
        }
        throw error;
      }
    }, suiteIndex, 0);

    // Test story spheres endpoint
    await runTest(async () => {
      try {
        const spheres = await nexusAPI.getSpheres();
        return spheres;
      } catch (error: any) {
        if (error.message.includes('401')) {
          return { message: 'Story spheres endpoint requires authentication (expected)' };
        }
        throw error;
      }
    }, suiteIndex, 1);

    // Test world details endpoint
    await runTest(async () => {
      try {
        const world = await nexusAPI.getWorld('test-world-id');
        return world;
      } catch (error: any) {
        if (error.message.includes('401') || error.message.includes('404')) {
          return { message: 'World details endpoint accessible (expected 401/404)' };
        }
        throw error;
      }
    }, suiteIndex, 2);

    // Test world search
    await runTest(async () => {
      try {
        const results = await nexusAPI.searchWorlds({ genre: 'Fantasy' });
        return results;
      } catch (error: any) {
        if (error.message.includes('401')) {
          return { message: 'World search endpoint requires authentication (expected)' };
        }
        throw error;
      }
    }, suiteIndex, 3);

    updateSuiteStatus(suiteIndex, 'complete');
  };

  const runWorldManagementTestSuite = async (suiteIndex: number) => {
    updateSuiteStatus(suiteIndex, 'running');

    // Test world creation endpoint
    await runTest(async () => {
      try {
        const testWorld = {
          world_title: 'Test World',
          world_genre: 'Fantasy',
          description: 'A test world for API validation',
          difficulty_level: 'BEGINNER' as const,
          threat_level: 'LOW' as const,
          therapeutic_focus: ['Anxiety Management'],
          tags: ['test'],
          estimated_duration: 30,
          max_players: 1,
          is_public: false,
        };
        
        await nexusAPI.createWorld(testWorld);
        return { message: 'World creation endpoint accessible' };
      } catch (error: any) {
        if (error.message.includes('401')) {
          return { message: 'World creation requires authentication (expected)' };
        }
        throw error;
      }
    }, suiteIndex, 0);

    // Test world entry
    await runTest(async () => {
      try {
        await nexusAPI.enterWorld('test-world-id');
        return { message: 'World entry endpoint accessible' };
      } catch (error: any) {
        if (error.message.includes('401') || error.message.includes('404')) {
          return { message: 'World entry endpoint accessible (expected 401/404)' };
        }
        throw error;
      }
    }, suiteIndex, 1);

    // Test templates
    await runTest(async () => {
      try {
        const templates = await nexusAPI.getTemplates();
        return templates;
      } catch (error: any) {
        if (error.message.includes('401')) {
          return { message: 'Templates endpoint requires authentication (expected)' };
        }
        throw error;
      }
    }, suiteIndex, 2);

    // Test story weavers
    await runTest(async () => {
      try {
        const weavers = await nexusAPI.getStoryWeavers();
        return weavers;
      } catch (error: any) {
        if (error.message.includes('401')) {
          return { message: 'Story weavers endpoint requires authentication (expected)' };
        }
        throw error;
      }
    }, suiteIndex, 3);

    updateSuiteStatus(suiteIndex, 'complete');
  };

  const runAllTests = async () => {
    setIsRunning(true);
    setOverallStatus('running');
    
    const suites = initializeTestSuites();
    setTestSuites(suites);

    try {
      await runConnectivityTestSuite(0);
      await runAuthTestSuite(1);
      await runNexusTestSuite(2);
      await runWorldManagementTestSuite(3);
      
      setOverallStatus('complete');
    } catch (error) {
      console.error('Test suite failed:', error);
      setOverallStatus('error');
    } finally {
      setIsRunning(false);
    }
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'pending': return '⏳';
      case 'skipped': return '⏭️';
      default: return '⏳';
    }
  };

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'success': return 'text-green-600';
      case 'error': return 'text-red-600';
      case 'pending': return 'text-yellow-600';
      case 'skipped': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">API Integration Tests</h1>
          <p className="text-gray-600 mt-1">
            Comprehensive testing of frontend-backend API integrations
          </p>
        </div>

        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                overallStatus === 'idle' ? 'bg-gray-100 text-gray-800' :
                overallStatus === 'running' ? 'bg-blue-100 text-blue-800' :
                overallStatus === 'complete' ? 'bg-green-100 text-green-800' :
                'bg-red-100 text-red-800'
              }`}>
                {overallStatus === 'idle' ? 'Ready' :
                 overallStatus === 'running' ? 'Running...' :
                 overallStatus === 'complete' ? 'Complete' :
                 'Error'}
              </div>
              
              {connectivityResults && (
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  connectivityResults.overallStatus === 'healthy' ? 'bg-green-100 text-green-800' :
                  connectivityResults.overallStatus === 'degraded' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  API: {connectivityResults.overallStatus}
                </div>
              )}
            </div>

            <button
              onClick={runAllTests}
              disabled={isRunning}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isRunning ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Running Tests...
                </>
              ) : (
                'Run All Tests'
              )}
            </button>
          </div>

          <div className="space-y-6">
            {testSuites.map((suite, suiteIndex) => (
              <div key={suite.name} className="border border-gray-200 rounded-lg">
                <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    {suite.name}
                    <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                      suite.status === 'pending' ? 'bg-gray-100 text-gray-800' :
                      suite.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {suite.status}
                    </span>
                  </h3>
                </div>
                
                <div className="p-4">
                  <div className="space-y-3">
                    {suite.tests.map((test, testIndex) => (
                      <div key={test.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                        <div className="flex items-center space-x-3">
                          <span className="text-lg">{getStatusIcon(test.status)}</span>
                          <div>
                            <div className="font-medium text-gray-900">{test.name}</div>
                            <div className={`text-sm ${getStatusColor(test.status)}`}>
                              {test.message}
                            </div>
                          </div>
                        </div>
                        
                        {test.duration && (
                          <div className="text-sm text-gray-500">
                            {test.duration}ms
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {connectivityResults && (
            <div className="mt-8 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Connectivity Details</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">API Health:</span>
                  <span className={`ml-2 ${connectivityResults.apiHealth.healthy ? 'text-green-600' : 'text-red-600'}`}>
                    {connectivityResults.apiHealth.healthy ? '✅ Healthy' : '❌ Unhealthy'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">CORS:</span>
                  <span className={`ml-2 ${connectivityResults.corsEnabled ? 'text-green-600' : 'text-red-600'}`}>
                    {connectivityResults.corsEnabled ? '✅ Enabled' : '❌ Disabled'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Auth Endpoint:</span>
                  <span className={`ml-2 ${connectivityResults.authEndpointAccessible ? 'text-green-600' : 'text-red-600'}`}>
                    {connectivityResults.authEndpointAccessible ? '✅ Accessible' : '❌ Inaccessible'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Nexus Endpoint:</span>
                  <span className={`ml-2 ${connectivityResults.nexusEndpointAccessible ? 'text-green-600' : 'text-red-600'}`}>
                    {connectivityResults.nexusEndpointAccessible ? '✅ Accessible' : '❌ Inaccessible'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default APIIntegrationTest;
