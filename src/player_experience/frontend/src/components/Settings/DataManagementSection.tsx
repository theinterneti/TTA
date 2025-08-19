import React, { useState } from 'react';

interface DataManagementSectionProps {
  onExportData: () => void;
  onDeleteAccount: () => void;
}

const DataManagementSection: React.FC<DataManagementSectionProps> = ({
  onExportData,
  onDeleteAccount,
}) => {
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
  const [deleteConfirmationText, setDeleteConfirmationText] = useState('');
  const [exportInProgress, setExportInProgress] = useState(false);

  const handleExportData = async () => {
    setExportInProgress(true);
    try {
      await onExportData();
    } finally {
      setExportInProgress(false);
    }
  };

  const handleDeleteAccount = () => {
    if (deleteConfirmationText === 'DELETE MY ACCOUNT') {
      onDeleteAccount();
      setShowDeleteConfirmation(false);
    }
  };

  const dataTypes = [
    {
      type: 'Therapeutic Progress',
      description: 'Your therapeutic milestones, insights, and progress tracking data',
      icon: '📈',
    },
    {
      type: 'Character Data',
      description: 'All created characters, their profiles, and therapeutic preferences',
      icon: '👤',
    },
    {
      type: 'Session History',
      description: 'Chat logs, interactions, and session summaries from your therapeutic journeys',
      icon: '💬',
    },
    {
      type: 'World Interactions',
      description: 'Your choices, progress, and customizations in therapeutic worlds',
      icon: '🌍',
    },
    {
      type: 'Settings & Preferences',
      description: 'Your therapeutic preferences, privacy settings, and customizations',
      icon: '⚙️',
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Management</h3>
        <p className="text-gray-600 mb-6">
          Manage your therapeutic data, export your information, or permanently delete your account.
        </p>
      </div>

      {/* Data Overview */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Your Data Overview</h4>
        <p className="text-sm text-gray-600 mb-4">
          Here's what data we store about your therapeutic journey:
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {dataTypes.map((item, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <span className="text-2xl">{item.icon}</span>
                <div>
                  <h5 className="font-medium text-gray-900">{item.type}</h5>
                  <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Data Export */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Export Your Data</h4>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h5 className="font-medium text-gray-900 mb-2">Complete Data Export</h5>
              <p className="text-sm text-gray-600 mb-4">
                Download a comprehensive archive of all your therapeutic data in a human-readable format. 
                This includes your progress, characters, session history, and all personal information.
              </p>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                <h6 className="font-medium text-blue-900 mb-2">Export includes:</h6>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Therapeutic progress reports and insights</li>
                  <li>• Character profiles and therapeutic preferences</li>
                  <li>• Complete session transcripts and interactions</li>
                  <li>• World progress and customization data</li>
                  <li>• Account settings and privacy preferences</li>
                  <li>• Timestamps and metadata for all activities</li>
                </ul>
              </div>

              <div className="text-xs text-gray-500 space-y-1">
                <p>• Export format: ZIP archive containing JSON and PDF files</p>
                <p>• Processing time: Usually 5-10 minutes for complete export</p>
                <p>• Download link will be sent to your registered email</p>
                <p>• Export link expires after 7 days for security</p>
              </div>
            </div>
          </div>

          <button
            onClick={handleExportData}
            disabled={exportInProgress}
            className={`btn-primary w-full ${exportInProgress ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {exportInProgress ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Preparing Export...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export All Data
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Data Portability */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Data Portability</h4>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <svg className="w-5 h-5 text-green-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h5 className="font-medium text-green-900">Your Right to Data Portability</h5>
              <p className="text-sm text-green-800 mt-1">
                You have the right to receive your personal data in a structured, commonly used, and machine-readable format. 
                You can also request to have this data transmitted directly to another service provider where technically feasible.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Account Deletion */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Account Deletion</h4>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start space-x-3 mb-4">
            <svg className="w-6 h-6 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div className="flex-1">
              <h5 className="font-medium text-red-900">Permanent Account Deletion</h5>
              <p className="text-sm text-red-800 mt-1">
                Permanently delete your account and all associated data. This action cannot be undone.
              </p>
            </div>
          </div>

          <div className="bg-white border border-red-200 rounded-lg p-4 mb-4">
            <h6 className="font-medium text-red-900 mb-2">What will be deleted:</h6>
            <ul className="text-sm text-red-800 space-y-1">
              <li>• All therapeutic progress and session data</li>
              <li>• Character profiles and customizations</li>
              <li>• Account settings and preferences</li>
              <li>• Chat history and interactions</li>
              <li>• Personal information and contact details</li>
            </ul>
          </div>

          <div className="bg-white border border-red-200 rounded-lg p-4 mb-4">
            <h6 className="font-medium text-red-900 mb-2">What will be retained (anonymized):</h6>
            <ul className="text-sm text-red-800 space-y-1">
              <li>• Aggregated usage statistics (no personal identifiers)</li>
              <li>• Research data contributions (if previously consented)</li>
              <li>• System logs for security purposes (personal data removed)</li>
            </ul>
          </div>

          <button
            onClick={() => setShowDeleteConfirmation(true)}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 w-full"
          >
            Delete My Account
          </button>
        </div>
      </div>

      {/* GDPR Rights */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Your Privacy Rights</h4>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p className="text-sm text-gray-700 mb-3">
            Under data protection regulations (GDPR, CCPA), you have the following rights:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
            <div>
              <h6 className="font-medium text-gray-900">Right to Access</h6>
              <p>Request copies of your personal data</p>
            </div>
            <div>
              <h6 className="font-medium text-gray-900">Right to Rectification</h6>
              <p>Request correction of inaccurate data</p>
            </div>
            <div>
              <h6 className="font-medium text-gray-900">Right to Erasure</h6>
              <p>Request deletion of your personal data</p>
            </div>
            <div>
              <h6 className="font-medium text-gray-900">Right to Portability</h6>
              <p>Receive your data in a portable format</p>
            </div>
            <div>
              <h6 className="font-medium text-gray-900">Right to Restrict Processing</h6>
              <p>Limit how we process your data</p>
            </div>
            <div>
              <h6 className="font-medium text-gray-900">Right to Object</h6>
              <p>Object to certain types of processing</p>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <svg className="w-6 h-6 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <h3 className="text-lg font-semibold text-gray-900">Confirm Account Deletion</h3>
              </div>
              
              <div className="mb-6">
                <p className="text-gray-600 mb-4">
                  This action will permanently delete your account and all associated data. This cannot be undone.
                </p>
                
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                  <p className="text-red-800 text-sm font-medium mb-2">Before you proceed:</p>
                  <ul className="text-red-700 text-sm space-y-1">
                    <li>• Consider exporting your data first</li>
                    <li>• This will end all active therapeutic sessions</li>
                    <li>• You will lose access to all progress and insights</li>
                    <li>• This action cannot be reversed</li>
                  </ul>
                </div>

                <p className="text-sm text-gray-600 mb-3">
                  To confirm deletion, please type <strong>"DELETE MY ACCOUNT"</strong> in the box below:
                </p>
                
                <input
                  type="text"
                  value={deleteConfirmationText}
                  onChange={(e) => setDeleteConfirmationText(e.target.value)}
                  className="input-field w-full"
                  placeholder="Type: DELETE MY ACCOUNT"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={handleDeleteAccount}
                  disabled={deleteConfirmationText !== 'DELETE MY ACCOUNT'}
                  className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors duration-200 ${
                    deleteConfirmationText === 'DELETE MY ACCOUNT'
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  Delete Account
                </button>
                <button
                  onClick={() => {
                    setShowDeleteConfirmation(false);
                    setDeleteConfirmationText('');
                  }}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataManagementSection;