"""

# Logseq: [[TTA.dev/Agent_orchestration/Protocol_bridge]]
Protocol bridge for translating between orchestration system messages and real agent communication.

This module provides message routing and protocol translation capabilities to enable
seamless communication between the orchestration system and real agent implementations.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .adapters import AgentCommunicationError, IPAAdapter, NGAAdapter, WBAAdapter
from .messaging import MessageResult
from .models import AgentMessage, AgentType

logger = logging.getLogger(__name__)


class ProtocolType(str, Enum):
    """Supported communication protocols."""

    ORCHESTRATION = "orchestration"  # Internal orchestration system protocol
    REAL_AGENT = "real_agent"  # Real agent implementation protocol
    HYBRID = "hybrid"  # Mixed protocol support


@dataclass
class MessageTranslationResult:
    """Result of message protocol translation."""

    success: bool
    translated_message: dict[str, Any] | None = None
    error: str | None = None
    protocol_used: ProtocolType | None = None


class ProtocolTranslator:
    """Translates messages between different agent communication protocols."""

    def __init__(self):
        self._translation_rules: dict[str, Callable] = {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default translation rules for common message types."""
        self._translation_rules.update(
            {
                "orchestration_to_ipa": self._translate_to_ipa_format,
                "orchestration_to_wba": self._translate_to_wba_format,
                "orchestration_to_nga": self._translate_to_nga_format,
                "ipa_to_orchestration": self._translate_from_ipa_format,
                "wba_to_orchestration": self._translate_from_wba_format,
                "nga_to_orchestration": self._translate_from_nga_format,
            }
        )

    def translate_message(
        self,
        message: AgentMessage | dict[str, Any],
        source_protocol: ProtocolType,
        target_protocol: ProtocolType,
        agent_type: AgentType,
    ) -> MessageTranslationResult:
        """
        Translate a message between different protocols.

        Args:
            message: Message to translate
            source_protocol: Source protocol type
            target_protocol: Target protocol type
            agent_type: Type of agent for protocol-specific translation

        Returns:
            MessageTranslationResult with translation outcome
        """
        try:
            # Convert AgentMessage to dict if needed
            if isinstance(message, AgentMessage):
                message_dict = message.model_dump()
            else:
                message_dict = message

            # Determine translation rule
            rule_key = f"{source_protocol.value}_to_{target_protocol.value}"
            if agent_type:
                specific_rule_key = (
                    f"{source_protocol.value}_to_{agent_type.value.lower()}"
                )
                if specific_rule_key in self._translation_rules:
                    rule_key = specific_rule_key

            # Apply translation rule
            if rule_key in self._translation_rules:
                translated = self._translation_rules[rule_key](message_dict)
                return MessageTranslationResult(
                    success=True,
                    translated_message=translated,
                    protocol_used=target_protocol,
                )
            # No specific rule, pass through with minimal transformation
            return MessageTranslationResult(
                success=True,
                translated_message=message_dict,
                protocol_used=ProtocolType.HYBRID,
            )

        except Exception as e:
            logger.error(f"Message translation failed: {e}")
            return MessageTranslationResult(success=False, error=str(e))

    def _translate_to_ipa_format(self, message: dict[str, Any]) -> dict[str, Any]:
        """Translate orchestration message to IPA format."""
        payload = message.get("payload", {})
        return {
            "text": payload.get("text", payload.get("input", "")),
            "session_id": payload.get("session_id"),
            "context": payload.get("context", {}),
            "metadata": {
                "message_id": message.get("message_id"),
                "timestamp": message.get("timestamp"),
                "sender": message.get("sender"),
            },
        }

    def _translate_to_wba_format(self, message: dict[str, Any]) -> dict[str, Any]:
        """Translate orchestration message to WBA format."""
        payload = message.get("payload", {})
        return {
            "world_id": payload.get("world_id", payload.get("session_id", "default")),
            "updates": payload.get("updates"),
            "action": payload.get("action", "fetch"),
            "context": payload.get("context", {}),
            "metadata": {
                "message_id": message.get("message_id"),
                "timestamp": message.get("timestamp"),
                "sender": message.get("sender"),
            },
        }

    def _translate_to_nga_format(self, message: dict[str, Any]) -> dict[str, Any]:
        """Translate orchestration message to NGA format."""
        payload = message.get("payload", {})
        return {
            "prompt": payload.get("prompt", payload.get("text", "")),
            "context": payload.get("context", {}),
            "player_input": payload.get("text", payload.get("input", "")),
            "session_id": payload.get("session_id"),
            "metadata": {
                "message_id": message.get("message_id"),
                "timestamp": message.get("timestamp"),
                "sender": message.get("sender"),
            },
        }

    def _translate_from_ipa_format(self, result: dict[str, Any]) -> dict[str, Any]:
        """Translate IPA result to orchestration format."""
        return {
            "success": True,
            "result": {
                "normalized_text": result.get("normalized_text"),
                "routing": result.get("routing", {}),
                "therapeutic_validation": result.get("therapeutic_validation"),
                "raw_intent": result.get("raw_intent"),
                "source": result.get("source", "ipa"),
            },
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _translate_from_wba_format(self, result: dict[str, Any]) -> dict[str, Any]:
        """Translate WBA result to orchestration format."""
        return {
            "success": True,
            "result": {
                "world_id": result.get("world_id"),
                "world_state": result.get("world_state"),
                "updated": result.get("updated", False),
                "cached": result.get("cached", False),
                "source": result.get("source", "wba"),
            },
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _translate_from_nga_format(self, result: dict[str, Any]) -> dict[str, Any]:
        """Translate NGA result to orchestration format."""
        return {
            "success": True,
            "result": {
                "story": result.get("story"),
                "raw": result.get("raw"),
                "context_used": result.get("context_used", False),
                "therapeutic_validation": result.get("therapeutic_validation"),
                "source": result.get("source", "nga"),
            },
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat(),
        }


class MessageRouter:
    """Routes messages between orchestration system and real agents."""

    def __init__(
        self, ipa_adapter: IPAAdapter, wba_adapter: WBAAdapter, nga_adapter: NGAAdapter
    ):
        self.ipa_adapter = ipa_adapter
        self.wba_adapter = wba_adapter
        self.nga_adapter = nga_adapter
        self.translator = ProtocolTranslator()
        self._routing_table: dict[AgentType, Callable] = {
            AgentType.IPA: self._route_to_ipa,
            AgentType.WBA: self._route_to_wba,
            AgentType.NGA: self._route_to_nga,
        }

    async def route_message(
        self, agent_type: AgentType, message: AgentMessage | dict[str, Any]
    ) -> MessageResult:
        """
        Route a message to the appropriate real agent.

        Args:
            agent_type: Type of agent to route to
            message: Message to route

        Returns:
            MessageResult indicating routing outcome
        """
        try:
            # Get routing handler
            handler = self._routing_table.get(agent_type)
            if not handler:
                return MessageResult(
                    message_id=self._get_message_id(message),
                    delivered=False,
                    error=f"No routing handler for agent type: {agent_type}",
                )

            # Route message
            return await handler(message)

        except Exception as e:
            logger.error(f"Message routing failed for {agent_type}: {e}")
            return MessageResult(
                message_id=self._get_message_id(message), delivered=False, error=str(e)
            )

    async def _route_to_ipa(
        self, message: AgentMessage | dict[str, Any]
    ) -> MessageResult:
        """Route message to IPA adapter."""
        try:
            # Translate message to IPA format
            translation = self.translator.translate_message(
                message,
                ProtocolType.ORCHESTRATION,
                ProtocolType.REAL_AGENT,
                AgentType.IPA,
            )

            if not translation.success:
                return MessageResult(
                    message_id=self._get_message_id(message),
                    delivered=False,
                    error=f"Translation failed: {translation.error}",
                )

            # Extract text for IPA processing
            translated_msg = translation.translated_message
            text = translated_msg.get("text", "")

            if not text:
                return MessageResult(
                    message_id=self._get_message_id(message),
                    delivered=False,
                    error="No text provided for IPA processing",
                )

            # Process through IPA adapter
            await self.ipa_adapter.process_input(text)

            return MessageResult(
                message_id=self._get_message_id(message), delivered=True, error=None
            )

        except AgentCommunicationError as e:
            return MessageResult(
                message_id=self._get_message_id(message), delivered=False, error=str(e)
            )

    async def _route_to_wba(
        self, message: AgentMessage | dict[str, Any]
    ) -> MessageResult:
        """Route message to WBA adapter."""
        try:
            # Translate message to WBA format
            translation = self.translator.translate_message(
                message,
                ProtocolType.ORCHESTRATION,
                ProtocolType.REAL_AGENT,
                AgentType.WBA,
            )

            if not translation.success:
                return MessageResult(
                    message_id=self._get_message_id(message),
                    delivered=False,
                    error=f"Translation failed: {translation.error}",
                )

            # Extract parameters for WBA processing
            translated_msg = translation.translated_message
            world_id = translated_msg.get("world_id", "default")
            updates = translated_msg.get("updates")

            # Process through WBA adapter
            await self.wba_adapter.process_world_request(world_id, updates)

            return MessageResult(
                message_id=self._get_message_id(message), delivered=True, error=None
            )

        except AgentCommunicationError as e:
            return MessageResult(
                message_id=self._get_message_id(message), delivered=False, error=str(e)
            )

    async def _route_to_nga(
        self, message: AgentMessage | dict[str, Any]
    ) -> MessageResult:
        """Route message to NGA adapter."""
        try:
            # Translate message to NGA format
            translation = self.translator.translate_message(
                message,
                ProtocolType.ORCHESTRATION,
                ProtocolType.REAL_AGENT,
                AgentType.NGA,
            )

            if not translation.success:
                return MessageResult(
                    message_id=self._get_message_id(message),
                    delivered=False,
                    error=f"Translation failed: {translation.error}",
                )

            # Extract parameters for NGA processing
            translated_msg = translation.translated_message
            prompt = translated_msg.get("prompt", "")
            context = translated_msg.get("context", {})

            if not prompt:
                return MessageResult(
                    message_id=self._get_message_id(message),
                    delivered=False,
                    error="No prompt provided for NGA processing",
                )

            # Process through NGA adapter
            await self.nga_adapter.generate_narrative(prompt, context)

            return MessageResult(
                message_id=self._get_message_id(message), delivered=True, error=None
            )

        except AgentCommunicationError as e:
            return MessageResult(
                message_id=self._get_message_id(message), delivered=False, error=str(e)
            )

    def _get_message_id(self, message: AgentMessage | dict[str, Any]) -> str:
        """Extract message ID from message."""
        if isinstance(message, AgentMessage):
            return message.message_id
        if isinstance(message, dict):
            return message.get("message_id", str(uuid.uuid4()))
        return str(uuid.uuid4())
