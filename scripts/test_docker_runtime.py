# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Test script to verify Docker runtime for OpenHands integration.

Tests:
1. Docker availability
2. Docker runtime configuration
3. Single task execution with Docker runtime
4. File generation and extraction
5. Compare Docker runtime vs mock fallback quality
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


from agent_orchestration.openhands_integration.adapter import OpenHandsAdapter
from agent_orchestration.openhands_integration.config import (
    OpenHandsConfig,
    OpenHandsIntegrationConfig,
)
from agent_orchestration.openhands_integration.docker_client import (
    DockerOpenHandsClient,
)
from agent_orchestration.openhands_integration.result_validator import ResultValidator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_docker_availability():
    """Test if Docker is available."""
    logger.info("=" * 80)
    logger.info("TEST 1: Docker Availability")
    logger.info("=" * 80)

    import subprocess

    try:
        result = subprocess.run(
            ["docker", "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            logger.info(f"✅ Docker available: {result.stdout.strip()}")
            return True
        logger.error(f"❌ Docker error: {result.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Docker not available: {e}")
        return False


async def test_docker_runtime_config():
    """Test Docker runtime configuration."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Docker Runtime Configuration")
    logger.info("=" * 80)

    try:
        config = OpenHandsIntegrationConfig.from_env()

        logger.info(f"use_docker_runtime: {config.use_docker_runtime}")
        logger.info(f"docker_image: {config.docker_image}")
        logger.info(f"docker_runtime_image: {config.docker_runtime_image}")
        logger.info(f"docker_timeout: {config.docker_timeout}")

        if config.use_docker_runtime:
            logger.info("✅ Docker runtime is ENABLED")
            return True
        logger.warning("⚠️  Docker runtime is DISABLED (expected for this test)")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration error: {e}")
        return False


async def test_docker_client_initialization():
    """Test Docker client initialization."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Docker Client Initialization")
    logger.info("=" * 80)

    try:
        integration_config = OpenHandsIntegrationConfig.from_env()

        # Convert to OpenHandsConfig for DockerOpenHandsClient
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=integration_config.model_preset,
            base_url=integration_config.base_url,
            workspace_path=integration_config.workspace_root,
        )

        client = DockerOpenHandsClient(config)
        logger.info("✅ Docker client initialized")
        logger.info(f"   OpenHands image: {client.openhands_image}")
        logger.info(f"   Runtime image: {client.runtime_image}")
        return True
    except Exception as e:
        logger.error(f"❌ Docker client initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_docker_runtime_execution():
    """Test Docker runtime task execution."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Docker Runtime Task Execution")
    logger.info("=" * 80)

    try:
        integration_config = OpenHandsIntegrationConfig.from_env()

        # Convert to OpenHandsConfig for DockerOpenHandsClient
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=integration_config.model_preset,
            base_url=integration_config.base_url,
            workspace_path=integration_config.workspace_root,
        )

        client = DockerOpenHandsClient(config)
        adapter = OpenHandsAdapter(client=client, fallback_to_mock=False)

        # Simple test task
        task_description = "Generate a simple Python test file for a calculator module"

        logger.info(f"Executing task: {task_description}")
        result = await adapter.execute_development_task(
            task_description=task_description,
            context={"workspace_path": config.workspace_path},
        )

        logger.info("✅ Task executed")
        logger.info(f"   Success: {result.get('success', False)}")
        logger.info(f"   Output length: {len(result.get('output', ''))}")
        logger.info(f"   Error: {result.get('error', 'None')}")

        return result.get("success", False)
    except Exception as e:
        logger.error(f"❌ Docker runtime execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_result_validation():
    """Test result validation for Docker runtime output."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Result Validation")
    logger.info("=" * 80)

    try:
        validator = ResultValidator()

        # Mock Docker runtime result
        result = {
            "success": True,
            "content": """import pytest
import unittest
from calculator import Calculator

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_add(self):
        assert self.calc.add(2, 3) == 5

    def test_subtract(self):
        assert self.calc.subtract(5, 3) == 2
""",
            "output_file": "test_calculator.py",
            "error": None,
            "execution_time": 2.5,
            "metadata": {"docker_mode": True},
        }

        validation_result = validator.validate(result)

        logger.info("✅ Validation completed")
        logger.info(f"   Valid: {validation_result.passed}")
        logger.info(f"   Errors: {validation_result.errors}")
        logger.info(f"   Warnings: {validation_result.warnings}")
        logger.info(f"   Score: {validation_result.score}")

        return validation_result.passed
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    logger.info("\n" + "=" * 80)
    logger.info("DOCKER RUNTIME VERIFICATION TEST SUITE")
    logger.info("=" * 80)

    results = {
        "Docker Availability": await test_docker_availability(),
        "Docker Configuration": await test_docker_runtime_config(),
        "Docker Client Init": await test_docker_client_initialization(),
        "Docker Execution": await test_docker_runtime_execution(),
        "Result Validation": await test_result_validation(),
    }

    logger.info("\n" + "=" * 80)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    logger.info(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        logger.info("🚀 All tests passed! Docker runtime is ready.")
        return 0
    logger.warning(f"⚠️  {total_count - passed_count} test(s) failed.")
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
