import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "../../store/store";
import {
  fetchSettings,
  updateTherapeuticLocal,
  updatePrivacyLocal,
  updateNotificationsLocal,
  updateAccessibilityLocal,
  updateTherapeuticSettings,
  updatePrivacySettings,
  exportPlayerData,
  // deletePlayerData, // TODO: Implement data deletion functionality
  markChangesSaved,
} from "../../store/slices/settingsSlice";
import TherapeuticSettingsSection from "../../components/Settings/TherapeuticSettingsSection";
import PrivacySettingsSection from "../../components/Settings/PrivacySettingsSection";
import CrisisSupportSection from "../../components/Settings/CrisisSupportSection";
// import DataManagementSection from "../../components/Settings/DataManagementSection"; // TODO: Implement data management section

const Settings: React.FC = () => {
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const {
    therapeutic,
    privacy,
    notifications,
    accessibility,
    isLoading,
    hasUnsavedChanges,
    error,
  } = useSelector((state: RootState) => state.settings);

  const [activeTab, setActiveTab] = useState("therapeutic");
  const [showUnsavedWarning, setShowUnsavedWarning] = useState(false);

  useEffect(() => {
    if (profile?.player_id) {
      dispatch(fetchSettings(profile.player_id) as any);
    }
  }, [dispatch, profile?.player_id]);

  const handleSaveSettings = async () => {
    if (!profile?.player_id) return;

    try {
      await dispatch(
        updateTherapeuticSettings({
          playerId: profile.player_id,
          settings: therapeutic,
        }) as any
      );

      await dispatch(
        updatePrivacySettings({
          playerId: profile.player_id,
          settings: privacy,
        }) as any
      );

      dispatch(markChangesSaved());
      setShowUnsavedWarning(false);
    } catch (error) {
      console.error("Failed to save settings:", error);
    }
  };

  const handleTabChange = (tab: string) => {
    if (hasUnsavedChanges) {
      setShowUnsavedWarning(true);
      return;
    }
    setActiveTab(tab);
  };

  const tabs = [
    { id: "therapeutic", label: "Therapeutic", icon: "🧠" },
    { id: "privacy", label: "Privacy & Data", icon: "🔒" },
    { id: "notifications", label: "Notifications", icon: "🔔" },
    { id: "accessibility", label: "Accessibility", icon: "♿" },
    { id: "crisis", label: "Crisis Support", icon: "🆘" },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="ml-2 text-gray-600">Loading settings...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">
            Manage your therapeutic preferences, privacy settings, and account
            options
          </p>
        </div>
        {hasUnsavedChanges && (
          <div className="flex items-center space-x-3">
            <span className="text-sm text-amber-600 flex items-center">
              <svg
                className="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
              Unsaved changes
            </span>
            <button
              onClick={handleSaveSettings}
              className="btn-primary text-sm py-1 px-3"
            >
              Save Changes
            </button>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg
              className="w-5 h-5 text-red-600 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Settings tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === tab.id
                    ? "border-primary-500 text-primary-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === "therapeutic" && (
            <TherapeuticSettingsSection
              settings={therapeutic}
              onUpdate={(updates) => dispatch(updateTherapeuticLocal(updates))}
            />
          )}

          {activeTab === "privacy" && (
            <PrivacySettingsSection
              settings={privacy}
              onUpdate={(updates) => dispatch(updatePrivacyLocal(updates))}
              onExportData={() =>
                profile?.player_id &&
                dispatch(exportPlayerData(profile.player_id) as any)
              }
            />
          )}

          {activeTab === "notifications" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Notification Preferences
                </h3>
                <p className="text-gray-600 mb-6">
                  Choose how and when you'd like to receive notifications about
                  your therapeutic journey.
                </p>
              </div>

              <div className="space-y-4">
                {[
                  {
                    key: "session_reminders",
                    label: "Session Reminders",
                    desc: "Get notified about scheduled therapeutic sessions",
                  },
                  {
                    key: "progress_updates",
                    label: "Progress Updates",
                    desc: "Receive updates about your therapeutic progress and milestones",
                  },
                  {
                    key: "milestone_celebrations",
                    label: "Milestone Celebrations",
                    desc: "Celebrate achievements and therapeutic breakthroughs",
                  },
                  {
                    key: "crisis_alerts",
                    label: "Crisis Support Alerts",
                    desc: "Important safety and crisis support notifications (recommended)",
                  },
                  {
                    key: "email_notifications",
                    label: "Email Notifications",
                    desc: "Receive notifications via email",
                  },
                  {
                    key: "push_notifications",
                    label: "Push Notifications",
                    desc: "Receive browser push notifications",
                  },
                ].map((setting) => (
                  <div
                    key={setting.key}
                    className="flex items-center justify-between py-3"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">
                        {setting.label}
                      </p>
                      <p className="text-sm text-gray-600">{setting.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer ml-4">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={
                          notifications[
                            setting.key as keyof typeof notifications
                          ]
                        }
                        onChange={(e) =>
                          dispatch(
                            updateNotificationsLocal({
                              [setting.key]: e.target.checked,
                            })
                          )
                        }
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "accessibility" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Accessibility Options
                </h3>
                <p className="text-gray-600 mb-6">
                  Customize the interface to better suit your accessibility
                  needs.
                </p>
              </div>

              <div className="space-y-4">
                {[
                  {
                    key: "high_contrast",
                    label: "High Contrast Mode",
                    desc: "Increase contrast for better visibility",
                  },
                  {
                    key: "large_text",
                    label: "Large Text",
                    desc: "Increase text size throughout the interface",
                  },
                  {
                    key: "screen_reader_optimized",
                    label: "Screen Reader Optimization",
                    desc: "Optimize interface for screen readers",
                  },
                  {
                    key: "reduced_motion",
                    label: "Reduced Motion",
                    desc: "Minimize animations and transitions",
                  },
                  {
                    key: "keyboard_navigation",
                    label: "Enhanced Keyboard Navigation",
                    desc: "Improve keyboard navigation support",
                  },
                ].map((setting) => (
                  <div
                    key={setting.key}
                    className="flex items-center justify-between py-3"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">
                        {setting.label}
                      </p>
                      <p className="text-sm text-gray-600">{setting.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer ml-4">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={
                          accessibility[
                            setting.key as keyof typeof accessibility
                          ]
                        }
                        onChange={(e) =>
                          dispatch(
                            updateAccessibilityLocal({
                              [setting.key]: e.target.checked,
                            })
                          )
                        }
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "crisis" && (
            <CrisisSupportSection
              crisisContactInfo={therapeutic.crisis_contact_info}
              onUpdate={(crisisInfo) =>
                dispatch(
                  updateTherapeuticLocal({ crisis_contact_info: crisisInfo })
                )
              }
            />
          )}
        </div>
      </div>

      {/* Unsaved Changes Warning Modal */}
      {showUnsavedWarning && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <svg
                  className="w-6 h-6 text-amber-600 mr-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                  />
                </svg>
                <h3 className="text-lg font-semibold text-gray-900">
                  Unsaved Changes
                </h3>
              </div>
              <p className="text-gray-600 mb-6">
                You have unsaved changes. What would you like to do?
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    handleSaveSettings();
                    setShowUnsavedWarning(false);
                  }}
                  className="btn-primary flex-1"
                >
                  Save Changes
                </button>
                <button
                  onClick={() => {
                    setShowUnsavedWarning(false);
                    // Reset changes and switch tab
                    dispatch(fetchSettings(profile!.player_id) as any);
                  }}
                  className="btn-secondary flex-1"
                >
                  Discard Changes
                </button>
                <button
                  onClick={() => setShowUnsavedWarning(false)}
                  className="text-gray-600 hover:text-gray-800 px-4 py-2"
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

export default Settings;
