#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Start_with_gameplay]]
TTA Startup Script with Gameplay Loop Integration

This script demonstrates how to start the TTA system with the integrated
Core Gameplay Loop functionality, ensuring proper initialization order
and dependency management.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integration.gameplay_loop_integration import GameplayLoopIntegration
from src.orchestration import TTAConfig, TTAOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """
    Main startup function that demonstrates the integrated TTA system.
    """
    logger.info("Starting TTA system with Gameplay Loop integration...")

    try:
        # Create orchestrator with default configuration
        orchestrator = TTAOrchestrator()

        # Display initial configuration
        logger.info("Configuration loaded:")
        logger.info(
            f"  - Core Gameplay Loop enabled: {orchestrator.config.get('core_gameplay_loop.enabled', False)}"
        )
        logger.info(
            f"  - Neo4j enabled: {orchestrator.config.get('tta.prototype.components.neo4j.enabled', False)}"
        )
        logger.info(
            f"  - Agent Orchestration enabled: {orchestrator.config.get('agent_orchestration.enabled', False)}"
        )

        # Start core infrastructure components first
        logger.info("Starting core infrastructure components...")

        # Start Neo4j (required for gameplay loop)
        if orchestrator.config.get("tta.prototype.components.neo4j.enabled", False):
            if orchestrator.start_component("tta.prototype_neo4j"):
                logger.info("✓ Neo4j component started successfully")
            else:
                logger.error("✗ Failed to start Neo4j component")
                return False

        # Start Agent Orchestration (optional but recommended)
        if orchestrator.config.get("agent_orchestration.enabled", False):
            if orchestrator.start_component("agent_orchestration"):
                logger.info("✓ Agent Orchestration component started successfully")
            else:
                logger.warning(
                    "⚠ Agent Orchestration component failed to start (optional)"
                )

        # Start Gameplay Loop component
        if orchestrator.config.get("core_gameplay_loop.enabled", False):
            if orchestrator.start_component("core_gameplay_loop"):
                logger.info("✓ Core Gameplay Loop component started successfully")

                # Get the gameplay component for demonstration
                gameplay_component = orchestrator.components.get("core_gameplay_loop")
                if gameplay_component:
                    # Display component status
                    status_info = gameplay_component.get_status_info()
                    logger.info(f"Gameplay Loop Status: {status_info}")

                    # Demonstrate integration layer
                    try:
                        integration = GameplayLoopIntegration(
                            gameplay_component=gameplay_component,
                            agent_orchestration=None,  # Would be set if available
                            safety_service=None,  # Would be set if available
                        )

                        integration_status = integration.get_integration_status()
                        logger.info(f"Integration Status: {integration_status}")

                    except Exception as e:
                        logger.warning(f"Integration layer initialization failed: {e}")

            else:
                logger.error("✗ Failed to start Core Gameplay Loop component")
                return False
        else:
            logger.warning("⚠ Core Gameplay Loop is disabled in configuration")

        # Start Player Experience API (includes gameplay endpoints)
        if orchestrator.config.get("player_experience.enabled", False):
            if orchestrator.start_component("player_experience"):
                logger.info("✓ Player Experience API started successfully")
                logger.info("  - Gameplay endpoints available at /api/v1/gameplay/")
            else:
                logger.warning("⚠ Player Experience API failed to start")

        # Display overall system status
        logger.info("\n" + "=" * 60)
        logger.info("TTA SYSTEM STATUS")
        logger.info("=" * 60)
        orchestrator.display_status()

        # Display available endpoints
        logger.info("\n" + "=" * 60)
        logger.info("AVAILABLE ENDPOINTS")
        logger.info("=" * 60)

        if orchestrator.config.get("player_experience.enabled", False):
            base_url = f"http://localhost:{orchestrator.config.get('player_experience.api.port', 8000)}"
            logger.info(f"Player Experience API: {base_url}")
            logger.info(f"  - Authentication: {base_url}/api/v1/auth/")
            logger.info(f"  - Gameplay Sessions: {base_url}/api/v1/gameplay/sessions")
            logger.info(
                f"  - Choice Processing: {base_url}/api/v1/gameplay/sessions/{{session_id}}/choices"
            )
            logger.info(f"  - Health Check: {base_url}/api/v1/gameplay/health")
            logger.info(f"  - API Documentation: {base_url}/docs")

        logger.info("\n" + "=" * 60)
        logger.info("INTEGRATION COMPLETE")
        logger.info("=" * 60)
        logger.info(
            "The TTA system is now running with Core Gameplay Loop integration."
        )
        logger.info("All components are properly initialized and ready for use.")

        # Keep the system running
        logger.info("\nPress Ctrl+C to stop the system...")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nShutting down TTA system...")

            # Stop all components gracefully
            if orchestrator.stop_all():
                logger.info("✓ All components stopped successfully")
            else:
                logger.error("✗ Some components failed to stop properly")

        return True

    except Exception as e:
        logger.error(f"Failed to start TTA system: {e}")
        return False


def validate_configuration():
    """
    Validate that the configuration is properly set up for gameplay loop integration.
    """
    logger.info("Validating configuration for gameplay loop integration...")

    try:
        config = TTAConfig()

        # Check required configuration
        required_configs = [
            "core_gameplay_loop.enabled",
            "tta.prototype.components.neo4j.enabled",
            "tta.prototype.components.neo4j.port",
            "tta.prototype.components.neo4j.username",
            "tta.prototype.components.neo4j.password",
        ]

        missing_configs = []
        for config_key in required_configs:
            if config.get(config_key) is None:
                missing_configs.append(config_key)

        if missing_configs:
            logger.error("Missing required configuration:")
            for config_key in missing_configs:
                logger.error(f"  - {config_key}")
            return False

        # Check gameplay loop specific configuration
        if not config.get("core_gameplay_loop.enabled", False):
            logger.error(
                "Core Gameplay Loop is disabled. Set 'core_gameplay_loop.enabled: true' in configuration."
            )
            return False

        if not config.get("tta.prototype.components.neo4j.enabled", False):
            logger.error(
                "Neo4j is disabled. Gameplay Loop requires Neo4j for data persistence."
            )
            return False

        logger.info("✓ Configuration validation passed")
        return True

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


if __name__ == "__main__":
    # Validate configuration first
    if not validate_configuration():
        logger.error(
            "Configuration validation failed. Please check your configuration."
        )
        sys.exit(1)

    # Run the main startup function
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        sys.exit(1)
