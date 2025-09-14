"""
Base Tool for the TTA Project.

This module provides the base tool class for all tools in the TTA project.
"""

import asyncio
import json
import logging
import os
from collections.abc import Callable
from typing import Any

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for environments without pydantic
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def dict(self, **kwargs):
            return {
                k: v
                for k, v in self.__dict__.items()
                if k not in kwargs.get("exclude", {})
            }

    def Field(*args, **kwargs):
        return None


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolParameter:
    """Schema for a tool parameter."""

    def __init__(
        self,
        name: str,
        description: str,
        type: str = "string",
        required: bool = False,
        default: Any = None,
        enum: list[str] | None = None,
    ):
        """
        Initialize a tool parameter.

        Args:
            name: Name of the parameter
            description: Description of the parameter
            type: Type of the parameter
            required: Whether the parameter is required
            default: Default value for the parameter
            enum: Enumeration of allowed values
        """
        self.name = name
        self.description = description
        self.type = type
        self.required = required
        self.default = default
        self.enum = enum

    def dict(self) -> dict[str, Any]:
        """
        Convert the parameter to a dictionary.

        Returns:
            Dictionary representation of the parameter
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "required": self.required,
            "default": self.default,
            "enum": self.enum,
        }


class BaseTool:
    """Base class for all tools in the TTA project."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: list[ToolParameter] = None,
        action_fn: Callable | None = None,
        kg_read: bool = False,
        kg_write: bool = False,
        tool_type: str = "standard",
    ):
        """
        Initialize a base tool.

        Args:
            name: Name of the tool
            description: Description of what the tool does
            parameters: Parameters for the tool
            action_fn: Function to call when the tool is used
            kg_read: Whether the tool reads from the knowledge graph
            kg_write: Whether the tool writes to the knowledge graph
            tool_type: Type of tool
        """
        self.name = name
        self.description = description
        self.parameters = parameters or []
        self.action_fn = action_fn
        self.kg_read = kg_read
        self.kg_write = kg_write

    def _run_coro_in_thread(self, coro_fn, *args, **kwargs):
        import threading

        result: dict[str, Any] = {}
        error: dict[str, BaseException] = {}

        def _runner():
            try:
                result["v"] = asyncio.run(coro_fn(*args, **kwargs))
            except BaseException as e:
                error["e"] = e

        t = threading.Thread(target=_runner, daemon=True)
        t.start()
        t.join()
        if "e" in error:
            raise error["e"]
        return result.get("v")

    def _direct_call(self, **kwargs) -> Any:
        """Directly call action_fn with best-effort async support (no metrics/policy)."""
        if not self.action_fn:
            raise ValueError(f"Tool {self.name} has no action function")
        if asyncio.iscoroutinefunction(self.action_fn):
            try:
                asyncio.get_running_loop()
                return self.action_fn(**kwargs)
            except RuntimeError:
                return asyncio.run(self.action_fn(**kwargs))
        return self.action_fn(**kwargs)

    def execute(self, **kwargs) -> Any:
        """
        Execute the tool with the given parameters via ToolInvocationService for metrics/policy.
        Backward compatible: falls back to direct call if service is unavailable.

        Args:
            **kwargs: Parameters to pass to the action function

        Returns:
            The result of the action function
        """
        # Validate parameters
        self._validate_parameters(kwargs)

        # Early policy allowlist enforcement (even if we fallback later)
        try:
            from src.agent_orchestration.tools.models import ToolPolicy

            allowed = os.environ.get("TTA_ALLOWED_CALLABLES", "").strip()
            allowed_list = (
                [s.strip() for s in allowed.split(",") if s.strip()] if allowed else []
            )
            if allowed_list:
                dotted = f"{getattr(self.action_fn, '__module__', '')}.{getattr(self.action_fn, '__qualname__', getattr(self.action_fn, '__name__', ''))}"
                ToolPolicy(allowed_callables=allowed_list).validate_callable_allowed(
                    dotted
                )
        except Exception:
            pass

        # Prefer centralized ToolInvocationService if available
        try:
            import redis.asyncio as aioredis

            from src.agent_orchestration.tools.coordinator import ToolCoordinator
            from src.agent_orchestration.tools.invocation_service import (
                ToolInvocationService,
            )
            from src.agent_orchestration.tools.metrics import (  # noqa: F401 (side effects)
                get_tool_metrics,
            )
            from src.agent_orchestration.tools.models import ToolPolicy, ToolSpec
            from src.agent_orchestration.tools.redis_tool_registry import (
                RedisToolRegistry,
            )
        except Exception:
            # Fallback to direct callable if orchestration stack is unavailable
            if self.action_fn:
                return self._direct_call(**kwargs)
            raise ValueError(f"Tool {self.name} has no action function") from None

        # Build registry
        try:
            redis_url = os.environ.get(
                "TTA_REDIS_URL",
                os.environ.get("TEST_REDIS_URI", "redis://localhost:6379/0"),
            )
            rclient = aioredis.from_url(redis_url)
            registry = RedisToolRegistry(rclient, key_prefix="ao")
        except Exception:
            if self.action_fn:
                return self._direct_call(**kwargs)
            raise ValueError(f"Tool {self.name} has no action function") from None

        # Build policy from centralized loader (falls back to env if no file)
        from src.agent_orchestration.tools.policy_config import load_tool_policy_config

        cfg = load_tool_policy_config()
        policy = ToolPolicy(config=cfg, allowed_callables=cfg.callable_allowlist)
        coord = ToolCoordinator(registry=registry, policy=policy)

        # Build ToolSpec with safety flags
        version = getattr(self, "version", None) or "1.0.0"
        name = (
            self.name
            if isinstance(self.name, str) and len(self.name) >= 3
            else f"dyn.{self.name}"
        )
        caps = [
            c for c, v in (("kg_read", self.kg_read), ("kg_write", self.kg_write)) if v
        ]
        safety = []
        if self.kg_read or self.kg_write:
            safety.append("network")
        spec = ToolSpec(
            name=name,
            version=version,
            description=self.description,
            capabilities=caps,
            safety_flags=safety,
        )

        # Enforce callable allowlist explicitly before invocation (raises if not allowed)
        dotted = f"{getattr(self.action_fn, '__module__', '')}.{getattr(self.action_fn, '__qualname__', getattr(self.action_fn, '__name__', ''))}"
        policy.validate_callable_allowed(dotted)

        # Execute via service or return coroutine in running loop
        svc = ToolInvocationService(registry=registry, coordinator=coord, policy=policy)
        if asyncio.iscoroutinefunction(self.action_fn):
            try:
                asyncio.get_running_loop()
                # Execute coroutine in background thread to return concrete result to sync caller
                return self._run_coro_in_thread(self.action_fn, **kwargs)
            except RuntimeError:
                # No loop: execute and return result
                return asyncio.run(
                    svc.invoke_tool_by_spec(spec, self.action_fn, **kwargs)
                )  # type: ignore
        # Synchronous callable path
        return svc.invoke_tool_by_spec_sync(spec, self.action_fn, **kwargs)  # type: ignore

    def _validate_parameters(self, params: dict[str, Any]) -> None:
        """
        Validate parameters against the tool's parameter schema.

        Args:
            params: Parameters to validate

        Raises:
            ValueError: If a required parameter is missing or a parameter has an invalid type
        """
        for param in self.parameters:
            # Check if required parameter is missing
            if param.required and param.name not in params:
                raise ValueError(f"Missing required parameter: {param.name}")

            # Check if parameter is present
            if param.name in params:
                value = params[param.name]

                # Check if parameter has a valid type
                if param.type == "string" and not isinstance(value, str):
                    raise ValueError(
                        f"Parameter {param.name} must be a string, got {type(value)}"
                    )
                elif param.type == "integer" and not isinstance(value, int):
                    raise ValueError(
                        f"Parameter {param.name} must be an integer, got {type(value)}"
                    )
                elif param.type == "boolean" and not isinstance(value, bool):
                    raise ValueError(
                        f"Parameter {param.name} must be a boolean, got {type(value)}"
                    )
                elif param.type == "array" and not isinstance(value, list):
                    raise ValueError(
                        f"Parameter {param.name} must be an array, got {type(value)}"
                    )
                elif param.type == "object" and not isinstance(value, dict):
                    raise ValueError(
                        f"Parameter {param.name} must be an object, got {type(value)}"
                    )

                # Check if parameter has a valid enum value
                if param.enum and value not in param.enum:
                    raise ValueError(
                        f"Parameter {param.name} must be one of {param.enum}, got {value}"
                    )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the tool to a dictionary representation.

        Returns:
            A dictionary representation of the tool
        """
        # Convert to dict excluding action_fn
        tool_dict = {
            "name": self.name,
            "description": self.description,
            "parameters": [param.dict() for param in self.parameters],
            "kg_read": self.kg_read,
            "kg_write": self.kg_write,
            "tool_type": self.tool_type,
        }

        return tool_dict

    def to_json(self) -> str:
        """
        Convert the tool to a JSON string.

        Returns:
            A JSON string representation of the tool
        """
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseTool":
        """
        Create a tool from a dictionary.

        Args:
            data: Dictionary representation of the tool

        Returns:
            A BaseTool instance
        """
        # Convert parameters from dict to ToolParameter
        if "parameters" in data:
            data["parameters"] = [
                ToolParameter(**param) for param in data["parameters"]
            ]

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "BaseTool":
        """
        Create a tool from a JSON string.

        Args:
            json_str: JSON string representation of the tool

        Returns:
            A BaseTool instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
