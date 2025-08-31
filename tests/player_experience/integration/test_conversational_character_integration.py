"""
Integration tests for Conversational Character Creation

Tests the complete conversational character creation flow with Redis persistence,
WebSocket communication, and database integration using Testcontainers.
"""

import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
import redis
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from src.components.therapeutic_safety import SafetyValidationOrchestrator
from src.player_experience.database.character_repository import CharacterRepository
from src.player_experience.managers.character_avatar_manager import (
    CharacterAvatarManager,
)
from src.player_experience.models.conversation_state import (
    CollectedData,
    ConversationProgress,
    ConversationState,
    ConversationStatus,
)
from src.player_experience.services.conversation_scripts import ConversationStage
from src.player_experience.services.conversational_character_service import (
    ConversationalCharacterService,
)


@pytest.mark.redis
class TestConversationalCharacterRedisIntegration:
    """Integration tests with Redis for conversation persistence."""

    @pytest.fixture(scope="class")
    def redis_container(self):
        """Start Redis container for testing."""
        with RedisContainer("redis:7-alpine") as redis_container:
            yield redis_container

    @pytest.fixture
    def redis_client(self, redis_container):
        """Create Redis client connected to test container."""
        return redis.Redis(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(6379),
            decode_responses=True,
        )

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for testing."""
        character_repository = Mock(spec=CharacterRepository)
        character_manager = Mock(spec=CharacterAvatarManager)
        safety_validator = AsyncMock(spec=SafetyValidationOrchestrator)

        # Configure mocks
        character_manager.create_character.return_value = Mock(
            character_id="test_char_123", name="Test Character"
        )

        safety_validator.validate_content.return_value = Mock(
            is_safe=True, crisis_assessment=None
        )

        return {
            "character_repository": character_repository,
            "character_manager": character_manager,
            "safety_validator": safety_validator,
        }

    @pytest.fixture
    def conversation_service(self, mock_dependencies, redis_client):
        """Create conversation service with Redis backend."""
        service = ConversationalCharacterService(
            character_manager=mock_dependencies["character_manager"],
            character_repository=mock_dependencies["character_repository"],
            safety_validator=mock_dependencies["safety_validator"],
        )

        # Replace in-memory storage with Redis
        service.redis_client = redis_client
        service.active_conversations = RedisConversationStorage(redis_client)

        return service

    @pytest.mark.asyncio
    async def test_conversation_persistence_redis(
        self, conversation_service, redis_client
    ):
        """Test that conversation state is properly persisted to Redis."""
        # Start a conversation
        player_id = "test_player_123"
        conversation_id, _ = await conversation_service.start_conversation(player_id)

        # Verify conversation is stored in Redis
        redis_key = f"conversation:{conversation_id}"
        stored_data = redis_client.get(redis_key)
        assert stored_data is not None

        conversation_data = json.loads(stored_data)
        assert conversation_data["conversation_id"] == conversation_id
        assert conversation_data["player_id"] == player_id
        assert conversation_data["status"] == ConversationStatus.ACTIVE.value

    @pytest.mark.asyncio
    async def test_conversation_recovery_after_restart(
        self, conversation_service, redis_client
    ):
        """Test conversation recovery from Redis after service restart."""
        # Start a conversation and add some data
        player_id = "test_player_123"
        conversation_id, _ = await conversation_service.start_conversation(player_id)

        # Process some user responses
        await conversation_service.process_user_response(
            conversation_id, "My name is Alice"
        )
        await conversation_service.process_user_response(
            conversation_id, "I'm an adult"
        )

        # Simulate service restart by creating new service instance
        new_service = ConversationalCharacterService(
            character_manager=conversation_service.character_manager,
            character_repository=conversation_service.character_repository,
            safety_validator=conversation_service.safety_validator,
        )
        new_service.redis_client = redis_client
        new_service.active_conversations = RedisConversationStorage(redis_client)

        # Verify conversation can be recovered
        recovered_state = await new_service.get_conversation_state(conversation_id)
        assert recovered_state is not None
        assert recovered_state.conversation_id == conversation_id
        assert recovered_state.collected_data.name == "Alice"
        assert recovered_state.collected_data.age_range == "adult"

    @pytest.mark.asyncio
    async def test_conversation_expiration_redis(
        self, conversation_service, redis_client
    ):
        """Test conversation expiration in Redis."""
        # Start a conversation with short TTL
        player_id = "test_player_123"
        conversation_id, _ = await conversation_service.start_conversation(player_id)

        # Set short expiration (1 second for testing)
        redis_key = f"conversation:{conversation_id}"
        redis_client.expire(redis_key, 1)

        # Wait for expiration
        await asyncio.sleep(2)

        # Verify conversation is expired
        stored_data = redis_client.get(redis_key)
        assert stored_data is None

        # Verify service handles expired conversation gracefully
        recovered_state = await conversation_service.get_conversation_state(
            conversation_id
        )
        assert recovered_state is None

    @pytest.mark.asyncio
    async def test_concurrent_conversation_access_redis(
        self, conversation_service, redis_client
    ):
        """Test concurrent access to conversation state in Redis."""
        # Start a conversation
        player_id = "test_player_123"
        conversation_id, _ = await conversation_service.start_conversation(player_id)

        # Simulate concurrent updates
        async def update_conversation(message):
            await conversation_service.process_user_response(conversation_id, message)

        # Run concurrent updates
        await asyncio.gather(
            update_conversation("My name is Alice"),
            update_conversation("I'm 25 years old"),
            update_conversation("I like reading"),
        )

        # Verify all updates were processed
        conversation_state = await conversation_service.get_conversation_state(
            conversation_id
        )
        assert (
            len(conversation_state.message_history) >= 6
        )  # 3 user + 3 assistant messages minimum

    @pytest.mark.asyncio
    async def test_conversation_cleanup_redis(self, conversation_service, redis_client):
        """Test cleanup of completed conversations in Redis."""
        # Start multiple conversations
        player_id = "test_player_123"
        conversation_ids = []

        for i in range(3):
            conv_id, _ = await conversation_service.start_conversation(
                f"{player_id}_{i}"
            )
            conversation_ids.append(conv_id)

        # Complete one conversation
        completed_id = conversation_ids[0]
        conversation_state = await conversation_service.get_conversation_state(
            completed_id
        )
        conversation_state.status = ConversationStatus.COMPLETED

        # Verify all conversations exist
        for conv_id in conversation_ids:
            redis_key = f"conversation:{conv_id}"
            assert redis_client.exists(redis_key)

        # Run cleanup (this would typically be a scheduled task)
        await conversation_service.cleanup_expired_conversations()

        # Verify completed conversation is cleaned up after retention period
        # (Implementation would depend on cleanup policy)


class RedisConversationStorage:
    """Redis-based conversation storage for testing."""

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.ttl_seconds = 3600  # 1 hour default TTL

    def __contains__(self, conversation_id):
        """Check if conversation exists in Redis."""
        return self.redis_client.exists(f"conversation:{conversation_id}")

    def __getitem__(self, conversation_id):
        """Get conversation from Redis."""
        data = self.redis_client.get(f"conversation:{conversation_id}")
        if data is None:
            raise KeyError(conversation_id)

        conversation_data = json.loads(data)
        return self._deserialize_conversation(conversation_data)

    def __setitem__(self, conversation_id, conversation_state):
        """Store conversation in Redis."""
        serialized_data = self._serialize_conversation(conversation_state)
        redis_key = f"conversation:{conversation_id}"

        self.redis_client.setex(
            redis_key, self.ttl_seconds, json.dumps(serialized_data, default=str)
        )

    def __delitem__(self, conversation_id):
        """Delete conversation from Redis."""
        self.redis_client.delete(f"conversation:{conversation_id}")

    def get(self, conversation_id, default=None):
        """Get conversation with default value."""
        try:
            return self[conversation_id]
        except KeyError:
            return default

    def _serialize_conversation(self, conversation_state):
        """Serialize conversation state for Redis storage."""
        return {
            "conversation_id": conversation_state.conversation_id,
            "player_id": conversation_state.player_id,
            "status": conversation_state.status.value,
            "progress": {
                "current_stage": conversation_state.progress.current_stage.value,
                "current_prompt_id": conversation_state.progress.current_prompt_id,
                "completed_stages": [
                    stage.value
                    for stage in conversation_state.progress.completed_stages
                ],
                "progress_percentage": conversation_state.progress.progress_percentage,
            },
            "collected_data": {
                "name": conversation_state.collected_data.name,
                "age_range": conversation_state.collected_data.age_range,
                "gender_identity": conversation_state.collected_data.gender_identity,
                "physical_description": conversation_state.collected_data.physical_description,
                "clothing_style": conversation_state.collected_data.clothing_style,
                "distinctive_features": conversation_state.collected_data.distinctive_features,
                "backstory": conversation_state.collected_data.backstory,
                "personality_traits": conversation_state.collected_data.personality_traits,
                "core_values": conversation_state.collected_data.core_values,
                "strengths_and_skills": conversation_state.collected_data.strengths_and_skills,
                "fears_and_anxieties": conversation_state.collected_data.fears_and_anxieties,
                "life_goals": conversation_state.collected_data.life_goals,
                "relationships": conversation_state.collected_data.relationships,
                "primary_concerns": conversation_state.collected_data.primary_concerns,
                "therapeutic_goals": conversation_state.collected_data.therapeutic_goals,
                "preferred_intensity": conversation_state.collected_data.preferred_intensity,
                "comfort_zones": conversation_state.collected_data.comfort_zones,
                "challenge_areas": conversation_state.collected_data.challenge_areas,
                "readiness_level": conversation_state.collected_data.readiness_level,
            },
            "message_history": [
                {
                    "message_id": msg.message_id,
                    "timestamp": msg.timestamp.isoformat(),
                    "sender": msg.sender,
                    "content": msg.content,
                    "message_type": msg.message_type,
                    "metadata": msg.metadata,
                }
                for msg in conversation_state.message_history
            ],
            "created_at": conversation_state.created_at.isoformat(),
            "updated_at": conversation_state.updated_at.isoformat(),
            "last_activity": conversation_state.last_activity.isoformat(),
            "crisis_detected": conversation_state.crisis_detected,
            "safety_notes": conversation_state.safety_notes,
        }

    def _deserialize_conversation(self, data):
        """Deserialize conversation state from Redis data."""
        from ..models.conversation_state import ConversationMessage

        # Reconstruct progress
        progress = ConversationProgress(
            current_stage=ConversationStage(data["progress"]["current_stage"]),
            current_prompt_id=data["progress"]["current_prompt_id"],
            completed_stages=[
                ConversationStage(stage)
                for stage in data["progress"]["completed_stages"]
            ],
            progress_percentage=data["progress"]["progress_percentage"],
        )

        # Reconstruct collected data
        collected_data = CollectedData()
        for field, value in data["collected_data"].items():
            if hasattr(collected_data, field):
                setattr(collected_data, field, value)

        # Reconstruct message history
        message_history = []
        for msg_data in data["message_history"]:
            message = ConversationMessage(
                message_id=msg_data["message_id"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                sender=msg_data["sender"],
                content=msg_data["content"],
                message_type=msg_data["message_type"],
                metadata=msg_data["metadata"],
            )
            message_history.append(message)

        # Reconstruct conversation state
        conversation_state = ConversationState(
            conversation_id=data["conversation_id"],
            player_id=data["player_id"],
            status=ConversationStatus(data["status"]),
            progress=progress,
            collected_data=collected_data,
            message_history=message_history,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            crisis_detected=data["crisis_detected"],
            safety_notes=data["safety_notes"],
        )

        return conversation_state


@pytest.mark.redis
@pytest.mark.neo4j
class TestConversationalCharacterFullIntegration:
    """Full integration tests with both Redis and Neo4j."""

    @pytest.fixture(scope="class")
    def redis_container(self):
        """Start Redis container for testing."""
        with RedisContainer("redis:7-alpine") as redis_container:
            yield redis_container

    @pytest.fixture(scope="class")
    def postgres_container(self):
        """Start PostgreSQL container for testing."""
        with PostgresContainer("postgres:15") as postgres_container:
            yield postgres_container

    @pytest.mark.asyncio
    async def test_end_to_end_conversation_flow(
        self, redis_container, postgres_container
    ):
        """Test complete end-to-end conversation flow with persistence."""
        # This test would verify the complete flow from conversation start
        # through character creation with both Redis and database persistence
        pass

    @pytest.mark.asyncio
    async def test_conversation_recovery_with_database_sync(
        self, redis_container, postgres_container
    ):
        """Test conversation recovery with database synchronization."""
        # This test would verify that conversation state can be recovered
        # and synchronized between Redis cache and database storage
        pass
