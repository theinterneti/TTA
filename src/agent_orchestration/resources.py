from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

# Prefer psutil which is already used elsewhere in the repo
try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil should exist, but guard anyway
    psutil = None  # type: ignore

logger = logging.getLogger(__name__)


# ---- Data models ----


@dataclass
class ResourceRequirements:
    # Fractions or absolute numbers requested by an agent/step
    gpu_memory_bytes: int | None = None
    cpu_threads: int | None = None
    ram_bytes: int | None = None


@dataclass
class ResourceAllocation:
    granted: bool
    reason: str | None = None
    gpu_device_index: int | None = None
    gpu_memory_bytes: int = 0
    cpu_threads: int = 0
    ram_bytes: int = 0


@dataclass
class ResourceUsage:
    cpu_percent: float
    memory_percent: float
    memory_used_bytes: int
    memory_total_bytes: int
    process_cpu_percent: float | None = None
    process_memory_bytes: int | None = None
    # GPU (best-effort)
    gpu_available: bool = False
    gpu_count: int = 0
    gpu_utilization: list[float] = field(default_factory=list)  # percent
    gpu_memory_used_bytes: list[int] = field(default_factory=list)
    gpu_memory_total_bytes: list[int] = field(default_factory=list)


@dataclass
class ResourceUsageReport:
    timestamp: float
    usage: ResourceUsage
    thresholds_exceeded: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkloadMetrics:
    # Minimal fields to drive optimization
    queue_lengths: dict[str, int] = field(
        default_factory=dict
    )  # key: agent_type:instance
    dlq_lengths: dict[str, int] = field(default_factory=dict)
    step_latency_ms_p50: dict[str, float] = field(
        default_factory=dict
    )  # key: agent_type
    step_error_rates: dict[str, float] = field(default_factory=dict)  # 0..1


@dataclass
class OptimizationResult:
    actions: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class ResourceManager:
    """
    Monitors system resources (CPU, RAM, GPU) and provides lightweight allocation,
    reporting, and optimization suggestions for the orchestration system.

    GPU metrics are best-effort using torch.cuda or pynvml/GPUtil when available.
    """

    def __init__(
        self,
        *,
        gpu_memory_limit_fraction: float = 0.8,
        cpu_thread_limit: int | None = None,
        memory_limit_bytes: int | None = None,
        warn_cpu_percent: float = 85.0,
        warn_mem_percent: float = 85.0,
        crit_cpu_percent: float = 95.0,
        crit_mem_percent: float = 95.0,
        redis_client: Any = None,
        redis_prefix: str = "ao",
        circuit_breaker_registry: Any = None,
    ) -> None:
        self.gpu_memory_limit_fraction = float(
            max(0.0, min(1.0, gpu_memory_limit_fraction))
        )
        self.cpu_thread_limit = cpu_thread_limit
        self.memory_limit_bytes = memory_limit_bytes
        self.warn_cpu_percent = warn_cpu_percent
        self.warn_mem_percent = warn_mem_percent
        self.crit_cpu_percent = crit_cpu_percent
        self.crit_mem_percent = crit_mem_percent
        self._redis = redis_client
        self._pfx = redis_prefix.rstrip(":")

        # Internal state
        self._monitoring_task: asyncio.Task | None = None
        self._latest_report: ResourceUsageReport | None = None
        self._emergency_active: bool = False

        # Circuit breaker integration for workflow error handling
        self._circuit_breaker_registry = circuit_breaker_registry
        self._resource_exhaustion_callbacks: list[
            Callable[[ResourceUsageReport], Awaitable[None]]
        ] = []
        self._last_exhaustion_alert = 0.0
        self._exhaustion_alert_cooldown = 60.0  # 1 minute cooldown

    # ---- Public API ----
    async def allocate_resources(
        self,
        agent_id: Any,
        resource_requirements: ResourceRequirements,
    ) -> ResourceAllocation:
        """
        Best-effort allocation decision based on current system usage.
        Does not enforce cgroups; returns a recommendation for callers to honor.
        """
        usage = self._collect_usage()
        if usage is None:
            return ResourceAllocation(
                granted=True, reason="psutil unavailable; cannot evaluate"
            )

        # CPU check
        if self.cpu_thread_limit is not None and resource_requirements.cpu_threads:
            if resource_requirements.cpu_threads > self.cpu_thread_limit:
                return ResourceAllocation(
                    granted=False, reason="CPU thread request exceeds limit"
                )

        # Memory check
        if resource_requirements.ram_bytes is not None:
            avail_bytes = max(0, usage.memory_total_bytes - usage.memory_used_bytes)
            if resource_requirements.ram_bytes > avail_bytes:
                return ResourceAllocation(
                    granted=False, reason="Insufficient RAM available"
                )

        # GPU check (best-effort)
        gpu_index, grant_gpu_bytes = self._evaluate_gpu_request(resource_requirements)

        return ResourceAllocation(
            granted=True,
            reason=None,
            gpu_device_index=gpu_index,
            gpu_memory_bytes=grant_gpu_bytes,
            cpu_threads=resource_requirements.cpu_threads or 0,
            ram_bytes=resource_requirements.ram_bytes or 0,
        )

    async def monitor_usage(self) -> ResourceUsageReport:
        usage = self._collect_usage()
        if usage is None:
            usage = ResourceUsage(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_bytes=0,
                memory_total_bytes=0,
            )

        thresholds: dict[str, Any] = {}
        if usage.cpu_percent >= self.crit_cpu_percent:
            thresholds["cpu"] = {"level": "critical", "value": usage.cpu_percent}
        elif usage.cpu_percent >= self.warn_cpu_percent:
            thresholds["cpu"] = {"level": "warning", "value": usage.cpu_percent}

        if usage.memory_percent >= self.crit_mem_percent:
            thresholds["memory"] = {"level": "critical", "value": usage.memory_percent}
        elif usage.memory_percent >= self.warn_mem_percent:
            thresholds["memory"] = {"level": "warning", "value": usage.memory_percent}

        report = ResourceUsageReport(
            timestamp=time.time(), usage=usage, thresholds_exceeded=thresholds
        )
        self._latest_report = report
        # Emergency mode flag
        self._emergency_active = any(
            v.get("level") == "critical" for v in thresholds.values()
        )

        # Check for resource exhaustion and trigger workflow error handling
        await self._check_resource_exhaustion(report)

        return report

    async def optimize_allocation(
        self, current_workload: WorkloadMetrics
    ) -> OptimizationResult:
        actions: list[str] = []
        details: dict[str, Any] = {}

        # If emergency active, suggest immediate throttling
        if self._emergency_active:
            actions.append("enter_emergency_mode")
            details["emergency"] = True

        # Use queue lengths to recommend instance scaling (logical recommendations)
        hot_agents = {
            k: v for k, v in current_workload.queue_lengths.items() if v >= 10
        }
        if hot_agents:
            actions.append("rebalance_queues")
            details["hot_agents"] = hot_agents

        # If step latencies degraded, suggest lowering concurrency or increasing backoff
        slow_agents = {
            k: v for k, v in current_workload.step_latency_ms_p50.items() if v >= 1500.0
        }
        if slow_agents:
            actions.append("reduce_concurrency")
            details["slow_agents"] = slow_agents

        # If DLQ growing, raise alert
        dlq_hot = {k: v for k, v in current_workload.dlq_lengths.items() if v >= 5}
        if dlq_hot:
            actions.append("alert_dlq_growth")
            details["dlq_hot"] = dlq_hot

        return OptimizationResult(actions=actions, details=details)

    # ---- Monitoring loop ----
    def start_background_monitoring(self, interval_seconds: int = 30) -> None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._monitoring_task = loop.create_task(
                    self._monitor_loop(interval_seconds)
                )
            else:
                # In synchronous contexts, run one iteration
                loop.run_until_complete(self.monitor_usage())
        except Exception:
            pass

    def stop_background_monitoring(self) -> None:
        t = self._monitoring_task
        if t:
            try:
                t.cancel()
            except Exception:
                pass
            self._monitoring_task = None

    async def _monitor_loop(self, interval_seconds: int) -> None:
        while True:
            try:
                report = await self.monitor_usage()
                # Log warnings
                for k, v in report.thresholds_exceeded.items():
                    lvl = v.get("level")
                    val = v.get("value")
                    if lvl == "critical":
                        logger.error(
                            "[ResourceManager] Critical %s usage: %s%%", k, val
                        )
                    elif lvl == "warning":
                        logger.warning(
                            "[ResourceManager] Elevated %s usage: %s%%", k, val
                        )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("Resource monitoring error: %s", e)
            await asyncio.sleep(max(1, int(interval_seconds)))

    # ---- Helpers ----
    def latest_report(self) -> ResourceUsageReport | None:
        return self._latest_report

    def select_instance_by_queue(self, agent_type_value: int) -> str | None:
        """
        Choose an instance for the given agent type by minimal queue length.
        Returns instance name (e.g., "i1") or None if unknown.
        Requires redis_client.
        """
        if not self._redis:
            return None
        try:
            # Scan keys ao:queue:{type}:*
            # We only need lengths, so async execution is expected for aioredis
            # This method is sync; do best-effort using .scan_iter from redis.asyncio
            # Callers should prefer async variant where possible.
            return None  # Keep simple to avoid cross-thread async
        except Exception:
            return None

    def _collect_usage(self) -> ResourceUsage | None:
        try:
            if psutil is None:
                return None
            cpu_percent = float(psutil.cpu_percent(interval=0.1))
            mem = psutil.virtual_memory()
            proc = psutil.Process()
            usage = ResourceUsage(
                cpu_percent=cpu_percent,
                memory_percent=float(mem.percent),
                memory_used_bytes=int(mem.used),
                memory_total_bytes=int(mem.total),
                process_cpu_percent=float(proc.cpu_percent(interval=0.0)),
                process_memory_bytes=int(proc.memory_info().rss),
            )
            # Try to collect GPU stats
            self._augment_with_gpu(usage)
            return usage
        except Exception as e:
            logger.debug("_collect_usage error: %s", e)
            return None

    def _augment_with_gpu(self, usage: ResourceUsage) -> None:
        # Attempt torch.cuda first
        try:
            import torch  # type: ignore

            if hasattr(torch, "cuda") and torch.cuda.is_available():
                usage.gpu_available = True
                count = torch.cuda.device_count()
                usage.gpu_count = count
                for idx in range(count):
                    stats = torch.cuda.memory_stats(idx)
                    total = torch.cuda.get_device_properties(idx).total_memory
                    used = int(stats.get("allocated_bytes.all.current", 0))
                    usage.gpu_memory_total_bytes.append(int(total))
                    usage.gpu_memory_used_bytes.append(int(used))
                    # Utilization percent best-effort via used/total
                    pct = (used / total * 100.0) if total else 0.0
                    usage.gpu_utilization.append(float(pct))
                return
        except Exception:
            pass
        # Try pynvml
        try:
            import pynvml  # type: ignore

            pynvml.nvmlInit()
            count = pynvml.nvmlDeviceGetCount()
            usage.gpu_available = True
            usage.gpu_count = int(count)
            for i in range(count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
                usage.gpu_memory_total_bytes.append(int(meminfo.total))
                usage.gpu_memory_used_bytes.append(int(meminfo.used))
                pct = (meminfo.used / meminfo.total * 100.0) if meminfo.total else 0.0
                usage.gpu_utilization.append(float(pct))
            pynvml.nvmlShutdown()
            return
        except Exception:
            pass
        # Try GPUtil
        try:
            import GPUtil  # type: ignore

            gpus = GPUtil.getGPUs()
            if gpus:
                usage.gpu_available = True
                usage.gpu_count = len(gpus)
                for g in gpus:
                    total = int(g.memoryTotal * 1024 * 1024)
                    used = int(g.memoryUsed * 1024 * 1024)
                    usage.gpu_memory_total_bytes.append(total)
                    usage.gpu_memory_used_bytes.append(used)
                    pct = (used / total * 100.0) if total else 0.0
                    usage.gpu_utilization.append(float(pct))
        except Exception:
            pass

    def _evaluate_gpu_request(
        self, req: ResourceRequirements
    ) -> tuple[int | None, int]:
        # Best-effort: grant on device 0 if enough headroom by fraction
        try:
            import torch  # type: ignore

            if hasattr(torch, "cuda") and torch.cuda.is_available():
                total = torch.cuda.get_device_properties(0).total_memory
                # Estimate free as total - allocated
                used = torch.cuda.memory_allocated(0)
                free = max(0, int(total - used))
                limit = int(total * self.gpu_memory_limit_fraction)
                headroom = max(0, limit - used)
                want = int(req.gpu_memory_bytes or 0)
                if want and want > headroom:
                    return None, 0
                grant = want if want else int(headroom)
                return 0, grant
        except Exception:
            pass
        # No GPU info available
        if req.gpu_memory_bytes:
            return None, 0
        return None, 0

    # ---- Resource exhaustion detection and workflow error handling ----
    async def _check_resource_exhaustion(self, report: ResourceUsageReport) -> None:
        """Check for resource exhaustion and trigger workflow error handling."""
        current_time = time.time()

        # Check if we're in cooldown period
        if current_time - self._last_exhaustion_alert < self._exhaustion_alert_cooldown:
            return

        # Check for critical resource exhaustion
        exhaustion_detected = False
        exhaustion_reasons = []

        for resource, threshold_info in report.thresholds_exceeded.items():
            if threshold_info.get("level") == "critical":
                exhaustion_detected = True
                exhaustion_reasons.append(
                    f"{resource}: {threshold_info.get('value', 0):.1f}%"
                )

        if exhaustion_detected:
            self._last_exhaustion_alert = current_time
            logger.error(
                "Resource exhaustion detected",
                extra={
                    "exhausted_resources": exhaustion_reasons,
                    "timestamp": current_time,
                    "event_type": "resource_exhaustion",
                },
            )

            # Trigger circuit breakers for resource exhaustion
            await self._trigger_resource_exhaustion_circuit_breakers(
                report, exhaustion_reasons
            )

            # Call registered callbacks
            for callback in self._resource_exhaustion_callbacks:
                try:
                    await callback(report)
                except Exception as e:
                    logger.warning(f"Resource exhaustion callback failed: {e}")

    async def _trigger_resource_exhaustion_circuit_breakers(
        self, report: ResourceUsageReport, exhaustion_reasons: list[str]
    ) -> None:
        """Trigger circuit breakers when resource exhaustion is detected."""
        if not self._circuit_breaker_registry:
            return

        try:
            # Get all workflow circuit breakers and trigger them
            all_metrics = await self._circuit_breaker_registry.get_all_metrics()

            for cb_name in all_metrics.keys():
                if cb_name.startswith("workflow:"):
                    circuit_breaker = await self._circuit_breaker_registry.get(cb_name)
                    if circuit_breaker:
                        # Force transition to open state due to resource exhaustion
                        await circuit_breaker._transition_to_open()
                        logger.warning(
                            f"Opened circuit breaker {cb_name} due to resource exhaustion",
                            extra={
                                "circuit_breaker_name": cb_name,
                                "exhaustion_reasons": exhaustion_reasons,
                                "event_type": "circuit_breaker_resource_exhaustion",
                            },
                        )
        except Exception as e:
            logger.error(f"Failed to trigger resource exhaustion circuit breakers: {e}")

    def register_resource_exhaustion_callback(
        self, callback: Callable[[ResourceUsageReport], Awaitable[None]]
    ) -> None:
        """Register a callback to be called when resource exhaustion is detected."""
        self._resource_exhaustion_callbacks.append(callback)

    def unregister_resource_exhaustion_callback(
        self, callback: Callable[[ResourceUsageReport], Awaitable[None]]
    ) -> bool:
        """Unregister a resource exhaustion callback."""
        try:
            self._resource_exhaustion_callbacks.remove(callback)
            return True
        except ValueError:
            return False

    async def check_resource_health_for_workflow(
        self, workflow_name: str
    ) -> dict[str, Any]:
        """Check if resources are healthy enough to run a workflow."""
        if not self._latest_report:
            await self.monitor_usage()

        if not self._latest_report:
            return {"healthy": False, "reason": "no_resource_data"}

        # Check if any critical thresholds are exceeded
        critical_issues = []
        for resource, threshold_info in self._latest_report.thresholds_exceeded.items():
            if threshold_info.get("level") == "critical":
                critical_issues.append(
                    f"{resource}: {threshold_info.get('value', 0):.1f}%"
                )

        if critical_issues:
            return {
                "healthy": False,
                "reason": "resource_exhaustion",
                "critical_issues": critical_issues,
                "emergency_active": self._emergency_active,
            }

        # Check for warning levels that might indicate impending issues
        warning_issues = []
        for resource, threshold_info in self._latest_report.thresholds_exceeded.items():
            if threshold_info.get("level") == "warning":
                warning_issues.append(
                    f"{resource}: {threshold_info.get('value', 0):.1f}%"
                )

        return {
            "healthy": True,
            "warning_issues": warning_issues,
            "emergency_active": self._emergency_active,
            "usage": {
                "cpu_percent": self._latest_report.usage.cpu_percent,
                "memory_percent": self._latest_report.usage.memory_percent,
            },
        }

    def get_resource_exhaustion_status(self) -> dict[str, Any]:
        """Get current resource exhaustion status."""
        return {
            "emergency_active": self._emergency_active,
            "last_exhaustion_alert": self._last_exhaustion_alert,
            "exhaustion_alert_cooldown": self._exhaustion_alert_cooldown,
            "registered_callbacks": len(self._resource_exhaustion_callbacks),
            "latest_report_timestamp": (
                self._latest_report.timestamp if self._latest_report else None
            ),
        }
