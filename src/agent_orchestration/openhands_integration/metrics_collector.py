"""
Metrics collector for OpenHands integration.

Provides:
- MetricsCollector: Collects and aggregates metrics
- ExecutionMetrics: Execution metrics
- ModelMetrics: Model performance metrics
- SystemMetrics: System-level metrics
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ExecutionMetrics:
    """Metrics for a single task execution."""

    task_id: str
    model_id: str
    task_type: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    success: bool = False
    error: Optional[str] = None
    quality_score: float = 0.0
    validation_passed: bool = False

    def finalize(self) -> None:
        """Finalize metrics after execution."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000


@dataclass
class ModelMetrics:
    """Aggregated metrics for a model."""

    model_id: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration_ms: float = 0.0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_quality_score: float = 0.0
    validation_pass_rate: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions

    @property
    def avg_duration_ms(self) -> float:
        """Calculate average duration."""
        if self.total_executions == 0:
            return 0.0
        return self.total_duration_ms / self.total_executions

    @property
    def avg_tokens(self) -> float:
        """Calculate average tokens."""
        if self.total_executions == 0:
            return 0.0
        return self.total_tokens / self.total_executions

    @property
    def avg_cost(self) -> float:
        """Calculate average cost."""
        if self.total_executions == 0:
            return 0.0
        return self.total_cost / self.total_executions


@dataclass
class SystemMetrics:
    """System-level metrics."""

    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_cost: float = 0.0
    total_tokens: int = 0
    uptime_seconds: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks

    @property
    def uptime_hours(self) -> float:
        """Calculate uptime in hours."""
        return self.uptime_seconds / 3600


class MetricsCollector:
    """Collects and aggregates metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.executions: list[ExecutionMetrics] = []
        self.model_metrics: dict[str, ModelMetrics] = {}
        self.system_metrics = SystemMetrics()
        self._lock = None  # Can be replaced with asyncio.Lock if needed

    def record_execution(self, metrics: ExecutionMetrics) -> None:
        """Record execution metrics.

        Args:
            metrics: Execution metrics
        """
        metrics.finalize()
        self.executions.append(metrics)

        # Update model metrics
        if metrics.model_id not in self.model_metrics:
            self.model_metrics[metrics.model_id] = ModelMetrics(model_id=metrics.model_id)

        model_metrics = self.model_metrics[metrics.model_id]
        model_metrics.total_executions += 1
        model_metrics.total_duration_ms += metrics.duration_ms
        model_metrics.total_tokens += metrics.tokens_used
        model_metrics.total_cost += metrics.cost

        if metrics.success:
            model_metrics.successful_executions += 1
        else:
            model_metrics.failed_executions += 1

        if metrics.validation_passed:
            model_metrics.validation_pass_rate = (
                model_metrics.validation_pass_rate * 0.9 + 1.0 * 0.1
            )
        else:
            model_metrics.validation_pass_rate = (
                model_metrics.validation_pass_rate * 0.9 + 0.0 * 0.1
            )

        model_metrics.avg_quality_score = (
            model_metrics.avg_quality_score * 0.9 + metrics.quality_score * 0.1
        )
        model_metrics.last_updated = datetime.now(timezone.utc)

        # Update system metrics
        self.system_metrics.total_tasks += 1
        if metrics.success:
            self.system_metrics.completed_tasks += 1
        else:
            self.system_metrics.failed_tasks += 1
        self.system_metrics.total_cost += metrics.cost
        self.system_metrics.total_tokens += metrics.tokens_used

        logger.info(
            f"Recorded execution: {metrics.task_id} "
            f"({metrics.model_id}, {metrics.duration_ms:.0f}ms, "
            f"success={metrics.success})"
        )

    def get_model_metrics(self, model_id: str) -> Optional[ModelMetrics]:
        """Get metrics for a model.

        Args:
            model_id: Model ID

        Returns:
            Model metrics or None
        """
        return self.model_metrics.get(model_id)

    def get_all_model_metrics(self) -> dict[str, ModelMetrics]:
        """Get metrics for all models.

        Returns:
            Dictionary of model metrics
        """
        return self.model_metrics.copy()

    def get_system_metrics(self) -> SystemMetrics:
        """Get system metrics.

        Returns:
            System metrics
        """
        self.system_metrics.uptime_seconds = (
            datetime.now(timezone.utc) - self.system_metrics.start_time
        ).total_seconds()
        return self.system_metrics

    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary.

        Returns:
            Metrics summary
        """
        system = self.get_system_metrics()
        return {
            "system": {
                "total_tasks": system.total_tasks,
                "completed_tasks": system.completed_tasks,
                "failed_tasks": system.failed_tasks,
                "success_rate": f"{system.success_rate * 100:.1f}%",
                "total_cost": f"${system.total_cost:.2f}",
                "total_tokens": system.total_tokens,
                "uptime_hours": f"{system.uptime_hours:.1f}h",
            },
            "models": {
                model_id: {
                    "executions": m.total_executions,
                    "success_rate": f"{m.success_rate * 100:.1f}%",
                    "avg_duration_ms": f"{m.avg_duration_ms:.0f}ms",
                    "avg_tokens": f"{m.avg_tokens:.0f}",
                    "avg_cost": f"${m.avg_cost:.4f}",
                    "avg_quality": f"{m.avg_quality_score:.2f}/5.0",
                }
                for model_id, m in self.model_metrics.items()
            },
        }

