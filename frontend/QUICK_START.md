# TTA Frontend - Quick Start Guide 🚀

**New to TTA?** Start with the [Full Onboarding Guide](./ONBOARDING_GUIDE.md) first!

## ⚡ 5-Minute Setup

```bash
# 1. Navigate to frontend directory
cd /home/thein/recovered-tta-storytelling/frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm start

# 4. Verify at http://localhost:3000
```

## 📚 Essential Reading (30 minutes)

**Read these files in order:**
1. [`./docs/README.md`](./docs/README.md) - Project overview & navigation
2. [`./docs/DEVELOPMENT_SETUP.md`](./docs/DEVELOPMENT_SETUP.md) - Environment setup
3. [`./docs/API_QUICK_REFERENCE.md`](./docs/API_QUICK_REFERENCE.md) - API endpoints

## 🚨 Critical Requirements

### Patient Safety (NON-NEGOTIABLE)
- ✅ Crisis support accessible within 2 clicks from any screen
- ✅ Never log sensitive patient data
- ✅ Test crisis workflows before any deployment

### Accessibility (WCAG 2.1 AA Required)
- ✅ Keyboard navigation for all interactive elements
- ✅ Screen reader compatibility with ARIA labels
- ✅ 4.5:1 minimum color contrast ratio

### HIPAA Compliance
- ✅ Encrypted storage for authentication tokens
- ✅ No patient data in console logs or error messages
- ✅ Secure API communication only

## 🎯 Development Phases

### Phase 1: Core Interface (Weeks 1-2)
- [ ] Authentication & session management
- [ ] Patient dashboard
- [ ] Crisis support integration

### Phase 2: Therapeutic Features (Weeks 3-4)
- [ ] Character interactions
- [ ] Session management
- [ ] Progress tracking

### Phase 3: Advanced Features (Weeks 5-6)
- [ ] Advanced therapeutic workflows
- [ ] Enhanced accessibility
- [ ] Crisis intervention protocols

## 🔧 Daily Workflow

```bash
# Before starting work
git pull origin main
npm test

# Before committing
npm run lint
npm run type-check
npm run test:a11y

# Create feature branch
git checkout -b feature/your-feature-name
```

## 📁 Key Directories

```
frontend/
├── src/
│   ├── components/common/    # Shared UI components
│   ├── pages/               # Page components
│   ├── store/               # Redux state management
│   └── types/               # TypeScript definitions
├── docs/                    # Complete documentation hub
│   ├── api/                # API specifications
│   ├── design-system/      # UI/UX guidelines
│   ├── therapeutic-content/ # Safety protocols
│   └── testing/            # Testing requirements
└── tests/                   # Test files
```

## 🆘 Crisis Support Resources

**Always Available:**
- National Suicide Prevention Lifeline: **988**
- Crisis Text Line: **Text HOME to 741741**
- Emergency Services: **911**

**In Code:**
```typescript
// Crisis support must be accessible from every component
import { CrisisSupport } from '../components/common/CrisisSupport';

// Always test crisis workflows
describe('Crisis Support', () => {
  it('should be accessible within 2 clicks', () => {
    // Test implementation
  });
});
```

## 🧪 Testing Checklist

```bash
# Run before every commit
npm test                 # Unit tests
npm run test:a11y       # Accessibility tests
npm run test:coverage   # Coverage report

# Manual testing required
- [ ] Crisis support button works from all pages
- [ ] Keyboard navigation functions properly
- [ ] Screen reader announces content correctly
- [ ] All forms validate properly
```

## 📞 Getting Help

### Documentation
- **Project Overview**: [`./docs/README.md`](./docs/README.md)
- **API Reference**: [`./docs/API_QUICK_REFERENCE.md`](./docs/API_QUICK_REFERENCE.md)
- **Therapeutic Guidelines**: [`./docs/therapeutic-content/`](./docs/therapeutic-content/)

### Common Issues
- **Build Errors**: Delete `node_modules`, run `npm install`
- **TypeScript Errors**: Restart TS server in VS Code
- **Test Failures**: Check for missing accessibility attributes

### Escalation
- **Crisis Support Issues**: Immediate escalation required
- **Security Concerns**: Report HIPAA compliance issues immediately
- **Accessibility Blockers**: High priority for patient access

## 🌟 Key Reminders

- **Patient Safety First**: Every decision prioritizes patient well-being
- **Accessibility is Essential**: Not optional—required for all users
- **Therapeutic Focus**: Features must support mental health goals
- **Your Impact Matters**: Your code helps heal and support people in need

---

**Ready to dive deeper?** Read the [Complete Onboarding Guide](./ONBOARDING_GUIDE.md) for comprehensive project understanding.

**Questions?** Check the documentation in [`./docs/`](./docs/) or reach out to the development team.
