# Logseq: [[TTA.dev/Agent_orchestration/Agents]]
from __future__ import annotations

import asyncio
import contextlib
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from .interfaces import AgentProxy, MessageCoordinator
from .messaging import FailureType, MessageResult, ReceivedMessage
from .models import (
    AgentCapabilitySet,
    AgentId,
    AgentMessage,
    AgentType,
    MessagePriority,
    MessageType,
)
from .performance import get_step_aggregator
from .state import AgentRuntimeStatus

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    started_at: float = field(default_factory=time.time)
    requests: int = 0
    errors: int = 0
    # Sliding window of last N outcomes (True=success, False=error)
    _window: list[bool] = field(default_factory=list)
    _window_size: int = 100

    def set_window_size(self, n: int) -> None:
        try:
            self._window_size = int(n) if int(n) > 0 else 100
            # trim if needed
            if len(self._window) > self._window_size:
                self._window = self._window[-self._window_size :]
        except Exception:
            self._window_size = 100

    def record_success(self) -> None:
        self.requests += 1
        self._window.append(True)
        if len(self._window) > self._window_size:
            self._window.pop(0)

    def record_error(self) -> None:
        self.errors += 1
        self._window.append(False)
        if len(self._window) > self._window_size:
            self._window.pop(0)

    def window_success_rate(self) -> float:
        if not self._window:
            return 1.0
        succ = sum(1 for x in self._window if x)
        return succ / float(len(self._window))

    def uptime_seconds(self) -> float:
        return max(0.0, time.time() - self.started_at)


class Agent(AgentProxy):
    """
    Base Agent abstraction providing:
    - Standardized async communication helpers (send/receive)
    - Lifecycle (start/stop/health_check)
    - Message (de)serialization helpers
    - Error handling + timeout management
    - State preservation hooks (export_state/import_state) for recovery

    Concrete agents should override `process()` and optionally `health_check()` and
    may override `export_state`/`import_state` to persist/restore critical runtime state.
    """

    def __init__(
        self,
        *,
        agent_id: AgentId,
        name: str | None = None,
        coordinator: MessageCoordinator | None = None,
        default_timeout_s: float | None = 10.0,
    ) -> None:
        self.agent_id = agent_id
        self.name = name or f"{agent_id.type.value}:{agent_id.instance or 'default'}"
        self._coordinator = coordinator
        self._default_timeout_s = default_timeout_s
        self._running = False
        self._metrics = AgentMetrics()
        self._status: AgentRuntimeStatus = AgentRuntimeStatus.IDLE
        self._degraded: bool = False

    # ---- Lifecycle ----
    async def start(self) -> None:
        self._running = True
        self._status = AgentRuntimeStatus.IDLE
        self._metrics.started_at = time.time()
        logger.info("Agent %s started", self.name)

    async def stop(self) -> None:
        self._running = False
        self._status = AgentRuntimeStatus.IDLE
        logger.info("Agent %s stopped", self.name)

    async def health_check(self) -> dict[str, Any]:
        """Basic health check; override for real checks.
        Returns a dict with status and minimal metrics.
        """
        status = (
            "healthy"
            if self._running and not self._degraded
            else "degraded"
            if self._degraded
            else "stopped"
        )
        return {
            "agent": self.name,
            "agent_id": (
                self.agent_id.model_dump()
                if hasattr(self.agent_id, "model_dump")
                else str(self.agent_id)
            ),
            "status": status,
            "uptime_s": self._metrics.uptime_seconds(),
            "requests": self._metrics.requests,
            "errors": self._metrics.errors,
        }

    # ---- Communication helpers ----
    def _new_message_id(self) -> str:
        return uuid.uuid4().hex

    def serialize(
        self,
        recipient: AgentId,
        payload: dict[str, Any],
        *,
        priority: MessagePriority = MessagePriority.NORMAL,
        message_type: MessageType = MessageType.REQUEST,
    ) -> AgentMessage:
        return AgentMessage(
            message_id=self._new_message_id(),
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            priority=priority,
        )

    async def send(
        self,
        recipient: AgentId,
        payload: dict[str, Any],
        *,
        priority: MessagePriority = MessagePriority.NORMAL,
        message_type: MessageType = MessageType.REQUEST,
    ) -> MessageResult:
        if not self._coordinator:
            raise RuntimeError("MessageCoordinator not configured for this agent")
        # Route via router if available on coordinator owner (component)
        with contextlib.suppress(Exception):
            from tta_ai.orchestration.router import AgentRouter  # type: ignore

            router = getattr(self._coordinator, "_agent_router", None)
            if router and isinstance(router, AgentRouter):
                recipient = await router.resolve_target(recipient)  # type: ignore[assignment]

        msg = self.serialize(
            recipient, payload, priority=priority, message_type=message_type
        )
        return await self._coordinator.send_message(
            sender=self.agent_id, recipient=recipient, message=msg
        )

    async def receive_next(
        self, *, visibility_timeout: int = 5
    ) -> ReceivedMessage | None:
        if not self._coordinator:
            return None
        return await self._coordinator.receive(
            self.agent_id, visibility_timeout=visibility_timeout
        )

    async def ack(self, token: str) -> bool:
        if not self._coordinator:
            return False
        return await self._coordinator.ack(self.agent_id, token)

    async def nack(
        self,
        token: str,
        *,
        failure: FailureType = FailureType.TRANSIENT,
        error: str | None = None,
    ) -> bool:
        if not self._coordinator:
            return False
        return await self._coordinator.nack(
            self.agent_id, token, failure=failure, error=error
        )

    # ---- Processing API ----
    async def process(
        self, input_payload: dict
    ) -> dict:  # abstract in spirit; kept concrete for ease of testing
        raise NotImplementedError

    async def process_with_timeout(
        self, input_payload: dict, *, timeout_s: float | None = None
    ) -> dict:
        timeout = self._default_timeout_s if timeout_s is None else timeout_s
        self._status = AgentRuntimeStatus.BUSY
        start = time.time()
        key = f"{self.agent_id.type.value}:{self.agent_id.instance or 'default'}"
        try:
            coro = self.process(input_payload)
            result: dict = await asyncio.wait_for(coro, timeout=timeout)
            # sliding window + cumulative
            with contextlib.suppress(Exception):
                self._metrics.record_success()
            # Fallback if record_success fails
            if not hasattr(self._metrics, "requests"):
                self._metrics.requests = 0
            # perf aggregation per agent instance
            with contextlib.suppress(Exception):
                get_step_aggregator().record(
                    key, (time.time() - start) * 1000.0, success=True
                )
            return result
        except TimeoutError:
            with contextlib.suppress(Exception):
                self._metrics.record_error()
            # Fallback if record_error fails
            if not hasattr(self._metrics, "errors"):
                self._metrics.errors = 0
            with contextlib.suppress(Exception):
                get_step_aggregator().record(
                    key, (time.time() - start) * 1000.0, success=False
                )
            raise
        except Exception as e:
            with contextlib.suppress(Exception):
                self._metrics.record_error()
            # Fallback if record_error fails
            if not hasattr(self._metrics, "errors"):
                self._metrics.errors = 0
            with contextlib.suppress(Exception):
                get_step_aggregator().record(
                    key, (time.time() - start) * 1000.0, success=False
                )
            logger.exception("Agent %s processing error: %s", self.name, e)
            raise
        finally:
            self._status = (
                AgentRuntimeStatus.IDLE if self._running else AgentRuntimeStatus.ERROR
            )

    # ---- Sync wrappers ----
    def process_sync(
        self, input_payload: dict, *, timeout_s: float | None = None
    ) -> dict:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(
                self.process_with_timeout(input_payload, timeout_s=timeout_s)
            )
        else:
            raise RuntimeError(
                "process_sync cannot run inside an active event loop; "
                "call process_with_timeout directly from async code"
            )

    def health_check_sync(self) -> dict[str, Any]:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.health_check())
        else:
            raise RuntimeError(
                "health_check_sync cannot run inside an active event loop; "
                "call health_check directly from async code"
            )

    # ---- Degradation control ----
    def set_degraded(self, degraded: bool = True) -> None:
        self._degraded = bool(degraded)

    # Convenience status snapshot
    def status_snapshot(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "agent_id": (
                self.agent_id.model_dump()
                if hasattr(self.agent_id, "model_dump")
                else str(self.agent_id)
            ),
            "running": self._running,
            "degraded": self._degraded,
            "status": self._status.value,
            "metrics": {
                "uptime_s": self._metrics.uptime_seconds(),
                "requests": self._metrics.requests,
                "errors": self._metrics.errors,
            },
        }

    # ---- State preservation hooks ----
    async def export_state(self) -> dict[str, Any]:
        """Return a minimal serializable dict representing agent state.
        Default is empty; proxies may override to include caches or context.
        """
        # Restart policy config/state
        self._restart_policy = {
            "max_attempts_window": (
                int(
                    getattr(self, "_config", {}).get(
                        "agent_orchestration.monitoring.restart_policy.max_attempts_window",
                        5,
                    )
                )
            ),
            "window_seconds": float(
                getattr(self, "_config", {}).get(
                    "agent_orchestration.monitoring.restart_policy.window_seconds", 60.0
                )
                if hasattr(self, "_config")
                else 60.0
            ),
            "backoff_factor": float(
                getattr(self, "_config", {}).get(
                    "agent_orchestration.monitoring.restart_policy.backoff_factor", 2.0
                )
                if hasattr(self, "_config")
                else 2.0
            ),
            "backoff_max": float(
                getattr(self, "_config", {}).get(
                    "agent_orchestration.monitoring.restart_policy.backoff_max", 60.0
                )
                if hasattr(self, "_config")
                else 60.0
            ),
            "circuit_breaker_failures": int(
                getattr(self, "_config", {}).get(
                    "agent_orchestration.monitoring.restart_policy.circuit_breaker_failures",
                    3,
                )
                if hasattr(self, "_config")
                else 3
            ),
        }
        self._restart_history: dict[tuple[str, str], list[float]] = {}
        self._circuit_open: dict[tuple[str, str], bool] = {}

        return {}

    async def import_state(self, state: dict[str, Any]) -> None:
        """Restore internal runtime state from a previously exported dict.
        Default is no-op; proxies may override.
        """
        return

    # ---- Capability Support ----

    async def get_capabilities(self) -> AgentCapabilitySet | None:
        """
        Get the capabilities advertised by this agent.

        Default implementation returns None. Concrete agents should override
        this method to advertise their capabilities for discovery.

        Returns:
            AgentCapabilitySet or None if agent doesn't advertise capabilities
        """
        return None

    def advertises_capabilities(self) -> bool:
        """Check if this agent advertises capabilities for discovery."""
        # This is a synchronous check that can be used without async context
        return hasattr(self, "_capabilities") or hasattr(self, "get_capabilities")


class AgentRegistry:
    """
    In-memory registry for agent instances with discovery, dynamic registration,
    and periodic health checking.
    """

    def __init__(self) -> None:
        self._agents: dict[tuple[str, str], Agent] = {}
        self._health_task: asyncio.Task | None = None
        self._health_interval_s: float = 15.0
        # Restart tracking for failure recovery
        self._restart_attempts: dict[tuple[str, str], int] = {}
        self._last_restart_ts: dict[tuple[str, str], float] = {}
        self._restart_backoff_s: float = 5.0

        # Restart policy configuration
        self._restart_policy: dict[str, Any] = {
            "max_attempts_window": 5,
            "window_seconds": 60.0,
            "backoff_factor": 2.0,
            "backoff_max": 60.0,
            "circuit_breaker_failures": 3,
        }
        self._restart_history: dict[tuple[str, str], list[float]] = {}
        self._circuit_open: dict[tuple[str, str], bool] = {}

        # Optional restart callback supplied by component for concrete restarts
        self._restart_cb: Callable[[Agent], Awaitable[bool]] | None = None
        self._fallback_map: dict[tuple[str, str], tuple[str, str]] = {}
        self._fallback_cb: Callable[[Agent, Agent], Awaitable[bool]] | None = None

    # Key helpers
    def _key(self, agent_id: AgentId) -> tuple[str, str]:
        return (agent_id.type.value, agent_id.instance or "default")

    def set_fallback_callback(
        self, cb: Callable[[Agent, Agent], Awaitable[bool]]
    ) -> None:
        self._fallback_cb = cb

    def set_restart_callback(self, cb: Callable[[Agent], Awaitable[bool]]) -> None:
        self._restart_cb = cb

    # Registration
    def register(self, agent: Agent) -> None:
        k = self._key(agent.agent_id)
        self._agents[k] = agent
        logger.info("Registered agent %s", agent.name)

    def deregister(self, agent_id: AgentId) -> None:
        k = self._key(agent_id)
        if k in self._agents:
            agent = self._agents.pop(k)
            logger.info("Deregistered agent %s", agent.name)

    def get(self, agent_id: AgentId) -> Agent | None:
        return self._agents.get(self._key(agent_id))

    def discover(self, agent_type: AgentType) -> list[Agent]:
        return [
            a
            for (t, _), a in self._agents.items()
            if t == agent_type.value and a._running and not a._degraded
        ]

    def all(self) -> list[Agent]:
        return list(self._agents.values())

    # Health checks
    async def run_health_checks_once(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        for agent in self._agents.values():
            try:
                res = await agent.health_check()
                results[agent.name] = res
                # simple degradation heuristic
                if res.get("status") not in ("healthy", "initializing"):
                    agent.set_degraded(True)
                else:
                    agent.set_degraded(False)
            except Exception as e:
                results[agent.name] = {"status": "error", "error": str(e)}
                agent.set_degraded(True)
        return results

    # Failure detection and basic restart scaffolding
    async def _maybe_restart(self, agent: Agent) -> bool:
        """Attempt restart via component-provided callback, with simple backoff."""
        if not self._restart_cb:
            return False
        key = self._key(agent.agent_id)
        now = time.time()
        last = self._last_restart_ts.get(key, 0.0)
        if (now - last) < self._restart_backoff_s:
            return False
        if not self._enforce_restart_policy(agent):
            return False
        backoff_factor = float(self._restart_policy.get("backoff_factor", 2.0))
        backoff_max = float(self._restart_policy.get("backoff_max", 60.0))
        # Simple exponential backoff using attempts count as exponent
        attempts = int(self._restart_attempts.get(key, 0))
        backoff = min(self._restart_backoff_s * (backoff_factor**attempts), backoff_max)
        # Enforce minimal spacing
        if (now - last) < backoff:
            return False
        ok = False
        try:
            ok = await self._restart_cb(agent)
        finally:
            self._last_restart_ts[key] = now
            self._restart_attempts[key] = self._restart_attempts.get(key, 0) + 1
            self._record_restart_attempt(agent, ok)
        return bool(ok)

    # Restart policy enforcement helpers
    def _enforce_restart_policy(self, agent: Agent) -> bool:
        key = self._key(agent.agent_id)
        now = time.time()
        hist = self._restart_history.get(key, [])
        window = float(self._restart_policy.get("window_seconds", 60.0))
        hist = [t for t in hist if (now - t) <= window]
        max_attempts = int(self._restart_policy.get("max_attempts_window", 5))
        if len(hist) >= max_attempts:
            return False
        self._restart_history[key] = hist
        # Circuit breaker check - return negated condition directly
        return not self._circuit_open.get(key, False)

    def _record_restart_attempt(self, agent: Agent, success: bool) -> None:
        key = self._key(agent.agent_id)
        now = time.time()
        self._restart_history.setdefault(key, []).append(now)
        # Circuit breaker: open if too many consecutive failures
        fails = int(self._restart_policy.get("circuit_breaker_failures", 3))
        if not success:
            consec = getattr(self, "_consec_fail", {})
            c = int(consec.get(key, 0)) + 1
            consec[key] = c
            self._consec_fail = consec
            if c >= fails:
                self._circuit_open[key] = True
        else:
            # reset counter on success
            consec = getattr(self, "_consec_fail", {})
            consec[key] = 0
            self._consec_fail = consec
            self._circuit_open[key] = False

    async def detect_and_recover(self) -> dict[str, Any]:
        """Run a health check sweep and attempt basic recovery actions.
        Heuristic: if agent health_check returns status not healthy/initializing or agent not running, mark degraded and try restart.
        """
        summary: dict[str, Any] = {"checked": 0, "restarted": 0, "degraded": 0}
        for agent in self._agents.values():
            summary["checked"] += 1
            try:
                res = await agent.health_check()
                ok = res.get("status") in ("healthy", "initializing")
                if not ok or not agent._running:
                    agent.set_degraded(True)
                    summary["degraded"] += 1
                    if await self._maybe_restart(agent):
                        summary["restarted"] += 1
                else:
                    agent.set_degraded(False)
            except Exception:
                agent.set_degraded(True)
                summary["degraded"] += 1
                await self._maybe_restart(agent)
        return summary

    def start_periodic_health_checks(self, interval_s: float = 15.0) -> None:
        self._health_interval_s = float(interval_s)
        if self._health_task and not self._health_task.done():
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self._health_task = loop.create_task(self._health_loop())

    async def _health_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(self._health_interval_s)
                await self.run_health_checks_once()
        except asyncio.CancelledError:
            return
        except Exception as e:
            logger.warning("AgentRegistry health loop error: %s", e)

    def stop_periodic_health_checks(self) -> None:
        if self._health_task and not self._health_task.done():
            self._health_task.cancel()

    # Diagnostics snapshot
    def snapshot(self) -> dict[str, Any]:
        return {a.name: a.status_snapshot() for a in self._agents.values()}
