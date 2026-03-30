#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Sync-component-docs]]
TTA Component Documentation Sync Script

Syncs component metrics from component-maturity-analysis.json to documentation files
to prevent discrepancies between automated reporting and manual documentation.

Usage:
    python scripts/sync-component-docs.py
    python scripts/sync-component-docs.py --dry-run
    python scripts/sync-component-docs.py --component "Narrative Arc Orchestrator"
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Component metrics source file
METRICS_SOURCE = Path("component-maturity-analysis.json")

# Documentation files to sync
DOCS_TO_SYNC = [
    "docs/component-promotion/COMPONENT_MATURITY_STATUS.md",
    "docs/component-promotion/TOP_3_PRIORITIES.md",
]


def load_component_metrics() -> dict[str, Any]:
    """Load component metrics from JSON file."""
    if not METRICS_SOURCE.exists():
        msg = f"❌ ERROR: {METRICS_SOURCE} not found!\n"
        msg += "Run the component analysis script first:\n"
        msg += "  uv run python scripts/analyze-component-maturity.py"
        sys.stderr.write(msg + "\n")
        sys.exit(1)

    return json.loads(METRICS_SOURCE.read_text())


def flatten_components(metrics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Flatten component data for easier access."""
    all_components = {}
    for group_name, components in metrics.items():
        for component_name, component_data in components.items():
            all_components[component_name] = {
                **component_data,
                "functional_group": group_name,
            }
    return all_components


def validate_documentation_consistency(
    components: dict[str, dict[str, Any]], dry_run: bool = False
) -> bool:
    """
    Validate that documentation files match component metrics.

    Returns True if all docs are consistent, False otherwise.
    """

    inconsistencies_found = False

    for doc_file in DOCS_TO_SYNC:
        doc_path = Path(doc_file)
        if not doc_path.exists():
            continue

        content = doc_path.read_text()

        # Check each component's coverage in the document
        for component_name, component_data in components.items():
            actual_coverage = component_data.get("coverage", {}).get("coverage", 0)

            # Find coverage references in document
            # Pattern: component name followed by coverage percentage
            pattern = rf"{re.escape(component_name)}.*?(\d+\.?\d*)%"
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)

            for match in matches:
                doc_coverage = float(match.group(1))

                # Allow 0.1% tolerance for rounding
                if abs(doc_coverage - actual_coverage) > 0.1:
                    inconsistencies_found = True

    if not inconsistencies_found:
        return True
    if not dry_run:
        pass
    return False


def generate_sync_report(components: dict[str, dict[str, Any]]) -> None:
    """Generate a report of current component metrics."""

    # Group by functional area
    by_group: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for name, data in components.items():
        group = data.get("functional_group", "Unknown")
        if group not in by_group:
            by_group[group] = []
        by_group[group].append((name, data))

    for _group_name, group_components in sorted(by_group.items()):
        for _component_name, component_data in sorted(group_components):
            component_data.get("coverage", {}).get("coverage", 0)
            component_data.get("current_stage", "Unknown")
            component_data.get("blocker_count", 0)


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Sync component metrics to documentation files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check for inconsistencies without making changes",
    )
    parser.add_argument(
        "--component",
        type=str,
        help="Check specific component only",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate component metrics report",
    )

    args = parser.parse_args()

    # Load component metrics
    metrics = load_component_metrics()
    components = flatten_components(metrics)

    # Filter to specific component if requested
    if args.component:
        if args.component not in components:
            sys.exit(1)
        components = {args.component: components[args.component]}

    # Generate report if requested
    if args.report:
        generate_sync_report(components)
        return

    # Validate documentation consistency
    is_consistent = validate_documentation_consistency(components, dry_run=args.dry_run)

    if not is_consistent:
        sys.exit(1)


if __name__ == "__main__":
    main()
