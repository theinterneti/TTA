// Logseq: [[TTA.dev/Player_experience/Frontend/Src/Types/Index]]
// Common types used across the application

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface ApiError {
  message: string;
  details?: ValidationError[];
  code?: string;
}

// Therapeutic types
export type IntensityLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type DifficultyLevel = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
export type SafetyLevel = 'safe' | 'caution' | 'crisis';
export type MessageType = 'user' | 'assistant' | 'system';

export interface TherapeuticGoal {
  id: string;
  title: string;
  description: string;
  category: string;
  progress: number; // 0-100
}

export interface ProgressMetric {
  metric_name: string;
  current_value: number;
  target_value: number;
  unit: string;
  trend: 'improving' | 'stable' | 'declining';
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  type: 'world' | 'character' | 'therapeutic_approach' | 'activity';
  priority: 'low' | 'medium' | 'high';
  metadata?: Record<string, any>;
}

export interface CrisisResource {
  id: string;
  name: string;
  description: string;
  contact_info: string;
  availability: string;
  type: 'hotline' | 'chat' | 'text' | 'emergency';
  url?: string;
}

// UI Component types
export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface TabItem {
  id: string;
  label: string;
  content: React.ReactNode;
  disabled?: boolean;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  actions?: Array<{
    label: string;
    action: () => void;
  }>;
}

// Form types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'textarea' | 'select' | 'checkbox' | 'radio';
  required?: boolean;
  placeholder?: string;
  options?: SelectOption[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: RegExp;
    custom?: (value: any) => string | null;
  };
}

export interface FormState {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
