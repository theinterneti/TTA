"""

# Logseq: [[TTA.dev/Agent_orchestration/Tools/Invocation_service]]
ToolInvocationService: Centralized entry point for dynamic tool executions.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from .coordinator import FactoryFn, ToolCoordinator
from .models import ToolPolicy, ToolSpec
from .redis_tool_registry import RedisToolRegistry

logger = logging.getLogger(__name__)


def _callable_dotted_path(fn: Callable[..., Any]) -> str:
    mod = getattr(fn, "__module__", "")
    qn = getattr(fn, "__qualname__", getattr(fn, "__name__", ""))
    return f"{mod}.{qn}" if mod else qn


class ToolInvocationService:
    def __init__(
        self,
        registry: RedisToolRegistry,
        coordinator: ToolCoordinator,
        policy: ToolPolicy,
        *,
        callable_resolver: Callable[[ToolSpec], Callable[..., Any]] | None = None,
        on_error: Callable[[Exception, ToolSpec], Any] | None = None,
    ) -> None:
        self._registry = registry
        self._coord = coordinator
        self._policy = policy
        self._resolve = callable_resolver
        self._on_error = on_error

    async def invoke_tool(
        self, tool_name: str, version: str | None, arguments: dict[str, Any]
    ) -> Any:
        spec = await self._registry.get_tool(tool_name, version)
        if not spec:
            raise ValueError(f"Tool not found: {tool_name} {version or '(latest)'}")
        if not self._resolve:
            raise ValueError("No callable_resolver provided for name-based invocation")
        fn = self._resolve(spec)
        # Policy checks: safety and allowlist
        try:
            # capability/safety
            if hasattr(self._policy, "validate_safety_flags"):
                self._policy.validate_safety_flags(spec.safety_flags)
            # callable allowlist
            dotted = _callable_dotted_path(fn)
            self._policy.validate_callable_allowed(dotted)
        except Exception:
            raise
        try:
            return await self._coord.run_tool(spec, fn, **(arguments or {}))
        except Exception as e:
            logger.exception("Tool invocation failed: %s %s", spec.name, spec.version)
            if self._on_error:
                return self._on_error(e, spec)
            raise

    async def invoke_tool_by_spec(
        self, spec: ToolSpec, callable_fn: Callable[..., Any], *args, **kwargs
    ) -> Any:
        # Policy checks: safety and allowlist
        try:
            if hasattr(self._policy, "validate_safety_flags"):
                self._policy.validate_safety_flags(spec.safety_flags)
            dotted = _callable_dotted_path(callable_fn)
            self._policy.validate_callable_allowed(dotted)
        except Exception:
            raise
        try:
            return await self._coord.run_tool(spec, callable_fn, *args, **kwargs)
        except Exception as e:
            logger.exception(
                "Tool invocation by spec failed: %s %s", spec.name, spec.version
            )
            if self._on_error:
                return self._on_error(e, spec)
            raise

    async def register_and_invoke(
        self,
        factory_fn: FactoryFn,
        signature: str,
        callable_fn: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Any:
        spec = await self._coord.create_or_get(signature, factory_fn)
        # Policy checks: safety and allowlist
        try:
            if hasattr(self._policy, "validate_safety_flags"):
                self._policy.validate_safety_flags(spec.safety_flags)
            dotted = _callable_dotted_path(callable_fn)
            self._policy.validate_callable_allowed(dotted)
        except Exception:
            raise
        try:
            return await self._coord.run_tool(spec, callable_fn, *args, **kwargs)
        except Exception as e:
            logger.exception(
                "Tool register+invoke failed: %s %s", spec.name, spec.version
            )
            if self._on_error:
                return self._on_error(e, spec)
            raise

    # Synchronous wrappers
    def invoke_tool_sync(
        self, tool_name: str, version: str | None, arguments: dict[str, Any]
    ) -> Any:
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "invoke_tool_sync cannot run inside an active event loop"
            )
        except RuntimeError:
            return asyncio.run(self.invoke_tool(tool_name, version, arguments))

    def invoke_tool_by_spec_sync(
        self, spec: ToolSpec, callable_fn: Callable[..., Any], *args, **kwargs
    ) -> Any:
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "invoke_tool_by_spec_sync cannot run inside an active event loop"
            )
        except RuntimeError:
            return asyncio.run(
                self.invoke_tool_by_spec(spec, callable_fn, *args, **kwargs)
            )

    def register_and_invoke_sync(
        self,
        factory_fn: FactoryFn,
        signature: str,
        callable_fn: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Any:
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "register_and_invoke_sync cannot run inside an active event loop"
            )
        except RuntimeError:
            return asyncio.run(
                self.register_and_invoke(
                    factory_fn, signature, callable_fn, *args, **kwargs
                )
            )
