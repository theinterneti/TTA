# TTA Keploy Test Manifest

## Recorded Test Suites

### ✅ Simple API (Port 8000)
**Status**: Recorded and Ready
**Test Count**: 9 scenarios
**Coverage**:
- Health checks
- Session CRUD (Create, Read, Update, Delete)
- Error handling
- Edge cases

**Endpoints Covered**:
- GET /health
- GET /
- POST /api/v1/sessions
- GET /api/v1/sessions/:id
- GET /api/v1/sessions
- DELETE /api/v1/sessions/:id

### 🎮 Player Experience API (Port 8080)
**Status**: Template Ready
**Test Count**: 0 (pending API availability)
**Planned Coverage**:
- Authentication & Authorization
- Character management
- Narrative/Story progression
- Therapeutic features

### 🤖 Agent Orchestration API
**Status**: Pending
**Planned Coverage**:
- Agent health checks
- Message routing
- Circuit breaker states
- Fallback mechanisms

## Test Execution

### Run All Tests
```bash
./complete-keploy-workflow.sh
```

### Run Specific Suite
```bash
# Simple API only
uv run python run-keploy-tests.py

# Player API (when available)
KEPLOY_PORT=8080 uv run python run-keploy-tests.py
```

## Coverage Metrics

| API | Endpoints | Test Cases | Status |
|-----|-----------|------------|--------|
| Simple API | 6 | 9 | ✅ Active |
| Player Experience | ~15 | 0 | 📝 Planned |
| Agent Orchestration | ~10 | 0 | 📝 Planned |

**Total Coverage**: 9 automated test cases (expanding)

## Next Steps

1. ✅ Record more Simple API scenarios
2. 🔄 Enable Player Experience API testing
3. 🔄 Add Agent Orchestration tests
4. 🔄 Integrate into CI/CD pipeline
