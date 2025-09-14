# TTA Frontend Development Environment Setup

This guide will help you set up your development environment for building the TTA therapeutic gaming frontend.

## 📋 Prerequisites

### Required Software
- **Node.js**: Version 16.x or higher
- **npm**: Version 8.x or higher (comes with Node.js)
- **Git**: For version control
- **VS Code**: Recommended IDE with extensions

### Recommended VS Code Extensions
```json
{
  "recommendations": [
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml",
    "ms-vscode.vscode-markdown",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Navigate to the frontend directory
cd /home/thein/recovered-tta-storytelling/frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 2. Verify Installation
The development server should start on `http://localhost:3000`. You should see:
- ✅ Login page loads without errors
- ✅ Navigation works between pages
- ✅ No TypeScript compilation errors
- ✅ Crisis support button is visible

## 🔧 Environment Configuration

### Environment Variables
Create a `.env.local` file in the frontend root:

```bash
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8080/api
REACT_APP_WS_URL=ws://localhost:8080/ws

# Authentication
REACT_APP_JWT_SECRET=your-jwt-secret-here

# Crisis Support
REACT_APP_CRISIS_HOTLINE=988
REACT_APP_CRISIS_TEXT=741741

# Feature Flags
REACT_APP_ENABLE_MOCK_DATA=true
REACT_APP_ENABLE_CRISIS_SIMULATION=false
REACT_APP_ENABLE_ANALYTICS=false

# Development
REACT_APP_LOG_LEVEL=debug
REACT_APP_ENABLE_REDUX_DEVTOOLS=true
```

### TypeScript Configuration
The project uses strict TypeScript settings for therapeutic safety:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  }
}
```

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── common/       # Shared components
│   │   └── therapeutic/  # Therapeutic-specific components
│   ├── pages/            # Page components
│   ├── store/            # Redux store and slices
│   ├── services/         # API services
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── hooks/            # Custom React hooks
│   └── styles/           # Global styles and themes
├── docs/                 # Documentation (this directory)
├── tests/                # Test files
└── package.json
```

## 🎨 Styling and Theming

### Material-UI Theme
The project uses Material-UI with a therapeutic theme:

```typescript
// src/theme/therapeuticTheme.ts
export const therapeuticTheme = createTheme({
  palette: {
    primary: {
      main: '#4A90E2', // Calming blue
      light: '#7BB3F0',
      dark: '#2E5C8A'
    },
    secondary: {
      main: '#81C784', // Soothing green
      light: '#A5D6A7',
      dark: '#4CAF50'
    },
    background: {
      default: '#F8F9FA',
      paper: '#FFFFFF'
    }
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontWeight: 600 },
    h2: { fontWeight: 600 },
    body1: { lineHeight: 1.6 }
  }
});
```

### CSS Variables
```css
:root {
  --color-therapeutic-primary: #4A90E2;
  --color-therapeutic-secondary: #81C784;
  --color-crisis-alert: #F44336;
  --color-success: #4CAF50;
  --color-warning: #FF9800;
  
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  --border-radius: 8px;
  --shadow-light: 0 2px 4px rgba(0,0,0,0.1);
  --shadow-medium: 0 4px 8px rgba(0,0,0,0.15);
}
```

## 🧪 Testing Setup

### Test Configuration
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run accessibility tests
npm run test:a11y
```

### Test Structure
```
tests/
├── __mocks__/            # Mock files
├── components/           # Component tests
├── pages/               # Page tests
├── services/            # Service tests
├── utils/               # Utility tests
├── integration/         # Integration tests
└── accessibility/       # A11y tests
```

### Example Test
```typescript
// tests/components/CrisisSupport.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { CrisisSupport } from '../../src/components/common/CrisisSupport';

describe('CrisisSupport', () => {
  it('should display crisis resources when activated', () => {
    render(<CrisisSupport />);
    
    const crisisButton = screen.getByLabelText('Crisis Support');
    fireEvent.click(crisisButton);
    
    expect(screen.getByText('Crisis Support Resources')).toBeInTheDocument();
    expect(screen.getByText('988')).toBeInTheDocument();
  });
});
```

## 🔍 Debugging and Development Tools

### Redux DevTools
Enable Redux DevTools for state debugging:
```typescript
// src/store/store.ts
const store = configureStore({
  reducer: rootReducer,
  devTools: process.env.REACT_APP_ENABLE_REDUX_DEVTOOLS === 'true'
});
```

### React Developer Tools
Install the React Developer Tools browser extension for component debugging.

### Network Debugging
Use browser DevTools Network tab to monitor API calls:
- Check request/response formats
- Verify authentication headers
- Monitor WebSocket connections

## 🚨 Crisis Support Development

### Testing Crisis Scenarios
```typescript
// Enable crisis simulation in development
if (process.env.REACT_APP_ENABLE_CRISIS_SIMULATION === 'true') {
  // Add crisis simulation controls to dev UI
  window.simulateCrisis = (level: 'low' | 'medium' | 'high') => {
    store.dispatch(simulateCrisisEvent({ level }));
  };
}
```

### Crisis Support Checklist
- [ ] Crisis button always visible and accessible
- [ ] Crisis resources load within 2 seconds
- [ ] Crisis hotline numbers are correct
- [ ] Crisis detection algorithms are tested
- [ ] Emergency contact flows work properly

## 🔐 Security Development Practices

### Authentication Testing
```typescript
// Test authentication flows
describe('Authentication', () => {
  it('should redirect to login when token expires', async () => {
    // Mock expired token
    mockAuthService.mockExpiredToken();
    
    // Attempt authenticated action
    await userEvent.click(screen.getByText('View Profile'));
    
    // Should redirect to login
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});
```

### Data Protection
- Never log sensitive patient data
- Use secure storage for tokens
- Implement proper CORS policies
- Validate all user inputs

## 📊 Performance Monitoring

### Bundle Analysis
```bash
# Analyze bundle size
npm run build
npm run analyze

# Check for unused dependencies
npm run depcheck
```

### Performance Metrics
Monitor these key metrics:
- **First Contentful Paint**: < 2 seconds
- **Largest Contentful Paint**: < 3 seconds
- **Time to Interactive**: < 4 seconds
- **Cumulative Layout Shift**: < 0.1

## 🌐 Accessibility Development

### A11y Testing Tools
```bash
# Install accessibility testing tools
npm install --save-dev @axe-core/react jest-axe

# Run accessibility tests
npm run test:a11y
```

### A11y Checklist
- [ ] All interactive elements are keyboard accessible
- [ ] Color contrast ratios meet WCAG 2.1 AA standards
- [ ] Screen reader compatibility tested
- [ ] Focus management works properly
- [ ] ARIA labels are present and correct

## 🔄 Development Workflow

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/crisis-support-enhancement

# Make changes and commit
git add .
git commit -m "feat: enhance crisis support accessibility"

# Push and create PR
git push origin feature/crisis-support-enhancement
```

### Code Quality Checks
```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check

# Run all quality checks
npm run quality-check
```

## 📚 Additional Resources

### Documentation Links
- [API Quick Reference](./API_QUICK_REFERENCE.md)
- [Component Library](./design-system/)
- [Therapeutic Guidelines](./therapeutic-content/)
- [Testing Strategy](./testing/)

### External Resources
- [React Documentation](https://reactjs.org/docs)
- [Material-UI Documentation](https://mui.com/)
- [Redux Toolkit Documentation](https://redux-toolkit.js.org/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## 🆘 Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### TypeScript Errors
```bash
# Restart TypeScript service in VS Code
Ctrl+Shift+P -> "TypeScript: Restart TS Server"
```

#### WebSocket Connection Issues
```bash
# Check WebSocket URL in .env.local
REACT_APP_WS_URL=ws://localhost:8080/ws
```

### Getting Help
1. Check the [documentation](./README.md)
2. Review [API specifications](./api/)
3. Check existing [GitHub issues](https://github.com/tta-dev/issues)
4. Contact the development team

---

**Happy coding! Remember: Patient safety and therapeutic outcomes are our top priorities.** 🎯
