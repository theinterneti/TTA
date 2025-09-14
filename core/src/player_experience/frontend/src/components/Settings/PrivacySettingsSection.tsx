import React, { useState } from 'react';

interface PrivacySettings {
  data_sharing_consent: boolean;
  research_participation: boolean;
  contact_preferences: string[];
  data_retention_period: number;
  anonymize_data: boolean;
}

interface PrivacySettingsSectionProps {
  settings: PrivacySettings;
  onUpdate: (updates: Partial<PrivacySettings>) => void;
  onExportData: () => void;
}

const PrivacySettingsSection: React.FC<PrivacySettingsSectionProps> = ({
  settings,
  onUpdate,
  onExportData,
}) => {
  const [showDataPolicy, setShowDataPolicy] = useState(false);
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);

  const contactPreferenceOptions = [
    { value: 'email', label: 'Email', description: 'Receive communications via email' },
    { value: 'in_app', label: 'In-App Notifications', description: 'Receive notifications within the application' },
    { value: 'sms', label: 'SMS/Text', description: 'Receive text messages (for urgent matters only)' },
    { value: 'none', label: 'No Contact', description: 'Minimal contact except for critical safety issues' },
  ];

  const handleContactPreferenceToggle = (preference: string) => {
    const updatedPreferences = settings.contact_preferences.includes(preference)
      ? settings.contact_preferences.filter(p => p !== preference)
      : [...settings.contact_preferences, preference];

    onUpdate({ contact_preferences: updatedPreferences });
  };

  const handleDataRetentionChange = (days: number) => {
    onUpdate({ data_retention_period: Math.max(30, Math.min(3650, days)) });
  };

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Privacy & Data Management</h3>
        <p className="text-gray-600 mb-6">
          Control how your data is collected, stored, and used. Your privacy and security are our top priorities.
        </p>
      </div>

      {/* Data Usage Policies */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-900">Data Usage Policies</h4>
            <p className="text-sm text-gray-600">Review how your data is collected and used</p>
          </div>
          <button
            onClick={() => setShowDataPolicy(!showDataPolicy)}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            {showDataPolicy ? 'Hide' : 'View'} Policy
          </button>
        </div>

        {showDataPolicy && (
          <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-700 space-y-3">
            <div>
              <h5 className="font-medium">Data Collection</h5>
              <p>We collect therapeutic interaction data, progress metrics, and user preferences to provide personalized therapeutic experiences.</p>
            </div>
            <div>
              <h5 className="font-medium">Data Storage</h5>
              <p>All data is encrypted and stored securely. Personal identifiers are separated from therapeutic content.</p>
            </div>
            <div>
              <h5 className="font-medium">Data Usage</h5>
              <p>Data is used solely for providing therapeutic services and improving the platform. No data is sold to third parties.</p>
            </div>
          </div>
        )}
      </div>

      {/* Data Sharing Consent */}
      <div className="space-y-4">
        <h4 className="font-medium text-gray-900">Data Sharing & Research</h4>

        <div className="flex items-start justify-between p-4 bg-white border border-gray-200 rounded-lg">
          <div className="flex-1">
            <p className="font-medium text-gray-900">Research Participation</p>
            <p className="text-sm text-gray-600 mt-1">
              Allow your anonymized data to contribute to therapeutic research and platform improvements.
              This helps us develop better therapeutic interventions for everyone.
            </p>
            <div className="mt-2 text-xs text-gray-500">
              • All personal identifiers are removed
              • Data is aggregated with other users
              • You can opt out at any time
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer ml-4">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={settings.research_participation}
              onChange={(e) => onUpdate({ research_participation: e.target.checked })}
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
          </label>
        </div>

        <div className="flex items-start justify-between p-4 bg-white border border-gray-200 rounded-lg">
          <div className="flex-1">
            <p className="font-medium text-gray-900">Data Sharing Consent</p>
            <p className="text-sm text-gray-600 mt-1">
              Allow sharing of anonymized therapeutic insights with qualified researchers and institutions
              for advancing mental health treatment methods.
            </p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer ml-4">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={settings.data_sharing_consent}
              onChange={(e) => onUpdate({ data_sharing_consent: e.target.checked })}
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
          </label>
        </div>
      </div>

      {/* Data Anonymization */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Data Protection</h4>

        <div className="flex items-start justify-between p-4 bg-white border border-gray-200 rounded-lg">
          <div className="flex-1">
            <p className="font-medium text-gray-900">Automatic Data Anonymization</p>
            <p className="text-sm text-gray-600 mt-1">
              Automatically remove or encrypt personal identifiers from stored therapeutic data.
              This provides an extra layer of privacy protection.
            </p>
            <div className="mt-2 text-xs text-green-600">
              ✓ Recommended for enhanced privacy
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer ml-4">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={settings.anonymize_data}
              onChange={(e) => onUpdate({ anonymize_data: e.target.checked })}
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
          </label>
        </div>
      </div>

      {/* Contact Preferences */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Contact Preferences</h4>
        <p className="text-sm text-gray-600 mb-4">
          Choose how you'd like to be contacted for important updates, safety notifications, and platform communications.
        </p>

        <div className="space-y-3">
          {contactPreferenceOptions.map((option) => (
            <label key={option.value} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                className="mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                checked={settings.contact_preferences.includes(option.value)}
                onChange={() => handleContactPreferenceToggle(option.value)}
              />
              <div className="flex-1">
                <span className="text-sm font-medium text-gray-900">{option.label}</span>
                <p className="text-xs text-gray-600">{option.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Data Retention */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Data Retention</h4>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Data Retention Period (days)
          </label>
          <div className="flex items-center space-x-4">
            <input
              type="range"
              min="30"
              max="3650"
              step="30"
              value={settings.data_retention_period}
              onChange={(e) => handleDataRetentionChange(parseInt(e.target.value))}
              className="flex-1"
            />
            <div className="text-sm font-medium text-gray-900 min-w-[80px]">
              {settings.data_retention_period} days
            </div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>30 days (minimum)</span>
            <span>10 years (maximum)</span>
          </div>
          <p className="text-sm text-gray-600 mt-3">
            Your therapeutic data will be automatically deleted after this period.
            You can export your data before deletion if needed.
          </p>
        </div>
      </div>

      {/* Data Management Actions */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Data Management</h4>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">Export Your Data</p>
              <p className="text-sm text-gray-600">
                Download a complete copy of your therapeutic data, progress, and account information in a readable format.
              </p>
            </div>
            <button
              onClick={onExportData}
              className="btn-secondary whitespace-nowrap"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export Data
            </button>
          </div>

          <div className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
            <div>
              <p className="font-medium text-red-900">Delete All Data</p>
              <p className="text-sm text-red-600">
                Permanently delete your account and all associated therapeutic data. This action cannot be undone.
              </p>
            </div>
            <button
              onClick={() => setShowDeleteConfirmation(true)}
              className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 whitespace-nowrap"
            >
              Delete Account
            </button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <svg className="w-6 h-6 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <h3 className="text-lg font-semibold text-gray-900">Delete Account</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Are you sure you want to permanently delete your account? This will:
              </p>
              <ul className="text-sm text-gray-600 mb-6 space-y-1">
                <li>• Delete all your therapeutic progress and data</li>
                <li>• Remove all characters and worlds</li>
                <li>• Cancel any active sessions</li>
                <li>• This action cannot be undone</li>
              </ul>
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    // Handle account deletion
                    console.log('Account deletion requested');
                    setShowDeleteConfirmation(false);
                  }}
                  className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex-1"
                >
                  Yes, Delete Account
                </button>
                <button
                  onClick={() => setShowDeleteConfirmation(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Privacy Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">🔒 Privacy Commitment</h4>
        <p className="text-blue-800 text-sm">
          We are committed to protecting your privacy and maintaining the confidentiality of your therapeutic data.
          All data is encrypted, access is strictly controlled, and we never sell personal information to third parties.
        </p>
      </div>
    </div>
  );
};

export default PrivacySettingsSection;
