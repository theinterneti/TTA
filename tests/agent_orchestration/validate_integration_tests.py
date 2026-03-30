#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Validate_integration_tests]]
Integration Test Validation Script

This script validates that the comprehensive integration test suite for Task 12.2
is properly implemented and ready for CI/CD execution.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""

    try:
        result = subprocess.run(
            cmd,
            check=False,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        if result.returncode == 0:
            if result.stdout.strip():
                # Show test count from output
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if ".py:" in line and any(char.isdigit() for char in line):
                        pass
            return True
        if result.stderr:
            pass
        return False

    except Exception:
        return False


def validate_test_files():
    """Validate that all test files exist and are properly structured."""

    test_files = [
        "test_multi_agent_workflow_integration.py",
        "test_end_to_end_workflows.py",
        "test_error_handling_recovery.py",
        "test_state_persistence_aggregation.py",
        "test_performance_concurrency.py",
        "README_INTEGRATION_TESTS.md",
        "INTEGRATION_TEST_SUMMARY.md",
    ]

    base_path = Path(__file__).parent
    all_exist = True

    for test_file in test_files:
        file_path = base_path / test_file
        if file_path.exists():
            pass
        else:
            all_exist = False

    return all_exist


def validate_test_discovery():
    """Validate that pytest can discover all integration tests."""

    commands = [
        (
            "uv run pytest tests/agent_orchestration/test_end_to_end_workflows.py --collect-only -q",
            "End-to-end workflow tests discovery",
        ),
        (
            "uv run pytest tests/agent_orchestration/test_error_handling_recovery.py --collect-only -q",
            "Error handling tests discovery",
        ),
        (
            "uv run pytest tests/agent_orchestration/test_state_persistence_aggregation.py --collect-only -q",
            "State persistence tests discovery",
        ),
        (
            "uv run pytest tests/agent_orchestration/test_performance_concurrency.py --collect-only -q",
            "Performance tests discovery",
        ),
    ]

    all_success = True
    total_tests = 0

    for cmd, desc in commands:
        success = run_command(cmd, desc)
        if not success:
            all_success = False
        else:
            # Try to extract test count
            try:
                result = subprocess.run(
                    cmd, check=False, shell=True, capture_output=True, text=True
                )
                for line in result.stdout.split("\n"):
                    if ".py:" in line and line.strip().split(":")[-1].strip().isdigit():
                        count = int(line.strip().split(":")[-1].strip())
                        total_tests += count
            except Exception:
                pass

    return all_success


def validate_three_tier_execution():
    """Validate three-tier test execution pattern."""

    test_file = "tests/agent_orchestration/test_end_to_end_workflows.py"

    commands = [
        (f"uv run pytest {test_file} --collect-only -q", "Tier 1: Unit tests only"),
        (
            f"uv run pytest {test_file} --redis --collect-only -q",
            "Tier 2: Redis integration",
        ),
        (
            f"uv run pytest {test_file} --neo4j --collect-only -q",
            "Tier 3: Neo4j integration",
        ),
        (
            f"uv run pytest {test_file} --redis --neo4j --collect-only -q",
            "Full integration: Redis + Neo4j",
        ),
    ]

    all_success = True
    for cmd, desc in commands:
        success = run_command(cmd, desc)
        if not success:
            all_success = False

    return all_success


def validate_ci_cd_compatibility():
    """Validate CI/CD configuration compatibility."""

    # Check if GitHub Actions workflow exists
    workflow_path = (
        Path(__file__).parent.parent.parent / ".github" / "workflows" / "tests.yml"
    )
    if workflow_path.exists():
        # Check if integration job exists
        with open(workflow_path) as f:
            content = f.read()

        checks = [
            ("integration:" in content, "Integration job defined"),
            ("neo4j:" in content, "Neo4j service configured"),
            ("redis:" in content, "Redis service configured"),
            ("--neo4j --redis" in content, "Integration test flags configured"),
        ]

        all_good = True
        for check, _desc in checks:
            if check:
                pass
            else:
                all_good = False

        return all_good
    return False


def validate_pytest_markers():
    """Validate that tests have proper pytest markers."""

    test_files = [
        "test_end_to_end_workflows.py",
        "test_error_handling_recovery.py",
        "test_state_persistence_aggregation.py",
        "test_performance_concurrency.py",
    ]

    base_path = Path(__file__).parent
    all_good = True

    for test_file in test_files:
        file_path = base_path / test_file
        if file_path.exists():
            with open(file_path) as f:
                content = f.read()

            markers = [
                ("@pytest.mark.integration", "Integration marker"),
                ("@pytest.mark.redis", "Redis marker"),
                ("@pytest.mark.neo4j", "Neo4j marker"),
            ]

            file_good = True
            for marker, _desc in markers:
                if marker in content:
                    pass
                else:
                    file_good = False
                    all_good = False

            if file_good:
                pass
        else:
            all_good = False

    return all_good


def main():
    """Main validation function."""

    validations = [
        ("Test File Structure", validate_test_files),
        ("Test Discovery", validate_test_discovery),
        ("Three-Tier Execution", validate_three_tier_execution),
        ("CI/CD Compatibility", validate_ci_cd_compatibility),
        ("Pytest Markers", validate_pytest_markers),
    ]

    results = {}
    for name, validator in validations:
        try:
            results[name] = validator()
        except Exception:
            results[name] = False

    # Summary

    all_passed = True
    for name, passed in results.items():
        if not passed:
            all_passed = False

    if all_passed:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
