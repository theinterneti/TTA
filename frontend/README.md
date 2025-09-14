# TTA Therapeutic Gaming - Frontend Application 🎮💚

Welcome to the **Therapeutic Technology Assistant (TTA)** frontend application—a React-based therapeutic gaming platform that provides mental health support through interactive digital experiences.

## 🌟 About This Application

TTA is a **therapeutic intervention platform** that uses gaming experiences to support individuals dealing with mental health challenges. This frontend application provides:

- **Secure Patient Authentication** with therapeutic context
- **Interactive Therapeutic Characters** for emotional support
- **Calming Virtual Environments** for therapeutic activities
- **Progress Tracking** for therapeutic goals and milestones
- **Crisis Support Integration** with immediate intervention capabilities
- **HIPAA-Compliant** data handling and privacy protection

## 🚀 Getting Started

### New Developer? Start Here!

**👋 First Time Setup:**
1. Read the [**Complete Onboarding Guide**](./ONBOARDING_GUIDE.md) (30-45 minutes)
2. Follow the [**Quick Start Guide**](./QUICK_START.md) (5 minutes)
3. Explore the [**Documentation Hub**](./docs/README.md)

**⚡ Quick Setup:**
```bash
# Install dependencies
npm install

# Start development server
npm start

# Verify at http://localhost:3000
```

## 📚 Documentation Hub

**Complete documentation available at:** [`./docs/`](./docs/)

### Essential Documentation
- **📖 [Main Documentation Hub](./docs/README.md)** - Complete project overview
- **🛠️ [Development Setup](./docs/DEVELOPMENT_SETUP.md)** - Environment configuration
- **⚡ [API Quick Reference](./docs/API_QUICK_REFERENCE.md)** - Common endpoints
- **📋 [Documentation Summary](./docs/DOCUMENTATION_SUMMARY.md)** - Implementation overview

### Specialized Documentation
- **🔌 [API Documentation](./docs/api/)** - Complete endpoint specifications
- **🎨 [Design System](./docs/design-system/)** - UI/UX guidelines
- **🧠 [Business Logic](./docs/business-logic/)** - Therapeutic workflows
- **📊 [Data Models](./docs/data-models/)** - TypeScript interfaces
- **🔗 [Integration](./docs/integration/)** - Service integration protocols
- **🛡️ [Therapeutic Content](./docs/therapeutic-content/)** - Safety guidelines
- **🧪 [Testing](./docs/testing/)** - Testing specifications

## 🏗️ Application Architecture

### Technology Stack
- **React 18** with TypeScript for type safety
- **Material-UI (MUI)** for therapeutic-themed components
- **Redux Toolkit** for state management
- **React Router** for navigation
- **Axios** for API communication
- **WebSocket** for real-time character interactions

### Project Structure
```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── common/       # Shared components (CrisisSupport, NavigationBar)
│   │   └── therapeutic/  # Therapeutic-specific components
│   ├── pages/            # Page components (Login, Dashboard, etc.)
│   ├── store/            # Redux store and slices
│   │   └── slices/       # Redux slices (auth, characters, worlds, etc.)
│   ├── services/         # API services and utilities
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── hooks/            # Custom React hooks
│   └── styles/           # Global styles and themes
├── docs/                 # Complete documentation hub
├── tests/                # Test files
└── package.json
```

### Key Components
- **`App.tsx`** - Main application with routing and authentication
- **`CrisisSupport.tsx`** - Always-available crisis intervention
- **`NavigationBar.tsx`** - Main navigation with user context
- **`Dashboard.tsx`** - Patient dashboard with progress visualization
- **`CharacterStudio.tsx`** - Therapeutic character interaction
- **`LoginPage.tsx`** - Secure authentication with therapeutic context

## 🚨 Critical Requirements

### 🛡️ Patient Safety (HIGHEST PRIORITY)
- **Crisis Support**: Accessible within 2 clicks from any screen
- **Crisis Detection**: Monitor for concerning patterns
- **Emergency Resources**: Immediate access to hotlines (988, 741741)
- **Audit Trails**: Log all crisis-related interactions

### 🔐 HIPAA Compliance
- **No Sensitive Logging**: Never log patient data
- **Secure Storage**: Encrypted authentication tokens
- **Data Minimization**: Only necessary therapeutic data
- **Access Controls**: Proper authentication and authorization

### ♿ Accessibility (WCAG 2.1 AA)
- **Keyboard Navigation**: All interactive elements accessible
- **Screen Reader Support**: Proper ARIA labels and semantic HTML
- **Color Contrast**: Minimum 4.5:1 ratio for normal text
- **Focus Management**: Clear indicators and logical tab order

### 🎯 Therapeutic Effectiveness
- **Evidence-Based Design**: Follow therapeutic intervention patterns
- **Progress Measurement**: Track therapeutic goal advancement
- **Personalization**: Adapt to individual therapeutic needs
- **Clinical Integration**: Support clinical team oversight

## 🧪 Testing & Quality Assurance

### Running Tests
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run accessibility tests
npm run test:a11y

# Run linting
npm run lint

# Type checking
npm run type-check
```

### Testing Requirements
- **Unit Tests**: All components must have test coverage
- **Integration Tests**: Test therapeutic workflows end-to-end
- **Accessibility Tests**: Automated WCAG compliance checking
- **Crisis Scenario Tests**: Verify emergency intervention flows

### Quality Gates
All code must pass:
- ✅ TypeScript compilation without errors
- ✅ ESLint rules for code quality
- ✅ Unit test coverage > 80%
- ✅ Accessibility compliance (WCAG 2.1 AA)
- ✅ Crisis support functionality verification

## 🔧 Development Workflow

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/crisis-support-enhancement

# Make changes and test
npm test
npm run test:a11y
npm run lint

# Commit with descriptive message
git commit -m "feat: enhance crisis support accessibility"

# Push and create PR
git push origin feature/crisis-support-enhancement
```

### Branch Naming Conventions
- `feature/` - New features
- `fix/` - Bug fixes
- `therapeutic/` - Therapeutic workflow improvements
- `accessibility/` - Accessibility enhancements
- `crisis/` - Crisis support related changes

## 🌐 Environment Configuration

### Environment Variables
Create `.env.local` file:
```bash
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8080/api
REACT_APP_WS_URL=ws://localhost:8080/ws

# Crisis Support
REACT_APP_CRISIS_HOTLINE=988
REACT_APP_CRISIS_TEXT=741741

# Feature Flags
REACT_APP_ENABLE_MOCK_DATA=true
REACT_APP_ENABLE_CRISIS_SIMULATION=false

# Development
REACT_APP_LOG_LEVEL=debug
REACT_APP_ENABLE_REDUX_DEVTOOLS=true
```

## 📊 Available Scripts

```bash
npm start              # Start development server
npm test               # Run test suite
npm run build          # Build for production
npm run lint           # Run ESLint
npm run format         # Format code with Prettier
npm run type-check     # TypeScript type checking
npm run test:a11y      # Accessibility testing
npm run test:coverage  # Test coverage report
npm run analyze        # Bundle size analysis
```

## 🆘 Crisis Support Resources

**Always Available:**
- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **Emergency Services**: 911

**In Application:**
- Crisis support button visible on all screens
- Immediate access to crisis resources
- Real-time crisis detection and intervention

## 📞 Support & Resources

### Getting Help
1. **Documentation**: Check [`./docs/`](./docs/) for comprehensive guides
2. **API Issues**: Review [`./docs/API_QUICK_REFERENCE.md`](./docs/API_QUICK_REFERENCE.md)
3. **Therapeutic Questions**: Consult [`./docs/therapeutic-content/`](./docs/therapeutic-content/)
4. **Development Setup**: Follow [`./docs/DEVELOPMENT_SETUP.md`](./docs/DEVELOPMENT_SETUP.md)

### Escalation Priorities
- **🚨 Crisis Support Issues**: Immediate escalation required
- **🔐 Security Concerns**: Report HIPAA compliance issues immediately
- **♿ Accessibility Blockers**: High priority for patient access
- **🎯 Therapeutic Effectiveness**: Consult clinical team for guidance

## 🌟 Contributing

### Before Contributing
1. Read the [Onboarding Guide](./ONBOARDING_GUIDE.md)
2. Understand therapeutic requirements in [`./docs/therapeutic-content/`](./docs/therapeutic-content/)
3. Review accessibility standards in [`./docs/design-system/`](./docs/design-system/)
4. Familiarize yourself with crisis support protocols

### Code Standards
- **Patient Safety First**: Every change must consider patient well-being
- **Accessibility Required**: WCAG 2.1 AA compliance is mandatory
- **Therapeutic Focus**: Features must support mental health goals
- **Quality Assurance**: All tests must pass before merging

---

## 🎯 Mission Statement

**We build technology that heals.** Every line of code in this application has the potential to provide comfort, support, and therapeutic intervention to individuals facing mental health challenges. Your work directly contributes to improving lives and supporting healing journeys.

**Thank you for being part of this important mission.** 💚

---

*For questions about this application or the TTA project, please refer to the documentation in [`./docs/`](./docs/) or contact the development team.*
