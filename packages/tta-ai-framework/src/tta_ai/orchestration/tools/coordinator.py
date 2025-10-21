"""
ToolCoordinator for dynamic tool generation, validation, and sharing (Task 7.1).
"""

from __future__ import annotations

import asyncio
import contextlib
import time
from collections.abc import Awaitable, Callable

from .metrics import get_tool_metrics, run_with_metrics
from .models import ToolPolicy, ToolSpec
from .redis_tool_registry import RedisToolRegistry

FactoryFn = Callable[[], Awaitable[ToolSpec]] | Callable[[], ToolSpec]


class ToolCoordinator:
    def __init__(
        self, registry: RedisToolRegistry, policy: ToolPolicy | None = None
    ) -> None:
        self._registry = registry
        self._policy = policy or ToolPolicy()
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock_for(self, sig: str) -> asyncio.Lock:
        if sig not in self._locks:
            self._locks[sig] = asyncio.Lock()
        return self._locks[sig]

    async def create_or_get(self, signature: str, factory_fn: FactoryFn) -> ToolSpec:
        """
        Get a tool by stable signature (e.g., ToolSpec.signature_hash) or create+register it.
        The factory_fn must build a ToolSpec with all fields populated.
        """
        # Acquire a per-signature lock to avoid duplicate creation across tasks.
        async with self._lock_for(signature):
            # Build spec via factory
            spec = (
                await factory_fn()
                if asyncio.iscoroutinefunction(factory_fn)
                else factory_fn()
            )
            # Validate safety and constraints before registration
            self._policy.check_safety(spec)
            now = time.time()
            if not spec.created_at:
                spec.created_at = now
            spec.last_used_at = now
            # Register idempotently; if exists, fetch existing
            created = await self._registry.register_tool(spec)
            if not created:
                existing = await self._registry.get_tool(spec.name, spec.version)
                if existing is None:
                    # race condition or deletion; try once more
                    await self._registry.register_tool(spec)
                    existing = await self._registry.get_tool(spec.name, spec.version)
                spec = existing or spec
            return spec

    async def run_tool(
        self, spec: ToolSpec, fn: Callable[..., object], *args, **kwargs
    ):
        """Run a tool callable with automatic metrics collection and policy timeouts."""
        timeout_ms = (
            self._policy.get_timeout_ms()
            if hasattr(self._policy, "get_timeout_ms")
            else None
        )
        res = run_with_metrics(spec.name, spec.version, fn, *args, **kwargs)
        # Async path: enforce timeout via asyncio.wait_for
        if hasattr(res, "__await__"):
            if timeout_ms and timeout_ms > 0:
                try:
                    return await asyncio.wait_for(res, timeout=timeout_ms / 1000.0)  # type: ignore
                except Exception:
                    # ensure metrics failure recorded on timeout/cancel
                    with contextlib.suppress(Exception):
                        get_tool_metrics().record_failure(spec.name, spec.version, 0.0)
                    raise
            return await res  # type: ignore
        # Sync path: best-effort timeout using a thread
        if timeout_ms and timeout_ms > 0:
            import queue
            import threading

            q: queue.Queue[tuple[str, object]] = queue.Queue()

            def _runner():
                try:
                    v = run_with_metrics(spec.name, spec.version, fn, *args, **kwargs)
                    q.put(("ok", v))
                except BaseException as e:
                    q.put(("err", e))

            t = threading.Thread(target=_runner, daemon=True)
            t.start()
            t.join(timeout_ms / 1000.0)
            if t.is_alive():
                with contextlib.suppress(Exception):
                    get_tool_metrics().record_failure(
                        spec.name, spec.version, timeout_ms
                    )
                # cannot kill the thread safely; document limitation
                raise TimeoutError(
                    f"Tool '{spec.name}:{spec.version}' execution exceeded {timeout_ms} ms"
                )
            kind, payload = q.get_nowait()
            if kind == "err":
                raise payload  # type: ignore
            return payload
        # Default sync path with metrics already collected
        return res
