# Phase 1: Therapeutic Safety Component Mapping

## Overview
This document maps all symbols from `therapeutic_safety.py` (3,529 lines, 21 classes) to the 4 new components.

## Component Breakdown

### 1. safety_validation/ (Safety Checks and Validation Logic)
**Purpose:** Core validation rules, rule engine, and validation result models.

**Classes (6):**
- `SafetyLevel` (Enum, line 65) - Safety level enumeration (SAFE, WARNING, BLOCKED)
- `ValidationType` (Enum, line 71) - Validation algorithm types
- `ValidationFinding` (dataclass, line 133) - Individual validation finding
- `ValidationResult` (dataclass, line 152) - Complete validation result
- `SafetyRule` (dataclass, line 240) - Safety rule definition
- `SafetyRuleEngine` (class, line 265) - Rule evaluation engine

**Rationale:** These classes form the core validation infrastructure. They define what safety means, how rules are structured, and how validation is performed. This is the foundation that other components build upon.

**Dependencies:**
- Standard library: re, dataclasses, enum, typing
- Internal: Uses SafetyLevel, ValidationType enums

**Public API:**
- SafetyLevel, ValidationType (enums for external use)
- ValidationFinding, ValidationResult (result models)
- SafetyRule, SafetyRuleEngine (rule definition and execution)

---

### 2. crisis_detection/ (Crisis Detection and Handling)
**Purpose:** Crisis assessment, intervention management, and emergency protocols.

**Classes (10):**
- `CrisisType` (Enum, line 81) - Types of crisis situations
- `CrisisLevel` (Enum, line 104) - Crisis severity levels
- `InterventionType` (Enum, line 113) - Types of interventions
- `EscalationStatus` (Enum, line 122) - Escalation status tracking
- `CrisisAssessment` (dataclass, line 194) - Crisis assessment result
- `InterventionAction` (dataclass, line 210) - Individual intervention action
- `CrisisIntervention` (dataclass, line 222) - Complete intervention record
- `CrisisInterventionManager` (class, line 1162) - Manages crisis interventions
- `EmergencyProtocolEngine` (class, line 1798) - Emergency protocol execution
- `HumanOversightEscalation` (class, line 2272) - Human oversight escalation

**Rationale:** These classes handle the critical path for crisis situations. They detect crises, assess severity, manage interventions, and escalate to human oversight when needed. This is a cohesive unit focused on crisis response.

**Dependencies:**
- Standard library: time, dataclasses, enum, typing
- Internal: Depends on safety_validation (SafetyLevel, ValidationResult)
- External: May use Redis for persistence

**Public API:**
- CrisisType, CrisisLevel, InterventionType, EscalationStatus (enums)
- CrisisAssessment, InterventionAction, CrisisIntervention (models)
- CrisisInterventionManager, EmergencyProtocolEngine, HumanOversightEscalation (managers)

---

### 3. therapeutic_scoring/ (Therapeutic Appropriateness Scoring)
**Purpose:** Therapeutic context validation and appropriateness scoring.

**Classes (2):**
- `TherapeuticContext` (Enum, line 93) - Therapeutic context types
- `TherapeuticValidator` (class, line 651) - Main therapeutic validation orchestrator

**Rationale:** TherapeuticValidator is the main orchestrator that coordinates validation across multiple dimensions. It uses the safety_validation engine and crisis_detection components to provide comprehensive therapeutic appropriateness scoring. This is the high-level API that most code will interact with.

**Dependencies:**
- Standard library: json, typing
- Internal: Depends on safety_validation (SafetyRuleEngine, ValidationResult, SafetyLevel)
- Internal: Depends on crisis_detection (CrisisType, CrisisLevel)
- External: Optional yaml support

**Public API:**
- TherapeuticContext (enum)
- TherapeuticValidator (main validation orchestrator)

---

### 4. safety_monitoring/ (Safety Metrics and Monitoring)
**Purpose:** Safety metrics collection, monitoring dashboard, and service orchestration.

**Classes (3):**
- `SafetyMonitoringDashboard` (class, line 2771) - Metrics dashboard
- `SafetyRulesProvider` (class, line 3348) - Redis-backed rules provider
- `SafetyService` (class, line 3431) - Service orchestration layer

**Functions (2):**
- `get_global_safety_service()` (line 3483) - Global service accessor
- `set_global_safety_service_for_testing()` (line 3526) - Testing hook

**Rationale:** These classes provide observability and service management. SafetyMonitoringDashboard tracks metrics, SafetyRulesProvider manages configuration, and SafetyService orchestrates the entire safety system. This is the operational layer.

**Dependencies:**
- Standard library: json, time, typing
- Internal: Depends on safety_validation (ValidationResult)
- Internal: Depends on therapeutic_scoring (TherapeuticValidator)
- External: Redis (optional, with fallback)
- **BUG FOUND:** Uses `contextlib.suppress` but doesn't import contextlib!

**Public API:**
- SafetyMonitoringDashboard (metrics and monitoring)
- SafetyRulesProvider (configuration management)
- SafetyService (main service orchestrator)
- get_global_safety_service() (global accessor)
- set_global_safety_service_for_testing() (testing hook)

---

## Shared Utilities
**None identified** - All symbols are cleanly categorized into the 4 components.

---

## Import Dependencies Summary

### External Dependencies:
- **Standard Library:** json, re, time, dataclasses, enum, typing
- **Optional:** yaml (try/except for YAML config support)
- **Optional:** redis.asyncio (try/except for Redis integration)
- **BUG:** contextlib used but not imported (lines 3375, 3513)

### Inter-Component Dependencies:
```
safety_validation (foundation)
    ↓
crisis_detection (depends on safety_validation)
    ↓
therapeutic_scoring (depends on both safety_validation and crisis_detection)
    ↓
safety_monitoring (depends on therapeutic_scoring, which transitively includes all)
```

---

## Migration Notes

### Backward Compatibility Strategy:
1. Create 4 new component directories with extracted code
2. Refactor `therapeutic_safety.py` to become a compatibility shim
3. Re-export all public symbols from the shim
4. No breaking changes to public API

### Public API Surface (must be preserved):
From `src/agent_orchestration/__init__.py`:
```python
from .therapeutic_safety import (
    SafetyLevel,
    SafetyService,
    TherapeuticValidator,
    get_global_safety_service,
)
```

All other classes may be used internally but are not part of the main package exports.

---

## Issues Found

### 1. Missing Import (BUG)
**Location:** Lines 3375, 3513
**Issue:** `contextlib.suppress()` is used but `contextlib` is never imported
**Fix:** Add `import contextlib` to imports section
**Component:** safety_monitoring

### 2. Inline Imports
**Location:** Various (e.g., line 3331 `import json`, line 3501 `import redis.asyncio`)
**Issue:** Imports inside functions/methods
**Fix:** Move to top-level imports or keep as-is for optional dependencies
**Decision:** Keep optional dependencies as try/except, move json to top

---

## Downstream Dependencies Analysis

### Files Importing from therapeutic_safety.py (24 files total)

#### src/agent_orchestration/ (4 files)
1. **`__init__.py`** (line 74-79)
   - Imports: `SafetyLevel`, `SafetyService`, `TherapeuticValidator`, `get_global_safety_service`
   - **PUBLIC API** - These are re-exported to package users
   - **CRITICAL:** Must maintain exact compatibility

2. **`service.py`** (line 623)
   - Imports: `SafetyLevel`, `TherapeuticValidator`
   - Usage: Inline import to avoid circular dependencies
   - Used in `_validate_therapeutic_content()` method

3. **`proxies.py`** (line 14)
   - Imports: `SafetyLevel`, `get_global_safety_service`
   - Usage: Agent proxy validation

4. **`unified_orchestrator.py`** (line 22)
   - Imports: `SafetyLevel`, `get_global_safety_service`
   - Usage: Orchestration workflow validation

#### src/components/ (1 file)
5. **`agent_orchestration_component.py`**
   - Imports: Uses `tta_ai.orchestration.therapeutic_safety`
   - Imports multiple symbols (needs detailed check)

#### src/integration/ (1 file)
6. **`gameplay_loop_integration.py`**
   - Imports: `SafetyLevel`, `SafetyService`
   - Usage: Integration layer validation

#### src/player_experience/ (2 files)
7. **`services/gameplay_service.py`**
   - Imports: `SafetyService`
   - Usage: Inline import for gameplay validation

8. **`api/routers/chat.py`**
   - Imports: Uses `tta_ai.orchestration.therapeutic_safety`
   - Usage: Chat API validation

#### tests/agent_orchestration/ (11 files)
9. **`test_therapeutic_safety.py`**
   - Imports: `SafetyLevel`, `SafetyRulesProvider`, `SafetyService`, `TherapeuticValidator`

10. **`test_enhanced_therapeutic_safety.py`**
    - Imports: `CrisisType`, `SafetyLevel`, `TherapeuticValidator`, `ValidationResult`, `ValidationType`

11. **`test_crisis_intervention_system.py`**
    - Imports: `CrisisInterventionManager`, `CrisisLevel`, `CrisisType`, `EmergencyProtocolEngine`, `EscalationStatus`, `HumanOversightEscalation`, `InterventionType`, `SafetyMonitoringDashboard`, `TherapeuticValidator`

12. **`test_crisis_detection_scenarios.py`**
    - Imports: Multiple crisis-related symbols

13. **`test_therapeutic_safety_integration.py`**
    - Imports: `SafetyLevel`, `TherapeuticValidator`

14. **`test_unified_orchestrator.py`**
    - Imports: Multiple symbols

15. **`test_therapeutic_validator_performance.py`**
    - Imports: Performance testing symbols

16. **`test_therapeutic_content_validation.py`**
    - Imports: Content validation symbols

17. **`test_performance_validation.py`**
    - Imports: Performance symbols

18. **`test_session_state_validation.py`**
    - Imports: Session validation symbols

19. **`test_end_to_end_validation.py`**
    - Imports: E2E testing symbols

#### packages/tta-ai-framework/ (4 files - DUPLICATE CODE)
20. **`src/tta_ai/orchestration/__init__.py`**
    - Imports: Same as src/agent_orchestration/__init__.py
    - **MUST BE KEPT IN SYNC**

21. **`src/tta_ai/orchestration/service.py`**
    - Imports: Same as src/agent_orchestration/service.py

22. **`src/tta_ai/orchestration/proxies.py`**
    - Imports: Same as src/agent_orchestration/proxies.py

23. **`src/tta_ai/orchestration/unified_orchestrator.py`**
    - Imports: Same as src/agent_orchestration/unified_orchestrator.py

---

### Public API Surface (MUST PRESERVE)

From `src/agent_orchestration/__init__.py`:
```python
from .therapeutic_safety import (
    SafetyLevel,           # Enum - safety_validation component
    SafetyService,         # Class - safety_monitoring component
    TherapeuticValidator,  # Class - therapeutic_scoring component
    get_global_safety_service,  # Function - safety_monitoring component
)
```

**Critical:** These 4 symbols are the public API. All other symbols are internal but may be used by tests.

---

### Symbols Used Across Codebase

**Most Frequently Used (PUBLIC API):**
1. `SafetyLevel` - Used in 10+ files
2. `TherapeuticValidator` - Used in 10+ files
3. `SafetyService` - Used in 5+ files
4. `get_global_safety_service` - Used in 3+ files

**Frequently Used (INTERNAL/TESTS):**
5. `ValidationResult` - Used in tests
6. `CrisisType` - Used in tests
7. `CrisisLevel` - Used in tests
8. `CrisisInterventionManager` - Used in tests
9. `SafetyRulesProvider` - Used in tests
10. `ValidationType` - Used in tests

**Less Frequently Used (TESTS ONLY):**
- `EmergencyProtocolEngine`
- `HumanOversightEscalation`
- `SafetyMonitoringDashboard`
- `InterventionType`
- `EscalationStatus`

---

### Backward Compatibility Plan

**Phase 1: Create New Components**
1. Create 4 new component directories with extracted code
2. Ensure all symbols work in new locations
3. All tests pass with new imports

**Phase 2: Create Compatibility Shim**
1. Refactor `therapeutic_safety.py` to re-export all symbols:
```python
# Backward compatibility shim
from .safety_validation import (
    SafetyLevel,
    ValidationType,
    ValidationFinding,
    ValidationResult,
    SafetyRule,
    SafetyRuleEngine,
)
from .crisis_detection import (
    CrisisType,
    CrisisLevel,
    InterventionType,
    EscalationStatus,
    CrisisAssessment,
    InterventionAction,
    CrisisIntervention,
    CrisisInterventionManager,
    EmergencyProtocolEngine,
    HumanOversightEscalation,
)
from .therapeutic_scoring import (
    TherapeuticContext,
    TherapeuticValidator,
)
from .safety_monitoring import (
    SafetyMonitoringDashboard,
    SafetyRulesProvider,
    SafetyService,
    get_global_safety_service,
    set_global_safety_service_for_testing,
)

__all__ = [
    # All symbols listed above
]
```

**Phase 3: Verify No Breaking Changes**
1. All existing imports continue to work
2. All tests pass without modification
3. Public API unchanged

**Phase 4: Optional Migration (Future)**
1. Update imports to use new component locations (optional)
2. Add deprecation warnings to shim (optional)
3. Eventually remove shim (far future, not in this phase)

---

## Verification Checklist
- [x] All 21 classes mapped to components
- [x] All 2 functions mapped to components
- [x] All dependencies identified
- [x] Inter-component dependencies documented
- [x] Public API surface identified
- [x] Backward compatibility strategy defined
- [x] Issues/bugs documented
- [x] No symbols unaccounted for
- [x] All downstream callers identified (24 files)
- [x] Public API symbols documented (4 symbols)
- [x] Backward compatibility plan created
- [x] No hidden dependencies found
