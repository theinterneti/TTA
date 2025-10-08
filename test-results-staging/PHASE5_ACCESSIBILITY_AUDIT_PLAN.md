# Phase 5: Accessibility Audit - Comprehensive Plan

**Plan Date:** 2025-10-06
**Environment:** TTA Staging (Homelab)
**Standards:** WCAG 2.1 Level AA
**Tools:** axe DevTools, Lighthouse, WAVE, Keyboard Testing
**Status:** 📋 PLANNING COMPLETE - READY FOR EXECUTION

---

## Executive Summary

This document outlines a comprehensive accessibility audit plan for the TTA staging environment. The plan focuses on validating **WCAG 2.1 Level AA compliance** and ensuring the application is usable by people with disabilities.

**Accessibility Goals:**
- WCAG 2.1 Level AA compliance
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance
- Focus management

---

## 1. Accessibility Audit Objectives

### 1.1 Primary Objectives

1. **Validate WCAG 2.1 Level AA Compliance**
   - Perceivable: Content is presentable to all users
   - Operable: UI components are operable by all users
   - Understandable: Information and UI are understandable
   - Robust: Content works with assistive technologies

2. **Test Keyboard Navigation**
   - All interactive elements accessible via keyboard
   - Logical tab order
   - Visible focus indicators
   - No keyboard traps

3. **Validate Screen Reader Compatibility**
   - Proper semantic HTML
   - ARIA labels and roles
   - Alt text for images
   - Form labels and instructions

4. **Assess Color Contrast**
   - Text meets contrast ratios
   - Interactive elements are distinguishable
   - Color is not the only means of conveying information

---

## 2. Accessibility Testing Tools

### 2.1 Automated Testing Tools

#### axe DevTools

**Installation:**
```bash
# Install axe-core (already in node_modules)
npm install --save-dev @axe-core/playwright
```

**Usage in Playwright:**
```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('accessibility test', async ({ page }) => {
  await page.goto('/dashboard');

  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

#### Lighthouse

**Usage:**
```bash
lighthouse http://localhost:3001 --only-categories=accessibility --output html --output-path ./test-results-staging/lighthouse-accessibility.html
```

#### WAVE (Web Accessibility Evaluation Tool)

**Usage:**
- Browser extension: https://wave.webaim.org/extension/
- Online tool: https://wave.webaim.org/

### 2.2 Manual Testing Tools

#### Keyboard Navigation

**Test with:**
- Tab key (forward navigation)
- Shift+Tab (backward navigation)
- Enter/Space (activate buttons/links)
- Arrow keys (navigate lists/menus)
- Escape (close modals/dialogs)

#### Screen Readers

**Test with:**
- NVDA (Windows) - Free
- JAWS (Windows) - Commercial
- VoiceOver (macOS) - Built-in
- TalkBack (Android) - Built-in
- ChromeVox (Chrome) - Extension

---

## 3. WCAG 2.1 Level AA Criteria

### 3.1 Perceivable

#### 1.1 Text Alternatives
- ✅ All images have alt text
- ✅ Decorative images have empty alt=""
- ✅ Icons have aria-label or title

#### 1.2 Time-based Media
- ⚠️ N/A (no video/audio content)

#### 1.3 Adaptable
- ✅ Semantic HTML structure
- ✅ Proper heading hierarchy (h1 → h2 → h3)
- ✅ Form labels associated with inputs
- ✅ Tables have proper headers

#### 1.4 Distinguishable
- ✅ Color contrast ratio ≥4.5:1 for normal text
- ✅ Color contrast ratio ≥3:1 for large text
- ✅ Color not sole means of conveying information
- ✅ Text can be resized to 200% without loss of content

### 3.2 Operable

#### 2.1 Keyboard Accessible
- ✅ All functionality available via keyboard
- ✅ No keyboard traps
- ✅ Keyboard shortcuts don't conflict

#### 2.2 Enough Time
- ✅ No time limits (or adjustable)
- ✅ Auto-updating content can be paused

#### 2.3 Seizures and Physical Reactions
- ✅ No flashing content >3 times per second

#### 2.4 Navigable
- ✅ Skip links to main content
- ✅ Page titles are descriptive
- ✅ Focus order is logical
- ✅ Link purpose is clear from context
- ✅ Multiple ways to find pages (nav, search)
- ✅ Headings and labels are descriptive
- ✅ Focus indicator is visible

#### 2.5 Input Modalities
- ✅ Pointer gestures have keyboard alternatives
- ✅ Pointer cancellation available
- ✅ Label in name matches accessible name

### 3.3 Understandable

#### 3.1 Readable
- ✅ Language of page is identified (lang attribute)
- ✅ Language of parts is identified (if different)

#### 3.2 Predictable
- ✅ Focus doesn't cause unexpected context changes
- ✅ Input doesn't cause unexpected context changes
- ✅ Navigation is consistent across pages
- ✅ Components are identified consistently

#### 3.3 Input Assistance
- ✅ Error messages are clear and helpful
- ✅ Labels and instructions provided for inputs
- ✅ Error suggestions provided
- ✅ Error prevention for critical actions

### 3.4 Robust

#### 4.1 Compatible
- ✅ Valid HTML (no parsing errors)
- ✅ Name, role, value available for UI components
- ✅ Status messages can be programmatically determined

---

## 4. Test Scenarios

### 4.1 Scenario 1: Keyboard Navigation Test

**Objective:** Validate all interactive elements are keyboard accessible

**Test Steps:**
1. Navigate to each page using only keyboard
2. Tab through all interactive elements
3. Verify focus indicators are visible
4. Verify tab order is logical
5. Activate buttons/links with Enter/Space
6. Close modals with Escape

**Pages to Test:**
- Login page
- Dashboard
- Characters page
- Worlds page
- Settings page
- Gameplay page

**Success Criteria:**
- ✅ All interactive elements reachable via Tab
- ✅ Focus indicators clearly visible
- ✅ Tab order follows visual layout
- ✅ No keyboard traps
- ✅ All actions performable via keyboard

### 4.2 Scenario 2: Screen Reader Test

**Objective:** Validate content is accessible to screen reader users

**Test Steps:**
1. Enable screen reader (NVDA/VoiceOver)
2. Navigate through each page
3. Verify all content is announced
4. Verify form labels are read correctly
5. Verify button purposes are clear
6. Verify error messages are announced

**Elements to Test:**
- Page titles
- Headings
- Links and buttons
- Form inputs and labels
- Error messages
- Status updates
- Modal dialogs

**Success Criteria:**
- ✅ All content announced correctly
- ✅ Form labels associated with inputs
- ✅ Button purposes clear
- ✅ Error messages announced
- ✅ Status updates announced

### 4.3 Scenario 3: Color Contrast Test

**Objective:** Validate color contrast meets WCAG AA standards

**Test Steps:**
1. Use axe DevTools to scan for contrast issues
2. Manually check with contrast checker
3. Test with different color blindness simulations
4. Verify information not conveyed by color alone

**Elements to Test:**
- Body text
- Headings
- Links
- Buttons
- Form inputs
- Error messages
- Status indicators

**Success Criteria:**
- ✅ Normal text: ≥4.5:1 contrast ratio
- ✅ Large text: ≥3:1 contrast ratio
- ✅ UI components: ≥3:1 contrast ratio
- ✅ Information not color-dependent

### 4.4 Scenario 4: Form Accessibility Test

**Objective:** Validate forms are accessible and usable

**Test Steps:**
1. Navigate forms with keyboard only
2. Verify labels are associated with inputs
3. Verify error messages are clear
4. Verify required fields are indicated
5. Test with screen reader

**Forms to Test:**
- Login form
- Character creation form
- API key input form
- Settings forms

**Success Criteria:**
- ✅ Labels associated with inputs
- ✅ Required fields indicated
- ✅ Error messages clear and helpful
- ✅ Keyboard accessible
- ✅ Screen reader compatible

### 4.5 Scenario 5: Modal Dialog Accessibility Test

**Objective:** Validate modals are accessible

**Test Steps:**
1. Open modal with keyboard
2. Verify focus moves to modal
3. Verify focus trapped in modal
4. Close modal with Escape
5. Verify focus returns to trigger element

**Modals to Test:**
- API key input modal
- Character creation modal
- Confirmation dialogs

**Success Criteria:**
- ✅ Focus moves to modal on open
- ✅ Focus trapped in modal
- ✅ Escape closes modal
- ✅ Focus returns to trigger on close
- ✅ Modal announced by screen reader

---

## 5. Accessibility Issues to Check

### 5.1 Common Issues

1. **Missing Alt Text**
   - Images without alt attributes
   - Decorative images with descriptive alt text

2. **Poor Color Contrast**
   - Text too light on light background
   - Buttons with insufficient contrast

3. **Missing Form Labels**
   - Inputs without associated labels
   - Placeholder text used as labels

4. **Keyboard Traps**
   - Focus stuck in modal
   - Cannot escape dropdown menu

5. **Missing Focus Indicators**
   - No visible focus outline
   - Focus outline removed with CSS

6. **Improper Heading Structure**
   - Skipping heading levels (h1 → h3)
   - Multiple h1 elements on page

7. **Missing ARIA Labels**
   - Icon buttons without labels
   - Complex widgets without roles

8. **Inaccessible Modals**
   - Focus not trapped
   - Cannot close with Escape
   - Focus not returned on close

---

## 6. Automated Accessibility Testing

### 6.1 Playwright + axe-core Integration

**Test Script:**
```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const pages = [
  { name: 'Login', url: '/login' },
  { name: 'Dashboard', url: '/dashboard' },
  { name: 'Characters', url: '/characters' },
  { name: 'Worlds', url: '/worlds' },
  { name: 'Settings', url: '/settings' },
];

for (const page of pages) {
  test(`${page.name} page accessibility`, async ({ page: pw }) => {
    await pw.goto(page.url);

    const accessibilityScanResults = await new AxeBuilder({ page: pw })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    // Log violations
    if (accessibilityScanResults.violations.length > 0) {
      console.log(`\n${page.name} Accessibility Violations:`);
      accessibilityScanResults.violations.forEach(violation => {
        console.log(`- ${violation.id}: ${violation.description}`);
        console.log(`  Impact: ${violation.impact}`);
        console.log(`  Nodes: ${violation.nodes.length}`);
      });
    }

    // Fail test if critical violations found
    const criticalViolations = accessibilityScanResults.violations.filter(
      v => v.impact === 'critical' || v.impact === 'serious'
    );

    expect(criticalViolations).toEqual([]);
  });
}
```

### 6.2 Lighthouse Accessibility Audit

**Command:**
```bash
# Run Lighthouse accessibility audit on all pages
for page in login dashboard characters worlds settings; do
  lighthouse "http://localhost:3001/$page" \
    --only-categories=accessibility \
    --output html \
    --output-path "./test-results-staging/lighthouse-accessibility-$page.html"
done
```

---

## 7. Manual Accessibility Testing Checklist

### 7.1 Keyboard Navigation Checklist

- [ ] All interactive elements reachable via Tab
- [ ] Tab order is logical and follows visual layout
- [ ] Focus indicators are clearly visible
- [ ] Shift+Tab moves focus backward
- [ ] Enter/Space activates buttons and links
- [ ] Escape closes modals and dropdowns
- [ ] Arrow keys navigate lists and menus
- [ ] No keyboard traps

### 7.2 Screen Reader Checklist

- [ ] Page title is descriptive
- [ ] Headings are properly structured (h1 → h2 → h3)
- [ ] All images have appropriate alt text
- [ ] Form labels are associated with inputs
- [ ] Error messages are announced
- [ ] Status updates are announced
- [ ] Buttons have clear purposes
- [ ] Links have descriptive text

### 7.3 Color Contrast Checklist

- [ ] Body text meets 4.5:1 contrast ratio
- [ ] Large text meets 3:1 contrast ratio
- [ ] Buttons meet 3:1 contrast ratio
- [ ] Form inputs meet 3:1 contrast ratio
- [ ] Error messages meet 4.5:1 contrast ratio
- [ ] Information not conveyed by color alone

### 7.4 Form Accessibility Checklist

- [ ] All inputs have associated labels
- [ ] Required fields are indicated
- [ ] Error messages are clear and helpful
- [ ] Error messages are associated with inputs
- [ ] Placeholder text is not used as labels
- [ ] Forms are keyboard accessible

---

## 8. Accessibility Violations Report Template

**Violation Report:**

```markdown
# Accessibility Violations Report

**Page:** [Page Name]
**Date:** [Date]
**Tool:** [Tool Name]

## Critical Violations

### Violation 1: [Violation ID]
- **Description:** [Description]
- **Impact:** Critical
- **WCAG Criterion:** [Criterion]
- **Element:** [Element selector]
- **Recommendation:** [How to fix]

## Serious Violations

### Violation 2: [Violation ID]
- **Description:** [Description]
- **Impact:** Serious
- **WCAG Criterion:** [Criterion]
- **Element:** [Element selector]
- **Recommendation:** [How to fix]

## Moderate Violations

[List moderate violations]

## Minor Violations

[List minor violations]

## Summary

- **Total Violations:** [Number]
- **Critical:** [Number]
- **Serious:** [Number]
- **Moderate:** [Number]
- **Minor:** [Number]
```

---

## 9. Remediation Recommendations

### 9.1 Quick Wins (Easy to Fix)

1. **Add Alt Text to Images**
   ```html
   <img src="logo.png" alt="TTA Logo">
   ```

2. **Associate Labels with Inputs**
   ```html
   <label for="username">Username</label>
   <input id="username" name="username" type="text">
   ```

3. **Add ARIA Labels to Icon Buttons**
   ```html
   <button aria-label="Close modal">
     <CloseIcon />
   </button>
   ```

4. **Improve Focus Indicators**
   ```css
   button:focus {
     outline: 2px solid #0066cc;
     outline-offset: 2px;
   }
   ```

### 9.2 Medium Effort Fixes

1. **Implement Keyboard Navigation**
   - Add keyboard event handlers
   - Manage focus programmatically
   - Implement focus trapping in modals

2. **Improve Color Contrast**
   - Adjust color palette
   - Use darker text colors
   - Increase button contrast

3. **Add Skip Links**
   ```html
   <a href="#main-content" class="skip-link">Skip to main content</a>
   ```

### 9.3 High Effort Fixes

1. **Refactor to Semantic HTML**
   - Replace divs with semantic elements
   - Use proper heading structure
   - Use lists for navigation

2. **Implement ARIA Patterns**
   - Add ARIA roles and properties
   - Implement live regions
   - Add ARIA descriptions

---

## 10. Deliverables

### 10.1 Reports to Generate

1. **Automated Accessibility Report**
   - axe-core scan results
   - Lighthouse accessibility scores
   - WAVE scan results

2. **Manual Testing Report**
   - Keyboard navigation results
   - Screen reader testing results
   - Color contrast analysis

3. **Violations Report**
   - List of all violations
   - Severity ratings
   - Remediation recommendations

4. **Remediation Plan**
   - Prioritized list of fixes
   - Effort estimates
   - Implementation timeline

---

## 11. Conclusion

This accessibility audit plan provides a comprehensive framework for validating WCAG 2.1 Level AA compliance. The plan covers **automated testing**, **manual testing**, and **remediation recommendations**.

**Status:** 📋 **PLANNING COMPLETE** - Ready for execution.

**Next Steps:**
1. Run automated accessibility tests
2. Perform manual keyboard navigation testing
3. Test with screen readers (if available)
4. Generate violations report
5. Create remediation plan

---

**Plan Created:** 2025-10-06
**Created By:** The Augster (AI Development Assistant)
**Phase 5 Status:** ✅ PLANNING COMPLETE
