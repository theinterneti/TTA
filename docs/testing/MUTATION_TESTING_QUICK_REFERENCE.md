# Mutation Testing Quick Reference

**Quick commands and tips for TTA mutation testing**

---

## 🚀 Quick Commands

### Run All Services
```bash
./scripts/run-mutation-tests.sh
```

### Run Single Service
```bash
./scripts/run-mutation-tests.sh model-selector
./scripts/run-mutation-tests.sh fallback-handler
./scripts/run-mutation-tests.sh performance-monitor
```

### Custom Threshold
```bash
./scripts/run-mutation-tests.sh -t 90 --all
```

### Manual Workflow Trigger
1. Go to **Actions** → **Mutation Testing**
2. Click **Run workflow**
3. Select service (or `all`)
4. Click **Run workflow**

---

## 📊 Current Scores

| Service | Score | Mutations | Tests |
|---------|-------|-----------|-------|
| ModelSelector | **100%** 🏆 | 534/534 | 18 |
| FallbackHandler | **100%** 🏆 | 352/352 | 16 |
| PerformanceMonitor | **100%** 🏆 | 519/519 | 27 |
| **TOTAL** | **100%** 🎉 | **1,405/1,405** | **61** |

---

## 🔍 Interpreting Results

### Mutation Score Ranges
- **100%** 🏆 - Perfect (all mutations killed)
- **95-99%** ✅ - Excellent
- **85-94%** ⚠️ - Good (room for improvement)
- **<85%** ❌ - Insufficient (CI fails)

### Report Files
- **Text Report:** `{service}-report.txt` - Summary statistics
- **HTML Report:** `{service}-report.html` - Detailed visualization
- **Session DB:** `session-{service}.sqlite` - Raw mutation data

---

## 🛠️ Common Tasks

### Add Tests for Surviving Mutants

1. **Download HTML report** from CI artifacts
2. **Find surviving mutants** in report
3. **Add concrete value test:**
   ```python
   def test_specific_calculation():
       # Hardcoded expected value
       result = calculate_something([1, 2, 3])
       assert result == 6  # NOT sum([1, 2, 3])
   ```
4. **Re-run locally** to verify
5. **Commit and push**

### Update After Code Changes

```bash
# 1. Update tests
# 2. Run mutation testing
./scripts/run-mutation-tests.sh {service}

# 3. Check score
# 4. Add tests if needed
# 5. Commit when score ≥95%
```

### View CI Results

1. Go to **Actions** → **Mutation Testing**
2. Click latest workflow run
3. Scroll to **Artifacts**
4. Download `mutation-report-{service}`
5. Open HTML file in browser

---

## 📝 Best Practices

### ✅ DO
- Use hardcoded expected values
- Test edge cases explicitly
- Use approximate comparisons for floats
- Cover all code paths
- Run locally before pushing

### ❌ DON'T
- Recalculate expected values in tests
- Skip edge case testing
- Use exact equality for floats
- Assume property tests are enough
- Push without local verification

---

## 🐛 Troubleshooting

### Tests Pass but Mutation Score Low
→ Add concrete value tests with hardcoded expectations

### Workflow Times Out
→ Check for hanging tests, increase timeout if needed

### Score Extraction Fails
→ Check text report manually, update grep pattern

### Dependencies Not Installing
→ Clear cache, update `uv.lock`, verify `pyproject.toml`

---

## 📚 Documentation

- **[CI/CD Guide](./MUTATION_TESTING_CICD_GUIDE.md)** - Complete CI/CD documentation
- **[Mutation Testing Guide](./MUTATION_TESTING_GUIDE.md)** - Comprehensive guide
- **[Implementation Plan](./NEXT_STEPS_IMPLEMENTATION_PLAN.md)** - Project plan and results

---

## 🔗 Links

- **Workflow:** [`.github/workflows/mutation-testing.yml`](../../.github/workflows/mutation-testing.yml)
- **Script:** [`scripts/run-mutation-tests.sh`](../../scripts/run-mutation-tests.sh)
- **GitHub Actions:** [View Runs](https://github.com/theinterneti/TTA/actions/workflows/mutation-testing.yml)

---

**Last Updated:** 2025-10-11
**Maintained By:** TTA Development Team
