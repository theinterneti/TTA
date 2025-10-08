"""
FastAPI middleware for automatic Prometheus metrics collection.

This middleware automatically collects HTTP request metrics, system metrics,
and integrates with the TTA monitoring infrastructure.
"""

import asyncio
import logging
import time
from collections.abc import Callable

import psutil
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse

from .prometheus_metrics import CONTENT_TYPE_LATEST, get_metrics_collector

# Import mock monitoring with fallback
try:
    from .mock_monitoring import (
        get_mock_monitoring_environment,
        should_use_mock_monitoring,
    )

    MOCK_MONITORING_AVAILABLE = True
except ImportError:
    MOCK_MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for FastAPI applications."""

    def __init__(
        self, app, service_name: str = "tta", collect_system_metrics: bool = True
    ):
        super().__init__(app)
        self.service_name = service_name
        self.collect_system_metrics = collect_system_metrics
        self.metrics_collector = get_metrics_collector(service_name)

        # Start system metrics collection if enabled
        if self.collect_system_metrics:
            self._start_system_metrics_collection()

    def _start_system_metrics_collection(self):
        """Start background task to collect system metrics."""

        async def collect_system_metrics():
            while True:
                try:
                    # Collect system metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory_percent = psutil.virtual_memory().percent
                    disk_percent = psutil.disk_usage("/").percent

                    # Update metrics
                    self.metrics_collector.update_system_metrics(
                        cpu_percent=cpu_percent,
                        memory_percent=memory_percent,
                        disk_percent=disk_percent,
                    )

                    # Update active connections gauge

                    # This would need to be implemented based on your connection tracking
                    # active_connections.labels(service=self.service_name).set(connection_count)

                except Exception as e:
                    logger.error(f"Error collecting system metrics: {e}")

                # Wait 30 seconds before next collection
                await asyncio.sleep(30)

        # Start the background task
        asyncio.create_task(collect_system_metrics())

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        # Skip metrics collection for the metrics endpoint itself
        if request.url.path in ["/metrics", "/metrics-prom"]:
            return await call_next(request)

        start_time = time.time()
        method = request.method
        endpoint = request.url.path

        try:
            # Process the request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            self.metrics_collector.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration,
            )

            # Add timing header
            response.headers["X-Process-Time"] = str(duration)

            return response

        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            self.metrics_collector.record_http_request(
                method=method, endpoint=endpoint, status_code=500, duration=duration
            )

            logger.error(f"Request failed: {e}")
            raise


def add_metrics_endpoint(app, path: str = "/metrics"):
    """Add Prometheus metrics endpoint to FastAPI app."""

    @app.get(path, response_class=PlainTextResponse)
    async def metrics():
        """Prometheus metrics endpoint."""
        try:
            collector = get_metrics_collector()
            metrics_data = collector.get_metrics()
            return PlainTextResponse(
                content=metrics_data, media_type=CONTENT_TYPE_LATEST
            )
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return PlainTextResponse(
                content="# Error generating metrics\n", status_code=500
            )


class MockMetricsMiddleware(BaseHTTPMiddleware):
    """Mock metrics middleware for environments without full monitoring infrastructure."""

    def __init__(self, app, service_name: str = "tta"):
        super().__init__(app)
        self.service_name = service_name
        logger.info(f"Using mock metrics middleware for service: {service_name}")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with minimal overhead."""
        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Add timing header for debugging
            response.headers["X-Process-Time"] = str(duration)

            # Log basic metrics to console in debug mode
            logger.debug(
                f"Request: {request.method} {request.url.path} "
                f"Status: {response.status_code} Duration: {duration:.3f}s"
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.debug(
                f"Request failed: {request.method} {request.url.path} "
                f"Duration: {duration:.3f}s Error: {e}"
            )
            raise


def add_mock_metrics_endpoint(app, path: str = "/metrics"):
    """Add mock metrics endpoint for environments without Prometheus."""

    @app.get(path, response_class=PlainTextResponse)
    async def mock_metrics():
        """Mock metrics endpoint that returns basic information."""
        import json
        from datetime import datetime

        mock_data = {
            "service": "tta",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Mock metrics endpoint - Prometheus not available",
            "basic_metrics": {
                "uptime_seconds": time.time(),
                "requests_processed": "N/A",
                "memory_usage": "N/A",
            },
        }

        return PlainTextResponse(
            content=f"# Mock TTA Metrics\n# {json.dumps(mock_data, indent=2)}\n",
            media_type="text/plain",
        )


def setup_monitoring_middleware(
    app,
    service_name: str = "tta",
    enable_prometheus: bool = True,
    metrics_path: str = "/metrics",
    force_mock: bool = False,
):
    """
    Setup monitoring middleware with automatic fallback to mock implementation.

    Args:
        app: FastAPI application instance
        service_name: Name of the service for metrics labeling
        enable_prometheus: Whether to enable full Prometheus metrics
        metrics_path: Path for the metrics endpoint
        force_mock: Force use of mock monitoring (for testing)
    """
    # Use the new factory function for automatic environment detection
    use_mock = force_mock or (
        MOCK_MONITORING_AVAILABLE and should_use_mock_monitoring()
    )

    if use_mock:
        logger.info(f"Using mock monitoring for service: {service_name}")
        app.add_middleware(MockMetricsMiddleware, service_name=service_name)
        add_mock_metrics_endpoint(app, metrics_path)
    else:
        try:
            if enable_prometheus:
                # Try to use full Prometheus metrics
                import prometheus_client

                app.add_middleware(
                    PrometheusMetricsMiddleware, service_name=service_name
                )
                add_metrics_endpoint(app, metrics_path)
                logger.info(f"Prometheus metrics enabled for service: {service_name}")
            else:
                raise ImportError("Prometheus disabled")

        except ImportError as e:
            # Fall back to mock metrics
            logger.warning(
                f"Prometheus not available ({e}), falling back to mock metrics"
            )
            if MOCK_MONITORING_AVAILABLE:
                app.add_middleware(MockMetricsMiddleware, service_name=service_name)
                add_mock_metrics_endpoint(app, metrics_path)
            else:
                logger.error("No monitoring implementation available")


# Environment detection utility
def detect_monitoring_environment() -> dict:
    """
    Detect available monitoring infrastructure.

    Returns:
        dict: Information about available monitoring tools
    """
    environment = {
        "prometheus_available": False,
        "grafana_available": False,
        "psutil_available": False,
        "redis_available": False,
        "neo4j_available": False,
    }

    # Check Prometheus client
    try:
        import prometheus_client

        environment["prometheus_available"] = True
    except ImportError:
        pass

    # Check psutil for system metrics
    try:
        import psutil

        environment["psutil_available"] = True
    except ImportError:
        pass

    # Check Redis availability
    try:
        import redis

        # Could add actual connection test here
        environment["redis_available"] = True
    except ImportError:
        pass

    # Check Neo4j availability
    try:
        import neo4j

        environment["neo4j_available"] = True
    except ImportError:
        pass

    return environment


class MockMetricsMiddleware(BaseHTTPMiddleware):
    """Mock metrics middleware for environments without Prometheus."""

    def __init__(self, app, service_name: str = "tta"):
        super().__init__(app)
        self.service_name = service_name
        self.mock_env = None

        if MOCK_MONITORING_AVAILABLE:
            self.mock_env = get_mock_monitoring_environment()
            if not self.mock_env.is_running:
                self.mock_env.start()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with mock metrics collection."""
        start_time = time.time()

        # Simulate some load for testing
        if self.mock_env:
            self.mock_env.simulate_load()

        response = await call_next(request)

        # Log mock metrics (could be enhanced to store in memory)
        duration = time.time() - start_time
        logger.debug(
            f"Mock metrics: {request.method} {request.url.path} - {response.status_code} - {duration:.3f}s"
        )

        return response


def create_metrics_middleware(app, service_name: str = "tta", force_mock: bool = False):
    """Create appropriate metrics middleware based on environment."""

    # Check if we should use mock monitoring
    use_mock = force_mock or (
        MOCK_MONITORING_AVAILABLE and should_use_mock_monitoring()
    )

    if use_mock:
        logger.info(f"Using mock metrics middleware for service: {service_name}")
        return MockMetricsMiddleware(app, service_name)
    logger.info(f"Using Prometheus metrics middleware for service: {service_name}")
    return PrometheusMetricsMiddleware(app, service_name)


def get_monitoring_status() -> dict:
    """Get current monitoring system status."""
    status = {
        "prometheus_available": False,
        "grafana_available": False,
        "mock_mode": False,
        "environment": detect_monitoring_environment(),
    }

    if MOCK_MONITORING_AVAILABLE:
        if should_use_mock_monitoring():
            status["mock_mode"] = True
            mock_env = get_mock_monitoring_environment()
            status.update(mock_env.get_status())
        else:
            # Try to check real monitoring services
            try:
                import requests

                # Check Prometheus
                response = requests.get("http://localhost:9090/-/healthy", timeout=2)
                status["prometheus_available"] = response.status_code == 200

                # Check Grafana
                response = requests.get("http://localhost:3000/api/health", timeout=2)
                status["grafana_available"] = response.status_code == 200
            except Exception:
                pass

    return status
