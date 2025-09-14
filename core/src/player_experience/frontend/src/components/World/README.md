# World Selection Components

This directory contains the React components for world selection and customization functionality.

## Components

### WorldDetailsModal
- **Purpose**: Displays detailed information about a selected world
- **Features**:
  - World preview and description
  - Therapeutic themes and approaches
  - Prerequisites and compatibility analysis
  - Customization options overview
  - Character compatibility scoring

### WorldCustomizationModal
- **Purpose**: Allows players to customize world parameters before selection
- **Features**:
  - Therapeutic intensity selection (LOW, MEDIUM, HIGH)
  - Narrative style options (GUIDED, EXPLORATORY, STRUCTURED)
  - Pacing controls (SLOW, MODERATE, FAST)
  - Interaction frequency settings (MINIMAL, REGULAR, FREQUENT)
  - Character-based recommendations
  - Experience preview generation

## Enhanced WorldSelection Page

The main WorldSelection page has been enhanced with:

### Search and Filtering
- **Search Bar**: Full-text search across world names, descriptions, and themes
- **Difficulty Filter**: Filter by BEGINNER, INTERMEDIATE, ADVANCED levels
- **Theme Filter**: Filter by therapeutic themes (dynamically populated)
- **Duration Filter**: Filter by estimated completion time
- **Clear Filters**: Reset all filters and search terms

### World Browser
- **Grid Layout**: Responsive card-based layout for world display
- **Compatibility Indicators**: Visual compatibility scores when character is selected
- **Sorting**: Automatic sorting by compatibility score when character is available
- **World Count**: Display of filtered results count

### Interactive Features
- **View Details**: Opens detailed world information modal
- **Customize**: Opens world parameter customization modal
- **Select World**: Initiates world selection with custom parameters

## Testing

Comprehensive test suites have been created for all components:

### WorldDetailsModal Tests
- Renders world details correctly
- Shows compatibility analysis
- Handles missing optional fields
- Manages modal state properly

### WorldCustomizationModal Tests
- Parameter selection functionality
- Character-based recommendations
- Preview generation
- Reset to recommended values

### WorldSelection Integration Tests
- Search and filtering functionality
- Empty states and loading states
- Character selection requirements
- Modal integration

## Requirements Fulfilled

This implementation fulfills the task requirements:

1. ✅ **World browser with filtering and search functionality**
   - Full-text search across multiple fields
   - Multiple filter categories (difficulty, theme, duration)
   - Dynamic theme filtering based on available worlds
   - Clear filters functionality

2. ✅ **World details view with compatibility indicators**
   - Comprehensive world details modal
   - Character compatibility scoring and analysis
   - Visual compatibility indicators with color coding
   - Prerequisites and therapeutic approach information

3. ✅ **World customization interface for parameters**
   - Dedicated customization modal
   - Four parameter categories with detailed options
   - Character-based recommendations
   - Experience preview functionality

4. ✅ **Unit tests for world selection components**
   - Comprehensive test coverage for all components
   - Integration tests for the main WorldSelection page
   - Mock implementations for API calls
   - Edge case and error state testing

## Technical Implementation

### State Management
- Redux Toolkit slices for world, character, and player state
- Async thunks for API integration
- Proper error handling and loading states

### TypeScript Integration
- Fully typed components and interfaces
- Type-safe Redux state management
- Proper prop typing for all components

### Accessibility
- WCAG compliant modal implementations
- Keyboard navigation support
- Screen reader friendly markup
- Focus management for modals

### Performance
- Memoized filtering and search logic
- Efficient re-rendering with proper dependency arrays
- Optimized component structure

## Usage

```tsx
import WorldSelection from './pages/WorldSelection/WorldSelection';
import { WorldDetailsModal, WorldCustomizationModal } from './components/World';

// The WorldSelection page handles all the integration automatically
// Modals are managed internally with proper state management
```

## Dependencies

- React 18+
- Redux Toolkit
- React Router DOM
- TypeScript
- Tailwind CSS
- Testing Library (React)
