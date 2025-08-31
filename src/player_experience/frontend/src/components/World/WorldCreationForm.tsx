import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { nexusAPI } from "../../services/api";
import { useAuthGuard } from "../../hooks/useAuthGuard";

interface WorldCreationData {
  world_title: string;
  world_genre: string;
  description: string;
  difficulty_level: "BEGINNER" | "INTERMEDIATE" | "ADVANCED";
  threat_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  therapeutic_focus: string[];
  tags: string[];
  estimated_duration: number;
  max_players: number;
  is_public: boolean;
}

interface WorldCreationFormProps {
  onSuccess?: (worldId: string) => void;
  onCancel?: () => void;
  className?: string;
}

const GENRES = [
  "Fantasy",
  "Sci-Fi",
  "Mystery",
  "Adventure",
  "Horror",
  "Romance",
  "Thriller",
  "Drama",
  "Comedy",
  "Historical",
  "Psychological",
  "Educational",
];

const THERAPEUTIC_FOCUSES = [
  "Anxiety Management",
  "Depression Support",
  "Trauma Recovery",
  "Social Skills",
  "Emotional Regulation",
  "Self-Esteem",
  "Grief Processing",
  "Addiction Recovery",
  "Relationship Building",
  "Stress Management",
  "Mindfulness",
  "Communication Skills",
];

const WorldCreationForm: React.FC<WorldCreationFormProps> = ({
  onSuccess,
  onCancel,
  className = "",
}) => {
  const { isAuthenticated, user } = useAuthGuard({ autoRedirect: false });
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const [formData, setFormData] = useState<WorldCreationData>({
    world_title: "",
    world_genre: "",
    description: "",
    difficulty_level: "BEGINNER",
    threat_level: "LOW",
    therapeutic_focus: [],
    tags: [],
    estimated_duration: 30,
    max_players: 1,
    is_public: false,
  });

  const [validationErrors, setValidationErrors] = useState<
    Record<string, string>
  >({});
  const [customTag, setCustomTag] = useState("");

  const validateStep = (step: number): boolean => {
    const errors: Record<string, string> = {};

    switch (step) {
      case 1:
        if (!formData.world_title.trim()) {
          errors.world_title = "World title is required";
        } else if (formData.world_title.length < 3) {
          errors.world_title = "World title must be at least 3 characters";
        } else if (formData.world_title.length > 100) {
          errors.world_title = "World title must be less than 100 characters";
        }

        if (!formData.world_genre) {
          errors.world_genre = "Please select a genre";
        }

        if (!formData.description.trim()) {
          errors.description = "Description is required";
        } else if (formData.description.length < 20) {
          errors.description = "Description must be at least 20 characters";
        } else if (formData.description.length > 1000) {
          errors.description = "Description must be less than 1000 characters";
        }
        break;

      case 2:
        if (formData.therapeutic_focus.length === 0) {
          errors.therapeutic_focus =
            "Please select at least one therapeutic focus";
        }

        if (formData.estimated_duration < 5) {
          errors.estimated_duration = "Duration must be at least 5 minutes";
        } else if (formData.estimated_duration > 300) {
          errors.estimated_duration = "Duration must be less than 300 minutes";
        }

        if (formData.max_players < 1) {
          errors.max_players = "Must allow at least 1 player";
        } else if (formData.max_players > 10) {
          errors.max_players = "Maximum 10 players allowed";
        }
        break;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (field: keyof WorldCreationData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleTherapeuticFocusToggle = (focus: string) => {
    const current = formData.therapeutic_focus;
    const updated = current.includes(focus)
      ? current.filter((f) => f !== focus)
      : [...current, focus];

    handleInputChange("therapeutic_focus", updated);
  };

  const handleAddTag = () => {
    if (customTag.trim() && !formData.tags.includes(customTag.trim())) {
      handleInputChange("tags", [...formData.tags, customTag.trim()]);
      setCustomTag("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    handleInputChange(
      "tags",
      formData.tags.filter((tag) => tag !== tagToRemove)
    );
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    setCurrentStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep(2)) return;

    if (!isAuthenticated) {
      setSubmitError("You must be logged in to create a world");
      return;
    }

    try {
      setIsSubmitting(true);
      setSubmitError(null);

      const response = await nexusAPI.createWorld(formData);
      const worldId = (response as any).world_id || (response as any).id;

      if (onSuccess) {
        onSuccess(worldId);
      }
    } catch (error: any) {
      console.error("Failed to create world:", error);
      setSubmitError(
        error.message || "Failed to create world. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          World Title *
        </label>
        <input
          type="text"
          value={formData.world_title}
          onChange={(e) => handleInputChange("world_title", e.target.value)}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            validationErrors.world_title ? "border-red-300" : "border-gray-300"
          }`}
          placeholder="Enter a compelling world title..."
          maxLength={100}
        />
        {validationErrors.world_title && (
          <p className="mt-1 text-sm text-red-600">
            {validationErrors.world_title}
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Genre *
        </label>
        <select
          value={formData.world_genre}
          onChange={(e) => handleInputChange("world_genre", e.target.value)}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            validationErrors.world_genre ? "border-red-300" : "border-gray-300"
          }`}
        >
          <option value="">Select a genre...</option>
          {GENRES.map((genre) => (
            <option key={genre} value={genre}>
              {genre}
            </option>
          ))}
        </select>
        {validationErrors.world_genre && (
          <p className="mt-1 text-sm text-red-600">
            {validationErrors.world_genre}
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description *
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => handleInputChange("description", e.target.value)}
          rows={4}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            validationErrors.description ? "border-red-300" : "border-gray-300"
          }`}
          placeholder="Describe your world's setting, story, and therapeutic goals..."
          maxLength={1000}
        />
        <div className="flex justify-between items-center mt-1">
          {validationErrors.description ? (
            <p className="text-sm text-red-600">
              {validationErrors.description}
            </p>
          ) : (
            <div />
          )}
          <p className="text-sm text-gray-500">
            {formData.description.length}/1000
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Difficulty Level
          </label>
          <select
            value={formData.difficulty_level}
            onChange={(e) =>
              handleInputChange("difficulty_level", e.target.value)
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="BEGINNER">Beginner</option>
            <option value="INTERMEDIATE">Intermediate</option>
            <option value="ADVANCED">Advanced</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Threat Level
          </label>
          <select
            value={formData.threat_level}
            onChange={(e) => handleInputChange("threat_level", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Therapeutic Focus Areas *
        </label>
        <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
          {THERAPEUTIC_FOCUSES.map((focus) => (
            <label
              key={focus}
              className="flex items-center space-x-2 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={formData.therapeutic_focus.includes(focus)}
                onChange={() => handleTherapeuticFocusToggle(focus)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{focus}</span>
            </label>
          ))}
        </div>
        {validationErrors.therapeutic_focus && (
          <p className="mt-1 text-sm text-red-600">
            {validationErrors.therapeutic_focus}
          </p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Estimated Duration (minutes)
          </label>
          <input
            type="number"
            value={formData.estimated_duration}
            onChange={(e) =>
              handleInputChange(
                "estimated_duration",
                parseInt(e.target.value) || 0
              )
            }
            min={5}
            max={300}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validationErrors.estimated_duration
                ? "border-red-300"
                : "border-gray-300"
            }`}
          />
          {validationErrors.estimated_duration && (
            <p className="mt-1 text-sm text-red-600">
              {validationErrors.estimated_duration}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Max Players
          </label>
          <input
            type="number"
            value={formData.max_players}
            onChange={(e) =>
              handleInputChange("max_players", parseInt(e.target.value) || 1)
            }
            min={1}
            max={10}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validationErrors.max_players
                ? "border-red-300"
                : "border-gray-300"
            }`}
          />
          {validationErrors.max_players && (
            <p className="mt-1 text-sm text-red-600">
              {validationErrors.max_players}
            </p>
          )}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Tags (Optional)
        </label>
        <div className="flex space-x-2 mb-2">
          <input
            type="text"
            value={customTag}
            onChange={(e) => setCustomTag(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleAddTag()}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Add a tag..."
            maxLength={20}
          />
          <button
            type="button"
            onClick={handleAddTag}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Add
          </button>
        </div>
        {formData.tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {formData.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="ml-1 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      <div>
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={formData.is_public}
            onChange={(e) => handleInputChange("is_public", e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">
            Make this world publicly available to other users
          </span>
        </label>
      </div>
    </div>
  );

  if (!isAuthenticated) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="text-center">
          <div className="text-yellow-500 text-2xl mb-4">🔒</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Authentication Required
          </h3>
          <p className="text-gray-600 mb-4">
            You must be logged in to create a new world.
          </p>
          <button
            onClick={() => (window.location.href = "/auth/login")}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Sign In
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">Create New World</h2>
        <div className="flex items-center mt-2">
          <div className="flex space-x-2">
            {[1, 2].map((step) => (
              <div
                key={step}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step === currentStep
                    ? "bg-blue-600 text-white"
                    : step < currentStep
                    ? "bg-green-600 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                {step < currentStep ? "✓" : step}
              </div>
            ))}
          </div>
          <div className="ml-4 text-sm text-gray-600">
            Step {currentStep} of 2:{" "}
            {currentStep === 1 ? "Basic Information" : "Configuration"}
          </div>
        </div>
      </div>

      <div className="p-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {currentStep === 1 ? renderStep1() : renderStep2()}
          </motion.div>
        </AnimatePresence>

        {submitError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-800">{submitError}</p>
          </div>
        )}
      </div>

      <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
        <div>
          {onCancel && (
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
          )}
        </div>

        <div className="flex space-x-3">
          {currentStep > 1 && (
            <button
              onClick={handlePrevious}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Previous
            </button>
          )}

          {currentStep < 2 ? (
            <button
              onClick={handleNext}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creating...
                </>
              ) : (
                "Create World"
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorldCreationForm;
