# TTA Architecture

**Last Updated:** 2026-01-09
**Status:** Two-layer toolkit approach

---

## 🏗️ Overview

TTA uses a **two-layer toolkit architecture** to separate universal patterns from game-specific logic:

```
Layer 1: TTA.dev (Universal)
           ↓ provides foundation
Layer 2: TTA Game Toolkit (Narrative-specific)
           ↓ builds features
Layer 3: TTA Game (Player-facing)
```

---

## 📊 Architecture Layers

### Layer 1: Universal Toolkit (TTA.dev)

**Location:** `~/repos/TTA.dev/platform/`
**Purpose:** Domain-agnostic patterns reusable across any project

**Packages:**
- `agent-coordination/` - Generic multi-agent patterns
- `primitives/` - Retry, fallback, timeout, cache
- `observability/` - OpenTelemetry tracing & metrics
- `agent-context/` - Universal state management

**Example:**
```python
from tta_dev.agent_coordination import AgentCoordinator
# Works for ANY multi-agent system (game, data pipeline, etc.)
```

### Layer 2: Game-Specific Toolkit (TTA repo)

**Location:** `~/repos/TTA/src/`
**Purpose:** Narrative and therapeutic extensions of universal patterns

**Components:**
```
src/agent_orchestration/     (3.8MB, 123 files)
├── Narrative-specific agent coordination
├── Story + therapy balance logic
└── Extends TTA.dev's AgentCoordinator

src/components/              (3.7MB, 84 files)
├── gameplay_loop/           - Game control flow
├── narrative_arc_orchestrator/ - Story structure
├── narrative_coherence_engine/ - Consistency
└── therapeutic_systems/     - Mental health mechanics

src/orchestration/           (192KB, 7 files)
└── High-level game orchestration

src/monitoring/              (128KB, 7 files)
└── Game-specific health checks

src/observability_integration/ (124KB, 6 files)
└── TTA-specific instrumentation
```

**Example:**
```python
from tta_dev.agent_coordination import AgentCoordinator
from tta.agent_orchestration import NarrativeCoordinator

class NarrativeCoordinator(AgentCoordinator):
    """Extends universal coordination with story + therapy logic"""

    def coordinate_narrative(self, story_context, therapeutic_goals):
        # Game-specific: Balance narrative coherence + therapeutic value
        narrator = self.get_agent("narrator")
        therapist = self.get_agent("therapeutic_guide")
        world_sim = self.get_agent("world_simulator")

        # This orchestration is TTA-specific
        return self._balance_story_and_therapy(...)
```

### Layer 3: Game Features (Player-facing)

**Location:** `~/repos/TTA/src/`
**Purpose:** What players interact with

**Components:**
```
src/player_experience/       (1.2GB)
├── frontend/                - React/TypeScript UI
├── api/                     - Game API endpoints
├── services/                - Gameplay services
└── database/                - World persistence

src/living_worlds/           (52KB)
└── Dynamic world generation
```

---

## 🎯 Decision Tree: Where Does Code Go?

### Question 1: Is it player-facing?

**YES** → `TTA/src/player_experience/` or `TTA/src/living_worlds/`

Examples:
- Character creation UI
- Game controls
- World visualization
- Player stats display

### Question 2: Is it specific to storytelling/therapy?

**YES** → `TTA/src/agent_orchestration/` or `TTA/src/components/`

Examples:
- Narrative arc management
- Therapeutic goal tracking
- Story coherence checks
- Narrator agent behavior

### Question 3: Could it work for a recipe app?

**YES** → `TTA.dev/platform/`

Examples:
- Retry on API failure
- Generic agent coordination
- Tracing/observability patterns
- Circuit breaker logic

**NO** → Keep in TTA

Examples:
- Story-specific agent coordination
- Therapeutic mechanics
- Narrative algorithms

---

## 📦 Package Dependencies

### TTA depends on TTA.dev

```python
# TTA/requirements.txt (development)
-e ../TTA.dev/platform/primitives
-e ../TTA.dev/platform/observability
-e ../TTA.dev/platform/agent-context

# Then game-specific dependencies
fastapi>=0.104.0
uvicorn>=0.24.0
# ... etc
```

### TTA.dev is independent

```python
# TTA.dev has NO dependency on TTA
# It's domain-agnostic and reusable
```

---

## 🔄 Development Workflow

### When Building New Features

1. **Need generic pattern?**
   ```
   Example: Need circuit breaker for LLM calls

   → Add to TTA.dev/platform/primitives
   → Test in TTA
   → Now available for tta-solo and future projects
   ```

2. **Need game-specific orchestration?**
   ```
   Example: Need to coordinate narrator + therapist agents

   → Add to TTA/src/agent_orchestration/
   → Use TTA.dev patterns internally
   → Stays specific to therapeutic narratives
   ```

3. **Need player feature?**
   ```
   Example: Character customization screen

   → Add to TTA/src/player_experience/frontend
   → Uses game toolkit for backend logic
   → Player-facing, game-specific
   ```

### Pattern Extraction

When code in TTA proves useful AND domain-agnostic:

1. Extract to TTA.dev
2. Generalize (remove game-specific assumptions)
3. Test in TTA
4. Refactor TTA to use new TTA.dev pattern
5. Benefit: Now available for all projects!

---

## 🎓 Why This Architecture?

### Benefits

**Separation of Concerns:**
- Universal patterns don't get polluted with game logic
- Game logic doesn't pretend to be universal
- Clear boundaries reduce confusion

**Code Reuse:**
- TTA.dev patterns work for recipe apps, data pipelines, etc.
- Don't have to extract game logic when reusing
- New projects start with clean foundation

**Maintainability:**
- Universal code is small and focused
- Game code can be messy during prototyping
- Clear rules: "Where does this go?"

**Future-Proofing:**
- TTA.dev can evolve independently
- Can add new consumers without touching TTA game
- Option to publish TTA.dev later (no pressure!)

---

## 🚀 Example: Building New Feature

### Scenario: Add "Story Checkpoint" Feature

**Step 1: Universal part**
```python
# TTA.dev: Add generic checkpoint pattern
# Location: TTA.dev/platform/primitives/checkpoint.py

class CheckpointPrimitive:
    """Generic checkpoint/savepoint pattern"""
    def save_state(self, state): ...
    def restore_state(self, checkpoint_id): ...
```

**Step 2: Game-specific part**
```python
# TTA: Extend for narrative checkpoints
# Location: TTA/src/components/narrative_checkpoints.py

from tta_dev_primitives import CheckpointPrimitive
from tta.agent_orchestration import NarrativeCoordinator

class NarrativeCheckpoint(CheckpointPrimitive):
    """Story checkpoint with therapeutic context"""

    def save_story_state(self, story_context, therapeutic_progress):
        # Game-specific: Save narrative state + therapy progress
        state = {
            'narrative': story_context,
            'therapy': therapeutic_progress,
            'character': self._get_character_state(),
            'world': self._get_world_state()
        }
        return self.save_state(state)
```

**Step 3: Player-facing part**
```python
# TTA: Add UI for checkpoints
# Location: TTA/src/player_experience/frontend/components/Checkpoints.tsx

import { useGameState } from './hooks'

export function CheckpointButton() {
    const { saveCheckpoint } = useGameState()

    return (
        <button onClick={saveCheckpoint}>
            Save Story Progress
        </button>
    )
}
```

---

## 📝 Repository Structure Summary

```
TTA.dev/                           (Universal toolkit)
└── platform/
    ├── agent-coordination/        Generic patterns
    ├── primitives/                Retry, fallback, etc.
    └── observability/             Tracing

TTA/                               (Game + Game toolkit)
├── src/agent_orchestration/       Narrative coordination
├── src/components/                Story/therapy systems
├── src/orchestration/             Game control flow
├── src/player_experience/         Player UI & features
└── src/living_worlds/             World generation
```

---

## ✅ Architecture Principles

1. **TTA.dev = Universal:** No game logic, works for any domain
2. **TTA Toolkit = Game-specific:** Narrative/therapy extensions
3. **TTA Game = Player-facing:** What users interact with
4. **Dependency:** TTA imports TTA.dev (not reverse)
5. **Pattern flow:** Prove in TTA → Extract to TTA.dev → Reuse everywhere

---

## 🎯 Success Metrics

You know the architecture is working when:

- [ ] Can answer "Where does this code go?" in < 10 seconds
- [ ] TTA.dev has zero game-specific logic
- [ ] TTA toolkit clearly extends TTA.dev patterns
- [ ] New projects can import TTA.dev cleanly
- [ ] No confusion about universal vs game-specific

---

**Generated:** 2026-01-09
**Philosophy:** Build for yourself, extract patterns as they prove useful, no pressure to publish
