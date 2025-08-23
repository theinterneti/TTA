from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

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
    gpu_memory_bytes: Optional[int] = None
    cpu_threads: Optional[int] = None
    ram_bytes: Optional[int] = None


@dataclass
class ResourceAllocation:
    granted: bool
    reason: Optional[str] = None
    gpu_device_index: Optional[int] = None
    gpu_memory_bytes: int = 0
    cpu_threads: int = 0
    ram_bytes: int = 0


@dataclass
class ResourceUsage:
    cpu_percent: float
    memory_percent: float
    memory_used_bytes: int
    memory_total_bytes: int
    process_cpu_percent: Optional[float] = None
    process_memory_bytes: Optional[int] = None
    # GPU (best-effort)
    gpu_available: bool = False
    gpu_count: int = 0
    gpu_utilization: List[float] = field(default_factory=list)  # percent
    gpu_memory_used_bytes: List[int] = field(default_factory=list)
    gpu_memory_total_bytes: List[int] = field(default_factory=list)


@dataclass
class ResourceUsageReport:
    timestamp: float
    usage: ResourceUsage
    thresholds_exceeded: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkloadMetrics:
    # Minimal fields to drive optimization
    queue_lengths: Dict[str, int] = field(default_factory=dict)  # key: agent_type:instance
    dlq_lengths: Dict[str, int] = field(default_factory=dict)
    step_latency_ms_p50: Dict[str, float] = field(default_factory=dict)  # key: agent_type
    step_error_rates: Dict[str, float] = field(default_factory=dict)  # 0..1


@dataclass
class OptimizationResult:
    actions: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


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
        cpu_thread_limit: Optional[int] = None,
        memory_limit_bytes: Optional[int] = None,
        warn_cpu_percent: float = 85.0,
        warn_mem_percent: float = 85.0,
        crit_cpu_percent: float = 95.0,
        crit_mem_percent: float = 95.0,
        redis_client: Any = None,
        redis_prefix: str = "ao",
    ) -> None:
        self.gpu_memory_limit_fraction = float(max(0.0, min(1.0, gpu_memory_limit_fraction)))
        self.cpu_thread_limit = cpu_thread_limit
        self.memory_limit_bytes = memory_limit_bytes
        self.warn_cpu_percent = warn_cpu_percent
        self.warn_mem_percent = warn_mem_percent
        self.crit_cpu_percent = crit_cpu_percent
        self.crit_mem_percent = crit_mem_percent
        self._redis = redis_client
        self._pfx = redis_prefix.rstrip(":")

        # Internal state
        self._monitoring_task: Optional[asyncio.Task] = None
        self._latest_report: Optional[ResourceUsageReport] = None
        self._emergency_active: bool = False

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
            return ResourceAllocation(granted=True, reason="psutil unavailable; cannot evaluate")

        # CPU check
        if self.cpu_thread_limit is not None and resource_requirements.cpu_threads:
            if resource_requirements.cpu_threads > self.cpu_thread_limit:
                return ResourceAllocation(granted=False, reason="CPU thread request exceeds limit")

        # Memory check
        if resource_requirements.ram_bytes is not None:
            avail_bytes = max(0, usage.memory_total_bytes - usage.memory_used_bytes)
            if resource_requirements.ram_bytes > avail_bytes:
                return ResourceAllocation(granted=False, reason="Insufficient RAM available")

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

        thresholds: Dict[str, Any] = {}
        if usage.cpu_percent >= self.crit_cpu_percent:
            thresholds["cpu"] = {"level": "critical", "value": usage.cpu_percent}
        elif usage.cpu_percent >= self.warn_cpu_percent:
            thresholds["cpu"] = {"level": "warning", "value": usage.cpu_percent}

        if usage.memory_percent >= self.crit_mem_percent:
            thresholds["memory"] = {"level": "critical", "value": usage.memory_percent}
        elif usage.memory_percent >= self.warn_mem_percent:
            thresholds["memory"] = {"level": "warning", "value": usage.memory_percent}

        report = ResourceUsageReport(timestamp=time.time(), usage=usage, thresholds_exceeded=thresholds)
        self._latest_report = report
        # Emergency mode flag
        self._emergency_active = any(v.get("level") == "critical" for v in thresholds.values())
        return report

    async def optimize_allocation(self, current_workload: WorkloadMetrics) -> OptimizationResult:
        actions: List[str] = []
        details: Dict[str, Any] = {}

        # If emergency active, suggest immediate throttling
        if self._emergency_active:
            actions.append("enter_emergency_mode")
            details["emergency"] = True

        # Use queue lengths to recommend instance scaling (logical recommendations)
        hot_agents = {k: v for k, v in current_workload.queue_lengths.items() if v >= 10}
        if hot_agents:
            actions.append("rebalance_queues")
            details["hot_agents"] = hot_agents

        # If step latencies degraded, suggest lowering concurrency or increasing backoff
        slow_agents = {k: v for k, v in current_workload.step_latency_ms_p50.items() if v >= 1500.0}
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
                self._monitoring_task = loop.create_task(self._monitor_loop(interval_seconds))
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
                        logger.error("[ResourceManager] Critical %s usage: %s%%", k, val)
                    elif lvl == "warning":
                        logger.warning("[ResourceManager] Elevated %s usage: %s%%", k, val)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug("Resource monitoring error: %s", e)
            await asyncio.sleep(max(1, int(interval_seconds)))

    # ---- Helpers ----
    def latest_report(self) -> Optional[ResourceUsageReport]:
        return self._latest_report

    def select_instance_by_queue(self, agent_type_value: int) -> Optional[str]:
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

    def _collect_usage(self) -> Optional[ResourceUsage]:
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

    def _evaluate_gpu_request(self, req: ResourceRequirements) -> Tuple[Optional[int], int]:
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

