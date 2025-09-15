"""
WebSocket performance and scalability tests.

This module tests WebSocket performance under various load conditions,
including concurrent connections, high event throughput, and resource usage.
"""

import asyncio
import json
import time
from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock

import psutil
import pytest

from src.agent_orchestration.realtime.event_publisher import EventPublisher
from src.agent_orchestration.realtime.models import AgentStatus, AgentStatusEvent
from src.agent_orchestration.realtime.websocket_manager import (
    WebSocketConnectionManager,
)


@dataclass
class PerformanceMetrics:
    """Container for performance test metrics."""

    start_time: float
    end_time: float
    total_connections: int
    successful_connections: int
    failed_connections: int
    total_events_sent: int
    total_events_received: int
    peak_memory_mb: float
    peak_cpu_percent: float
    average_response_time_ms: float

    @property
    def duration_seconds(self) -> float:
        return self.end_time - self.start_time

    @property
    def connection_success_rate(self) -> float:
        if self.total_connections == 0:
            return 0.0
        return self.successful_connections / self.total_connections

    @property
    def events_per_second(self) -> float:
        if self.duration_seconds == 0:
            return 0.0
        return self.total_events_sent / self.duration_seconds


@pytest.mark.performance
@pytest.mark.redis
class TestWebSocketPerformance:
    """Test WebSocket performance and scalability."""

    @pytest.fixture
    async def high_capacity_websocket_manager(self, redis_client):
        """Create WebSocket manager configured for high capacity."""
        config_dict = {
            "agent_orchestration.realtime.enabled": True,
            "agent_orchestration.realtime.websocket.enabled": True,
            "agent_orchestration.realtime.websocket.heartbeat_interval": 30.0,  # Longer for performance
            "agent_orchestration.realtime.websocket.connection_timeout": 60.0,
            "agent_orchestration.realtime.websocket.max_connections": 100,  # High limit
            "agent_orchestration.realtime.websocket.auth_required": False,
            "agent_orchestration.realtime.events.enabled": True,
            "agent_orchestration.realtime.events.buffer_size": 1000,
        }

        manager = WebSocketConnectionManager(
            config=config_dict, redis_client=redis_client
        )

        return manager

    @pytest.fixture
    async def event_publisher(self, redis_client):
        """Create event publisher for performance testing."""
        publisher = EventPublisher(
            redis_client=redis_client,
            channel_prefix="perf_test:events",
            enabled=True,
            buffer_size=1000,
        )
        return publisher

    async def create_mock_websocket(self, connection_id: int) -> Mock:
        """Create a mock WebSocket connection for testing."""
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_ws.send_text = AsyncMock()
        mock_ws.receive_text = AsyncMock(
            side_effect=[
                json.dumps({"type": "auth", "user_id": f"perf_user_{connection_id}"}),
                json.dumps({"type": "subscribe", "event_types": ["agent_status"]}),
                asyncio.CancelledError(),  # Keep connection alive until cancelled
            ]
        )
        mock_ws.client = Mock()
        mock_ws.client.host = "127.0.0.1"
        mock_ws.client.port = 12345 + connection_id
        mock_ws.headers = {"user-agent": f"perf-test-client-{connection_id}"}

        return mock_ws

    async def test_concurrent_connection_capacity(
        self, high_capacity_websocket_manager
    ):
        """Test maximum concurrent WebSocket connections."""
        connection_count = 50  # Test with 50 concurrent connections
        connections = []
        tasks = []
        successful_connections = 0
        failed_connections = 0

        start_time = time.time()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        # Create concurrent connections
        for i in range(connection_count):
            mock_ws = await self.create_mock_websocket(i)
            connections.append(mock_ws)

            # Start connection handling
            task = asyncio.create_task(
                high_capacity_websocket_manager.handle_connection(mock_ws)
            )
            tasks.append(task)

        # Let connections establish
        await asyncio.sleep(1.0)

        # Check connection success
        for mock_ws in connections:
            if mock_ws.accept.called:
                successful_connections += 1
            else:
                failed_connections += 1

        # Measure resource usage
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        peak_cpu = psutil.Process().cpu_percent()

        # Get connection stats
        stats = await high_capacity_websocket_manager.get_connection_stats()

        # Cleanup
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        end_time = time.time()

        # Create performance metrics
        metrics = PerformanceMetrics(
            start_time=start_time,
            end_time=end_time,
            total_connections=connection_count,
            successful_connections=successful_connections,
            failed_connections=failed_connections,
            total_events_sent=0,
            total_events_received=0,
            peak_memory_mb=peak_memory,
            peak_cpu_percent=peak_cpu,
            average_response_time_ms=0.0,
        )

        # Assertions
        assert metrics.connection_success_rate >= 0.9  # At least 90% success rate
        assert metrics.peak_memory_mb - initial_memory < 500  # Memory increase < 500MB
        assert (
            stats["active_connections"] >= successful_connections * 0.8
        )  # Most connections active

        print("Concurrent Connection Test Results:")
        print(f"  Total Connections: {metrics.total_connections}")
        print(f"  Successful: {metrics.successful_connections}")
        print(f"  Success Rate: {metrics.connection_success_rate:.2%}")
        print(f"  Memory Usage: {metrics.peak_memory_mb:.1f} MB")
        print(f"  Active Connections: {stats['active_connections']}")

    async def test_high_event_throughput(
        self, high_capacity_websocket_manager, event_publisher
    ):
        """Test high event throughput performance."""
        connection_count = 20
        events_per_connection = 50
        total_events = connection_count * events_per_connection

        connections = []
        tasks = []
        events_received = 0

        # Track received events
        async def count_event(event_data):
            nonlocal events_received
            events_received += 1

        start_time = time.time()

        # Create connections
        for i in range(connection_count):
            mock_ws = await self.create_mock_websocket(i)
            mock_ws.send_json.side_effect = count_event
            connections.append(mock_ws)

            task = asyncio.create_task(
                high_capacity_websocket_manager.handle_connection(mock_ws)
            )
            tasks.append(task)

        # Let connections establish
        await asyncio.sleep(0.5)

        # Publish events rapidly
        event_tasks = []
        for i in range(total_events):
            event = AgentStatusEvent(
                agent_id=f"perf_agent_{i % 10}",
                status=AgentStatus.PROCESSING,
                message=f"Performance test event {i}",
                source="performance_test",
            )

            task = asyncio.create_task(event_publisher.publish_event(event))
            event_tasks.append(task)

        # Wait for all events to be published
        await asyncio.gather(*event_tasks)

        # Wait for events to be received
        await asyncio.sleep(2.0)

        end_time = time.time()

        # Cleanup
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Calculate metrics
        duration = end_time - start_time
        events_per_second = total_events / duration if duration > 0 else 0

        # Assertions
        assert events_per_second > 100  # Should handle at least 100 events/second
        assert (
            event_publisher.events_published >= total_events * 0.9
        )  # At least 90% published

        print("High Throughput Test Results:")
        print(f"  Total Events: {total_events}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Events/Second: {events_per_second:.1f}")
        print(f"  Events Published: {event_publisher.events_published}")
        print(f"  Events Received: {events_received}")

    async def test_connection_churn_performance(self, high_capacity_websocket_manager):
        """Test performance under high connection churn (frequent connect/disconnect)."""
        churn_cycles = 10
        connections_per_cycle = 20
        total_connections = churn_cycles * connections_per_cycle

        successful_connections = 0
        failed_connections = 0

        start_time = time.time()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        for cycle in range(churn_cycles):
            cycle_tasks = []

            # Create connections for this cycle
            for i in range(connections_per_cycle):
                connection_id = cycle * connections_per_cycle + i
                mock_ws = await self.create_mock_websocket(connection_id)

                # Shorter connection duration for churn test
                mock_ws.receive_text = AsyncMock(
                    side_effect=[
                        json.dumps(
                            {"type": "auth", "user_id": f"churn_user_{connection_id}"}
                        ),
                        json.dumps(
                            {"type": "subscribe", "event_types": ["agent_status"]}
                        ),
                        asyncio.sleep(0.1),  # Brief connection
                        asyncio.CancelledError(),
                    ]
                )

                task = asyncio.create_task(
                    high_capacity_websocket_manager.handle_connection(mock_ws)
                )
                cycle_tasks.append((task, mock_ws))

            # Let connections establish and disconnect
            await asyncio.sleep(0.2)

            # Count successful connections
            for task, mock_ws in cycle_tasks:
                if mock_ws.accept.called:
                    successful_connections += 1
                else:
                    failed_connections += 1

                # Cancel remaining tasks
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            # Brief pause between cycles
            await asyncio.sleep(0.1)

        end_time = time.time()
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Calculate metrics
        duration = end_time - start_time
        connections_per_second = total_connections / duration if duration > 0 else 0
        memory_increase = peak_memory - initial_memory

        # Assertions
        assert (
            connections_per_second > 50
        )  # Should handle at least 50 connections/second
        assert memory_increase < 200  # Memory increase should be reasonable
        assert successful_connections / total_connections >= 0.8  # At least 80% success

        print("Connection Churn Test Results:")
        print(f"  Total Connections: {total_connections}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Connections/Second: {connections_per_second:.1f}")
        print(f"  Success Rate: {successful_connections / total_connections:.2%}")
        print(f"  Memory Increase: {memory_increase:.1f} MB")

    async def test_large_message_handling(self, high_capacity_websocket_manager):
        """Test performance with large WebSocket messages."""
        connection_count = 10
        large_message_size = 10000  # 10KB messages
        messages_per_connection = 10

        connections = []
        tasks = []
        messages_received = 0
        total_bytes_sent = 0

        # Create large message content
        large_content = "x" * large_message_size

        async def count_large_message(event_data):
            nonlocal messages_received, total_bytes_sent
            messages_received += 1
            if isinstance(event_data, str):
                total_bytes_sent += len(event_data.encode("utf-8"))
            else:
                total_bytes_sent += len(json.dumps(event_data).encode("utf-8"))

        start_time = time.time()

        # Create connections
        for i in range(connection_count):
            mock_ws = await self.create_mock_websocket(i)
            mock_ws.send_json.side_effect = count_large_message
            connections.append(mock_ws)

            task = asyncio.create_task(
                high_capacity_websocket_manager.handle_connection(mock_ws)
            )
            tasks.append(task)

        await asyncio.sleep(0.5)  # Let connections establish

        # Send large messages
        for _ in range(messages_per_connection):
            large_event = AgentStatusEvent(
                agent_id="large_message_agent",
                status=AgentStatus.PROCESSING,
                message=large_content,  # Large message content
                source="performance_test",
            )

            await high_capacity_websocket_manager.broadcast_event(large_event)
            await asyncio.sleep(0.1)  # Brief pause between messages

        await asyncio.sleep(1.0)  # Wait for message processing

        end_time = time.time()

        # Cleanup
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Calculate metrics
        duration = end_time - start_time
        throughput_mbps = (
            (total_bytes_sent / (1024 * 1024)) / duration if duration > 0 else 0
        )

        # Assertions
        assert throughput_mbps > 1.0  # Should handle at least 1 MB/s
        assert messages_received >= (
            connection_count * messages_per_connection * 0.8
        )  # 80% delivery

        print("Large Message Test Results:")
        print(f"  Message Size: {large_message_size} bytes")
        print(f"  Total Messages: {connection_count * messages_per_connection}")
        print(f"  Messages Received: {messages_received}")
        print(f"  Total Bytes: {total_bytes_sent / (1024 * 1024):.1f} MB")
        print(f"  Throughput: {throughput_mbps:.2f} MB/s")

    async def test_memory_usage_under_load(
        self, high_capacity_websocket_manager, event_publisher
    ):
        """Test memory usage under sustained load."""
        connection_count = 30
        test_duration = 10.0  # 10 seconds
        event_interval = 0.1  # Event every 100ms

        connections = []
        tasks = []
        memory_samples = []

        start_time = time.time()

        # Create connections
        for i in range(connection_count):
            mock_ws = await self.create_mock_websocket(i)
            connections.append(mock_ws)

            task = asyncio.create_task(
                high_capacity_websocket_manager.handle_connection(mock_ws)
            )
            tasks.append(task)

        await asyncio.sleep(0.5)  # Let connections establish

        # Start memory monitoring
        async def monitor_memory():
            while time.time() - start_time < test_duration:
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
                await asyncio.sleep(1.0)

        memory_task = asyncio.create_task(monitor_memory())

        # Generate sustained load
        event_count = 0
        while time.time() - start_time < test_duration:
            event = AgentStatusEvent(
                agent_id=f"load_agent_{event_count % 5}",
                status=AgentStatus.PROCESSING,
                message=f"Load test event {event_count}",
                source="load_test",
            )

            await event_publisher.publish_event(event)
            event_count += 1
            await asyncio.sleep(event_interval)

        # Stop monitoring
        memory_task.cancel()
        try:
            await memory_task
        except asyncio.CancelledError:
            pass

        # Cleanup
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Analyze memory usage
        if memory_samples:
            initial_memory = memory_samples[0]
            peak_memory = max(memory_samples)
            final_memory = memory_samples[-1]
            memory_growth = final_memory - initial_memory

            # Assertions
            assert memory_growth < 100  # Memory growth should be < 100MB
            assert peak_memory < initial_memory + 200  # Peak should be reasonable

            print("Memory Usage Test Results:")
            print(f"  Test Duration: {test_duration}s")
            print(f"  Events Generated: {event_count}")
            print(f"  Initial Memory: {initial_memory:.1f} MB")
            print(f"  Peak Memory: {peak_memory:.1f} MB")
            print(f"  Final Memory: {final_memory:.1f} MB")
            print(f"  Memory Growth: {memory_growth:.1f} MB")
