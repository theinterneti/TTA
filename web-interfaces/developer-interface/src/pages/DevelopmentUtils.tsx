import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BoltIcon,
  BuildingOfficeIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CpuChipIcon,
  EyeIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { LiveReloadMonitor } from '../components/development/LiveReloadMonitor';
import { BuildStatusDashboard } from '../components/development/BuildStatusDashboard';
import { PerformanceMetrics } from '../components/development/PerformanceMetrics';
import { ErrorReporting } from '../components/development/ErrorReporting';
import { LogViewer } from '../components/development/LogViewer';

const DevelopmentUtils: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'reload' | 'build' | 'performance' | 'errors' | 'logs'>('reload');
  const [realTimeData, setRealTimeData] = useState({
    buildStatus: 'idle' as 'idle' | 'building' | 'success' | 'error',
    errorCount: 0,
    performanceScore: 0,
    lastUpdate: new Date()
  });

  const tabs = [
    {
      id: 'reload',
      name: 'Live Reload',
      icon: BoltIcon,
      description: 'Monitor live reload status across interfaces',
      color: 'text-yellow-600'
    },
    {
      id: 'build',
      name: 'Build Status',
      icon: BuildingOfficeIcon,
      description: 'Track build status and compilation errors',
      color: 'text-blue-600'
    },
    {
      id: 'performance',
      name: 'Performance',
      icon: ChartBarIcon,
      description: 'Monitor performance metrics and optimization',
      color: 'text-green-600'
    },
    {
      id: 'errors',
      name: 'Error Reporting',
      icon: ExclamationTriangleIcon,
      description: 'View and manage runtime errors',
      color: 'text-red-600'
    },
    {
      id: 'logs',
      name: 'Log Viewer',
      icon: DocumentTextIcon,
      description: 'Real-time log monitoring and filtering',
      color: 'text-purple-600'
    }
  ];

  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      setRealTimeData(prev => ({
        ...prev,
        errorCount: Math.floor(Math.random() * 5),
        performanceScore: Math.floor(Math.random() * 100),
        lastUpdate: new Date()
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'reload':
        return <LiveReloadMonitor />;
      case 'build':
        return <BuildStatusDashboard />;
      case 'performance':
        return <PerformanceMetrics />;
      case 'errors':
        return <ErrorReporting />;
      case 'logs':
        return <LogViewer />;
      default:
        return <LiveReloadMonitor />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Development Utilities</h1>
          <p className="text-gray-600 mt-1">
            Monitor and debug TTA interfaces during development
          </p>
        </div>

        {/* Real-time Status Indicators */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-white rounded-lg px-3 py-2 shadow-sm">
            <div className={`w-2 h-2 rounded-full ${
              realTimeData.buildStatus === 'success' ? 'bg-green-500' :
              realTimeData.buildStatus === 'error' ? 'bg-red-500' :
              realTimeData.buildStatus === 'building' ? 'bg-yellow-500 animate-pulse' :
              'bg-gray-400'
            }`} />
            <span className="text-sm font-medium text-gray-700">
              {realTimeData.buildStatus === 'building' ? 'Building' : 'Ready'}
            </span>
          </div>

          <div className="flex items-center space-x-2 bg-white rounded-lg px-3 py-2 shadow-sm">
            <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
            <span className="text-sm font-medium text-gray-700">
              {realTimeData.errorCount} errors
            </span>
          </div>

          <div className="flex items-center space-x-2 bg-white rounded-lg px-3 py-2 shadow-sm">
            <ClockIcon className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-gray-600">
              {realTimeData.lastUpdate.toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-4 shadow-sm border border-gray-200"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <BoltIcon className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Live Reload</p>
              <p className="text-lg font-semibold text-gray-900">Active</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-4 shadow-sm border border-gray-200"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BuildingOfficeIcon className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Build Time</p>
              <p className="text-lg font-semibold text-gray-900">2.3s</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-4 shadow-sm border border-gray-200"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CpuChipIcon className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Performance</p>
              <p className="text-lg font-semibold text-gray-900">{realTimeData.performanceScore}%</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-4 shadow-sm border border-gray-200"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Errors</p>
              <p className="text-lg font-semibold text-gray-900">{realTimeData.errorCount}</p>
            </div>
          </div>
        </motion.div>
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
                        ? tab.color
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
    </div>
  );
};

export default DevelopmentUtils;
