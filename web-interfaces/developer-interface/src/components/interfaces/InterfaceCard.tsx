import React from 'react';
import { motion } from 'framer-motion';
import {
  ArrowTopRightOnSquareIcon,
  EyeIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface InterfaceCardProps {
  interface: {
    id: string;
    name: string;
    description: string;
    port: number;
    url: string;
    directUrl: string;
    icon: React.ComponentType<any>;
    color: string;
    status: 'healthy' | 'unhealthy' | 'unknown';
    features: string[];
    technology: string[];
  };
  onSelect: () => void;
  onOpenDirect: () => void;
}

export const InterfaceCard: React.FC<InterfaceCardProps> = ({
  interface: interface_,
  onSelect,
  onOpenDirect
}) => {
  const Icon = interface_.icon;

  const getStatusIcon = () => {
    switch (interface_.status) {
      case 'healthy':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'unhealthy':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusColor = () => {
    switch (interface_.status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'unhealthy':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200 overflow-hidden"
    >
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-lg ${interface_.color}`}>
              <Icon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{interface_.name}</h3>
              <p className="text-sm text-gray-600">Port {interface_.port}</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor()}`}>
              {interface_.status}
            </span>
          </div>
        </div>

        <p className="text-gray-600 text-sm mb-4">{interface_.description}</p>

        {/* Features */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Key Features</h4>
          <div className="flex flex-wrap gap-1">
            {interface_.features.slice(0, 3).map((feature) => (
              <span
                key={feature}
                className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
              >
                {feature}
              </span>
            ))}
            {interface_.features.length > 3 && (
              <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-600">
                +{interface_.features.length - 3} more
              </span>
            )}
          </div>
        </div>

        {/* Technology Stack */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Technology</h4>
          <div className="flex flex-wrap gap-1">
            {interface_.technology.map((tech) => (
              <span
                key={tech}
                className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            <button
              onClick={onSelect}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
            >
              <EyeIcon className="h-4 w-4 mr-1" />
              Preview
            </button>

            <button
              onClick={onOpenDirect}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
            >
              <ArrowTopRightOnSquareIcon className="h-4 w-4 mr-1" />
              Open
            </button>
          </div>

          <div className="text-right">
            <p className="text-xs text-gray-600">Direct URL</p>
            <code className="text-xs font-mono text-gray-800">
              :{interface_.port}
            </code>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
