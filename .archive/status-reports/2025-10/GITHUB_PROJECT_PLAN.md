# TTA Component Packaging - GitHub Project Plan

**Status:** Milestones created ✅
**Date:** 2025-10-26
**Repository:** theinterneti/TTA

---

## Milestones Created

### ✅ Milestone 2: MVP Foundation - Core Features
- **Due:** November 15, 2025
- **Description:** Current MVP priority - core therapeutic narrative features
- **Link:** https://github.com/theinterneti/TTA/milestone/2

### ✅ Milestone 3: Packaging Phase 1 - Foundation
- **Due:** November 8, 2025
- **Description:** Extract foundational packages (tta-common, tta-monitoring)
- **Link:** https://github.com/theinterneti/TTA/milestone/3

### ✅ Milestone 4: Packaging Phase 2 - Consolidation
- **Due:** November 22, 2025
- **Description:** Audit and merge agent_orchestration with tta-ai-framework
- **Link:** https://github.com/theinterneti/TTA/milestone/4

### ✅ Milestone 5: Packaging Phase 3 - Domain Packages
- **Due:** December 13, 2025
- **Description:** Extract player experience and component libraries
- **Link:** https://github.com/theinterneti/TTA/milestone/5

---

## Issues to Create Manually

> **Note:** Labels need to be created first. Create these labels:
> - `packaging` - Component packaging work
> - `mvp` - MVP-related tasks
> - `priority:high`, `priority:medium`, `priority:low` - Priority levels
> - `infrastructure` - Infrastructure work
> - `observability` - Monitoring/observability
> - `architecture` - Architecture decisions
> - `investigation` - Research/analysis needed

### Phase 1 Issues (Milestone 3)

#### Issue 1: Create tta-common foundational package
**Labels:** `packaging`, `priority:high`, `infrastructure`

**Body:**
```markdown
## Goal
Extract common utilities, types, and exceptions into a foundational package.

## Motivation
- Zero dependencies, used by multiple components
- Foundation for other packages
- Reduces code duplication

## Tasks
- [ ] Create package structure in `packages/tta-common/`
- [ ] Move files from `src/common/` (3 files, 15 definitions)
- [ ] Update imports across codebase
- [ ] Write tests
- [ ] Create README and documentation
- [ ] Configure pyproject.toml
- [ ] Install as editable package: `uv pip install -e packages/tta-common`

## Success Criteria
- [ ] Package installs successfully
- [ ] All tests pass
- [ ] Zero import errors in main app
- [ ] Documentation complete

**Priority:** HIGH - Blocks other packaging work
**Effort:** 1-2 days
**Phase:** Foundation (Week 1)
```

#### Issue 2: Create tta-monitoring infrastructure package
**Labels:** `packaging`, `priority:high`, `infrastructure`, `observability`

**Body:**
```markdown
## Goal
Extract monitoring and analytics into a reusable infrastructure package.

## Motivation
- Zero external dependencies (only needs tta-common)
- Highly reusable across projects
- Clean separation from business logic

## Tasks
- [ ] Create package structure in `packages/tta-monitoring/`
- [ ] Move `src/monitoring/` (7 files, 36 definitions)
- [ ] Move `src/analytics/` (3 files, 43 definitions)
- [ ] Organize into metrics, observability, analytics modules
- [ ] Update imports across codebase
- [ ] Add Prometheus and Grafana integration examples
- [ ] Write tests
- [ ] Create README and documentation
- [ ] Install as editable package

## Success Criteria
- [ ] Package installs successfully
- [ ] All tests pass
- [ ] Metrics collection working
- [ ] Grafana dashboards importable
- [ ] Documentation complete

**Priority:** HIGH - Foundation package
**Effort:** 2-3 days
**Phase:** Foundation (Week 1)
**Depends on:** tta-common
```

### Phase 2 Issues (Milestone 4)

#### Issue 3: Audit agent_orchestration vs tta-ai-framework overlap
**Labels:** `packaging`, `priority:medium`, `architecture`, `investigation`

**Body:**
```markdown
## Goal
Identify duplicate code between `src/agent_orchestration/` (120 files) and `packages/tta-ai-framework/`.

## Motivation
- Likely significant overlap
- Need to consolidate before further packaging
- Ensure clean architecture

## Tasks
- [ ] Map functionality in both locations
- [ ] Identify duplicate code
- [ ] Identify unique agent_orchestration code
- [ ] Determine application-specific vs reusable code
- [ ] Document findings in audit report
- [ ] Create consolidation plan

## Deliverables
- [ ] Audit report document
- [ ] Code overlap matrix
- [ ] Migration plan

## Success Criteria
- [ ] Clear understanding of overlap
- [ ] Decision on what to keep/merge/delete
- [ ] Migration plan approved

**Priority:** MEDIUM - Critical for architecture
**Effort:** 3-5 days
**Phase:** Consolidation (Week 2-3)
```

#### Issue 4: Merge agent_orchestration into tta-ai-framework
**Labels:** `packaging`, `priority:medium`, `architecture`

**Body:**
```markdown
## Goal
Consolidate agent orchestration code into the tta-ai-framework package.

## Prerequisites
- [ ] Audit completed

## Tasks
- [ ] Move unique code from agent_orchestration to tta-ai-framework
- [ ] Update all imports
- [ ] Update tta-ai-framework version
- [ ] Remove duplicate code
- [ ] Keep application-specific code in src/
- [ ] Write tests for migrated code
- [ ] Update documentation

## Success Criteria
- [ ] All tests pass
- [ ] No duplicate code
- [ ] Clear responsibility boundaries
- [ ] tta-ai-framework version bumped

**Priority:** MEDIUM
**Effort:** 3-5 days
**Phase:** Consolidation (Week 2-3)
**Depends on:** Audit issue
```

### Phase 3 Issues (Milestone 5)

#### Issue 5: Create tta-player-experience package
**Labels:** `packaging`, `priority:medium`, `feature`

**Body:**
```markdown
## Goal
Extract player-facing features into an independent package.

## Motivation
- Large, well-defined domain (80 files, 543 definitions)
- Minimal dependencies (tta-common, tta-monitoring)
- Can version player features separately

## Prerequisites
- [ ] tta-common package exists
- [ ] tta-monitoring package exists

## Tasks
- [ ] Create package structure in `packages/tta-player-experience/`
- [ ] Move files from `src/player_experience/`
- [ ] Organize into api, managers, services, models modules
- [ ] Update imports across codebase
- [ ] Write tests
- [ ] Create README and API documentation
- [ ] Install as editable package

## Success Criteria
- [ ] Package installs successfully
- [ ] All tests pass
- [ ] Player API functional
- [ ] Documentation complete

**Priority:** MEDIUM
**Effort:** 3-5 days
**Phase:** Domain Packages (Week 4+)
**Depends on:** tta-common, tta-monitoring
```

#### Issue 6: Split tta-components into domain packages
**Labels:** `packaging`, `priority:low`, `architecture`

**Body:**
```markdown
## Goal
Split large components directory into focused, reusable packages.

## Motivation
- 84 files, 288 definitions - too large
- Multiple domains mixed together
- Better to have focused packages

## Packages to Create
1. **tta-gameplay-components**
   - gameplay_loop, adventure_experience, living_worlds

2. **tta-narrative-components**
   - arc_orchestrator, coherence_validator, story_elements

3. **tta-therapeutic-components**
   - scoring, safety, interventions

## Tasks
- [ ] Plan component split
- [ ] Create tta-gameplay-components package
- [ ] Create tta-narrative-components package
- [ ] Create tta-therapeutic-components package
- [ ] Move code from src/components
- [ ] Update imports
- [ ] Write tests
- [ ] Documentation for each package

## Dependencies
- tta-common
- tta-ai-framework
- tta-narrative-engine

## Success Criteria
- [ ] 3 new packages created
- [ ] All tests pass
- [ ] Clear domain boundaries
- [ ] Documentation complete

**Priority:** LOW - Can be done incrementally
**Effort:** 5-7 days
**Phase:** Domain Packages (Week 4+)
```

### MVP Tracking Issues (Milestone 2)

#### Issue 7: [MVP] Track workflow primitive adoption and impact
**Labels:** `mvp`, `priority:high`, `metrics`

**Body:**
```markdown
## Goal
Monitor how new workflow primitives affect MVP development velocity.

## Metrics to Track
- [ ] Time to implement new workflows
- [ ] Code reuse percentage (target: 80%+)
- [ ] Test coverage increase
- [ ] Bug reduction
- [ ] Developer satisfaction

## Actions
- [ ] Weekly check-in on primitive usage
- [ ] Collect developer feedback
- [ ] Document best practices
- [ ] Adjust approach based on feedback

## Success Criteria
- [ ] Primitives used in 80%+ new workflows
- [ ] Positive developer feedback
- [ ] Faster feature development
- [ ] Higher code quality

**Priority:** HIGH - MVP tracking
**Phase:** Ongoing during MVP
```

#### Issue 8: [MVP] Update architecture documentation
**Labels:** `mvp`, `priority:medium`, `documentation`

**Body:**
```markdown
## Goal
Update architecture docs to reflect new packaging strategy.

## Tasks
- [ ] Update architecture diagrams
- [ ] Document package dependencies
- [ ] Add packaging guidelines
- [ ] Update developer onboarding docs
- [ ] Create package usage examples

## Documents to Update
- [ ] AGENTIC_PRIMITIVES_IMPLEMENTATION.md ✅
- [ ] COMPONENT_PACKAGING_STRATEGY.md ✅
- [ ] README.md
- [ ] docs/architecture/README.md
- [ ] CONTRIBUTING.md

## Success Criteria
- [ ] Clear package dependency graph
- [ ] Developer guidelines complete
- [ ] Examples for each package
- [ ] Onboarding updated

**Priority:** MEDIUM
**Phase:** Ongoing during MVP
```

---

## Project Board Structure (Manual Setup)

### Columns

1. **📋 Backlog** - Not yet started
2. **🎯 Ready** - Ready to work on
3. **🔄 In Progress** - Currently being worked on
4. **👀 Review** - Ready for review
5. **✅ Done** - Completed

### Views

1. **By Phase** - Group by milestone
2. **By Priority** - Sort by priority label
3. **MVP Focus** - Filter to mvp label only

---

## Quick Start

### 1. Create Labels
```bash
gh label create packaging --color "0366d6" --description "Component packaging work"
gh label create mvp --color "d73a4a" --description "MVP-related tasks"
gh label create "priority:high" --color "e11d21" --description "High priority"
gh label create "priority:medium" --color "fbca04" --description "Medium priority"
gh label create "priority:low" --color "009800" --description "Low priority"
gh label create infrastructure --color "c5def5" --description "Infrastructure work"
gh label create observability --color "5319e7" --description "Monitoring/observability"
gh label create architecture --color "1d76db" --description "Architecture decisions"
gh label create investigation --color "fef2c0" --description "Research/analysis needed"
```

### 2. Create Issues
Copy the issue text above and create through GitHub web interface or:
```bash
gh issue create --title "..." --body "..." --label "..." --milestone <number>
```

### 3. Create Project Board
1. Go to https://github.com/theinterneti/TTA/projects
2. Click "New project"
3. Choose "Board" template
4. Name: "TTA Component Packaging"
5. Add milestones and issues
6. Organize by milestone

---

## Timeline Overview

```
Week 1 (Nov 1-8):        Phase 1 - Foundation Packages
Week 2-3 (Nov 9-22):     Phase 2 - Agent Consolidation
Week 4+ (Nov 23-Dec 13): Phase 3 - Domain Packages

Throughout: MVP development continues in parallel
```

---

## Success Metrics

### After Phase 1 (Nov 8)
- ✅ 6 total packages (2 new)
- ✅ Clear dependency graph
- ✅ All tests passing

### After Phase 2 (Nov 22)
- ✅ Agent code consolidated
- ✅ No duplicate functionality
- ✅ tta-ai-framework cleaned up

### After Phase 3 (Dec 13)
- ✅ 8-10 total packages
- ✅ Main app < 40% of codebase
- ✅ Documentation complete

---

## Links

- **Repository:** https://github.com/theinterneti/TTA
- **Milestones:** https://github.com/theinterneti/TTA/milestones
- **Issues:** https://github.com/theinterneti/TTA/issues
- **Documentation:**
  - [Agentic Primitives Implementation](AGENTIC_PRIMITIVES_IMPLEMENTATION.md)
  - [Component Packaging Strategy](COMPONENT_PACKAGING_STRATEGY.md)

---

## Notes

- **MVP Priority:** Always prioritize MVP features over packaging
- **Incremental Approach:** Package one component at a time
- **Testing:** Each package must have comprehensive tests
- **Documentation:** Keep docs updated as packages evolve
- **Communication:** Weekly updates on packaging progress
