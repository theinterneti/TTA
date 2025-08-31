import React, { useState, useCallback } from "react";
import {
  Control,
  Controller,
  FieldErrors,
  useFieldArray,
  useWatch,
} from "react-hook-form";
import { CharacterFormData } from "../characterFormSchema";
import { IntensityLevel } from "../../../types";

interface TherapeuticProfileStepProps {
  control: Control<CharacterFormData, any>;
  errors: FieldErrors<CharacterFormData>;
}

const TherapeuticProfileStep: React.FC<TherapeuticProfileStepProps> =
  React.memo(({ control, errors }) => {
    const [newPrimaryConcern, setNewPrimaryConcern] = useState("");
    const [newTherapeuticGoal, setNewTherapeuticGoal] = useState("");

    const {
      fields: concernFields,
      append: appendConcern,
      remove: removeConcern,
    } = useFieldArray({
      control: control as any,
      name: "therapeutic_profile.primary_concerns",
    });

    const {
      fields: goalFields,
      append: appendGoal,
      remove: removeGoal,
    } = useFieldArray({
      control: control as any,
      name: "therapeutic_profile.therapeutic_goals",
    });

    // Watch form values for the summary
    const formValues = useWatch({ control });

    const handleAddConcern = useCallback(() => {
      if (newPrimaryConcern.trim()) {
        appendConcern(newPrimaryConcern.trim());
        setNewPrimaryConcern("");
      }
    }, [newPrimaryConcern, appendConcern]);

    const handleAddGoal = useCallback(() => {
      if (newTherapeuticGoal.trim()) {
        appendGoal(newTherapeuticGoal.trim());
        setNewTherapeuticGoal("");
      }
    }, [newTherapeuticGoal, appendGoal]);

    const handleConcernKeyPress = useCallback(
      (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
          e.preventDefault();
          handleAddConcern();
        }
      },
      [handleAddConcern]
    );

    const handleGoalKeyPress = useCallback(
      (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
          e.preventDefault();
          handleAddGoal();
        }
      },
      [handleAddGoal]
    );

    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Therapeutic Profile
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Primary Concerns *
              </label>
              <div className="space-y-2">
                <div className="flex gap-2">
                  <input
                    type="text"
                    className="input-field flex-1"
                    placeholder="Add a primary concern..."
                    value={newPrimaryConcern}
                    onChange={(e) => setNewPrimaryConcern(e.target.value)}
                    onKeyPress={handleConcernKeyPress}
                  />
                  <button
                    type="button"
                    onClick={handleAddConcern}
                    className="btn-secondary px-4 py-2"
                    disabled={!newPrimaryConcern.trim()}
                  >
                    Add
                  </button>
                </div>

                {concernFields.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {concernFields.map((field, index) => (
                      <div
                        key={field.id}
                        className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm flex items-center gap-2"
                      >
                        <span>{(field as any).value || field}</span>
                        <button
                          type="button"
                          onClick={() => removeConcern(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {errors.therapeutic_profile?.primary_concerns && (
                  <p className="text-red-600 text-sm">
                    {errors.therapeutic_profile.primary_concerns.message}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Therapeutic Goals
              </label>
              <div className="space-y-2">
                <div className="flex gap-2">
                  <input
                    type="text"
                    className="input-field flex-1"
                    placeholder="Add a therapeutic goal..."
                    value={newTherapeuticGoal}
                    onChange={(e) => setNewTherapeuticGoal(e.target.value)}
                    onKeyPress={handleGoalKeyPress}
                  />
                  <button
                    type="button"
                    onClick={handleAddGoal}
                    className="btn-secondary px-4 py-2"
                    disabled={!newTherapeuticGoal.trim()}
                  >
                    Add
                  </button>
                </div>

                {goalFields.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {goalFields.map((field, index) => (
                      <div
                        key={field.id}
                        className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm flex items-center gap-2"
                      >
                        <span>{(field as any).value || field}</span>
                        <button
                          type="button"
                          onClick={() => removeGoal(index)}
                          className="text-purple-600 hover:text-purple-800"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Therapeutic Intensity
              </label>
              <Controller
                name="therapeutic_profile.preferred_intensity"
                control={control}
                render={({ field }) => (
                  <select {...field} className="input-field">
                    <option value="LOW">
                      Low - Gentle guidance and support
                    </option>
                    <option value="MEDIUM">
                      Medium - Balanced therapeutic approach
                    </option>
                    <option value="HIGH">
                      High - Intensive therapeutic work
                    </option>
                  </select>
                )}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Readiness Level:{" "}
                {Math.round(
                  (formValues.therapeutic_profile?.readiness_level || 0.5) * 10
                )}
                /10
              </label>
              <Controller
                name="therapeutic_profile.readiness_level"
                control={control}
                render={({ field }) => (
                  <input
                    {...field}
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    onChange={(e) => field.onChange(parseFloat(e.target.value))}
                  />
                )}
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Not Ready</span>
                <span>Somewhat Ready</span>
                <span>Very Ready</span>
              </div>
            </div>
          </div>
        </div>

        {/* Character Summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Character Summary</h4>
          <div className="space-y-2 text-sm">
            <p>
              <span className="font-medium">Name:</span>{" "}
              {formValues.name || "Not set"}
            </p>
            <p>
              <span className="font-medium">Readiness Level:</span>{" "}
              {Math.round(
                (formValues.therapeutic_profile?.readiness_level || 0.5) * 10
              )}
              /10
            </p>
            <p>
              <span className="font-medium">Intensity:</span>{" "}
              {formValues.therapeutic_profile?.preferred_intensity || "MEDIUM"}
            </p>
            <p>
              <span className="font-medium">Traits:</span>{" "}
              {formValues.background?.personality_traits?.join(", ") ||
                "None added"}
            </p>
            <p>
              <span className="font-medium">Goals:</span>{" "}
              {formValues.background?.life_goals?.join(", ") || "None added"}
            </p>
            <p>
              <span className="font-medium">Therapeutic Goals:</span>{" "}
              {formValues.therapeutic_profile?.therapeutic_goals?.join(", ") ||
                "None added"}
            </p>
          </div>
        </div>
      </div>
    );
  });

TherapeuticProfileStep.displayName = "TherapeuticProfileStep";

export default TherapeuticProfileStep;
