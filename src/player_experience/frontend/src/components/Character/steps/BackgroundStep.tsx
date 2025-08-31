import React, { useState, useCallback } from "react";
import {
  Control,
  Controller,
  FieldErrors,
  useFieldArray,
} from "react-hook-form";
import { CharacterFormData } from "../characterFormSchema";

interface BackgroundStepProps {
  control: Control<CharacterFormData>;
  errors: FieldErrors<CharacterFormData>;
}

const BackgroundStep: React.FC<BackgroundStepProps> = React.memo(
  ({ control, errors }) => {
    const [newTrait, setNewTrait] = useState("");
    const [newGoal, setNewGoal] = useState("");

    const {
      fields: traitFields,
      append: appendTrait,
      remove: removeTrait,
    } = useFieldArray({
      control: control as any,
      name: "background.personality_traits",
    });

    const {
      fields: goalFields,
      append: appendGoal,
      remove: removeGoal,
    } = useFieldArray({
      control: control as any,
      name: "background.life_goals",
    });

    const handleAddTrait = useCallback(() => {
      if (newTrait.trim()) {
        appendTrait(newTrait.trim());
        setNewTrait("");
      }
    }, [newTrait, appendTrait]);

    const handleAddGoal = useCallback(() => {
      if (newGoal.trim()) {
        appendGoal(newGoal.trim());
        setNewGoal("");
      }
    }, [newGoal, appendGoal]);

    const handleTraitKeyPress = useCallback(
      (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
          e.preventDefault();
          handleAddTrait();
        }
      },
      [handleAddTrait]
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
            Background & Personality
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Background Story *
              </label>
              <Controller
                name="background.backstory"
                control={control}
                render={({ field }) => (
                  <>
                    <textarea
                      {...field}
                      className={`input-field ${
                        errors.background?.backstory ? "border-red-500" : ""
                      }`}
                      rows={4}
                      placeholder="Tell your character's story, their past experiences, and what brought them here..."
                    />
                    {errors.background?.backstory && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.background.backstory.message}
                      </p>
                    )}
                  </>
                )}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Personality Traits *
              </label>
              <div className="space-y-2">
                <div className="flex gap-2">
                  <input
                    type="text"
                    className="input-field flex-1"
                    placeholder="Add a personality trait..."
                    value={newTrait}
                    onChange={(e) => setNewTrait(e.target.value)}
                    onKeyPress={handleTraitKeyPress}
                  />
                  <button
                    type="button"
                    onClick={handleAddTrait}
                    className="btn-secondary px-4 py-2"
                    disabled={!newTrait.trim()}
                  >
                    Add
                  </button>
                </div>

                {traitFields.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {traitFields.map((field, index) => (
                      <div
                        key={field.id}
                        className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center gap-2"
                      >
                        <span>{(field as any).value || field}</span>
                        <button
                          type="button"
                          onClick={() => removeTrait(index)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {errors.background?.personality_traits && (
                  <p className="text-red-600 text-sm">
                    {errors.background.personality_traits.message}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Life Goals *
              </label>
              <div className="space-y-2">
                <div className="flex gap-2">
                  <input
                    type="text"
                    className="input-field flex-1"
                    placeholder="Add a life goal..."
                    value={newGoal}
                    onChange={(e) => setNewGoal(e.target.value)}
                    onKeyPress={handleGoalKeyPress}
                  />
                  <button
                    type="button"
                    onClick={handleAddGoal}
                    className="btn-secondary px-4 py-2"
                    disabled={!newGoal.trim()}
                  >
                    Add
                  </button>
                </div>

                {goalFields.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {goalFields.map((field, index) => (
                      <div
                        key={field.id}
                        className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm flex items-center gap-2"
                      >
                        <span>{(field as any).value || field}</span>
                        <button
                          type="button"
                          onClick={() => removeGoal(index)}
                          className="text-green-600 hover:text-green-800"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {errors.background?.life_goals && (
                  <p className="text-red-600 text-sm">
                    {errors.background.life_goals.message}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
);

BackgroundStep.displayName = "BackgroundStep";

export default BackgroundStep;
