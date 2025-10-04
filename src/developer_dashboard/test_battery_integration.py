"""
Developer Dashboard Integration for TTA Comprehensive Test Battery.

Provides real-time test execution monitoring, results visualization,
and service status reporting for the developer dashboard.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import aiofiles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status."""

    NOT_STARTED = "not_started"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class TestResult:
    """Individual test result."""

    test_id: str
    name: str
    category: str
    status: TestStatus
    duration: float
    error_message: str | None = None
    timestamp: str | None = None
    service_mode: dict[str, str] | None = None


@dataclass
class TestBatteryStatus:
    """Overall test battery status."""

    battery_id: str
    status: TestStatus
    start_time: str
    end_time: str | None
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    success_rate: float
    service_status: dict[str, str]
    categories_tested: list[str]
    mock_mode: bool


class TestBatteryDashboard:
    """Dashboard integration for comprehensive test battery."""

    def __init__(self, app: FastAPI):
        self.app = app
        self.active_connections: list[WebSocket] = []
        self.current_status: TestBatteryStatus | None = None
        self.test_results: list[TestResult] = []
        self.test_history: list[TestBatteryStatus] = []

        # Setup routes
        self._setup_routes()

        # Load historical data
        asyncio.create_task(self._load_historical_data())

    def _setup_routes(self):
        """Setup FastAPI routes for dashboard integration."""

        @self.app.get("/dashboard/test-battery/status")
        async def get_test_battery_status():
            """Get current test battery status."""
            return JSONResponse(
                {
                    "current_status": (
                        asdict(self.current_status) if self.current_status else None
                    ),
                    "recent_results": [
                        asdict(result) for result in self.test_results[-10:]
                    ],
                    "service_status": await self._get_service_status(),
                    "last_updated": datetime.utcnow().isoformat(),
                }
            )

        @self.app.get("/dashboard/test-battery/history")
        async def get_test_battery_history(limit: int = 50):
            """Get test battery execution history."""
            return JSONResponse(
                {
                    "history": [
                        asdict(status) for status in self.test_history[-limit:]
                    ],
                    "total_executions": len(self.test_history),
                }
            )

        @self.app.get("/dashboard/test-battery/metrics")
        async def get_test_battery_metrics():
            """Get test battery performance metrics."""
            return JSONResponse(await self._calculate_metrics())

        @self.app.websocket("/dashboard/test-battery/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time test updates."""
            await self._handle_websocket_connection(websocket)

        @self.app.get("/dashboard/test-battery", response_class=HTMLResponse)
        async def test_battery_dashboard():
            """Serve test battery dashboard HTML."""
            return await self._get_dashboard_html()

    async def _handle_websocket_connection(self, websocket: WebSocket):
        """Handle WebSocket connection for real-time updates."""
        await websocket.accept()
        self.active_connections.append(websocket)

        try:
            # Send current status immediately
            if self.current_status:
                await websocket.send_json(
                    {"type": "status_update", "data": asdict(self.current_status)}
                )

            # Keep connection alive
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast_update(self, update_type: str, data: dict[str, Any]):
        """Broadcast update to all connected WebSocket clients."""
        if not self.active_connections:
            return

        message = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Send to all connected clients
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)

    async def update_test_battery_status(self, status: TestBatteryStatus):
        """Update test battery status and broadcast to dashboard."""
        self.current_status = status

        # Add to history if completed
        if status.status in [
            TestStatus.PASSED,
            TestStatus.FAILED,
            TestStatus.CANCELLED,
        ]:
            self.test_history.append(status)
            await self._save_historical_data()

        # Broadcast update
        await self.broadcast_update("battery_status", asdict(status))

    async def update_test_result(self, result: TestResult):
        """Update individual test result and broadcast to dashboard."""
        # Update or add test result
        existing_index = None
        for i, existing_result in enumerate(self.test_results):
            if existing_result.test_id == result.test_id:
                existing_index = i
                break

        if existing_index is not None:
            self.test_results[existing_index] = result
        else:
            self.test_results.append(result)

        # Broadcast update
        await self.broadcast_update("test_result", asdict(result))

    async def _get_service_status(self) -> dict[str, Any]:
        """Get current service status."""
        try:
            # Try to import and use mock service manager
            from tests.comprehensive_battery.mocks.mock_services import (
                MockServiceManager,
            )

            manager = MockServiceManager()
            status = await manager.get_service_status()
            await manager.cleanup()

            return {
                "services": status,
                "last_checked": datetime.utcnow().isoformat(),
                "available": True,
            }
        except Exception as e:
            logger.warning(f"Could not get service status: {e}")
            return {
                "services": {},
                "last_checked": datetime.utcnow().isoformat(),
                "available": False,
                "error": str(e),
            }

    async def _calculate_metrics(self) -> dict[str, Any]:
        """Calculate test battery performance metrics."""
        if not self.test_history:
            return {
                "total_executions": 0,
                "average_success_rate": 0.0,
                "average_duration": 0.0,
                "trend": "stable",
            }

        recent_history = self.test_history[-30:]  # Last 30 executions

        total_executions = len(self.test_history)
        success_rates = [h.success_rate for h in recent_history]
        average_success_rate = (
            sum(success_rates) / len(success_rates) if success_rates else 0.0
        )

        # Calculate average duration (if available)
        durations = []
        for history in recent_history:
            if history.start_time and history.end_time:
                start = datetime.fromisoformat(
                    history.start_time.replace("Z", "+00:00")
                )
                end = datetime.fromisoformat(history.end_time.replace("Z", "+00:00"))
                duration = (end - start).total_seconds()
                durations.append(duration)

        average_duration = sum(durations) / len(durations) if durations else 0.0

        # Calculate trend
        if len(success_rates) >= 10:
            recent_avg = sum(success_rates[-5:]) / 5
            older_avg = sum(success_rates[-10:-5]) / 5
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "total_executions": total_executions,
            "average_success_rate": round(average_success_rate, 2),
            "average_duration": round(average_duration, 2),
            "trend": trend,
            "last_30_executions": len(recent_history),
            "mock_mode_percentage": (
                round(
                    sum(1 for h in recent_history if h.mock_mode)
                    / len(recent_history)
                    * 100,
                    1,
                )
                if recent_history
                else 0.0
            ),
        }

    async def _load_historical_data(self):
        """Load historical test data from storage."""
        try:
            history_file = Path("./test-results/dashboard_history.json")
            if history_file.exists():
                async with aiofiles.open(history_file) as f:
                    data = json.loads(await f.read())

                    self.test_history = [
                        TestBatteryStatus(**item) for item in data.get("history", [])
                    ]
                    logger.info(
                        f"Loaded {len(self.test_history)} historical test records"
                    )
        except Exception as e:
            logger.warning(f"Could not load historical data: {e}")

    async def _save_historical_data(self):
        """Save historical test data to storage."""
        try:
            history_file = Path("./test-results/dashboard_history.json")
            history_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "history": [
                    asdict(status) for status in self.test_history[-100:]
                ],  # Keep last 100
                "last_updated": datetime.utcnow().isoformat(),
            }

            async with aiofiles.open(history_file, "w") as f:
                await f.write(json.dumps(data, indent=2))

        except Exception as e:
            logger.error(f"Could not save historical data: {e}")

    async def _get_dashboard_html(self) -> str:
        """Get dashboard HTML content."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TTA Test Battery Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
                .status-item { padding: 15px; border-radius: 6px; text-align: center; }
                .status-passed { background: #d4edda; color: #155724; }
                .status-failed { background: #f8d7da; color: #721c24; }
                .status-running { background: #fff3cd; color: #856404; }
                .status-not-started { background: #e2e3e5; color: #383d41; }
                .metric { font-size: 24px; font-weight: bold; }
                .label { font-size: 14px; margin-top: 5px; }
                #log { background: #000; color: #0f0; padding: 15px; border-radius: 6px; height: 300px; overflow-y: auto; font-family: monospace; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 TTA Comprehensive Test Battery Dashboard</h1>

                <div class="card">
                    <h2>Current Status</h2>
                    <div id="current-status" class="status-grid">
                        <div class="status-item status-not-started">
                            <div class="metric">-</div>
                            <div class="label">Status</div>
                        </div>
                        <div class="status-item">
                            <div class="metric" id="success-rate">-</div>
                            <div class="label">Success Rate</div>
                        </div>
                        <div class="status-item">
                            <div class="metric" id="total-tests">-</div>
                            <div class="label">Total Tests</div>
                        </div>
                        <div class="status-item">
                            <div class="metric" id="service-mode">-</div>
                            <div class="label">Service Mode</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Real-time Log</h2>
                    <div id="log">Connecting to test battery...</div>
                </div>

                <div class="card">
                    <h2>Service Status</h2>
                    <div id="service-status">Loading...</div>
                </div>
            </div>

            <script>
                // Use secure WebSocket (wss://) in production, ws:// only for local development
                // nosemgrep: javascript.lang.security.detect-insecure-websocket.detect-insecure-websocket
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'; // nosemgrep
                const ws = new WebSocket(`${protocol}//${window.location.host}/dashboard/test-battery/ws`);
                const log = document.getElementById('log');

                function addLog(message) {
                    const timestamp = new Date().toLocaleTimeString();
                    log.innerHTML += `[${timestamp}] ${message}\\n`;
                    log.scrollTop = log.scrollHeight;
                }

                ws.onopen = function() {
                    addLog('Connected to test battery dashboard');
                };

                ws.onmessage = function(event) {
                    const message = JSON.parse(event.data);

                    if (message.type === 'battery_status') {
                        updateBatteryStatus(message.data);
                        addLog(`Battery status: ${message.data.status} (${message.data.success_rate}% success)`);
                    } else if (message.type === 'test_result') {
                        addLog(`Test ${message.data.name}: ${message.data.status}`);
                    }
                };

                function updateBatteryStatus(status) {
                    document.getElementById('success-rate').textContent = status.success_rate + '%';
                    document.getElementById('total-tests').textContent = status.total_tests;
                    document.getElementById('service-mode').textContent = status.mock_mode ? 'Mock' : 'Real';
                }

                // Load initial data
                fetch('/dashboard/test-battery/status')
                    .then(response => response.json())
                    .then(data => {
                        if (data.current_status) {
                            updateBatteryStatus(data.current_status);
                        }

                        const serviceStatus = document.getElementById('service-status');
                        if (data.service_status && data.service_status.services) {
                            let html = '<div class="status-grid">';
                            for (const [service, info] of Object.entries(data.service_status.services)) {
                                const statusClass = info.status === 'real' ? 'status-passed' : 'status-failed';
                                html += `<div class="status-item ${statusClass}">
                                    <div class="metric">${service.toUpperCase()}</div>
                                    <div class="label">${info.status}</div>
                                </div>`;
                            }
                            html += '</div>';
                            serviceStatus.innerHTML = html;
                        }
                    });
            </script>
        </body>
        </html>
        """


# Integration helper functions
async def integrate_with_dashboard(app: FastAPI) -> TestBatteryDashboard:
    """Integrate comprehensive test battery with developer dashboard."""
    dashboard = TestBatteryDashboard(app)
    logger.info("Test battery dashboard integration initialized")
    return dashboard


async def report_test_execution(
    dashboard: TestBatteryDashboard, battery_id: str, results_dir: Path
):
    """Report test execution results to dashboard."""
    try:
        # Load test results
        summary_file = results_dir / "test_summary.json"
        if summary_file.exists():
            async with aiofiles.open(summary_file) as f:
                summary_data = json.loads(await f.read())

            # Create status object
            status = TestBatteryStatus(
                battery_id=battery_id,
                status=(
                    TestStatus.PASSED
                    if summary_data.get("failed_tests", 0) == 0
                    else TestStatus.FAILED
                ),
                start_time=summary_data.get(
                    "start_time", datetime.utcnow().isoformat()
                ),
                end_time=summary_data.get("end_time", datetime.utcnow().isoformat()),
                total_tests=summary_data.get("total_tests", 0),
                passed_tests=summary_data.get("passed_tests", 0),
                failed_tests=summary_data.get("failed_tests", 0),
                skipped_tests=summary_data.get("skipped_tests", 0),
                success_rate=summary_data.get("success_rate", 0.0),
                service_status=summary_data.get("service_status", {}),
                categories_tested=summary_data.get("categories_tested", []),
                mock_mode=summary_data.get("mock_mode", False),
            )

            await dashboard.update_test_battery_status(status)
            logger.info(f"Reported test execution {battery_id} to dashboard")

    except Exception as e:
        logger.error(f"Failed to report test execution to dashboard: {e}")
