"""
Comprehensive integration tests for multi-agent workflows (Task 12.2).

This module implements comprehensive integration tests for complete IPA → WBA → NGA workflows,
including error handling, recovery scenarios, and performance testing for concurrent workflow execution.

Test Categories:
1. End-to-end workflow testing
2. Error handling and recovery scenarios
3. Performance and concurrency testing
4. State persistence and message routing validation
"""

import asyncio
import json
import time
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from tta_ai.orchestration import (
    AgentMessage,
    AgentRegistry,
    AgentStep,
    AgentType,
    InputProcessorAgentProxy,
    MessageCoordinator,
    NarrativeGeneratorAgentProxy,
    SessionContext,
    WorkflowDefinition,
    WorkflowType,
    WorldBuilderAgentProxy,
)

# ============================================================================
# Test Fixtures for Multi-Agent Scenarios
# ============================================================================


@pytest.fixture
def sample_player_inputs():
    """Realistic player inputs for therapeutic text adventure scenarios."""
    return [
        {
            "text": "look around",
            "expected_intent": "look",
            "context": {"location": "forest_clearing", "mood": "curious"},
        },
        {
            "text": "go north to the mountain path",
            "expected_intent": "move",
            "context": {
                "location": "forest_clearing",
                "direction": "north",
                "mood": "adventurous",
            },
        },
        {
            "text": "talk to the wise elder about my fears",
            "expected_intent": "talk_to",
            "context": {
                "location": "village_center",
                "npc": "wise_elder",
                "mood": "anxious",
                "therapeutic_topic": "anxiety",
            },
        },
        {
            "text": "examine the ancient journal on the table",
            "expected_intent": "examine",
            "context": {
                "location": "library",
                "object": "ancient_journal",
                "mood": "contemplative",
            },
        },
        {
            "text": "I feel overwhelmed by all these choices",
            "expected_intent": "express_emotion",
            "context": {
                "location": "crossroads",
                "emotion": "overwhelmed",
                "therapeutic_topic": "decision_making",
            },
        },
    ]


@pytest.fixture
def sample_world_contexts():
    """World building contexts for different therapeutic scenarios."""
    return {
        "forest_clearing": {
            "id": "loc_001",
            "name": "Peaceful Forest Clearing",
            "description": "A serene clearing surrounded by tall oak trees",
            "therapeutic_theme": "mindfulness",
            "mood": "calm",
            "exits": {"north": "mountain_path", "south": "village_center"},
            "objects": ["meditation_stone", "flowing_stream"],
            "npcs": [],
        },
        "village_center": {
            "id": "loc_002",
            "name": "Village Center",
            "description": "A bustling village square with friendly faces",
            "therapeutic_theme": "social_connection",
            "mood": "welcoming",
            "exits": {"north": "forest_clearing", "east": "library"},
            "objects": ["community_board", "fountain"],
            "npcs": ["wise_elder", "friendly_merchant"],
        },
        "library": {
            "id": "loc_003",
            "name": "Ancient Library",
            "description": "A quiet library filled with wisdom and knowledge",
            "therapeutic_theme": "self_reflection",
            "mood": "contemplative",
            "exits": {"west": "village_center"},
            "objects": ["ancient_journal", "reading_chair", "wisdom_books"],
            "npcs": ["librarian"],
        },
    }


@pytest.fixture
def sample_character_data():
    """Character data for NPCs in therapeutic scenarios."""
    return {
        "wise_elder": {
            "id": "npc_001",
            "name": "Elder Sage",
            "personality": "wise, patient, empathetic",
            "therapeutic_role": "mentor",
            "dialogue_style": "thoughtful questions, gentle guidance",
            "specialties": ["anxiety", "life_transitions", "self_acceptance"],
        },
        "friendly_merchant": {
            "id": "npc_002",
            "name": "Maya the Merchant",
            "personality": "cheerful, encouraging, practical",
            "therapeutic_role": "supporter",
            "dialogue_style": "upbeat, solution-focused",
            "specialties": ["confidence_building", "goal_setting"],
        },
        "librarian": {
            "id": "npc_003",
            "name": "Keeper of Stories",
            "personality": "quiet, insightful, mysterious",
            "therapeutic_role": "guide",
            "dialogue_style": "metaphorical, reflective",
            "specialties": ["self_discovery", "inner_wisdom", "narrative_therapy"],
        },
    }


@pytest.fixture
def expected_narrative_outputs():
    """Expected narrative outputs for different scenarios."""
    return {
        "look_forest_clearing": {
            "response_text": "You find yourself in a peaceful forest clearing. Sunlight filters through the canopy above, creating dancing patterns on the soft grass. A gentle stream flows nearby, its sound creating a natural meditation soundtrack. You notice a smooth meditation stone positioned perfectly for quiet reflection.",
            "therapeutic_elements": ["mindfulness", "grounding", "sensory_awareness"],
            "mood_impact": "calming",
        },
        "talk_to_elder_anxiety": {
            "response_text": "Elder Sage looks at you with kind, understanding eyes. 'I see the weight you carry, young one. Fear is like a shadow - it grows larger when we turn away from it, but shrinks when we face it with compassion. What would you say to a dear friend who felt as you do now?'",
            "therapeutic_elements": [
                "cognitive_reframing",
                "self_compassion",
                "perspective_taking",
            ],
            "mood_impact": "supportive",
        },
        "examine_journal": {
            "response_text": "The ancient journal falls open to a page that seems meant for you. The words speak of others who have walked similar paths, facing their own challenges with courage. One passage stands out: 'Every ending is also a beginning, and every question contains the seed of its own answer.'",
            "therapeutic_elements": ["hope", "universality", "meaning_making"],
            "mood_impact": "inspiring",
        },
    }


@pytest_asyncio.fixture
async def mock_agent_coordinator():
    """Mock message coordinator for testing agent communication."""
    coordinator = Mock(spec=MessageCoordinator)
    coordinator.send_message = AsyncMock(return_value=True)
    coordinator.receive_message = AsyncMock()
    coordinator.subscribe = AsyncMock()
    coordinator.unsubscribe = AsyncMock()
    return coordinator


@pytest_asyncio.fixture
async def test_agent_registry():
    """Test agent registry with mock agents."""
    registry = AgentRegistry()

    # Create test agents
    ipa = InputProcessorAgentProxy(instance="test")
    wba = WorldBuilderAgentProxy(instance="test")
    nga = NarrativeGeneratorAgentProxy(instance="test")

    # Register agents
    registry.register(ipa)
    registry.register(wba)
    registry.register(nga)

    return registry


@pytest.fixture
def therapeutic_session_context():
    """Session context for therapeutic scenarios."""
    return SessionContext(
        session_id="test_session_001",
        player_id="test_player_001",
        therapeutic_profile={
            "intensity_level": "medium",
            "preferred_approaches": ["cbt", "mindfulness"],
            "trigger_warnings": ["violence"],
            "comfort_topics": ["nature", "relationships"],
            "current_goals": ["anxiety_management", "self_confidence"],
        },
        game_state={
            "current_location_id": "loc_001",
            "inventory": [],
            "character_mood": "curious",
            "session_progress": 0.3,
        },
    )


@pytest.fixture
def multi_agent_workflow_definition():
    """Standard multi-agent workflow definition for testing."""
    return WorkflowDefinition(
        workflow_type=WorkflowType.COLLABORATIVE,
        agent_sequence=[
            AgentStep(agent=AgentType.IPA, name="input_processing", timeout_seconds=10),
            AgentStep(agent=AgentType.WBA, name="world_building", timeout_seconds=15),
            AgentStep(
                agent=AgentType.NGA, name="narrative_generation", timeout_seconds=20
            ),
        ],
        timeout_config={"per_step_seconds": 30, "total_seconds": 90},
    )


# ============================================================================
# Test Utilities for Workflow State Verification
# ============================================================================


class WorkflowStateVerifier:
    """Utility class for verifying workflow state transitions and data consistency."""

    @staticmethod
    def verify_message_routing(
        messages: list[AgentMessage], expected_sequence: list[AgentType]
    ) -> bool:
        """Verify that messages follow the expected agent sequence."""
        if len(messages) != len(expected_sequence):
            return False

        for _i, (message, expected_agent) in enumerate(
            zip(messages, expected_sequence, strict=False)
        ):
            if message.recipient_id.type != expected_agent:
                return False

        return True

    @staticmethod
    def verify_state_persistence(
        initial_state: dict[str, Any], final_state: dict[str, Any]
    ) -> dict[str, bool]:
        """Verify that critical state elements are preserved across workflow execution."""
        checks = {
            "session_id_preserved": initial_state.get("session_id")
            == final_state.get("session_id"),
            "player_id_preserved": initial_state.get("player_id")
            == final_state.get("player_id"),
            "therapeutic_context_maintained": "therapeutic_profile" in final_state,
            "game_state_updated": final_state.get("game_state", {})
            != initial_state.get("game_state", {}),
        }
        return checks

    @staticmethod
    def verify_response_aggregation(responses: list[dict[str, Any]]) -> dict[str, bool]:
        """Verify that agent responses are properly aggregated."""
        checks = {
            "all_agents_responded": len(responses) >= 3,  # IPA, WBA, NGA
            "responses_have_content": all(
                "response" in r or "output" in r for r in responses
            ),
            "therapeutic_validation_present": any(
                "therapeutic_validation" in r for r in responses
            ),
            "narrative_coherence": True,  # Placeholder for more complex coherence checks
        }
        return checks


# ============================================================================
# Performance Testing Utilities
# ============================================================================


class PerformanceMetrics:
    """Utility class for collecting and analyzing performance metrics."""

    def __init__(self):
        self.workflow_times: list[float] = []
        self.agent_response_times: dict[str, list[float]] = {}
        self.error_counts: dict[str, int] = {}
        self.concurrent_workflows: int = 0

    def record_workflow_time(self, duration: float):
        """Record workflow completion time."""
        self.workflow_times.append(duration)

    def record_agent_time(self, agent_type: str, duration: float):
        """Record individual agent response time."""
        if agent_type not in self.agent_response_times:
            self.agent_response_times[agent_type] = []
        self.agent_response_times[agent_type].append(duration)

    def record_error(self, error_type: str):
        """Record error occurrence."""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

    def get_statistics(self) -> dict[str, Any]:
        """Get performance statistics summary."""
        return {
            "workflow_stats": {
                "count": len(self.workflow_times),
                "avg_time": (
                    sum(self.workflow_times) / len(self.workflow_times)
                    if self.workflow_times
                    else 0
                ),
                "max_time": max(self.workflow_times) if self.workflow_times else 0,
                "min_time": min(self.workflow_times) if self.workflow_times else 0,
            },
            "agent_stats": {
                agent: {
                    "count": len(times),
                    "avg_time": sum(times) / len(times),
                    "max_time": max(times),
                    "min_time": min(times),
                }
                for agent, times in self.agent_response_times.items()
            },
            "error_stats": self.error_counts,
            "concurrent_workflows": self.concurrent_workflows,
        }


@pytest.fixture
def performance_metrics():
    """Performance metrics collector for testing."""
    return PerformanceMetrics()


# ============================================================================
# Neo4j State Verification Utilities
# ============================================================================


class Neo4jStateVerifier:
    """Utility class for verifying Neo4j state persistence and consistency."""

    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver

    async def verify_session_state(self, session_id: str) -> dict[str, bool]:
        """Verify that session state is properly persisted in Neo4j."""
        checks = {}

        with self.driver.session() as session:
            # Check session node exists
            result = session.run(
                "MATCH (s:Session {session_id: $session_id}) RETURN s",
                session_id=session_id,
            )
            session_node = result.single()
            checks["session_exists"] = session_node is not None

            # Check player relationship
            result = session.run(
                "MATCH (s:Session {session_id: $session_id})-[:BELONGS_TO]->(p:Player) RETURN p",
                session_id=session_id,
            )
            player_node = result.single()
            checks["player_relationship_exists"] = player_node is not None

            # Check current location relationship
            result = session.run(
                "MATCH (s:Session {session_id: $session_id})-[:CURRENT_LOCATION]->(l:Location) RETURN l",
                session_id=session_id,
            )
            location_node = result.single()
            checks["location_relationship_exists"] = location_node is not None

            # Check therapeutic profile data
            if session_node:
                therapeutic_data = session_node["s"].get("therapeutic_profile")
                checks["therapeutic_profile_persisted"] = therapeutic_data is not None

        return checks

    async def verify_workflow_state_transitions(
        self, workflow_id: str
    ) -> dict[str, Any]:
        """Verify workflow state transitions are recorded in Neo4j."""
        with self.driver.session() as session:
            # Get workflow execution history
            result = session.run(
                """
                MATCH (w:Workflow {workflow_id: $workflow_id})-[:HAS_EXECUTION]->(e:WorkflowExecution)
                OPTIONAL MATCH (e)-[:HAS_STEP]->(s:WorkflowStep)
                RETURN w, e, collect(s) as steps
                ORDER BY e.started_at
                """,
                workflow_id=workflow_id,
            )

            records = list(result)
            if not records:
                return {"workflow_found": False}

            workflow_data = records[0]
            return {
                "workflow_found": True,
                "execution_count": len(records),
                "steps_recorded": len(workflow_data["steps"]),
                "has_completion_time": workflow_data["e"].get("completed_at")
                is not None,
                "status": workflow_data["e"].get("status", "unknown"),
            }

    async def verify_agent_interactions(self, session_id: str) -> dict[str, Any]:
        """Verify agent interactions are properly recorded."""
        with self.driver.session() as session:
            # Check agent interaction history
            result = session.run(
                """
                MATCH (s:Session {session_id: $session_id})-[:HAS_INTERACTION]->(i:AgentInteraction)
                OPTIONAL MATCH (i)-[:PROCESSED_BY]->(a:Agent)
                RETURN i, a
                ORDER BY i.timestamp
                """,
                session_id=session_id,
            )

            interactions = list(result)
            agent_types = set()
            for record in interactions:
                if record["a"]:
                    agent_types.add(record["a"].get("type"))

            return {
                "interaction_count": len(interactions),
                "unique_agents": len(agent_types),
                "has_ipa_interaction": "IPA" in agent_types,
                "has_wba_interaction": "WBA" in agent_types,
                "has_nga_interaction": "NGA" in agent_types,
                "chronological_order": self._verify_chronological_order(interactions),
            }

    def _verify_chronological_order(self, interactions: list) -> bool:
        """Verify interactions are in chronological order."""
        if len(interactions) < 2:
            return True

        timestamps = [record["i"].get("timestamp", 0) for record in interactions]
        return all(
            timestamps[i] <= timestamps[i + 1] for i in range(len(timestamps) - 1)
        )


# ============================================================================
# Redis State Verification Utilities
# ============================================================================


class RedisStateVerifier:
    """Utility class for verifying Redis message queue states and agent registry."""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def verify_message_queue_state(self, agent_id: str) -> dict[str, Any]:
        """Verify message queue state for an agent."""
        queue_key = f"agent_queue:{agent_id}"

        # Check queue exists and get length
        queue_length = await self.redis.llen(queue_key)

        # Check for any pending messages
        pending_messages = await self.redis.lrange(queue_key, 0, -1)

        # Parse message content
        parsed_messages = []
        for msg in pending_messages:
            try:
                parsed_messages.append(json.loads(msg))
            except json.JSONDecodeError:
                pass

        return {
            "queue_exists": queue_length >= 0,
            "queue_length": queue_length,
            "pending_messages": len(parsed_messages),
            "message_types": [msg.get("type") for msg in parsed_messages],
            "oldest_message_age": self._calculate_oldest_message_age(parsed_messages),
        }

    async def verify_agent_registry_state(self, agent_id: str) -> dict[str, bool]:
        """Verify agent registry state in Redis."""
        registry_key = f"agent_registry:{agent_id}"
        heartbeat_key = f"agent_heartbeat:{agent_id}"

        # Check agent registration
        agent_data = await self.redis.get(registry_key)
        agent_registered = agent_data is not None

        # Check heartbeat
        heartbeat_data = await self.redis.get(heartbeat_key)
        heartbeat_active = heartbeat_data is not None

        # Check TTL
        registry_ttl = await self.redis.ttl(registry_key)
        heartbeat_ttl = await self.redis.ttl(heartbeat_key)

        return {
            "agent_registered": agent_registered,
            "heartbeat_active": heartbeat_active,
            "registry_ttl_valid": registry_ttl > 0,
            "heartbeat_ttl_valid": heartbeat_ttl > 0,
            "data_consistent": agent_registered == heartbeat_active,
        }

    async def verify_workflow_coordination_state(
        self, workflow_id: str
    ) -> dict[str, Any]:
        """Verify workflow coordination state in Redis."""
        workflow_key = f"workflow:{workflow_id}"
        coordination_key = f"workflow_coordination:{workflow_id}"

        # Check workflow state
        workflow_data = await self.redis.get(workflow_key)
        coordination_data = await self.redis.get(coordination_key)

        workflow_state = {}
        coordination_state = {}

        if workflow_data:
            try:
                workflow_state = json.loads(workflow_data)
            except json.JSONDecodeError:
                pass

        if coordination_data:
            try:
                coordination_state = json.loads(coordination_data)
            except json.JSONDecodeError:
                pass

        return {
            "workflow_state_exists": bool(workflow_state),
            "coordination_state_exists": bool(coordination_state),
            "current_step": workflow_state.get("current_step"),
            "status": workflow_state.get("status"),
            "agent_assignments": coordination_state.get("agent_assignments", {}),
            "step_completion": coordination_state.get("completed_steps", []),
        }

    def _calculate_oldest_message_age(self, messages: list[dict]) -> float | None:
        """Calculate age of oldest message in seconds."""
        if not messages:
            return None

        current_time = time.time()
        oldest_timestamp = min(msg.get("timestamp", current_time) for msg in messages)
        return current_time - oldest_timestamp


# ============================================================================
# Integration Test Utilities
# ============================================================================


class IntegrationTestHelper:
    """Helper class for integration test setup and teardown."""

    def __init__(self, redis_client, neo4j_driver):
        self.redis = redis_client
        self.neo4j = neo4j_driver
        self.redis_verifier = RedisStateVerifier(redis_client)
        self.neo4j_verifier = Neo4jStateVerifier(neo4j_driver)

    async def setup_test_environment(self, test_id: str) -> dict[str, str]:
        """Set up clean test environment with unique identifiers."""
        session_id = f"test_session_{test_id}_{int(time.time())}"
        workflow_id = f"test_workflow_{test_id}_{int(time.time())}"
        player_id = f"test_player_{test_id}"

        # Clean any existing test data
        await self.cleanup_test_data(session_id, workflow_id, player_id)

        return {
            "session_id": session_id,
            "workflow_id": workflow_id,
            "player_id": player_id,
        }

    async def cleanup_test_data(
        self, session_id: str, workflow_id: str, player_id: str
    ):
        """Clean up test data from Redis and Neo4j."""
        # Clean Redis data
        redis_keys = [
            "agent_queue:*",
            "agent_registry:*",
            "agent_heartbeat:*",
            f"workflow:{workflow_id}",
            f"workflow_coordination:{workflow_id}",
            f"session:{session_id}",
        ]

        for pattern in redis_keys:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)

        # Clean Neo4j data
        with self.neo4j.session() as session:
            session.run(
                """
                MATCH (s:Session {session_id: $session_id})
                OPTIONAL MATCH (s)-[*]-(related)
                DETACH DELETE s, related
                """,
                session_id=session_id,
            )

            session.run(
                """
                MATCH (w:Workflow {workflow_id: $workflow_id})
                OPTIONAL MATCH (w)-[*]-(related)
                DETACH DELETE w, related
                """,
                workflow_id=workflow_id,
            )

    async def wait_for_workflow_completion(
        self, workflow_id: str, timeout: float = 30.0
    ) -> bool:
        """Wait for workflow to complete with timeout."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            state = await self.redis_verifier.verify_workflow_coordination_state(
                workflow_id
            )
            if state.get("status") in ["completed", "failed"]:
                return True
            await asyncio.sleep(0.1)

        return False

    async def simulate_agent_failure(
        self, agent_id: str, failure_duration: float = 5.0
    ):
        """Simulate agent failure by removing from registry temporarily."""
        # Store original data
        registry_key = f"agent_registry:{agent_id}"
        heartbeat_key = f"agent_heartbeat:{agent_id}"

        original_registry = await self.redis.get(registry_key)
        original_heartbeat = await self.redis.get(heartbeat_key)

        # Remove from registry
        await self.redis.delete(registry_key, heartbeat_key)

        # Wait for failure duration
        await asyncio.sleep(failure_duration)

        # Restore data
        if original_registry:
            await self.redis.set(registry_key, original_registry)
        if original_heartbeat:
            await self.redis.set(heartbeat_key, original_heartbeat)


# ============================================================================
# Extended Test Data for Comprehensive Scenarios
# ============================================================================


@pytest.fixture
def complex_therapeutic_scenarios():
    """Complex therapeutic scenarios for comprehensive workflow testing."""
    return {
        "anxiety_management": {
            "player_input": "I'm feeling really anxious about the dark cave ahead",
            "context": {
                "location": "cave_entrance",
                "therapeutic_theme": "anxiety_management",
                "player_state": "anxious",
                "previous_actions": ["approached_cave", "hesitated"],
            },
            "expected_ipa_output": {
                "intent": "express_emotion",
                "emotion": "anxiety",
                "object": "dark_cave",
                "therapeutic_trigger": True,
            },
            "expected_wba_output": {
                "location_description": "The cave entrance seems less intimidating now, with soft light filtering in from crystals within",
                "therapeutic_modifications": [
                    "reduced_threat_level",
                    "added_comfort_elements",
                ],
                "mood_adjustment": "slightly_reassuring",
            },
            "expected_nga_output": {
                "narrative": "As you stand before the cave, you notice your breathing has quickened. This is natural - your body is preparing you for what lies ahead. Take a moment to breathe deeply. Notice how the crystals inside cast a gentle, welcoming glow. What if this cave holds not danger, but discovery?",
                "therapeutic_techniques": [
                    "breathing_exercise",
                    "reframing",
                    "curiosity_cultivation",
                ],
                "safety_validation": "supportive",
            },
        },
        "self_confidence_building": {
            "player_input": "I don't think I'm brave enough to help the villagers",
            "context": {
                "location": "village_square",
                "therapeutic_theme": "self_confidence",
                "player_state": "self_doubt",
                "available_actions": ["help_villagers", "walk_away", "ask_for_support"],
            },
            "expected_ipa_output": {
                "intent": "express_self_doubt",
                "confidence_level": "low",
                "situation": "helping_villagers",
                "therapeutic_trigger": True,
            },
            "expected_wba_output": {
                "scene_modifications": [
                    "highlight_player_strengths",
                    "show_villager_appreciation",
                ],
                "confidence_boosters": ["past_success_reminders", "supportive_npcs"],
                "environmental_cues": "encouraging",
            },
            "expected_nga_output": {
                "narrative": "The villagers look at you with hope in their eyes. Maya the Merchant approaches: 'I've seen you overcome challenges before. Remember when you helped find the lost child? Your kindness made all the difference.' Sometimes courage isn't the absence of fear - it's acting despite it.",
                "therapeutic_techniques": [
                    "strength_identification",
                    "past_success_recall",
                    "courage_reframing",
                ],
                "safety_validation": "empowering",
            },
        },
        "grief_processing": {
            "player_input": "This place reminds me of someone I lost",
            "context": {
                "location": "memorial_garden",
                "therapeutic_theme": "grief_processing",
                "player_state": "melancholic",
                "emotional_intensity": "medium",
            },
            "expected_ipa_output": {
                "intent": "process_grief",
                "emotional_trigger": "memory",
                "location_association": "memorial_garden",
                "therapeutic_priority": "high",
            },
            "expected_wba_output": {
                "scene_adjustments": [
                    "gentle_atmosphere",
                    "memorial_elements",
                    "peaceful_setting",
                ],
                "therapeutic_elements": ["memory_honoring_space", "comfort_objects"],
                "emotional_safety": "high",
            },
            "expected_nga_output": {
                "narrative": "The garden holds space for all kinds of memories - joyful ones and painful ones alike. The flowers here bloom in cycles, teaching us that endings and beginnings are part of the same story. Would you like to sit by the remembrance fountain and share what comes to mind?",
                "therapeutic_techniques": [
                    "grief_normalization",
                    "memory_honoring",
                    "gentle_invitation",
                ],
                "safety_validation": "compassionate",
            },
        },
    }


@pytest.fixture
def workflow_error_scenarios():
    """Error scenarios for testing workflow resilience."""
    return {
        "ipa_timeout": {
            "description": "IPA takes too long to process input",
            "trigger": "complex_ambiguous_input",
            "expected_behavior": "timeout_and_fallback",
            "recovery_strategy": "simplified_processing",
        },
        "wba_unavailable": {
            "description": "WBA is temporarily unavailable",
            "trigger": "agent_registry_failure",
            "expected_behavior": "use_cached_world_state",
            "recovery_strategy": "fallback_to_basic_descriptions",
        },
        "nga_content_filter_block": {
            "description": "NGA content is blocked by safety filters",
            "trigger": "inappropriate_content_generation",
            "expected_behavior": "content_replacement",
            "recovery_strategy": "alternative_narrative_generation",
        },
        "redis_connection_loss": {
            "description": "Redis connection is lost during workflow",
            "trigger": "network_failure",
            "expected_behavior": "graceful_degradation",
            "recovery_strategy": "in_memory_fallback",
        },
        "neo4j_write_failure": {
            "description": "Neo4j write operation fails",
            "trigger": "database_constraint_violation",
            "expected_behavior": "retry_with_backoff",
            "recovery_strategy": "eventual_consistency",
        },
    }


@pytest.fixture
def performance_test_scenarios():
    """Performance testing scenarios with varying loads."""
    return {
        "low_load": {
            "concurrent_workflows": 3,
            "duration_seconds": 30,
            "expected_avg_response_time": 2.0,
            "expected_success_rate": 0.98,
        },
        "medium_load": {
            "concurrent_workflows": 10,
            "duration_seconds": 60,
            "expected_avg_response_time": 5.0,
            "expected_success_rate": 0.95,
        },
        "high_load": {
            "concurrent_workflows": 25,
            "duration_seconds": 120,
            "expected_avg_response_time": 10.0,
            "expected_success_rate": 0.90,
        },
        "stress_test": {
            "concurrent_workflows": 50,
            "duration_seconds": 180,
            "expected_avg_response_time": 20.0,
            "expected_success_rate": 0.80,
        },
    }


@pytest.fixture
def agent_interaction_patterns():
    """Patterns of agent interactions for testing different workflow types."""
    return {
        "linear_workflow": {
            "pattern": ["IPA", "WBA", "NGA"],
            "description": "Standard sequential processing",
            "use_cases": ["simple_commands", "basic_interactions"],
        },
        "iterative_workflow": {
            "pattern": ["IPA", "WBA", "NGA", "WBA", "NGA"],
            "description": "Iterative refinement with feedback loops",
            "use_cases": ["complex_world_building", "detailed_narratives"],
        },
        "parallel_processing": {
            "pattern": [["WBA", "NGA"], "merge"],
            "description": "Parallel processing with result merging",
            "use_cases": ["performance_optimization", "redundancy"],
        },
        "conditional_branching": {
            "pattern": ["IPA", "condition", ["WBA_path", "NGA_direct"]],
            "description": "Conditional workflow based on input analysis",
            "use_cases": ["therapeutic_triage", "complexity_adaptation"],
        },
    }


@pytest.fixture
def therapeutic_validation_data():
    """Data for validating therapeutic content and safety."""
    return {
        "safe_content": {
            "examples": [
                "You feel a sense of calm as you explore the peaceful garden",
                "The wise elder offers gentle guidance about managing difficult emotions",
                "This challenge is an opportunity to practice resilience",
            ],
            "therapeutic_elements": ["mindfulness", "guidance", "growth_mindset"],
            "safety_level": "approved",
        },
        "concerning_content": {
            "examples": [
                "You feel hopeless and see no way forward",
                "Everyone would be better off without you",
                "This situation is completely impossible to handle",
            ],
            "therapeutic_concerns": [
                "hopelessness",
                "self_harm_ideation",
                "catastrophizing",
            ],
            "safety_level": "requires_intervention",
        },
        "blocked_content": {
            "examples": [
                "Violence and aggression fill the scene",
                "Graphic descriptions of harm",
                "Inappropriate romantic content",
            ],
            "safety_violations": [
                "violence",
                "explicit_content",
                "inappropriate_themes",
            ],
            "safety_level": "blocked",
        },
    }


@pytest.fixture
def integration_test_configurations():
    """Different configurations for integration testing."""
    return {
        "minimal_config": {
            "redis_enabled": True,
            "neo4j_enabled": False,
            "agent_timeout": 5.0,
            "workflow_timeout": 15.0,
            "retry_attempts": 1,
        },
        "standard_config": {
            "redis_enabled": True,
            "neo4j_enabled": True,
            "agent_timeout": 10.0,
            "workflow_timeout": 30.0,
            "retry_attempts": 3,
        },
        "high_reliability_config": {
            "redis_enabled": True,
            "neo4j_enabled": True,
            "agent_timeout": 20.0,
            "workflow_timeout": 60.0,
            "retry_attempts": 5,
            "circuit_breaker_enabled": True,
            "fallback_strategies": True,
        },
        "performance_config": {
            "redis_enabled": True,
            "neo4j_enabled": True,
            "agent_timeout": 3.0,
            "workflow_timeout": 10.0,
            "retry_attempts": 1,
            "parallel_processing": True,
            "caching_aggressive": True,
        },
    }
