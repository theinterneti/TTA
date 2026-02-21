#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Tests/Comprehensive_battery/Demo_mock_functionality]]
Demonstration of TTA Comprehensive Test Battery Mock Functionality

This script demonstrates the comprehensive test battery's ability to:
1. Automatically detect unavailable services
2. Fall back to mock implementations gracefully
3. Continue testing with mixed real/mock environments
4. Provide detailed status reporting and recommendations
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.comprehensive_battery.comprehensive_test_battery import (
    ComprehensiveTestBattery,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def demonstrate_mock_functionality():
    """Demonstrate the mock functionality of the test battery."""

    # Initialize test battery
    logger.info("🚀 Initializing Comprehensive Test Battery...")
    test_battery = ComprehensiveTestBattery(
        config_path="tests/comprehensive_battery/config/comprehensive_test_config.yaml",
        max_concurrent_tests=2,
        test_timeout_seconds=30,
    )

    try:
        # Initialize the test battery (this will trigger mock fallback for unavailable services)
        logger.info("🔧 Attempting to initialize database connections...")
        initialization_success = await test_battery.initialize()

        if not initialization_success:
            logger.error("❌ Failed to initialize test battery")
            return False

        # Get mock service status
        mock_summary = test_battery.mock_service_manager.get_mock_summary()

        for service_status in mock_summary["services"].values():
            "✅" if service_status["real"] else "🎭"
            "REAL" if service_status["real"] else "MOCK"

            if service_status["error"]:
                pass

        for _recommendation in mock_summary["recommendations"]:
            pass

        # Demonstrate mock Neo4j operations
        logger.info("🎭 Demonstrating mock Neo4j operations...")

        async with test_battery.neo4j_driver.session() as session:
            # Create a test user
            result = await session.run(
                "CREATE (u:User {name: $name, created_at: $created_at}) RETURN u",
                name="demo_user",
                created_at=datetime.utcnow().isoformat(),
            )
            await result.single()

            # Query users
            result = await session.run(
                "MATCH (u:User) RETURN u.name as name, u.created_at as created_at"
            )
            users = await result.data()
            for user in users:
                # Handle mock data structure
                user.get("name", "Unknown")
                user.get("created_at", "Unknown")

        # Demonstrate mock Redis operations
        logger.info("🎭 Demonstrating Redis operations (real or mock)...")

        # Set some test data
        await test_battery.redis_client.set("demo:session:123", "active", ex=300)

        # Use mapping parameter for hset
        user_data = {
            "username": "test_user",
            "last_active": datetime.utcnow().isoformat(),
            "session_count": "5",
        }
        await test_battery.redis_client.hset("demo:user:456", mapping=user_data)

        # Retrieve data
        await test_battery.redis_client.get("demo:session:123")
        user_data = await test_battery.redis_client.hgetall("demo:user:456")

        # Demonstrate test data generation
        logger.info("🎲 Demonstrating test data generation...")

        if test_battery.test_data_generator:
            # Generate test users
            test_users = await test_battery.test_data_generator.generate_test_users(
                count=3
            )
            for user in test_users:
                (
                    user.preferences.get("genres", ["unknown"])
                    if isinstance(user.preferences, dict)
                    else ["unknown"]
                )

            # Generate test scenarios
            test_scenarios = (
                await test_battery.test_data_generator.generate_story_scenarios(count=2)
            )
            for scenario in test_scenarios:
                (
                    scenario.test_data.get("genre", "unknown")
                    if hasattr(scenario, "test_data")
                    else "unknown"
                )
                (
                    scenario.test_data.get("complexity", "medium")
                    if hasattr(scenario, "test_data")
                    else "medium"
                )

        return True

    except Exception as e:
        logger.error(f"❌ Demo failed: {e}", exc_info=True)
        return False

    finally:
        # Cleanup
        logger.info("🧹 Cleaning up resources...")
        await test_battery.cleanup()


async def main():
    """Main entry point."""
    try:
        success = await demonstrate_mock_functionality()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
