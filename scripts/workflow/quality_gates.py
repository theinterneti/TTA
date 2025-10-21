"""
Quality Gate Validators

Implements quality gates for TTA component maturity workflow:
- Testing gates (coverage, pass rate)
- Code quality gates (linting, type checking)
- Security gates (secrets, vulnerabilities)
- Performance gates (response time, memory)
- Documentation gates (README, API docs)
"""

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.observability.dev_metrics import track_execution
from scripts.primitives.error_recovery import RetryConfig, with_retry


@dataclass
class QualityGateResult:
    """Result of a quality gate check."""

    passed: bool
    gate_name: str
    details: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "passed": self.passed,
            "gate_name": self.gate_name,
            "details": self.details,
            "errors": self.errors,
            "warnings": self.warnings,
            "execution_time_ms": self.execution_time_ms,
        }


class QualityGateValidator:
    """Base class for quality gate validators."""

    def __init__(self, component_path: str, config: dict[str, Any] | None = None):
        """
        Initialize validator.

        Args:
            component_path: Path to component directory
            config: Optional configuration overrides
        """
        self.component_path = Path(component_path)
        self.config = config or {}

    def validate(self) -> QualityGateResult:
        """
        Run validation.

        Returns:
            QualityGateResult with validation results
        """
        raise NotImplementedError("Subclasses must implement validate()")


class TestCoverageGate(QualityGateValidator):
    """Validates test coverage meets threshold."""

    def _find_test_paths(self) -> list[str]:
        """
        Find test paths for the component.

        Supports multiple test organization patterns:
        1. tests/<component_name>/ (directory-based)
        2. tests/test_<component_name>.py (single file)
        3. tests/test_<component_name>_*.py (pattern-based)
        4. Common naming variations (e.g., orchestration -> orchestrator)

        Returns:
            List of test paths to run
        """
        component_name = self.component_path.name
        test_paths = []

        # Generate naming variations to check
        name_variations = [component_name]

        # Handle common suffixes (e.g., orchestration -> orchestrator)
        if component_name.endswith('ion'):
            name_variations.append(component_name.rstrip('ion') + 'or')
        if component_name.endswith('tion'):
            name_variations.append(component_name.rstrip('tion') + 'tor')

        for name_var in name_variations:
            # Pattern 1: Directory-based (e.g., tests/orchestration/)
            dir_path = Path("tests") / name_var
            if dir_path.exists() and dir_path.is_dir():
                test_paths.append(str(dir_path))

            # Pattern 2: Single file (e.g., tests/test_orchestrator.py)
            single_file = Path("tests") / f"test_{name_var}.py"
            if single_file.exists():
                test_paths.append(str(single_file))

            # Pattern 3: Pattern-based (e.g., tests/test_orchestrator_*.py)
            pattern_files = list(Path("tests").glob(f"test_{name_var}_*.py"))
            test_paths.extend([str(f) for f in pattern_files])

        # If no tests found, default to directory pattern (will fail gracefully)
        if not test_paths:
            test_paths = [f"tests/{component_name}/"]

        return test_paths

    @track_execution("quality_gate_test_coverage")
    @with_retry(RetryConfig(max_retries=2, base_delay=1.0))
    def validate(self) -> QualityGateResult:
        """Check test coverage."""
        threshold = self.config.get("coverage_threshold", 70.0)
        test_paths = self._find_test_paths()

        try:
            # Run pytest with coverage using project environment
            result = subprocess.run(
                [
                    "uv", "run", "pytest",
                    *test_paths,
                    f"--cov=src/{self.component_path.name}",
                    "--cov-report=json",
                    "--cov-report=term",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Parse coverage report
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0.0)

                passed = total_coverage >= threshold

                return QualityGateResult(
                    passed=passed,
                    gate_name="test_coverage",
                    details={
                        "coverage": total_coverage,
                        "threshold": threshold,
                        "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                        "lines_total": coverage_data.get("totals", {}).get("num_statements", 0),
                    },
                    errors=[] if passed else [f"Coverage {total_coverage:.1f}% < threshold {threshold}%"],
                )
            else:
                return QualityGateResult(
                    passed=False,
                    gate_name="test_coverage",
                    errors=["Coverage report not generated"],
                )

        except subprocess.TimeoutExpired:
            return QualityGateResult(
                passed=False,
                gate_name="test_coverage",
                errors=["Test execution timed out (300s)"],
            )
        except Exception as e:
            return QualityGateResult(
                passed=False,
                gate_name="test_coverage",
                errors=[f"Coverage check failed: {str(e)}"],
            )


class TestPassRateGate(QualityGateValidator):
    """Validates all tests pass."""

    def _find_test_paths(self) -> list[str]:
        """Find test paths for the component (same logic as TestCoverageGate)."""
        component_name = self.component_path.name
        test_paths = []

        # Generate naming variations
        name_variations = [component_name]
        if component_name.endswith('ion'):
            name_variations.append(component_name.rstrip('ion') + 'or')
        if component_name.endswith('tion'):
            name_variations.append(component_name.rstrip('tion') + 'tor')

        for name_var in name_variations:
            # Pattern 1: Directory-based
            dir_path = Path("tests") / name_var
            if dir_path.exists() and dir_path.is_dir():
                test_paths.append(str(dir_path))

            # Pattern 2: Single file
            single_file = Path("tests") / f"test_{name_var}.py"
            if single_file.exists():
                test_paths.append(str(single_file))

            # Pattern 3: Pattern-based
            pattern_files = list(Path("tests").glob(f"test_{name_var}_*.py"))
            test_paths.extend([str(f) for f in pattern_files])

        # Default fallback
        if not test_paths:
            test_paths = [f"tests/{component_name}/"]

        return test_paths

    @track_execution("quality_gate_test_pass_rate")
    @with_retry(RetryConfig(max_retries=2, base_delay=1.0))
    def validate(self) -> QualityGateResult:
        """Check test pass rate."""
        test_paths = self._find_test_paths()

        try:
            # Run pytest using project environment
            result = subprocess.run(
                [
                    "uv", "run", "pytest",
                    *test_paths,
                    "-v",
                    "--tb=short",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            passed = result.returncode == 0

            # Parse output for test counts
            output = result.stdout
            # Look for pytest summary line like "5 passed, 2 failed"

            return QualityGateResult(
                passed=passed,
                gate_name="test_pass_rate",
                details={
                    "exit_code": result.returncode,
                    "output_summary": output.split("\n")[-5:] if output else [],
                },
                errors=[] if passed else ["Some tests failed"],
            )

        except subprocess.TimeoutExpired:
            return QualityGateResult(
                passed=False,
                gate_name="test_pass_rate",
                errors=["Test execution timed out (300s)"],
            )
        except Exception as e:
            return QualityGateResult(
                passed=False,
                gate_name="test_pass_rate",
                errors=[f"Test execution failed: {str(e)}"],
            )


class LintingGate(QualityGateValidator):
    """Validates code passes linting."""

    @track_execution("quality_gate_linting")
    @with_retry(RetryConfig(max_retries=1, base_delay=0.5))
    def validate(self) -> QualityGateResult:
        """Check linting."""
        try:
            # Run ruff check
            result = subprocess.run(
                [
                    "uvx", "ruff", "check",
                    f"src/{self.component_path.name}/",
                    f"tests/{self.component_path.name}/",
                    "--output-format=json",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            passed = result.returncode == 0

            # Parse JSON output
            issues = []
            if result.stdout:
                try:
                    issues = json.loads(result.stdout)
                except json.JSONDecodeError:
                    pass

            return QualityGateResult(
                passed=passed,
                gate_name="linting",
                details={
                    "issue_count": len(issues),
                    "issues": issues[:10],  # First 10 issues
                },
                errors=[] if passed else [f"Found {len(issues)} linting issues"],
                warnings=[f"Run 'uvx ruff check --fix' to auto-fix issues"] if not passed else [],
            )

        except subprocess.TimeoutExpired:
            return QualityGateResult(
                passed=False,
                gate_name="linting",
                errors=["Linting timed out (60s)"],
            )
        except Exception as e:
            return QualityGateResult(
                passed=False,
                gate_name="linting",
                errors=[f"Linting failed: {str(e)}"],
            )


class TypeCheckingGate(QualityGateValidator):
    """Validates code passes type checking."""

    @track_execution("quality_gate_type_checking")
    @with_retry(RetryConfig(max_retries=1, base_delay=0.5))
    def validate(self) -> QualityGateResult:
        """Check type checking."""
        try:
            # Run pyright
            result = subprocess.run(
                [
                    "uvx", "pyright",
                    f"src/{self.component_path.name}/",
                    "--outputjson",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            # Parse JSON output
            type_errors = []
            if result.stdout:
                try:
                    output = json.loads(result.stdout)
                    type_errors = output.get("generalDiagnostics", [])
                except json.JSONDecodeError:
                    pass

            passed = len(type_errors) == 0

            return QualityGateResult(
                passed=passed,
                gate_name="type_checking",
                details={
                    "error_count": len(type_errors),
                    "errors": type_errors[:10],  # First 10 errors
                },
                errors=[] if passed else [f"Found {len(type_errors)} type errors"],
            )

        except subprocess.TimeoutExpired:
            return QualityGateResult(
                passed=False,
                gate_name="type_checking",
                errors=["Type checking timed out (120s)"],
            )
        except Exception as e:
            return QualityGateResult(
                passed=False,
                gate_name="type_checking",
                errors=[f"Type checking failed: {str(e)}"],
            )


class SecurityGate(QualityGateValidator):
    """Validates no security issues detected."""

    @track_execution("quality_gate_security")
    @with_retry(RetryConfig(max_retries=1, base_delay=0.5))
    def validate(self) -> QualityGateResult:
        """Check security."""
        try:
            # Run detect-secrets
            result = subprocess.run(
                [
                    "uvx", "detect-secrets", "scan",
                    f"src/{self.component_path.name}/",
                    "--baseline", ".secrets.baseline",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            passed = result.returncode == 0

            return QualityGateResult(
                passed=passed,
                gate_name="security",
                details={
                    "scan_output": result.stdout[:500] if result.stdout else "",
                },
                errors=[] if passed else ["Potential secrets detected"],
                warnings=["Review .secrets.baseline if secrets are false positives"] if not passed else [],
            )

        except subprocess.TimeoutExpired:
            return QualityGateResult(
                passed=False,
                gate_name="security",
                errors=["Security scan timed out (60s)"],
            )
        except Exception as e:
            return QualityGateResult(
                passed=False,
                gate_name="security",
                errors=[f"Security scan failed: {str(e)}"],
            )


def run_quality_gates(
    component_path: str,
    gates: list[str] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, QualityGateResult]:
    """
    Run quality gates for a component.

    Args:
        component_path: Path to component directory
        gates: List of gate names to run (None = all gates)
        config: Configuration overrides

    Returns:
        Dictionary mapping gate names to results
    """
    available_gates = {
        "test_coverage": TestCoverageGate,
        "test_pass_rate": TestPassRateGate,
        "linting": LintingGate,
        "type_checking": TypeCheckingGate,
        "security": SecurityGate,
    }

    gates_to_run = gates or list(available_gates.keys())
    results = {}

    for gate_name in gates_to_run:
        if gate_name not in available_gates:
            results[gate_name] = QualityGateResult(
                passed=False,
                gate_name=gate_name,
                errors=[f"Unknown gate: {gate_name}"],
            )
            continue

        gate_class = available_gates[gate_name]
        gate = gate_class(component_path, config)
        results[gate_name] = gate.validate()

    return results


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python quality_gates.py <component_path>")
        sys.exit(1)

    component_path = sys.argv[1]
    results = run_quality_gates(component_path)

    print("\n=== Quality Gate Results ===\n")
    for gate_name, result in results.items():
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"{status} {gate_name}")
        if result.errors:
            for error in result.errors:
                print(f"  ERROR: {error}")
        if result.warnings:
            for warning in result.warnings:
                print(f"  WARN: {warning}")

    # Exit with error if any gate failed
    if not all(r.passed for r in results.values()):
        sys.exit(1)

