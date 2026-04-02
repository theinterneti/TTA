#!/usr/bin/env python3
"""
Validate agent configuration boundaries.

Usage:
    python scripts/validate_agent_boundaries.py test-agent
    python scripts/validate_agent_boundaries.py --all
"""

import argparse
import sys
from pathlib import Path

import yaml


def load_agent_config(agent_name: str) -> dict:
    """Load agent configuration from markdown file.

    Args:
        agent_name: Agent name (e.g., "test-agent")

    Returns:
        Parsed YAML frontmatter
    """
    agent_file = Path(f".github/agents/{agent_name}.md")

    if not agent_file.exists():
        print(f"❌ Agent not found: {agent_name}", file=sys.stderr)
        sys.exit(1)

    content = agent_file.read_text()

    # Extract YAML frontmatter (between --- markers)
    if not content.startswith("---"):
        print(f"❌ No YAML frontmatter in {agent_file}", file=sys.stderr)
        sys.exit(1)

    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"❌ Invalid YAML frontmatter in {agent_file}", file=sys.stderr)
        sys.exit(1)

    frontmatter = parts[1].strip()

    try:
        config = yaml.safe_load(frontmatter)
        return config
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in {agent_file}: {e}", file=sys.stderr)
        sys.exit(1)


def validate_boundaries(agent_name: str, config: dict) -> bool:
    """Validate agent boundary configuration.

    Args:
        agent_name: Agent name
        config: Agent configuration

    Returns:
        True if valid
    """
    required_fields = [
        "agent_name",
        "description",
        "version",
        "security_level",
        "boundary_violations_fatal",
        "audit_enabled",
    ]

    all_valid = True

    # Check required fields
    for field in required_fields:
        if field not in config:
            print(f"❌ Missing required field: {field}")
            all_valid = False

    # Validate security level
    if config.get("security_level") not in ["low", "medium", "high", "critical"]:
        print(f"❌ Invalid security_level: {config.get('security_level')}")
        all_valid = False

    # Check agent name matches
    if config.get("agent_name") != agent_name:
        print(f"❌ agent_name mismatch: {config.get('agent_name')} != {agent_name}")
        all_valid = False

    return all_valid


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate agent boundaries")
    parser.add_argument(
        "agent_name", nargs="?", help="Agent name to validate (e.g., test-agent)"
    )
    parser.add_argument("--all", action="store_true", help="Validate all agents")
    args = parser.parse_args()

    if args.all:
        agent_dir = Path(".github/agents")
        agent_files = [f.stem for f in agent_dir.glob("*.md") if f.stem != "SCHEMA"]
        print(f"📂 Validating {len(agent_files)} agents\n")

        all_valid = True
        for agent_name in agent_files:
            print(f"Validating {agent_name}...")
            config = load_agent_config(agent_name)
            if not validate_boundaries(agent_name, config):
                all_valid = False
            else:
                print(f"✅ {agent_name} configuration valid\n")

        if all_valid:
            print("\n✅ All agent configurations valid")
            sys.exit(0)
        else:
            print("\n❌ Some agent configurations invalid")
            sys.exit(1)

    elif args.agent_name:
        config = load_agent_config(args.agent_name)
        if validate_boundaries(args.agent_name, config):
            print(f"✅ {args.agent_name} configuration valid")
            sys.exit(0)
        else:
            print(f"❌ {args.agent_name} configuration invalid")
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
