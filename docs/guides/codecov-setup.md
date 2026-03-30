# Codecov Quick Start

## ⚡ TL;DR

We're now tracking code coverage with Codecov! Coverage reports are automatically generated on every push and PR.

## 🎯 What You Need to Know

### Coverage Targets

| Stage | Required Coverage |
|-------|------------------|
| Development | 70% |
| Staging | 80% |
| Production | 85% |

### Current Status (Baseline: 2025-10-29)

- **Overall**: 28.33% → Target: 70%
- **observability_integration**: 75.93% ✅ (Staging ready!)
- **orchestration**: 68.07% (2% away from target)
- **agent_orchestration**: 17.88% (Needs major work)

## 🚀 Setup (One-Time, Already Done!)

The repo is configured. You just need the GitHub secret:

1. Get token from <https://app.codecov.io/gh/theinterneti/TTA/settings>
2. Add as `CODECOV_TOKEN` in GitHub Secrets
3. That's it! 🎉

## 📊 Viewing Coverage

### On Pull Requests

Every PR automatically gets:
- ✅ Coverage comment with summary
- ✅ GitHub status check
- ✅ Codecov report link

### Web Dashboard

Visit: <https://app.codecov.io/gh/theinterneti/TTA>

View:
- Overall project coverage
- Per-component coverage
- Line-by-line file coverage
- Coverage trends over time

### Locally

```bash
# Generate coverage report
uv run pytest tests/ --cov=src --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## ✍️ Writing Tests for Coverage

### Focus Areas (Priority Order)

1. **Quick Wins**: `orchestration` (68% → 70%, ~13 lines)
2. **High Value**: `player_experience` (56% → 70%, ~1,600 lines)
3. **Core Infrastructure**: `agent_orchestration` (18% → 70%, ~4,500 lines)

### Coverage Best Practices

```python
# ✅ GOOD: Test happy path AND edge cases
def test_process_input_valid():
    result = process_input("valid input")
    assert result.success is True

def test_process_input_empty():
    result = process_input("")
    assert result.error == "Input required"

def test_process_input_special_chars():
    result = process_input("!@#$%")
    assert result.sanitized is True

# ❌ BAD: Only testing happy path
def test_process_input():
    result = process_input("valid input")
    assert result.success is True
```

### What Gets Measured

- ✅ Line coverage: Which lines executed
- ✅ Branch coverage: Which if/else paths taken
- ✅ Function coverage: Which functions called
- ❌ NOT mutation testing (use `mutmut` for that)

## 🎓 Understanding Coverage Reports

### Green Lines = Good

```python
def add(a, b):          # ✅ Covered
    return a + b        # ✅ Covered
```

### Red Lines = Need Tests

```python
def divide(a, b):       # ✅ Covered
    if b == 0:          # ⚠️ Branch partially covered
        return None     # ❌ Never executed!
    return a / b        # ✅ Covered
```

Need to add test for `b == 0` case!

### Coverage ≠ Quality

- **70% coverage** with thoughtful tests > **100% coverage** with shallow tests
- Focus on critical paths, edge cases, error handling
- Use mutation testing to validate test quality

## 🔧 Troubleshooting

### "Coverage decreased" on PR

**Fix**: Add tests for your new code
```bash
# Check what needs coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Look for lines marked with "Missing"
```

### Coverage report not generating

**Fix**: Ensure pytest-cov is installed
```bash
uv sync --all-extras
```

### Codecov upload failing

**Fix**: Check `CODECOV_TOKEN` secret is set in GitHub

## 📚 Resources

- **Full Setup Guide**: `docs/CODECOV_SETUP.md`
- **Coverage Baseline**: `COVERAGE_BASELINE_REPORT.md`
- **Current Status**: `CURRENT_STATUS.md`
- **Codecov Dashboard**: <https://app.codecov.io/gh/theinterneti/TTA>

## 💡 Pro Tips

1. **Check coverage before pushing**:
   ```bash
   uv run pytest --cov=src --cov-report=term-missing
   ```

2. **Focus on changed files**: Don't worry about unrelated files

3. **Use parametrize for multiple cases**:
   ```python
   @pytest.mark.parametrize("input,expected", [
       ("", "empty"),
       ("hello", "valid"),
       ("!@#", "invalid"),
   ])
   def test_validate(input, expected):
       assert validate(input) == expected
   ```

4. **Mock external dependencies**: Don't test APIs, databases in unit tests

---

**Questions?** Check `docs/CODECOV_SETUP.md` or ask the team!


---