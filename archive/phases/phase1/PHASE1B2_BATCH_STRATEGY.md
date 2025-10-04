# Phase 1B.2: Exception Chaining - Batch Strategy

## 📊 Total B904 Errors: 121

**Note:** Error count increased from 104 to 121 (likely due to files not previously scanned or new code).

---

## 🎯 Batching Strategy

### Batch 1: Player Experience Database (24 errors)
**Files:**
- `src/player_experience/database/player_profile_repository.py` (16 errors)
- `src/player_experience/database/player_profile_schema.py` (5 errors)
- `src/player_experience/database/user_repository.py` (3 errors)

### Batch 2: Model Management & Components (17 errors)
**Files:**
- `src/components/model_management/api.py` (16 errors)
- `src/components/docker_component.py` (1 error)

### Batch 3: Player Experience API - Auth & Core (19 errors)
**Files:**
- `src/player_experience/api/routers/auth.py` (14 errors)
- `src/player_experience/api/auth.py` (3 errors)
- `src/player_experience/api/routers/openrouter_auth.py` (2 errors)

### Batch 4: Player Experience API - Gameplay & Worlds (19 errors)
**Files:**
- `src/player_experience/api/routers/conversation.py` (8 errors)
- `src/player_experience/api/routers/franchise_worlds.py` (6 errors)
- `src/player_experience/api/routers/gameplay.py` (5 errors)

### Batch 5: Player Experience Managers & Services (12 errors)
**Files:**
- `src/player_experience/managers/player_profile_manager.py` (11 errors)
- `src/player_experience/services/auth_service.py` (1 error)

### Batch 6: Agent Orchestration (10 errors)
**Files:**
- `src/agent_orchestration/service.py` (5 errors)
- `src/agent_orchestration/optimization/performance_analytics.py` (5 errors)

### Batch 7: API Gateway & Remaining (20 errors)
**Files:**
- `src/api_gateway/interfaces/patient_api.py` (4 errors)
- `src/player_experience/api/routers/privacy.py` (3 errors)
- `src/player_experience/franchise_worlds/api/main.py` (2 errors)
- `src/agent_orchestration/api/diagnostics.py` (2 errors)
- `src/agent_orchestration/adapters.py` (3 errors)
- `src/player_experience/security/rate_limiter.py` (1 error)
- `src/player_experience/franchise_worlds/integration/PlayerExperienceIntegration.py` (1 error)
- `src/player_experience/api/validation_schemas.py` (1 error)
- `src/player_experience/api/routers/chat.py` (1 error)
- `src/components/model_management/providers/custom_api.py` (1 error)
- `src/analytics/services/reporting_service.py` (1 error)

---

## 📝 Pattern to Apply

```python
# Before
try:
    # some code
except Exception as e:
    raise CustomError("message")

# After
try:
    # some code
except Exception as e:
    raise CustomError("message") from e
```

**Important:** Ensure the exception variable name matches what's in the except clause!

---

## ✅ Verification Steps (Per Batch)

1. Run: `uv run ruff check [files] | grep B904`
2. Run: `uv run black --check [files]`
3. Run: `uv run isort --check [files]`
4. Commit with message: `fix(error-handling): add exception chaining to [module] (B904)`
5. Push and monitor CI

---

## 📊 Expected Progress

| Batch | Errors Fixed | Cumulative Fixed | Remaining |
|-------|--------------|------------------|-----------|
| 1 | 24 | 24 | 97 |
| 2 | 17 | 41 | 80 |
| 3 | 19 | 60 | 61 |
| 4 | 19 | 79 | 42 |
| 5 | 12 | 91 | 30 |
| 6 | 10 | 101 | 20 |
| 7 | 20 | 121 | 0 |

**Total Estimated Time:** 2-3 hours

