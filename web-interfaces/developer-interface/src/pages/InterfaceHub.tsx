import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ComputerDesktopIcon,
  HeartIcon,
  UserGroupIcon,
  CogIcon,
  GlobeAltIcon,
  ChartBarIcon,
  DocumentTextIcon,
  EyeIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/react/24/outline';
import { InterfaceCard } from '../components/interfaces/InterfaceCard';
import { InterfacePreview } from '../components/interfaces/InterfacePreview';
import { HealthStatus } from '../components/monitoring/HealthStatus';
import { useInterfaceHealth } from '../hooks/useInterfaceHealth';

interface TTAInterface {
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
}

const InterfaceHub: React.FC = () => {
  const [selectedInterface, setSelectedInterface] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<'grid' | 'preview'>('grid');
  const { healthStatus, isLoading, refetch } = useInterfaceHealth();

  const interfaces: TTAInterface[] = [
    {
      id: 'patient',
      name: 'Patient/Player Interface',
      description: 'Therapeutic gaming experience for patients and users',
      port: 3000,
      url: '/',
      directUrl: 'http://localhost:3000',
      icon: ComputerDesktopIcon,
      color: 'bg-blue-500',
      status: healthStatus?.patient || 'unknown',
      features: ['Character Creation', 'World Exploration', 'Therapeutic Chat', 'Progress Tracking'],
      technology: ['React 18', 'TypeScript', 'Tailwind CSS', 'Framer Motion']
    },
    {
      id: 'clinical',
      name: 'Clinical Dashboard',
      description: 'Healthcare provider monitoring and oversight',
      port: 3001,
      url: '/clinical',
      directUrl: 'http://localhost:3001',
      icon: HeartIcon,
      color: 'bg-green-500',
      status: healthStatus?.clinical || 'unknown',
      features: ['Patient Monitoring', 'Analytics', 'Crisis Management', 'HIPAA Compliance'],
      technology: ['React 18', 'TypeScript', 'Material-UI', 'Chart.js']
    },
    {
      id: 'admin',
      name: 'System Administrator',
      description: 'System management and administration',
      port: 3002,
      url: '/admin',
      directUrl: 'http://localhost:3002',
      icon: CogIcon,
      color: 'bg-purple-500',
      status: healthStatus?.admin || 'unknown',
      features: ['User Management', 'System Monitoring', 'Configuration', 'Database Admin'],
      technology: ['React 18', 'TypeScript', 'Ant Design', 'Monaco Editor']
    },
    {
      id: 'public',
      name: 'Public Information Portal',
      description: 'General information and research findings',
      port: 3003,
      url: '/public',
      directUrl: 'http://localhost:3003',
      icon: GlobeAltIcon,
      color: 'bg-indigo-500',
      status: healthStatus?.public || 'unknown',
      features: ['Research Findings', 'System Information', 'Public Access', 'Documentation'],
      technology: ['Next.js', 'TypeScript', 'Tailwind CSS', 'Static Generation']
    },
    {
      id: 'stakeholder',
      name: 'Stakeholder Dashboard',
      description: 'Research and oversight data access',
      port: 3004,
      url: '/stakeholder',
      directUrl: 'http://localhost:3004',
      icon: ChartBarIcon,
      color: 'bg-orange-500',
      status: healthStatus?.stakeholder || 'unknown',
      features: ['Analytics', 'Research Data', 'Performance Metrics', 'Export Tools'],
      technology: ['React 18', 'TypeScript', 'Chart.js', 'D3.js']
    },
    {
      id: 'api-docs',
      name: 'API Documentation Portal',
      description: 'Interactive API documentation and testing',
      port: 3005,
      url: '/docs',
      directUrl: 'http://localhost:3005',
      icon: DocumentTextIcon,
      color: 'bg-teal-500',
      status: healthStatus?.apiDocs || 'unknown',
      features: ['Interactive Docs', 'API Testing', 'Code Examples', 'Authentication'],
      technology: ['React 18', 'TypeScript', 'Swagger UI', 'Monaco Editor']
    }
  ];

  useEffect(() => {
    // Auto-refresh health status every 30 seconds
    const interval = setInterval(() => {
      refetch();
    }, 30000);

    return () => clearInterval(interval);
  }, [refetch]);

  const handleInterfaceSelect = (interfaceId: string) => {
    setSelectedInterface(interfaceId);
    setPreviewMode('preview');
  };

  const handleBackToGrid = () => {
    setSelectedInterface(null);
    setPreviewMode('grid');
  };

  const selectedInterfaceData = interfaces.find(i => i.id === selectedInterface);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Interface Hub</h1>
          <p className="text-gray-600 mt-1">
            Navigate and preview all TTA web interfaces from a single dashboard
          </p>
        </div>

        <div className="flex items-center space-x-4">
          <HealthStatus
            isLoading={isLoading}
            onRefresh={refetch}
            healthData={healthStatus}
          />

          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setPreviewMode('grid')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                previewMode === 'grid'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Grid View
            </button>
            <button
              onClick={() => setPreviewMode('preview')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                previewMode === 'preview'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              disabled={!selectedInterface}
            >
              Preview
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      {previewMode === 'grid' ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {interfaces.map((interface_) => (
            <InterfaceCard
              key={interface_.id}
              interface={interface_}
              onSelect={() => handleInterfaceSelect(interface_.id)}
              onOpenDirect={() => window.open(interface_.directUrl, '_blank')}
            />
          ))}
        </motion.div>
      ) : (
        selectedInterfaceData && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="space-y-4"
          >
            {/* Preview Header */}
            <div className="flex items-center justify-between bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleBackToGrid}
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  ← Back to Grid
                </button>
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${selectedInterfaceData.color}`}>
                    <selectedInterfaceData.icon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {selectedInterfaceData.name}
                    </h2>
                    <p className="text-sm text-gray-600">
                      {selectedInterfaceData.description}
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  selectedInterfaceData.status === 'healthy'
                    ? 'bg-green-100 text-green-800'
                    : selectedInterfaceData.status === 'unhealthy'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {selectedInterfaceData.status}
                </span>

                <button
                  onClick={() => window.open(selectedInterfaceData.directUrl, '_blank')}
                  className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                >
                  <ArrowTopRightOnSquareIcon className="h-4 w-4 mr-1" />
                  Open Direct
                </button>
              </div>
            </div>

            {/* Interface Preview */}
            <InterfacePreview
              interface={selectedInterfaceData}
              onError={() => {
                // Handle preview error
                console.error(`Failed to load preview for ${selectedInterfaceData.name}`);
              }}
            />
          </motion.div>
        )
      )}
    </div>
  );
};

export default InterfaceHub;
