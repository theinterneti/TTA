"""Tests for monitoring.performance_monitor module."""

# Logseq: [[TTA.dev/Tests/Monitoring/Test_performance_monitor]]

from src.monitoring.performance_monitor import get_performance_monitor


class TestGetPerformanceMonitor:
    """Tests for get_performance_monitor function."""

    def test_get_performance_monitor_returns_monitor(self):
        """Test that function returns a monitor object."""
        monitor = get_performance_monitor()
        assert monitor is not None

    def test_performance_monitor_has_start_request(self):
        """Test that monitor has start_request method."""
        monitor = get_performance_monitor()
        assert hasattr(monitor, "start_request")
        assert callable(monitor.start_request)

    def test_performance_monitor_has_end_request(self):
        """Test that monitor has end_request method."""
        monitor = get_performance_monitor()
        assert hasattr(monitor, "end_request")
        assert callable(monitor.end_request)

    def test_performance_monitor_has_record_metric(self):
        """Test that monitor has record_metric method."""
        monitor = get_performance_monitor()
        assert hasattr(monitor, "record_metric")
        assert callable(monitor.record_metric)

    def test_start_request_method(self):
        """Test start_request method."""
        monitor = get_performance_monitor()
        # Should not raise exception
        monitor.start_request("req-123")

    def test_end_request_method(self):
        """Test end_request method."""
        monitor = get_performance_monitor()
        # Should not raise exception
        monitor.end_request("req-123")

    def test_record_metric_method(self):
        """Test record_metric method."""
        monitor = get_performance_monitor()
        # Should not raise exception
        monitor.record_metric("response_time", 0.5)

    def test_multiple_requests(self):
        """Test handling multiple requests."""
        monitor = get_performance_monitor()
        for i in range(10):
            monitor.start_request(f"req-{i}")
            monitor.record_metric("response_time", 0.1 * i)
            monitor.end_request(f"req-{i}")
