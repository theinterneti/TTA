/**
 * Error Handling Utilities Tests
 *
 * Comprehensive tests for error serialization, formatting, and display utilities.
 */

import {
  serializeError,
  getErrorMessage,
  displayError,
  isNetworkError,
  isAuthError,
  isValidationError,
  createErrorNotification,
  ErrorSeverity,
} from '../errorHandling';

describe('Error Handling Utilities', () => {
  // Suppress console output during tests
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'info').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('serializeError', () => {
    it('should handle null/undefined errors', () => {
      const result = serializeError(null);

      expect(result.message).toBe('An unknown error occurred');
      expect(result.severity).toBe(ErrorSeverity.ERROR);
      expect(result.userMessage).toBe('Something went wrong. Please try again.');
      expect(result.timestamp).toBeDefined();
    });

    it('should serialize Error objects', () => {
      const error = new Error('Test error message');
      const result = serializeError(error);

      expect(result.message).toBe('Test error message');
      expect(result.severity).toBe(ErrorSeverity.ERROR);
      expect(result.userMessage).toContain('error');
      expect(result.technicalDetails).toBeDefined();
      expect(result.technicalDetails.name).toBe('Error');
    });

    it('should serialize API error responses', () => {
      const apiError = {
        response: {
          status: 422,
          data: {
            detail: 'Validation failed',
          },
        },
      };

      const result = serializeError(apiError);

      expect(result.message).toBe('Validation failed');
      expect(result.code).toBe('422');
      expect(result.severity).toBe(ErrorSeverity.ERROR);
      expect(result.userMessage).toContain('Validation error');
    });

    it('should serialize string errors', () => {
      const result = serializeError('Simple error message');

      expect(result.message).toBe('Simple error message');
      expect(result.severity).toBe(ErrorSeverity.ERROR);
      expect(result.userMessage).toBe('Simple error message');
    });

    it('should serialize objects with message property', () => {
      const error = {
        message: 'Custom error',
        code: 'CUSTOM_ERROR',
        severity: ErrorSeverity.WARNING,
      };

      const result = serializeError(error);

      expect(result.message).toBe('Custom error');
      expect(result.code).toBe('CUSTOM_ERROR');
      expect(result.severity).toBe(ErrorSeverity.WARNING);
    });

    it('should handle generic objects', () => {
      const error = { foo: 'bar', baz: 123 };
      const result = serializeError(error);

      expect(result.message).toContain('foo');
      expect(result.message).toContain('bar');
      expect(result.userMessage).toBe('An unexpected error occurred. Please try again.');
    });

    it('should never return "[object Object]"', () => {
      const testCases = [
        null,
        undefined,
        new Error('test'),
        { response: { status: 500, data: {} } },
        'string error',
        { message: 'test' },
        { foo: 'bar' },
        [],
        123,
      ];

      testCases.forEach((testCase) => {
        const result = serializeError(testCase);
        expect(result.message).not.toContain('[object Object]');
        expect(result.userMessage).not.toContain('[object Object]');
      });
    });
  });

  describe('getErrorMessage', () => {
    it('should extract user-friendly message from errors', () => {
      const error = new Error('Technical error message');
      const message = getErrorMessage(error);

      expect(message).toBeDefined();
      expect(message).not.toContain('[object Object]');
    });

    it('should include context in message', () => {
      const error = new Error('Test error');
      const message = getErrorMessage(error, 'Character Creation');

      expect(message).toContain('Character Creation');
    });

    it('should format API errors appropriately', () => {
      const apiError = {
        response: {
          status: 401,
          data: { detail: 'Unauthorized' },
        },
      };

      const message = getErrorMessage(apiError);
      expect(message).toContain('log in');
    });
  });

  describe('HTTP Status Code Handling', () => {
    const testCases = [
      { status: 400, expectedText: 'Invalid request' },
      { status: 401, expectedText: 'log in' },
      { status: 403, expectedText: 'permission' },
      { status: 404, expectedText: 'not found' },
      { status: 422, expectedText: 'Validation error' },
      { status: 429, expectedText: 'Too many requests' },
      { status: 500, expectedText: 'Server error' },
      { status: 503, expectedText: 'temporarily unavailable' },
    ];

    testCases.forEach(({ status, expectedText }) => {
      it(`should format ${status} errors correctly`, () => {
        const error = {
          response: {
            status,
            data: {},
          },
        };

        const message = getErrorMessage(error);
        expect(message.toLowerCase()).toContain(expectedText.toLowerCase());
      });
    });
  });

  describe('Validation Error Formatting', () => {
    it('should format Pydantic validation errors', () => {
      const error = {
        response: {
          status: 422,
          data: {
            detail: [
              {
                loc: ['body', 'name'],
                msg: 'String should have at least 2 characters',
                type: 'value_error',
              },
              {
                loc: ['body', 'email'],
                msg: 'Invalid email format',
                type: 'value_error',
              },
            ],
          },
        },
      };

      const message = getErrorMessage(error);
      expect(message).toContain('Validation error');
      expect(message).toContain('name');
      expect(message).toContain('email');
    });

    it('should format simple validation errors', () => {
      const error = {
        response: {
          status: 422,
          data: {
            detail: 'Character name is required',
          },
        },
      };

      const message = getErrorMessage(error);
      expect(message).toContain('Validation error');
      expect(message).toContain('Character name is required');
    });
  });

  describe('Error Type Detection', () => {
    it('should detect network errors', () => {
      const networkError = new Error('Network request failed');
      expect(isNetworkError(networkError)).toBe(true);

      const otherError = new Error('Something else');
      expect(isNetworkError(otherError)).toBe(false);
    });

    it('should detect authentication errors', () => {
      const authError = {
        response: {
          status: 401,
          data: {},
        },
      };
      expect(isAuthError(authError)).toBe(true);

      const forbiddenError = {
        response: {
          status: 403,
          data: {},
        },
      };
      expect(isAuthError(forbiddenError)).toBe(true);

      const otherError = {
        response: {
          status: 500,
          data: {},
        },
      };
      expect(isAuthError(otherError)).toBe(false);
    });

    it('should detect validation errors', () => {
      const validationError = {
        response: {
          status: 422,
          data: {},
        },
      };
      expect(isValidationError(validationError)).toBe(true);

      const badRequestError = {
        response: {
          status: 400,
          data: {},
        },
      };
      expect(isValidationError(badRequestError)).toBe(true);

      const otherError = {
        response: {
          status: 500,
          data: {},
        },
      };
      expect(isValidationError(otherError)).toBe(false);
    });
  });

  describe('createErrorNotification', () => {
    it('should create notification with default options', () => {
      const error = new Error('Test error');
      const notification = createErrorNotification(error);

      expect(notification.id).toBeDefined();
      expect(notification.message).toBeDefined();
      expect(notification.message).not.toContain('[object Object]');
      expect(notification.severity).toBe(ErrorSeverity.ERROR);
      expect(notification.dismissible).toBe(true);
      expect(notification.autoHideDuration).toBe(5000);
    });

    it('should create notification with custom options', () => {
      const error = new Error('Test error');
      const action = { label: 'Retry', handler: jest.fn() };

      const notification = createErrorNotification(error, 'Test Context', {
        dismissible: false,
        autoHideDuration: 10000,
        action,
      });

      expect(notification.message).toContain('Test Context');
      expect(notification.dismissible).toBe(false);
      expect(notification.autoHideDuration).toBe(10000);
      expect(notification.action).toBe(action);
    });

    it('should not auto-hide critical errors', () => {
      const criticalError = {
        response: {
          status: 500,
          data: { detail: 'Server error' },
        },
      };

      const notification = createErrorNotification(criticalError);
      expect(notification.severity).toBe(ErrorSeverity.CRITICAL);
      expect(notification.autoHideDuration).toBeUndefined();
    });
  });

  describe('displayError', () => {
    it('should log errors to console', () => {
      const error = new Error('Test error');
      displayError(error);

      expect(console.error).toHaveBeenCalled();
    });

    it('should log with appropriate level based on severity', () => {
      const warningError = {
        message: 'Warning message',
        severity: ErrorSeverity.WARNING,
      };

      displayError(warningError);
      expect(console.warn).toHaveBeenCalled();
    });

    it('should return serialized error', () => {
      const error = new Error('Test error');
      const result = displayError(error, 'Test Context');

      expect(result.message).toBe('Test error');
      expect(result.userMessage).toBeDefined();
    });
  });

  describe('Context Handling', () => {
    it('should prepend context to user messages', () => {
      const error = new Error('Test error');
      const message = getErrorMessage(error, 'Character Creation');

      expect(message).toMatch(/Character Creation/);
    });

    it('should handle missing context gracefully', () => {
      const error = new Error('Test error');
      const message = getErrorMessage(error);

      expect(message).toBeDefined();
      expect(message).not.toContain('undefined');
    });
  });

  describe('Edge Cases', () => {
    it('should handle circular references', () => {
      const circular: any = { foo: 'bar' };
      circular.self = circular;

      const result = serializeError(circular);
      expect(result.userMessage).toBeDefined();
      expect(result.userMessage).not.toContain('[object Object]');
    });

    it('should handle very long error messages', () => {
      const longMessage = 'A'.repeat(1000);
      const error = new Error(longMessage);

      const result = serializeError(error);
      expect(result.userMessage).toBeDefined();
      expect(result.userMessage.length).toBeLessThan(200);
    });

    it('should handle errors with special characters', () => {
      const error = new Error('Error with <html> & "quotes" and \'apostrophes\'');
      const result = serializeError(error);

      expect(result.userMessage).toBeDefined();
      expect(result.userMessage).not.toContain('[object Object]');
    });
  });
});
