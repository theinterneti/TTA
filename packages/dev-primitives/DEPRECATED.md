# ⚠️ DEPRECATED

This package has been deprecated in favor of `tta-dev-primitives` from the TTA.dev repository.

## Migration

**Old (deprecated):**
```python
from dev_primitives.recovery import CircuitBreaker, ErrorCategory
```

**New (recommended):**
```python
from tta_dev_primitives.recovery import CircuitBreaker, ErrorCategory
```

## Why?

The `dev-primitives` package has been consolidated into `tta-dev-primitives` in the TTA.dev repository with:
- ✅ Better naming clarity (development tools, not game components)
- ✅ Professional packaging and versioning
- ✅ Comprehensive testing (35 tests, 100% passing)
- ✅ All features consolidated in one place
- ✅ Circuit breaker integration with error classification
- ✅ Maintained separately from TTA game code

## Timeline

- **Current**: This package still works but is no longer maintained
- **Next**: Code will be migrated to use `tta-dev-primitives`
- **Future**: This directory will be removed

## Links

- **New Package**: https://github.com/theinterneti/TTA.dev/tree/main/packages/tta-dev-primitives
- **Migration PR**: https://github.com/theinterneti/TTA/pull/101

---

*Last Updated: October 28, 2025*
