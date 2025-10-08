# Phase 4: Performance Testing - Comprehensive Plan

**Plan Date:** 2025-10-06
**Environment:** TTA Staging (Homelab)
**Tools:** Playwright, Lighthouse, Chrome DevTools
**Status:** 📋 PLANNING COMPLETE - READY FOR EXECUTION

---

## Executive Summary

This document outlines a comprehensive performance testing plan for the TTA staging environment. The plan focuses on validating **response times**, **API performance**, and **user experience metrics** to ensure the system meets performance targets.

**Performance Targets:**
- Form submissions: <3 seconds
- AI responses: <10 seconds
- Page load time: <2 seconds
- API response time: <200ms (95th percentile)

---

## 1. Performance Testing Objectives

### 1.1 Primary Objectives

1. **Validate Form Performance**
   - API key input form submission time
   - Character creation form submission time
   - Settings save time

2. **Measure AI Response Times**
   - Story generation time
   - Choice consequence generation time
   - Narrative continuation time

3. **Assess Page Load Performance**
   - First Contentful Paint (FCP)
   - Largest Contentful Paint (LCP)
   - Time to Interactive (TTI)
   - Cumulative Layout Shift (CLS)

4. **Identify Performance Bottlenecks**
   - Slow API endpoints
   - Large bundle sizes
   - Inefficient database queries
   - Network latency issues

---

## 2. Test Scenarios

### 2.1 Scenario 1: API Key Input Form Performance

**Objective:** Measure time from form submission to response

**Test Steps:**
1. Navigate to Settings > AI Models
2. Click "Connect to OpenRouter"
3. Enter API key: `sk-or-v1-test-key-12345`
4. Click "Connect with API Key"
5. Measure time to response (success or error)

**Metrics to Capture:**
- Form submission time
- API response time
- UI update time
- Total time to completion

**Performance Target:** <3 seconds total

**Test Script:**
```typescript
test('API key form performance', async ({ page }) => {
  const startTime = Date.now();

  await page.goto('/settings');
  await page.click('[data-testid="settings-tab-models"]');
  await page.click('button:has-text("Connect to OpenRouter")');

  const formStartTime = Date.now();
  await page.fill('input[name="api_key"]', 'sk-or-v1-test-key-12345');
  await page.click('button:has-text("Connect with API Key")');

  // Wait for response
  await page.waitForSelector('[data-testid="connection-status"]', { timeout: 5000 });
  const formEndTime = Date.now();

  const formSubmissionTime = formEndTime - formStartTime;
  console.log(`Form submission time: ${formSubmissionTime}ms`);

  expect(formSubmissionTime).toBeLessThan(3000);
});
```

### 2.2 Scenario 2: Character Creation Form Performance

**Objective:** Measure time from form submission to character creation

**Test Steps:**
1. Navigate to Characters page
2. Click "Create Character"
3. Fill in character details
4. Click "Create"
5. Measure time to character created

**Metrics to Capture:**
- Form fill time
- API request time
- Database write time
- UI update time

**Performance Target:** <3 seconds total

### 2.3 Scenario 3: AI Story Generation Performance

**Objective:** Measure time for AI to generate story content

**Test Steps:**
1. Start a new story
2. Measure time from "Start Story" click to first scene displayed
3. Make a choice
4. Measure time from choice click to next scene displayed

**Metrics to Capture:**
- Initial story generation time
- Choice consequence generation time
- API latency
- Total user wait time

**Performance Target:** <10 seconds per AI response

### 2.4 Scenario 4: Page Load Performance

**Objective:** Measure page load times for all major pages

**Pages to Test:**
- Login page
- Dashboard
- Characters page
- Worlds page
- Settings page
- Gameplay page

**Metrics to Capture:**
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to Interactive (TTI)
- Cumulative Layout Shift (CLS)
- Total Blocking Time (TBT)

**Performance Targets:**
- FCP: <1.8s
- LCP: <2.5s
- TTI: <3.8s
- CLS: <0.1
- TBT: <200ms

---

## 3. Performance Testing Tools

### 3.1 Playwright Performance API

**Usage:**
```typescript
test('measure page load performance', async ({ page }) => {
  const startTime = Date.now();
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  const loadTime = Date.now() - startTime;

  console.log(`Page load time: ${loadTime}ms`);
  expect(loadTime).toBeLessThan(2000);
});
```

### 3.2 Lighthouse

**Usage:**
```bash
# Install Lighthouse
npm install -g lighthouse

# Run Lighthouse on staging
lighthouse http://localhost:3001 --output html --output-path ./test-results-staging/lighthouse-report.html

# Run on specific pages
lighthouse http://localhost:3001/dashboard --output json --output-path ./test-results-staging/lighthouse-dashboard.json
```

**Metrics Captured:**
- Performance score (0-100)
- Accessibility score
- Best practices score
- SEO score
- Core Web Vitals

### 3.3 Chrome DevTools Performance Tab

**Usage:**
1. Open Chrome DevTools (F12)
2. Go to Performance tab
3. Click Record
4. Perform actions
5. Stop recording
6. Analyze timeline

**Metrics to Analyze:**
- JavaScript execution time
- Rendering time
- Network requests
- Memory usage

### 3.4 Network Tab Analysis

**Metrics to Capture:**
- Total requests
- Total transfer size
- Total resource size
- DOMContentLoaded time
- Load time

---

## 4. API Performance Testing

### 4.1 API Endpoints to Test

| Endpoint | Method | Expected Response Time |
|----------|--------|------------------------|
| `/health` | GET | <50ms |
| `/api/v1/auth/login` | POST | <200ms |
| `/api/v1/characters` | GET | <200ms |
| `/api/v1/characters` | POST | <500ms |
| `/api/v1/worlds` | GET | <200ms |
| `/api/v1/sessions` | POST | <300ms |
| `/api/v1/gameplay/action` | POST | <10000ms (AI) |

### 4.2 API Performance Test Script

```bash
#!/bin/bash
# API Performance Test Script

API_URL="http://localhost:8081"

echo "Testing API Performance..."

# Test health endpoint
echo "Testing /health..."
time curl -s -o /dev/null -w "%{time_total}\n" $API_URL/health

# Test auth endpoint
echo "Testing /api/v1/auth/login..."
time curl -s -o /dev/null -w "%{time_total}\n" -X POST $API_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"DemoPassword123!"}'

# Test characters endpoint
echo "Testing /api/v1/characters..."
time curl -s -o /dev/null -w "%{time_total}\n" $API_URL/api/v1/characters \
  -H "Authorization: Bearer $TOKEN"

echo "API Performance Test Complete"
```

---

## 5. Database Performance Testing

### 5.1 Redis Performance

**Metrics to Test:**
- Session read time
- Session write time
- Cache hit rate
- Connection pool usage

**Test Commands:**
```bash
# Connect to Redis
redis-cli -h localhost -p 6380

# Test SET performance
redis-cli -h localhost -p 6380 --latency

# Test GET performance
redis-cli -h localhost -p 6380 --latency-history

# Monitor operations
redis-cli -h localhost -p 6380 MONITOR
```

### 5.2 Neo4j Performance

**Metrics to Test:**
- Story graph query time
- Relationship traversal time
- Node creation time
- Query complexity

**Test Queries:**
```cypher
// Test simple query
PROFILE MATCH (n:Story) RETURN n LIMIT 10;

// Test relationship traversal
PROFILE MATCH (s:Story)-[:HAS_SCENE]->(scene:Scene) RETURN s, scene LIMIT 10;

// Test complex query
PROFILE MATCH (s:Story)-[:HAS_SCENE]->(scene:Scene)-[:HAS_CHOICE]->(choice:Choice)
WHERE s.id = 'story-123'
RETURN s, scene, choice;
```

### 5.3 PostgreSQL Performance

**Metrics to Test:**
- User query time
- Character query time
- Session query time
- Index usage

**Test Queries:**
```sql
-- Test user query
EXPLAIN ANALYZE SELECT * FROM users WHERE username = 'demo_user';

-- Test character query
EXPLAIN ANALYZE SELECT * FROM characters WHERE player_id = 'player-123';

-- Test session query
EXPLAIN ANALYZE SELECT * FROM sessions WHERE user_id = 'user-123' ORDER BY created_at DESC LIMIT 10;
```

---

## 6. Load Testing (Optional)

### 6.1 Concurrent User Simulation

**Tool:** Locust (already in project)

**Test Scenario:**
- Simulate 10 concurrent users
- Each user performs complete journey
- Measure response times under load

**Locust Script:**
```python
from locust import HttpUser, task, between

class TTAUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def login(self):
        self.client.post("/api/v1/auth/login", json={
            "username": "demo_user",
            "password": "DemoPassword123!"
        })

    @task
    def get_characters(self):
        self.client.get("/api/v1/characters")

    @task
    def get_worlds(self):
        self.client.get("/api/v1/worlds")
```

**Run Command:**
```bash
locust -f testing/load_tests/locustfile.py --host=http://localhost:8081 --users=10 --spawn-rate=2 --run-time=5m
```

---

## 7. Performance Benchmarks

### 7.1 Current Baseline (To Be Measured)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Login Time | <2s | TBD | ⏳ |
| Dashboard Load | <2s | TBD | ⏳ |
| Character Creation | <3s | TBD | ⏳ |
| API Key Submission | <3s | TBD | ⏳ |
| AI Story Generation | <10s | TBD | ⏳ |
| Settings Save | <1s | TBD | ⏳ |

### 7.2 Performance Budget

**JavaScript Bundle Size:**
- Main bundle: <500KB (gzipped)
- Vendor bundle: <1MB (gzipped)
- Total: <1.5MB (gzipped)

**API Response Sizes:**
- Character data: <50KB
- World data: <100KB
- Story scene: <20KB

**Network Requests:**
- Initial page load: <30 requests
- Subsequent navigation: <10 requests

---

## 8. Performance Optimization Recommendations

### 8.1 Frontend Optimizations

1. **Code Splitting**
   - Lazy load routes
   - Split vendor bundles
   - Dynamic imports for heavy components

2. **Image Optimization**
   - Use WebP format
   - Implement lazy loading
   - Optimize image sizes

3. **Caching Strategy**
   - Service worker for offline support
   - Cache API responses
   - Cache static assets

4. **Bundle Optimization**
   - Tree shaking
   - Minification
   - Compression (gzip/brotli)

### 8.2 Backend Optimizations

1. **Database Indexing**
   - Add indexes on frequently queried fields
   - Optimize query patterns
   - Use connection pooling

2. **API Caching**
   - Cache frequently accessed data
   - Use Redis for session storage
   - Implement CDN for static assets

3. **Query Optimization**
   - Reduce N+1 queries
   - Use batch operations
   - Implement pagination

---

## 9. Deliverables

### 9.1 Reports to Generate

1. **Performance Test Report**
   - Test results for all scenarios
   - Metrics comparison vs targets
   - Bottlenecks identified
   - Recommendations

2. **Lighthouse Reports**
   - HTML reports for each page
   - JSON data for analysis
   - Performance scores

3. **API Performance Report**
   - Response times for all endpoints
   - Slow endpoints identified
   - Optimization recommendations

4. **Database Performance Report**
   - Query performance metrics
   - Slow queries identified
   - Index recommendations

---

## 10. Conclusion

This performance testing plan provides a comprehensive framework for validating the TTA staging environment's performance. The plan covers **form performance**, **AI response times**, **page load metrics**, and **API performance**.

**Status:** 📋 **PLANNING COMPLETE** - Ready for execution once character creation is fixed.

**Next Steps:**
1. Fix character creation blocker
2. Execute performance tests
3. Analyze results
4. Implement optimizations
5. Re-test and validate improvements

---

**Plan Created:** 2025-10-06
**Created By:** The Augster (AI Development Assistant)
**Phase 4 Status:** ✅ PLANNING COMPLETE
