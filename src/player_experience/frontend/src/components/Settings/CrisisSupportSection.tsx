import React, { useState } from 'react';

interface CrisisContactInfo {
  emergency_contact: string;
  therapist_contact?: string;
  preferred_crisis_resources: string[];
}

interface CrisisSupportSectionProps {
  crisisContactInfo?: CrisisContactInfo;
  onUpdate: (crisisInfo: CrisisContactInfo) => void;
}

const CrisisSupportSection: React.FC<CrisisSupportSectionProps> = ({
  crisisContactInfo,
  onUpdate,
}) => {
  const [showResourcesModal, setShowResourcesModal] = useState(false);
  const [selectedResource, setSelectedResource] = useState<string | null>(null);

  const defaultCrisisResources = [
    {
      id: 'national-suicide-prevention',
      name: 'National Suicide Prevention Lifeline',
      contact: '988',
      description: '24/7 free and confidential support for people in distress',
      type: 'phone',
      availability: '24/7',
      website: 'https://suicidepreventionlifeline.org',
    },
    {
      id: 'crisis-text-line',
      name: 'Crisis Text Line',
      contact: 'Text HOME to 741741',
      description: 'Free, 24/7 crisis support via text message',
      type: 'text',
      availability: '24/7',
      website: 'https://crisistextline.org',
    },
    {
      id: 'samhsa-helpline',
      name: 'SAMHSA National Helpline',
      contact: '1-800-662-4357',
      description: 'Treatment referral and information service',
      type: 'phone',
      availability: '24/7',
      website: 'https://samhsa.gov',
    },
    {
      id: 'nami-helpline',
      name: 'NAMI HelpLine',
      contact: '1-800-950-6264',
      description: 'Information, referrals and support for mental health',
      type: 'phone',
      availability: 'Mon-Fri 10am-10pm ET',
      website: 'https://nami.org',
    },
    {
      id: 'trevor-project',
      name: 'The Trevor Project',
      contact: '1-866-488-7386',
      description: 'Crisis support for LGBTQ+ youth',
      type: 'phone',
      availability: '24/7',
      website: 'https://thetrevorproject.org',
    },
  ];

  const handleContactInfoUpdate = (field: keyof CrisisContactInfo, value: string | string[]) => {
    const updatedInfo = {
      emergency_contact: crisisContactInfo?.emergency_contact || '',
      therapist_contact: crisisContactInfo?.therapist_contact || '',
      preferred_crisis_resources: crisisContactInfo?.preferred_crisis_resources || [],
      ...crisisContactInfo,
      [field]: value,
    };
    onUpdate(updatedInfo);
  };

  const handleResourceToggle = (resourceId: string) => {
    const currentResources = crisisContactInfo?.preferred_crisis_resources || [];
    const updatedResources = currentResources.includes(resourceId)
      ? currentResources.filter(id => id !== resourceId)
      : [...currentResources, resourceId];
    
    handleContactInfoUpdate('preferred_crisis_resources', updatedResources);
  };

  const handleEmergencyAccess = (resourceId: string) => {
    const resource = defaultCrisisResources.find(r => r.id === resourceId);
    if (resource) {
      if (resource.type === 'phone') {
        window.open(`tel:${resource.contact.replace(/[^\d]/g, '')}`);
      } else if (resource.type === 'text') {
        // For text resources, show instructions
        setSelectedResource(resourceId);
        setShowResourcesModal(true);
      } else if (resource.website) {
        window.open(resource.website, '_blank');
      }
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Crisis Support Resources</h3>
        <p className="text-gray-600 mb-6">
          Set up your crisis support preferences and access immediate help when needed. 
          Your safety and well-being are our highest priority.
        </p>
      </div>

      {/* Emergency Alert */}
      <div className="bg-red-50 border-l-4 border-red-400 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              If you're in immediate danger or having thoughts of self-harm
            </h3>
            <div className="mt-2 text-sm text-red-700">
              <p>Call 911 (US) or your local emergency services immediately.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Access Crisis Resources */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Immediate Crisis Support</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {defaultCrisisResources.slice(0, 4).map((resource) => (
            <div key={resource.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h5 className="font-medium text-gray-900">{resource.name}</h5>
                  <p className="text-sm text-gray-600 mt-1">{resource.description}</p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  resource.availability === '24/7' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {resource.availability}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">{resource.contact}</span>
                <button
                  onClick={() => handleEmergencyAccess(resource.id)}
                  className="bg-red-600 hover:bg-red-700 text-white text-sm font-medium py-1 px-3 rounded transition-colors"
                >
                  Contact Now
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Personal Crisis Contacts */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Personal Crisis Contacts</h4>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Emergency Contact
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="Name and phone number of trusted person"
              value={crisisContactInfo?.emergency_contact || ''}
              onChange={(e) => handleContactInfoUpdate('emergency_contact', e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              This person may be contacted in case of a mental health emergency
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Therapist/Counselor Contact (Optional)
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="Your therapist's name and contact information"
              value={crisisContactInfo?.therapist_contact || ''}
              onChange={(e) => handleContactInfoUpdate('therapist_contact', e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              Your current mental health professional, if applicable
            </p>
          </div>
        </div>
      </div>

      {/* Preferred Crisis Resources */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Preferred Crisis Resources</h4>
        <p className="text-sm text-gray-600 mb-4">
          Select the crisis resources you'd prefer to have quick access to. These will be prioritized in emergency situations.
        </p>
        
        <div className="space-y-3">
          {defaultCrisisResources.map((resource) => (
            <label key={resource.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                className="mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                checked={crisisContactInfo?.preferred_crisis_resources?.includes(resource.id) || false}
                onChange={() => handleResourceToggle(resource.id)}
              />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">{resource.name}</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    resource.availability === '24/7' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-blue-100 text-blue-800'
                  }`}>
                    {resource.availability}
                  </span>
                </div>
                <p className="text-xs text-gray-600 mt-1">{resource.description}</p>
                <p className="text-xs text-gray-500 mt-1">{resource.contact}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Crisis Plan */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h4 className="font-medium text-blue-900 mb-4">🛡️ Your Crisis Safety Plan</h4>
        <div className="space-y-3 text-sm text-blue-800">
          <div className="flex items-start space-x-2">
            <span className="font-medium">1.</span>
            <span>Recognize your warning signs and triggers</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="font-medium">2.</span>
            <span>Use internal coping strategies (breathing, grounding techniques)</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="font-medium">3.</span>
            <span>Contact people and social settings that provide distraction</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="font-medium">4.</span>
            <span>Contact family members or friends who may help resolve the crisis</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="font-medium">5.</span>
            <span>Contact mental health professionals or agencies</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="font-medium">6.</span>
            <span>Reduce access to lethal means</span>
          </div>
        </div>
      </div>

      {/* Crisis Detection Settings */}
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Crisis Detection & Response</h4>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="font-medium text-gray-900">Automatic Crisis Detection</p>
              <p className="text-sm text-gray-600 mt-1">
                Allow the system to monitor for signs of distress in your interactions and proactively offer support resources.
              </p>
              <div className="mt-2 text-xs text-gray-500">
                • Analyzes language patterns for distress indicators
                • Provides immediate access to crisis resources
                • Maintains complete confidentiality
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                className="sr-only peer"
                defaultChecked={true}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Resources Modal */}
      {showResourcesModal && selectedResource && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              {(() => {
                const resource = defaultCrisisResources.find(r => r.id === selectedResource);
                return resource ? (
                  <>
                    <div className="flex items-center mb-4">
                      <svg className="w-6 h-6 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <h3 className="text-lg font-semibold text-gray-900">{resource.name}</h3>
                    </div>
                    <p className="text-gray-600 mb-4">{resource.description}</p>
                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <p className="font-medium text-gray-900 mb-2">How to contact:</p>
                      <p className="text-gray-700">{resource.contact}</p>
                      <p className="text-sm text-gray-600 mt-2">Available: {resource.availability}</p>
                    </div>
                    <div className="flex space-x-3">
                      {resource.website && (
                        <button
                          onClick={() => window.open(resource.website, '_blank')}
                          className="btn-primary flex-1"
                        >
                          Visit Website
                        </button>
                      )}
                      <button
                        onClick={() => setShowResourcesModal(false)}
                        className="btn-secondary flex-1"
                      >
                        Close
                      </button>
                    </div>
                  </>
                ) : null;
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CrisisSupportSection;