from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .interfaces import MessageCoordinator, AgentProxy
from .models import AgentId, AgentMessage, MessagePriority, MessageType, AgentType
from .messaging import MessageResult, ReceivedMessage, FailureType
from .state import AgentRuntimeStatus
from .performance import get_step_aggregator

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    started_at: float = field(default_factory=time.time)
    requests: int = 0
    errors: int = 0

    def uptime_seconds(self) -> float:
        return max(0.0, time.time() - self.started_at)


class Agent(AgentProxy):
    """
    Base Agent abstraction providing:
    - Standardized async communication helpers (send/receive)
    - Lifecycle (start/stop/health_check)
    - Message (de)serialization helpers
    - Error handling + timeout management

    Concrete agents should override `process()` and optionally `health_check()`.
    """

    def __init__(
        self,
        *,
        agent_id: AgentId,
        name: Optional[str] = None,
        coordinator: Optional[MessageCoordinator] = None,
        default_timeout_s: Optional[float] = 10.0,
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

    async def health_check(self) -> Dict[str, Any]:
        """Basic health check; override for real checks.
        Returns a dict with status and minimal metrics.
        """
        status = "healthy" if self._running and not self._degraded else "degraded" if self._degraded else "stopped"
        return {
            "agent": self.name,
            "agent_id": self.agent_id.model_dump() if hasattr(self.agent_id, "model_dump") else str(self.agent_id),
            "status": status,
            "uptime_s": self._metrics.uptime_seconds(),
            "requests": self._metrics.requests,
            "errors": self._metrics.errors,
        }

    # ---- Communication helpers ----
    def _new_message_id(self) -> str:
        return uuid.uuid4().hex

    def serialize(self, recipient: AgentId, payload: Dict[str, Any], *, priority: MessagePriority = MessagePriority.NORMAL, message_type: MessageType = MessageType.REQUEST) -> AgentMessage:
        return AgentMessage(
            message_id=self._new_message_id(),
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            priority=priority,
        )

    async def send(self, recipient: AgentId, payload: Dict[str, Any], *, priority: MessagePriority = MessagePriority.NORMAL, message_type: MessageType = MessageType.REQUEST) -> MessageResult:
        if not self._coordinator:
            raise RuntimeError("MessageCoordinator not configured for this agent")
        msg = self.serialize(recipient, payload, priority=priority, message_type=message_type)
        return await self._coordinator.send_message(sender=self.agent_id, recipient=recipient, message=msg)

    async def receive_next(self, *, visibility_timeout: int = 5) -> Optional[ReceivedMessage]:
        if not self._coordinator:
            return None
        return await self._coordinator.receive(self.agent_id, visibility_timeout=visibility_timeout)

    async def ack(self, token: str) -> bool:
        if not self._coordinator:
            return False
        return await self._coordinator.ack(self.agent_id, token)

    async def nack(self, token: str, *, failure: FailureType = FailureType.TRANSIENT, error: Optional[str] = None) -> bool:
        if not self._coordinator:
            return False
        return await self._coordinator.nack(self.agent_id, token, failure=failure, error=error)

    # ---- Processing API ----
    async def process(self, input_payload: dict) -> dict:  # abstract in spirit; kept concrete for ease of testing
        raise NotImplementedError

    async def process_with_timeout(self, input_payload: dict, *, timeout_s: Optional[float] = None) -> dict:
        timeout = self._default_timeout_s if timeout_s is None else timeout_s
        self._status = AgentRuntimeStatus.BUSY
        start = time.time()
        key = f"{self.agent_id.type.value}:{self.agent_id.instance or 'default'}"
        try:
            coro = self.process(input_payload)
            result: dict = await asyncio.wait_for(coro, timeout=timeout)
            self._metrics.requests += 1
            # perf aggregation per agent instance
            try:
                get_step_aggregator().record(key, (time.time() - start) * 1000.0, success=True)
            except Exception:
                pass
            return result
        except asyncio.TimeoutError:
            self._metrics.errors += 1
            try:
                get_step_aggregator().record(key, (time.time() - start) * 1000.0, success=False)
            except Exception:
                pass
            raise
        except Exception as e:
            self._metrics.errors += 1
            try:
                get_step_aggregator().record(key, (time.time() - start) * 1000.0, success=False)
            except Exception:
                pass
            logger.exception("Agent %s processing error: %s", self.name, e)
            raise
        finally:
            self._status = AgentRuntimeStatus.IDLE if self._running else AgentRuntimeStatus.ERROR

    # ---- Sync wrappers ----
    def process_sync(self, input_payload: dict, *, timeout_s: Optional[float] = None) -> dict:
        return asyncio.run(self.process_with_timeout(input_payload, timeout_s=timeout_s))

    def health_check_sync(self) -> Dict[str, Any]:
        return asyncio.run(self.health_check())

    # ---- Degradation control ----
    def set_degraded(self, degraded: bool = True) -> None:
        self._degraded = bool(degraded)

    # Convenience status snapshot
    def status_snapshot(self) -> Dict[str, Any]:
        d = {
            "name": self.name,
            "agent_id": self.agent_id.model_dump() if hasattr(self.agent_id, "model_dump") else str(self.agent_id),
            "running": self._running,
            "degraded": self._degraded,
            "status": self._status.value,
            "metrics": {
                "uptime_s": self._metrics.uptime_seconds(),
                "requests": self._metrics.requests,
                "errors": self._metrics.errors,
            },
        }
        return d


class AgentRegistry:
    """
    In-memory registry for agent instances with discovery, dynamic registration,
    and periodic health checking.
    """

    def __init__(self) -> None:
        self._agents: Dict[Tuple[str, str], Agent] = {}
        self._health_task: Optional[asyncio.Task] = None
        self._health_interval_s: float = 15.0

    # Key helpers
    def _key(self, agent_id: AgentId) -> Tuple[str, str]:
        return (agent_id.type.value, agent_id.instance or "default")

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

    def get(self, agent_id: AgentId) -> Optional[Agent]:
        return self._agents.get(self._key(agent_id))

    def discover(self, agent_type: AgentType) -> List[Agent]:
        return [a for (t, _), a in self._agents.items() if t == agent_type.value and a._running and not a._degraded]

    def all(self) -> List[Agent]:
        return list(self._agents.values())

    # Health checks
    async def run_health_checks_once(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
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
    def snapshot(self) -> Dict[str, Any]:
        return {a.name: a.status_snapshot() for a in self._agents.values()}

