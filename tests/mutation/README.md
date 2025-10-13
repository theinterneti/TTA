# Mutation Testing for TTA Model Management

This directory contains configuration and results for mutation testing of the Model Management component.

## What is Mutation Testing?

Mutation testing validates the effectiveness of your test suite by introducing small changes (mutations) to your code and checking if your tests catch these changes.

**Workflow:**
1. Mutmut mutates code (e.g., changes `>` to `>=`)
2. Test suite runs against mutated code
3. If tests FAIL → Mutation killed ✅ (good test)
4. If tests PASS → Mutation survived ❌ (weak test)
5. Mutation score = killed / total mutations

## Quick Start

```bash
# Run mutation tests on model management
uvx mutmut run --paths-to-mutate=src/components/model_management

# Show results
uvx mutmut results

# Show surviving mutations
uvx mutmut show

# Generate HTML report
uvx mutmut html
```

## Configuration

Mutation testing is configured in `mutation_config.toml`. Key settings:

- **paths_to_mutate**: Code to mutate (`src/components/model_management`)
- **runner**: Test command (`pytest -x --tb=short`)
- **tests_dir**: Test directory (`tests/unit/model_management`)

## Interpreting Results

### Mutation Score

**Mutation Score = (Killed Mutations / Total Mutations) × 100**

| Score | Quality |
|-------|---------|
| 90-100% | Excellent |
| 80-90% | Good |
| 70-80% | Adequate |
| < 70% | Weak |

### Surviving Mutations

When a mutation survives (tests don't catch it):

1. **Review the mutation** - What changed?
2. **Assess impact** - Is this a real bug?
3. **Add test** - Write test to kill the mutation
4. **Or document** - Explain why it's acceptable (e.g., logging)

## Best Practices

1. **Run weekly** - Too slow for PR checks (30-60 minutes)
2. **Focus on critical code** - Model selection, fallback, security
3. **Investigate all survivors** - Don't ignore them
4. **Document acceptable survivors** - Explain why they're OK
5. **Track score over time** - Monitor test suite quality

## Directory Structure

```
tests/mutation/
├── mutation_config.toml    # Mutation testing configuration
├── mutation_results/        # Generated mutation results
│   ├── latest.json         # Latest mutation test results
│   └── history/            # Historical results
├── html/                    # Generated HTML reports
└── README.md               # This file
```

## Common Commands

### Run Mutation Tests

```bash
# Full mutation test run
uvx mutmut run --paths-to-mutate=src/components/model_management

# Run on specific file
uvx mutmut run --paths-to-mutate=src/components/model_management/services/model_selector.py

# Use faster test runner
uvx mutmut run --runner="pytest -x --tb=line"
```

### View Results

```bash
# Show summary
uvx mutmut results

# Show surviving mutations
uvx mutmut show

# Show specific mutation
uvx mutmut show 42

# Generate HTML report
uvx mutmut html
```

### Debug Mutations

```bash
# Apply a specific mutation to see what changed
uvx mutmut apply 42

# Run tests manually to debug
uvx pytest tests/unit/model_management/ -v

# Revert mutation
git checkout src/components/model_management/
```

## CI/CD Integration

Mutation tests run weekly in GitHub Actions:

```yaml
mutation-tests:
  runs-on: ubuntu-latest
  if: github.event_name == 'schedule'  # Weekly only
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
    - name: Run mutation tests
      run: uvx mutmut run --paths-to-mutate=src/components/model_management
    - name: Generate report
      run: uvx mutmut html
    - name: Upload report
      uses: actions/upload-artifact@v4
      with:
        name: mutation-report
        path: html/
```

## Troubleshooting

### Mutation Tests Taking Too Long

**Problem:** Tests run for hours

**Solutions:**
- Run on specific files only
- Use faster test runner: `--runner="pytest -x --tb=line"`
- Reduce test scope temporarily
- Use parallel workers (if available)

### Tests Timing Out

**Problem:** Individual tests timeout

**Solutions:**
- Increase timeout in config
- Optimize slow tests
- Skip slow tests during mutation testing

### High Number of Survivors

**Problem:** Many mutations survive

**Solutions:**
- Review test coverage
- Add missing test cases
- Focus on critical paths first
- Document acceptable survivors

## Resources

- [Mutmut Documentation](https://mutmut.readthedocs.io/)
- [Advanced Testing Methodology](../../docs/testing/ADVANCED_TESTING_METHODOLOGY.md)
- [Testing Strategy Summary](../../docs/testing/TESTING_STRATEGY_SUMMARY.md)

---

**Last Updated:** 2025-10-10
**Maintained by:** The Augster (AI Development Assistant)
