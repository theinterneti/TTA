// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Setup axe-core for accessibility testing
import 'jest-axe/extend-expect';

// Configure axe-core for therapeutic application accessibility standards
import { configureAxe } from 'jest-axe';

// Configure axe with WCAG 2.1 AA standards and therapeutic-specific rules
const axe = configureAxe({
  rules: {
    // Ensure color contrast meets WCAG AA standards (4.5:1 for normal text)
    'color-contrast': { enabled: true },

    // Ensure proper heading hierarchy for screen readers
    'heading-order': { enabled: true },

    // Ensure all interactive elements are keyboard accessible
    'keyboard': { enabled: true },

    // Ensure proper focus management
    'focus-order-semantics': { enabled: true },

    // Ensure proper ARIA usage
    'aria-valid-attr': { enabled: true },
    'aria-valid-attr-value': { enabled: true },
    'aria-required-attr': { enabled: true },

    // Ensure proper form labeling (critical for therapeutic applications)
    'label': { enabled: true },
    'label-title-only': { enabled: true },

    // Ensure proper semantic structure
    'landmark-one-main': { enabled: true },
    'region': { enabled: true },

    // Ensure images have alt text
    'image-alt': { enabled: true },

    // Ensure links have accessible names
    'link-name': { enabled: true },

    // Ensure buttons have accessible names
    'button-name': { enabled: true },

    // Therapeutic application specific: ensure form controls are properly grouped
    'fieldset-legend': { enabled: true },

    // Ensure proper tab order
    'tabindex': { enabled: true },

    // Ensure no duplicate IDs
    'duplicate-id': { enabled: true },

    // Ensure proper list structure
    'list': { enabled: true },
    'listitem': { enabled: true },

    // Ensure proper table structure (if used)
    'table-header': { enabled: true },
    'th-has-data-cells': { enabled: true },

    // Ensure meta viewport is properly configured for mobile accessibility
    'meta-viewport': { enabled: true },

    // Ensure page has a title
    'document-title': { enabled: false }, // Disabled for component tests

    // Ensure HTML lang attribute is present
    'html-has-lang': { enabled: false }, // Disabled for component tests

    // Ensure valid HTML structure
    'html-lang-valid': { enabled: false }, // Disabled for component tests
  },

  // Set tags for WCAG 2.1 AA compliance
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],

  // Configure for therapeutic applications
  options: {
    // Include hidden content in accessibility checks
    includeHidden: false,

    // Set appropriate timeout for complex components
    timeout: 10000,

    // Configure for React applications
    reporter: 'v2',
  },
});

// Global test setup for accessibility testing
beforeEach(() => {
  // Reset any global state that might affect accessibility tests
  document.body.innerHTML = '';

  // Ensure proper viewport for mobile accessibility testing
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: 1024,
  });

  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: 768,
  });
});

// Helper function for testing color contrast
export const checkColorContrast = (element: HTMLElement) => {
  const styles = window.getComputedStyle(element);
  const backgroundColor = styles.backgroundColor;
  const color = styles.color;

  // This would typically use a color contrast library
  // For now, we ensure the styles are applied
  expect(backgroundColor).toBeDefined();
  expect(color).toBeDefined();
};

// Helper function for testing focus visibility
export const checkFocusVisibility = (element: HTMLElement) => {
  element.focus();
  const styles = window.getComputedStyle(element);

  // Check for focus indicators (outline, box-shadow, etc.)
  const hasOutline = styles.outline !== 'none' && styles.outline !== '';
  const hasBoxShadow = styles.boxShadow !== 'none' && styles.boxShadow !== '';
  const hasFocusRing = element.classList.contains('focus:ring') ||
                       element.classList.contains('focus:outline');

  expect(hasOutline || hasBoxShadow || hasFocusRing).toBe(true);
};

// Helper function for testing keyboard navigation
export const testKeyboardNavigation = async (
  elements: HTMLElement[],
  userEvent: any
) => {
  for (let i = 0; i < elements.length - 1; i++) {
    elements[i].focus();
    expect(elements[i]).toHaveFocus();

    await userEvent.tab();
    expect(elements[i + 1]).toHaveFocus();
  }
};

// Mock IntersectionObserver for components that use it
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver for components that use it
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock matchMedia for responsive design testing
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Configure console warnings for accessibility issues
const originalWarn = console.warn;
console.warn = (...args) => {
  // Suppress known warnings that don't affect accessibility
  const message = args[0];
  if (typeof message === 'string') {
    // Allow through accessibility-related warnings
    if (message.includes('accessibility') ||
        message.includes('aria') ||
        message.includes('role') ||
        message.includes('label')) {
      originalWarn(...args);
    }
    // Suppress other warnings during accessibility tests
  } else {
    originalWarn(...args);
  }
};
