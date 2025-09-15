import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ComputerDesktopIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  BoltIcon,
  CpuChipIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const [systemStats, setSystemStats] = useState({
    totalInterfaces: 7,
    healthyInterfaces: 6,
    buildTime: 2.3,
    errorCount: 1,
    lastUpdate: new Date(),
    performanceScore: 94
  });

  const [recentActivity, setRecentActivity] = useState([
    { id: 1, type: 'build', message: 'Patient Interface build completed', time: '2 minutes ago', status: 'success' },
    { id: 2, type: 'error', message: 'Stakeholder Dashboard compilation error', time: '5 minutes ago', status: 'error' },
    { id: 3, type: 'reload', message: 'Clinical Dashboard hot reload', time: '8 minutes ago', status: 'info' },
    { id: 4, type: 'test', message: 'API endpoint test completed', time: '12 minutes ago', status: 'success' },
    { id: 5, type: 'deploy', message: 'Developer Interface deployed', time: '15 minutes ago', status: 'success' }
  ]);

  const quickActions = [
    {
      name: 'Interface Hub',
      description: 'Navigate and preview all interfaces',
      icon: ComputerDesktopIcon,
      color: 'bg-blue-500',
      link: '/interfaces'
    },
    {
      name: 'Testing Tools',
      description: 'Authentication and API testing',
      icon: BoltIcon,
      color: 'bg-yellow-500',
      link: '/testing'
    },
    {
      name: 'Performance Monitor',
      description: 'View performance metrics',
      icon: ChartBarIcon,
      color: 'bg-green-500',
      link: '/performance'
    },
    {
      name: 'Development Utils',
      description: 'Build status and error reporting',
      icon: CpuChipIcon,
      color: 'bg-purple-500',
      link: '/development'
    }
  ];

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setSystemStats(prev => ({
        ...prev,
        lastUpdate: new Date(),
        performanceScore: Math.floor(Math.random() * 20) + 80,
        errorCount: Math.floor(Math.random() * 3)
      }));
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'build':
        return <CpuChipIcon className="h-5 w-5" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5" />;
      case 'reload':
        return <BoltIcon className="h-5 w-5" />;
      case 'test':
        return <CheckCircleIcon className="h-5 w-5" />;
      case 'deploy':
        return <ComputerDesktopIcon className="h-5 w-5" />;
      default:
        return <ClockIcon className="h-5 w-5" />;
    }
  };

  const getActivityColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600 bg-green-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'info':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Developer Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Unified development environment for TTA web interfaces
          </p>
        </div>

        <div className="flex items-center space-x-3 bg-white rounded-lg px-4 py-2 shadow-sm">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-sm font-medium text-gray-700">Live</span>
          <span className="text-sm text-gray-500">
            {systemStats.lastUpdate.toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-6 shadow-sm border border-gray-200"
        >
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <ComputerDesktopIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Interfaces</p>
              <p className="text-2xl font-bold text-gray-900">{systemStats.totalInterfaces}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-6 shadow-sm border border-gray-200"
        >
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Healthy</p>
              <p className="text-2xl font-bold text-gray-900">
                {systemStats.healthyInterfaces}/{systemStats.totalInterfaces}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-6 shadow-sm border border-gray-200"
        >
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <ClockIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Build Time</p>
              <p className="text-2xl font-bold text-gray-900">{systemStats.buildTime}s</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-lg p-6 shadow-sm border border-gray-200"
        >
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-lg ${systemStats.errorCount > 0 ? 'bg-red-100' : 'bg-gray-100'}`}>
              <ExclamationTriangleIcon className={`h-6 w-6 ${systemStats.errorCount > 0 ? 'text-red-600' : 'text-gray-400'}`} />
            </div>
            <div>
              <p className="text-sm text-gray-600">Errors</p>
              <p className="text-2xl font-bold text-gray-900">{systemStats.errorCount}</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link key={action.name} to={action.link}>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className={`p-2 rounded-lg ${action.color}`}>
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <h3 className="font-medium text-gray-900">{action.name}</h3>
                  </div>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </motion.div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {recentActivity.map((activity) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="px-6 py-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className={`p-2 rounded-lg ${getActivityColor(activity.status)}`}>
                  {getActivityIcon(activity.type)}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                  <p className="text-xs text-gray-600">{activity.time}</p>
                </div>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  activity.status === 'success' ? 'bg-green-100 text-green-800' :
                  activity.status === 'error' ? 'bg-red-100 text-red-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {activity.status}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Performance Overview */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Performance Overview</h2>
          <Link
            to="/performance"
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View Details →
          </Link>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex-1 bg-gray-200 rounded-full h-3">
            <div
              className="bg-green-500 h-3 rounded-full transition-all duration-500"
              style={{ width: `${systemStats.performanceScore}%` }}
            />
          </div>
          <span className="text-lg font-semibold text-gray-900">
            {systemStats.performanceScore}%
          </span>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Overall system performance score based on build times, error rates, and response times
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
