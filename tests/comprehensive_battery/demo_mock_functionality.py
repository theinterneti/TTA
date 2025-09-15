#!/usr/bin/env python3
"""
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

from tests.comprehensive_battery.comprehensive_test_battery import ComprehensiveTestBattery
from tests.comprehensive_battery.mocks.mock_services import MockServiceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demonstrate_mock_functionality():
    """Demonstrate the mock functionality of the test battery."""
    
    print("=" * 80)
    print("TTA COMPREHENSIVE TEST BATTERY - MOCK FUNCTIONALITY DEMO")
    print("=" * 80)
    print()
    
    # Initialize test battery
    logger.info("🚀 Initializing Comprehensive Test Battery...")
    test_battery = ComprehensiveTestBattery(
        config_path="tests/comprehensive_battery/config/comprehensive_test_config.yaml",
        max_concurrent_tests=2,
        test_timeout_seconds=30
    )
    
    try:
        # Initialize the test battery (this will trigger mock fallback for unavailable services)
        logger.info("🔧 Attempting to initialize database connections...")
        initialization_success = await test_battery.initialize()
        
        if not initialization_success:
            logger.error("❌ Failed to initialize test battery")
            return False
        
        print()
        print("=" * 80)
        print("SERVICE STATUS REPORT")
        print("=" * 80)
        
        # Get mock service status
        mock_summary = test_battery.mock_service_manager.get_mock_summary()
        
        print(f"🎭 Mock Mode: {'ENABLED' if mock_summary['mock_mode'] else 'DISABLED'}")
        print()
        
        print("📊 Service Status:")
        for service_name, service_status in mock_summary['services'].items():
            status_icon = "✅" if service_status['real'] else "🎭"
            status_text = "REAL" if service_status['real'] else "MOCK"
            print(f"  {status_icon} {service_name.upper()}: {status_text}")
            
            if service_status['error']:
                print(f"    └─ Error: {service_status['error']}")
        
        print()
        print("💡 Recommendations:")
        for recommendation in mock_summary['recommendations']:
            print(f"  • {recommendation}")
        
        print()
        print("=" * 80)
        print("MOCK DATABASE OPERATIONS DEMO")
        print("=" * 80)
        
        # Demonstrate mock Neo4j operations
        logger.info("🎭 Demonstrating mock Neo4j operations...")
        
        async with test_battery.neo4j_driver.session() as session:
            # Create a test user
            result = await session.run(
                "CREATE (u:User {name: $name, created_at: $created_at}) RETURN u",
                name="demo_user", created_at=datetime.utcnow().isoformat()
            )
            user_record = await result.single()
            print(f"  ✅ Created user: {user_record.data()}")
            
            # Query users
            result = await session.run("MATCH (u:User) RETURN u.name as name, u.created_at as created_at")
            users = await result.data()
            print(f"  📋 Found {len(users)} users in mock database")
            for user in users:
                # Handle mock data structure
                name = user.get('name', 'Unknown')
                created_at = user.get('created_at', 'Unknown')
                print(f"    - {name} (created: {created_at})")
        
        # Demonstrate mock Redis operations
        logger.info("🎭 Demonstrating Redis operations (real or mock)...")
        
        # Set some test data
        await test_battery.redis_client.set("demo:session:123", "active", ex=300)

        # Use mapping parameter for hset
        user_data = {
            "username": "test_user",
            "last_active": datetime.utcnow().isoformat(),
            "session_count": "5"
        }
        await test_battery.redis_client.hset("demo:user:456", mapping=user_data)
        
        # Retrieve data
        session_status = await test_battery.redis_client.get("demo:session:123")
        user_data = await test_battery.redis_client.hgetall("demo:user:456")
        
        print(f"  ✅ Session status: {session_status}")
        print(f"  📋 User data: {user_data}")
        
        print()
        print("=" * 80)
        print("TEST FRAMEWORK CAPABILITIES")
        print("=" * 80)
        
        # Demonstrate test data generation
        logger.info("🎲 Demonstrating test data generation...")
        
        if test_battery.test_data_generator:
            # Generate test users
            test_users = await test_battery.test_data_generator.generate_test_users(count=3)
            print(f"  👥 Generated {len(test_users)} test user profiles:")
            for user in test_users:
                prefs = user.preferences.get('genres', ['unknown']) if isinstance(user.preferences, dict) else ['unknown']
                print(f"    - {user.username} ({user.gaming_experience}, prefers: {', '.join(prefs)})")

            # Generate test scenarios
            test_scenarios = await test_battery.test_data_generator.generate_story_scenarios(count=2)
            print(f"  📚 Generated {len(test_scenarios)} story scenarios:")
            for scenario in test_scenarios:
                genre = scenario.test_data.get('genre', 'unknown') if hasattr(scenario, 'test_data') else 'unknown'
                complexity = scenario.test_data.get('complexity', 'medium') if hasattr(scenario, 'test_data') else 'medium'
                print(f"    - {scenario.name}: {genre} ({complexity} complexity)")
        
        print()
        print("=" * 80)
        print("MOCK FUNCTIONALITY SUMMARY")
        print("=" * 80)
        
        print("✅ DEMONSTRATED CAPABILITIES:")
        print("  • Automatic service availability detection")
        print("  • Graceful fallback to mock implementations")
        print("  • Mixed real/mock environment operation")
        print("  • Detailed status reporting and recommendations")
        print("  • Mock database operations (Neo4j)")
        print("  • Real/mock Redis operations")
        print("  • Test data generation")
        print("  • Comprehensive logging and error handling")
        
        print()
        print("🎯 BENEFITS:")
        print("  • Tests can run without full infrastructure setup")
        print("  • Development and CI/CD environments supported")
        print("  • Framework robustness demonstrated")
        print("  • Easy transition between mock and real services")
        print("  • Comprehensive validation of test framework logic")
        
        print()
        print("=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 80)
        
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
