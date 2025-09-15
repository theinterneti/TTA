import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  UserIcon,
  HeartIcon,
  CogIcon,
  ChartBarIcon,
  CodeBracketIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  ClipboardDocumentIcon
} from '@heroicons/react/24/outline';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import toast from 'react-hot-toast';

interface UserRole {
  id: string;
  name: string;
  role: 'patient' | 'clinician' | 'admin' | 'stakeholder' | 'developer' | 'public';
  description: string;
  icon: React.ComponentType<any>;
  color: string;
  permissions: string[];
  interfaces: string[];
  sampleCredentials: {
    username: string;
    password: string;
  };
}

export const AuthSwitcher: React.FC = () => {
  const [selectedRole, setSelectedRole] = useState<string>('patient');
  const [generatedToken, setGeneratedToken] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);

  const userRoles: UserRole[] = [
    {
      id: 'patient',
      name: 'Patient/Player',
      role: 'patient',
      description: 'End user accessing therapeutic gaming features',
      icon: UserIcon,
      color: 'bg-blue-500',
      permissions: ['read:own_profile', 'write:own_progress', 'access:therapeutic_chat'],
      interfaces: ['Patient Interface'],
      sampleCredentials: {
        username: 'test_patient',
        password: 'patient123'
      }
    },
    {
      id: 'clinician',
      name: 'Healthcare Provider',
      role: 'clinician',
      description: 'Clinical staff monitoring patient progress',
      icon: HeartIcon,
      color: 'bg-green-500',
      permissions: ['read:patient_data', 'write:clinical_notes', 'access:crisis_management'],
      interfaces: ['Clinical Dashboard', 'Patient Interface'],
      sampleCredentials: {
        username: 'dr_smith',
        password: 'clinician123'
      }
    },
    {
      id: 'admin',
      name: 'System Administrator',
      role: 'admin',
      description: 'Full system access and management',
      icon: CogIcon,
      color: 'bg-purple-500',
      permissions: ['read:all', 'write:all', 'admin:system', 'admin:users'],
      interfaces: ['All Interfaces'],
      sampleCredentials: {
        username: 'admin',
        password: 'admin123'
      }
    },
    {
      id: 'stakeholder',
      name: 'Researcher/Stakeholder',
      role: 'stakeholder',
      description: 'Read-only access to aggregated data',
      icon: ChartBarIcon,
      color: 'bg-orange-500',
      permissions: ['read:analytics', 'read:reports', 'export:data'],
      interfaces: ['Stakeholder Dashboard'],
      sampleCredentials: {
        username: 'researcher',
        password: 'research123'
      }
    },
    {
      id: 'developer',
      name: 'Developer',
      role: 'developer',
      description: 'API access and development tools',
      icon: CodeBracketIcon,
      color: 'bg-indigo-500',
      permissions: ['read:api_docs', 'test:endpoints', 'debug:system'],
      interfaces: ['API Documentation', 'Developer Interface'],
      sampleCredentials: {
        username: 'developer',
        password: 'dev123'
      }
    },
    {
      id: 'public',
      name: 'Public User',
      role: 'public',
      description: 'No authentication required',
      icon: GlobeAltIcon,
      color: 'bg-gray-500',
      permissions: ['read:public_info'],
      interfaces: ['Public Portal'],
      sampleCredentials: {
        username: 'N/A',
        password: 'N/A'
      }
    }
  ];

  const selectedRoleData = userRoles.find(role => role.id === selectedRole);

  const generateTestToken = async () => {
    if (!selectedRoleData) return;

    setIsGenerating(true);
    try {
      // Simulate token generation (in real implementation, this would call the API)
      const mockToken = btoa(JSON.stringify({
        sub: selectedRoleData.sampleCredentials.username,
        role: selectedRoleData.role,
        permissions: selectedRoleData.permissions,
        exp: Math.floor(Date.now() / 1000) + (60 * 60), // 1 hour expiry
        iat: Math.floor(Date.now() / 1000),
        iss: 'tta-dev-interface'
      }));

      // Add some delay to simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      setGeneratedToken(`dev.${mockToken}.signature`);
      toast.success(`Generated ${selectedRoleData.name} token`);
    } catch (error) {
      toast.error('Failed to generate token');
    } finally {
      setIsGenerating(false);
    }
  };

  const applyRoleToInterface = (interfaceName: string) => {
    // In a real implementation, this would set the authentication context
    // for the specified interface
    toast.success(`Applied ${selectedRoleData?.name} role to ${interfaceName}`);
  };

  return (
    <div className="space-y-6">
      {/* Role Selection */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Select User Role</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {userRoles.map((role) => {
            const Icon = role.icon;
            return (
              <motion.div
                key={role.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedRole(role.id)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedRole === role.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-3 mb-3">
                  <div className={`p-2 rounded-lg ${role.color}`}>
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{role.name}</h4>
                    <p className="text-sm text-gray-600">{role.role}</p>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-3">{role.description}</p>
                <div className="flex flex-wrap gap-1">
                  {role.interfaces.map((interface_) => (
                    <span
                      key={interface_}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                    >
                      {interface_}
                    </span>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Selected Role Details */}
      {selectedRoleData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg border border-gray-200 p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className={`p-3 rounded-lg ${selectedRoleData.color}`}>
              <selectedRoleData.icon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedRoleData.name}
              </h3>
              <p className="text-gray-600">{selectedRoleData.description}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Permissions */}
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Permissions</h4>
              <div className="space-y-1">
                {selectedRoleData.permissions.map((permission) => (
                  <div key={permission} className="flex items-center space-x-2">
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                    <span className="text-sm text-gray-700">{permission}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Sample Credentials */}
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Sample Credentials</h4>
              <div className="bg-gray-50 rounded-lg p-3 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Username:</span>
                  <div className="flex items-center space-x-2">
                    <code className="text-sm font-mono bg-white px-2 py-1 rounded">
                      {selectedRoleData.sampleCredentials.username}
                    </code>
                    <CopyToClipboard
                      text={selectedRoleData.sampleCredentials.username}
                      onCopy={() => toast.success('Username copied!')}
                    >
                      <button className="text-gray-400 hover:text-gray-600">
                        <ClipboardDocumentIcon className="h-4 w-4" />
                      </button>
                    </CopyToClipboard>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Password:</span>
                  <div className="flex items-center space-x-2">
                    <code className="text-sm font-mono bg-white px-2 py-1 rounded">
                      {selectedRoleData.sampleCredentials.password}
                    </code>
                    <CopyToClipboard
                      text={selectedRoleData.sampleCredentials.password}
                      onCopy={() => toast.success('Password copied!')}
                    >
                      <button className="text-gray-400 hover:text-gray-600">
                        <ClipboardDocumentIcon className="h-4 w-4" />
                      </button>
                    </CopyToClipboard>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={generateTestToken}
              disabled={isGenerating}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? 'Generating...' : 'Generate Test Token'}
            </button>

            {selectedRoleData.interfaces.map((interface_) => (
              <button
                key={interface_}
                onClick={() => applyRoleToInterface(interface_)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Apply to {interface_}
              </button>
            ))}
          </div>

          {/* Generated Token */}
          {generatedToken && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium text-gray-900">Generated Token</h4>
                <CopyToClipboard
                  text={generatedToken}
                  onCopy={() => toast.success('Token copied!')}
                >
                  <button className="text-blue-600 hover:text-blue-700 text-sm">
                    Copy Token
                  </button>
                </CopyToClipboard>
              </div>
              <code className="text-xs font-mono text-gray-700 break-all">
                {generatedToken}
              </code>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};
