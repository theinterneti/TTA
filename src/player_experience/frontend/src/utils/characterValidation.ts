/**
 * Character creation validation utilities
 */

export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Validate character name
 */
export const validateName = (name: string): string | null => {
  if (!name || name.trim().length === 0) {
    return 'Character name is required';
  }
  if (name.trim().length < 2) {
    return 'Character name must be at least 2 characters';
  }
  if (name.length > 50) {
    return 'Character name must be 50 characters or less';
  }
  if (!/^[a-zA-Z\s\-']+$/.test(name.trim())) {
    return 'Name can only contain letters, spaces, hyphens, and apostrophes';
  }
  return null;
};

/**
 * Format validation errors for display
 */
export const formatValidationErrors = (errors: ValidationError[]): Record<string, string> => {
  const formatted: Record<string, string> = {};
  errors.forEach(error => {
    formatted[error.field] = error.message;
  });
  return formatted;
};

/**
 * Parse API error response
 */
export const parseAPIError = (error: any): string => {
  if (typeof error === 'string') {
    return error;
  }

  if (error?.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
    }
    return JSON.stringify(detail);
  }

  if (error?.message) {
    return error.message;
  }

  return 'An unexpected error occurred';
};
