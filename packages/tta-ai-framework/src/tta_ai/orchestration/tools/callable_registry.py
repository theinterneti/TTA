from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

from .models import ToolSpec


class CallableRegistry:
    """Thread-safe registry mapping ToolSpec (name/version) to Python callables.

    - Supports exact and latest version resolution
    - Designed for pluggable backends: subclass and override core methods
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        # map: name -> { version -> callable }
        self._map: dict[str, dict[str, Callable[..., Any]]] = {}

    def register_callable(
        self, tool_name: str, version: str, callable_fn: Callable[..., Any]
    ) -> None:
        with self._lock:
            self._map.setdefault(tool_name, {})[version] = callable_fn

    def _latest_version(
        self, versions: dict[str, Callable[..., Any]]
    ) -> tuple[str, Callable[..., Any]] | None:
        if not versions:
            return None
        # naive: lexicographic max; can be improved with semver parsing
        v = max(versions.keys())
        return (v, versions[v])

    def resolve_callable(self, spec: ToolSpec) -> Callable[..., Any]:
        name = spec.name
        version = spec.version
        with self._lock:
            versions = self._map.get(name) or {}
            if version and version in versions:
                return versions[version]
            # latest version fallback
            latest = self._latest_version(versions)
            if latest is None:
                raise ValueError(f"No callable registered for tool {name}")
            return latest[1]

    # Extension points for distributed backends
    def get_registered(self) -> dict[str, dict[str, str]]:
        """Return a snapshot of registered entries with dotted paths if possible.
        Default returns function repr (not importable). Override for richer data.
        """
        with self._lock:
            return {
                n: {v: repr(fn) for v, fn in versions.items()} for n, versions in self._map.items()
            }
