#!/usr/bin/env python3
"""
Component Registry CLI

Command-line interface for TTA component registry and maturity tracking.
"""

# ruff: noqa: ALL

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.registry import ComponentRegistry

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def cmd_list(args):
    """List all components."""
    registry = ComponentRegistry()
    components = registry.get_all_components()

    if not components:
        print("No components found.")
        return

    # Sort by name
    components = sorted(components, key=lambda c: c.name)

    # Print header
    print(f"\n{'Component':<30} {'Stage':<15} {'Coverage':<10} {'MATURITY.md':<15}")
    print("=" * 70)

    # Print components
    for comp in components:
        stage_emoji = "✅" if comp.current_stage in ["Staging", "Production"] else "⚠️"
        stage = f"{stage_emoji} {comp.current_stage}"

        # Get coverage from last metrics
        coverage = "N/A"
        if comp.last_metrics:
            cov_pct = comp.last_metrics.get("coverage", {}).get("percentage", 0)
            coverage = f"{cov_pct:.1f}%"

        maturity = "✓" if comp.maturity_file else "✗"

        print(f"{comp.name:<30} {stage:<15} {coverage:<10} {maturity:<15}")

    print(f"\nTotal: {len(components)} components")


def cmd_show(args):
    """Show detailed information about a component."""
    registry = ComponentRegistry()
    component = registry.get_component(args.component)

    if not component:
        print(f"Component '{args.component}' not found.")
        return 1

    print(f"\n=== {component.display_name} ===\n")
    print(f"Name: {component.name}")
    print(f"Stage: {component.current_stage}")
    print(f"Owner: {component.owner}")
    print(f"Functional Group: {component.functional_group}")
    print(f"Type: {component.component_type}")
    print("\nPaths:")
    print(f"  Source: {component.source_path}")
    print(f"  Tests: {component.test_path or 'None'}")
    print(f"  MATURITY.md: {component.maturity_file or 'None'}")

    if component.last_metrics:
        print(f"\nMetrics (Last Updated: {component.last_updated or 'Unknown'}):")
        m = component.last_metrics

        cov = m.get("coverage", {})
        print(
            f"  Coverage: {cov.get('percentage', 0):.1f}% ({cov.get('lines_covered', 0)}/{cov.get('lines_total', 0)} lines)"
        )

        lint = m.get("linting", {})
        print(f"  Linting: {lint.get('total_violations', 0)} violations")

        tc = m.get("type_checking", {})
        print(
            f"  Type Checking: {tc.get('errors', 0)} errors, {tc.get('warnings', 0)} warnings"
        )

        sec = m.get("security", {})
        print(f"  Security: {sec.get('total_issues', 0)} issues")

        tests = m.get("tests", {})
        print(
            f"  Tests: {tests.get('passed', 0)} passed, {tests.get('failed', 0)} failed, {tests.get('skipped', 0)} skipped"
        )

        # Check staging criteria
        meets_staging = (
            cov.get("percentage", 0) >= 70.0
            and lint.get("total_violations", 1) == 0
            and tc.get("errors", 1) == 0
            and sec.get("total_issues", 1) == 0
            and tests.get("failed", 1) == 0
        )
        print(f"\nMeets Staging Criteria: {'✅ Yes' if meets_staging else '❌ No'}")
    else:
        print("\nNo metrics available. Run 'update-maturity' to collect metrics.")


def cmd_update_maturity(args):
    """Update maturity metrics for components."""
    registry = ComponentRegistry()

    if args.all:
        print("Updating metrics for all components...\n")
        results = registry.update_all_metrics(dry_run=args.dry_run)

        print("\n=== RESULTS ===")
        print(f"Total: {results['total']}")
        print(f"Updated: {len(results['updated'])}")
        print(f"Failed: {len(results['failed'])}")

        if results["updated"]:
            print("\n=== UPDATED COMPONENTS ===")
            for comp in results["updated"]:
                meets = "✅" if comp["meets_staging"] else "❌"
                print(
                    f"{comp['name']:<30} | Coverage: {comp['coverage']:5.1f}% | Staging: {meets}"
                )

        if results["failed"]:
            print("\n=== FAILED ===")
            for fail in results["failed"]:
                print(f"{fail['component']}: {fail['error']}")

        if args.dry_run:
            print("\n(Dry run - no changes saved)")
    else:
        # Update single component
        component = registry.get_component(args.component)
        if not component:
            print(f"Component '{args.component}' not found.")
            return 1

        print(f"Updating metrics for {component.name}...")
        # For now, just run update_all_metrics with filter
        # In production, we'd have a single-component update method
        results = registry.update_all_metrics(dry_run=args.dry_run)

        # Find our component in results
        comp_result = next(
            (c for c in results["updated"] if c["name"] == component.name), None
        )
        if comp_result:
            meets = "✅" if comp_result["meets_staging"] else "❌"
            print(f"\nCoverage: {comp_result['coverage']:.1f}%")
            print(f"Meets Staging: {meets}")
        else:
            print(f"Failed to update {component.name}")


def cmd_validate(args):
    """Validate component maturity status."""
    registry = ComponentRegistry()

    if args.all:
        components = registry.get_all_components()
    else:
        component = registry.get_component(args.component)
        if not component:
            print(f"Component '{args.component}' not found.")
            return 1
        components = [component]

    print("\n=== VALIDATION REPORT ===\n")

    for comp in components:
        if not comp.last_metrics:
            print(f"{comp.name}: ⚠️ No metrics available")
            continue

        m = comp.last_metrics
        cov = m.get("coverage", {}).get("percentage", 0)
        lint = m.get("linting", {}).get("total_violations", 0)
        tc = m.get("type_checking", {}).get("errors", 0)
        sec = m.get("security", {}).get("total_issues", 0)
        tests = m.get("tests", {}).get("failed", 0)

        meets_staging = (
            cov >= 70.0 and lint == 0 and tc == 0 and sec == 0 and tests == 0
        )

        status = "✅" if meets_staging else "❌"
        print(f"{comp.name}: {status}")

        if not meets_staging:
            print("  Issues:")
            if cov < 70.0:
                print(f"    - Coverage: {cov:.1f}% (need ≥70%)")
            if lint > 0:
                print(f"    - Linting: {lint} violations")
            if tc > 0:
                print(f"    - Type checking: {tc} errors")
            if sec > 0:
                print(f"    - Security: {sec} issues")
            if tests > 0:
                print(f"    - Tests: {tests} failed")


def cmd_promotion_candidates(args):
    """List components ready for promotion."""
    registry = ComponentRegistry()
    candidates = registry.get_promotion_candidates()

    if not candidates:
        print("No components meet staging promotion criteria.")
        print("\nRun 'update-maturity --all' to collect latest metrics.")
        return

    print(f"\n=== PROMOTION CANDIDATES ({len(candidates)}) ===\n")

    for comp in candidates:
        m = comp.last_metrics
        cov = m.get("coverage", {}).get("percentage", 0)
        print(f"✅ {comp.name:<30} | Coverage: {cov:.1f}%")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TTA Component Registry CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    parser_list = subparsers.add_parser("list", help="List all components")
    parser_list.set_defaults(func=cmd_list)

    # Show command
    parser_show = subparsers.add_parser("show", help="Show component details")
    parser_show.add_argument("component", help="Component name")
    parser_show.set_defaults(func=cmd_show)

    # Update maturity command
    parser_update = subparsers.add_parser(
        "update-maturity", help="Update component maturity metrics"
    )
    parser_update.add_argument(
        "--all", action="store_true", help="Update all components"
    )
    parser_update.add_argument(
        "--dry-run", action="store_true", help="Don't save changes"
    )
    parser_update.add_argument(
        "component", nargs="?", help="Component name (if not --all)"
    )
    parser_update.set_defaults(func=cmd_update_maturity)

    # Validate command
    parser_validate = subparsers.add_parser(
        "validate", help="Validate component maturity"
    )
    parser_validate.add_argument(
        "--all", action="store_true", help="Validate all components"
    )
    parser_validate.add_argument(
        "component", nargs="?", help="Component name (if not --all)"
    )
    parser_validate.set_defaults(func=cmd_validate)

    # Promotion candidates command
    parser_promo = subparsers.add_parser(
        "promotion-candidates", help="List promotion candidates"
    )
    parser_promo.set_defaults(func=cmd_promotion_candidates)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
