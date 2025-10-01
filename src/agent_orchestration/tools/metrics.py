"""
Tool execution metrics aggregator for dynamic tools.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ToolExecStats:
    successes: int = 0
    failures: int = 0
    total_duration_ms: float = 0.0
    # simple histogram buckets in ms
    buckets: dict[str, int] = field(
        default_factory=lambda: {
            "<10": 0,
            "10-50": 0,
            "50-200": 0,
            "200-1000": 0,
            ">=1000": 0,
        }
    )

    def observe(self, duration_ms: float, ok: bool) -> None:
        if ok:
            self.successes += 1
        else:
            self.failures += 1
        self.total_duration_ms += float(duration_ms)
        d = float(duration_ms)
        if d < 10:
            self.buckets["<10"] += 1
        elif d < 50:
            self.buckets["10-50"] += 1
        elif d < 200:
            self.buckets["50-200"] += 1
        elif d < 1000:
            self.buckets["200-1000"] += 1
        else:
            self.buckets[">=1000"] += 1

    def snapshot(self) -> dict:
        total = self.successes + self.failures
        error_rate = (self.failures / total) if total else 0.0
        avg_ms = (self.total_duration_ms / total) if total else 0.0
        return {
            "successes": self.successes,
            "failures": self.failures,
            "error_rate": error_rate,
            "avg_ms": avg_ms,
            "buckets": dict(self.buckets),
        }


class ToolMetrics:
    def __init__(self) -> None:
        self._tools: dict[str, ToolExecStats] = {}
        self._last_update = time.time()

    def _key(self, name: str, version: str) -> str:
        return f"{name}:{version}"

    def record_success(self, name: str, version: str, duration_ms: float) -> None:
        k = self._key(name, version)
        s = self._tools.setdefault(k, ToolExecStats())
        s.observe(duration_ms, ok=True)

    def record_failure(self, name: str, version: str, duration_ms: float) -> None:
        k = self._key(name, version)
        s = self._tools.setdefault(k, ToolExecStats())
        s.observe(duration_ms, ok=False)

    def snapshot(self) -> dict[str, dict]:
        self._last_update = time.time()
        return {k: v.snapshot() for k, v in self._tools.items()}


# Lightweight decorator and context manager for automatic metrics
import time as _time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def tool_execution(name: str, version: str) -> Callable[[F], F]:
    """Decorator to record duration and outcome for a tool call."""

    def _decorator(fn: F) -> F:
        @wraps(fn)
        def _wrapped(*args, **kwargs):
            start = _time.perf_counter()
            try:
                res = fn(*args, **kwargs)
                if hasattr(res, "__await__"):
                    # handle coroutine
                    async def _awaitable():
                        try:
                            r = await res  # type: ignore
                            dur = (_time.perf_counter() - start) * 1000.0
                            try:
                                get_tool_metrics().record_success(name, version, dur)
                            except Exception:
                                pass
                            return r
                        except Exception:
                            dur = (_time.perf_counter() - start) * 1000.0
                            try:
                                get_tool_metrics().record_failure(name, version, dur)
                            except Exception:
                                pass
                            raise

                    return _awaitable()
                # sync path
                dur = (_time.perf_counter() - start) * 1000.0
                try:
                    get_tool_metrics().record_success(name, version, dur)
                except Exception:
                    pass
                return res
            except Exception:
                dur = (_time.perf_counter() - start) * 1000.0
                try:
                    get_tool_metrics().record_failure(name, version, dur)
                except Exception:
                    pass
                raise

        return _wrapped  # type: ignore

    return _decorator


@contextmanager
def tool_exec_context(name: str, version: str) -> Generator[None, None, None]:
    start = _time.perf_counter()
    try:
        yield
        dur = (_time.perf_counter() - start) * 1000.0
        try:
            get_tool_metrics().record_success(name, version, dur)
        except Exception:
            pass
    except Exception:
        dur = (_time.perf_counter() - start) * 1000.0
        try:
            get_tool_metrics().record_failure(name, version, dur)
        except Exception:
            pass
        raise


def run_with_metrics(
    name: str, version: str, fn: Callable[..., Any], *args, **kwargs
) -> Any:
    """Run function and record metrics; supports sync and async return."""
    wrapped = tool_execution(name, version)(fn)
    return wrapped(*args, **kwargs)


# Singleton accessor
_tool_metrics_singleton: ToolMetrics | None = None


def get_tool_metrics() -> ToolMetrics:
    global _tool_metrics_singleton
    if _tool_metrics_singleton is None:
        _tool_metrics_singleton = ToolMetrics()
    return _tool_metrics_singleton
