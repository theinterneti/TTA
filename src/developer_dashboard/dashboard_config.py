"""

# Logseq: [[TTA.dev/Developer_dashboard/Dashboard_config]]
Developer Dashboard Configuration for TTA Comprehensive Test Battery.

Configuration settings and initialization for dashboard integration.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """Configuration for developer dashboard."""

    # Server settings
    host: str = "localhost"
    port: int = 8080
    debug: bool = False

    # Test battery integration
    enable_test_battery: bool = True
    test_results_dir: str = "./test-results"
    websocket_enabled: bool = True

    # Dashboard features
    enable_real_time_updates: bool = True
    enable_historical_data: bool = True
    max_history_records: int = 1000

    # Security settings
    cors_origins: list = None  # type: ignore[assignment]
    api_key_required: bool = False
    api_key: str | None = None

    # Monitoring settings
    enable_metrics: bool = True
    metrics_retention_days: int = 30
    alert_on_failures: bool = True
    failure_threshold: float = 0.8  # Alert if success rate drops below 80%

    @classmethod
    def from_env(cls) -> "DashboardConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("DASHBOARD_HOST", "localhost"),
            port=int(os.getenv("DASHBOARD_PORT", "8080")),
            debug=os.getenv("DASHBOARD_DEBUG", "false").lower() == "true",
            enable_test_battery=os.getenv("DASHBOARD_TEST_BATTERY", "true").lower()
            == "true",
            test_results_dir=os.getenv("TEST_RESULTS_DIR", "./test-results"),
            websocket_enabled=os.getenv("DASHBOARD_WEBSOCKET", "true").lower()
            == "true",
            enable_real_time_updates=os.getenv("DASHBOARD_REAL_TIME", "true").lower()
            == "true",
            enable_historical_data=os.getenv("DASHBOARD_HISTORY", "true").lower()
            == "true",
            max_history_records=int(os.getenv("DASHBOARD_MAX_HISTORY", "1000")),
            cors_origins=(  # type: ignore[arg-type]
                os.getenv("DASHBOARD_CORS_ORIGINS", "").split(",")
                if os.getenv("DASHBOARD_CORS_ORIGINS")
                else None
            ),
            api_key_required=os.getenv("DASHBOARD_API_KEY_REQUIRED", "false").lower()
            == "true",
            api_key=os.getenv("DASHBOARD_API_KEY"),
            enable_metrics=os.getenv("DASHBOARD_METRICS", "true").lower() == "true",
            metrics_retention_days=int(os.getenv("DASHBOARD_METRICS_RETENTION", "30")),
            alert_on_failures=os.getenv("DASHBOARD_ALERTS", "true").lower() == "true",
            failure_threshold=float(os.getenv("DASHBOARD_FAILURE_THRESHOLD", "0.8")),
        )


def create_dashboard_app(config: DashboardConfig) -> FastAPI:
    """Create and configure FastAPI application for dashboard."""

    app = FastAPI(
        title="TTA Developer Dashboard",
        description="Real-time monitoring and testing dashboard for TTA storytelling system",
        version="1.0.0",
        debug=config.debug,
    )

    # CORS middleware
    if config.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Static files for dashboard assets
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "tta-developer-dashboard",
            "version": "1.0.0",
            "test_battery_enabled": config.enable_test_battery,
        }

    # Dashboard home
    @app.get("/")
    async def dashboard_home():
        """Dashboard home page."""
        return {
            "message": "TTA Developer Dashboard",
            "endpoints": {
                "test_battery": "/dashboard/test-battery",
                "health": "/health",
                "metrics": "/dashboard/test-battery/metrics",
            },
        }

    return app


async def initialize_dashboard(
    config: DashboardConfig | None = None,
) -> tuple[FastAPI, Any]:
    """Initialize the developer dashboard with test battery integration."""

    if config is None:
        config = DashboardConfig.from_env()

    # Create FastAPI app
    app = create_dashboard_app(config)

    # Initialize test battery integration if enabled
    test_battery_dashboard = None
    if config.enable_test_battery:
        try:
            from .test_battery_integration import integrate_with_dashboard

            test_battery_dashboard = await integrate_with_dashboard(app)
            logger.info("Test battery dashboard integration enabled")
        except ImportError as e:
            logger.warning(f"Could not enable test battery integration: {e}")

    # Setup additional monitoring if enabled
    if config.enable_metrics:
        await setup_metrics_monitoring(app, config)

    logger.info(f"Dashboard initialized on {config.host}:{config.port}")
    return app, test_battery_dashboard


async def setup_metrics_monitoring(app: FastAPI, config: DashboardConfig):
    """Setup metrics monitoring and alerting."""

    @app.get("/dashboard/metrics/system")
    async def get_system_metrics():
        """Get system performance metrics."""
        try:
            import psutil

            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
                "timestamp": "2025-09-15T12:00:00Z",
            }
        except ImportError:
            return {
                "error": "psutil not available",
                "timestamp": "2025-09-15T12:00:00Z",
            }

    @app.get("/dashboard/metrics/test-performance")
    async def get_test_performance_metrics():
        """Get test performance metrics."""
        try:
            results_dir = Path(config.test_results_dir)
            if not results_dir.exists():
                return {"error": "Test results directory not found"}

            # Analyze recent test results
            recent_results = []
            for result_file in results_dir.glob("*/test_summary.json"):
                try:
                    with result_file.open() as f:
                        import json

                        data = json.load(f)
                        recent_results.append(data)
                except Exception as e:
                    logger.debug(
                        f"Skipping test result file {result_file}: {type(e).__name__}: {e}"
                    )
                    continue

            if not recent_results:
                return {"error": "No test results found"}

            # Calculate performance metrics
            total_executions = len(recent_results)
            avg_duration = (
                sum(r.get("duration_seconds", 0) for r in recent_results)
                / total_executions
            )
            avg_success_rate = (
                sum(r.get("success_rate", 0) for r in recent_results) / total_executions
            )

            return {
                "total_executions": total_executions,
                "average_duration": round(avg_duration, 2),
                "average_success_rate": round(avg_success_rate, 2),
                "last_execution": (
                    max(r.get("end_time", "") for r in recent_results)
                    if recent_results
                    else None
                ),
                "timestamp": "2025-09-15T12:00:00Z",
            }

        except Exception as e:
            return {"error": str(e)}


# Dashboard startup script
async def start_dashboard():
    """Start the developer dashboard server."""
    import uvicorn

    config = DashboardConfig.from_env()
    app, dashboard = await initialize_dashboard(config)

    # Store dashboard reference for external access
    app.state.test_battery_dashboard = dashboard

    # Start server
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level="info" if not config.debug else "debug",
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(start_dashboard())
