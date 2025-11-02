"""
Comprehensive Data Collection System for Extended Session Testing

Provides detailed logging, monitoring, and data collection capabilities
for comprehensive analysis of TTA storytelling system performance and
quality over extended sessions.
"""

import asyncio
import csv
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import psutil

logger = logging.getLogger(__name__)


@dataclass
class TurnData:
    """Comprehensive data for a single turn."""

    turn_number: int
    timestamp: datetime
    session_id: str

    # User interaction
    user_input: str
    user_input_length: int
    user_thinking_time: float

    # System response
    system_response: str
    response_length: int
    response_time: float

    # Quality metrics
    narrative_coherence_score: float | None = None
    world_consistency_score: float | None = None
    user_engagement_score: float | None = None

    # Technical metrics
    memory_usage_mb: float | None = None
    cpu_usage_percent: float | None = None

    # World state
    world_state_snapshot: dict[str, Any] = field(default_factory=dict)
    choice_data: dict[str, Any] = field(default_factory=dict)

    # Errors and issues
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class SessionData:
    """Comprehensive data for an entire session."""

    session_id: str
    test_id: str
    start_time: datetime
    end_time: datetime | None = None

    # Configuration
    model_name: str = ""
    profile_name: str = ""
    scenario_name: str = ""

    # Session metrics
    total_turns: int = 0
    completed_turns: int = 0
    session_duration_minutes: float = 0.0

    # Turn data
    turns: list[TurnData] = field(default_factory=list)

    # Aggregated metrics
    avg_response_time: float = 0.0
    avg_narrative_coherence: float = 0.0
    avg_world_consistency: float = 0.0
    avg_user_engagement: float = 0.0

    # Technical performance
    peak_memory_usage_mb: float = 0.0
    avg_cpu_usage: float = 0.0
    total_errors: int = 0

    # Quality trends
    coherence_trend: list[float] = field(default_factory=list)
    consistency_trend: list[float] = field(default_factory=list)
    engagement_trend: list[float] = field(default_factory=list)


@dataclass
class PerformanceMetrics:
    """System performance metrics."""

    timestamp: datetime
    memory_usage_mb: float
    cpu_usage_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float


class ComprehensiveDataCollector:
    """
    Comprehensive data collection system for extended session testing.

    Collects detailed data on user interactions, system responses, quality
    metrics, performance data, and world state changes for thorough analysis.
    """

    def __init__(self, output_dir: str = "testing/results/extended_evaluation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data storage
        self.session_data: dict[str, SessionData] = {}
        self.performance_history: list[PerformanceMetrics] = []

        # Monitoring
        self.monitoring_active = False
        self.monitoring_task: asyncio.Task | None = None

        # File handles for real-time logging
        self.log_files: dict[str, Any] = {}

        logger.info(
            f"ComprehensiveDataCollector initialized with output dir: {self.output_dir}"
        )

    async def start_session_collection(
        self,
        session_id: str,
        test_id: str,
        model_name: str,
        profile_name: str,
        scenario_name: str,
    ) -> None:
        """Start data collection for a new session."""
        session_data = SessionData(
            session_id=session_id,
            test_id=test_id,
            start_time=datetime.now(),
            model_name=model_name,
            profile_name=profile_name,
            scenario_name=scenario_name,
        )

        self.session_data[session_id] = session_data

        # Create session-specific log files
        await self._create_session_log_files(session_id)

        # Start performance monitoring if not already active
        if not self.monitoring_active:
            await self.start_performance_monitoring()

        logger.info(f"Started data collection for session {session_id}")

    async def collect_turn_data(
        self,
        session_id: str,
        turn_number: int,
        user_input: str,
        system_response: str,
        user_thinking_time: float,
        response_time: float,
        world_state: dict[str, Any] = None,
        choice_data: dict[str, Any] = None,
    ) -> TurnData:
        """Collect comprehensive data for a single turn."""
        if session_id not in self.session_data:
            logger.warning(f"Session {session_id} not found, creating new session data")
            await self.start_session_collection(
                session_id, f"unknown_{session_id}", "unknown", "unknown", "unknown"
            )

        # Collect performance metrics
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
        cpu_usage = psutil.cpu_percent()

        # Create turn data
        turn_data = TurnData(
            turn_number=turn_number,
            timestamp=datetime.now(),
            session_id=session_id,
            user_input=user_input,
            user_input_length=len(user_input),
            user_thinking_time=user_thinking_time,
            system_response=system_response,
            response_length=len(system_response),
            response_time=response_time,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            world_state_snapshot=world_state or {},
            choice_data=choice_data or {},
        )

        # Add to session data
        session_data = self.session_data[session_id]
        session_data.turns.append(turn_data)
        session_data.completed_turns += 1

        # Update peak memory usage
        session_data.peak_memory_usage_mb = max(
            session_data.peak_memory_usage_mb, memory_usage
        )

        # Log turn data in real-time
        await self._log_turn_data(session_id, turn_data)

        logger.debug(f"Collected turn {turn_number} data for session {session_id}")
        return turn_data

    async def update_turn_quality_metrics(
        self,
        session_id: str,
        turn_number: int,
        narrative_coherence: float = None,
        world_consistency: float = None,
        user_engagement: float = None,
    ) -> None:
        """Update quality metrics for a specific turn."""
        if session_id not in self.session_data:
            logger.warning(f"Session {session_id} not found for quality metrics update")
            return

        session_data = self.session_data[session_id]

        # Find the turn data
        turn_data = None
        for turn in session_data.turns:
            if turn.turn_number == turn_number:
                turn_data = turn
                break

        if not turn_data:
            logger.warning(f"Turn {turn_number} not found in session {session_id}")
            return

        # Update quality metrics
        if narrative_coherence is not None:
            turn_data.narrative_coherence_score = narrative_coherence
            session_data.coherence_trend.append(narrative_coherence)

        if world_consistency is not None:
            turn_data.world_consistency_score = world_consistency
            session_data.consistency_trend.append(world_consistency)

        if user_engagement is not None:
            turn_data.user_engagement_score = user_engagement
            session_data.engagement_trend.append(user_engagement)

        logger.debug(
            f"Updated quality metrics for turn {turn_number} in session {session_id}"
        )

    async def log_error(
        self, session_id: str, turn_number: int, error_message: str
    ) -> None:
        """Log an error for a specific turn."""
        if session_id in self.session_data:
            session_data = self.session_data[session_id]
            session_data.total_errors += 1

            # Find the turn and add error
            for turn in session_data.turns:
                if turn.turn_number == turn_number:
                    turn.errors.append(error_message)
                    break

        logger.error(f"Session {session_id}, Turn {turn_number}: {error_message}")

    async def log_warning(
        self, session_id: str, turn_number: int, warning_message: str
    ) -> None:
        """Log a warning for a specific turn."""
        if session_id in self.session_data:
            # Find the turn and add warning
            session_data = self.session_data[session_id]
            for turn in session_data.turns:
                if turn.turn_number == turn_number:
                    turn.warnings.append(warning_message)
                    break

        logger.warning(f"Session {session_id}, Turn {turn_number}: {warning_message}")

    async def end_session_collection(self, session_id: str) -> SessionData:
        """End data collection for a session and calculate final metrics."""
        if session_id not in self.session_data:
            logger.warning(f"Session {session_id} not found for ending collection")
            return None

        session_data = self.session_data[session_id]
        session_data.end_time = datetime.now()

        # Calculate session duration
        if session_data.start_time and session_data.end_time:
            duration = session_data.end_time - session_data.start_time
            session_data.session_duration_minutes = duration.total_seconds() / 60

        # Calculate aggregated metrics
        await self._calculate_session_aggregates(session_data)

        # Save session data
        await self._save_session_data(session_data)

        # Close log files
        await self._close_session_log_files(session_id)

        logger.info(f"Ended data collection for session {session_id}")
        return session_data

    async def start_performance_monitoring(self, interval_seconds: float = 5.0) -> None:
        """Start continuous performance monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(
            self._performance_monitoring_loop(interval_seconds)
        )
        logger.info("Started performance monitoring")

    async def stop_performance_monitoring(self) -> None:
        """Stop performance monitoring."""
        if not self.monitoring_active:
            return

        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped performance monitoring")

    async def _performance_monitoring_loop(self, interval_seconds: float) -> None:
        """Continuous performance monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect performance metrics
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent()
                disk_io = psutil.disk_io_counters()
                network_io = psutil.net_io_counters()

                metrics = PerformanceMetrics(
                    timestamp=datetime.now(),
                    memory_usage_mb=memory.used / (1024 * 1024),
                    cpu_usage_percent=cpu_percent,
                    disk_io_read_mb=disk_io.read_bytes / (1024 * 1024)
                    if disk_io
                    else 0,
                    disk_io_write_mb=disk_io.write_bytes / (1024 * 1024)
                    if disk_io
                    else 0,
                    network_io_sent_mb=network_io.bytes_sent / (1024 * 1024)
                    if network_io
                    else 0,
                    network_io_recv_mb=network_io.bytes_recv / (1024 * 1024)
                    if network_io
                    else 0,
                )

                self.performance_history.append(metrics)

                # Keep only recent history (last hour)
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.performance_history = [
                    m for m in self.performance_history if m.timestamp > cutoff_time
                ]

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(interval_seconds)

    async def _create_session_log_files(self, session_id: str) -> None:
        """Create log files for a session."""
        session_dir = self.output_dir / session_id
        session_dir.mkdir(exist_ok=True)

        # Create CSV file for turn data
        turns_file = session_dir / "turns.csv"
        turns_csv = open(turns_file, "w", newline="")
        turns_writer = csv.writer(turns_csv)
        turns_writer.writerow(
            [
                "turn_number",
                "timestamp",
                "user_input_length",
                "user_thinking_time",
                "response_length",
                "response_time",
                "narrative_coherence_score",
                "world_consistency_score",
                "user_engagement_score",
                "memory_usage_mb",
                "cpu_usage_percent",
                "error_count",
                "warning_count",
            ]
        )

        # Create JSON file for detailed data
        detailed_file = session_dir / "detailed_turns.jsonl"
        detailed_json = open(detailed_file, "w")

        self.log_files[session_id] = {
            "turns_csv": turns_csv,
            "turns_writer": turns_writer,
            "detailed_json": detailed_json,
        }

    async def _log_turn_data(self, session_id: str, turn_data: TurnData) -> None:
        """Log turn data to files in real-time."""
        if session_id not in self.log_files:
            return

        files = self.log_files[session_id]

        # Write to CSV
        files["turns_writer"].writerow(
            [
                turn_data.turn_number,
                turn_data.timestamp.isoformat(),
                turn_data.user_input_length,
                turn_data.user_thinking_time,
                turn_data.response_length,
                turn_data.response_time,
                turn_data.narrative_coherence_score,
                turn_data.world_consistency_score,
                turn_data.user_engagement_score,
                turn_data.memory_usage_mb,
                turn_data.cpu_usage_percent,
                len(turn_data.errors),
                len(turn_data.warnings),
            ]
        )
        files["turns_csv"].flush()

        # Write to JSON Lines
        turn_dict = asdict(turn_data)
        turn_dict["timestamp"] = turn_data.timestamp.isoformat()
        files["detailed_json"].write(json.dumps(turn_dict) + "\n")
        files["detailed_json"].flush()

    async def _calculate_session_aggregates(self, session_data: SessionData) -> None:
        """Calculate aggregated metrics for a session."""
        turns = session_data.turns
        if not turns:
            return

        # Response time aggregates
        response_times = [t.response_time for t in turns]
        session_data.avg_response_time = sum(response_times) / len(response_times)

        # Quality metric aggregates
        coherence_scores = [
            t.narrative_coherence_score
            for t in turns
            if t.narrative_coherence_score is not None
        ]
        if coherence_scores:
            session_data.avg_narrative_coherence = sum(coherence_scores) / len(
                coherence_scores
            )

        consistency_scores = [
            t.world_consistency_score
            for t in turns
            if t.world_consistency_score is not None
        ]
        if consistency_scores:
            session_data.avg_world_consistency = sum(consistency_scores) / len(
                consistency_scores
            )

        engagement_scores = [
            t.user_engagement_score
            for t in turns
            if t.user_engagement_score is not None
        ]
        if engagement_scores:
            session_data.avg_user_engagement = sum(engagement_scores) / len(
                engagement_scores
            )

        # CPU usage aggregate
        cpu_usages = [
            t.cpu_usage_percent for t in turns if t.cpu_usage_percent is not None
        ]
        if cpu_usages:
            session_data.avg_cpu_usage = sum(cpu_usages) / len(cpu_usages)

        session_data.total_turns = len(turns)

    async def _save_session_data(self, session_data: SessionData) -> None:
        """Save complete session data to file."""
        session_dir = self.output_dir / session_data.session_id
        session_dir.mkdir(exist_ok=True)

        # Save session summary
        summary_file = session_dir / "session_summary.json"
        summary_data = asdict(session_data)

        # Convert datetime objects to strings
        summary_data["start_time"] = session_data.start_time.isoformat()
        if session_data.end_time:
            summary_data["end_time"] = session_data.end_time.isoformat()

        # Convert turn timestamps
        for turn_data in summary_data["turns"]:
            turn_data["timestamp"] = datetime.fromisoformat(
                turn_data["timestamp"]
            ).isoformat()

        with open(summary_file, "w") as f:
            json.dump(summary_data, f, indent=2)

        logger.info(f"Saved session data for {session_data.session_id}")

    async def _close_session_log_files(self, session_id: str) -> None:
        """Close log files for a session."""
        if session_id in self.log_files:
            files = self.log_files[session_id]
            files["turns_csv"].close()
            files["detailed_json"].close()
            del self.log_files[session_id]

    async def export_performance_data(self) -> str:
        """Export performance monitoring data to CSV."""
        if not self.performance_history:
            return ""

        perf_file = self.output_dir / "performance_history.csv"

        with open(perf_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "timestamp",
                    "memory_usage_mb",
                    "cpu_usage_percent",
                    "disk_io_read_mb",
                    "disk_io_write_mb",
                    "network_io_sent_mb",
                    "network_io_recv_mb",
                ]
            )

            for metrics in self.performance_history:
                writer.writerow(
                    [
                        metrics.timestamp.isoformat(),
                        metrics.memory_usage_mb,
                        metrics.cpu_usage_percent,
                        metrics.disk_io_read_mb,
                        metrics.disk_io_write_mb,
                        metrics.network_io_sent_mb,
                        metrics.network_io_recv_mb,
                    ]
                )

        logger.info(f"Exported performance data to {perf_file}")
        return str(perf_file)

    async def generate_data_summary(self) -> dict[str, Any]:
        """Generate a summary of all collected data."""
        summary = {
            "total_sessions": len(self.session_data),
            "total_turns": sum(len(s.turns) for s in self.session_data.values()),
            "total_errors": sum(s.total_errors for s in self.session_data.values()),
            "avg_session_duration": 0.0,
            "avg_turns_per_session": 0.0,
            "performance_data_points": len(self.performance_history),
        }

        if self.session_data:
            durations = [
                s.session_duration_minutes
                for s in self.session_data.values()
                if s.session_duration_minutes > 0
            ]
            if durations:
                summary["avg_session_duration"] = sum(durations) / len(durations)

            turn_counts = [len(s.turns) for s in self.session_data.values()]
            if turn_counts:
                summary["avg_turns_per_session"] = sum(turn_counts) / len(turn_counts)

        return summary

    async def cleanup(self) -> None:
        """Clean up resources and close all files."""
        await self.stop_performance_monitoring()

        # Close any remaining log files
        for session_id in list(self.log_files.keys()):
            await self._close_session_log_files(session_id)

        logger.info("ComprehensiveDataCollector cleanup completed")
