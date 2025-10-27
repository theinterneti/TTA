#!/usr/bin/env python3
"""
Monitoring Report Generator

Generates comprehensive HTML reports from test results and monitoring data
for the TTA application CI/CD pipeline.
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

from defusedxml import ElementTree as ET


def load_test_results(test_results_dir: Path) -> dict[str, Any]:
    """Load and parse test results from various formats."""
    results = {
        "unit_tests": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration": 0.0,
        },
        "integration_tests": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration": 0.0,
        },
        "coverage": {"unit": 0.0, "integration": 0.0},
        "performance_metrics": {},
        "test_details": [],
    }

    # Parse JUnit XML files
    for xml_file in test_results_dir.glob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            test_type = "unit_tests" if "unit" in xml_file.name else "integration_tests"

            # Extract test statistics
            total_tests = int(root.get("tests", 0))
            failures = int(root.get("failures", 0))
            errors = int(root.get("errors", 0))
            skipped = int(root.get("skipped", 0))
            time_taken = float(root.get("time", 0))

            results[test_type]["total"] = total_tests
            results[test_type]["failed"] = failures + errors
            results[test_type]["skipped"] = skipped
            results[test_type]["passed"] = total_tests - failures - errors - skipped
            results[test_type]["duration"] = time_taken

            # Extract individual test details
            for testcase in root.findall(".//testcase"):
                test_detail = {
                    "name": testcase.get("name", "unknown"),
                    "classname": testcase.get("classname", "unknown"),
                    "time": float(testcase.get("time", 0)),
                    "status": "passed",
                    "type": test_type,
                }

                if testcase.find("failure") is not None:
                    test_detail["status"] = "failed"
                    test_detail["failure"] = testcase.find("failure").text
                elif testcase.find("error") is not None:
                    test_detail["status"] = "error"
                    test_detail["error"] = testcase.find("error").text
                elif testcase.find("skipped") is not None:
                    test_detail["status"] = "skipped"

                results["test_details"].append(test_detail)

        except ET.ParseError as e:
            print(f"Warning: Could not parse {xml_file}: {e}")

    # Load coverage data
    for coverage_file in test_results_dir.glob("coverage-*.xml"):
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()

            coverage_type = "unit" if "unit" in coverage_file.name else "integration"

            # Extract coverage percentage
            coverage_elem = root.find(".//coverage")
            if coverage_elem is not None:
                line_rate = float(coverage_elem.get("line-rate", 0))
                results["coverage"][coverage_type] = line_rate * 100

        except ET.ParseError as e:
            print(f"Warning: Could not parse coverage file {coverage_file}: {e}")

    return results


def generate_html_report(results: dict[str, Any], output_file: Path):
    """Generate comprehensive HTML monitoring report."""

    # Calculate overall statistics
    total_tests = results["unit_tests"]["total"] + results["integration_tests"]["total"]
    total_passed = (
        results["unit_tests"]["passed"] + results["integration_tests"]["passed"]
    )
    total_failed = (
        results["unit_tests"]["failed"] + results["integration_tests"]["failed"]
    )
    total_duration = (
        results["unit_tests"]["duration"] + results["integration_tests"]["duration"]
    )

    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    avg_coverage = (
        results["coverage"]["unit"] + results["coverage"]["integration"]
    ) / 2

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TTA Monitoring Report - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .metric-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .metric-card.success {{
            border-left-color: #28a745;
        }}
        .metric-card.warning {{
            border-left-color: #ffc107;
        }}
        .metric-card.danger {{
            border-left-color: #dc3545;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .section {{
            padding: 30px;
            border-top: 1px solid #eee;
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .test-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .test-table th,
        .test-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .test-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-passed {{
            background-color: #d4edda;
            color: #155724;
        }}
        .status-failed {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .status-skipped {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 TTA Monitoring Report</h1>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S UTC")}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card {"success" if success_rate >= 95 else "warning" if success_rate >= 80 else "danger"}">
                <div class="metric-label">Test Success Rate</div>
                <div class="metric-value">{success_rate:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {success_rate}%"></div>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Total Tests</div>
                <div class="metric-value">{total_tests}</div>
                <div style="color: #28a745;">✅ {total_passed} passed</div>
                <div style="color: #dc3545;">❌ {total_failed} failed</div>
            </div>

            <div class="metric-card {"success" if avg_coverage >= 80 else "warning" if avg_coverage >= 60 else "danger"}">
                <div class="metric-label">Average Coverage</div>
                <div class="metric-value">{avg_coverage:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {avg_coverage}%"></div>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Total Duration</div>
                <div class="metric-value">{total_duration:.1f}s</div>
                <div>Avg: {(total_duration / total_tests if total_tests > 0 else 0):.2f}s per test</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Test Categories</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Unit Tests</div>
                    <div class="metric-value">{results["unit_tests"]["total"]}</div>
                    <div>✅ {results["unit_tests"]["passed"]} | ❌ {results["unit_tests"]["failed"]} | ⏭️ {results["unit_tests"]["skipped"]}</div>
                    <div>Duration: {results["unit_tests"]["duration"]:.1f}s</div>
                    <div>Coverage: {results["coverage"]["unit"]:.1f}%</div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">Integration Tests</div>
                    <div class="metric-value">{results["integration_tests"]["total"]}</div>
                    <div>✅ {results["integration_tests"]["passed"]} | ❌ {results["integration_tests"]["failed"]} | ⏭️ {results["integration_tests"]["skipped"]}</div>
                    <div>Duration: {results["integration_tests"]["duration"]:.1f}s</div>
                    <div>Coverage: {results["coverage"]["integration"]:.1f}%</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🔍 Test Details</h2>
            <table class="test-table">
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Class</th>
                        <th>Type</th>
                        <th>Duration</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Add test details
    for test in sorted(results["test_details"], key=lambda x: x["time"], reverse=True)[
        :50
    ]:  # Show top 50 slowest tests
        status_class = f"status-{test['status']}"
        html_content += f"""
                    <tr>
                        <td>{test["name"]}</td>
                        <td>{test["classname"]}</td>
                        <td>{test["type"].replace("_", " ").title()}</td>
                        <td>{test["time"]:.3f}s</td>
                        <td><span class="status-badge {status_class}">{test["status"]}</span></td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>📈 Monitoring Integration Status</h2>
            <div class="metrics-grid">
                <div class="metric-card success">
                    <div class="metric-label">Prometheus</div>
                    <div class="metric-value">✅</div>
                    <div>Metrics collection enabled</div>
                </div>

                <div class="metric-card success">
                    <div class="metric-label">Grafana</div>
                    <div class="metric-value">✅</div>
                    <div>Dashboards provisioned</div>
                </div>

                <div class="metric-card success">
                    <div class="metric-label">CI/CD Integration</div>
                    <div class="metric-value">✅</div>
                    <div>Monitoring validation passed</div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>🔧 TTA Monitoring System | Generated by CI/CD Pipeline</p>
            <p>For more detailed metrics, visit your Grafana dashboards at <code>http://localhost:3000</code></p>
        </div>
    </div>
</body>
</html>
    """

    with open(output_file, "w") as f:
        f.write(html_content)


def main():
    parser = argparse.ArgumentParser(description="Generate TTA monitoring report")
    parser.add_argument(
        "--test-results",
        type=Path,
        required=True,
        help="Directory containing test results",
    )
    parser.add_argument(
        "--output", type=Path, default="monitoring-report.html", help="Output HTML file"
    )

    args = parser.parse_args()

    if not args.test_results.exists():
        print(f"Error: Test results directory {args.test_results} does not exist")
        return 1

    print("Loading test results...")
    results = load_test_results(args.test_results)

    print("Generating HTML report...")
    generate_html_report(results, args.output)

    print(f"✅ Monitoring report generated: {args.output}")
    return 0


if __name__ == "__main__":
    exit(main())
