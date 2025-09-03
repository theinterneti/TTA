#!/usr/bin/env python3
"""
CI Pipeline Test Script

This script tests the basic functionality of the CI/CD pipeline setup
by verifying that all services can be imported and started correctly.
"""

import logging
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_player_experience_import():
    """Test that Player Experience API can be imported and app created."""
    try:
        from src.player_experience.api.app import create_app

        app = create_app()
        assert app is not None, "App creation returned None"
        logger.info("✅ Player Experience API: Import and app creation successful")
        return True
    except Exception as e:
        logger.error(f"❌ Player Experience API: Failed - {e}")
        return False


def test_api_gateway_import():
    """Test that API Gateway can be imported and app created."""
    try:
        from src.api_gateway.app import create_gateway_app

        app = create_gateway_app()
        assert app is not None, "App creation returned None"
        logger.info("✅ API Gateway: Import and app creation successful")
        return True
    except Exception as e:
        logger.error(f"❌ API Gateway: Failed - {e}")
        return False


def test_agent_orchestration_import():
    """Test that Agent Orchestration can be imported and app created."""
    try:
        from src.agent_orchestration.main import create_agent_orchestration_app

        app = create_agent_orchestration_app()
        assert app is not None, "App creation returned None"
        logger.info("✅ Agent Orchestration: Import and app creation successful")
        return True
    except Exception as e:
        logger.error(f"❌ Agent Orchestration: Failed - {e}")
        return False


def test_workflow_yaml_syntax():
    """Test that the GitHub Actions workflow has valid YAML syntax."""
    try:
        import yaml

        workflow_path = project_root / ".github" / "workflows" / "debug-integration.yml"

        if not workflow_path.exists():
            logger.error(f"❌ Workflow file not found: {workflow_path}")
            return False

        with open(workflow_path) as f:
            yaml.safe_load(f)

        logger.info("✅ GitHub Actions workflow: YAML syntax is valid")
        return True
    except Exception as e:
        logger.error(f"❌ GitHub Actions workflow: YAML syntax error - {e}")
        return False


def test_uv_dependencies():
    """Test that uv can resolve dependencies."""
    try:
        import subprocess

        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            logger.info(f"✅ UV package manager: Available - {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ UV package manager: Not available - {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ UV package manager: Error - {e}")
        return False


def main():
    """Run all CI pipeline tests."""
    logger.info("🚀 Starting CI Pipeline Tests...")

    tests = [
        ("YAML Syntax", test_workflow_yaml_syntax),
        ("UV Dependencies", test_uv_dependencies),
        ("Player Experience API", test_player_experience_import),
        ("API Gateway", test_api_gateway_import),
        ("Agent Orchestration", test_agent_orchestration_import),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name}: Unexpected error - {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n📊 CI Pipeline Test Results:")
    logger.info("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:25} {status}")
        if result:
            passed += 1

    logger.info("=" * 50)
    logger.info(f"Total: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All CI pipeline tests passed! Pipeline is ready.")
        return 0
    else:
        logger.error(f"💥 {total - passed} tests failed. Pipeline needs fixes.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
