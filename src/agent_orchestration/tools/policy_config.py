"""
Policy configuration for tool execution governance.

- Supports file-based YAML/JSON or environment variables
- Backward compatible with TTA_ALLOWED_CALLABLES
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List, Optional

try:
    import yaml  # type: ignore
except Exception:
    yaml = None  # optional dependency

from pydantic import BaseModel, Field


class ToolPolicyConfig(BaseModel):
    callable_allowlist: List[str] = Field(default_factory=list)
    allow_network_tools: bool = True
    allow_filesystem_tools: bool = True
    allow_process_tools: bool = True
    default_timeout_ms: Optional[int] = None
    max_concurrency: Optional[int] = None
    cpu_limit_percent: Optional[int] = None
    memory_limit_mb: Optional[int] = None


_ENV_BOOL_KEYS = {
    "TTA_ALLOW_NETWORK_TOOLS": "allow_network_tools",
    "TTA_ALLOW_FILESYSTEM_TOOLS": "allow_filesystem_tools",
    "TTA_ALLOW_PROCESS_TOOLS": "allow_process_tools",
}

_ENV_INT_KEYS = {
    "TTA_TOOL_TIMEOUT_MS": "default_timeout_ms",
    "TTA_TOOL_MAX_CONCURRENCY": "max_concurrency",
    "TTA_TOOL_CPU_LIMIT_PERCENT": "cpu_limit_percent",
    "TTA_TOOL_MEMORY_LIMIT_MB": "memory_limit_mb",
}


def _parse_bool(val: str | None, default: bool) -> bool:
    if val is None:
        return default
    v = val.strip().lower()
    return v in ("1", "true", "yes", "y", "on")


def _parse_int(val: str | None) -> Optional[int]:
    if not val:
        return None
    try:
        return int(val)
    except Exception:
        return None


def _load_from_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # detect by extension
    if path.endswith(('.yaml', '.yml')):
        if yaml is None:
            raise RuntimeError("PyYAML not installed but YAML config provided")
        data = yaml.safe_load(content) or {}
    else:
        data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("policy config root must be an object")
    return data


def load_tool_policy_config() -> ToolPolicyConfig:
    """Load ToolPolicyConfig from file or environment; defaults are permissive.

    Order:
      1) If TTA_TOOL_POLICY_CONFIG points to YAML/JSON file, load and parse
      2) Apply env var overrides
      3) Else build from env-only fallbacks
      4) Else return default ToolPolicyConfig()
    """
    cfg_path = os.environ.get("TTA_TOOL_POLICY_CONFIG")
    base: dict = {}

    # 1) File
    if cfg_path and os.path.exists(cfg_path):
        try:
            base = _load_from_file(cfg_path)
        except Exception:
            # fall back to env-only
            base = {}

    # 2) Env overrides (callable allowlist)
    allowed = os.environ.get("TTA_ALLOWED_CALLABLES", "").strip()
    if allowed:
        allowlist = [s.strip() for s in allowed.split(",") if s.strip()]
        base["callable_allowlist"] = allowlist

    # 2b) Env boolean flags
    for env_key, field_name in _ENV_BOOL_KEYS.items():
        if env_key in os.environ:
            base[field_name] = _parse_bool(os.environ.get(env_key), base.get(field_name, True))

    # 2c) Env integer options
    for env_key, field_name in _ENV_INT_KEYS.items():
        if env_key in os.environ:
            parsed = _parse_int(os.environ.get(env_key))
            if parsed is not None:
                base[field_name] = parsed

    # 3/4) Build model (defaults permissive)
    try:
        return ToolPolicyConfig(**base)
    except Exception:
        # if anything goes wrong, return permissive defaults
        return ToolPolicyConfig()

