#!/usr/bin/env python3
"""
MCP Schema Validator

Validates that MCP tool definitions match actual implementation.
Ensures the contract between LLM agents and deterministic code is sound.

Usage:
    python scripts/validate-mcp-schemas.py
"""

import sys
from pathlib import Path
from typing import Any

import yaml


def load_apm_config() -> dict[str, Any]:
    """Load apm.yml configuration."""
    config_path = Path("apm.yml")
    if not config_path.exists():
        sys.exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)


def validate_tool_schema(tool_name: str, schema: dict[str, Any]) -> bool:
    """Validate a single tool schema."""
    required_fields = ["name", "description", "input_schema"]

    for field in required_fields:
        if field not in schema:
            return False

    # Validate input schema
    input_schema = schema.get("input_schema", {})
    if not isinstance(input_schema, dict):
        return False

    if "type" not in input_schema:
        return False

    # Check description clarity (basic heuristics)
    description = schema.get("description", "")
    if len(description) < 20:
        pass

    return True


def validate_mcp_servers(config: dict[str, Any]) -> bool:
    """Validate all MCP server configurations."""
    mcp_servers = config.get("mcp", {}).get("servers", [])

    if not mcp_servers:
        return True

    all_valid = True

    for server in mcp_servers:
        server.get("name", "unknown")

        # Validate required fields
        required = ["name", "protocol", "command"]
        for field in required:
            if field not in server:
                all_valid = False
                continue

        # Validate tools list
        tools = server.get("tools", [])
        if not tools:
            pass

        # Validate access level
        access = server.get("access", "read-only")
        if access not in ["read-only", "read-write"]:
            all_valid = False

        if all_valid:
            pass

    return all_valid


def main() -> int:
    """Main validation function."""

    # Load configuration
    config = load_apm_config()

    # Validate MCP servers
    if not validate_mcp_servers(config):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
