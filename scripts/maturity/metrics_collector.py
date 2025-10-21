"""
Metrics Collection Module

Programmatically collect quality metrics from various tools:
- pytest (coverage, test status)
- ruff (linting)
- pyright (type checking)
- bandit (security)
"""

import json
import logging
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CoverageMetrics:
    """Test coverage metrics from pytest."""

    percentage: float
    lines_covered: int
    lines_total: int
    missing_lines: list[int] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    error: str | None = None


@dataclass
class LintingMetrics:
    """Linting metrics from ruff."""

    total_violations: int
    by_severity: dict[str, int] = field(default_factory=dict)
    by_rule: dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    error: str | None = None


@dataclass
class TypeCheckingMetrics:
    """Type checking metrics from pyright."""

    errors: int
    warnings: int
    information: int
    timestamp: datetime = field(default_factory=datetime.now)
    error: str | None = None


@dataclass
class SecurityMetrics:
    """Security metrics from bandit."""

    total_issues: int
    by_severity: dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    error: str | None = None


@dataclass
class TestMetrics:
    """Test execution metrics from pytest."""

    passed: int
    failed: int
    skipped: int
    total: int
    timestamp: datetime = field(default_factory=datetime.now)
    error: str | None = None


@dataclass
class MetricsResult:
    """Combined metrics result for a component."""

    component_name: str
    coverage: CoverageMetrics
    linting: LintingMetrics
    type_checking: TypeCheckingMetrics
    security: SecurityMetrics
    tests: TestMetrics
    timestamp: datetime = field(default_factory=datetime.now)

    def meets_staging_criteria(self) -> bool:
        """Check if component meets dev→staging promotion criteria."""
        return (
            self.coverage.percentage >= 70.0
            and self.linting.total_violations == 0
            and self.type_checking.errors == 0
            and self.security.total_issues == 0
            and self.tests.failed == 0
        )

    def get_current_stage(self) -> str:
        """Determine current maturity stage based on criteria."""
        if self.meets_staging_criteria():
            return "Staging"
        return "Development"


def collect_coverage(component_path: str, test_path: str) -> CoverageMetrics:
    """
    Collect test coverage metrics using pytest.

    Args:
        component_path: Path to component file (e.g., "src/components/carbon_component.py")
        test_path: Path to test file (e.g., "tests/test_components.py")

    Returns:
        CoverageMetrics object with coverage data
    """
    cov_json_path = None
    try:
        # Create temporary directory and file for coverage JSON output
        temp_dir = tempfile.mkdtemp()
        cov_json_path = Path(temp_dir) / "coverage.json"

        # Run pytest with coverage
        cmd = [
            "uv",
            "run",
            "pytest",
            test_path,
            f"--cov={component_path}",
            f"--cov-report=json:{cov_json_path}",
            "-q",
        ]

        subprocess.run(  # noqa: S603
            cmd, capture_output=True, text=True, timeout=60, check=False
        )

        # Parse coverage JSON
        try:
            if not cov_json_path.exists():
                logger.error(f"Coverage JSON not created at {cov_json_path}")
                return CoverageMetrics(
                    percentage=0.0,
                    lines_covered=0,
                    lines_total=0,
                    error="Coverage JSON file not created",
                )

            with cov_json_path.open() as f:
                cov_data = json.load(f)

            # Extract coverage percentage
            totals = cov_data.get("totals", {})
            percent_covered = totals.get("percent_covered", 0.0)
            num_statements = totals.get("num_statements", 0)
            covered_lines = totals.get("covered_lines", 0)

            # Get missing lines for the component
            files = cov_data.get("files", {})
            missing_lines = []
            for file_path, file_data in files.items():
                if component_path in file_path:
                    missing_lines = file_data.get("missing_lines", [])
                    break

            return CoverageMetrics(
                percentage=round(percent_covered, 2),
                lines_covered=covered_lines,
                lines_total=num_statements,
                missing_lines=missing_lines,
            )

        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Failed to parse coverage JSON: {e}")
            return CoverageMetrics(
                percentage=0.0,
                lines_covered=0,
                lines_total=0,
                error=f"Failed to parse coverage data: {e}",
            )
        finally:
            # Clean up temp file and directory
            if cov_json_path and cov_json_path.exists():
                cov_json_path.unlink()
            if temp_dir and Path(temp_dir).exists():
                Path(temp_dir).rmdir()

    except subprocess.TimeoutExpired:
        logger.error("Coverage collection timed out")
        return CoverageMetrics(
            percentage=0.0,
            lines_covered=0,
            lines_total=0,
            error="Coverage collection timed out",
        )
    except Exception as e:
        logger.error(f"Coverage collection failed: {e}")
        return CoverageMetrics(
            percentage=0.0,
            lines_covered=0,
            lines_total=0,
            error=str(e),
        )


def collect_linting(component_path: str) -> LintingMetrics:
    """
    Collect linting metrics using ruff.

    Args:
        component_path: Path to component file

    Returns:
        LintingMetrics object with linting data
    """
    try:
        cmd = ["uvx", "ruff", "check", component_path, "--output-format=json"]

        result = subprocess.run(  # noqa: S603
            cmd, capture_output=True, text=True, timeout=30, check=False
        )

        # Parse ruff JSON output
        try:
            violations = json.loads(result.stdout) if result.stdout else []

            # Count violations by rule
            by_rule: dict[str, int] = {}
            for violation in violations:
                rule_code = violation.get("code", "UNKNOWN")
                by_rule[rule_code] = by_rule.get(rule_code, 0) + 1

            return LintingMetrics(
                total_violations=len(violations),
                by_rule=by_rule,
                by_severity={},  # Ruff doesn't provide severity levels
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ruff JSON: {e}")
            return LintingMetrics(
                total_violations=0, error=f"Failed to parse ruff output: {e}"
            )

    except subprocess.TimeoutExpired:
        logger.error("Linting collection timed out")
        return LintingMetrics(total_violations=0, error="Linting collection timed out")
    except Exception as e:
        logger.error(f"Linting collection failed: {e}")
        return LintingMetrics(total_violations=0, error=str(e))


def collect_type_checking(component_path: str) -> TypeCheckingMetrics:
    """
    Collect type checking metrics using pyright.

    Args:
        component_path: Path to component file

    Returns:
        TypeCheckingMetrics object with type checking data
    """
    try:
        cmd = ["uvx", "pyright", component_path, "--outputjson"]

        result = subprocess.run(  # noqa: S603
            cmd, capture_output=True, text=True, timeout=60, check=False
        )

        # Parse pyright JSON output
        try:
            data = json.loads(result.stdout) if result.stdout else {}

            summary = data.get("summary", {})
            errors = summary.get("errorCount", 0)
            warnings = summary.get("warningCount", 0)
            information = summary.get("informationCount", 0)

            return TypeCheckingMetrics(
                errors=errors, warnings=warnings, information=information
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse pyright JSON: {e}")
            return TypeCheckingMetrics(
                errors=0,
                warnings=0,
                information=0,
                error=f"Failed to parse pyright output: {e}",
            )

    except subprocess.TimeoutExpired:
        logger.error("Type checking collection timed out")
        return TypeCheckingMetrics(
            errors=0,
            warnings=0,
            information=0,
            error="Type checking collection timed out",
        )
    except Exception as e:
        logger.error(f"Type checking collection failed: {e}")
        return TypeCheckingMetrics(errors=0, warnings=0, information=0, error=str(e))


def collect_security(component_path: str) -> SecurityMetrics:
    """
    Collect security metrics using bandit.

    Args:
        component_path: Path to component file

    Returns:
        SecurityMetrics object with security data
    """
    try:
        cmd = ["uvx", "bandit", "-r", component_path, "-f", "json"]

        result = subprocess.run(  # noqa: S603
            cmd, capture_output=True, text=True, timeout=30, check=False
        )

        # Parse bandit JSON output
        try:
            data = json.loads(result.stdout) if result.stdout else {}

            results = data.get("results", [])
            by_severity: dict[str, int] = {}

            for issue in results:
                severity = issue.get("issue_severity", "UNKNOWN")
                by_severity[severity] = by_severity.get(severity, 0) + 1

            return SecurityMetrics(total_issues=len(results), by_severity=by_severity)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse bandit JSON: {e}")
            return SecurityMetrics(
                total_issues=0, error=f"Failed to parse bandit output: {e}"
            )

    except subprocess.TimeoutExpired:
        logger.error("Security scan timed out")
        return SecurityMetrics(total_issues=0, error="Security scan timed out")
    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        return SecurityMetrics(total_issues=0, error=str(e))


def collect_test_status(test_path: str) -> TestMetrics:
    """
    Collect test execution metrics using pytest.

    Args:
        test_path: Path to test file

    Returns:
        TestMetrics object with test execution data
    """
    try:
        cmd = ["uv", "run", "pytest", test_path, "-v", "--tb=no"]

        result = subprocess.run(  # noqa: S603
            cmd, capture_output=True, text=True, timeout=60, check=False
        )

        # Parse pytest output for test counts
        # Look for lines like "3 passed, 2 failed, 1 skipped in 5.23s"
        output = result.stdout
        passed = failed = skipped = 0

        if "passed" in output:
            for line in output.split("\n"):
                if "passed" in line or "failed" in line or "skipped" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            passed = int(parts[i - 1])
                        elif part == "failed" and i > 0:
                            failed = int(parts[i - 1])
                        elif part == "skipped" and i > 0:
                            skipped = int(parts[i - 1])

        total = passed + failed + skipped

        return TestMetrics(passed=passed, failed=failed, skipped=skipped, total=total)

    except subprocess.TimeoutExpired:
        logger.error("Test execution timed out")
        return TestMetrics(
            passed=0, failed=0, skipped=0, total=0, error="Test execution timed out"
        )
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return TestMetrics(passed=0, failed=0, skipped=0, total=0, error=str(e))


def collect_all_metrics(
    component_name: str, component_path: str, test_path: str
) -> MetricsResult:
    """
    Collect all quality metrics for a component.

    Args:
        component_name: Name of the component (e.g., "carbon")
        component_path: Path to component file
        test_path: Path to test file

    Returns:
        MetricsResult object with all metrics
    """
    logger.info(f"Collecting metrics for {component_name}...")

    coverage = collect_coverage(component_path, test_path)
    linting = collect_linting(component_path)
    type_checking = collect_type_checking(component_path)
    security = collect_security(component_path)
    tests = collect_test_status(test_path)

    return MetricsResult(
        component_name=component_name,
        coverage=coverage,
        linting=linting,
        type_checking=type_checking,
        security=security,
        tests=tests,
    )


def _derive_module_path(source_path: Path) -> str:
    """
    Convert file path to Python module path.

    Examples:
        src/components/carbon_component.py -> src.components.carbon_component
        src/components/model_management/model_management_component.py ->
            src.components.model_management.model_management_component
    """
    # Remove .py extension
    path_str = str(source_path.with_suffix(""))

    # Replace path separators with dots
    return path_str.replace("/", ".")


def collect_metrics_from_metadata(component_metadata) -> MetricsResult:  # noqa: ANN001
    """
    Collect metrics using component metadata from registry.

    Args:
        component_metadata: ComponentMetadata object from registry

    Returns:
        MetricsResult with collected metrics
    """
    # Derive module path from source file
    component_path = _derive_module_path(component_metadata.source_path)

    # Get test path
    # For shared test files like tests/test_components.py, we need to specify the test function
    # For now, use the file path and let the metrics collector handle it
    test_path = (
        str(component_metadata.test_path) if component_metadata.test_path else ""
    )

    # Collect metrics
    return collect_all_metrics(
        component_name=component_metadata.name,
        component_path=component_path,
        test_path=test_path,
    )
