from __future__ import annotations

import asyncio
import json
import logging
import time
import math
from typing import Any, Dict, List, Optional, Tuple

from redis.asyncio import Redis

from ..agents import Agent, AgentRegistry
from ..models import AgentId, AgentType

logger = logging.getLogger(__name__)


class RedisAgentRegistry(AgentRegistry):
    """
    Redis-backed AgentRegistry adapter.

    Keys:
      - {pfx}:agents:{type}:{instance} -> JSON payload
      - {pfx}:agents:index -> set of keys

    Liveness:
      - Store last_heartbeat timestamp; liveness = now - last_heartbeat <= ttl
      - Background heartbeats update registered agents periodically
    """

    def __init__(self, redis: Redis, key_prefix: str = "ao", heartbeat_ttl_s: float = 30.0, heartbeat_interval_s: Optional[float] = None) -> None:
        super().__init__()
        self._redis = redis
        self._pfx = key_prefix.rstrip(":")
        self._ttl = float(heartbeat_ttl_s)
        self._hb_task: Optional[asyncio.Task] = None
        self._hb_interval_s: float = float(heartbeat_interval_s) if heartbeat_interval_s is not None else max(1.0, heartbeat_ttl_s / 3.0)

    # ---- Key helpers ----
    def _key(self, agent_id: AgentId) -> str:
        return f"{self._pfx}:agents:{agent_id.type.value}:{agent_id.instance or 'default'}"

    def _index_key(self) -> str:
        return f"{self._pfx}:agents:index"

    # ---- Overrides ----
    def register(self, agent: Agent) -> None:
        super().register(agent)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._persist(agent))
        except RuntimeError:
            asyncio.run(self._persist(agent))

    def deregister(self, agent_id: AgentId) -> None:
        super().deregister(agent_id)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._delete(agent_id))
        except RuntimeError:
            asyncio.run(self._delete(agent_id))

    async def _persist(self, agent: Agent) -> None:
        key = self._key(agent.agent_id)
        try:
            payload = {
                "name": agent.name,
                "agent_id": agent.agent_id.model_dump() if hasattr(agent.agent_id, "model_dump") else str(agent.agent_id),
                "status": agent.status_snapshot(),
                "last_heartbeat": time.time(),
            }
            px = max(1, int(self._ttl * 1000))
            await self._redis.set(key, json.dumps(payload), px=px)
            await self._redis.sadd(self._index_key(), key)
        except Exception as e:
            logger.warning("Failed to persist agent registration: %s", e)

    async def _delete(self, agent_id: AgentId) -> None:
        key = self._key(agent_id)
        try:
            await self._redis.delete(key)
            await self._redis.srem(self._index_key(), key)
        except Exception:
            pass

    # ---- Heartbeats ----
    def start_heartbeats(self) -> None:
        if self._hb_task and not self._hb_task.done():
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self._hb_task = loop.create_task(self._heartbeat_loop())

    def stop_heartbeats(self) -> None:
        if self._hb_task and not self._hb_task.done():
            self._hb_task.cancel()

    async def _heartbeat_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(self._hb_interval_s)
                await self._heartbeat_once()
        except asyncio.CancelledError:
            return
        except Exception as e:
            logger.warning("RedisAgentRegistry heartbeat error: %s", e)

    async def _heartbeat_once(self) -> None:
        for agent in self.all():
            await self._heartbeat_agent(agent)

    async def _heartbeat_agent(self, agent: Agent) -> None:
        key = self._key(agent.agent_id)
        try:
            # Refresh TTL and last_heartbeat; embed current status snapshot
            payload = {
                "name": agent.name,
                "agent_id": agent.agent_id.model_dump() if hasattr(agent.agent_id, "model_dump") else str(agent.agent_id),
                "status": agent.status_snapshot(),
                "last_heartbeat": time.time(),
            }
            px = max(1, int(self._ttl * 1000))
            await self._redis.set(key, json.dumps(payload), px=px)
        except Exception:
            pass

    # ---- Discovery across processes ----
    async def list_registered(self) -> List[Dict[str, Any]]:
        try:
            keys = await self._redis.smembers(self._index_key())
            agents: List[Dict[str, Any]] = []
            for bkey in keys:
                k = bkey.decode() if isinstance(bkey, (bytes, bytearray)) else bkey
                val = await self._redis.get(k)
                if not val:
                    continue
                try:
                    data = json.loads(val)
                except Exception:
                    continue
                # Liveness calculation
                last = float(data.get("last_heartbeat", 0.0))
                data["alive"] = (time.time() - last) <= self._ttl
                agents.append(data)
            return agents
        except Exception:
            return []

    async def snapshot_async(self) -> Dict[str, Any]:
        """Async snapshot combining local in-memory and redis-discovered agents."""
        local = super().snapshot()
        remote = await self.list_registered()
        return {"local": local, "redis_index": remote}

