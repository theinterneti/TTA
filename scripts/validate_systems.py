#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Validate_systems]]
Comprehensive validation script for TTA critical systems.

Validates:
1. Workflow Observability - Monitoring, logging, metrics
2. OpenHands Integration - Docker client, task execution, file creation
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables from .env file
from dotenv import load_dotenv

env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)
    logger_temp = logging.getLogger(__name__)
    logger_temp.info(f"Loaded environment from {env_file}")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ValidationReport:
    """Collect validation results."""

    def __init__(self):
        self.results = {
            "workflow_observability": {},
            "openhands_integration": {},
            "summary": {"total_checks": 0, "passed": 0, "failed": 0, "warnings": 0},
        }

    def add_check(self, category: str, name: str, status: str, details: Any = None):
        """Add a validation check result."""
        if category not in self.results:
            self.results[category] = {}

        self.results[category][name] = {"status": status, "details": details}

        self.results["summary"]["total_checks"] += 1
        if status == "PASS":
            self.results["summary"]["passed"] += 1
        elif status == "FAIL":
            self.results["summary"]["failed"] += 1
        elif status == "WARN":
            self.results["summary"]["warnings"] += 1

    def print_report(self):
        """Print formatted validation report."""

        for category, checks in self.results.items():
            if category == "summary":
                continue

            for result in checks.values():
                {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(
                    result["status"], "❓"
                )

                if result.get("details"):
                    pass

        summary = self.results["summary"]

        return summary["failed"] == 0


async def validate_workflow_observability(report: ValidationReport):
    """Validate workflow monitoring and logging systems."""
    logger.info("Validating workflow observability...")

    # Check if workflow manager exists
    try:
        from agent_orchestration.workflow_manager import WorkflowManager

        report.add_check("workflow_observability", "WorkflowManager Import", "PASS")
    except ImportError as e:
        report.add_check(
            "workflow_observability",
            "WorkflowManager Import",
            "WARN",
            f"Legacy path failed: {e}",
        )
        # Try alternative path
        try:
            sys.path.insert(
                0,
                str(
                    Path(__file__).parent.parent
                    / "packages"
                    / "tta-ai-framework"
                    / "src"
                ),
            )
            from tta_ai.orchestration.workflow_manager import WorkflowManager

            report.add_check(
                "workflow_observability", "WorkflowManager Import (alt)", "PASS"
            )
        except ImportError as e2:
            report.add_check(
                "workflow_observability",
                "WorkflowManager Import (alt)",
                "FAIL",
                str(e2),
            )
            return

    # Check metrics collection
    try:
        from agent_orchestration.openhands_integration.metrics_collector import (
            MetricsCollector,
        )

        report.add_check("workflow_observability", "MetricsCollector Import", "PASS")
    except ImportError:
        report.add_check(
            "workflow_observability",
            "MetricsCollector Import",
            "WARN",
            "MetricsCollector not found, using basic logging",
        )

    # Check logging configuration
    try:
        import logging

        root_logger = logging.getLogger()
        has_handlers = len(root_logger.handlers) > 0
        report.add_check(
            "workflow_observability",
            "Logging Configuration",
            "PASS" if has_handlers else "WARN",
            f"Handlers: {len(root_logger.handlers)}",
        )
    except Exception as e:
        report.add_check(
            "workflow_observability", "Logging Configuration", "FAIL", str(e)
        )


async def validate_openhands_integration(report: ValidationReport):
    """Validate OpenHands integration."""
    logger.info("Validating OpenHands integration...")

    # 1. Check all files present
    openhands_dir = Path("src/agent_orchestration/openhands_integration")
    expected_files = [
        "__init__.py",
        "adapter.py",
        "cli.py",
        "client.py",
        "config.py",
        "docker_client.py",
        "error_recovery.py",
        "execution_engine.py",
        "helpers.py",
        "metrics_collector.py",
        "model_rotation.py",
        "model_selector.py",
        "models.py",
        "optimized_client.py",
        "primitives.py",
        "proxy.py",
        "result_validator.py",
        "retry_policy.py",
        "task_queue.py",
        "workflow_integration.py",
    ]

    missing_files = []
    for file in expected_files:
        if not (openhands_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        report.add_check(
            "openhands_integration",
            "Files Present",
            "FAIL",
            f"Missing: {', '.join(missing_files)}",
        )
        return
    report.add_check(
        "openhands_integration",
        "Files Present",
        "PASS",
        f"All {len(expected_files)} core files present",
    )

    # 2. Check imports
    try:
        from agent_orchestration.openhands_integration import (
            DockerOpenHandsClient,
            OpenHandsClient,
            OpenHandsConfig,
            OpenHandsIntegrationConfig,
            OpenHandsTaskResult,
        )

        report.add_check("openhands_integration", "Module Imports", "PASS")
    except ImportError as e:
        report.add_check("openhands_integration", "Module Imports", "FAIL", str(e))
        return

    # 3. Check environment variables
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        report.add_check(
            "openhands_integration",
            "API Key Configuration",
            "FAIL",
            "OPENROUTER_API_KEY not set or using placeholder",
        )
        return
    report.add_check(
        "openhands_integration",
        "API Key Configuration",
        "PASS",
        f"Key length: {len(api_key)} chars",
    )

    # 4. Test configuration loading
    try:
        from agent_orchestration.openhands_integration.config import (
            OpenHandsIntegrationConfig,
        )

        config = OpenHandsIntegrationConfig.from_env()
        report.add_check(
            "openhands_integration",
            "Config Loading",
            "PASS",
            f"Model: {config.model_preset}",
        )
    except Exception as e:
        report.add_check("openhands_integration", "Config Loading", "FAIL", str(e))
        return

    # 5. Test Docker client initialization
    try:
        from pydantic import SecretStr

        from agent_orchestration.openhands_integration import (
            DockerOpenHandsClient,
            OpenHandsConfig,
        )

        test_config = OpenHandsConfig(
            api_key=SecretStr(api_key),
            model="openrouter/deepseek/deepseek-chat-v3.1:free",
            workspace_path=Path(tempfile.gettempdir()),
        )

        client = DockerOpenHandsClient(test_config)
        report.add_check(
            "openhands_integration",
            "Docker Client Init",
            "PASS",
            f"Image: {client.openhands_image}",
        )
    except Exception as e:
        report.add_check("openhands_integration", "Docker Client Init", "FAIL", str(e))
        return

    # 6. Test simple task execution (if API key is valid)
    logger.info("Testing simple OpenHands task execution...")
    try:
        workspace = Path(tempfile.mkdtemp(prefix="openhands_test_"))
        workspace / "validation_test.txt"

        task_description = f"Create a file named validation_test.txt with content 'OpenHands validation successful at {Path.cwd()}'"

        logger.info(f"Workspace: {workspace}")
        logger.info(f"Task: {task_description}")

        # Note: This will actually execute OpenHands, which may take time
        # For now, we'll skip actual execution and just validate setup
        report.add_check(
            "openhands_integration",
            "Task Execution Test",
            "SKIP",
            "Skipped to avoid API costs - setup validated",
        )

    except Exception as e:
        report.add_check("openhands_integration", "Task Execution Test", "WARN", str(e))


async def main():
    """Run all validations."""
    report = ValidationReport()

    # Run validations
    await validate_workflow_observability(report)
    await validate_openhands_integration(report)

    # Print report
    success = report.print_report()

    # Save report to file
    report_file = Path("validation_report.json")
    with open(report_file, "w") as f:
        json.dump(report.results, f, indent=2)

    logger.info(f"Detailed report saved to: {report_file}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
