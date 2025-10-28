# ⚠️ DEPRECATED

This package has been deprecated in favor of `tta-dev-primitives` from the TTA.dev repository.

## Migration

**Old (deprecated):**

```python
from tta_workflow_primitives.core import SequentialPrimitive
from tta_workflow_primitives.recovery import RetryPrimitive
```

**New (recommended):**

```python
from tta_dev_primitives.core import SequentialPrimitive
from tta_dev_primitives.recovery import RetryPrimitive
```

## Why?

The `tta-workflow-primitives` package has been renamed to `tta-dev-primitives` and moved to the TTA.dev repository with:

- ✅ Better naming clarity (development tools, not game components)
- ✅ Professional packaging and versioning
- ✅ Comprehensive testing (35 tests, 100% passing)
- ✅ Circuit breaker consolidation from dev-primitives
- ✅ Maintained separately from TTA game code

## Timeline

- **Current**: This package still works but is no longer maintained
- **Next**: Code will be migrated to use `tta-dev-primitives`
- **Future**: This directory will be removed

## Links

- [New Package](https://github.com/theinterneti/TTA.dev/tree/main/packages/tta-dev-primitives)
- [Migration PR](https://github.com/theinterneti/TTA/pull/101)

---

Last Updated: October 28, 2025
