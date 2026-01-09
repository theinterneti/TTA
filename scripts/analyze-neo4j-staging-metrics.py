#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Analyze-neo4j-staging-metrics]]
Analyze Neo4j Staging Metrics

This script analyzes the health and metrics logs collected during the
7-day observation period for the Neo4j staging deployment.

Usage:
    python scripts/analyze-neo4j-staging-metrics.py [--days DAYS]

Arguments:
    --days DAYS  Number of days to analyze (default: 7)
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path


def parse_health_log(log_file: Path, days: int = 7) -> tuple[list[dict], dict]:
    """Parse health check log and calculate statistics."""
    cutoff_time = datetime.now() - timedelta(days=days)

    health_checks = []
    stats = {
        "total_checks": 0,
        "up_checks": 0,
        "down_checks": 0,
        "total_response_time": 0,
        "min_response_time": float("inf"),
        "max_response_time": 0,
        "errors": [],
    }

    if not log_file.exists():
        print(f"Warning: Health log not found: {log_file}")
        return health_checks, stats

    with open(log_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp = datetime.fromtimestamp(int(row["timestamp_unix"]))

            if timestamp < cutoff_time:
                continue

            health_checks.append(row)
            stats["total_checks"] += 1

            if row["status"] == "UP":
                stats["up_checks"] += 1
                response_time = int(row["response_time_ms"])
                stats["total_response_time"] += response_time
                stats["min_response_time"] = min(
                    stats["min_response_time"], response_time
                )
                stats["max_response_time"] = max(
                    stats["max_response_time"], response_time
                )
            else:
                stats["down_checks"] += 1
                if row["error"]:
                    stats["errors"].append(
                        {"timestamp": row["timestamp"], "error": row["error"]}
                    )

    return health_checks, stats


def parse_metrics_log(log_file: Path, days: int = 7) -> list[dict]:
    """Parse metrics log."""
    cutoff_time = datetime.now() - timedelta(days=days)

    metrics = []

    if not log_file.exists():
        print(f"Warning: Metrics log not found: {log_file}")
        return metrics

    with open(log_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp = datetime.fromtimestamp(int(row["timestamp_unix"]))

            if timestamp < cutoff_time:
                continue

            metrics.append(row)

    return metrics


def calculate_uptime(stats: dict) -> float:
    """Calculate uptime percentage."""
    if stats["total_checks"] == 0:
        return 0.0

    return (stats["up_checks"] / stats["total_checks"]) * 100


def calculate_avg_response_time(stats: dict) -> float:
    """Calculate average response time."""
    if stats["up_checks"] == 0:
        return 0.0

    return stats["total_response_time"] / stats["up_checks"]


def generate_report(
    health_checks: list[dict], stats: dict, metrics: list[dict], days: int
):
    """Generate analysis report."""
    uptime = calculate_uptime(stats)
    avg_response_time = calculate_avg_response_time(stats)

    # Calculate downtime
    total_minutes = days * 24 * 60
    check_interval_minutes = 5  # Assuming 5-minute intervals
    expected_checks = total_minutes / check_interval_minutes
    downtime_checks = stats["down_checks"]
    downtime_minutes = downtime_checks * check_interval_minutes

    print("=" * 80)
    print("NEO4J STAGING MONITORING REPORT")
    print("=" * 80)
    print()
    print(f"Analysis Period: Last {days} days")
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("-" * 80)
    print("UPTIME STATISTICS")
    print("-" * 80)
    print(f"Total Health Checks: {stats['total_checks']}")
    print(f"Successful Checks: {stats['up_checks']}")
    print(f"Failed Checks: {stats['down_checks']}")
    print(f"Uptime Percentage: {uptime:.2f}%")
    print(
        f"Estimated Downtime: {downtime_minutes:.0f} minutes ({downtime_minutes / 60:.1f} hours)"
    )
    print()

    # Check if uptime meets 99.5% target
    target_uptime = 99.5
    if uptime >= target_uptime:
        print(f"✅ PASSED: Uptime {uptime:.2f}% meets target of {target_uptime}%")
    else:
        print(f"❌ FAILED: Uptime {uptime:.2f}% below target of {target_uptime}%")
        print(f"   Gap: {target_uptime - uptime:.2f}%")
    print()

    print("-" * 80)
    print("PERFORMANCE STATISTICS")
    print("-" * 80)
    if stats["up_checks"] > 0:
        print(f"Average Response Time: {avg_response_time:.2f} ms")
        print(f"Min Response Time: {stats['min_response_time']} ms")
        print(f"Max Response Time: {stats['max_response_time']} ms")
    else:
        print("No successful health checks recorded")
    print()

    print("-" * 80)
    print("ERROR SUMMARY")
    print("-" * 80)
    if stats["errors"]:
        print(f"Total Errors: {len(stats['errors'])}")
        print()
        print("Recent Errors (last 10):")
        for error in stats["errors"][-10:]:
            print(f"  {error['timestamp']}: {error['error']}")
    else:
        print("✅ No errors recorded")
    print()

    print("-" * 80)
    print("METRICS SUMMARY")
    print("-" * 80)
    if metrics:
        print(f"Total Metric Collections: {len(metrics)}")
        print()

        # Calculate average metrics (if available)
        cpu_values = [m["cpu_percent"] for m in metrics if m["cpu_percent"] != "N/A"]
        if cpu_values:
            # Remove '%' sign and convert to float
            cpu_values = [float(v.replace("%", "")) for v in cpu_values]
            print(f"Average CPU Usage: {sum(cpu_values) / len(cpu_values):.2f}%")

        mem_values = [
            m["memory_percent"] for m in metrics if m["memory_percent"] != "N/A"
        ]
        if mem_values:
            # Remove '%' sign and convert to float
            mem_values = [float(v.replace("%", "")) for v in mem_values]
            print(f"Average Memory Usage: {sum(mem_values) / len(mem_values):.2f}%")
    else:
        print("No metrics collected")
    print()

    print("=" * 80)
    print("PROMOTION CRITERIA ASSESSMENT")
    print("=" * 80)
    print()
    print("Staging → Production Criteria:")
    print(
        f"  [{'✅' if uptime >= 99.5 else '❌'}] Uptime ≥99.5% over {days} days: {uptime:.2f}%"
    )
    print("  [⏳] Integration tests passing: Pending validation")
    print("  [⏳] Performance benchmarks met: Pending validation")
    print("  [⏳] Security audit complete: Pending validation")
    print()

    if uptime >= 99.5:
        print(
            "✅ Neo4j staging deployment meets uptime requirement for production promotion"
        )
    else:
        print("❌ Neo4j staging deployment does NOT meet uptime requirement")
        print("   Additional monitoring time needed or investigation required")
    print()
    print("=" * 80)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Analyze Neo4j staging metrics")
    parser.add_argument(
        "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )
    args = parser.parse_args()

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    log_dir = project_root / "logs" / "staging"

    health_log = log_dir / "neo4j-health.log"
    metrics_log = log_dir / "neo4j-metrics.log"

    # Parse logs
    health_checks, stats = parse_health_log(health_log, args.days)
    metrics = parse_metrics_log(metrics_log, args.days)

    # Generate report
    generate_report(health_checks, stats, metrics, args.days)

    # Exit with appropriate code
    uptime = calculate_uptime(stats)
    if uptime >= 99.5:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
