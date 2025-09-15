import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  HomeIcon,
  ComputerDesktopIcon,
  BeakerIcon,
  WrenchScrewdriverIcon,
  ChartBarIcon,
  EyeIcon,
  NetworkIcon,
  CogIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';

interface DeveloperLayoutProps {
  children: React.ReactNode;
}

export const DeveloperLayout: React.FC<DeveloperLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Interface Hub', href: '/interfaces', icon: ComputerDesktopIcon },
    { name: 'Testing Tools', href: '/testing', icon: BeakerIcon },
    { name: 'Development Utils', href: '/development', icon: WrenchScrewdriverIcon },
    { name: 'API Testing', href: '/api-testing', icon: NetworkIcon },
    { name: 'Performance', href: '/performance', icon: ChartBarIcon },
    { name: 'Accessibility', href: '/accessibility', icon: EyeIcon },
    { name: 'Network Monitor', href: '/network', icon: NetworkIcon },
    { name: 'Settings', href: '/settings', icon: CogIcon },
  ];

  const isActive = (href: string) => {
    return location.pathname === href || (href !== '/dashboard' && location.pathname.startsWith(href));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <WrenchScrewdriverIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">TTA Dev</h1>
              <p className="text-xs text-gray-600">Developer Interface</p>
            </div>
          </div>

          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 rounded-md text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);

              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    active
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <Icon
                    className={`mr-3 h-5 w-5 transition-colors ${
                      active
                        ? 'text-blue-500'
                        : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Environment Indicator */}
        <div className="absolute bottom-4 left-3 right-3">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-yellow-800">Development Mode</span>
            </div>
            <p className="text-xs text-yellow-700 mt-1">
              This interface is for development use only
            </p>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-30 bg-white border-b border-gray-200 px-4 py-3 lg:px-6">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
            >
              <Bars3Icon className="h-6 w-6" />
            </button>

            <div className="flex items-center space-x-4">
              {/* Environment Switcher */}
              <select className="text-sm border border-gray-300 rounded-md px-3 py-1 bg-white">
                <option value="development">Development</option>
                <option value="staging" disabled>Staging</option>
                <option value="production" disabled>Production</option>
              </select>

              {/* Status Indicator */}
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span>All Systems Operational</span>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-4 lg:p-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
};
