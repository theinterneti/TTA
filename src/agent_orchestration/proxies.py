from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from .agents import Agent
from .interfaces import MessageCoordinator
from .models import AgentId, AgentType
from .messaging import FailureType
from .therapeutic_safety import get_global_safety_service, SafetyLevel
from .adapters import IPAAdapter, WBAAdapter, NGAAdapter, RetryConfig
from .realtime.agent_event_integration import get_agent_event_integrator
from .realtime.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class InputProcessorAgentProxy(Agent):
    """Wraps Input Processor Agent functionality with validation and retry logic."""

    def __init__(self, *, coordinator: Optional[MessageCoordinator] = None, instance: Optional[str] = None, default_timeout_s: float = 8.0, enable_real_agent: bool = True, fallback_to_mock: bool = True, agent_registry=None, event_publisher: Optional[EventPublisher] = None) -> None:
        super().__init__(agent_id=AgentId(type=AgentType.IPA, instance=instance), name=f"ipa:{instance or 'default'}", coordinator=coordinator, default_timeout_s=default_timeout_s)

        # Real agent communication setup
        self.enable_real_agent = enable_real_agent
        self.fallback_to_mock = fallback_to_mock
        self.agent_registry = agent_registry

        if self.enable_real_agent:
            retry_config = RetryConfig(max_retries=3, base_delay=0.5)
            self.ipa_adapter = IPAAdapter(fallback_to_mock=fallback_to_mock, retry_config=retry_config)
        else:
            self.ipa_adapter = None

        # Real-time event integration
        self.event_integrator = get_agent_event_integrator(
            agent_id=str(self.agent_id),
            event_publisher=event_publisher,
            enabled=event_publisher is not None
        )

        # Register with agent registry if provided
        if self.agent_registry:
            try:
                self.agent_registry.register(self)
                logger.info(f"Registered IPA proxy {self.name} with agent registry")
            except Exception as e:
                logger.warning(f"Failed to register with agent registry: {e}")

    async def process(self, input_payload: dict) -> dict:
        # Validate user input
        text = (input_payload or {}).get("text", "").strip()
        if not text:
            raise ValueError("InputProcessorAgentProxy requires non-empty 'text'")

        # Track operation with real-time events
        async with self.event_integrator.track_operation(
            operation_type="input_processing",
            operation_data={"text_length": len(text), "has_context": bool(input_payload.get("context"))}
        ) as operation:

            # Safety validation (annotate only; never block)
            await operation["publish_progress"](0.1, "Performing safety validation")
            safety = get_global_safety_service()
            validation_meta = None
            try:
                res = await safety.validate_text(text)
                validation_meta = res.to_dict()
            except Exception:
                # Fail-open: do not block or raise
                validation_meta = {"error": "safety_validation_failed"}

            # Process through real IPA if available
            if self.enable_real_agent and self.ipa_adapter:
                try:
                    await operation["publish_progress"](0.3, "Processing with real IPA")
                    ipa_result = await self.ipa_adapter.process_input(text)

                    await operation["publish_progress"](0.8, "Merging results with safety validation")

                    # Merge real IPA results with safety validation
                    result = {
                        "normalized_text": ipa_result.get("normalized_text", text),
                        "routing": ipa_result.get("routing", {"intent": "unknown"}),
                        "therapeutic_validation": validation_meta,
                        "raw_intent": ipa_result.get("raw_intent"),
                        "source": ipa_result.get("source", "real_ipa")
                    }

                    await operation["publish_progress"](1.0, "Input processing completed")
                    logger.info(f"IPA processed input with intent: {result['routing'].get('intent', 'unknown')}")
                    return result

                except Exception as e:
                    logger.error(f"Real IPA processing failed: {e}")
                    if not self.fallback_to_mock:
                        raise
                    logger.warning("Falling back to mock implementation")
                    await operation["publish_progress"](0.5, "Falling back to mock implementation")

            # Fallback to mock implementation
            await operation["publish_progress"](0.7, "Using mock implementation")
            routing = {"intent": "unknown"}
            result = {
                "normalized_text": text,
                "routing": routing,
                "therapeutic_validation": validation_meta,
                "source": "mock_fallback"
            }

            await operation["publish_progress"](1.0, "Mock processing completed")
            return result

    async def handle_with_retry(self, payload: dict, *, retries: int = 2, backoff_s: float = 0.5) -> dict:
        attempt = 0
        while True:
            try:
                return await self.process_with_timeout(payload)
            except asyncio.TimeoutError:
                attempt += 1
                if attempt > retries:
                    raise
                await asyncio.sleep(backoff_s * attempt)
            except Exception:
                attempt += 1
                if attempt > retries:
                    raise
                await asyncio.sleep(backoff_s * attempt)

    async def discover_ipa_instances(self) -> List[Dict[str, Any]]:
        """
        Discover available IPA instances through the agent registry.

        Returns:
            List of available IPA instances with their metadata
        """
        if not self.agent_registry:
            return []

        try:
            # Get all registered agents
            registered_agents = await self.agent_registry.list_registered()

            # Filter for IPA instances
            ipa_instances = [
                agent for agent in registered_agents
                if agent.get("agent_id", {}).get("type") == AgentType.IPA.value
                and agent.get("alive", False)
            ]

            logger.debug(f"Discovered {len(ipa_instances)} live IPA instances")
            return ipa_instances

        except Exception as e:
            logger.error(f"Failed to discover IPA instances: {e}")
            return []

    async def select_best_ipa_instance(self) -> Optional[Dict[str, Any]]:
        """
        Select the best available IPA instance based on load and health.

        Returns:
            Best IPA instance metadata or None if none available
        """
        instances = await self.discover_ipa_instances()

        if not instances:
            return None

        # Simple selection: prefer instances with lower load
        # In a real implementation, this could consider more factors
        best_instance = min(
            instances,
            key=lambda x: x.get("status", {}).get("load", 1.0)
        )

        logger.debug(f"Selected IPA instance: {best_instance.get('name', 'unknown')}")
        return best_instance


class WorldBuilderAgentProxy(Agent):
    """Wraps World Builder Agent functionality with world state caching."""

    def __init__(self, *, coordinator: Optional[MessageCoordinator] = None, instance: Optional[str] = None, default_timeout_s: float = 12.0, enable_real_agent: bool = True, fallback_to_mock: bool = True, neo4j_manager=None, tools: Optional[Dict[str, Any]] = None, agent_registry=None, event_publisher: Optional[EventPublisher] = None) -> None:
        super().__init__(agent_id=AgentId(type=AgentType.WBA, instance=instance), name=f"wba:{instance or 'default'}", coordinator=coordinator, default_timeout_s=default_timeout_s)

        # Legacy cache for fallback
        self._cache: Dict[str, Any] = {}
        self._cache_ttl_s = 30.0
        self._cache_times: Dict[str, float] = {}

        # Real agent communication setup
        self.enable_real_agent = enable_real_agent
        self.fallback_to_mock = fallback_to_mock
        self.neo4j_manager = neo4j_manager
        self.tools = tools or {}
        self.agent_registry = agent_registry

        # Real-time event integration
        self.event_integrator = get_agent_event_integrator(
            agent_id=str(self.agent_id),
            event_publisher=event_publisher,
            enabled=event_publisher is not None
        )

        if self.enable_real_agent:
            retry_config = RetryConfig(max_retries=3, base_delay=1.0)
            self.wba_adapter = WBAAdapter(
                neo4j_manager=neo4j_manager,
                tools=tools,
                fallback_to_mock=fallback_to_mock,
                retry_config=retry_config
            )
        else:
            self.wba_adapter = None

        # Register with agent registry if provided
        if self.agent_registry:
            try:
                self.agent_registry.register(self)
                logger.info(f"Registered WBA proxy {self.name} with agent registry")
            except Exception as e:
                logger.warning(f"Failed to register with agent registry: {e}")

    def _cache_get(self, key: str) -> Optional[Any]:
        ts = self._cache_times.get(key)
        if ts is None:
            return None
        if (time.time() - ts) > self._cache_ttl_s:
            self._cache.pop(key, None)
            self._cache_times.pop(key, None)
            return None
        return self._cache.get(key)

    def _cache_set(self, key: str, value: Any) -> None:
        self._cache[key] = value
        self._cache_times[key] = time.time()

    async def process(self, input_payload: dict) -> dict:
        # Expected payload: {"world_id": str, "updates": {...} or None}
        world_id = (input_payload or {}).get("world_id")
        if not world_id:
            raise ValueError("WorldBuilderAgentProxy requires 'world_id'")
        updates = (input_payload or {}).get("updates")

        cache_key = f"world:{world_id}"

        # Check cache first for read operations (no updates)
        if updates is None:
            cached = self._cache_get(cache_key)
            if cached is not None:
                return {"world_id": world_id, "world_state": cached, "cached": True, "source": "cache"}

        # Process through real WBA if available
        if self.enable_real_agent and self.wba_adapter:
            try:
                wba_result = await self.wba_adapter.process_world_request(world_id, updates)

                # Cache the result for performance
                if wba_result.get("world_state"):
                    self._cache_set(cache_key, wba_result["world_state"])

                # Add cached flag for consistency
                wba_result["cached"] = False

                logger.info(f"WBA processed world {world_id} with source: {wba_result.get('source', 'unknown')}")
                return wba_result

            except Exception as e:
                logger.error(f"Real WBA processing failed: {e}")
                if not self.fallback_to_mock:
                    raise
                logger.warning("Falling back to mock implementation")

        # Fallback to mock implementation
        if updates is None:
            # Simulate fetch world state (placeholder)
            world_state = {"id": world_id, "regions": [], "entities": []}
            self._cache_set(cache_key, world_state)
            return {"world_id": world_id, "world_state": world_state, "cached": False, "source": "mock_fallback"}
        # Apply updates (placeholder logic)
        current = self._cache_get(cache_key) or {"id": world_id, "regions": [], "entities": []}
        if isinstance(updates, dict):
            current.update(updates)
        self._cache_set(cache_key, current)
        return {"world_id": world_id, "world_state": current, "updated": True, "source": "mock_fallback"}

    async def handle_concurrent_update(self, world_id: str, updates: Dict[str, Any], version: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle concurrent world state updates with conflict resolution.

        Args:
            world_id: ID of the world to update
            updates: Updates to apply
            version: Optional version for optimistic locking

        Returns:
            Result of the update operation with conflict resolution info
        """
        if self.enable_real_agent and self.wba_adapter:
            try:
                # Real WBA should handle conflict resolution internally
                # For now, we pass through the version info in the updates
                enhanced_updates = updates.copy()
                if version:
                    enhanced_updates["_version"] = version

                result = await self.wba_adapter.process_world_request(world_id, enhanced_updates)

                # Check if conflict was detected and resolved
                if result.get("conflict_resolved"):
                    logger.info(f"Conflict resolved for world {world_id}")

                return result

            except Exception as e:
                logger.error(f"Concurrent update handling failed: {e}")
                if not self.fallback_to_mock:
                    raise

        # Fallback: simple last-write-wins strategy
        logger.warning("Using simple last-write-wins conflict resolution")
        return await self.process({"world_id": world_id, "updates": updates})

    async def get_world_version(self, world_id: str) -> Optional[str]:
        """
        Get the current version of a world state for optimistic locking.

        Args:
            world_id: ID of the world

        Returns:
            Current version string or None if not available
        """
        if self.enable_real_agent and self.wba_adapter:
            try:
                result = await self.wba_adapter.process_world_request(world_id, None)
                return result.get("world_state", {}).get("_version")
            except Exception as e:
                logger.error(f"Failed to get world version: {e}")

        # Fallback: use timestamp as version
        import time
        return str(int(time.time() * 1000))


class NarrativeGeneratorAgentProxy(Agent):
    """Wraps Narrative Generator Agent functionality with content filtering."""

    def __init__(self, *, coordinator: Optional[MessageCoordinator] = None, instance: Optional[str] = None, default_timeout_s: float = 15.0, enable_real_agent: bool = True, fallback_to_mock: bool = True, agent_registry=None, event_publisher: Optional[EventPublisher] = None) -> None:
        super().__init__(agent_id=AgentId(type=AgentType.NGA, instance=instance), name=f"nga:{instance or 'default'}", coordinator=coordinator, default_timeout_s=default_timeout_s)

        # Real agent communication setup
        self.enable_real_agent = enable_real_agent
        self.fallback_to_mock = fallback_to_mock
        self.agent_registry = agent_registry

        # Narrative state tracking
        self._narrative_context: Dict[str, Any] = {}
        self._narrative_history: List[Dict[str, Any]] = []

        if self.enable_real_agent:
            retry_config = RetryConfig(max_retries=3, base_delay=1.5)
            self.nga_adapter = NGAAdapter(fallback_to_mock=fallback_to_mock, retry_config=retry_config)
        else:
            self.nga_adapter = None

        # Real-time event integration
        self.event_integrator = get_agent_event_integrator(
            agent_id=str(self.agent_id),
            event_publisher=event_publisher,
            enabled=event_publisher is not None
        )

        # Register with agent registry if provided
        if self.agent_registry:
            try:
                self.agent_registry.register(self)
                logger.info(f"Registered NGA proxy {self.name} with agent registry")
            except Exception as e:
                logger.warning(f"Failed to register with agent registry: {e}")

    def _filter_content(self, text: str) -> str:
        # Very basic content filtering placeholder; real implementation would use safety policies
        banned = ["violence", "hate"]
        lowered = text.lower()
        for b in banned:
            lowered = lowered.replace(b, "[redacted]")
        return lowered

    async def process(self, input_payload: dict) -> dict:
        # Expected payload: {"prompt": str, "context": {...}}
        prompt = (input_payload or {}).get("prompt", "").strip()
        if not prompt:
            raise ValueError("NarrativeGeneratorAgentProxy requires non-empty 'prompt'")
        context = (input_payload or {}).get("context") or {}
        # Update narrative context
        session_id = context.get("session_id", "default")
        self._update_narrative_context(session_id, prompt, context)

        # Process through real NGA if available
        if self.enable_real_agent and self.nga_adapter:
            try:
                # Enhance context with narrative history
                enhanced_context = context.copy()
                enhanced_context.update({
                    "narrative_context": self._narrative_context.get(session_id, {}),
                    "narrative_history": self._get_recent_narrative_history(session_id, limit=5)
                })

                nga_result = await self.nga_adapter.generate_narrative(prompt, enhanced_context)
                story = nga_result.get("story", "")

                # Track narrative state
                self._track_narrative_state(session_id, prompt, story, enhanced_context)

                # Safety validation for real NGA result
                safety = get_global_safety_service()
                validation_meta = None
                try:
                    res = await safety.validate_text(story)
                    validation_meta = res.to_dict()
                    if res.level == SafetyLevel.BLOCKED:
                        # Replace content with alternative suggestion; ensure supportive language
                        alt = safety.suggest_alternative(SafetyLevel.BLOCKED, story)
                        if "support" not in alt.lower():
                            alt = "I'm here to support you. " + alt
                        return {
                            "story": alt,
                            "raw": story,
                            "context_used": bool(enhanced_context),
                            "therapeutic_validation": validation_meta,
                            "source": nga_result.get("source", "real_nga")
                        }
                except Exception:
                    validation_meta = {"error": "safety_validation_failed"}

                # Apply content filtering to the story
                filtered_story = self._filter_content(story)

                logger.info(f"NGA generated narrative with source: {nga_result.get('source', 'unknown')}")
                return {
                    "story": filtered_story,
                    "raw": nga_result.get("raw", story),
                    "context_used": bool(enhanced_context),
                    "therapeutic_validation": validation_meta,
                    "source": nga_result.get("source", "real_nga")
                }

            except Exception as e:
                logger.error(f"Real NGA processing failed: {e}")
                if not self.fallback_to_mock:
                    raise
                logger.warning("Falling back to mock implementation")

        # Fallback to mock implementation
        story = f"Story: {prompt[:64]}..."
        safety = get_global_safety_service()
        validation_meta = None
        try:
            res = await safety.validate_text(story)
            validation_meta = res.to_dict()
            if res.level == SafetyLevel.BLOCKED:
                # Replace content with alternative suggestion; ensure supportive language
                alt = safety.suggest_alternative(SafetyLevel.BLOCKED, story)
                if "support" not in alt.lower():
                    alt = "I’m here to support you. " + alt
                return {"story": alt, "raw": story, "context_used": bool(context), "therapeutic_validation": validation_meta}
            # WARNING -> annotate only; SAFE -> proceed
        except Exception:
            validation_meta = {"error": "safety_validation_failed"}
        filtered = self._filter_content(story)
        return {"story": filtered, "raw": story, "context_used": bool(context), "therapeutic_validation": validation_meta, "source": "mock_fallback"}

    def _update_narrative_context(self, session_id: str, prompt: str, context: Dict[str, Any]) -> None:
        """Update narrative context for a session."""
        if session_id not in self._narrative_context:
            self._narrative_context[session_id] = {
                "session_start": time.time(),
                "total_interactions": 0,
                "themes": [],
                "characters": [],
                "locations": []
            }

        session_context = self._narrative_context[session_id]
        session_context["total_interactions"] += 1
        session_context["last_prompt"] = prompt
        session_context["last_update"] = time.time()

        # Extract themes, characters, locations from context
        if "world_state" in context:
            world_state = context["world_state"]
            if isinstance(world_state, dict):
                session_context["locations"].extend(world_state.get("regions", []))
                session_context["characters"].extend(world_state.get("entities", []))

    def _get_recent_narrative_history(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent narrative history for a session."""
        session_history = [
            entry for entry in self._narrative_history
            if entry.get("session_id") == session_id
        ]
        return session_history[-limit:] if session_history else []

    def _track_narrative_state(self, session_id: str, prompt: str, story: str, context: Dict[str, Any]) -> None:
        """Track narrative state for continuity."""
        narrative_entry = {
            "session_id": session_id,
            "timestamp": time.time(),
            "prompt": prompt,
            "story": story,
            "context_snapshot": context.copy(),
            "story_length": len(story),
            "themes_detected": self._extract_themes(story),
        }

        self._narrative_history.append(narrative_entry)

        # Keep only recent history (last 100 entries per session)
        session_entries = [e for e in self._narrative_history if e.get("session_id") == session_id]
        if len(session_entries) > 100:
            # Remove oldest entries for this session
            entries_to_remove = session_entries[:-100]
            for entry in entries_to_remove:
                self._narrative_history.remove(entry)

    def _extract_themes(self, story: str) -> List[str]:
        """Extract themes from generated story (simple keyword-based approach)."""
        themes = []
        story_lower = story.lower()

        theme_keywords = {
            "adventure": ["adventure", "journey", "quest", "explore"],
            "friendship": ["friend", "companion", "ally", "together"],
            "mystery": ["mystery", "secret", "hidden", "unknown"],
            "growth": ["learn", "grow", "develop", "change"],
            "courage": ["brave", "courage", "fear", "overcome"]
        }

        for theme, keywords in theme_keywords.items():
            if any(keyword in story_lower for keyword in keywords):
                themes.append(theme)

        return themes

    async def get_narrative_continuity_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get narrative continuity context for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dict containing narrative continuity information
        """
        session_context = self._narrative_context.get(session_id, {})
        recent_history = self._get_recent_narrative_history(session_id, limit=10)

        # Analyze narrative patterns
        themes_frequency = {}
        characters_mentioned = set()
        locations_visited = set()

        for entry in recent_history:
            for theme in entry.get("themes_detected", []):
                themes_frequency[theme] = themes_frequency.get(theme, 0) + 1

            # Extract characters and locations from context
            context_snapshot = entry.get("context_snapshot", {})
            if "world_state" in context_snapshot:
                world_state = context_snapshot["world_state"]
                if isinstance(world_state, dict):
                    characters_mentioned.update(world_state.get("entities", []))
                    locations_visited.update(world_state.get("regions", []))

        return {
            "session_context": session_context,
            "recent_themes": themes_frequency,
            "characters_mentioned": list(characters_mentioned),
            "locations_visited": list(locations_visited),
            "narrative_arc_length": len(recent_history),
            "session_duration": time.time() - session_context.get("session_start", time.time())
        }

    async def format_narrative_output(self, story: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format narrative output with enhanced metadata and structure.

        Args:
            story: Generated story text
            context: Generation context

        Returns:
            Formatted narrative output
        """
        # Basic formatting
        formatted_story = story.strip()

        # Add paragraph breaks for better readability
        if len(formatted_story) > 200:
            # Simple paragraph detection based on sentence endings
            sentences = formatted_story.split('. ')
            if len(sentences) > 3:
                mid_point = len(sentences) // 2
                formatted_story = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])

        # Extract narrative elements
        narrative_elements = {
            "word_count": len(formatted_story.split()),
            "estimated_reading_time": len(formatted_story.split()) / 200,  # ~200 words per minute
            "narrative_tone": self._analyze_narrative_tone(formatted_story),
            "therapeutic_elements": self._identify_therapeutic_elements(formatted_story)
        }

        return {
            "formatted_story": formatted_story,
            "original_story": story,
            "narrative_elements": narrative_elements,
            "generation_context": context,
            "formatting_applied": True
        }

    def _analyze_narrative_tone(self, story: str) -> str:
        """Analyze the tone of the narrative (simple keyword-based approach)."""
        story_lower = story.lower()

        tone_indicators = {
            "hopeful": ["hope", "bright", "positive", "optimistic", "better"],
            "contemplative": ["think", "reflect", "consider", "ponder", "wonder"],
            "adventurous": ["exciting", "thrilling", "adventure", "bold", "daring"],
            "peaceful": ["calm", "serene", "peaceful", "quiet", "gentle"],
            "mysterious": ["mysterious", "strange", "unknown", "hidden", "secret"]
        }

        tone_scores = {}
        for tone, keywords in tone_indicators.items():
            score = sum(1 for keyword in keywords if keyword in story_lower)
            if score > 0:
                tone_scores[tone] = score

        return max(tone_scores, key=tone_scores.get) if tone_scores else "neutral"

    def _identify_therapeutic_elements(self, story: str) -> List[str]:
        """Identify therapeutic elements in the narrative."""
        story_lower = story.lower()
        elements = []

        therapeutic_patterns = {
            "emotional_validation": ["understand", "feel", "emotion", "valid"],
            "problem_solving": ["solution", "solve", "overcome", "handle"],
            "self_reflection": ["realize", "understand", "learn", "discover"],
            "social_connection": ["friend", "support", "together", "help"],
            "resilience": ["strong", "persevere", "continue", "endure"]
        }

        for element, keywords in therapeutic_patterns.items():
            if any(keyword in story_lower for keyword in keywords):
                elements.append(element)

        return elements

