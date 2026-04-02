"""Re-exports FreeModelTracker from ttadev.primitives.llm.

The canonical implementation lives in TTA.dev.

Compatibility note
------------------
TTA's ``__init__.py`` imports ``load_cached_models``, ``recommend_for_role``,
and ``save_cache`` from this module.  Those names were renamed or privatised
upstream, so this shim exposes backwards-compatible versions.

Note: ``fetch_free_models`` and ``get_free_models`` are now async coroutines;
sync callers must be updated separately.
"""

from __future__ import annotations

from ttadev.primitives.llm import (
    FreeModelTracker,
    ORModel,
    fetch_free_models,
    get_free_models,
    rank_models_for_role,
)
from ttadev.primitives.llm.free_model_tracker import (
    _DEFAULT_CACHE_PATH,
    _load_cache,
    _save_cache,
)

# ── Backwards-compatible aliases ──────────────────────────────────────────────

#: Alias kept for callers that used ``recommend_for_role`` (renamed upstream).
recommend_for_role = rank_models_for_role


def load_cached_models() -> tuple[list[ORModel], float]:
    """Compatibility shim — load cached free models from the default cache path."""
    return _load_cache(_DEFAULT_CACHE_PATH)


def save_cache(models: list[ORModel]) -> None:
    """Compatibility shim — persist free models to the default cache path."""
    _save_cache(models, _DEFAULT_CACHE_PATH)


__all__ = [
    "FreeModelTracker",
    "ORModel",
    "fetch_free_models",
    "get_free_models",
    "rank_models_for_role",
    "recommend_for_role",
    "load_cached_models",
    "save_cache",
]
