# Language-Specific Pathway Strategy for TTA.dev

**Date**: October 29, 2025
**Purpose**: Propose architecture for language-specific agentic workflows with on-demand loading

---

## Executive Summary

**Current State**: TTA.dev already has significant **Python-specific** content embedded in "universal" context:
- Python quality standards instruction file
- Python-specific chat modes (backend-dev, langgraph-engineer)
- Python tooling references (pytest, ruff, pyright, uv)
- Python package dependencies throughout

**Proposed Solution**: Implement **Language Pathways** - modular, on-demand language ecosystems that AI agents can access when needed but don't pollute universal context.

---

## Current Language-Specific Content in TTA.dev

### ✅ Already Identified as Python-Specific

#### 1. Instruction Files (`.github/instructions/`)
- `python-quality-standards.instructions.md` (292 lines)
  - Black, ruff, pyright configuration
  - UV package manager usage
  - Python-specific best practices

#### 2. Frontend Instruction Files
- `frontend-react.instructions.md` (233 lines)
  - TypeScript/React/JSX standards
  - npm/pnpm tooling
  - Component patterns

#### 3. All Packages
- `tta-observability-integration` - Python-only (OpenTelemetry Python SDK)
- `ai-dev-toolkit` - Python-only (requires Python >=3.12)
- `tta-ai-framework` - Python-only
- `tta-narrative-engine` - Python-only
- `keploy-framework` - Python-only

#### 4. Test Battery (in TTA, not yet extracted)
- Python pytest framework
- Python-specific mutation testing
- Python coverage tools

### ⚠️ Hidden Python Dependencies

#### Chat Modes with Python Assumptions
- `backend-dev.chatmode.md` - References FastAPI, pytest, ruff, pyright, UV
- `backend-implementer.chatmode.md` - Python-focused implementation
- `langgraph-engineer.chatmode.md` - Python LangGraph SDK
- `api-gateway-engineer.chatmode.md` - Likely FastAPI-focused

#### Cross-Language Chat Modes (Safe)
- `architect.chatmode.md` - Language-agnostic design
- `devops.chatmode.md` - Infrastructure-focused
- `qa-engineer.chatmode.md` - Testing concepts (but references pytest)
- `database-admin.chatmode.md` - Database-focused

#### Universal Content (Safe)
- Component maturity concepts
- Testing philosophies (AAA, TDD)
- Security principles
- API design patterns

---

## Problem Analysis

### Context Pollution Issues

**Current Problem**: When working on a **Rust** or **Go** project:
1. Agent loads Python quality standards (ruff, black, pyright)
2. Backend chat mode references FastAPI and pytest
3. Package examples show `uv run` and Python syntax
4. Testing instructions reference pytest and coverage.py

**Result**: Wasted context tokens + potential confusion + wrong tool suggestions

### Why This Matters

**Context Window Usage**:
- Python instructions: ~500-1000 tokens
- Python chat modes: ~1000-2000 tokens
- Python package docs: ~2000-5000 tokens
- **Total waste for non-Python project**: 4,500-8,500 tokens

**AI Confusion**:
- Agent might suggest `pytest` for a Rust project (should use `cargo test`)
- Agent might reference `ruff` instead of `clippy`
- Agent might use Python patterns in JavaScript/TypeScript

---

## Proposed Solution: Language Pathways

### Architecture

```
TTA.dev/
├── packages/
│   ├── universal-agent-context/          # Language-agnostic only
│   │   ├── .github/
│   │   │   ├── instructions/
│   │   │   │   ├── api-security.instructions.md          # ✅ Universal
│   │   │   │   ├── testing-philosophy.instructions.md    # ✅ Universal
│   │   │   │   ├── component-maturity.instructions.md    # ✅ Universal
│   │   │   │   └── safety.instructions.md                # ✅ Universal
│   │   │   └── chatmodes/
│   │   │       ├── architect.chatmode.md                 # ✅ Universal
│   │   │       ├── devops.chatmode.md                    # ✅ Universal
│   │   │       └── database-admin.chatmode.md            # ✅ Universal
│   │   └── README.md
│   │
│   ├── python-pathway/                   # Python ecosystem
│   │   ├── .github/
│   │   │   ├── instructions/
│   │   │   │   ├── python-quality.instructions.md
│   │   │   │   ├── python-testing.instructions.md
│   │   │   │   └── python-async.instructions.md
│   │   │   └── chatmodes/
│   │   │       ├── python-backend-dev.chatmode.md
│   │   │       └── python-data-engineer.chatmode.md
│   │   ├── packages/
│   │   │   ├── python-test-battery/
│   │   │   ├── python-observability/
│   │   │   └── python-workflow-primitives/
│   │   └── README.md
│   │
│   ├── javascript-pathway/               # JavaScript/TypeScript ecosystem
│   │   ├── .github/
│   │   │   ├── instructions/
│   │   │   │   ├── typescript-standards.instructions.md
│   │   │   │   ├── react-patterns.instructions.md
│   │   │   │   └── node-testing.instructions.md
│   │   │   └── chatmodes/
│   │   │       ├── typescript-backend-dev.chatmode.md
│   │   │       └── react-frontend-dev.chatmode.md
│   │   ├── packages/
│   │   │   ├── typescript-test-framework/
│   │   │   ├── react-component-library/
│   │   │   └── node-observability/
│   │   └── README.md
│   │
│   ├── rust-pathway/                     # Rust ecosystem
│   │   ├── .github/
│   │   │   ├── instructions/
│   │   │   │   ├── rust-standards.instructions.md
│   │   │   │   ├── rust-testing.instructions.md
│   │   │   │   └── rust-async.instructions.md
│   │   │   └── chatmodes/
│   │   │       └── rust-backend-dev.chatmode.md
│   │   ├── packages/
│   │   │   ├── rust-test-framework/
│   │   │   └── rust-observability/
│   │   └── README.md
│   │
│   └── go-pathway/                       # Go ecosystem
│       ├── .github/
│       │   ├── instructions/
│       │   │   ├── go-standards.instructions.md
│       │   │   └── go-testing.instructions.md
│       │   └── chatmodes/
│       │       └── go-backend-dev.chatmode.md
│       ├── packages/
│       │   └── go-test-framework/
│       └── README.md
```

---

## On-Demand Loading Mechanism

### 1. Project Detection

**Automatic Language Detection**:
```yaml
# In project root: .tta/config.yml
language_pathways:
  primary: python
  secondary: [typescript]

auto_detect: true
detect_from:
  - pyproject.toml      # Python
  - package.json        # JavaScript/TypeScript
  - Cargo.toml          # Rust
  - go.mod              # Go
```

### 2. Explicit Activation

**Manual Activation in Chat**:
```
User: @python activate python pathway
Agent: ✅ Python pathway activated. Loaded:
       - Python quality standards
       - Python testing framework
       - Python backend-dev chat mode
       - Python-specific packages
```

**Deactivation**:
```
User: @python deactivate python pathway
Agent: ✅ Python pathway deactivated. Context cleared.
```

### 3. Context File Markers

**In AGENTS.md / CLAUDE.md / GEMINI.md**:
```markdown
## Active Language Pathways

Current project uses: **Python** + **TypeScript**

To load language-specific context:
- Python: See `packages/python-pathway/README.md`
- TypeScript: See `packages/javascript-pathway/README.md`

**Note**: Language pathways are loaded on-demand to preserve context budget.
```

### 4. Instruction File Metadata

**YAML Frontmatter with Load Control**:
```yaml
---
pathway: python
loadStrategy: on-demand
applyTo:
  - pattern: "**/*.py"
autoLoad:
  when:
    - projectHas: "pyproject.toml"
    - projectHas: "requirements.txt"
tags: ["python", "quality", "testing"]
---
```

---

## Migration Strategy

### Phase 1: Identify & Extract Universal Content

**Actions**:
1. Review all instruction files in `universal-agent-context`
2. Identify truly universal concepts:
   - API design principles (REST, GraphQL)
   - Security patterns (authentication, authorization)
   - Testing philosophies (AAA, TDD, BDD)
   - Component maturity (stages, quality gates)
   - Architecture patterns (SOLID, DDD, Clean Architecture)
3. Extract language-specific references
4. Create language-agnostic instruction files

**Example Transformation**:

**Before** (python-quality-standards.instructions.md):
```markdown
## Code Formatting

### Black Formatter
- Line Length: 88 characters
- Run: `uvx ruff format src/`
```

**After** (universal: code-quality.instructions.md):
```markdown
## Code Formatting

All code must be consistently formatted using the standard formatter for your language:
- Use consistent line length (typically 80-120 characters)
- Apply automatic formatting before committing
- Configure formatter in project config file
```

**Language-Specific** (python-pathway: python-quality.instructions.md):
```markdown
## Python Code Formatting

### Ruff Formatter (Python)
- Line Length: 88 characters
- Command: `uvx ruff format src/`
- Config: pyproject.toml
```

---

### Phase 2: Create Python Pathway

**Actions**:
1. Create `packages/python-pathway/` directory
2. Move Python-specific instructions
3. Move Python-specific chat modes
4. Move Python packages (observability, test-battery, etc.)
5. Create pathway README with activation instructions
6. Add auto-detection logic

**Structure**:
```
packages/python-pathway/
├── .github/
│   ├── instructions/
│   │   ├── python-quality.instructions.md       # From universal
│   │   ├── python-testing.instructions.md       # From TTA test battery
│   │   ├── python-async.instructions.md         # New
│   │   └── python-packaging.instructions.md     # UV, pip, poetry
│   └── chatmodes/
│       ├── python-backend-dev.chatmode.md       # From backend-dev
│       ├── python-data-engineer.chatmode.md     # New
│       └── python-ml-engineer.chatmode.md       # New
├── packages/
│   ├── python-test-battery/                     # From TTA
│   ├── python-observability/                    # From tta-observability
│   └── python-workflow-primitives/              # From ai-dev-toolkit
├── examples/
│   ├── fastapi-project/
│   ├── langchain-agent/
│   └── pytest-setup/
└── README.md                                     # Python pathway docs
```

---

### Phase 3: Create JavaScript/TypeScript Pathway

**Actions**:
1. Extract frontend-react.instructions.md
2. Create TypeScript quality standards
3. Create Node.js testing framework
4. Create React/Next.js patterns
5. Build JavaScript package ecosystem

**Structure**:
```
packages/javascript-pathway/
├── .github/
│   ├── instructions/
│   │   ├── typescript-quality.instructions.md
│   │   ├── react-patterns.instructions.md
│   │   ├── node-testing.instructions.md
│   │   └── npm-packaging.instructions.md
│   └── chatmodes/
│       ├── typescript-backend-dev.chatmode.md
│       ├── react-frontend-dev.chatmode.md
│       └── nodejs-fullstack-dev.chatmode.md
├── packages/
│   ├── typescript-test-framework/
│   ├── react-component-library/
│   ├── node-observability/
│   └── nextjs-patterns/
├── examples/
│   ├── nextjs-app/
│   ├── react-component-library/
│   └── jest-setup/
└── README.md
```

---

### Phase 4: Create Rust Pathway

**Why Rust?**
- High-performance backend services
- Systems programming
- WebAssembly targets
- Growing AI/ML ecosystem (Candle, Burn)

**Structure**:
```
packages/rust-pathway/
├── .github/
│   ├── instructions/
│   │   ├── rust-quality.instructions.md         # clippy, rustfmt
│   │   ├── rust-testing.instructions.md         # cargo test, proptest
│   │   ├── rust-async.instructions.md           # tokio, async-std
│   │   └── rust-packaging.instructions.md       # Cargo.toml
│   └── chatmodes/
│       ├── rust-backend-dev.chatmode.md
│       └── rust-systems-dev.chatmode.md
├── packages/
│   ├── rust-test-framework/
│   └── rust-observability/
└── README.md
```

---

### Phase 5: Create Go Pathway

**Why Go?**
- Microservices and APIs
- Cloud-native development
- Simplicity and performance
- Strong standard library

**Structure**:
```
packages/go-pathway/
├── .github/
│   ├── instructions/
│   │   ├── go-quality.instructions.md           # gofmt, golangci-lint
│   │   ├── go-testing.instructions.md           # go test, testify
│   │   └── go-packaging.instructions.md         # go.mod
│   └── chatmodes/
│       └── go-backend-dev.chatmode.md
├── packages/
│   └── go-test-framework/
└── README.md
```

---

## Implementation Details

### Auto-Detection Logic

**Algorithm**:
```python
def detect_language_pathways(project_root: Path) -> list[str]:
    """Detect which language pathways to activate based on project files."""
    pathways = []

    # Python detection
    if any([
        (project_root / "pyproject.toml").exists(),
        (project_root / "requirements.txt").exists(),
        (project_root / "setup.py").exists(),
    ]):
        pathways.append("python")

    # JavaScript/TypeScript detection
    if (project_root / "package.json").exists():
        pathways.append("javascript")

        # Check for TypeScript
        package_json = json.loads((project_root / "package.json").read_text())
        if "typescript" in package_json.get("devDependencies", {}):
            pathways.append("typescript")

    # Rust detection
    if (project_root / "Cargo.toml").exists():
        pathways.append("rust")

    # Go detection
    if (project_root / "go.mod").exists():
        pathways.append("go")

    return pathways
```

### Loading Strategy

**Lazy Loading**:
```yaml
# .tta/config.yml
pathways:
  python:
    enabled: true
    autoLoad: true
    components:
      - instructions: ["python-quality", "python-testing"]
      - chatmodes: ["python-backend-dev"]
      - packages: ["python-test-battery"]

  javascript:
    enabled: true
    autoLoad: false  # Manual activation only
    components:
      - instructions: ["typescript-quality", "react-patterns"]
      - chatmodes: ["typescript-backend-dev", "react-frontend-dev"]
```

**Context Budget Management**:
```yaml
contextBudget:
  maxTokens: 100000
  reserveForUniversal: 30000   # Universal context always loaded
  perPathway: 15000             # Max tokens per pathway
  prioritization:
    - universal                 # Always highest priority
    - primary-language          # Detected primary language
    - secondary-languages       # Additional languages if budget allows
```

---

## Benefits

### 1. Clean Context Separation
- ✅ Universal concepts remain universal
- ✅ Language-specific details stay isolated
- ✅ No cross-language pollution

### 2. Better AI Performance
- ✅ Reduced context confusion
- ✅ More relevant suggestions
- ✅ Better token utilization

### 3. Multilingual Project Support
- ✅ Python backend + TypeScript frontend
- ✅ Rust services + Go microservices
- ✅ Load only what's needed

### 4. Easier Maintenance
- ✅ Update Python pathway without affecting Rust
- ✅ Add new languages incrementally
- ✅ Clear ownership boundaries

### 5. Community Contributions
- ✅ Language experts can contribute to specific pathways
- ✅ Clear contribution guidelines per language
- ✅ Isolated testing per pathway

---

## Challenges & Solutions

### Challenge 1: Cross-Language Concepts

**Problem**: Some patterns apply to multiple languages (e.g., async/await)

**Solution**: Extract to universal with language-specific examples
```markdown
# universal: async-patterns.instructions.md
## Async/Await Pattern

Use async/await for non-blocking I/O operations.

**Python**: `async def`, `await`
**JavaScript**: `async function`, `await`
**Rust**: `async fn`, `.await`
```

### Challenge 2: Package Dependencies

**Problem**: Observability package is Python-only but conceptually universal

**Solution**: Create language-specific implementations
```
packages/
├── python-pathway/packages/python-observability/
├── javascript-pathway/packages/node-observability/
├── rust-pathway/packages/rust-observability/
└── go-pathway/packages/go-observability/
```

### Challenge 3: Activation Complexity

**Problem**: Users must manually activate pathways

**Solution**: Auto-detection with clear feedback
```markdown
# In AGENTS.md
🔍 Detected project languages: **Python**, **TypeScript**

✅ Auto-loaded pathways:
   - Python pathway (primary language)
   - JavaScript pathway (frontend detected)

📚 Available but not loaded:
   - Rust pathway (run: @activate rust)
   - Go pathway (run: @activate go)
```

### Challenge 4: Documentation Overhead

**Problem**: More pathways = more documentation to maintain

**Solution**: Shared templates and automated validation
```
templates/
├── pathway-readme-template.md
├── instruction-file-template.md
└── chatmode-template.md

scripts/
└── validate-pathway-structure.py  # Ensures consistency
```

---

## Recommendations

### Immediate Actions (Phase 1)

1. **Audit Universal Context** (1-2 days)
   - Review all instruction files
   - Identify Python-specific content
   - Extract universal concepts

2. **Create Python Pathway** (3-5 days)
   - Set up directory structure
   - Move Python-specific instructions
   - Move Python-specific chat modes
   - Document activation process

3. **Test Isolation** (1-2 days)
   - Verify no Python leakage in universal context
   - Test with non-Python project
   - Validate context budget usage

### Short-Term Goals (1-2 months)

4. **Create JavaScript/TypeScript Pathway** (1 week)
   - Extract frontend-react instructions
   - Create TypeScript standards
   - Build React/Node.js chat modes

5. **Implement Auto-Detection** (3-5 days)
   - Build detection algorithm
   - Add configuration system
   - Test with multi-language projects

6. **Documentation** (1 week)
   - Write pathway activation guides
   - Create examples for each pathway
   - Document best practices

### Long-Term Goals (3-6 months)

7. **Rust Pathway** (2-3 weeks)
   - Research Rust ecosystem tools
   - Create Rust-specific instructions
   - Build Rust chat modes
   - Rust test framework

8. **Go Pathway** (2-3 weeks)
   - Research Go ecosystem tools
   - Create Go-specific instructions
   - Build Go chat modes
   - Go test framework

9. **Community Expansion** (Ongoing)
   - Accept contributions for new pathways
   - Language experts maintain their pathways
   - Cross-pathway pattern sharing

---

## Success Metrics

### Context Efficiency
- **Baseline**: 8,500 tokens wasted on Python for Rust project
- **Target**: <500 tokens of language-specific content in cross-language contexts
- **Measurement**: Token usage analysis per project type

### AI Accuracy
- **Baseline**: Agent suggests Python tools for non-Python projects
- **Target**: 95% accuracy in language-specific tool suggestions
- **Measurement**: User feedback and suggestion analysis

### Developer Experience
- **Baseline**: Manual context management, confusion about applicable tools
- **Target**: Automatic pathway detection, clear tool boundaries
- **Measurement**: User surveys, onboarding time

### Pathway Adoption
- **Target**: 3 pathways in production (Python, JavaScript, Rust) within 6 months
- **Target**: 100+ projects using pathway system
- **Measurement**: GitHub statistics, package downloads

---

## Conclusion

**The Opportunity**: Transform TTA.dev from a Python-centric toolkit into a true **multi-language AI development platform**.

**The Strategy**: Implement **Language Pathways** - modular, on-demand language ecosystems that provide:
- ✅ Clean context separation
- ✅ Better AI performance
- ✅ Multi-language project support
- ✅ Community scalability

**Next Steps**:
1. Review and approve this strategy
2. Begin Phase 1: Audit and extract universal content
3. Create Python pathway as proof-of-concept
4. Validate with multi-language projects
5. Expand to JavaScript, Rust, Go

**Expected Impact**:
- 4,500-8,500 tokens saved per cross-language project
- Better AI suggestions (95% accuracy target)
- Support for Python + TypeScript + Rust + Go projects
- Clear contribution model for language communities

---

**Status**: Proposal - Awaiting Review
**Next Review**: After Phase 1 completion
**Owner**: TTA Development Team


---
**Logseq:** [[TTA.dev/.archive/Status-reports/2025-10/Language_pathway_strategy]]
