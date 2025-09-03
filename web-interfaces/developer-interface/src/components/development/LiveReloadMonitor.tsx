import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BoltIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  SignalIcon
} from '@heroicons/react/24/outline';
import useWebSocket from 'react-use-websocket';

interface InterfaceStatus {
  id: string;
  name: string;
  port: number;
  status: 'connected' | 'disconnected' | 'reloading' | 'error';
  lastReload: Date | null;
  reloadCount: number;
  buildTime: number;
  errors: string[];
}

export const LiveReloadMonitor: React.FC = () => {
  const [interfaces, setInterfaces] = useState<InterfaceStatus[]>([
    {
      id: 'patient',
      name: 'Patient Interface',
      port: 3000,
      status: 'connected',
      lastReload: new Date(),
      reloadCount: 12,
      buildTime: 1.2,
      errors: []
    },
    {
      id: 'clinical',
      name: 'Clinical Dashboard',
      port: 3001,
      status: 'connected',
      lastReload: new Date(Date.now() - 30000),
      reloadCount: 8,
      buildTime: 2.1,
      errors: []
    },
    {
      id: 'admin',
      name: 'Admin Interface',
      port: 3002,
      status: 'reloading',
      lastReload: new Date(Date.now() - 5000),
      reloadCount: 15,
      buildTime: 1.8,
      errors: []
    },
    {
      id: 'public',
      name: 'Public Portal',
      port: 3003,
      status: 'connected',
      lastReload: new Date(Date.now() - 120000),
      reloadCount: 3,
      buildTime: 0.9,
      errors: []
    },
    {
      id: 'stakeholder',
      name: 'Stakeholder Dashboard',
      port: 3004,
      status: 'error',
      lastReload: new Date(Date.now() - 300000),
      reloadCount: 5,
      buildTime: 3.2,
      errors: ['TypeScript compilation error', 'Missing dependency']
    },
    {
      id: 'api-docs',
      name: 'API Documentation',
      port: 3005,
      status: 'connected',
      lastReload: new Date(Date.now() - 60000),
      reloadCount: 7,
      buildTime: 1.5,
      errors: []
    }
  ]);

  const [globalStats, setGlobalStats] = useState({
    totalReloads: 0,
    averageBuildTime: 0,
    activeConnections: 0,
    errorCount: 0
  });

  // WebSocket connection for real-time updates (mock implementation)
  const { lastMessage, connectionStatus } = useWebSocket(
    'ws://localhost:3006/ws/live-reload',
    {
      shouldReconnect: () => true,
      reconnectAttempts: 10,
      reconnectInterval: 3000,
    }
  );

  useEffect(() => {
    // Calculate global stats
    const stats = interfaces.reduce((acc, interface_) => ({
      totalReloads: acc.totalReloads + interface_.reloadCount,
      averageBuildTime: acc.averageBuildTime + interface_.buildTime,
      activeConnections: acc.activeConnections + (interface_.status === 'connected' ? 1 : 0),
      errorCount: acc.errorCount + interface_.errors.length
    }), { totalReloads: 0, averageBuildTime: 0, activeConnections: 0, errorCount: 0 });

    stats.averageBuildTime = stats.averageBuildTime / interfaces.length;
    setGlobalStats(stats);
  }, [interfaces]);

  useEffect(() => {
    // Simulate live reload events
    const interval = setInterval(() => {
      setInterfaces(prev => prev.map(interface_ => {
        if (Math.random() < 0.1) { // 10% chance of reload
          return {
            ...interface_,
            status: 'reloading',
            lastReload: new Date(),
            reloadCount: interface_.reloadCount + 1,
            buildTime: Math.random() * 3 + 0.5
          };
        }
        if (interface_.status === 'reloading' && Math.random() < 0.7) {
          return {
            ...interface_,
            status: Math.random() < 0.9 ? 'connected' : 'error'
          };
        }
        return interface_;
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: InterfaceStatus['status']) => {
    switch (status) {
      case 'connected':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'reloading':
        return <ArrowPathIcon className="h-5 w-5 text-yellow-500 animate-spin" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'disconnected':
        return <SignalIcon className="h-5 w-5 text-gray-400" />;
      default:
        return <SignalIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: InterfaceStatus['status']) => {
    switch (status) {
      case 'connected':
        return 'bg-green-100 text-green-800';
      case 'reloading':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'disconnected':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const forceReload = (interfaceId: string) => {
    setInterfaces(prev => prev.map(interface_ =>
      interface_.id === interfaceId
        ? { ...interface_, status: 'reloading', lastReload: new Date() }
        : interface_
    ));
  };

  return (
    <div className="space-y-6">
      {/* Global Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <BoltIcon className="h-6 w-6 text-blue-600" />
            <div>
              <p className="text-sm text-blue-600">Total Reloads</p>
              <p className="text-2xl font-bold text-blue-900">{globalStats.totalReloads}</p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <CheckCircleIcon className="h-6 w-6 text-green-600" />
            <div>
              <p className="text-sm text-green-600">Active Connections</p>
              <p className="text-2xl font-bold text-green-900">{globalStats.activeConnections}</p>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <ClockIcon className="h-6 w-6 text-purple-600" />
            <div>
              <p className="text-sm text-purple-600">Avg Build Time</p>
              <p className="text-2xl font-bold text-purple-900">
                {globalStats.averageBuildTime.toFixed(1)}s
              </p>
            </div>
          </div>
        </div>

        <div className="bg-red-50 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <XCircleIcon className="h-6 w-6 text-red-600" />
            <div>
              <p className="text-sm text-red-600">Errors</p>
              <p className="text-2xl font-bold text-red-900">{globalStats.errorCount}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Interface Status List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Interface Status</h3>
          <p className="text-sm text-gray-600">Real-time monitoring of live reload status</p>
        </div>

        <div className="divide-y divide-gray-200">
          {interfaces.map((interface_) => (
            <motion.div
              key={interface_.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="px-6 py-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(interface_.status)}
                  <div>
                    <h4 className="font-medium text-gray-900">{interface_.name}</h4>
                    <p className="text-sm text-gray-600">Port {interface_.port}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-6">
                  <div className="text-right">
                    <p className="text-sm text-gray-900">
                      {interface_.reloadCount} reloads
                    </p>
                    <p className="text-xs text-gray-600">
                      {interface_.buildTime.toFixed(1)}s build time
                    </p>
                  </div>

                  <div className="text-right">
                    <p className="text-sm text-gray-900">
                      {interface_.lastReload
                        ? interface_.lastReload.toLocaleTimeString()
                        : 'Never'
                      }
                    </p>
                    <p className="text-xs text-gray-600">Last reload</p>
                  </div>

                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(interface_.status)}`}>
                    {interface_.status}
                  </span>

                  <button
                    onClick={() => forceReload(interface_.id)}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                  >
                    <ArrowPathIcon className="h-4 w-4 mr-1" />
                    Reload
                  </button>
                </div>
              </div>

              {/* Error Messages */}
              {interface_.errors.length > 0 && (
                <div className="mt-3 p-3 bg-red-50 rounded-lg">
                  <h5 className="text-sm font-medium text-red-800 mb-1">Errors:</h5>
                  <ul className="text-sm text-red-700 space-y-1">
                    {interface_.errors.map((error, index) => (
                      <li key={index}>• {error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* WebSocket Connection Status */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              connectionStatus === 'Open' ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-sm font-medium text-gray-900">
              WebSocket Connection: {connectionStatus}
            </span>
          </div>
          <span className="text-sm text-gray-600">
            Real-time updates {connectionStatus === 'Open' ? 'enabled' : 'disabled'}
          </span>
        </div>
      </div>
    </div>
  );
};
