"""

# Logseq: [[TTA.dev/Tests/Comprehensive_battery/Utils/Report_generator]]
Test Report Generator

Generates comprehensive reports from test execution results including:
- Executive summary with pass/fail statistics
- Detailed test results by category
- Performance analysis and metrics
- Issue identification and recommendations
- Visual charts and graphs (when possible)
- Export in multiple formats (JSON, CSV, PDF)
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..comprehensive_test_battery import TestCategory, TestResult

logger = logging.getLogger(__name__)


class TestReportGenerator:
    """
    Generates comprehensive test reports from execution results.

    Provides detailed analysis, recommendations, and multiple export
    formats for comprehensive test battery results.
    """

    def __init__(
        self, results_directory: str = "./testing/results/comprehensive_battery"
    ):
        self.results_directory = Path(results_directory)
        self.results_directory.mkdir(parents=True, exist_ok=True)

    async def generate_comprehensive_report(
        self,
        results: list[TestResult],
        start_time: datetime,
        end_time: datetime,
        config: Any,
        metrics_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate comprehensive test report."""
        try:
            # Generate timestamp for report files
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

            # Create report data structure
            report_data = await self._create_report_data(
                results, start_time, end_time, config, metrics_data
            )

            # Generate different report formats
            report_files = {}

            # JSON report
            json_path = await self._generate_json_report(report_data, timestamp)
            report_files["json"] = json_path

            # CSV report
            csv_path = await self._generate_csv_report(results, timestamp)
            report_files["csv"] = csv_path

            # HTML report
            html_path = await self._generate_html_report(report_data, timestamp)
            report_files["html"] = html_path

            # Executive summary
            summary_path = await self._generate_executive_summary(
                report_data, timestamp
            )
            report_files["summary"] = summary_path

            logger.info(f"Comprehensive report generated: {len(report_files)} formats")

            return {
                "report_generated": True,
                "report_files": report_files,
                "report_path": str(self.results_directory),
                "summary": report_data["executive_summary"],
                "recommendations": report_data["recommendations"],
            }

        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {e}")
            return {"report_generated": False, "error": str(e)}

    async def _create_report_data(
        self,
        results: list[TestResult],
        start_time: datetime,
        end_time: datetime,
        config: Any,
        metrics_data: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Create comprehensive report data structure."""
        # Calculate summary statistics
        total_tests = len(results)
        passed_tests = len([r for r in results if r.passed])
        failed_tests = total_tests - passed_tests
        total_duration = (end_time - start_time).total_seconds()

        # Group results by category
        results_by_category = self._group_results_by_category(results)

        # Analyze performance metrics
        performance_analysis = self._analyze_performance_metrics(results, metrics_data)

        # Identify issues and generate recommendations
        issues = self._identify_issues(results)
        recommendations = self._generate_recommendations(results, issues)

        return {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "test_execution_start": start_time.isoformat(),
                "test_execution_end": end_time.isoformat(),
                "total_duration_seconds": total_duration,
                "report_version": "1.0",
            },
            "executive_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (
                    (passed_tests / total_tests * 100) if total_tests > 0 else 0
                ),
                "total_duration_minutes": total_duration / 60,
                "overall_status": "PASS" if failed_tests == 0 else "FAIL",
            },
            "category_results": results_by_category,
            "performance_analysis": performance_analysis,
            "issues_identified": issues,
            "recommendations": recommendations,
            "detailed_results": [self._serialize_test_result(r) for r in results],
            "configuration": self._serialize_config(config),
            "metrics_data": metrics_data,
        }

    def _group_results_by_category(
        self, results: list[TestResult]
    ) -> dict[str, dict[str, Any]]:
        """Group test results by category."""
        categories = {}

        for category in TestCategory:
            category_results = [r for r in results if r.category == category]

            if category_results:
                passed = len([r for r in category_results if r.passed])
                failed = len(category_results) - passed
                avg_duration = sum(r.duration_seconds for r in category_results) / len(
                    category_results
                )

                categories[category.value] = {
                    "total_tests": len(category_results),
                    "passed_tests": passed,
                    "failed_tests": failed,
                    "success_rate": (passed / len(category_results) * 100),
                    "average_duration_seconds": avg_duration,
                    "status": "PASS" if failed == 0 else "FAIL",
                }

        return categories

    def _analyze_performance_metrics(
        self, results: list[TestResult], metrics_data: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Analyze performance metrics from test results."""
        analysis = {
            "response_times": [],
            "throughput_metrics": [],
            "resource_usage": {},
            "performance_issues": [],
        }

        # Extract performance metrics from test results
        for result in results:
            if result.metrics:
                # Response time analysis
                if "response_time" in result.metrics:
                    analysis["response_times"].append(
                        {
                            "test_name": result.test_name,
                            "response_time": result.metrics["response_time"],
                            "category": result.category.value,
                        }
                    )

                # Throughput analysis
                if "throughput_rps" in result.metrics:
                    analysis["throughput_metrics"].append(
                        {
                            "test_name": result.test_name,
                            "throughput_rps": result.metrics["throughput_rps"],
                            "category": result.category.value,
                        }
                    )

        # Include external metrics data if available
        if metrics_data:
            analysis["resource_usage"] = metrics_data.get("system_resource_summary", {})

            # Identify performance issues
            cpu_usage = metrics_data.get("system_resource_summary", {}).get(
                "cpu_usage", {}
            )
            memory_usage = metrics_data.get("system_resource_summary", {}).get(
                "memory_usage", {}
            )

            if cpu_usage.get("max", 0) > 80:
                analysis["performance_issues"].append("High CPU usage detected (>80%)")

            if memory_usage.get("max", 0) > 80:
                analysis["performance_issues"].append(
                    "High memory usage detected (>80%)"
                )

        return analysis

    def _identify_issues(self, results: list[TestResult]) -> list[dict[str, Any]]:
        """Identify issues from test results."""
        issues = []

        # Failed tests
        failed_results = [r for r in results if not r.passed]
        for result in failed_results:
            issues.append(
                {
                    "type": "test_failure",
                    "severity": (
                        "high"
                        if result.category
                        in [TestCategory.ADVERSARIAL, TestCategory.DATA_PIPELINE]
                        else "medium"
                    ),
                    "test_name": result.test_name,
                    "category": result.category.value,
                    "error_message": result.error_message,
                    "description": f"Test {result.test_name} failed: {result.error_message}",
                }
            )

        # Performance issues
        slow_tests = [r for r in results if r.duration_seconds > 60]  # > 1 minute
        for result in slow_tests:
            issues.append(
                {
                    "type": "performance_issue",
                    "severity": "medium",
                    "test_name": result.test_name,
                    "category": result.category.value,
                    "duration": result.duration_seconds,
                    "description": f"Test {result.test_name} took {result.duration_seconds:.1f} seconds (slow)",
                }
            )

        # Category-specific issues
        category_success_rates = {}
        for category in TestCategory:
            category_results = [r for r in results if r.category == category]
            if category_results:
                passed = len([r for r in category_results if r.passed])
                success_rate = (passed / len(category_results)) * 100
                category_success_rates[category.value] = success_rate

                if success_rate < 90:  # < 90% success rate
                    issues.append(
                        {
                            "type": "category_failure",
                            "severity": "high",
                            "category": category.value,
                            "success_rate": success_rate,
                            "description": f"Category {category.value} has low success rate: {success_rate:.1f}%",
                        }
                    )

        return issues

    def _generate_recommendations(
        self, results: list[TestResult], issues: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Generate recommendations based on test results and issues."""
        recommendations = []

        # Recommendations based on issues
        high_severity_issues = [i for i in issues if i["severity"] == "high"]
        if high_severity_issues:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "critical_fixes",
                    "title": "Address Critical Test Failures",
                    "description": f"Fix {len(high_severity_issues)} high-severity issues before production deployment",
                    "action_items": [
                        f"Investigate and fix: {issue['description']}"
                        for issue in high_severity_issues[:5]  # Top 5 issues
                    ],
                }
            )

        # Performance recommendations
        performance_issues = [i for i in issues if i["type"] == "performance_issue"]
        if performance_issues:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "performance_optimization",
                    "title": "Optimize System Performance",
                    "description": f"Address {len(performance_issues)} performance issues",
                    "action_items": [
                        "Review and optimize slow-running tests",
                        "Consider increasing system resources",
                        "Implement performance monitoring in production",
                    ],
                }
            )

        # Security recommendations (from adversarial tests)
        adversarial_failures = [
            r
            for r in results
            if r.category == TestCategory.ADVERSARIAL and not r.passed
        ]
        if adversarial_failures:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "security",
                    "title": "Address Security Vulnerabilities",
                    "description": f"Fix {len(adversarial_failures)} security-related test failures",
                    "action_items": [
                        "Conduct security code review",
                        "Implement additional input validation",
                        "Review authentication and authorization mechanisms",
                    ],
                }
            )

        # Data pipeline recommendations
        pipeline_failures = [
            r
            for r in results
            if r.category == TestCategory.DATA_PIPELINE and not r.passed
        ]
        if pipeline_failures:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "data_integrity",
                    "title": "Fix Data Pipeline Issues",
                    "description": f"Address {len(pipeline_failures)} data pipeline failures",
                    "action_items": [
                        "Review data transformation processes",
                        "Verify database consistency mechanisms",
                        "Implement data validation checks",
                    ],
                }
            )

        # General recommendations
        total_success_rate = (
            (len([r for r in results if r.passed]) / len(results)) * 100
            if results
            else 0
        )
        if total_success_rate < 95:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "quality_improvement",
                    "title": "Improve Overall Test Success Rate",
                    "description": f"Current success rate is {total_success_rate:.1f}%, target is 95%+",
                    "action_items": [
                        "Review and fix failing tests",
                        "Improve error handling and recovery",
                        "Enhance system monitoring and alerting",
                    ],
                }
            )

        return recommendations

    def _serialize_test_result(self, result: TestResult) -> dict[str, Any]:
        """Serialize test result for JSON export."""
        return {
            "test_name": result.test_name,
            "category": result.category.value,
            "status": result.status.value,
            "passed": result.passed,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat() if result.end_time else None,
            "duration_seconds": result.duration_seconds,
            "error_message": result.error_message,
            "metrics": result.metrics,
            "details": result.details,
        }

    def _serialize_config(self, config: Any) -> dict[str, Any]:
        """Serialize configuration for JSON export."""
        try:
            # Extract relevant configuration settings
            return {
                "max_concurrent_tests": getattr(config, "max_concurrent_tests", None),
                "test_timeout_seconds": getattr(config, "test_timeout_seconds", None),
                "max_concurrent_users": getattr(config, "max_concurrent_users", None),
                "load_test_duration_minutes": getattr(
                    config, "load_test_duration_minutes", None
                ),
                "neo4j_uri": getattr(config, "neo4j_uri", None),
                "redis_url": getattr(config, "redis_url", None),
            }
        except Exception:
            return {"error": "Could not serialize configuration"}

    async def _generate_json_report(
        self, report_data: dict[str, Any], timestamp: str
    ) -> str:
        """Generate JSON format report."""
        json_path = self.results_directory / f"comprehensive_report_{timestamp}.json"

        with open(json_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(json_path)

    async def _generate_csv_report(
        self, results: list[TestResult], timestamp: str
    ) -> str:
        """Generate CSV format report."""
        csv_path = self.results_directory / f"test_results_{timestamp}.csv"

        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(
                [
                    "Test Name",
                    "Category",
                    "Status",
                    "Passed",
                    "Duration (s)",
                    "Error Message",
                    "Start Time",
                    "End Time",
                ]
            )

            # Write test results
            for result in results:
                writer.writerow(
                    [
                        result.test_name,
                        result.category.value,
                        result.status.value,
                        result.passed,
                        result.duration_seconds,
                        result.error_message or "",
                        result.start_time.isoformat(),
                        result.end_time.isoformat() if result.end_time else "",
                    ]
                )

        return str(csv_path)

    async def _generate_html_report(
        self, report_data: dict[str, Any], timestamp: str
    ) -> str:
        """Generate HTML format report."""
        html_path = self.results_directory / f"comprehensive_report_{timestamp}.html"

        # Simple HTML template
        html_content = self._create_html_template(report_data)

        with open(html_path, "w") as f:
            f.write(html_content)

        return str(html_path)

    async def _generate_executive_summary(
        self, report_data: dict[str, Any], timestamp: str
    ) -> str:
        """Generate executive summary report."""
        summary_path = self.results_directory / f"executive_summary_{timestamp}.txt"

        summary_content = self._create_executive_summary_content(report_data)

        with open(summary_path, "w") as f:
            f.write(summary_content)

        return str(summary_path)

    def _create_html_template(self, report_data: dict[str, Any]) -> str:
        """Create HTML template for report."""
        # Simple HTML template - could be enhanced with CSS and JavaScript
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>TTA Comprehensive Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>TTA Comprehensive Test Report</h1>

    <div class="summary">
        <h2>Executive Summary</h2>
        <p><strong>Total Tests:</strong> {
            report_data["executive_summary"]["total_tests"]
        }</p>
        <p><strong>Passed:</strong> <span class="pass">{
            report_data["executive_summary"]["passed_tests"]
        }</span></p>
        <p><strong>Failed:</strong> <span class="fail">{
            report_data["executive_summary"]["failed_tests"]
        }</span></p>
        <p><strong>Success Rate:</strong> {
            report_data["executive_summary"]["success_rate"]:.1f}%</p>
        <p><strong>Duration:</strong> {
            report_data["executive_summary"]["total_duration_minutes"]:.1f} minutes</p>
    </div>

    <h2>Category Results</h2>
    <table>
        <tr><th>Category</th><th>Total</th><th>Passed</th><th>Failed</th><th>Success Rate</th></tr>
        {
            "".join(
                [
                    f"<tr><td>{cat}</td><td>{data['total_tests']}</td><td>{data['passed_tests']}</td><td>{data['failed_tests']}</td><td>{data['success_rate']:.1f}%</td></tr>"
                    for cat, data in report_data["category_results"].items()
                ]
            )
        }
    </table>

    <h2>Recommendations</h2>
    <ul>
        {
            "".join(
                [
                    f"<li><strong>{rec['title']}:</strong> {rec['description']}</li>"
                    for rec in report_data["recommendations"]
                ]
            )
        }
    </ul>

    <p><em>Generated at: {report_data["report_metadata"]["generated_at"]}</em></p>
</body>
</html>
        """

    def _create_executive_summary_content(self, report_data: dict[str, Any]) -> str:
        """Create executive summary content."""
        summary = report_data["executive_summary"]

        content = f"""
TTA COMPREHENSIVE TEST BATTERY - EXECUTIVE SUMMARY
================================================

Generated: {report_data["report_metadata"]["generated_at"]}
Test Period: {report_data["report_metadata"]["test_execution_start"]} to {report_data["report_metadata"]["test_execution_end"]}

OVERALL RESULTS
--------------
Total Tests: {summary["total_tests"]}
Passed: {summary["passed_tests"]}
Failed: {summary["failed_tests"]}
Success Rate: {summary["success_rate"]:.1f}%
Total Duration: {summary["total_duration_minutes"]:.1f} minutes
Overall Status: {summary["overall_status"]}

CATEGORY BREAKDOWN
-----------------
"""

        for category, data in report_data["category_results"].items():
            content += f"{category.upper()}: {data['passed_tests']}/{data['total_tests']} passed ({data['success_rate']:.1f}%)\n"

        content += """

KEY RECOMMENDATIONS
------------------
"""

        for i, rec in enumerate(report_data["recommendations"][:5], 1):
            content += f"{i}. {rec['title']}: {rec['description']}\n"

        content += f"""

ISSUES IDENTIFIED
----------------
Total Issues: {len(report_data["issues_identified"])}
High Severity: {len([i for i in report_data["issues_identified"] if i["severity"] == "high"])}
Medium Severity: {len([i for i in report_data["issues_identified"] if i["severity"] == "medium"])}

For detailed results, see the comprehensive JSON and HTML reports.
        """

        return content
