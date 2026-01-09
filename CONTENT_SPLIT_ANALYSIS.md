# Content Split Analysis: recovered-tta-storytelling

**Date:** 2026-01-09
**Purpose:** Identify what goes to TTA (game) vs TTA.dev (toolkit)

---

## 🎯 The Two Projects

Based on README analysis, recovered-tta-storytelling contains TWO distinct concerns:

### TTA (The Game) 🎮
- **Therapeutic Text Adventure** - Narrative storytelling game
- **Purpose:** Therapeutic gaming experience
- **Content:** Game logic, narrative engine, player experience

### TTA.dev (The Toolkit) 🛠️
- **AI Development Toolkit**
- **Purpose:** Agentic primitives and workflow patterns
- **Content:** Platform, primitives, infrastructure

**Key Quote from README:**
> "TTA (This Repo): The Game & Narrative Content"
> "TTA.dev: The Platform & Infrastructure"

---

## 📊 Content Breakdown by Destination

### → TTA Game Repository

**Game-Specific Content (1.3GB):**

```
src/player_experience/ (1.2GB) - 82 Python files
├── frontend/           # React/TypeScript game UI
├── api/routers/        # Game API endpoints
│   ├── gameplay.py
│   ├── narrative_v2.py
│   └── worlds.py
├── services/
│   ├── gameplay_service.py
│   └── default_character_world_service.py
├── database/
│   └── world_repository.py
├── managers/
│   ├── world_management_module.py
│   └── ai_world_generator.py
├── models/
│   └── world.py
└── franchise_worlds/   # World/character data

src/living_worlds/ (52KB) - 1 Python file
└── Dynamic world generation

src/components/ (partial - 3.7M total)
├── narrative_arc_orchestrator_component.py
├── narrative_coherence_engine.py
├── gameplay_loop_component.py
├── gameplay_loop/
│   └── narrative/
│       └── therapeutic_storyteller.py
└── player_experience/

src/integration/ (partial)
└── gameplay_loop_integration.py

AI Prompts:
└── src/ai_components/prompts/*/narrative_generation.yaml
```

**Infrastructure (27MB):**
```
nginx/ (27MB)
└── Web server configs for game hosting
```

**Documentation:**
```
_archive/ (12MB) - Historical game development
docs/ (6.2MB) - Game-specific documentation
```

### → TTA.dev Repository

**Platform/Toolkit Content:**

```
platform/ (?)
├── app/
└── dev/

src/agent_orchestration/ (3.8MB) - 123 Python files
src/orchestration/ (192KB) - 7 Python files
src/monitoring/ (128KB) - 7 Python files
src/observability_integration/ (124KB) - 6 Python files
src/ai_components/ (partial - 124KB) - 3 Python files
src/analytics/ (120KB) - 3 Python files
src/api_gateway/ (24KB) - 1 Python file
src/common/ (56KB) - 3 Python files
src/infrastructure/ (4KB)
src/developer_dashboard/ (36KB) - 2 Python files
```

**Question:** TTA.dev already has:
- `platform/agent-context`
- `platform/agent-coordination`
- `platform/observability`
- `platform/primitives`

Does it already have the content from recovered-tta-storytelling's platform/ and src/?

---

## 🔍 Current State Analysis

### What Exists Now

**TTA.dev (2.0GB):** Clean, optimized toolkit
- Has platform/ with 7 packages
- Has docs/, scripts/, tests/
- NO game content

**tta-solo (201MB):** Development environment
- Docker compose setup
- May or may not have game code

**recovered-tta-storytelling (24GB):** Both mixed together
- Has platform/ (toolkit)
- Has src/ with BOTH game AND toolkit code
- Completely unmanageable

### What's Missing

**TTA Game Repository:** Doesn't appear to exist as separate repo!
- recovered-tta-storytelling README says "TTA (This Repo): The Game"
- But the repo name suggests it's a "recovered" version
- Need to find/create proper TTA game repository

---

## 🎯 Extraction Plan

### Option A: Create New TTA Game Repo

```bash
# 1. Create new TTA game repository
cd ~/repos
git clone <TTA-game-remote> TTA  # or git init TTA

# 2. Extract game content
cd recovered-tta-storytelling
cp -r src/player_experience ../TTA/src/
cp -r src/living_worlds ../TTA/src/
cp -r src/components/gameplay_loop ../TTA/src/components/
cp -r src/components/narrative* ../TTA/src/components/
cp -r nginx ../TTA/
cp -r _archive ../TTA/
cp README.md ../TTA/  # It's already game-focused

# 3. Clean up and commit
cd ../TTA
rm -rf src/player_experience/frontend/node_modules  # Don't commit this
# Add proper .gitignore
git add .
git commit -m "Initial: Extract game content from recovered-tta-storytelling"
```

### Option B: Use tta-solo as TTA Game

If tta-solo is intended to be the game:
```bash
cd ~/repos/tta-solo
# Merge game content from recovered-tta-storytelling
# ...
```

### Option C: recovered-tta-storytelling IS the game (just cleanup)

Maybe recovered-tta-storytelling should stay as the game repo:
```bash
cd ~/repos/recovered-tta-storytelling

# 1. Remove bloat
rm -rf venv-staging/ .venv/ list/
rm -rf test-results-staging/ playwright-staging-report/ htmlcov/

# 2. Remove toolkit code (already in TTA.dev)
# Compare and remove duplicates with TTA.dev

# 3. Rename repository
cd ~/repos
mv recovered-tta-storytelling TTA

# 4. Clean git history
cd TTA
git filter-repo ...
```

---

## 🤔 Questions to Answer

1. **Does a TTA game repository already exist?**
   - Check GitHub for theinterneti/TTA or similar
   - Check if tta-solo is the game repo
   - Or do we need to create it from scratch?

2. **What's in TTA.dev that came from recovered-tta-storytelling?**
   - Compare platform/ directories
   - Compare src/agent_orchestration, src/orchestration, etc.
   - Are they duplicates or unique content?

3. **What's the relationship with tta-solo?**
   - Is tta-solo the game?
   - Is it just a dev environment?
   - Does it have game content already?

4. **Do we keep recovered-tta-storytelling name or rename to TTA?**
   - README already calls it "TTA"
   - Name suggests it's a recovery/backup
   - Should it be the canonical TTA game repo?

---

## 📋 Recommended Next Steps

### Step 1: Investigate Existing Repos

```bash
# Check remote for TTA game
cd ~/repos/recovered-tta-storytelling
git remote -v

# Check tta-solo purpose
cd ~/repos/tta-solo
cat README.md
ls -la

# Check if TTA.dev came from this
cd ~/repos/TTA.dev
git log --all --oneline | head -20
# Look for "import from" or "extracted from" messages
```

### Step 2: Compare Content

```bash
# Compare platform directories
diff -qr ~/repos/recovered-tta-storytelling/platform \
        ~/repos/TTA.dev/platform

# Compare agent_orchestration
# Does TTA.dev have this already?
```

### Step 3: Decide Repository Structure

Choose one:

**A. Three Repos:**
```
TTA/        (new) - Game content only
TTA.dev/    (exists) - Toolkit only
tta-solo/   (exists) - Dev environment
```

**B. Two Repos:**
```
TTA/        (rename recovered-tta-storytelling) - Game
TTA.dev/    (exists) - Toolkit
# tta-solo absorbed into one of the above
```

**C. Keep Current + Cleanup:**
```
recovered-tta-storytelling/ (cleanup) - Game archive/reference
TTA.dev/    (exists) - Active toolkit
tta-solo/   (exists) - Active game development
```

---

## ✅ Success Criteria

- [ ] Game content extracted to proper TTA game repository
- [ ] Toolkit content verified in TTA.dev (no duplicates)
- [ ] No loss of unique game features
- [ ] recovered-tta-storytelling either cleaned or archived
- [ ] Clear separation: Game vs Toolkit
- [ ] 24GB freed (or reduced to <1GB if keeping)

---

**Generated:** 2026-01-09
**Next:** Determine destination repositories and extraction strategy
