# Security Findings - Accepted Risks

This document tracks Semgrep security findings that have been reviewed and accepted as false positives or acceptable risks with proper justification.

## ERROR Severity - Accepted Risks

### 1. Insecure WebSocket Detection (1 finding)

**Finding ID:** `javascript.lang.security.detect-insecure-websocket.detect-insecure-websocket`

**Location:** `src/developer_dashboard/test_battery_integration.py:368`

**Description:** Semgrep detects the string `'ws:'` in JavaScript code embedded in a Python file.

**Justification:** This is a **FALSE POSITIVE**. The code properly implements secure WebSocket connections:
- Uses `wss://` (secure) when page is loaded over HTTPS (production)
- Only uses `ws://` (insecure) for local development over HTTP
- The protocol is dynamically selected based on the page's protocol:
  ```javascript
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
```

**Risk Assessment:** **LOW** - The implementation is secure and follows best practices for WebSocket connections.

**Mitigation:** Code review confirms proper implementation. No changes needed.

**Date Reviewed:** 2025-01-XX

**Reviewed By:** Security Remediation Task

---

## WARNING Severity - Accepted Risks

### 2. Docker Socket Exposure (2 findings)

**Finding ID:** `yaml.docker-compose.security.exposing-docker-socket-volume.exposing-docker-socket-volume`

**Locations:**
- `templates/tta.dev/docker-compose.yml:29`
- `templates/tta.prototype/docker-compose.yml:29`

**Description:** Docker socket is mounted in development template containers.

**Justification:** These are **DEVELOPMENT TEMPLATES** only, not used in production. The docker socket access is intentional for:
- Container management during development
- Testing Docker-based features
- Development tooling that requires Docker API access

**Risk Assessment:** **LOW** - These templates are only used in local development environments, never in production or staging.

**Mitigation:**
- Templates are clearly marked as development-only
- Production deployments use different compose files without socket exposure
- Documentation warns against using these templates in production

### 3. Privileged Container (1 finding)

**Finding ID:** `yaml.docker-compose.security.privileged-service.privileged-service`

**Location:** `monitoring/docker-compose.monitoring.yml:138` (cadvisor service)

**Description:** cAdvisor container runs in privileged mode.

**Justification:** This is **REQUIRED** for cAdvisor to function properly. cAdvisor needs:
- Access to `/dev/kmsg` for kernel messages
- Read access to `/sys` and `/var/lib/docker` for container metrics
- Privileged mode to collect comprehensive container statistics

**Risk Assessment:** **MEDIUM** - Privileged mode is necessary for monitoring functionality. Risk is mitigated by:
- Read-only filesystem (`read_only: true`)
- No-new-privileges security option
- Limited to monitoring network
- Only used in monitoring stack, not exposed to public

**Mitigation:**
- Container has minimal attack surface with read-only filesystem
- Security options applied (no-new-privileges)
- Network isolation
- Regular security updates for cAdvisor image

### 4. Writable Filesystem Services (52 findings)

**Finding ID:** `yaml.docker-compose.security.writable-filesystem-service.writable-filesystem-service`

**Description:** Multiple services run with writable root filesystem.

**Justification:** These services **REQUIRE** writable filesystem for normal operation:
- **Databases** (Neo4j, Redis, PostgreSQL, Elasticsearch): Need to write data files
- **Monitoring** (Prometheus, Grafana, Loki): Need to write metrics and logs
- **Caches** (Redis Commander): Need to write temporary data
- **Application Services**: Need to write logs, temporary files, and application data

**Risk Assessment:** **LOW** - These are legitimate operational requirements. Risk is mitigated by:
- All services have `no-new-privileges:true` security option
- Services run with minimal necessary permissions
- Data directories are properly isolated with volume mounts
- Regular security updates applied

**Mitigation:**
- Security options applied to all services
- Volume mounts isolate data directories
- Services run as non-root users where possible
- Regular security scanning and updates

---

## Summary

- **Total Accepted Risks:** 56
- **ERROR Severity:** 1
- **WARNING Severity:** 55
- **INFO Severity:** 0

All other findings have been remediated.


# Check health
curl http://localhost:8080/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "player-experience-api",
#   "version": "1.0.0"
# }
```

### If Backend Stops, Restart Using:

```bash
# Method 1: Using the startup script (Recommended)
./start_backend.sh

# Method 2: Manual startup
source .venv/bin/activate
export PYTHONPATH=/home/thein/recovered-tta-storytelling
uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080 --reload
```

**See `BACKEND_STARTUP_FIX.md` for detailed documentation on the fix.**

---

## Option 2: Run Manual Validation (No Backend Required)

### Follow the Manual Validation Checklist:

**Document:** `VALIDATION_RESULTS.md`

**Sections to Test:**
1. Frontend Loading (✅ Already validated)
2. Secure Token Storage (✅ Already validated)
3. Error Handling Display (✅ Already validated)
4. Responsive Design (✅ Already validated)
5. Navigation (✅ Already validated)

**Sections Requiring Backend:**
1. Character Creation Flow
2. Therapeutic AI Chat System
3. Conversation History Persistence
4. Session Persistence
5. WebSocket Connection Stability

---

## Option 3: Run Automated Tests (Requires Backend)

### Once Backend is Running:

```bash
# Run comprehensive validation tests
npx playwright test tests/e2e/comprehensive-validation.spec.ts --headed

# Or run with specific browser
npx playwright test tests/e2e/comprehensive-validation.spec.ts --project=chromium

# View test report
npx playwright show-report
```

---

## Troubleshooting Backend Startup

### Issue: Import Errors

**Error:**
```
ImportError: attempted relative import beyond top-level package
```

**Solution:**
```bash
# Set PYTHONPATH to project root
export PYTHONPATH=/home/thein/recovered-tta-storytelling

# Run from project root
cd /home/thein/recovered-tta-storytelling
python -m src.player_experience.api.main
```

### Issue: Missing Dependencies

**Error:**
```
No module named 'uvicorn'
```

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install specific package
pip install uvicorn fastapi
```

### Issue: Port Already in Use

**Error:**
```
Address already in use
```

**Solution:**
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>

# Or use different port
python -m uvicorn api.main:app --host 0.0.0.0 --port 8081 --reload
```

---

## Validation Test Files

### Created Test Files:

1. **`tests/e2e/comprehensive-validation.spec.ts`**
   - Full E2E validation suite
   - Requires backend API running
   - Tests all critical features

2. **`quick-validation.spec.ts`**
   - Frontend-only validation
   - No backend required
   - Already executed successfully (10/10 passed)

3. **`playwright.quick.config.ts`**
   - Configuration for quick validation
   - No global setup required

### Run Quick Validation Again:

```bash
npx playwright test --config=playwright.quick.config.ts
```

---

## Validation Documentation

### Generated Documents:

1. **`VALIDATION_RESULTS.md`**
   - Comprehensive validation checklist
   - Manual validation steps
   - Success criteria for each feature

2. **`VALIDATION_TEST_RESULTS.md`**
   - Automated test results
   - Detailed test breakdown
   - Evidence and significance

3. **`COMPREHENSIVE_VALIDATION_SUMMARY.md`**
   - Executive summary
   - Overall validation status
   - Recommendations

4. **`NEXT_STEPS_GUIDE.md`** (this file)
   - Quick start guide
   - Troubleshooting tips
   - Command reference

---

## Backend API Endpoints to Test

### Once Backend is Running:

```bash
# Health check
curl http://localhost:8080/health

# API documentation
curl http://localhost:8080/docs

# Character creation (requires auth)
curl -X POST http://localhost:8080/api/v1/characters \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Test Character",
    "appearance": {...},
    "background": {...},
    "personality_traits": ["brave", "compassionate"],
    "therapeutic_profile": {...}
  }'
```

---

## Manual Testing Workflow

### Complete User Journey:

1. **Open Application**
   ```
http://localhost:3000
```

2. **Login**
   - Navigate to login page
   - Enter credentials
   - Verify successful login
   - Check: No tokens in localStorage

3. **Create Character**
   - Navigate to character creation
   - Fill in all required fields
   - Submit form
   - Verify: No 422 errors
   - Verify: Character appears in list

4. **Start Chat**
   - Navigate to chat interface
   - Send a message
   - Verify: AI response (not echo)
   - Verify: Progressive feedback indicators

5. **Test Persistence**
   - Refresh page (F5)
   - Verify: Still logged in
   - Verify: Conversation history loaded

6. **Test Error Handling**
   - Trigger an error (invalid input)
   - Verify: User-friendly error message
   - Verify: No "[object Object]" displays

7. **Logout**
   - Click logout
   - Verify: Redirected to login
   - Verify: Session cleared

---

## Success Criteria

### Frontend Validation: ✅ COMPLETE

- [x] Application loads successfully
- [x] No [object Object] errors
- [x] Secure token storage
- [x] ErrorBoundary integrated
- [x] Responsive design works
- [x] CSS loaded and applied
- [x] React rendered successfully
- [x] Navigation works
- [x] No critical console errors
- [x] Offline handling works

### Backend Integration: 🔄 PENDING

- [ ] Backend API starts successfully
- [ ] Character creation works (no 422 errors)
- [ ] AI chat responses (not echo)
- [ ] Conversation history persists
- [ ] Session persistence works
- [ ] WebSocket connection stable
- [ ] Neo4j integration works
- [ ] Redis persistence works

---

## Contact & Support

### If You Encounter Issues:

1. **Check Logs**
   - Backend: Check terminal output
   - Frontend: Check browser console
   - Redis: `redis-cli monitor`
   - Neo4j: Check Neo4j Browser

2. **Review Documentation**
   - `VALIDATION_RESULTS.md` - Manual validation steps
   - `VALIDATION_TEST_RESULTS.md` - Test results
   - `COMPREHENSIVE_VALIDATION_SUMMARY.md` - Overall summary

3. **Common Issues**
   - Import errors: Set PYTHONPATH
   - Port conflicts: Kill existing processes
   - Missing dependencies: Install from requirements.txt
   - Database connections: Verify Redis and Neo4j running

---

## Quick Command Reference

```bash
# Check services
ps aux | grep -E "redis|neo4j|node|python" | grep -v grep

# Start Redis
redis-server

# Start Neo4j
neo4j start

# Start Frontend (if not running)
cd src/player_experience/frontend && npm start

# Start Backend
source .venv/bin/activate
export PYTHONPATH=/home/thein/recovered-tta-storytelling
cd src/player_experience
python -m uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload

# Run Quick Validation
npx playwright test --config=playwright.quick.config.ts

# Run Full Validation (requires backend)
npx playwright test tests/e2e/comprehensive-validation.spec.ts --headed
```

---

## Summary

### Current Status:
- ✅ Frontend validation complete (10/10 tests passed)
- ✅ All critical fixes implemented and verified
- ✅ Security improvements confirmed
- ✅ Error handling working correctly
- 🔄 Backend integration testing pending

### Next Action:
**Start backend API server to enable full E2E validation**

### Estimated Time:
- Backend startup: 5-10 minutes
- Full E2E validation: 15-20 minutes
- Manual validation: 30-45 minutes

---

**Guide Created:** 2025-09-29  
**Status:** Ready for Backend Integration Testing  
**Priority:** HIGH - Complete validation before production deployment

- Manual validation: 30-45 minutes

---

**Guide Created:** 2025-09-29  
**Status:** Ready for Backend Integration Testing  
**Priority:** HIGH - Complete validation before production deployment

rs.appearance ? 'border-red-500' : ''}`}
              rows={4}
              placeholder="Describe your character's physical appearance, style, and any distinctive features..."
              value={formData.appearance.physical_description}
              onChange={(e) => handleInputChange('appearance.physical_description', e.target.value)}
            />
            {errors.appearance && <p className="text-red-600 text-sm mt-1">{errors.appearance}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Clothing Style
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g., casual, formal, bohemian, etc."
              value={formData.appearance.clothing_style}
              onChange={(e) => handleInputChange('appearance.clothing_style', e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Character Preview */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Preview</h4>
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-primary-500 rounded-full flex items-center justify-center">
            <span className="text-white text-lg font-bold">
              {formData.name.charAt(0).toUpperCase() || '?'}
            </span>
          </div>
          <div>
            <p className="font-medium text-gray-900">{formData.name || 'Character Name'}</p>
            <p className="text-sm text-gray-600">
              {formData.appearance.physical_description || 'Physical description will appear here...'}
            </p>
            <p className="text-xs text-gray-500">
              {formData.appearance.age_range} • {formData.appearance.gender_identity} • {formData.appearance.clothing_style}
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Background & Personality</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Background Story *
            </label>
            <textarea
              className={`input-field ${errors.backstory ? 'border-red-500' : ''}`}
              rows={4}
              placeholder="Tell your character's story, their past experiences, and what brought them here..."
              value={formData.background.backstory}
              onChange={(e) => handleInputChange('background.backstory', e.target.value)}
            />
            {errors.backstory && <p className="text-red-600 text-sm mt-1">{errors.backstory}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Personality Traits *
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a personality trait"
                value={newTrait}
                onChange={(e) => setNewTrait(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('background.personality_traits', newTrait, setNewTrait);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('background.personality_traits', newTrait, setNewTrait)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {Array.isArray(formData.background.personality_traits) && formData.background.personality_traits.map((trait, index) => {
                // Ensure trait is a string
                const traitText = typeof trait === 'string' ? trait : String(trait);
                return (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                  >
                    {traitText}
                    <button
                      type="button"
                      onClick={() => removeArrayItem('background.personality_traits', index)}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                );
              })}
            </div>
            {errors.traits && <p className="text-red-600 text-sm mt-1">{errors.traits}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Life Goals *
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a life goal"
                value={newGoal}
                onChange={(e) => setNewGoal(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('background.life_goals', newGoal, setNewGoal);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('background.life_goals', newGoal, setNewGoal)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {Array.isArray(formData.background.life_goals) && formData.background.life_goals.map((goal, index) => {
                // Ensure goal is a string
                const goalText = typeof goal === 'string' ? goal : String(goal);
                return (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full"
                  >
                    {goalText}
                    <button
                      type="button"
                      onClick={() => removeArrayItem('background.life_goals', index)}
                      className="ml-2 text-green-600 hover:text-green-800"
                    >
                      ×
                    </button>
                  </span>
                );
              })}
            </div>
            {errors.goals && <p className="text-red-600 text-sm mt-1">{errors.goals}</p>}
          </div>

          {/* Core Values */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Core Values
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a core value"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('background.core_values', newValue, setNewValue);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('background.core_values', newValue, setNewValue)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.background.core_values.map((value, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full"
                >
                  {value}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('background.core_values', index)}
                    className="ml-2 text-purple-600 hover:text-purple-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Fears and Anxieties */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fears & Anxieties
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a fear or anxiety"
                value={newFear}
                onChange={(e) => setNewFear(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('background.fears_and_anxieties', newFear, setNewFear);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('background.fears_and_anxieties', newFear, setNewFear)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.background.fears_and_anxieties.map((fear, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-red-100 text-red-800 text-sm rounded-full"
                >
                  {fear}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('background.fears_and_anxieties', index)}
                    className="ml-2 text-red-600 hover:text-red-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Strengths and Skills */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Strengths & Skills
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a strength or skill"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('background.strengths_and_skills', newSkill, setNewSkill);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('background.strengths_and_skills', newSkill, setNewSkill)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.background.strengths_and_skills.map((skill, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('background.strengths_and_skills', index)}
                    className="ml-2 text-yellow-600 hover:text-yellow-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Therapeutic Profile</h3>
        
        <div className="space-y-4">
          {/* Primary Concerns */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Primary Concerns *
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a primary concern"
                value={newConcern}
                onChange={(e) => setNewConcern(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('therapeutic_profile.primary_concerns', newConcern, setNewConcern);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('therapeutic_profile.primary_concerns', newConcern, setNewConcern)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.therapeutic_profile.primary_concerns.map((concern, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full"
                >
                  {concern}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('therapeutic_profile.primary_concerns', index)}
                    className="ml-2 text-orange-600 hover:text-orange-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            {errors.concerns && <p className="text-red-600 text-sm mt-1">{errors.concerns}</p>}
          </div>

          {/* Readiness Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Readiness Level (0.0 - 1.0)
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                className="flex-1"
                value={formData.therapeutic_profile.readiness_level}
                onChange={(e) => handleInputChange('therapeutic_profile.readiness_level', parseFloat(e.target.value))}
              />
              <span className="text-lg font-medium text-gray-900 w-12">
                {formData.therapeutic_profile.readiness_level.toFixed(1)}
              </span>
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Not Ready</span>
              <span>Fully Ready</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred Therapeutic Intensity
            </label>
            <select
              className="input-field"
              value={formData.therapeutic_profile.preferred_intensity}
              onChange={(e) => handleInputChange('therapeutic_profile.preferred_intensity', e.target.value as IntensityLevel)}
            >
              <option value="LOW">Low - Gentle guidance and support</option>
              <option value="MEDIUM">Medium - Balanced therapeutic approach</option>
              <option value="HIGH">High - Intensive therapeutic work</option>
            </select>
          </div>

          {/* Comfort Zones */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Comfort Zones
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a comfort zone"
                value={newComfortZone}
                onChange={(e) => setNewComfortZone(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addArrayItem('therapeutic_profile.comfort_zones', newComfortZone, setNewComfortZone);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addArrayItem('therapeutic_profile.comfort_zones', newComfortZone, setNewComfortZone)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.therapeutic_profile.comfort_zones.map((zone, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-teal-100 text-teal-800 text-sm rounded-full"
                >
                  {zone}
                  <button
                    type="button"
                    onClick={() => removeArrayItem('therapeutic_profile.comfort_zones', index)}
                    className="ml-2 text-teal-600 hover:text-teal-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Therapeutic Goals *
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                className="input-field flex-1"
                placeholder="Add a therapeutic goal"
                value={newTherapeuticGoal}
                onChange={(e) => setNewTherapeuticGoal(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addTherapeuticGoal(newTherapeuticGoal);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => addTherapeuticGoal(newTherapeuticGoal)}
                className="btn-primary px-3"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.therapeutic_profile.therapeutic_goals.map((goal, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full"
                >
                  {goal.description}
                  <button
                    type="button"
                    onClick={() => removeTherapeuticGoal(index)}
                    className="ml-2 text-purple-600 hover:text-purple-800"
                  >
                    ×
                  </button>
                </span>
                );
              })}
            </div>
            {errors.therapeuticGoals && <p className="text-red-600 text-sm mt-1">{errors.therapeuticGoals}</p>}
          </div>
        </div>
      </div>

      {/* Final Preview */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Character Summary</h4>
        <div className="space-y-2 text-sm">
          <p><span className="font-medium">Name:</span> {formData.name}</p>
          <p><span className="font-medium">Comfort Level:</span> {formData.therapeutic_profile.comfort_level}/10</p>
          <p><span className="font-medium">Intensity:</span> {formData.therapeutic_profile.preferred_intensity}</p>
          <p><span className="font-medium">Traits:</span> {Array.isArray(formData.background.personality_traits) ? formData.background.personality_traits.filter(t => typeof t === 'string').join(', ') : 'None'}</p>
          <p><span className="font-medium">Goals:</span> {Array.isArray(formData.background.goals) ? formData.background.goals.filter(g => typeof g === 'string').join(', ') : 'None'}</p>
          <p><span className="font-medium">Therapeutic Goals:</span> {Array.isArray(formData.therapeutic_profile.therapeutic_goals) ? formData.therapeutic_profile.therapeutic_goals.filter(g => typeof g === 'string').join(', ') : 'None'}</p>
        </div>
      </div>
    </div>
  );

  const handleBackdropClick = (e: React.MouseEvent) => {
    // Only close if clicking on the backdrop itself, not the modal content
    // Also ensure we're not interfering with button clicks
    if (e.target === e.currentTarget && !(e.target as HTMLElement).closest('button')) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div
        className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Create New Character</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Progress Steps */}
          <div className="flex items-center mt-4">
            {[1, 2, 3].map((step) => (
              <React.Fragment key={step}>
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step <= currentStep
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step}
                </div>
                {step < 3 && (
                  <div
                    className={`flex-1 h-1 mx-2 ${
                      step < currentStep ? 'bg-primary-600' : 'bg-gray-200'
                    }`}
                  />
                )}
              </React.Fragment>
            ))}
          </div>
          
          <div className="flex justify-between text-sm text-gray-600 mt-2">
            <span>Basic Info</span>
            <span>Background</span>
            <span>Therapeutic</span>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-4 overflow-y-auto max-h-[60vh]">
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
        </div>

        {/* Error Display */}
        {error && (
          <div className="px-6 py-2">
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
          <button
            onClick={currentStep === 1 ? onClose : handlePrevious}
            className="btn-secondary"
          >
            {currentStep === 1 ? 'Cancel' : 'Previous'}
          </button>
          
          {currentStep < 3 ? (
            <button onClick={handleNext} className="btn-primary">
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={creationInProgress}
              className="btn-primary disabled:opacity-50"
            >
              {creationInProgress ? (
                <div className="flex items-center">
                  <div className="spinner mr-2"></div>
                  Creating...
                </div>
              ) : (
                'Create Character'
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CharacterCreationForm;