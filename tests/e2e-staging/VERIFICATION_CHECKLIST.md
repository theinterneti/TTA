# TTA Staging Environment Verification Checklist

Use this checklist to systematically verify your staging environment is ready for users.

## 🚀 Pre-Test Setup

### Environment Preparation

- [ ] **Docker Compose Running**
  ```bash
  docker-compose -f docker-compose.staging-homelab.yml ps
  # All containers should show "Up"
  ```

- [ ] **All Services Accessible**
  ```bash
  npm run staging:validate
  # All checks should pass with ✓
  ```

- [ ] **Environment Variables Set** (optional)
  ```bash
  # Copy and customize if needed
  cp .env.staging.testing.example .env.staging.testing
  ```

- [ ] **Playwright Installed**
  ```bash
  npx playwright install chromium
  ```

## 🧪 Automated Test Execution

### Run Complete Test Suite

- [ ] **Run Staging Tests**
  ```bash
  npm run test:staging
  ```
  - [ ] Test completes without errors
  - [ ] All 6 phases pass
  - [ ] Total time < 120 seconds
  - [ ] No console errors

- [ ] **Review HTML Report**
  ```bash
  npm run test:staging:report
  ```
  - [ ] All tests show green checkmarks
  - [ ] No failed assertions
  - [ ] Screenshots look correct (if any)
  - [ ] No unexpected warnings

## 👤 Manual User Journey Validation

### Phase 1: Landing & Authentication

- [ ] **Open Application**
  - Navigate to: http://localhost:3001
  - [ ] Page loads within 3 seconds
  - [ ] No console errors in browser DevTools
  - [ ] Page title is correct

- [ ] **Sign-in Discoverability**
  - [ ] Sign-in button/link is immediately visible
  - [ ] Button text is clear ("Sign in", "Login", etc.)
  - [ ] Button is properly styled and clickable
  - [ ] No confusing UI elements

- [ ] **Authentication Flow**
  - [ ] Click sign-in button
  - [ ] Login form appears or OAuth redirect happens
  - [ ] Demo credentials work: `demo_user` / `DemoPassword123!`
  - [ ] Authentication completes within 10 seconds
  - [ ] Redirects to dashboard automatically

### Phase 2: Dashboard & Orientation

- [ ] **Dashboard Loads**
  - [ ] Dashboard appears within 3 seconds
  - [ ] Welcome message is visible
  - [ ] User's name/info is displayed (if applicable)
  - [ ] No loading spinners stuck

- [ ] **Clear Next Steps**
  - [ ] Call-to-action buttons are visible
  - [ ] Button text is clear ("Create Character", "Start Adventure", etc.)
  - [ ] Navigation menu is intuitive
  - [ ] No dead-end states

### Phase 3: Character Creation

- [ ] **Navigate to Character Creation**
  - [ ] Click "Create Character" or similar button
  - [ ] Character creation page loads within 2 seconds
  - [ ] Form is displayed correctly

- [ ] **Form Usability**
  - [ ] All form fields are labeled clearly
  - [ ] Required fields are marked
  - [ ] Placeholder text is helpful
  - [ ] No confusing terminology

- [ ] **Create Character**
  - [ ] Fill in character name: "Test Character"
  - [ ] Fill in backstory (if required)
  - [ ] Submit form
  - [ ] Success message appears
  - [ ] Character is saved (no errors)
  - [ ] Redirects to next step

### Phase 4: World Selection

- [ ] **View Available Worlds**
  - [ ] World selection page loads within 3 seconds
  - [ ] Multiple worlds are displayed
  - [ ] Each world has clear description
  - [ ] World cards are visually appealing

- [ ] **World Information**
  - [ ] World names are clear
  - [ ] Descriptions are engaging
  - [ ] Difficulty/theme is indicated
  - [ ] Selection button is obvious

- [ ] **Select World**
  - [ ] Click "Select" or "Choose" button
  - [ ] World loads within 5 seconds
  - [ ] Transitions smoothly to chat

### Phase 5: Gameplay / Chat Interface

- [ ] **Chat Interface Loads**
  - [ ] Chat interface appears within 3 seconds
  - [ ] Message area is visible
  - [ ] Input field is accessible
  - [ ] Send button is present

- [ ] **Initial Story Content**
  - [ ] AI generates initial story within 10 seconds
  - [ ] Story content is engaging
  - [ ] Text is readable and well-formatted
  - [ ] No placeholder text or errors

- [ ] **User Interaction**
  - [ ] Type message: "I look around."
  - [ ] Send button is clickable
  - [ ] Message appears in chat
  - [ ] Loading indicator shows while waiting

- [ ] **AI Response**
  - [ ] AI responds within 20 seconds
  - [ ] Response is relevant to user input
  - [ ] Response is engaging and coherent
  - [ ] No error messages

- [ ] **Continued Interaction**
  - [ ] Send another message
  - [ ] AI responds again
  - [ ] Conversation flows naturally
  - [ ] No lag or freezing

### Phase 6: Data Persistence

- [ ] **Session Persistence**
  - [ ] Refresh the page (F5)
  - [ ] Page reloads within 3 seconds
  - [ ] Still logged in (no re-authentication)
  - [ ] Chat history is preserved
  - [ ] Character is still selected

- [ ] **Data Integrity**
  - [ ] All previous messages are visible
  - [ ] Character data is intact
  - [ ] World selection is remembered
  - [ ] No data loss

## 🎯 User Experience Validation

### Intuitiveness (No Instruction Needed)

- [ ] **First Impression**
  - [ ] Purpose of app is immediately clear
  - [ ] Next steps are obvious
  - [ ] No confusion about what to do

- [ ] **Navigation**
  - [ ] Can navigate without help
  - [ ] Back button works as expected
  - [ ] Breadcrumbs or progress indicators present
  - [ ] No getting lost or stuck

- [ ] **Feedback**
  - [ ] Loading states are clear
  - [ ] Success messages are shown
  - [ ] Errors are explained clearly
  - [ ] Progress is visible

### Engagement (Fun Factor)

- [ ] **Story Quality**
  - [ ] Initial story is engaging
  - [ ] AI responses are interesting
  - [ ] Narrative flows well
  - [ ] Want to continue playing

- [ ] **Visual Design**
  - [ ] UI is visually appealing
  - [ ] Colors and fonts are pleasant
  - [ ] Layout is clean and organized
  - [ ] No visual bugs or glitches

- [ ] **Performance**
  - [ ] No noticeable lag
  - [ ] Smooth transitions
  - [ ] Fast response times
  - [ ] No freezing or crashes

## 🔍 Technical Validation

### Database Persistence

- [ ] **Redis (Session Data)**
  ```bash
  docker exec -it tta-staging-redis redis-cli
  > KEYS openrouter:session:*
  # Should show session keys
  ```

- [ ] **Neo4j (Character Data)**
  ```bash
  # Open Neo4j Browser: http://localhost:7475
  # Run query:
  MATCH (c:Character) RETURN c LIMIT 5
  # Should show created characters
  ```

- [ ] **PostgreSQL (User Data)**
  ```bash
  docker exec -it tta-staging-postgres psql -U tta_staging_user -d tta_staging
  # Run query:
  SELECT * FROM users LIMIT 5;
  # Should show user records
  ```

### API Health

- [ ] **API Endpoints**
  - [ ] Health: http://localhost:8081/health
  - [ ] Docs: http://localhost:8081/docs
  - [ ] All endpoints return 200 OK

### Console Logs

- [ ] **No Errors**
  - Open browser DevTools (F12)
  - Check Console tab
  - [ ] No red error messages
  - [ ] No 404 errors
  - [ ] No CORS errors
  - [ ] No authentication errors

## 📊 Performance Metrics

### Response Times

- [ ] **Page Load Times**
  - [ ] Landing page: < 3s
  - [ ] Dashboard: < 3s
  - [ ] Character creation: < 2s
  - [ ] World selection: < 3s
  - [ ] Chat interface: < 3s

- [ ] **API Response Times**
  - [ ] Authentication: < 5s
  - [ ] Character creation: < 3s
  - [ ] Initial story: < 10s
  - [ ] AI response: < 20s

### Resource Usage

- [ ] **Browser Performance**
  - [ ] CPU usage reasonable (< 50%)
  - [ ] Memory usage stable (< 500MB)
  - [ ] No memory leaks
  - [ ] Smooth scrolling

## ✅ Final Verification

### All Systems Go

- [ ] **Automated Tests Pass**
  - All Playwright tests pass
  - No flaky tests
  - Consistent results

- [ ] **Manual Tests Pass**
  - Complete user journey works
  - No blockers or critical issues
  - User experience is intuitive

- [ ] **Technical Validation Pass**
  - All databases working
  - All APIs responding
  - Data persists correctly

- [ ] **Performance Acceptable**
  - Response times within targets
  - No lag or freezing
  - Smooth user experience

### Ready for Users

- [ ] **Confidence Level: High**
  - Would you let a user try this without instruction?
  - Would you be comfortable demoing this?
  - Are you proud of the user experience?

## 🐛 Issue Tracking

### Issues Found

| Issue | Severity | Phase | Status | Notes |
|-------|----------|-------|--------|-------|
| Example: Slow AI response | Medium | Phase 5 | Open | Investigating model selection |
|  |  |  |  |  |
|  |  |  |  |  |

### Severity Levels

- **Critical:** Blocks user journey, must fix before release
- **High:** Significant impact on UX, should fix soon
- **Medium:** Noticeable but not blocking, fix when possible
- **Low:** Minor issue, nice to have

## 📝 Sign-Off

### Validation Complete

- **Date:** _______________
- **Tester:** _______________
- **Environment:** Staging (localhost)
- **Result:** ☐ Pass ☐ Pass with Issues ☐ Fail

### Notes

```
[Add any additional notes, observations, or recommendations here]
```

---

**Next Steps:**
- [ ] Address any critical issues
- [ ] Re-run validation after fixes
- [ ] Document any workarounds
- [ ] Prepare for production deployment
