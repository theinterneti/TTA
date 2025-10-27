"""
Redis-based event subscriber for real-time agent orchestration communication.

This module provides event subscription and distribution capabilities using Redis pub/sub,
allowing multiple components to listen for and react to real-time events.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from collections.abc import Callable
from typing import Any
from uuid import uuid4

from redis.asyncio import Redis

from .models import EventType, WebSocketEvent

logger = logging.getLogger(__name__)


class EventSubscriber:
    """Redis-based event subscriber for real-time communication."""

    def __init__(
        self,
        redis_client: Redis,
        channel_prefix: str = "ao:events",
        subscriber_id: str | None = None,
    ):
        self.redis_client = redis_client
        self.channel_prefix = channel_prefix.rstrip(":")
        self.subscriber_id = subscriber_id or uuid4().hex

        # Subscription management
        self.subscriptions: dict[str, set[Callable]] = {}  # channel -> handlers
        self.pubsub = None
        self.subscription_task: asyncio.Task | None = None

        # Statistics
        self.events_received = 0
        self.events_processed = 0
        self.events_failed = 0
        self.is_running = False

        logger.info(f"EventSubscriber initialized: {self.subscriber_id}")

    async def start(self) -> None:
        """Start the event subscriber."""
        if self.is_running:
            return

        try:
            self.pubsub = self.redis_client.pubsub()
            self.subscription_task = asyncio.create_task(self._subscription_loop())
            self.is_running = True
            logger.info(f"EventSubscriber started: {self.subscriber_id}")
        except Exception as e:
            logger.error(f"Failed to start EventSubscriber: {e}")
            raise

    async def stop(self) -> None:
        """Stop the event subscriber."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel subscription task
        if self.subscription_task:
            self.subscription_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.subscription_task

        # Close pubsub connection
        if self.pubsub:
            await self.pubsub.close()
            self.pubsub = None

        logger.info(f"EventSubscriber stopped: {self.subscriber_id}")

    async def subscribe_to_all_events(
        self, handler: Callable[[WebSocketEvent], None]
    ) -> None:
        """Subscribe to all events."""
        await self.subscribe_to_channel(f"{self.channel_prefix}:all", handler)

    async def subscribe_to_event_type(
        self, event_type: EventType, handler: Callable[[WebSocketEvent], None]
    ) -> None:
        """Subscribe to a specific event type."""
        await self.subscribe_to_channel(
            f"{self.channel_prefix}:{event_type.value}", handler
        )

    async def subscribe_to_agent_events(
        self, agent_id: str, handler: Callable[[WebSocketEvent], None]
    ) -> None:
        """Subscribe to events for a specific agent."""
        await self.subscribe_to_channel(
            f"{self.channel_prefix}:agent:{agent_id}", handler
        )

    async def subscribe_to_user_events(
        self, user_id: str, handler: Callable[[WebSocketEvent], None]
    ) -> None:
        """Subscribe to events for a specific user."""
        await self.subscribe_to_channel(
            f"{self.channel_prefix}:user:{user_id}", handler
        )

    async def subscribe_to_channel(
        self, channel: str, handler: Callable[[WebSocketEvent], None]
    ) -> None:
        """Subscribe to a specific Redis channel."""
        if channel not in self.subscriptions:
            self.subscriptions[channel] = set()

            # Subscribe to the channel in Redis
            if self.pubsub:
                await self.pubsub.subscribe(channel)
                logger.debug(f"Subscribed to Redis channel: {channel}")

        # Add handler to the channel
        self.subscriptions[channel].add(handler)
        logger.debug(
            f"Added handler to channel {channel}: {len(self.subscriptions[channel])} total handlers"
        )

    async def unsubscribe_from_channel(
        self, channel: str, handler: Callable[[WebSocketEvent], None] | None = None
    ) -> None:
        """Unsubscribe from a specific Redis channel."""
        if channel not in self.subscriptions:
            return

        if handler:
            # Remove specific handler
            self.subscriptions[channel].discard(handler)
            if not self.subscriptions[channel]:
                # No more handlers, unsubscribe from Redis
                if self.pubsub:
                    await self.pubsub.unsubscribe(channel)
                del self.subscriptions[channel]
                logger.debug(f"Unsubscribed from Redis channel: {channel}")
        else:
            # Remove all handlers and unsubscribe
            if self.pubsub:
                await self.pubsub.unsubscribe(channel)
            del self.subscriptions[channel]
            logger.debug(f"Unsubscribed from Redis channel: {channel}")

    async def _subscription_loop(self) -> None:
        """Main subscription loop that processes incoming events."""
        try:
            while self.is_running and self.pubsub:
                try:
                    # Get message from Redis pubsub
                    message = await self.pubsub.get_message(timeout=1.0)

                    if message is None:
                        continue

                    # Skip subscription confirmation messages
                    if message["type"] not in ["message", "pmessage"]:
                        continue

                    self.events_received += 1

                    # Process the message
                    await self._process_message(message)

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in subscription loop: {e}")
                    self.events_failed += 1
                    await asyncio.sleep(1.0)  # Brief pause before retrying

        except asyncio.CancelledError:
            logger.debug("Subscription loop cancelled")
        except Exception as e:
            logger.error(f"Subscription loop error: {e}")
        finally:
            logger.debug("Subscription loop ended")

    async def _process_message(self, message: dict[str, Any]) -> None:
        """Process a received Redis message."""
        try:
            channel = (
                message["channel"].decode("utf-8")
                if isinstance(message["channel"], bytes)
                else message["channel"]
            )
            data = (
                message["data"].decode("utf-8")
                if isinstance(message["data"], bytes)
                else message["data"]
            )

            # Parse event data
            try:
                event_data = json.loads(data)
                event = WebSocketEvent(**event_data)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse event data: {e}")
                self.events_failed += 1
                return

            # Get handlers for this channel
            handlers = self.subscriptions.get(channel, set())

            if not handlers:
                logger.debug(f"No handlers for channel: {channel}")
                return

            # Call all handlers for this channel
            handler_tasks = []
            for handler in handlers:
                task = asyncio.create_task(self._call_handler(handler, event))
                handler_tasks.append(task)

            # Wait for all handlers to complete
            if handler_tasks:
                results = await asyncio.gather(*handler_tasks, return_exceptions=True)
                success_count = sum(
                    1 for result in results if not isinstance(result, Exception)
                )

                if success_count > 0:
                    self.events_processed += 1

                # Log any handler errors
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(
                            f"Handler {i} failed for channel {channel}: {result}"
                        )
                        self.events_failed += 1

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.events_failed += 1

    async def _call_handler(
        self, handler: Callable[[WebSocketEvent], None], event: WebSocketEvent
    ) -> None:
        """Call an event handler safely."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Event handler error: {e}")
            raise

    def get_statistics(self) -> dict[str, Any]:
        """Get event subscriber statistics."""
        return {
            "subscriber_id": self.subscriber_id,
            "is_running": self.is_running,
            "events_received": self.events_received,
            "events_processed": self.events_processed,
            "events_failed": self.events_failed,
            "active_subscriptions": len(self.subscriptions),
            "total_handlers": sum(
                len(handlers) for handlers in self.subscriptions.values()
            ),
            "subscribed_channels": list(self.subscriptions.keys()),
        }

    async def get_channel_info(self) -> dict[str, Any]:
        """Get information about subscribed channels."""
        channel_info = {}

        for channel, handlers in self.subscriptions.items():
            channel_info[channel] = {
                "handler_count": len(handlers),
                "handler_types": [type(handler).__name__ for handler in handlers],
            }

        return channel_info


class EventDistributor:
    """Distributes events to multiple subscribers and WebSocket connections."""

    def __init__(self, redis_client: Redis, channel_prefix: str = "ao:events"):
        self.redis_client = redis_client
        self.channel_prefix = channel_prefix.rstrip(":")
        self.subscribers: list[EventSubscriber] = []
        self.websocket_managers: set[Any] = set()

        logger.info("EventDistributor initialized")

    def add_subscriber(self, subscriber: EventSubscriber) -> None:
        """Add an event subscriber."""
        self.subscribers.append(subscriber)
        logger.debug(f"Added subscriber: {len(self.subscribers)} total")

    def remove_subscriber(self, subscriber: EventSubscriber) -> None:
        """Remove an event subscriber."""
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)
            logger.debug(f"Removed subscriber: {len(self.subscribers)} remaining")

    def add_websocket_manager(self, manager: Any) -> None:
        """Add a WebSocket manager for event distribution."""
        self.websocket_managers.add(manager)
        logger.debug(f"Added WebSocket manager: {len(self.websocket_managers)} total")

    def remove_websocket_manager(self, manager: Any) -> None:
        """Remove a WebSocket manager."""
        self.websocket_managers.discard(manager)
        logger.debug(
            f"Removed WebSocket manager: {len(self.websocket_managers)} remaining"
        )

    async def start_all_subscribers(self) -> None:
        """Start all registered subscribers."""
        for subscriber in self.subscribers:
            if not subscriber.is_running:
                await subscriber.start()
        logger.info(f"Started {len(self.subscribers)} event subscribers")

    async def stop_all_subscribers(self) -> None:
        """Stop all registered subscribers."""
        for subscriber in self.subscribers:
            if subscriber.is_running:
                await subscriber.stop()
        logger.info(f"Stopped {len(self.subscribers)} event subscribers")

    def get_statistics(self) -> dict[str, Any]:
        """Get distributor statistics."""
        return {
            "total_subscribers": len(self.subscribers),
            "running_subscribers": sum(1 for s in self.subscribers if s.is_running),
            "websocket_managers": len(self.websocket_managers),
            "subscriber_stats": [s.get_statistics() for s in self.subscribers],
        }
