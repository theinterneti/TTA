# Logseq: [[TTA.dev/Scripts/Performance_regression_check]]
# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Performance Regression Detection Script

This script analyzes test results and performance metrics to detect
performance regressions in the TTA application.
"""

import argparse
import json
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from defusedxml import ElementTree as ET


@dataclass
class PerformanceMetric:
    """Performance metric data."""

    name: str
    value: float
    unit: str
    timestamp: datetime
    test_category: str


@dataclass
class RegressionResult:
    """Regression detection result."""

    metric_name: str
    current_value: float
    baseline_value: float
    change_percent: float
    is_regression: bool
    severity: str  # 'minor', 'major', 'critical'


class PerformanceRegressionDetector:
    """Detects performance regressions by comparing current metrics with baseline."""

    def __init__(self, threshold_percent: float = 20.0):
        self.threshold_percent = threshold_percent
        self.baseline_metrics: dict[str, float] = {}
        self.current_metrics: dict[str, float] = {}

    def load_test_results(self, test_results_dir: Path) -> list[PerformanceMetric]:
        """Load performance metrics from test results."""
        metrics = []

        # Load JUnit XML files
        for xml_file in test_results_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                # Extract test execution times
                for testcase in root.findall(".//testcase"):
                    name = testcase.get("name", "unknown")
                    time_str = testcase.get("time", "0")
                    classname = testcase.get("classname", "unknown")

                    try:
                        execution_time = float(time_str)
                        metrics.append(
                            PerformanceMetric(
                                name=f"test_execution_time_{name}",
                                value=execution_time,
                                unit="seconds",
                                timestamp=datetime.now(),
                                test_category=classname,
                            )
                        )
                    except ValueError:
                        continue

            except ET.ParseError:
                continue

        # Load custom metrics files (JSON format)
        for json_file in test_results_dir.glob("*-metrics.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                for metric_name, metric_data in data.items():
                    if isinstance(metric_data, dict) and "value" in metric_data:
                        metrics.append(
                            PerformanceMetric(
                                name=metric_name,
                                value=float(metric_data["value"]),
                                unit=metric_data.get("unit", "unknown"),
                                timestamp=datetime.now(),
                                test_category=metric_data.get("category", "custom"),
                            )
                        )
                    elif isinstance(metric_data, (int, float)):
                        metrics.append(
                            PerformanceMetric(
                                name=metric_name,
                                value=float(metric_data),
                                unit="unknown",
                                timestamp=datetime.now(),
                                test_category="custom",
                            )
                        )
            except (json.JSONDecodeError, FileNotFoundError):
                continue

        return metrics

    def load_baseline_metrics(
        self, baseline_file: Path | None = None
    ) -> dict[str, float]:
        """Load baseline metrics from file or use defaults."""
        if baseline_file and baseline_file.exists():
            try:
                with open(baseline_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Default baseline metrics (these would typically come from historical data)
        return {
            "avg_test_execution_time": 5.0,  # seconds
            "avg_http_response_time": 0.5,  # seconds
            "avg_story_generation_time": 10.0,  # seconds
            "avg_model_response_time": 2.0,  # seconds
            "memory_usage_peak": 512.0,  # MB
            "cpu_usage_peak": 50.0,  # percent
        }

    def calculate_aggregated_metrics(
        self, metrics: list[PerformanceMetric]
    ) -> dict[str, float]:
        """Calculate aggregated metrics from raw performance data."""
        aggregated = {}

        # Group metrics by category
        by_category = {}
        for metric in metrics:
            category = metric.test_category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(metric.value)

        # Calculate averages for each category
        for category, values in by_category.items():
            if values:
                aggregated[f"avg_{category}_execution_time"] = statistics.mean(values)
                aggregated[f"max_{category}_execution_time"] = max(values)
                aggregated[f"p95_{category}_execution_time"] = (
                    statistics.quantiles(values, n=20)[18]
                    if len(values) > 1
                    else values[0]
                )

        # Calculate overall metrics
        all_values = [m.value for m in metrics]
        if all_values:
            aggregated["avg_test_execution_time"] = statistics.mean(all_values)
            aggregated["max_test_execution_time"] = max(all_values)
            aggregated["total_test_time"] = sum(all_values)

        return aggregated

    def detect_regressions(
        self, current_metrics: dict[str, float], baseline_metrics: dict[str, float]
    ) -> list[RegressionResult]:
        """Detect performance regressions by comparing current vs baseline metrics."""
        results = []

        for metric_name in current_metrics:
            if metric_name not in baseline_metrics:
                continue

            current_value = current_metrics[metric_name]
            baseline_value = baseline_metrics[metric_name]

            if baseline_value == 0:
                continue  # Avoid division by zero

            change_percent = ((current_value - baseline_value) / baseline_value) * 100
            is_regression = abs(change_percent) > self.threshold_percent

            # Determine severity
            severity = "minor"
            if abs(change_percent) > 50:
                severity = "critical"
            elif abs(change_percent) > 30:
                severity = "major"

            results.append(
                RegressionResult(
                    metric_name=metric_name,
                    current_value=current_value,
                    baseline_value=baseline_value,
                    change_percent=change_percent,
                    is_regression=is_regression,
                    severity=severity,
                )
            )

        return results

    def generate_report(self, results: list[RegressionResult]) -> str:
        """Generate a human-readable regression report."""
        report = ["# Performance Regression Analysis Report", ""]
        report.append(f"**Analysis Date:** {datetime.now().isoformat()}")
        report.append(f"**Regression Threshold:** {self.threshold_percent}%")
        report.append("")

        # Summary
        regressions = [r for r in results if r.is_regression]
        critical_regressions = [r for r in regressions if r.severity == "critical"]
        major_regressions = [r for r in regressions if r.severity == "major"]

        report.append("## Summary")
        report.append(f"- **Total Metrics Analyzed:** {len(results)}")
        report.append(f"- **Regressions Detected:** {len(regressions)}")
        report.append(f"- **Critical Regressions:** {len(critical_regressions)}")
        report.append(f"- **Major Regressions:** {len(major_regressions)}")
        report.append("")

        if regressions:
            report.append("## Detected Regressions")
            report.append("")

            for result in sorted(
                regressions, key=lambda x: abs(x.change_percent), reverse=True
            ):
                status_emoji = (
                    "🔴"
                    if result.severity == "critical"
                    else "🟡"
                    if result.severity == "major"
                    else "🟠"
                )
                report.append(
                    f"{status_emoji} **{result.metric_name}** ({result.severity.upper()})"
                )
                report.append(f"  - Current: {result.current_value:.3f}")
                report.append(f"  - Baseline: {result.baseline_value:.3f}")
                report.append(f"  - Change: {result.change_percent:+.1f}%")
                report.append("")
        else:
            report.append("## ✅ No Performance Regressions Detected")
            report.append("")
            report.append("All metrics are within acceptable performance thresholds.")
            report.append("")

        # All metrics table
        report.append("## All Metrics")
        report.append("")
        report.append("| Metric | Current | Baseline | Change % | Status |")
        report.append("|--------|---------|----------|----------|--------|")

        for result in sorted(results, key=lambda x: x.metric_name):
            status = "🔴 REGRESSION" if result.is_regression else "✅ OK"
            report.append(
                f"| {result.metric_name} | {result.current_value:.3f} | "
                f"{result.baseline_value:.3f} | {result.change_percent:+.1f}% | {status} |"
            )

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Detect performance regressions in TTA tests"
    )
    parser.add_argument(
        "--test-results",
        type=Path,
        required=True,
        help="Directory containing test results",
    )
    parser.add_argument(
        "--baseline-file", type=Path, help="JSON file containing baseline metrics"
    )
    parser.add_argument(
        "--baseline-branch",
        type=str,
        default="main",
        help="Git branch to use as baseline (not implemented)",
    )
    parser.add_argument(
        "--threshold", type=float, default=20.0, help="Regression threshold percentage"
    )
    parser.add_argument("--output", type=Path, help="Output file for the report")

    args = parser.parse_args()

    if not args.test_results.exists():
        sys.exit(1)

    detector = PerformanceRegressionDetector(threshold_percent=args.threshold)

    # Load current metrics
    current_metrics_raw = detector.load_test_results(args.test_results)
    current_metrics = detector.calculate_aggregated_metrics(current_metrics_raw)

    # Load baseline metrics
    baseline_metrics = detector.load_baseline_metrics(args.baseline_file)

    # Detect regressions
    results = detector.detect_regressions(current_metrics, baseline_metrics)

    # Generate report
    report = detector.generate_report(results)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
    else:
        pass

    # Exit with error code if critical regressions found
    critical_regressions = [
        r for r in results if r.is_regression and r.severity == "critical"
    ]
    if critical_regressions:
        sys.exit(1)

    major_regressions = [
        r for r in results if r.is_regression and r.severity == "major"
    ]
    if major_regressions:
        pass
        # Don't exit with error for major regressions, just warn


if __name__ == "__main__":
    main()
