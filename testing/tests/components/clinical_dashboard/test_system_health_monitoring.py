"""
Tests for System Health Monitoring Integration

This module tests the comprehensive system health monitoring functionality
including real-time health checks, trend analysis, alert generation, and
health aggregation across all therapeutic systems.
"""

import asyncio
from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from src.components.clinical_dashboard.clinical_dashboard_manager import (
    AlertSeverity,
    ClinicalDashboardManager,
)


class MockTherapeuticSystem:
    """Mock therapeutic system for testing health monitoring."""

    def __init__(self, name: str, status: str = "healthy"):
        self.name = name
        self.status = status
        self.health_check_count = 0
        self.should_fail = False

    async def health_check(self):
        """Mock health check method."""
        self.health_check_count += 1

        if self.should_fail:
            raise Exception(f"Health check failed for {self.name}")

        return {
            "status": self.status,
            "system": self.name,
            "metrics": {
                "requests_processed": 1000,
                "average_response_time": 50.0,
                "error_rate": 0.1,
            },
            "uptime": "99.9%",
        }


class TestSystemHealthMonitoring:
    """Test System Health Monitoring Integration functionality."""

    @pytest_asyncio.fixture
    async def dashboard_with_systems(self):
        """Create dashboard manager with mock therapeutic systems."""
        manager = ClinicalDashboardManager()

        # Create mock therapeutic systems
        manager.consequence_system = MockTherapeuticSystem("consequence_system")
        manager.emotional_safety_system = MockTherapeuticSystem("emotional_safety_system")
        manager.adaptive_difficulty_engine = MockTherapeuticSystem("adaptive_difficulty_engine")
        manager.character_development_system = MockTherapeuticSystem("character_development_system")
        manager.therapeutic_integration_system = MockTherapeuticSystem("therapeutic_integration_system")
        manager.gameplay_loop_controller = MockTherapeuticSystem("gameplay_loop_controller")
        manager.replayability_system = MockTherapeuticSystem("replayability_system")
        manager.collaborative_system = MockTherapeuticSystem("collaborative_system")
        manager.error_recovery_manager = MockTherapeuticSystem("error_recovery_manager")

        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_comprehensive_system_health_all_healthy(self, dashboard_with_systems):
        """Test comprehensive system health when all systems are healthy."""
        manager = dashboard_with_systems

        # Get comprehensive health status
        health_status = await manager.get_comprehensive_system_health()

        # Verify overall health
        assert health_status["overall_status"] == "healthy"
        assert health_status["overall_health_percentage"] == 100.0

        # Verify systems summary
        summary = health_status["systems_summary"]
        assert summary["total"] == 9
        assert summary["healthy"] == 9
        assert summary["degraded"] == 0
        assert summary["unhealthy"] == 0

        # Verify individual system health
        systems_health = health_status["systems_health"]
        assert len(systems_health) == 9

        for system_name in systems_health:
            system_health = systems_health[system_name]
            assert system_health["status"] == "healthy"
            assert "timestamp" in system_health
            assert "system_name" in system_health

    @pytest.mark.asyncio
    async def test_comprehensive_system_health_mixed_status(self, dashboard_with_systems):
        """Test comprehensive system health with mixed system statuses."""
        manager = dashboard_with_systems

        # Set different statuses for systems
        manager.consequence_system.status = "healthy"
        manager.emotional_safety_system.status = "degraded"
        manager.adaptive_difficulty_engine.status = "unhealthy"
        manager.character_development_system.status = "healthy"
        manager.therapeutic_integration_system.status = "healthy"
        manager.gameplay_loop_controller.status = "degraded"
        manager.replayability_system.status = "healthy"
        manager.collaborative_system.status = "healthy"
        manager.error_recovery_manager.status = "healthy"

        # Get comprehensive health status
        health_status = await manager.get_comprehensive_system_health()

        # Verify overall health (6 healthy + 2 degraded + 1 unhealthy = 7.0/9 = 77.8%)
        assert health_status["overall_status"] == "degraded"  # 70-90% range
        assert 75.0 <= health_status["overall_health_percentage"] <= 80.0

        # Verify systems summary
        summary = health_status["systems_summary"]
        assert summary["total"] == 9
        assert summary["healthy"] == 6
        assert summary["degraded"] == 2
        assert summary["unhealthy"] == 1

    @pytest.mark.asyncio
    async def test_system_health_caching(self, dashboard_with_systems):
        """Test system health caching mechanism."""
        manager = dashboard_with_systems

        # First call should trigger health checks
        health_status1 = await manager.get_comprehensive_system_health()
        initial_check_counts = {
            name: system.health_check_count
            for name, system in [
                ("consequence_system", manager.consequence_system),
                ("emotional_safety_system", manager.emotional_safety_system),
            ]
        }

        # Second call within cache interval should use cached data
        health_status2 = await manager.get_comprehensive_system_health()

        # Verify health check counts haven't increased (using cache)
        for name, system in [
            ("consequence_system", manager.consequence_system),
            ("emotional_safety_system", manager.emotional_safety_system),
        ]:
            assert system.health_check_count == initial_check_counts[name]

        # Verify results are consistent
        assert health_status1["overall_status"] == health_status2["overall_status"]
        assert health_status1["overall_health_percentage"] == health_status2["overall_health_percentage"]

    @pytest.mark.asyncio
    async def test_health_alert_generation(self, dashboard_with_systems):
        """Test health alert generation for unhealthy systems."""
        manager = dashboard_with_systems

        # Set some systems to unhealthy status
        manager.emotional_safety_system.status = "unhealthy"
        manager.adaptive_difficulty_engine.status = "degraded"

        # Clear any existing alerts
        manager.active_alerts.clear()

        # Trigger health check
        await manager.get_comprehensive_system_health()

        # Verify alerts were generated
        assert len(manager.active_alerts) >= 2  # At least one for unhealthy, one for degraded

        # Check for critical alert (unhealthy system)
        critical_alerts = [
            alert for alert in manager.active_alerts.values()
            if alert.severity == AlertSeverity.CRITICAL and "unhealthy" in alert.message
        ]
        assert len(critical_alerts) >= 1

        # Check for medium alert (degraded system)
        medium_alerts = [
            alert for alert in manager.active_alerts.values()
            if alert.severity == AlertSeverity.MEDIUM and "degraded" in alert.message
        ]
        assert len(medium_alerts) >= 1

    @pytest.mark.asyncio
    async def test_system_health_trends(self, dashboard_with_systems):
        """Test system health trend analysis."""
        manager = dashboard_with_systems
        system_name = "consequence_system"

        # Simulate health history with improving trend
        history_entries = []
        for i in range(10):
            timestamp = datetime.utcnow() - timedelta(hours=i)
            status = "healthy" if i < 3 else "degraded" if i < 7 else "unhealthy"

            entry = {
                "status": status,
                "timestamp": timestamp.isoformat(),
                "response_time_ms": 50.0 + i * 5,
                "system_name": system_name,
            }
            history_entries.append(entry)

        # Add history in reverse order (oldest first)
        manager.system_health_history[system_name] = list(reversed(history_entries))

        # Get health trends
        trends = await manager.get_system_health_trends(system_name, hours=24)

        # Verify trend data
        assert trends["system_name"] == system_name
        assert trends["timeframe_hours"] == 24
        assert trends["total_health_checks"] == 10
        assert "availability_percentage" in trends
        assert "status_distribution" in trends
        assert "trend_direction" in trends
        assert trends["trend_direction"] in ["improving", "declining", "stable", "insufficient_data"]

    @pytest.mark.asyncio
    async def test_health_check_error_handling(self, dashboard_with_systems):
        """Test error handling during health checks."""
        manager = dashboard_with_systems

        # Make some systems fail health checks
        manager.consequence_system.should_fail = True
        manager.emotional_safety_system.should_fail = True

        # Get health status (should handle errors gracefully)
        health_status = await manager.get_comprehensive_system_health()

        # Verify overall status reflects errors
        assert health_status["overall_status"] in ["degraded", "critical"]

        # Verify error systems are marked as error status
        systems_health = health_status["systems_health"]
        assert systems_health["consequence_system"]["status"] == "error"
        assert systems_health["emotional_safety_system"]["status"] == "error"
        assert "error" in systems_health["consequence_system"]
        assert "error" in systems_health["emotional_safety_system"]

    @pytest.mark.asyncio
    async def test_health_monitoring_performance(self, dashboard_with_systems):
        """Test health monitoring performance benchmarks."""
        import time

        manager = dashboard_with_systems

        # Test comprehensive health check performance
        start_time = time.perf_counter()
        health_status = await manager.get_comprehensive_system_health()
        health_check_time = (time.perf_counter() - start_time) * 1000

        assert health_check_time < 500.0  # Should complete in under 500ms
        assert health_status["overall_status"] in ["healthy", "degraded", "critical"]

        # Test health trends performance
        system_name = "consequence_system"

        # Add some history data
        for i in range(50):
            entry = {
                "status": "healthy",
                "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                "response_time_ms": 50.0,
                "system_name": system_name,
            }
            manager.system_health_history[system_name].append(entry)

        start_time = time.perf_counter()
        trends = await manager.get_system_health_trends(system_name)
        trends_time = (time.perf_counter() - start_time) * 1000

        assert trends_time < 100.0  # Should complete in under 100ms
        assert "trend_direction" in trends

    @pytest.mark.asyncio
    async def test_health_cache_expiration(self, dashboard_with_systems):
        """Test health cache expiration and refresh."""
        manager = dashboard_with_systems

        # Set short cache interval for testing
        original_interval = manager.health_check_interval
        manager.health_check_interval = 0.1  # 100ms

        try:
            # First health check
            await manager.get_comprehensive_system_health()
            initial_check_count = manager.consequence_system.health_check_count

            # Wait for cache to expire
            await asyncio.sleep(0.2)

            # Second health check should refresh cache
            await manager.get_comprehensive_system_health()
            final_check_count = manager.consequence_system.health_check_count

            # Verify health checks were called again
            assert final_check_count > initial_check_count

        finally:
            # Restore original interval
            manager.health_check_interval = original_interval

    @pytest.mark.asyncio
    async def test_system_not_available_handling(self, dashboard_with_systems):
        """Test handling of systems that are not available."""
        manager = dashboard_with_systems

        # Set some systems to None (not available)
        manager.consequence_system = None
        manager.emotional_safety_system = None

        # Get health status
        health_status = await manager.get_comprehensive_system_health()

        # Verify not available systems are handled
        systems_health = health_status["systems_health"]
        assert systems_health["consequence_system"]["status"] == "not_available"
        assert systems_health["emotional_safety_system"]["status"] == "not_available"

        # Verify overall health reflects unavailable systems
        assert health_status["overall_health_percentage"] < 100.0
        assert health_status["systems_summary"]["unhealthy"] >= 2
