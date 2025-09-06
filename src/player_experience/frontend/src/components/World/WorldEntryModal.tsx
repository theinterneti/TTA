import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { nexusAPI } from "../../services/api";
import { useWorldData } from "../../hooks/useWorldData";
import { useAuthGuard } from "../../hooks/useAuthGuard";

export interface WorldEntryData {
  character_id?: string;
  entry_preferences?: {
    difficulty_adjustment?: "easier" | "normal" | "harder";
    therapeutic_focus?: string[];
    session_duration?: number;
    privacy_mode?: boolean;
  };
  custom_parameters?: Record<string, any>;
}

export interface WorldEntryResponse {
  session_id: string;
  world_id: string;
  character_id?: string;
  entry_point: string;
  session_config: {
    difficulty_level: string;
    therapeutic_focus: string[];
    estimated_duration: number;
    privacy_mode: boolean;
  };
  initial_state: {
    location: string;
    narrative_context: string;
    available_actions: string[];
  };
  status: "ready" | "pending" | "error";
  message?: string;
}

interface WorldEntryModalProps {
  worldId: string;
  isOpen: boolean;
  onClose: () => void;
  onEntrySuccess: (response: WorldEntryResponse) => void;
  onEntryError?: (error: Error) => void;
}

const WorldEntryModal: React.FC<WorldEntryModalProps> = ({
  worldId,
  isOpen,
  onClose,
  onEntrySuccess,
  onEntryError,
}) => {
  const { isAuthenticated, user } = useAuthGuard({ autoRedirect: false });
  const {
    world,
    loading: worldLoading,
    error: worldError,
  } = useWorldData(worldId);

  const [entryData, setEntryData] = useState<WorldEntryData>({
    entry_preferences: {
      difficulty_adjustment: "normal",
      therapeutic_focus: [],
      session_duration: 30,
      privacy_mode: false,
    },
  });

  const [entering, setEntering] = useState(false);
  const [entryError, setEntryError] = useState<string | null>(null);
  const [step, setStep] = useState<
    "preferences" | "character" | "confirmation"
  >("preferences");

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setStep("preferences");
      setEntryError(null);
      setEntering(false);
    }
  }, [isOpen]);

  const handlePreferenceChange = (key: string, value: any) => {
    setEntryData((prev) => ({
      ...prev,
      entry_preferences: {
        ...prev.entry_preferences,
        [key]: value,
      },
    }));
  };

  const handleTherapeuticFocusToggle = (focus: string) => {
    const current = entryData.entry_preferences?.therapeutic_focus || [];
    const updated = current.includes(focus)
      ? current.filter((f) => f !== focus)
      : [...current, focus];

    handlePreferenceChange("therapeutic_focus", updated);
  };

  const handleEnterWorld = async () => {
    if (!isAuthenticated) {
      setEntryError("You must be logged in to enter a world");
      return;
    }

    try {
      setEntering(true);
      setEntryError(null);

      const response = await nexusAPI.enterWorld(worldId, {
        ...entryData,
        user_id: user?.id,
      });

      // Handle successful entry
      onEntrySuccess(response as any);
      onClose();
    } catch (error: any) {
      console.error("Failed to enter world:", error);
      const errorMessage =
        error.message || "Failed to enter world. Please try again.";
      setEntryError(errorMessage);
      onEntryError?.(error);
    } finally {
      setEntering(false);
    }
  };

  const renderPreferencesStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Session Preferences
        </h3>

        {/* Difficulty Adjustment */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Difficulty Adjustment
          </label>
          <div className="grid grid-cols-3 gap-3">
            {[
              {
                value: "easier",
                label: "Easier",
                desc: "More guidance and support",
              },
              { value: "normal", label: "Normal", desc: "Standard experience" },
              {
                value: "harder",
                label: "Harder",
                desc: "More challenging scenarios",
              },
            ].map((option) => (
              <button
                key={option.value}
                onClick={() =>
                  handlePreferenceChange("difficulty_adjustment", option.value)
                }
                className={`p-3 rounded-lg border text-left transition-colors ${
                  entryData.entry_preferences?.difficulty_adjustment ===
                  option.value
                    ? "border-blue-500 bg-blue-50 text-blue-900"
                    : "border-gray-300 hover:border-gray-400"
                }`}
              >
                <div className="font-medium">{option.label}</div>
                <div className="text-xs text-gray-600 mt-1">{option.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Session Duration */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Preferred Session Duration:{" "}
            {entryData.entry_preferences?.session_duration || 30} minutes
          </label>
          <input
            type="range"
            min="15"
            max="120"
            step="15"
            value={entryData.entry_preferences?.session_duration || 30}
            onChange={(e) =>
              handlePreferenceChange(
                "session_duration",
                parseInt(e.target.value)
              )
            }
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>15 min</span>
            <span>60 min</span>
            <span>120 min</span>
          </div>
        </div>

        {/* Therapeutic Focus */}
        {world?.therapeutic_focus && world.therapeutic_focus.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Focus Areas for This Session
            </label>
            <div className="grid grid-cols-2 gap-2">
              {world.therapeutic_focus.map((focus) => (
                <label
                  key={focus}
                  className="flex items-center space-x-2 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={(
                      entryData.entry_preferences?.therapeutic_focus || []
                    ).includes(focus)}
                    onChange={() => handleTherapeuticFocusToggle(focus)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">{focus}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Privacy Mode */}
        <div className="mb-6">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={entryData.entry_preferences?.privacy_mode || false}
              onChange={(e) =>
                handlePreferenceChange("privacy_mode", e.target.checked)
              }
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <div>
              <span className="text-sm font-medium text-gray-700">
                Private Session
              </span>
              <p className="text-xs text-gray-500">
                Your session data will not be shared with other users or used
                for analytics
              </p>
            </div>
          </label>
        </div>
      </div>
    </div>
  );

  const renderConfirmationStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Ready to Enter
        </h3>

        {world && (
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h4 className="font-medium text-gray-900 mb-2">
              {world.world_title}
            </h4>
            <p className="text-sm text-gray-600 mb-3">{world.description}</p>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">Genre:</span>
                <span className="ml-2 text-gray-600">{world.world_genre}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Difficulty:</span>
                <span className="ml-2 text-gray-600">
                  {world.difficulty_level}
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Duration:</span>
                <span className="ml-2 text-gray-600">
                  ~{entryData.entry_preferences?.session_duration} minutes
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Privacy:</span>
                <span className="ml-2 text-gray-600">
                  {entryData.entry_preferences?.privacy_mode
                    ? "Private"
                    : "Standard"}
                </span>
              </div>
            </div>
          </div>
        )}

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="text-blue-600 mr-3 mt-0.5">ℹ️</div>
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">What happens next?</p>
              <ul className="list-disc list-inside space-y-1 text-blue-700">
                <li>You'll be transported to the world's starting location</li>
                <li>The narrative will adapt to your selected preferences</li>
                <li>You can pause or exit the session at any time</li>
                <li>Your progress will be automatically saved</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
          {/* Background overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Enter World</h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* Content */}
            {worldLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">
                  Loading world details...
                </span>
              </div>
            ) : worldError ? (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex items-center">
                  <div className="text-red-500 mr-3">⚠️</div>
                  <div>
                    <h3 className="text-sm font-medium text-red-800">
                      Failed to Load World
                    </h3>
                    <p className="text-sm text-red-700 mt-1">{worldError}</p>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {step === "preferences" && renderPreferencesStep()}
                {step === "confirmation" && renderConfirmationStep()}

                {entryError && (
                  <div className="mt-4 bg-red-50 border border-red-200 rounded-md p-4">
                    <div className="flex items-center">
                      <div className="text-red-500 mr-3">⚠️</div>
                      <div>
                        <h3 className="text-sm font-medium text-red-800">
                          Entry Failed
                        </h3>
                        <p className="text-sm text-red-700 mt-1">
                          {entryError}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex justify-between mt-8">
                  <div>
                    {step === "confirmation" && (
                      <button
                        onClick={() => setStep("preferences")}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                      >
                        Back
                      </button>
                    )}
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={onClose}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>

                    {step === "preferences" ? (
                      <button
                        onClick={() => setStep("confirmation")}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                      >
                        Continue
                      </button>
                    ) : (
                      <button
                        onClick={handleEnterWorld}
                        disabled={entering || !isAuthenticated}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
                      >
                        {entering ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Entering...
                          </>
                        ) : (
                          "Enter World"
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </>
            )}
          </motion.div>
        </div>
      </div>
    </AnimatePresence>
  );
};

export default WorldEntryModal;
