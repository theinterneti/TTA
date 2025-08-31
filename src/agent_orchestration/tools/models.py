"""
Tool models and validation for dynamic tool system (Task 7.1/7.2).
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from ..models import AgentId


class ToolStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class ToolParameter(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=512)
    required: bool = True
    schema: dict[str, Any] = Field(
        default_factory=dict, description="JSON schema for the parameter"
    )


class ToolSpec(BaseModel):
    name: str = Field(..., min_length=3, max_length=128)
    version: str = Field("1.0.0", description="Semver string")
    description: str = Field(..., min_length=1, max_length=1024)
    parameters: list[ToolParameter] = Field(default_factory=list)
    returns_schema: dict[str, Any] = Field(default_factory=dict)
    capabilities: list[str] = Field(
        default_factory=list, description="Tags/capabilities e.g. ['kg_read']"
    )
    safety_flags: list[str] = Field(
        default_factory=list,
        description="Flags like 'network', 'filesystem', 'process'",
    )
    owner: AgentId | None = None
    created_at: float = Field(default=0.0)
    last_used_at: float = Field(default=0.0)
    status: ToolStatus = ToolStatus.ACTIVE

    def signature_hash(self) -> str:
        payload = {
            "name": self.name,
            "version": self.version,
            "parameters": [p.model_dump() for p in self.parameters],
            "returns_schema": self.returns_schema,
            "capabilities": sorted(self.capabilities),
            "safety_flags": sorted(self.safety_flags),
        }
        s = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

    @field_validator("version")
    @classmethod
    def _validate_semver(cls, v: str) -> str:
        # very lightweight semver check: X.Y or X.Y.Z numeric
        parts = v.split(".")
        if not (2 <= len(parts) <= 3):
            raise ValueError("version must be in semver-like form e.g. 1.0.0")
        for p in parts:
            if not p.isdigit():
                raise ValueError("version segments must be numeric")
        return v

    @field_validator("parameters")
    @classmethod
    def _limit_params(cls, params: list[ToolParameter]) -> list[ToolParameter]:
        if len(params) > 16:
            raise ValueError("too many parameters (max 16)")
        return params


class ToolRegistration(BaseModel):
    spec: ToolSpec
    registered_at: float


class ToolInvocation(BaseModel):
    tool_name: str
    version: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)


from .policy_config import ToolPolicyConfig


class ToolPolicy(BaseModel):
    # Base flags retained for backward compatibility (if constructed without config)
    allow_network_tools: bool = False
    allow_filesystem_tools: bool = False
    allow_process_tools: bool = False
    allow_subprocess_tools: bool = False
    allow_shell_exec: bool = False
    allowed_callables: list[str] = Field(
        default_factory=list, description="Dot-path allowlist for wrapped callables"
    )
    max_schema_depth: int = 5

    # New configuration container
    config: ToolPolicyConfig | None = None

    def _effective(self) -> ToolPolicyConfig:
        # Merge legacy flags into a ToolPolicyConfig if provided
        if self.config:
            return self.config
        # Defaults permissive except legacy flags, which default to False here to preserve prior behavior
        return ToolPolicyConfig(
            callable_allowlist=list(self.allowed_callables),
            allow_network_tools=self.allow_network_tools,
            allow_filesystem_tools=self.allow_filesystem_tools,
            allow_process_tools=self.allow_process_tools,
        )

    def is_capability_allowed(self, capability: str) -> bool:
        cfg = self._effective()
        if capability == "network":
            return bool(cfg.allow_network_tools)
        if capability == "filesystem":
            return bool(cfg.allow_filesystem_tools)
        if capability == "process":
            return bool(cfg.allow_process_tools)
        # default allow unknown capabilities
        return True

    def get_timeout_ms(self) -> int | None:
        cfg = self._effective()
        return cfg.default_timeout_ms

    def validate_safety_flags(self, safety_flags: list[str]) -> None:
        # Use capability gating
        for flag in safety_flags:
            if not self.is_capability_allowed(flag):
                raise ValueError(f"{flag} tools are disabled by policy")

    def check_safety(self, spec: ToolSpec) -> None:
        # Backward-compat: honor legacy flags and schema depth checks
        self.validate_safety_flags(spec.safety_flags)

        # basic schema depth check
        def depth(obj: Any, d: int = 0) -> int:
            if isinstance(obj, dict):
                return max([d] + [depth(v, d + 1) for v in obj.values()])
            if isinstance(obj, list):
                return max([d] + [depth(v, d + 1) for v in obj])
            return d

        for p in spec.parameters:
            if depth(p.schema) > self.max_schema_depth:
                raise ValueError("parameter schema too deep")
        if depth(spec.returns_schema) > self.max_schema_depth:
            raise ValueError("returns schema too deep")

    def validate_callable_allowed(self, dotted_path: str) -> None:
        cfg = self._effective()
        if cfg.callable_allowlist and dotted_path not in set(cfg.callable_allowlist):
            raise ValueError(f"callable {dotted_path} not in allowed_callables")
