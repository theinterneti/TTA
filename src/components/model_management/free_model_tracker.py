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

from pathlib import Path

from ttadev.primitives.llm import (
    FreeModelTracker,
    ORModel,
    fetch_free_models,
    get_free_models,
    rank_models_for_role,
)
from ttadev.primitives.llm.free_model_tracker import (
    _DEFAULT_CACHE_PATH,
    _DEFAULT_CACHE_TTL,
    _load_cache,
    _save_cache,
)

# ── Backwards-compatible aliases ──────────────────────────────────────────────

#: Public alias for the cache TTL constant (used by tests and callers).
CACHE_TTL_SECONDS: float = _DEFAULT_CACHE_TTL

#: Public alias for the cache path (can be patched in tests).
CACHE_PATH: Path = _DEFAULT_CACHE_PATH

#: Alias kept for callers that used ``recommend_for_role`` (renamed upstream).
recommend_for_role = rank_models_for_role


def load_cached_models(cache_path: Path | None = None) -> tuple[list[ORModel], float]:
    """Compatibility shim — load cached free models from the given or default cache path."""
    return _load_cache(cache_path if cache_path is not None else CACHE_PATH)


def save_cache(models: list[ORModel], cache_path: Path | None = None) -> None:
    """Compatibility shim — persist free models to the given or default cache path."""
    _save_cache(models, cache_path if cache_path is not None else CACHE_PATH)


__all__ = [
    "CACHE_PATH",
    "CACHE_TTL_SECONDS",
    "FreeModelTracker",
    "ORModel",
    "fetch_free_models",
    "get_free_models",
    "rank_models_for_role",
    "recommend_for_role",
    "load_cached_models",
    "save_cache",
]
