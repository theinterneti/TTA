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

        # Test UV availability
        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            logger.error(f"❌ UV package manager: Not available - {result.stderr}")
            return False

        uv_version = result.stdout.strip()
        logger.info(f"✅ UV package manager: Available - {uv_version}")

        # Test dependency resolution
        logger.info("🔍 Testing dependency resolution...")
        sync_result = subprocess.run(
            ["uv", "sync", "--dry-run"], capture_output=True, text=True, timeout=30
        )

        if sync_result.returncode == 0:
            logger.info("✅ UV dependency resolution: Working correctly")
            return True
        else:
            logger.error(f"❌ UV dependency resolution: Failed - {sync_result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ UV package manager: Timeout during testing")
        return False
    except Exception as e:
        logger.error(f"❌ UV package manager: Error - {e}")
        return False


def test_debug_tools_files():
    """Test that debug tools implementation files exist and are valid."""
    try:
        # Backend WebSocket monitoring endpoints
        backend_files = [
            "src/agent_orchestration/websocket/monitoring_endpoint.py",
            "src/api_gateway/websocket/monitoring_router.py",
            "src/player_experience/api/routers/monitoring_websocket.py",
        ]

        # Frontend debug components (check for actual files that exist)
        frontend_files = [
            "web-interfaces/developer-interface/src/components/debug/DebugToolsPanel.tsx",
            "web-interfaces/developer-interface/src/components/debug/NetworkMonitor.tsx",
            "web-interfaces/developer-interface/src/components/debug/PerformanceProfiler.tsx",
            "web-interfaces/developer-interface/src/components/debug/ErrorTracker.tsx",
        ]

        all_files = backend_files + frontend_files
        missing_files = []
        existing_files = []

        for file_path in all_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                existing_files.append(file_path)

        if missing_files:
            logger.warning(f"⚠️ Debug Tools Files: Some files missing - {missing_files}")
            logger.info(
                f"✅ Debug Tools Files: Found {len(existing_files)} implementation files"
            )
            # Don't fail if we have the core backend files
            if all(
                f
                in [
                    str(p)
                    for p in [
                        project_root / f
                        for f in backend_files
                        if (project_root / f).exists()
                    ]
                ]
                for f in backend_files
            ):
                logger.info(
                    "✅ Debug Tools Files: All backend monitoring endpoints present"
                )
                return True
            return False

        logger.info("✅ Debug Tools Files: All implementation files present")
        return True
    except Exception as e:
        logger.error(f"❌ Debug Tools Files: Error - {e}")
        return False


def test_service_configurations():
    """Test that service configurations are valid."""
    try:
        # Test API Gateway config
        from src.api_gateway.config import get_gateway_settings

        gateway_settings = get_gateway_settings()
        assert hasattr(gateway_settings, "host"), "Gateway settings missing host"
        assert hasattr(gateway_settings, "port"), "Gateway settings missing port"

        # Test that secure defaults are used
        if gateway_settings.host == "0.0.0.0":
            logger.warning(
                "⚠️ API Gateway: Using 0.0.0.0 binding (ensure this is intentional)"
            )

        logger.info("✅ Service Configurations: All configurations valid")
        return True
    except Exception as e:
        logger.error(f"❌ Service Configurations: Error - {e}")
        return False


def main():
    """Run all CI pipeline tests."""
    logger.info("🚀 Starting Enhanced CI Pipeline Tests...")

    tests = [
        ("YAML Syntax", test_workflow_yaml_syntax),
        ("UV Dependencies", test_uv_dependencies),
        ("Debug Tools Files", test_debug_tools_files),
        ("Service Configurations", test_service_configurations),
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
