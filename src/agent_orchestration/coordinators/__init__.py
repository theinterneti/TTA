"""Message coordination backends (e.g., Redis) will live here."""

from .redis_message_coordinator import RedisMessageCoordinator

__all__ = [
    "RedisMessageCoordinator",
]
