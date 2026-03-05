# Observability Package Export - Quick Start Guide

**Package:** `tta-observability-integration` v0.1.0
**Target:** https://github.com/theinterneti/TTA.dev

---

## 🚀 Quick Export (3 Steps)

### Step 1: Run Export Script
```bash
./scripts/export-observability-package.sh
```

This creates `export/tta-observability-integration/` with all files ready.

### Step 2: Copy to TTA.dev
```bash
# Option A: Let the script copy for you (interactive)
# The script will ask if you want to copy to TTA.dev

# Option B: Manual copy
cp -r export/tta-observability-integration/* \
      /path/to/TTA.dev/packages/tta-observability-integration/
```

### Step 3: Test in TTA.dev
```bash
cd /path/to/TTA.dev/packages/tta-observability-integration
uv run pytest tests/ --cov=src
```

---

## 📦 What Gets Exported

### Source Code (6 files)
- `src/observability_integration/__init__.py` - Public API
- `src/observability_integration/apm_setup.py` - OpenTelemetry setup
- `src/observability_integration/primitives/__init__.py` - Primitives API
- `src/observability_integration/primitives/router.py` - RouterPrimitive
- `src/observability_integration/primitives/cache.py` - CachePrimitive
- `src/observability_integration/primitives/timeout.py` - TimeoutPrimitive

### Tests (4 files)
- `tests/unit/observability_integration/test_apm_setup.py`
- `tests/unit/observability_integration/test_router_primitive.py`
- `tests/unit/observability_integration/test_cache_primitive.py`
- `tests/unit/observability_integration/test_timeout_primitive.py`

### Documentation (3 files)
- `specs/observability-integration.md` - Complete specification
- `docs/OBSERVABILITY_INTEGRATION_PROGRESS.md` - Progress tracking
- `docs/OBSERVABILITY_PACKAGE_EXPORT_PLAN.md` - Export plan

### Configuration (4 files)
- `pyproject.toml` - Package configuration
- `README.md` - Package overview
- `CHANGELOG.md` - Version history
- `MANIFEST.txt` - File listing

**Total:** 17 files

---

## 🔑 Key Features

### OpenTelemetry APM
```python
from observability_integration import initialize_observability

initialize_observability(
    service_name="tta",
    enable_prometheus=True,
    prometheus_port=9464
)
```

### RouterPrimitive (30% cost savings)
```python
from observability_integration.primitives import RouterPrimitive

router = RouterPrimitive(
    routes={"fast": llama, "premium": gpt4},
    router_fn=lambda data, ctx: "premium" if complex(data) else "fast"
)
```

### CachePrimitive (40% cost savings)
```python
from observability_integration.primitives import CachePrimitive

cache = CachePrimitive(
    primitive=gpt4,
    cache_key_fn=lambda data, ctx: data["prompt"][:50],
    ttl_seconds=3600
)
```

### TimeoutPrimitive
```python
from observability_integration.primitives import TimeoutPrimitive

timeout = TimeoutPrimitive(
    primitive=slow_op,
    timeout_seconds=30
)
```

---

## 📋 Checklist

### Before Export
- [x] All source files identified
- [x] All tests passing
- [x] Documentation complete
- [x] Export script created

### During Export
- [ ] Run `./scripts/export-observability-package.sh`
- [ ] Review files in `export/tta-observability-integration/`
- [ ] Verify all 17 files present

### After Export
- [ ] Copy to TTA.dev repository
- [ ] Run tests in TTA.dev
- [ ] Create PR in TTA.dev
- [ ] Update TTA to use package

---

## 🔗 Documentation

- **Export Plan:** `OBSERVABILITY_PACKAGE_EXPORT_PLAN.md`
- **Summary:** `OBSERVABILITY_PACKAGE_SUMMARY.md`
- **This Guide:** `OBSERVABILITY_EXPORT_QUICK_START.md`
- **Export Script:** `scripts/export-observability-package.sh`

---

## 💡 Tips

1. **Review before export:** Check `OBSERVABILITY_PACKAGE_EXPORT_PLAN.md`
2. **Test locally first:** Run tests before copying to TTA.dev
3. **Use the script:** Automated export is safer than manual
4. **Verify imports:** Ensure `tta-dev-primitives` is available in TTA.dev

---

## 🆘 Troubleshooting

### Script fails to find TTA.dev
```bash
# Set the path explicitly
TTA_DEV_REPO=/path/to/TTA.dev ./scripts/export-observability-package.sh
```

### Tests fail in TTA.dev
```bash
# Ensure tta-dev-primitives is installed
cd /path/to/TTA.dev
uv sync --all-extras
```

### Import errors
```bash
# Verify package structure
ls -la packages/tta-observability-integration/src/
```

---

**Ready to export?** Run: `./scripts/export-observability-package.sh`


---
**Logseq:** [[TTA.dev/.archive/Observability/2025-10/Observability_export_quick_start]]
