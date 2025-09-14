import React from "react";
import { Control, Controller, FieldErrors } from "react-hook-form";
import { CharacterFormData } from "../characterFormSchema";

interface BasicInfoStepProps {
  control: Control<CharacterFormData, any>;
  errors: FieldErrors<CharacterFormData>;
}

const BasicInfoStep: React.FC<BasicInfoStepProps> = React.memo(
  ({ control, errors }) => {
    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Basic Information
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Character Name *
              </label>
              <Controller
                name="name"
                control={control}
                render={({ field }) => (
                  <>
                    <input
                      {...field}
                      type="text"
                      className={`input-field ${
                        errors.name ? "border-red-500" : ""
                      }`}
                      placeholder="Enter your character's name"
                      maxLength={50}
                    />
                    {errors.name && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.name.message}
                      </p>
                    )}
                    <p className="text-gray-500 text-xs mt-1">
                      {field.value?.length || 0}/50 characters
                    </p>
                  </>
                )}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Appearance Description *
              </label>
              <Controller
                name="appearance.physical_description"
                control={control}
                render={({ field }) => (
                  <>
                    <textarea
                      {...field}
                      className={`input-field ${
                        errors.appearance?.physical_description
                          ? "border-red-500"
                          : ""
                      }`}
                      rows={4}
                      placeholder="Describe your character's appearance, style, and any distinctive features..."
                    />
                    {errors.appearance?.physical_description && (
                      <p className="text-red-600 text-sm mt-1">
                        {errors.appearance.physical_description.message}
                      </p>
                    )}
                  </>
                )}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Age Range
                </label>
                <Controller
                  name="appearance.age_range"
                  control={control}
                  render={({ field }) => (
                    <select {...field} className="input-field">
                      <option value="young">Young Adult (18-25)</option>
                      <option value="adult">Adult (26-40)</option>
                      <option value="middle">Middle-aged (41-60)</option>
                      <option value="senior">Senior (60+)</option>
                    </select>
                  )}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gender Identity
                </label>
                <Controller
                  name="appearance.gender_identity"
                  control={control}
                  render={({ field }) => (
                    <select {...field} className="input-field">
                      <option value="non-binary">Non-binary</option>
                      <option value="female">Female</option>
                      <option value="male">Male</option>
                      <option value="other">Other</option>
                      <option value="prefer-not-to-say">
                        Prefer not to say
                      </option>
                    </select>
                  )}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Clothing Style
              </label>
              <Controller
                name="appearance.clothing_style"
                control={control}
                render={({ field }) => (
                  <select {...field} className="input-field">
                    <option value="casual">Casual</option>
                    <option value="professional">Professional</option>
                    <option value="artistic">Artistic</option>
                    <option value="sporty">Sporty</option>
                    <option value="elegant">Elegant</option>
                    <option value="alternative">Alternative</option>
                  </select>
                )}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }
);

BasicInfoStep.displayName = "BasicInfoStep";

export default BasicInfoStep;
