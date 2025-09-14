import * as yup from "yup";
import { IntensityLevel } from "../../types";

export interface CharacterFormData {
  name: string;
  appearance: {
    physical_description: string;
    age_range?: string;
    gender_identity?: string;
    clothing_style?: string;
    distinctive_features?: string[];
  };
  background: {
    name: string;
    backstory: string;
    personality_traits: string[];
    life_goals: string[];
  };
  therapeutic_profile: {
    primary_concerns: string[];
    preferred_intensity: IntensityLevel;
    therapeutic_goals?: string[];
    comfort_zones?: string[];
    readiness_level: number;
    comfort_level: number;
  };
}

export const characterFormSchema = yup.object({
  name: yup
    .string()
    .required("Character name is required")
    .max(50, "Character name must be 50 characters or less")
    .trim(),

  appearance: yup.object({
    physical_description: yup
      .string()
      .required("Character appearance description is required")
      .trim(),
    age_range: yup.string().optional(),
    gender_identity: yup.string().optional(),
    clothing_style: yup.string().optional(),
    distinctive_features: yup.array().of(yup.string().required()).optional(),
  }),

  background: yup.object({
    name: yup.string().required(),
    backstory: yup
      .string()
      .required("Character background story is required")
      .trim(),
    personality_traits: yup
      .array()
      .of(yup.string().required())
      .min(1, "At least one personality trait is required"),
    life_goals: yup
      .array()
      .of(yup.string().required())
      .min(1, "At least one character goal is required"),
  }),

  therapeutic_profile: yup.object({
    primary_concerns: yup
      .array()
      .of(yup.string().required())
      .min(1, "At least one primary concern is required"),
    preferred_intensity: yup
      .mixed<IntensityLevel>()
      .oneOf(["LOW", "MEDIUM", "HIGH"])
      .required(),
    therapeutic_goals: yup.array().of(yup.string().required()).optional(),
    comfort_zones: yup.array().of(yup.string().required()).optional(),
    readiness_level: yup.number().min(0).max(1).required(),
    comfort_level: yup.number().min(1).max(10).required(),
  }),
});

export const defaultFormValues: CharacterFormData = {
  name: "",
  appearance: {
    physical_description: "",
    age_range: "adult",
    gender_identity: "non-binary",
    clothing_style: "casual",
    distinctive_features: [],
  },
  background: {
    name: "",
    backstory: "",
    personality_traits: [],
    life_goals: [],
  },
  therapeutic_profile: {
    primary_concerns: [],
    preferred_intensity: "MEDIUM" as IntensityLevel,
    therapeutic_goals: [],
    comfort_zones: [],
    readiness_level: 0.5,
    comfort_level: 5,
  },
};
