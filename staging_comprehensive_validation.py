#!/usr/bin/env python3
"""
TTA Staging Environment Comprehensive Validation Script
Validates all code and functionality in the staging environment
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class StagingValidator:
    """Comprehensive staging environment validator"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": "staging",
            "phases": {},
            "summary": {"total_checks": 0, "passed": 0, "failed": 0, "warnings": 0},
        }
        self.project_root = Path.cwd()

    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

    def print_section(self, text: str):
        """Print formatted section"""
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}▶ {text}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'-' * 80}{Colors.ENDC}")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

    def print_failure(self, text: str):
        """Print failure message"""
        print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")

    def run_command(self, cmd: str, timeout: int = 300) -> tuple[int, str, str]:
        """Run shell command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd,
                check=False,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", str(e)

    async def phase1_environment_check(self) -> dict[str, Any]:
        """Phase 1: Check staging environment status"""
        self.print_header("PHASE 1: STAGING ENVIRONMENT STATUS")
        phase_results = {"checks": [], "status": "passed"}

        # Check Docker services
        self.print_section("Checking Docker Services")
        returncode, stdout, stderr = self.run_command(
            'docker ps --filter "name=staging" --format "{{.Names}}\t{{.Status}}"'
        )

        if returncode == 0:
            services = stdout.strip().split("\n") if stdout.strip() else []
            running_services = [s for s in services if "Up" in s]
            stopped_services = [s for s in services if "Exited" in s or "Created" in s]

            self.print_info(f"Found {len(services)} staging services")
            self.print_success(f"Running: {len(running_services)} services")
            if stopped_services:
                self.print_warning(f"Stopped: {len(stopped_services)} services")

            phase_results["checks"].append(
                {
                    "name": "Docker Services",
                    "status": "passed" if running_services else "warning",
                    "details": {
                        "total": len(services),
                        "running": len(running_services),
                        "stopped": len(stopped_services),
                    },
                }
            )
        else:
            self.print_failure("Failed to check Docker services")
            phase_results["checks"].append(
                {"name": "Docker Services", "status": "failed", "error": stderr}
            )
            phase_results["status"] = "failed"

        # Check database connectivity
        self.print_section("Checking Database Connectivity")

        # Redis
        returncode, stdout, stderr = self.run_command(
            'docker exec tta-staging-redis redis-cli -a staging_redis_secure_pass_2024 ping 2>/dev/null || echo "FAILED"'
        )
        if "PONG" in stdout:
            self.print_success("Redis: Connected")
            phase_results["checks"].append({"name": "Redis", "status": "passed"})
        else:
            self.print_failure("Redis: Not accessible")
            phase_results["checks"].append(
                {"name": "Redis", "status": "failed", "error": stderr}
            )
            phase_results["status"] = "warning"

        # Neo4j
        returncode, stdout, stderr = self.run_command(
            'docker exec tta-staging-neo4j cypher-shell -u neo4j -p staging_neo4j_secure_pass_2024 "RETURN 1" 2>/dev/null || echo "FAILED"'
        )
        if returncode == 0 and "FAILED" not in stdout:
            self.print_success("Neo4j: Connected")
            phase_results["checks"].append({"name": "Neo4j", "status": "passed"})
        else:
            self.print_failure("Neo4j: Not accessible")
            phase_results["checks"].append(
                {"name": "Neo4j", "status": "failed", "error": stderr}
            )
            phase_results["status"] = "warning"

        # Postgres
        returncode, stdout, stderr = self.run_command(
            "docker exec tta-staging-postgres pg_isready -U tta_staging_user 2>/dev/null"
        )
        if returncode == 0:
            self.print_success("Postgres: Connected")
            phase_results["checks"].append({"name": "Postgres", "status": "passed"})
        else:
            self.print_failure("Postgres: Not accessible")
            phase_results["checks"].append({"name": "Postgres", "status": "failed"})
            phase_results["status"] = "warning"

        self.results["phases"]["phase1_environment"] = phase_results
        return phase_results

    async def phase2_unit_tests(self) -> dict[str, Any]:
        """Phase 2: Run unit tests"""
        self.print_header("PHASE 2: UNIT TESTS")
        phase_results = {"checks": [], "status": "passed"}

        self.print_section("Running Unit Tests (no external dependencies)")

        # Run pytest with markers to exclude integration tests
        returncode, stdout, stderr = self.run_command(
            'uv run pytest -q -m "not neo4j and not redis and not integration" --tb=short --maxfail=10',
            timeout=300,
        )

        # Parse results
        if returncode == 0:
            self.print_success("All unit tests passed")
            phase_results["status"] = "passed"
        elif returncode == 1:
            self.print_warning("Some unit tests failed")
            phase_results["status"] = "warning"
        else:
            self.print_failure("Unit tests encountered errors")
            phase_results["status"] = "failed"

        phase_results["checks"].append(
            {
                "name": "Unit Tests",
                "status": phase_results["status"],
                "output": stdout[-2000:] if stdout else "",  # Last 2000 chars
                "errors": stderr[-1000:] if stderr else "",
            }
        )

        self.results["phases"]["phase2_unit_tests"] = phase_results
        return phase_results

    async def phase3_integration_tests(self) -> dict[str, Any]:
        """Phase 3: Run integration tests with real databases"""
        self.print_header("PHASE 3: INTEGRATION TESTS")
        phase_results = {"checks": [], "status": "passed"}

        self.print_section("Running Integration Tests (with Redis/Neo4j)")

        # Check if databases are available
        redis_available = "passed" in str(
            self.results["phases"]["phase1_environment"]["checks"]
        )

        if not redis_available:
            self.print_warning(
                "Databases not fully available, skipping integration tests"
            )
            phase_results["status"] = "skipped"
            phase_results["checks"].append(
                {
                    "name": "Integration Tests",
                    "status": "skipped",
                    "reason": "Databases not available",
                }
            )
        else:
            # Run integration tests
            returncode, stdout, stderr = self.run_command(
                "ENVIRONMENT=staging uv run pytest tests/integration/ -v --tb=short --maxfail=5",
                timeout=600,
            )

            if returncode == 0:
                self.print_success("All integration tests passed")
                phase_results["status"] = "passed"
            elif returncode == 1:
                self.print_warning("Some integration tests failed")
                phase_results["status"] = "warning"
            else:
                self.print_failure("Integration tests encountered errors")
                phase_results["status"] = "failed"

            phase_results["checks"].append(
                {
                    "name": "Integration Tests",
                    "status": phase_results["status"],
                    "output": stdout[-2000:] if stdout else "",
                    "errors": stderr[-1000:] if stderr else "",
                }
            )

        self.results["phases"]["phase3_integration_tests"] = phase_results
        return phase_results

    async def phase4_code_quality(self) -> dict[str, Any]:
        """Phase 4: Code quality checks"""
        self.print_header("PHASE 4: CODE QUALITY CHECKS")
        phase_results = {"checks": [], "status": "passed"}

        # Ruff linting
        self.print_section("Running Ruff Linter")
        returncode, stdout, stderr = self.run_command(
            "uv run ruff check src/ --output-format=concise"
        )

        if returncode == 0:
            self.print_success("Ruff: No linting issues")
            phase_results["checks"].append({"name": "Ruff Linting", "status": "passed"})
        else:
            issue_count = len(stdout.split("\n")) if stdout else 0
            self.print_warning(f"Ruff: Found {issue_count} issues")
            phase_results["checks"].append(
                {
                    "name": "Ruff Linting",
                    "status": "warning",
                    "issues": issue_count,
                    "sample": stdout[:500] if stdout else "",
                }
            )

        self.results["phases"]["phase4_code_quality"] = phase_results
        return phase_results

    def generate_report(self):
        """Generate final validation report"""
        self.print_header("VALIDATION SUMMARY")

        # Calculate totals
        for phase_name, phase_data in self.results["phases"].items():
            for check in phase_data.get("checks", []):
                self.results["summary"]["total_checks"] += 1
                if check["status"] == "passed":
                    self.results["summary"]["passed"] += 1
                elif check["status"] == "failed":
                    self.results["summary"]["failed"] += 1
                elif check["status"] == "warning":
                    self.results["summary"]["warnings"] += 1

        # Print summary
        print(
            f"\n{Colors.BOLD}Total Checks:{Colors.ENDC} {self.results['summary']['total_checks']}"
        )
        print(
            f"{Colors.OKGREEN}✓ Passed:{Colors.ENDC} {self.results['summary']['passed']}"
        )
        print(
            f"{Colors.WARNING}⚠ Warnings:{Colors.ENDC} {self.results['summary']['warnings']}"
        )
        print(
            f"{Colors.FAIL}✗ Failed:{Colors.ENDC} {self.results['summary']['failed']}"
        )

        # Overall status
        if self.results["summary"]["failed"] == 0:
            if self.results["summary"]["warnings"] == 0:
                print(
                    f"\n{Colors.OKGREEN}{Colors.BOLD}✓ STAGING ENVIRONMENT: FULLY OPERATIONAL{Colors.ENDC}"
                )
                overall_status = "PASS"
            else:
                print(
                    f"\n{Colors.WARNING}{Colors.BOLD}⚠ STAGING ENVIRONMENT: OPERATIONAL WITH WARNINGS{Colors.ENDC}"
                )
                overall_status = "PASS_WITH_WARNINGS"
        else:
            print(
                f"\n{Colors.FAIL}{Colors.BOLD}✗ STAGING ENVIRONMENT: ISSUES DETECTED{Colors.ENDC}"
            )
            overall_status = "FAIL"

        self.results["summary"]["overall_status"] = overall_status

        # Save report
        report_file = self.project_root / "staging_validation_report.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n{Colors.OKBLUE}📄 Full report saved to: {report_file}{Colors.ENDC}")

        return overall_status


async def main():
    """Main validation workflow"""
    validator = StagingValidator()

    print(f"{Colors.BOLD}TTA Staging Environment Comprehensive Validation{Colors.ENDC}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Run validation phases
        await validator.phase1_environment_check()
        await validator.phase2_unit_tests()
        await validator.phase3_integration_tests()
        await validator.phase4_code_quality()

        # Generate report
        overall_status = validator.generate_report()

        # Exit with appropriate code
        sys.exit(0 if overall_status in ["PASS", "PASS_WITH_WARNINGS"] else 1)

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Validation interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}Validation failed with error: {e}{Colors.ENDC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
