"""

# Logseq: [[TTA.dev/Monitoring/Performance_monitor]]
Mock performance monitor for TTA containerized deployment.
"""


def get_performance_monitor():
    """Return a mock performance monitor."""

    class MockPerformanceMonitor:
        def start_request(self, request_id):
            pass

        def end_request(self, request_id):
            pass

        def record_metric(self, name, value):
            pass

    return MockPerformanceMonitor()
