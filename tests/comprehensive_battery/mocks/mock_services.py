"""

# Logseq: [[TTA.dev/Tests/Comprehensive_battery/Mocks/Mock_services]]
Mock service manager for coordinating mock implementations.

Provides centralized management of mock services and automatic fallback
when real services are unavailable.
"""

import logging
from typing import Any

from .mock_neo4j import create_mock_driver
from .mock_redis import create_mock_redis_client

logger = logging.getLogger(__name__)


class MockServiceManager:
    """
    Manages mock services and provides fallback mechanisms.

    Automatically detects when real services are unavailable and
    provides mock implementations with appropriate logging.
    """

    def __init__(self):
        self.mock_mode = False
        self.services_status: dict[str, dict[str, Any]] = {
            "neo4j": {"available": False, "mock": False, "client": None},
            "redis": {"available": False, "mock": False, "client": None},
        }

    async def get_neo4j_driver(self, uri: str, auth: tuple | None = None):
        """Get Neo4j driver with automatic fallback to mock."""
        try:
            # Try to import and create real driver
            from neo4j import AsyncGraphDatabase

            driver = AsyncGraphDatabase.driver(uri, auth=auth)
            await driver.verify_connectivity()

            self.services_status["neo4j"] = {
                "available": True,
                "mock": False,
                "client": driver,
            }

            logger.info("✅ Using real Neo4j driver")
            return driver

        except Exception as e:
            logger.warning(f"❌ Neo4j not available ({e}), using mock implementation")

            mock_driver = create_mock_driver(uri, auth)

            self.services_status["neo4j"] = {
                "available": False,
                "mock": True,
                "client": mock_driver,
                "error": str(e),
            }

            self.mock_mode = True
            return mock_driver

    async def get_redis_client(self, url: str = "redis://localhost:6379", **kwargs):
        """Get Redis client with automatic fallback to mock."""
        try:
            # Try to import and create real client
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, **kwargs)
            await client.ping()

            self.services_status["redis"] = {
                "available": True,
                "mock": False,
                "client": client,
            }

            logger.info("✅ Using real Redis client")
            return client

        except Exception as e:
            logger.warning(f"❌ Redis not available ({e}), using mock implementation")

            mock_client = create_mock_redis_client(url, **kwargs)

            self.services_status["redis"] = {
                "available": False,
                "mock": True,
                "client": mock_client,
                "error": str(e),
            }

            self.mock_mode = True
            return mock_client

    def is_mock_mode(self) -> bool:
        """Check if running in mock mode."""
        return self.mock_mode

    def get_services_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all services."""
        return self.services_status.copy()

    def get_mock_summary(self) -> dict[str, Any]:
        """Get summary of mock usage."""
        neo4j_status = self.services_status["neo4j"]
        redis_status = self.services_status["redis"]

        return {
            "mock_mode": self.mock_mode,
            "services": {
                "neo4j": {
                    "real": neo4j_status["available"],
                    "mock": neo4j_status["mock"],
                    "error": neo4j_status.get("error"),
                },
                "redis": {
                    "real": redis_status["available"],
                    "mock": redis_status["mock"],
                    "error": redis_status.get("error"),
                },
            },
            "recommendations": self._get_recommendations(),
        }

    def _get_recommendations(self) -> list:
        """Get recommendations based on service status."""
        recommendations = []

        if self.services_status["neo4j"]["mock"]:
            recommendations.append(
                "Neo4j is using mock implementation. For full testing, ensure Neo4j is running with proper authentication."
            )

        if self.services_status["redis"]["mock"]:
            recommendations.append(
                "Redis is using mock implementation. For full testing, ensure Redis server is running and accessible."
            )

        if self.mock_mode:
            recommendations.append(
                "Running in mock mode. Test results demonstrate framework functionality but may not reflect real system behavior."
            )
        else:
            recommendations.append(
                "All services are available. Test results reflect actual system behavior."
            )

        return recommendations

    async def cleanup(self):
        """Clean up all service connections."""
        for service_name, service_info in self.services_status.items():
            if service_info["client"]:
                try:
                    await service_info["client"].close()
                    logger.debug(f"Closed {service_name} client")
                except Exception as e:
                    logger.warning(f"Error closing {service_name} client: {e}")

        logger.info("Mock service manager cleanup completed")


# Global instance for easy access
mock_service_manager = MockServiceManager()
