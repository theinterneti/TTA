# Error Message Standards

**Version:** 1.0.0  
**Last Updated:** 2025-09-29

This document defines the standardized error message format and guidelines for the TTA Player Experience application.

---

## Table of Contents

1. [Overview](#overview)
2. [Error Severity Levels](#error-severity-levels)
3. [Error Message Format](#error-message-format)
4. [User-Friendly Message Guidelines](#user-friendly-message-guidelines)
5. [Error Categories](#error-categories)
6. [Implementation Examples](#implementation-examples)
7. [Testing Guidelines](#testing-guidelines)

---

## Overview

All errors in the TTA application follow a consistent format to ensure:
- **User-friendly messaging** - Clear, actionable guidance for users
- **Technical accuracy** - Detailed information for debugging
- **Consistent experience** - Same error types displayed the same way
- **Appropriate severity** - Correct urgency and visual treatment

### Core Principles

1. **Never show "[object Object]"** - Always serialize errors properly
2. **Be specific but not technical** - Explain what happened in plain language
3. **Provide actionable guidance** - Tell users what they can do
4. **Log technical details** - Keep detailed info in console for debugging
5. **Match severity to impact** - Use appropriate severity levels

---

## Error Severity Levels

### INFO
**Use for:** Informational messages, confirmations, non-critical updates

**Visual Treatment:**
- Color: Blue (#2196F3)
- Icon: Info circle
- Auto-hide: 3 seconds

**Examples:**
- "Character saved successfully"
- "Session restored"
- "Settings updated"

### WARNING
**Use for:** Potential issues, degraded functionality, non-blocking problems

**Visual Treatment:**
- Color: Orange (#FF9800)
- Icon: Warning triangle
- Auto-hide: 5 seconds

**Examples:**
- "Connection unstable - some features may be limited"
- "Session will expire in 5 minutes"
- "Character limit approaching (4/5 characters)"

### ERROR
**Use for:** Failed operations, validation errors, recoverable errors

**Visual Treatment:**
- Color: Red (#F44336)
- Icon: Error circle
- Auto-hide: 5 seconds (or manual dismiss)

**Examples:**
- "Failed to create character. Please check your input and try again."
- "Authentication failed. Please log in again."
- "Unable to load conversation history."

### CRITICAL
**Use for:** System failures, data loss risks, security issues

**Visual Treatment:**
- Color: Dark Red (#D32F2F)
- Icon: Alert octagon
- Auto-hide: Never (requires manual dismiss)
- May include action buttons

**Examples:**
- "Connection lost. Your progress may not be saved."
- "Security token expired. Please log in immediately."
- "System error. Please contact support if this persists."

---

## Error Message Format

### Standard Error Object

```typescript
interface SerializedError {
  message: string;           // Technical message
  severity: ErrorSeverity;   // INFO | WARNING | ERROR | CRITICAL
  code?: string;             // HTTP status or error code
  details?: string;          // Additional context
  timestamp: string;         // ISO 8601 timestamp
  userMessage: string;       // User-friendly message
  technicalDetails?: any;    // Full error object for logging
}
```

### User-Facing Display

**Format:**
```
[Icon] [User Message]
[Optional: Action Button]
```

**Example:**
```
⚠️ Failed to create character. Please check your input and try again.
[Try Again]
```

---

## User-Friendly Message Guidelines

### DO:
✅ Use plain language: "Failed to save" not "Persistence operation unsuccessful"
✅ Be specific: "Character name must be 2-50 characters" not "Invalid input"
✅ Provide guidance: "Please check your connection and try again"
✅ Use active voice: "Unable to load" not "Loading could not be completed"
✅ Be concise: Keep messages under 100 characters when possible
✅ Include context: "Character Creation: Invalid name format"

### DON'T:
❌ Show technical jargon: "NullPointerException in CharacterService"
❌ Show stack traces: "at line 42 in character.service.ts"
❌ Show raw objects: "[object Object]"
❌ Be vague: "Something went wrong"
❌ Blame the user: "You entered invalid data"
❌ Use ALL CAPS: "ERROR: FAILED TO SAVE"

### Message Templates

**Authentication Errors:**
- "You need to log in to continue."
- "Your session has expired. Please log in again."
- "You don't have permission to perform this action."

**Validation Errors:**
- "Character name must be 2-50 characters."
- "Please enter a valid email address."
- "Password must contain at least 8 characters."

**Network Errors:**
- "Network error. Please check your connection and try again."
- "Request timed out. Please try again."
- "Unable to connect to server. Please try again later."

**Server Errors:**
- "Server error. Our team has been notified. Please try again later."
- "Service temporarily unavailable. Please try again in a few moments."

**Not Found Errors:**
- "Character not found. It may have been deleted."
- "The requested page does not exist."

---

## Error Categories

### 1. Authentication Errors (401, 403)

**HTTP 401 Unauthorized:**
```typescript
{
  userMessage: "You need to log in to continue.",
  severity: ErrorSeverity.ERROR,
  code: "401"
}
```

**HTTP 403 Forbidden:**
```typescript
{
  userMessage: "You don't have permission to perform this action.",
  severity: ErrorSeverity.ERROR,
  code: "403"
}
```

### 2. Validation Errors (400, 422)

**HTTP 400 Bad Request:**
```typescript
{
  userMessage: "Invalid request. Please check your input and try again.",
  severity: ErrorSeverity.ERROR,
  code: "400"
}
```

**HTTP 422 Unprocessable Entity:**
```typescript
{
  userMessage: "Validation error: Character name must be at least 2 characters",
  severity: ErrorSeverity.ERROR,
  code: "422",
  details: "Field: name, Constraint: min_length"
}
```

### 3. Not Found Errors (404)

```typescript
{
  userMessage: "The requested resource was not found.",
  severity: ErrorSeverity.ERROR,
  code: "404"
}
```

### 4. Rate Limiting (429)

```typescript
{
  userMessage: "Too many requests. Please wait a moment and try again.",
  severity: ErrorSeverity.WARNING,
  code: "429"
}
```

### 5. Server Errors (500, 503)

**HTTP 500 Internal Server Error:**
```typescript
{
  userMessage: "Server error. Our team has been notified. Please try again later.",
  severity: ErrorSeverity.CRITICAL,
  code: "500"
}
```

**HTTP 503 Service Unavailable:**
```typescript
{
  userMessage: "Service temporarily unavailable. Please try again in a few moments.",
  severity: ErrorSeverity.ERROR,
  code: "503"
}
```

### 6. Network Errors

```typescript
{
  userMessage: "Network error. Please check your connection and try again.",
  severity: ErrorSeverity.ERROR
}
```

### 7. WebSocket Errors

```typescript
{
  userMessage: "Connection lost. Attempting to reconnect...",
  severity: ErrorSeverity.WARNING
}
```

---

## Implementation Examples

### Using Error Utilities

```typescript
import { serializeError, displayError, getErrorMessage } from '../utils/errorHandling';

// Serialize and log error
try {
  await createCharacter(data);
} catch (error) {
  const serialized = displayError(error, 'Character Creation');
  // serialized.userMessage is ready for display
}

// Get user-friendly message only
try {
  await saveSession();
} catch (error) {
  const message = getErrorMessage(error, 'Session Save');
  showNotification(message);
}
```

### Using Notification Provider

```typescript
import { useNotification } from '../components/Notifications/NotificationProvider';

const { showError, showSuccess, showWarning } = useNotification();

// Show error with automatic formatting
try {
  await createCharacter(data);
  showSuccess('Character created successfully!');
} catch (error) {
  showError(error, 'Character Creation');
}
```

### Using Error Boundary

```tsx
import ErrorBoundary from '../components/ErrorBoundary/ErrorBoundary';

<ErrorBoundary
  onError={(error, errorInfo) => {
    // Log to monitoring service
    logError(error, errorInfo);
  }}
>
  <YourComponent />
</ErrorBoundary>
```

---

## Testing Guidelines

### Manual Testing Checklist

- [ ] All error scenarios display user-friendly messages
- [ ] No "[object Object]" displays anywhere
- [ ] Error severity matches visual treatment
- [ ] Technical details logged to console
- [ ] Action buttons work correctly
- [ ] Auto-hide timing is appropriate
- [ ] Error messages are clear and actionable

### Automated Testing

```typescript
describe('Error Handling', () => {
  it('should serialize error objects correctly', () => {
    const error = new Error('Test error');
    const serialized = serializeError(error);
    
    expect(serialized.userMessage).toBeDefined();
    expect(serialized.userMessage).not.toContain('[object Object]');
    expect(serialized.severity).toBeDefined();
  });

  it('should format API errors with user-friendly messages', () => {
    const apiError = {
      response: {
        status: 422,
        data: { detail: 'Validation failed' }
      }
    };
    
    const message = getErrorMessage(apiError);
    expect(message).toContain('Validation error');
  });
});
```

---

## Maintenance

### When to Update This Document

- New error categories are introduced
- Error message templates change
- Severity level definitions change
- New error handling utilities are added

### Review Schedule

- **Quarterly:** Review error messages for clarity
- **After incidents:** Update based on user feedback
- **With major releases:** Ensure consistency across features

---

**Document Owner:** Frontend Team  
**Last Review:** 2025-09-29  
**Next Review:** 2025-12-29

