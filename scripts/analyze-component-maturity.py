#!/usr/bin/env python3
"""
TTA Component Maturity Analysis Script

Analyzes all components for maturity status, test coverage, code quality,
and generates blocker reports.

Enhanced Features:
- Current stage tracking (Development/Staging/Production)
- 7-day observation period tracking for staging components
- Active blocker tracking with issue references
- Code quality status (linting, type checking, security)
"""

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Component definitions
COMPONENTS = {
    "Core Infrastructure": {
        "Neo4j": {
            "path": "src/components/neo4j_component.py",
            "test_path": "tests/test_components.py",  # Contains Neo4j tests
            "maturity_file": "src/components/MATURITY.md",
        },
        "Docker": {
            "path": "src/components/docker_component.py",
            "test_path": "tests/test_components.py",
            "maturity_file": "src/components/MATURITY.md",
        },
        "Carbon": {
            "path": "src/components/carbon_component.py",
            "test_path": "tests/test_components.py",
            "maturity_file": "src/components/MATURITY.md",
        },
    },
    "AI/Agent Systems": {
        "Model Management": {
            "path": "src/components/model_management/",
            "test_path": "tests/test_model_management.py",
            "maturity_file": "src/components/model_management/MATURITY.md",
        },
        "LLM": {
            "path": "src/components/llm_component.py",
            "test_path": "tests/test_components.py",
            "maturity_file": "src/components/MATURITY.md",
        },
        "Agent Orchestration": {
            "path": "src/components/agent_orchestration_component.py",
            "test_path": "tests/agent_orchestration/",
            "maturity_file": "src/components/MATURITY.md",
        },
        "Narrative Arc Orchestrator": {
            "path": "src/components/narrative_arc_orchestrator/",
            "test_path": "tests/test_narrative_arc_orchestrator_component.py",
            "maturity_file": "src/components/narrative_arc_orchestrator/MATURITY.md",
        },
    },
    "Player Experience": {
        "Gameplay Loop": {
            "path": "src/components/gameplay_loop/",
            "test_path": "tests/integration/test_gameplay_loop_integration.py",
            "maturity_file": "src/components/gameplay_loop/MATURITY.md",
        },
        "Character Arc Manager": {
            "path": "src/components/character_arc_manager.py",
            "test_path": "tests/test_character_avatar_manager.py",
            "maturity_file": "src/components/MATURITY.md",
        },
        "Player Experience": {
            "path": "src/components/player_experience_component.py",
            "test_path": "tests/test_player_experience_component_integration.py",
            "maturity_file": "src/components/MATURITY.md",
        },
    },
    "Therapeutic Content": {
        "Narrative Coherence": {
            "path": "src/components/narrative_coherence/",
            "test_path": "tests/test_narrative_coherence_engine.py",
            "maturity_file": "src/components/narrative_coherence/MATURITY.md",
        },
        "Therapeutic Systems": {
            "path": "src/components/therapeutic_systems_enhanced/",
            "test_path": "tests/test_therapeutic_effectiveness_integration.py",
            "maturity_file": "src/components/therapeutic_systems_enhanced/MATURITY.md",
        },
    },
}


def run_command(cmd: list[str], capture_output=True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, check=False, capture_output=capture_output, text=True, timeout=60
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"⚠️  Command timed out: {' '.join(cmd)}")
        return subprocess.CompletedProcess(cmd, 1, "", "Timeout")
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return subprocess.CompletedProcess(cmd, 1, "", str(e))


def check_test_coverage(component_path: str, test_path: str) -> dict[str, Any]:
    """Check test coverage for a component."""
    print(f"  Checking coverage for {component_path}...")

    # Check if test file exists
    if not Path(test_path).exists():
        return {
            "coverage": 0.0,
            "tests_exist": False,
            "error": f"Test file not found: {test_path}",
        }

    # Run pytest with coverage using uv run (not uvx) to access project dependencies
    # Use --cov=src/components to track all component imports properly
    cmd = [
        "uv",
        "run",
        "pytest",
        test_path,
        "--cov=src/components",
        "--cov-report=json",
        "-q",
        "--no-cov-on-fail",
    ]

    result = run_command(cmd)

    # Try to read coverage.json and extract coverage for specific component
    try:
        with open("coverage.json") as f:
            data = json.load(f)

            # Find the specific component file in the coverage data
            component_file = None
            for file_path in data.get("files", {}).keys():
                if component_path in file_path:
                    component_file = file_path
                    break

            if component_file:
                coverage = data["files"][component_file]["summary"]["percent_covered"]
                return {
                    "coverage": round(coverage, 1),
                    "tests_exist": True,
                    "tests_passed": result.returncode == 0,
                }
            # Component file not found in coverage data - might not be imported
            return {
                "coverage": 0.0,
                "tests_exist": True,
                "tests_passed": result.returncode == 0,
                "error": f"Component {component_path} not found in coverage data (not imported by tests)",
            }
    except FileNotFoundError:
        return {
            "coverage": 0.0,
            "tests_exist": True,
            "tests_passed": False,
            "error": "Coverage data not generated",
        }
    except Exception as e:
        return {
            "coverage": 0.0,
            "tests_exist": True,
            "tests_passed": False,
            "error": str(e),
        }


def check_code_quality(component_path: str) -> dict[str, Any]:
    """Check code quality (linting, type checking, security)."""
    print(f"  Checking code quality for {component_path}...")

    results = {}

    # Linting with ruff (uvx is fine here - standalone tool)
    result = run_command(["uvx", "ruff", "check", component_path])
    results["linting"] = {
        "passed": result.returncode == 0,
        "issues": result.stdout.count("\n") if result.returncode != 0 else 0,
    }

    # Type checking with pyright (uvx is fine here - standalone tool)
    result = run_command(["uvx", "pyright", component_path])
    results["type_checking"] = {
        "passed": result.returncode == 0,
        "output": result.stdout[:200] if result.returncode != 0 else "",
    }

    # Security scan with bandit (uvx is fine here - standalone tool)
    result = run_command(["uvx", "bandit", "-r", component_path, "-ll"])
    results["security"] = {
        "passed": result.returncode == 0,
        "output": result.stdout[:200] if result.returncode != 0 else "",
    }

    return results


def check_documentation(component_path: str) -> dict[str, bool]:
    """Check if documentation exists."""
    print(f"  Checking documentation for {component_path}...")

    path = Path(component_path)

    # Check for README
    if path.is_dir():
        readme_exists = (path / "README.md").exists()
    else:
        readme_exists = (path.parent / "README.md").exists()

    return {
        "readme_exists": readme_exists,
        "api_docs_exist": False,  # Would need to check for specific API doc files
        "usage_examples_exist": readme_exists,  # Assume README has examples if it exists
    }


def get_component_stage(maturity_file: str) -> str:
    """Extract current stage from MATURITY.md file."""
    print(f"  Checking stage from {maturity_file}...")

    try:
        maturity_path = Path(maturity_file)
        if not maturity_path.exists():
            return "Development"

        with open(maturity_path) as f:
            content = f.read()

            # Look for "**Current Stage**: Staging" or similar patterns
            stage_match = re.search(
                r"\*\*Current Stage\*\*:\s*(\w+)", content, re.IGNORECASE
            )
            if stage_match:
                stage = stage_match.group(1)
                # Normalize stage names
                if stage.lower() in ["staging", "stage"]:
                    return "Staging"
                if stage.lower() in ["production", "prod"]:
                    return "Production"
                if stage.lower() in ["development", "dev"]:
                    return "Development"
                return stage

            # Alternative pattern: "Status: Staging" or "Stage: Staging"
            alt_match = re.search(
                r"(?:Status|Stage):\s*(\w+)", content, re.IGNORECASE
            )
            if alt_match:
                stage = alt_match.group(1)
                if stage.lower() in ["staging", "stage"]:
                    return "Staging"
                if stage.lower() in ["production", "prod"]:
                    return "Production"

    except Exception as e:
        print(f"    Warning: Could not parse stage from {maturity_file}: {e}")

    return "Development"


def get_observation_period(maturity_file: str) -> dict[str, Any] | None:
    """Extract 7-day observation period info from MATURITY.md file."""
    try:
        maturity_path = Path(maturity_file)
        if not maturity_path.exists():
            return None

        with open(maturity_path) as f:
            content = f.read()

            # Look for deployment date patterns
            # Pattern 1: "Promoted to Staging: 2025-10-08"
            # Pattern 2: "Deployed: 2025-10-08"
            # Pattern 3: "Promotion Date: 2025-10-08"
            date_patterns = [
                r"Promoted to Staging.*?(\d{4}-\d{2}-\d{2})",
                r"Deployed.*?(\d{4}-\d{2}-\d{2})",
                r"Promotion Date.*?(\d{4}-\d{2}-\d{2})",
            ]

            for pattern in date_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    deployed_date = datetime.strptime(match.group(1), "%Y-%m-%d")
                    observation_end = deployed_date + timedelta(days=7)
                    now = datetime.now()
                    days_remaining = (observation_end - now).days

                    return {
                        "deployed": deployed_date.strftime("%Y-%m-%d"),
                        "observation_end": observation_end.strftime("%Y-%m-%d"),
                        "days_remaining": max(0, days_remaining),
                        "complete": days_remaining <= 0,
                    }

    except Exception as e:
        print(f"    Warning: Could not parse observation period: {e}")

    return None


def get_blocker_issues(maturity_file: str) -> list[dict[str, str]]:
    """Extract blocker issue references from MATURITY.md file."""
    blockers = []

    try:
        maturity_path = Path(maturity_file)
        if not maturity_path.exists():
            return blockers

        with open(maturity_path) as f:
            content = f.read()

            # Look for issue references in blocker sections
            # Pattern: "Issue #23", "#23", "Blocker: #23", etc.
            issue_matches = re.finditer(
                r"(?:Issue|Blocker|TODO)?\s*#(\d+)(?::\s*(.+?)(?:\n|$))?",
                content,
                re.IGNORECASE,
            )

            for match in issue_matches:
                issue_num = match.group(1)
                description = match.group(2) if match.group(2) else "See issue for details"
                blockers.append(
                    {"issue": f"#{issue_num}", "description": description.strip()}
                )

    except Exception as e:
        print(f"    Warning: Could not parse blocker issues: {e}")

    return blockers


def analyze_component(name: str, config: dict[str, str]) -> dict[str, Any]:
    """Analyze a single component."""
    print(f"\n📊 Analyzing: {name}")

    analysis = {
        "name": name,
        "path": config["path"],
        "test_path": config["test_path"],
        "maturity_file": config["maturity_file"],
    }

    # Get current stage from MATURITY.md
    current_stage = get_component_stage(config["maturity_file"])
    analysis["current_stage"] = current_stage

    # Get observation period (if in staging)
    if current_stage == "Staging":
        observation_period = get_observation_period(config["maturity_file"])
        analysis["observation_period"] = observation_period
    else:
        analysis["observation_period"] = None

    # Get blocker issues from MATURITY.md
    blocker_issues = get_blocker_issues(config["maturity_file"])
    analysis["blocker_issues"] = blocker_issues

    # Check test coverage
    coverage_data = check_test_coverage(config["path"], config["test_path"])
    analysis["coverage"] = coverage_data

    # Check code quality
    quality_data = check_code_quality(config["path"])
    analysis["quality"] = quality_data

    # Check documentation
    doc_data = check_documentation(config["path"])
    analysis["documentation"] = doc_data

    # Determine blockers (automated checks)
    blockers = []
    if coverage_data["coverage"] < 70:
        blockers.append(
            {
                "type": "tests",
                "description": f"Test coverage ({coverage_data['coverage']}%) below 70% threshold",
                "gap": round(70 - coverage_data["coverage"], 1),
            }
        )

    if not quality_data["linting"]["passed"]:
        blockers.append(
            {
                "type": "code_quality",
                "description": f"Linting issues found ({quality_data['linting']['issues']} issues)",
            }
        )

    if not quality_data["type_checking"]["passed"]:
        blockers.append(
            {"type": "code_quality", "description": "Type checking errors found"}
        )

    if not quality_data["security"]["passed"]:
        blockers.append(
            {"type": "security", "description": "Security scan found issues"}
        )

    if not doc_data["readme_exists"]:
        blockers.append(
            {"type": "documentation", "description": "Component README missing"}
        )

    analysis["blockers"] = blockers
    analysis["blocker_count"] = len(blockers)

    # Determine readiness based on current stage
    if current_stage == "Development":
        analysis["ready_for_staging"] = (
            len(blockers) == 0 and coverage_data["coverage"] >= 70
        )
        analysis["ready_for_production"] = False
    elif current_stage == "Staging":
        analysis["ready_for_staging"] = True  # Already in staging
        # For production: need 80% coverage + observation period complete + no blockers
        observation_complete = (
            analysis["observation_period"] is not None
            and analysis["observation_period"]["complete"]
        )
        analysis["ready_for_production"] = (
            len(blockers) == 0
            and coverage_data["coverage"] >= 80
            and observation_complete
        )
    elif current_stage == "Production":
        analysis["ready_for_staging"] = True
        analysis["ready_for_production"] = True
    else:
        analysis["ready_for_staging"] = (
            len(blockers) == 0 and coverage_data["coverage"] >= 70
        )
        analysis["ready_for_production"] = False

    return analysis


def main():
    """Main analysis function."""
    print("=" * 80)
    print("TTA Component Maturity Analysis")
    print("=" * 80)

    all_results = {}

    for group_name, components in COMPONENTS.items():
        print(f"\n{'=' * 80}")
        print(f"Functional Group: {group_name}")
        print(f"{'=' * 80}")

        group_results = {}
        for component_name, config in components.items():
            result = analyze_component(component_name, config)
            group_results[component_name] = result

        all_results[group_name] = group_results

    # Save results
    output_file = "component-maturity-analysis.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 80}")
    print(f"✅ Analysis complete! Results saved to: {output_file}")
    print(f"{'=' * 80}")

    return all_results


if __name__ == "__main__":
    main()
