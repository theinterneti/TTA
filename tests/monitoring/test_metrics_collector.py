"""Tests for monitoring.metrics_collector module."""

# Logseq: [[TTA.dev/Tests/Monitoring/Test_metrics_collector]]

from src.monitoring.metrics_collector import record_request_metric


class TestRecordRequestMetric:
    """Tests for record_request_metric function."""

    def test_record_request_metric_basic(self):
        """Test basic metric recording."""
        # Should not raise any exception
        record_request_metric("GET", "/api/test", 200, 0.5)

    def test_record_request_metric_with_different_methods(self):
        """Test with different HTTP methods."""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        for method in methods:
            record_request_metric(method, "/api/test", 200, 0.1)

    def test_record_request_metric_with_different_status_codes(self):
        """Test with different status codes."""
        status_codes = [200, 201, 400, 404, 500, 503]
        for status in status_codes:
            record_request_metric("GET", "/api/test", status, 0.1)

    def test_record_request_metric_with_various_durations(self):
        """Test with various request durations."""
        durations = [0.001, 0.1, 1.0, 10.0, 100.0]
        for duration in durations:
            record_request_metric("GET", "/api/test", 200, duration)

    def test_record_request_metric_with_special_endpoints(self):
        """Test with special endpoint paths."""
        endpoints = ["/", "/api/", "/api/v1/users", "/health", "/metrics"]
        for endpoint in endpoints:
            record_request_metric("GET", endpoint, 200, 0.1)
