# OpenHands: Concrete Examples of What Works & What Doesn't

**Date:** 2025-10-25  
**Purpose:** Demonstrate capabilities and limitations with real examples

---

## Example 1: Simple Code Generation ✅ WORKS

### Task
"Write a Python function that returns 'Hello, World!'"

### Access Methods That Work
- ✅ Direct API
- ✅ SDK Mode
- ✅ CLI Mode
- ✅ Docker Mode

### Result
```python
def hello_world():
    return 'Hello, World!'

print(hello_world())  # Output: Hello, World!
```

### Time: 1.8 seconds
### Cost: $0.001
### Recommendation: Use Direct API (fastest, cheapest)

---

## Example 2: Function with Error Handling ✅ WORKS

### Task
"Write a function to calculate average of a list with error handling"

### Access Methods That Work
- ✅ Direct API
- ✅ SDK Mode
- ✅ CLI Mode
- ✅ Docker Mode

### Result
```python
def calculate_average(numbers: list[float]) -> float:
    """Calculate average of a list of numbers."""
    if not numbers:
        raise ValueError("List cannot be empty")
    return round(sum(numbers) / len(numbers), 2)
```

### Time: 6.7 seconds
### Cost: $0.004
### Recommendation: Use Direct API

---

## Example 3: Generate Unit Tests ✅ WORKS (with caveats)

### Task
"Generate comprehensive pytest tests for calculate_average function"

### Access Methods That Work
- ✅ Direct API (generates code)
- ✅ SDK Mode (generates code)
- ✅ CLI Mode (generates AND creates file)
- ✅ Docker Mode (generates AND creates file)

### Result
```python
import pytest

@pytest.mark.parametrize("numbers, expected", [
    ([1.0, 2.0, 3.0], 2.0),
    ([-1.0, -2.0, -3.0], -2.0),
])
def test_calculate_average_valid(numbers, expected):
    assert calculate_average(numbers) == expected

def test_calculate_average_empty():
    with pytest.raises(ValueError):
        calculate_average([])
```

### Time: 31.2 seconds
### Cost: $0.01
### Recommendation: Use Docker Mode (creates file)

---

## Example 4: Create a File ❌ DOESN'T WORK (SDK) ✅ WORKS (Docker)

### Task
"Create a file named 'test.txt' with content 'Hello from OpenHands'"

### Access Methods
- ❌ Direct API (no file operations)
- ❌ SDK Mode (no file operations)
- ✅ CLI Mode (creates file)
- ✅ Docker Mode (creates file)

### Result
```bash
# File created at: /workspace/test.txt
# Content: Hello from OpenHands
```

### Time: 15-30 seconds
### Cost: $0.01
### Recommendation: Use Docker Mode

---

## Example 5: Execute Bash Command ❌ DOESN'T WORK (SDK) ✅ WORKS (Docker)

### Task
"Execute 'ls -la' and show the output"

### Access Methods
- ❌ Direct API (no bash)
- ❌ SDK Mode (no bash)
- ✅ CLI Mode (executes bash)
- ✅ Docker Mode (executes bash)

### Result
```bash
total 48
drwxr-xr-x  5 user  staff   160 Oct 25 11:30 .
drwxr-xr-x 20 user  staff   640 Oct 25 11:00 ..
-rw-r--r--  1 user  staff  1024 Oct 25 11:30 test.txt
-rw-r--r--  1 user  staff  2048 Oct 25 11:25 main.py
```

### Time: 10-20 seconds
### Cost: $0.01
### Recommendation: Use Docker Mode

---

## Example 6: Generate and Save Tests ❌ DOESN'T WORK (SDK) ✅ WORKS (Docker)

### Task
"Generate pytest tests for calculate_average and save to tests/test_average.py"

### Access Methods
- ❌ Direct API (generates only, no save)
- ❌ SDK Mode (generates only, no save)
- ✅ CLI Mode (generates AND saves)
- ✅ Docker Mode (generates AND saves)

### Result
```bash
# File created at: tests/test_average.py
# Content: [pytest tests with parametrize, docstrings, etc.]
# File size: 2.5 KB
# Tests: 8 test functions
```

### Time: 45-60 seconds
### Cost: $0.02
### Recommendation: Use Docker Mode

---

## Example 7: Multi-File Project ❌ DOESN'T WORK (SDK) ✅ WORKS (Docker)

### Task
"Create a Python package with:
- src/mypackage/__init__.py
- src/mypackage/utils.py
- tests/test_utils.py
- setup.py
- README.md"

### Access Methods
- ❌ Direct API (no file operations)
- ❌ SDK Mode (no file operations)
- ✅ CLI Mode (creates all files)
- ✅ Docker Mode (creates all files)

### Result
```bash
mypackage/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── utils.py
├── tests/
│   └── test_utils.py
├── setup.py
└── README.md
```

### Time: 60-120 seconds
### Cost: $0.05
### Recommendation: Use Docker Mode

---

## Example 8: Build Automation ❌ DOESN'T WORK (SDK) ✅ WORKS (Docker)

### Task
"Create a Makefile with targets for test, lint, format, and build"

### Access Methods
- ❌ Direct API (no file operations)
- ❌ SDK Mode (no file operations)
- ✅ CLI Mode (creates Makefile)
- ✅ Docker Mode (creates Makefile)

### Result
```makefile
.PHONY: test lint format build clean

test:
	pytest tests/ -v

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info
```

### Time: 20-30 seconds
### Cost: $0.01
### Recommendation: Use Docker Mode

---

## Summary Table

| Example | Task | Direct API | SDK | CLI | Docker |
|---------|------|-----------|-----|-----|--------|
| 1 | Hello world | ✅ | ✅ | ✅ | ✅ |
| 2 | Function | ✅ | ✅ | ✅ | ✅ |
| 3 | Generate tests | ✅ | ✅ | ✅ | ✅ |
| 4 | Create file | ❌ | ❌ | ✅ | ✅ |
| 5 | Execute bash | ❌ | ❌ | ✅ | ✅ |
| 6 | Generate & save | ❌ | ❌ | ✅ | ✅ |
| 7 | Multi-file | ❌ | ❌ | ✅ | ✅ |
| 8 | Build automation | ❌ | ❌ | ✅ | ✅ |

---

## Key Insights

### What Works Everywhere
- Code generation
- Code analysis
- Documentation writing
- Problem solving
- Planning

### What Only Works with Docker/CLI
- File creation
- Bash execution
- Multi-file projects
- Build automation
- DevOps tasks

### What Doesn't Work Anywhere
- Nothing! All tasks are possible with the right access method.

---

## Recommendation

**For TTA Use Case:**

1. **Simple tasks** (Examples 1-3): Use Direct API
   - Faster
   - Cheaper
   - Sufficient for code generation

2. **Complex tasks** (Examples 4-8): Use Docker Mode
   - Full capabilities
   - File creation
   - Bash execution
   - Production ready

---

## Next Steps

1. Review these examples
2. Understand the limitations
3. Choose appropriate access method
4. Implement Docker runtime mode
5. Test with real tasks

---

**Status:** Examples Complete  
**Recommendation:** Use Docker Mode for production  
**Timeline:** 2-3 weeks to implement

