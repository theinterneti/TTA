import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  UserIcon,
  KeyIcon,
  CogIcon,
  BeakerIcon,
  ClipboardDocumentIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { AuthSwitcher } from '../components/testing/AuthSwitcher';
import { JWTTokenManager } from '../components/testing/JWTTokenManager';
import { EnvironmentSwitcher } from '../components/testing/EnvironmentSwitcher';
import { QuickAPITester } from '../components/testing/QuickAPITester';
import { InterfaceHealthMonitor } from '../components/testing/InterfaceHealthMonitor';
import { TestScenarioRunner } from '../components/testing/TestScenarioRunner';

const TestingTools: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'auth' | 'jwt' | 'env' | 'api' | 'health' | 'scenarios'>('auth');

  const tabs = [
    { id: 'auth', name: 'Authentication', icon: UserIcon, description: 'Switch between user roles' },
    { id: 'jwt', name: 'JWT Manager', icon: KeyIcon, description: 'Generate and validate tokens' },
    { id: 'env', name: 'Environment', icon: CogIcon, description: 'Switch environments' },
    { id: 'api', name: 'Quick API Test', icon: BeakerIcon, description: 'Test API endpoints' },
    { id: 'health', name: 'Health Monitor', icon: CheckCircleIcon, description: 'Monitor interface health' },
    { id: 'scenarios', name: 'Test Scenarios', icon: ClipboardDocumentIcon, description: 'Run test scenarios' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'auth':
        return <AuthSwitcher />;
      case 'jwt':
        return <JWTTokenManager />;
      case 'env':
        return <EnvironmentSwitcher />;
      case 'api':
        return <QuickAPITester />;
      case 'health':
        return <InterfaceHealthMonitor />;
      case 'scenarios':
        return <TestScenarioRunner />;
      default:
        return <AuthSwitcher />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Testing Tools</h1>
        <p className="text-gray-600 mt-1">
          Comprehensive testing and development utilities for TTA interfaces
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon
                    className={`-ml-0.5 mr-2 h-5 w-5 transition-colors ${
                      activeTab === tab.id
                        ? 'text-blue-500'
                        : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                  />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* Tab Description */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                {tabs.find(tab => tab.id === activeTab)?.name}
              </h2>
              <p className="text-gray-600">
                {tabs.find(tab => tab.id === activeTab)?.description}
              </p>
            </div>

            {/* Tab Content */}
            {renderTabContent()}
          </motion.div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 cursor-pointer"
          onClick={() => setActiveTab('health')}
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Health Check</h3>
              <p className="text-sm text-gray-600">Check all interfaces</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 cursor-pointer"
          onClick={() => setActiveTab('auth')}
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <UserIcon className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Switch Role</h3>
              <p className="text-sm text-gray-600">Test different users</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 cursor-pointer"
          onClick={() => setActiveTab('api')}
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <BeakerIcon className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">API Test</h3>
              <p className="text-sm text-gray-600">Quick endpoint test</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default TestingTools;
