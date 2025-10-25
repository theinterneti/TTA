#!/usr/bin/env python3
"""
Development Environment Setup Script

This script sets up a complete development environment for testing
the TTA Core Gameplay Loop integration.
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration import TTAConfig, TTAOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are available."""
    logger.info("Checking dependencies...")

    dependencies = {
        "neo4j": "Neo4j database (required for gameplay loop)",
        "redis-server": "Redis cache (required for session management)",
        "python3": "Python 3.8+ (required for TTA system)",
    }

    missing = []
    for dep, description in dependencies.items():
        try:
            result = subprocess.run(
                ["which", dep], check=False, capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info(f"✓ {dep} found: {result.stdout.strip()}")
            else:
                missing.append((dep, description))
        except Exception as e:
            missing.append((dep, f"{description} - Error: {e}"))

    if missing:
        logger.warning("Missing dependencies:")
        for dep, desc in missing:
            logger.warning(f"  ✗ {dep}: {desc}")
        return False

    logger.info("✓ All dependencies available")
    return True


def setup_databases():
    """Setup and start required databases."""
    logger.info("Setting up databases...")

    # Start Neo4j (if available)
    try:
        result = subprocess.run(
            ["neo4j", "status"], check=False, capture_output=True, text=True
        )
        if "Neo4j is running" in result.stdout:
            logger.info("✓ Neo4j is already running")
        else:
            logger.info("Starting Neo4j...")
            subprocess.run(["neo4j", "start"], check=True)
            logger.info("✓ Neo4j started")
    except subprocess.CalledProcessError:
        logger.warning("⚠ Could not start Neo4j - may need manual setup")
    except FileNotFoundError:
        logger.warning("⚠ Neo4j not found - install Neo4j for full functionality")

    # Start Redis (if available)
    try:
        result = subprocess.run(
            ["redis-cli", "ping"], check=False, capture_output=True, text=True
        )
        if "PONG" in result.stdout:
            logger.info("✓ Redis is already running")
        else:
            logger.info("Starting Redis...")
            subprocess.Popen(["redis-server", "--daemonize", "yes"])
            logger.info("✓ Redis started")
    except FileNotFoundError:
        logger.warning("⚠ Redis not found - install Redis for full functionality")


def validate_configuration():
    """Validate TTA configuration for gameplay loop."""
    logger.info("Validating configuration...")

    try:
        config = TTAConfig()

        # Check core gameplay loop configuration
        if not config.get("core_gameplay_loop.enabled", False):
            logger.warning("⚠ Core Gameplay Loop is disabled")
            logger.info("  Enable with: core_gameplay_loop.enabled: true")
        else:
            logger.info("✓ Core Gameplay Loop enabled")

        # Check Neo4j configuration
        if not config.get("tta.prototype.components.neo4j.enabled", False):
            logger.warning("⚠ Neo4j component is disabled")
        else:
            logger.info("✓ Neo4j component enabled")

        # Check other important settings
        max_sessions = config.get("core_gameplay_loop.max_concurrent_sessions", 100)
        timeout = config.get("core_gameplay_loop.session_timeout_minutes", 30)

        logger.info(f"✓ Max concurrent sessions: {max_sessions}")
        logger.info(f"✓ Session timeout: {timeout} minutes")

        return True

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def run_integration_tests():
    """Run integration tests to validate the system."""
    logger.info("Running integration tests...")

    test_commands = [
        [
            "python3",
            "-m",
            "pytest",
            "tests/integration/test_gameplay_loop_integration.py",
            "-v",
        ],
        ["python3", "-m", "pytest", "tests/integration/test_gameplay_api.py", "-v"],
    ]

    for cmd in test_commands:
        try:
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                logger.info("✓ Tests passed")
            else:
                logger.warning(f"⚠ Tests failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.warning("⚠ Tests timed out")
        except FileNotFoundError:
            logger.warning("⚠ pytest not found - install with: pip install pytest")


async def test_system_startup():
    """Test system startup and component initialization."""
    logger.info("Testing system startup...")

    try:
        orchestrator = TTAOrchestrator()

        # Test component discovery
        logger.info(f"Discovered {len(orchestrator.components)} components")

        # Check if gameplay loop component is available
        if "core_gameplay_loop" in orchestrator.components:
            logger.info("✓ GameplayLoopComponent discovered")

            # Test component startup
            if orchestrator.start_component("core_gameplay_loop"):
                logger.info("✓ GameplayLoopComponent started successfully")

                # Get component status
                component = orchestrator.components["core_gameplay_loop"]
                status = component.get_status_info()
                logger.info(f"Component status: {status}")

                # Stop component
                orchestrator.stop_component("core_gameplay_loop")
                logger.info("✓ GameplayLoopComponent stopped successfully")
            else:
                logger.warning("⚠ GameplayLoopComponent failed to start")
        else:
            logger.warning("⚠ GameplayLoopComponent not discovered")

        return True

    except Exception as e:
        logger.error(f"System startup test failed: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("=" * 60)
    logger.info("TTA CORE GAMEPLAY LOOP - DEVELOPMENT SETUP")
    logger.info("=" * 60)

    # Step 1: Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed. Please install missing dependencies.")
        return False

    # Step 2: Setup databases
    setup_databases()

    # Step 3: Validate configuration
    if not validate_configuration():
        logger.error("Configuration validation failed.")
        return False

    # Step 4: Test system startup
    startup_success = asyncio.run(test_system_startup())
    if not startup_success:
        logger.error("System startup test failed.")
        return False

    # Step 5: Run integration tests
    run_integration_tests()

    logger.info("=" * 60)
    logger.info("DEVELOPMENT SETUP COMPLETE")
    logger.info("=" * 60)
    logger.info("Your development environment is ready!")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Start the system: python3 scripts/start_with_gameplay.py")
    logger.info(
        "2. Test API endpoints: curl http://localhost:8000/api/v1/gameplay/health"
    )
    logger.info("3. View API docs: http://localhost:8000/docs")
    logger.info("4. Run tests: python3 -m pytest tests/integration/ -v")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
