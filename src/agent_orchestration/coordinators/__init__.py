"""Message coordination backends (e.g., Redis) will live here."""

# Logseq: [[TTA.dev/Agent_orchestration/Coordinators/__init__]]

from .redis_message_coordinator import RedisMessageCoordinator

__all__ = [
    "RedisMessageCoordinator",
]
