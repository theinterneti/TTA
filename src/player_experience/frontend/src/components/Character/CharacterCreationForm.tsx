import React, { useState, useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { RootState, AppDispatch } from "../../store/store";
import { createCharacter } from "../../store/slices/characterSlice";
import {
  CharacterFormData,
  characterFormSchema,
  defaultFormValues,
} from "./characterFormSchema";
import BasicInfoStep from "./steps/BasicInfoStep";
import BackgroundStep from "./steps/BackgroundStep";
import TherapeuticProfileStep from "./steps/TherapeuticProfileStep";

// Interface moved to characterFormSchema.ts

interface CharacterCreationFormProps {
  onClose: () => void;
  onSuccess?: () => void;
}

const CharacterCreationForm: React.FC<CharacterCreationFormProps> = ({
  onClose,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { profile } = useSelector((state: RootState) => state.player);
  const { creationInProgress, error } = useSelector(
    (state: RootState) => state.character
  );

  const [currentStep, setCurrentStep] = useState(1);

  const {
    control,
    handleSubmit,
    trigger,
    formState: { errors, isValid },
  } = useForm<CharacterFormData>({
    resolver: yupResolver(characterFormSchema) as any,
    defaultValues: defaultFormValues,
    mode: "onChange",
  });

  // All state management is now handled by React Hook Form
  // No more complex useState patterns that caused re-render loops

  // Validation is now handled by Yup schema - no more complex validation logic

  // Memoize getFieldsForStep to prevent recreation on every render
  const getFieldsForStep = useCallback(
    (step: number): (keyof CharacterFormData)[] => {
      switch (step) {
        case 1:
          return ["name", "appearance"];
        case 2:
          return ["background"];
        case 3:
          return ["therapeutic_profile"];
        default:
          return [];
      }
    },
    []
  ); // No dependencies - pure function

  const validateCurrentStep = useCallback(async (): Promise<boolean> => {
    const fieldsToValidate = getFieldsForStep(currentStep);
    const result = await trigger(fieldsToValidate);
    return result;
  }, [currentStep, trigger, getFieldsForStep]); // Include all dependencies

  // Form input handling is now managed by React Hook Form - no more complex state updates

  const handleNext = useCallback(async () => {
    const isValid = await validateCurrentStep();
    if (isValid) {
      setCurrentStep((prev) => prev + 1);
    }
  }, [validateCurrentStep]);

  const handlePrevious = useCallback(() => {
    setCurrentStep((prev) => prev - 1);
  }, []);

  // Array management is now handled by useFieldArray in step components

  const onSubmit = useCallback(
    async (data: CharacterFormData) => {
      if (!profile?.player_id) return;

      try {
        // Transform form data to match expected API structure
        const submissionData = {
          ...data,
          appearance: {
            ...data.appearance,
            // Map physical_description to description for backward compatibility
            description: data.appearance.physical_description,
          },
          background: {
            ...data.background,
            name: data.name,
            // Map backstory to story for backward compatibility
            story: data.background.backstory,
            // Map life_goals to goals for backward compatibility
            goals: data.background.life_goals,
          },
          therapeutic_profile: {
            ...data.therapeutic_profile,
            // Map readiness_level to comfort_level for backward compatibility
            comfort_level: Math.round(
              data.therapeutic_profile.readiness_level * 10
            ),
          },
        };

        await dispatch(
          createCharacter({
            playerId: profile.player_id,
            characterData: submissionData,
          })
        ).unwrap();

        onSuccess?.();
        onClose();
      } catch (error) {
        console.error("Failed to create character:", error);
      }
    },
    [profile?.player_id, dispatch, onSuccess, onClose]
  );

  // Submit handler is now the onSubmit function above

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return <BasicInfoStep control={control} errors={errors} />;
      case 2:
        return <BackgroundStep control={control} errors={errors} />;
      case 3:
        return <TherapeuticProfileStep control={control} errors={errors} />;
      default:
        return null;
    }
  };
  // Old render methods removed - now using step components

  // All old render methods removed - using step components

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden">
        <form onSubmit={handleSubmit(onSubmit)}>
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">
                Create New Character
              </h2>
              <button
                type="button"
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
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

            {/* Progress Steps */}
            <div className="flex items-center mt-4">
              {[1, 2, 3].map((step) => (
                <React.Fragment key={step}>
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      step <= currentStep
                        ? "bg-primary-600 text-white"
                        : "bg-gray-200 text-gray-600"
                    }`}
                  >
                    {step}
                  </div>
                  {step < 3 && (
                    <div
                      className={`flex-1 h-1 mx-2 ${
                        step < currentStep ? "bg-primary-600" : "bg-gray-200"
                      }`}
                    />
                  )}
                </React.Fragment>
              ))}
            </div>

            <div className="flex justify-between text-sm text-gray-600 mt-2">
              <span>Basic Info</span>
              <span>Background</span>
              <span>Therapeutic</span>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-4 overflow-y-auto max-h-[60vh]">
            {renderCurrentStep()}
          </div>

          {/* Error Display */}
          {error && (
            <div className="px-6 py-2">
              <div className="bg-red-50 border border-red-200 rounded-md p-3">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
            <button
              type="button"
              onClick={currentStep === 1 ? onClose : handlePrevious}
              className="btn-secondary"
            >
              {currentStep === 1 ? "Cancel" : "Previous"}
            </button>

            {currentStep < 3 ? (
              <button
                type="button"
                onClick={handleNext}
                className="btn-primary"
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                disabled={creationInProgress || !isValid}
                className="btn-primary disabled:opacity-50"
              >
                {creationInProgress ? (
                  <div className="flex items-center">
                    <div className="spinner mr-2"></div>
                    Creating...
                  </div>
                ) : (
                  "Create Character"
                )}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default CharacterCreationForm;
