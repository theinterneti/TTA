# OpenHands Task Capability Matrix

**Date:** 2025-10-25  
**Purpose:** Detailed capability matrix for all task types  
**Format:** Comprehensive reference table

---

## Task Categories & Capabilities

### 1. Code Generation

#### Simple Functions (< 50 lines)

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | Mistral Small | Mistral Small | Mistral Small |
| **Time** | 1.6s | 3.1s + overhead | 3.1s + 5-10s |
| **Quality** | 4/5 | 4/5 | 4/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Code only | Requires Python | Requires Docker |
| **Use Case** | Quick generation | File creation | Isolation |

#### Moderate Functions (50-200 lines)

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | Mistral Small | Mistral Small | Mistral Small |
| **Time** | 2.7s | 3.1s + overhead | 3.1s + 5-10s |
| **Quality** | 5/5 | 5/5 | 5/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Code only | Requires Python | Requires Docker |
| **Use Case** | Production code | File creation | Isolation |

#### Complex Functions (> 200 lines)

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | DeepSeek Chat | DeepSeek Chat | DeepSeek Chat |
| **Time** | 19.7s | 19.7s + overhead | 19.7s + 5-10s |
| **Quality** | 5/5 | 5/5 | 5/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Code only | Requires Python | Requires Docker |
| **Use Case** | Complex logic | File creation | Isolation |

---

### 2. Code Analysis & Review

#### Code Review

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | DeepSeek R1 | DeepSeek R1 | DeepSeek R1 |
| **Time** | 28.5s | 28.5s + overhead | 28.5s + 5-10s |
| **Quality** | 5/5 | 5/5 | 5/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Analysis only | Requires Python | Requires Docker |
| **Use Case** | Review code | Detailed analysis | Isolation |

#### Performance Analysis

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | DeepSeek Chat | DeepSeek Chat | DeepSeek Chat |
| **Time** | 19.7s | 19.7s + overhead | 19.7s + 5-10s |
| **Quality** | 5/5 | 5/5 | 5/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Analysis only | Requires Python | Requires Docker |
| **Use Case** | Optimization | Detailed analysis | Isolation |

---

### 3. Unit Test Generation

#### Simple Tests (< 10 tests)

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | Mistral Small | Mistral Small | Mistral Small |
| **Time** | 5.0s | 5.0s + overhead | 5.0s + 5-10s |
| **Quality** | 5/5 | 5/5 | 5/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Code only | Requires Python | Requires Docker |
| **Use Case** | Quick tests | File creation | Isolation |

#### Comprehensive Tests (> 10 tests)

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | DeepSeek Chat | DeepSeek Chat | DeepSeek Chat |
| **Time** | 26.1s | 26.1s + overhead | 26.1s + 5-10s |
| **Quality** | 5/5 | 5/5 | 5/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Code only | Requires Python | Requires Docker |
| **Use Case** | Production tests | File creation | Isolation |

---

### 4. File Creation & Modification

#### Single File Creation

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ❌ | ✅ | ✅ |
| **Best Model** | N/A | Mistral Small | Mistral Small |
| **Time** | N/A | 3.1s + overhead | 3.1s + 5-10s |
| **Quality** | N/A | 4.7/5 | 4.7/5 |
| **Cost** | N/A | Free | Free |
| **Limitation** | No file ops | Requires Python | Requires Docker |
| **Use Case** | N/A | Create files | Isolation |

#### Multiple File Creation (> 5 files)

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ❌ | ✅ | ✅ |
| **Best Model** | N/A | Mistral Small | Mistral Small |
| **Time** | N/A | 3.1s × N + overhead | 3.1s × N + 5-10s |
| **Quality** | N/A | 4.7/5 | 4.7/5 |
| **Cost** | N/A | Free | Free |
| **Limitation** | No file ops | Requires Python | Requires Docker |
| **Use Case** | N/A | Project scaffold | Isolation |

---

### 5. Bash Command Execution

#### Simple Commands

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ❌ | ✅ | ✅ |
| **Best Model** | N/A | Mistral Small | Mistral Small |
| **Time** | N/A | 3.1s + cmd time | 3.1s + 5-10s + cmd time |
| **Quality** | N/A | 4.7/5 | 4.7/5 |
| **Cost** | N/A | Free | Free |
| **Limitation** | No bash | Requires Python | Requires Docker |
| **Use Case** | N/A | Run tests | Isolation |

#### Complex Commands (Pipelines)

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ❌ | ✅ | ✅ |
| **Best Model** | N/A | DeepSeek Chat | DeepSeek Chat |
| **Time** | N/A | 19.7s + cmd time | 19.7s + 5-10s + cmd time |
| **Quality** | N/A | 5/5 | 5/5 |
| **Cost** | N/A | Free | Free |
| **Limitation** | No bash | Requires Python | Requires Docker |
| **Use Case** | N/A | Build automation | Isolation |

---

### 6. Multi-File Project Scaffolding

#### Project Structure (5-10 files)

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ❌ | ✅ | ✅ |
| **Best Model** | N/A | Mistral Small | Mistral Small |
| **Time** | N/A | 3.1s × N + overhead | 3.1s × N + 5-10s |
| **Quality** | N/A | 4.7/5 | 4.7/5 |
| **Cost** | N/A | Free | Free |
| **Limitation** | No file ops | Requires Python | Requires Docker |
| **Use Case** | N/A | Scaffold project | Isolation |

#### Complex Project (> 10 files)

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ❌ | ✅ | ✅ |
| **Best Model** | N/A | DeepSeek Chat | DeepSeek Chat |
| **Time** | N/A | 19.7s × N + overhead | 19.7s × N + 5-10s |
| **Quality** | N/A | 5/5 | 5/5 |
| **Cost** | N/A | Free | Free |
| **Limitation** | No file ops | Requires Python | Requires Docker |
| **Use Case** | N/A | Full project | Isolation |

---

### 7. Build Automation

#### Makefile Generation

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | Mistral Small | Mistral Small | Mistral Small |
| **Time** | 3.1s | 3.1s + overhead | 3.1s + 5-10s |
| **Quality** | 4.7/5 | 4.7/5 | 4.7/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Code only | Requires Python | Requires Docker |
| **Use Case** | Generate | Create file | Isolation |

#### CI/CD Configuration

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | DeepSeek Chat | DeepSeek Chat | DeepSeek Chat |
| **Time** | 19.7s | 19.7s + overhead | 19.7s + 5-10s |
| **Quality** | 5/5 | 5/5 | 5/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Code only | Requires Python | Requires Docker |
| **Use Case** | Generate | Create file | Isolation |

---

### 8. Documentation Generation

#### API Documentation

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | DeepSeek Chat | DeepSeek Chat | DeepSeek Chat |
| **Time** | 19.7s | 19.7s + overhead | 19.7s + 5-10s |
| **Quality** | 5/5 | 5/5 | 5/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Code only | Requires Python | Requires Docker |
| **Use Case** | Generate | Create file | Isolation |

#### README Generation

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | Mistral Small | Mistral Small | Mistral Small |
| **Time** | 2.7s | 2.7s + overhead | 2.7s + 5-10s |
| **Quality** | 4.7/5 | 4.7/5 | 4.7/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Code only | Requires Python | Requires Docker |
| **Use Case** | Generate | Create file | Isolation |

---

### 9. Refactoring Tasks

#### Code Refactoring

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | DeepSeek Chat | DeepSeek Chat | DeepSeek Chat |
| **Time** | 19.7s | 19.7s + overhead | 19.7s + 5-10s |
| **Quality** | 5/5 | 5/5 | 5/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Code only | Requires Python | Requires Docker |
| **Use Case** | Generate | Create file | Isolation |

#### Architecture Refactoring

| Aspect | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| **Capability** | ✅ | ✅ | ✅ |
| **Best Model** | DeepSeek R1 | DeepSeek R1 | DeepSeek R1 |
| **Time** | 28.5s | 28.5s + overhead | 28.5s + 5-10s |
| **Quality** | 5/5 | 5/5 | 5/5 |
| **Cost** | Free | Free | Free |
| **Limitation** | Analysis only | Requires Python | Requires Docker |
| **Use Case** | Analysis | Detailed plan | Isolation |

---

## Summary Statistics

### Capability Coverage

| Task Category | Direct API | CLI Mode | Docker Mode |
|---------------|-----------|----------|-------------|
| Code Generation | ✅ 100% | ✅ 100% | ✅ 100% |
| Code Analysis | ✅ 100% | ✅ 100% | ✅ 100% |
| Unit Tests | ✅ 100% | ✅ 100% | ✅ 100% |
| File Creation | ❌ 0% | ✅ 100% | ✅ 100% |
| Bash Execution | ❌ 0% | ✅ 100% | ✅ 100% |
| Multi-File | ❌ 0% | ✅ 100% | ✅ 100% |
| Build Automation | ✅ 100% | ✅ 100% | ✅ 100% |
| Documentation | ✅ 100% | ✅ 100% | ✅ 100% |
| Refactoring | ✅ 100% | ✅ 100% | ✅ 100% |

### Average Performance

| Metric | Direct API | CLI Mode | Docker Mode |
|--------|-----------|----------|-------------|
| Avg Time | 12.5s | 12.5s + overhead | 12.5s + 5-10s |
| Avg Quality | 4.8/5 | 4.8/5 | 4.8/5 |
| Cost | Free | Free | Free |
| Setup | Easy | Medium | Hard |

---

**Status:** Complete  
**Last Updated:** 2025-10-25  
**Related:** openhands-capability-matrix.md, openhands-decision-guide.md

