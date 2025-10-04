# Visual Regression Testing for TherapeuticGoalsSelector

This directory contains comprehensive visual regression tests for the TherapeuticGoalsSelector component, ensuring consistent UI/UX across different states, viewports, and browsers.

## 🎯 **Overview**

Visual regression testing automatically detects unintended visual changes in the TherapeuticGoalsSelector component by comparing screenshots across different test runs. This ensures that:

- UI components render consistently across browsers and viewports
- Visual changes are intentional and reviewed
- Therapeutic interface maintains professional appearance
- Accessibility visual indicators remain intact
- Responsive design works correctly

## 🛠️ **Setup**

### Prerequisites
- Node.js 22.19.0 LTS (managed via nvm)
- Storybook 8.6.14 running on port 6006
- Playwright browsers installed

### Installation
```bash
# Install visual regression testing dependencies (already done)
npm install --save-dev @storybook/test-runner chromatic --legacy-peer-deps

# Install Playwright browsers
npx playwright install
```

## 🚀 **Usage**

### Running Visual Regression Tests

```bash
# Run all visual regression tests
npm run test:visual

# Run with browser UI (headed mode)
npm run test:visual:headed

# Debug mode with step-by-step execution
npm run test:visual:debug

# Update baseline screenshots (after intentional changes)
npm run test:visual:update

# View test results report
npm run test:visual:report
```

### Running Storybook Test Runner

```bash
# Start Storybook first
npm run storybook

# In another terminal, run Storybook tests
npm run test:storybook
```

### Chromatic Integration (Cloud-based)

```bash
# Run Chromatic visual regression tests
npm run chromatic

# Note: Requires CHROMATIC_PROJECT_TOKEN environment variable
```

## 📁 **Test Structure**

```
tests/visual-regression/
├── README.md                                    # This file
├── global-setup.ts                             # Global test setup
├── TherapeuticGoalsSelector.visual.spec.ts     # Main visual tests
└── screenshots/                                # Baseline screenshots
    ├── Desktop Chrome/
    ├── Desktop Firefox/
    ├── Desktop Safari/
    ├── Mobile Chrome/
    ├── Mobile Safari/
    └── Tablet/
```

## 🧪 **Test Coverage**

### Component States Tested
- ✅ Default state (empty selections)
- ✅ With selected therapeutic goals
- ✅ With selected primary concerns
- ✅ With custom entries
- ✅ Maximum selections reached
- ✅ Interactive states (hover, focus)
- ✅ Tab navigation states

### Viewports Tested
- ✅ Desktop (1200x800)
- ✅ Large Desktop (1920x1080)
- ✅ Tablet (768x1024)
- ✅ Mobile (375x667)

### Browsers Tested
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari/WebKit

## 🔧 **Configuration**

### Playwright Visual Config (`playwright-visual.config.ts`)
- **Threshold**: 20% pixel difference allowed
- **Max Diff Pixels**: 1000 pixels maximum difference
- **Animation Handling**: Disabled for consistency
- **Retry Logic**: 2 retries on CI, 0 locally
- **Parallel Execution**: Disabled on CI for consistency

### Test Runner Config (`.storybook/test-runner.ts`)
- **Viewport**: Standardized to 1200x800
- **Animation Disabling**: CSS-based animation suppression
- **Font Loading**: Waits for networkidle state
- **Screenshot Options**: Focused on story element only

## 📊 **Interpreting Results**

### Successful Tests
- ✅ Green checkmarks indicate visual consistency
- Screenshots match baseline within threshold

### Failed Tests
- ❌ Red X indicates visual differences detected
- Diff images show exact pixel differences
- Review changes to determine if intentional

### Updating Baselines
```bash
# After reviewing and approving visual changes
npm run test:visual:update
```

## 🔄 **CI/CD Integration**

Visual regression tests are integrated into the GitHub Actions workflow:

```yaml
- name: Run visual regression tests
  run: |
    npm run storybook &
    sleep 30
    npm run test:visual
```

## 🎨 **Chromatic Integration**

For advanced visual regression testing with team collaboration:

1. **Setup Chromatic Account**
   - Visit [chromatic.com](https://chromatic.com)
   - Connect GitHub repository
   - Get project token

2. **Configure Environment**
   ```bash
   export CHROMATIC_PROJECT_TOKEN=your_token_here
   ```

3. **Run Chromatic Tests**
   ```bash
   npm run chromatic
   ```

## 🐛 **Troubleshooting**

### Common Issues

**Storybook not starting**
```bash
# Check if port 6006 is available
lsof -i :6006
# Kill process if needed
kill -9 <PID>
```

**Flaky visual tests**
- Increase wait times in global-setup.ts
- Check for dynamic content or animations
- Verify font loading completion

**Screenshot differences**
- Check for OS-specific font rendering
- Verify browser versions match
- Review animation disabling effectiveness

### Debug Mode
```bash
# Run single test in debug mode
npx playwright test TherapeuticGoalsSelector.visual.spec.ts --debug
```

## 📈 **Best Practices**

1. **Consistent Environment**
   - Use same OS/browser versions
   - Disable animations completely
   - Wait for font loading

2. **Meaningful Baselines**
   - Update baselines only after review
   - Document visual changes in commits
   - Test across all supported viewports

3. **Efficient Testing**
   - Focus on critical visual states
   - Use appropriate thresholds
   - Group related visual tests

## 🎯 **Success Criteria**

- ✅ All visual regression tests pass consistently
- ✅ Screenshots captured for all component states
- ✅ Cross-browser visual consistency verified
- ✅ Responsive design validated across viewports
- ✅ CI/CD integration working smoothly
- ✅ Team workflow established for visual changes
