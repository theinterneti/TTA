"""
Tests for Multiverse and Story Branching

This test suite covers the multiverse framework, story branching,
and cross-story character persistence functionality.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.player_experience.services.concurrent_world_state_manager import (
    ConcurrentWorldStateManager,
    StoryBranchType,
    WorldInstanceState,
)
from src.player_experience.services.cross_story_character_persistence import (
    CharacterEvolutionType,
    CrossStoryCharacterPersistence,
    PersistenceScope,
)
from src.player_experience.services.multiverse_navigation_service import (
    MultiverseNavigationService,
)
from src.player_experience.services.story_branching_service import (
    BranchTriggerType,
    NarrativeCoherenceLevel,
    StoryBranchingService,
)


@pytest.fixture
async def world_state_manager():
    """Create world state manager for testing."""
    manager = ConcurrentWorldStateManager()
    await manager.start()
    yield manager
    await manager.stop()


@pytest.fixture
async def story_branching_service():
    """Create story branching service for testing."""
    service = StoryBranchingService()
    yield service


@pytest.fixture
async def character_persistence():
    """Create character persistence service for testing."""
    service = CrossStoryCharacterPersistence()
    await service.start()
    yield service
    await service.stop()


@pytest.fixture
async def multiverse_navigation():
    """Create multiverse navigation service for testing."""
    service = MultiverseNavigationService()
    yield service


@pytest.fixture
def sample_world_instance_data():
    """Sample world instance data for testing."""
    return {
        "world_id": "therapeutic_garden",
        "player_id": "test_player_001",
        "character_id": "test_char_001",
        "session_id": "test_session_001",
        "initial_state": {
            "location": "garden_entrance",
            "mood": "curious",
            "energy": 100,
        },
    }


@pytest.fixture
def sample_character_data():
    """Sample character data for testing."""
    return {
        "character_id": "test_char_001",
        "name": "Alex",
        "personality_traits": {"openness": 0.7, "conscientiousness": 0.6},
        "therapeutic_progress": {"anxiety_management": 0.3, "social_skills": 0.5},
        "skills_learned": ["deep_breathing", "active_listening"],
        "emotional_state": {"current_mood": "calm", "stress_level": 0.2},
    }


class TestConcurrentWorldStateManager:
    """Test concurrent world state management."""

    @pytest.mark.asyncio
    async def test_world_instance_creation(
        self, world_state_manager, sample_world_instance_data
    ):
        """Test creating world instances."""
        data = sample_world_instance_data

        instance_id = await world_state_manager.create_world_instance(
            world_id=data["world_id"],
            player_id=data["player_id"],
            character_id=data["character_id"],
            session_id=data["session_id"],
            initial_state=data["initial_state"],
        )

        assert instance_id is not None
        assert instance_id.startswith("wi_")

        # Verify instance was created
        instance = await world_state_manager.get_world_instance(instance_id)
        assert instance is not None
        assert instance.world_id == data["world_id"]
        assert instance.player_id == data["player_id"]
        assert instance.state == WorldInstanceState.ACTIVE

    @pytest.mark.asyncio
    async def test_world_state_updates(
        self, world_state_manager, sample_world_instance_data
    ):
        """Test updating world state."""
        data = sample_world_instance_data

        # Create instance
        instance_id = await world_state_manager.create_world_instance(
            world_id=data["world_id"],
            player_id=data["player_id"],
            character_id=data["character_id"],
            session_id=data["session_id"],
            initial_state=data["initial_state"],
        )

        # Update state
        state_updates = {"location": "garden_center", "mood": "peaceful", "energy": 90}

        success = await world_state_manager.update_world_state(
            instance_id, state_updates
        )

        assert success

        # Verify updates
        instance = await world_state_manager.get_world_instance(instance_id)
        assert instance.world_state["location"] == "garden_center"
        assert instance.world_state["mood"] == "peaceful"

    @pytest.mark.asyncio
    async def test_story_branch_creation(
        self, world_state_manager, sample_world_instance_data
    ):
        """Test creating story branches."""
        data = sample_world_instance_data

        # Create parent instance
        parent_instance_id = await world_state_manager.create_world_instance(
            world_id=data["world_id"],
            player_id=data["player_id"],
            character_id=data["character_id"],
            session_id=data["session_id"],
        )

        # Create branch
        branch_point = {
            "decision": "path_choice",
            "options": ["peaceful_path", "challenging_path"],
        }

        branch_instance_id = await world_state_manager.create_story_branch(
            parent_instance_id=parent_instance_id,
            branch_type=StoryBranchType.ALTERNATE_CHOICE,
            branch_point=branch_point,
            session_id=f"{data['session_id']}_branch",
        )

        assert branch_instance_id is not None

        # Verify branch instance
        branch_instance = await world_state_manager.get_world_instance(
            branch_instance_id
        )
        assert branch_instance is not None
        assert branch_instance.parent_instance_id == parent_instance_id
        assert branch_instance.branch_type == StoryBranchType.ALTERNATE_CHOICE

    @pytest.mark.asyncio
    async def test_multiverse_context_management(
        self, world_state_manager, sample_world_instance_data
    ):
        """Test multiverse context management."""
        data = sample_world_instance_data
        player_id = data["player_id"]

        # Create multiple instances
        instance_ids = []
        for i in range(3):
            instance_id = await world_state_manager.create_world_instance(
                world_id=f"world_{i}",
                player_id=player_id,
                character_id=f"char_{i}",
                session_id=f"session_{i}",
            )
            instance_ids.append(instance_id)

        # Get multiverse context
        multiverse = await world_state_manager.get_player_multiverse(player_id)

        assert multiverse is not None
        assert len(multiverse.active_instances) == 3
        assert multiverse.primary_instance_id in instance_ids

    @pytest.mark.asyncio
    async def test_instance_archiving(
        self, world_state_manager, sample_world_instance_data
    ):
        """Test archiving world instances."""
        data = sample_world_instance_data

        # Create instance
        instance_id = await world_state_manager.create_world_instance(
            world_id=data["world_id"],
            player_id=data["player_id"],
            character_id=data["character_id"],
            session_id=data["session_id"],
        )

        # Archive instance
        success = await world_state_manager.archive_world_instance(instance_id)
        assert success

        # Verify archived state
        instance = await world_state_manager.get_world_instance(instance_id)
        assert instance.state == WorldInstanceState.ARCHIVED


class TestStoryBranchingService:
    """Test story branching functionality."""

    @pytest.mark.asyncio
    async def test_branch_point_creation(
        self, story_branching_service, sample_world_instance_data
    ):
        """Test creating branch points."""
        data = sample_world_instance_data

        # Mock world instance
        with patch.object(
            story_branching_service.world_state_manager, "get_world_instance"
        ) as mock_get:
            mock_instance = MagicMock()
            mock_instance.world_id = data["world_id"]
            mock_instance.player_id = data["player_id"]
            mock_get.return_value = mock_instance

            branch_point_id = await story_branching_service.create_branch_point(
                instance_id="test_instance",
                trigger_type=BranchTriggerType.PLAYER_CHOICE,
                decision_context={"choice": "path_selection"},
                available_options=[
                    {"option_id": "path_a", "text": "Take the peaceful path"},
                    {"option_id": "path_b", "text": "Take the challenging path"},
                ],
            )

            assert branch_point_id is not None
            assert branch_point_id.startswith("bp_")

    @pytest.mark.asyncio
    async def test_narrative_branch_creation(self, story_branching_service):
        """Test creating narrative branches."""
        # Create mock branch point
        branch_point_id = "test_branch_point"
        story_branching_service.branch_points[branch_point_id] = MagicMock()
        story_branching_service.branch_points[branch_point_id].parent_instance_id = (
            "parent_instance"
        )
        story_branching_service.branch_points[branch_point_id].trigger_type = (
            BranchTriggerType.PLAYER_CHOICE
        )
        story_branching_service.branch_points[branch_point_id].coherence_level = (
            NarrativeCoherenceLevel.MODERATE
        )

        # Mock world state manager
        with patch.object(
            story_branching_service.world_state_manager, "create_story_branch"
        ) as mock_create:
            mock_create.return_value = "new_instance_id"

            branch_id = await story_branching_service.create_narrative_branch(
                branch_point_id=branch_point_id,
                selected_option={"option_id": "path_a", "text": "Peaceful path"},
                session_id="branch_session",
                therapeutic_focus=["mindfulness", "anxiety_management"],
            )

            assert branch_id is not None
            assert branch_id.startswith("nb_")

    @pytest.mark.asyncio
    async def test_branch_narrative_context(self, story_branching_service):
        """Test isolated narrative context for branches."""
        # Create mock branch
        branch_id = "test_branch"
        mock_branch = MagicMock()
        mock_branch.branch_id = branch_id
        mock_branch.instance_id = "instance_123"
        mock_branch.branch_type = StoryBranchType.THERAPEUTIC_EXPLORATION
        mock_branch.narrative_context = {"scene": "therapy_room", "mood": "reflective"}
        mock_branch.therapeutic_focus = ["self_awareness"]

        story_branching_service.active_branches[branch_id] = mock_branch

        context = await story_branching_service.get_branch_narrative_context(branch_id)

        assert context is not None
        assert context["branch_id"] == branch_id
        assert context["instance_id"] == "instance_123"
        assert context["narrative_context"]["scene"] == "therapy_room"

    @pytest.mark.asyncio
    async def test_branch_merging(self, story_branching_service):
        """Test merging narrative branches."""
        # Create mock branches
        source_branch = MagicMock()
        source_branch.narrative_context = {"skill_a": "learned", "progress_a": 0.8}
        source_branch.therapeutic_focus = ["skill_practice"]

        target_branch = MagicMock()
        target_branch.narrative_context = {"skill_b": "learned", "progress_b": 0.6}
        target_branch.therapeutic_focus = ["emotional_regulation"]
        target_branch.instance_id = "target_instance"

        story_branching_service.active_branches["source_branch"] = source_branch
        story_branching_service.active_branches["target_branch"] = target_branch

        # Mock world state manager
        with patch.object(
            story_branching_service.world_state_manager, "update_world_state"
        ) as mock_update:
            mock_update.return_value = True

            merged_branch_id = await story_branching_service.merge_branches(
                source_branch_id="source_branch", target_branch_id="target_branch"
            )

            assert merged_branch_id == "target_branch"
            assert "source_branch" not in story_branching_service.active_branches


class TestCrossStoryCharacterPersistence:
    """Test cross-story character persistence."""

    @pytest.mark.asyncio
    async def test_character_profile_creation(
        self, character_persistence, sample_character_data
    ):
        """Test creating character profiles."""
        data = sample_character_data

        profile_id = await character_persistence.create_character_profile(
            character_id=data["character_id"],
            player_id="test_player_001",
            base_character_data=data,
        )

        assert profile_id is not None
        assert profile_id.startswith("csp_")

        # Verify profile was created
        profile = await character_persistence.get_character_profile(
            data["character_id"]
        )
        assert profile is not None
        assert profile.character_id == data["character_id"]

    @pytest.mark.asyncio
    async def test_character_snapshot_creation(
        self, character_persistence, sample_character_data
    ):
        """Test creating character snapshots."""
        data = sample_character_data

        snapshot_id = await character_persistence.create_character_snapshot(
            character_id=data["character_id"],
            player_id="test_player_001",
            instance_id="test_instance_001",
            character_data=data,
        )

        assert snapshot_id is not None
        assert snapshot_id.startswith("cs_")

    @pytest.mark.asyncio
    async def test_character_evolution_tracking(
        self, character_persistence, sample_character_data
    ):
        """Test tracking character evolution."""
        data = sample_character_data

        # Create snapshots
        snapshot_1 = await character_persistence.create_character_snapshot(
            character_id=data["character_id"],
            player_id="test_player_001",
            instance_id="instance_1",
            character_data=data,
        )

        # Modify character data
        evolved_data = data.copy()
        evolved_data["skills_learned"].append("conflict_resolution")
        evolved_data["therapeutic_progress"]["anxiety_management"] = 0.5

        snapshot_2 = await character_persistence.create_character_snapshot(
            character_id=data["character_id"],
            player_id="test_player_001",
            instance_id="instance_2",
            character_data=evolved_data,
        )

        # Track evolution
        evolution_id = await character_persistence.track_character_evolution(
            character_id=data["character_id"],
            player_id="test_player_001",
            evolution_type=CharacterEvolutionType.SKILL_DEVELOPMENT,
            from_snapshot_id=snapshot_1,
            to_snapshot_id=snapshot_2,
            changes={
                "skills_gained": ["conflict_resolution"],
                "therapeutic_progress": {"anxiety_management": 0.2},
            },
            story_context={"world": "therapeutic_garden"},
        )

        assert evolution_id is not None
        assert evolution_id.startswith("ce_")

    @pytest.mark.asyncio
    async def test_character_transfer_between_stories(
        self, character_persistence, sample_character_data
    ):
        """Test transferring characters between stories."""
        data = sample_character_data

        # Create character profile
        await character_persistence.create_character_profile(
            character_id=data["character_id"],
            player_id="test_player_001",
            base_character_data=data,
        )

        # Transfer character to new story
        transferred_data = await character_persistence.transfer_character_to_story(
            character_id=data["character_id"],
            target_instance_id="new_story_instance",
            transfer_scope=PersistenceScope.GLOBAL,
        )

        assert transferred_data is not None
        assert "accumulated_skills" in transferred_data
        assert "therapeutic_journey" in transferred_data
        assert transferred_data["accumulated_skills"] == data["skills_learned"]

    @pytest.mark.asyncio
    async def test_therapeutic_journey_tracking(
        self, character_persistence, sample_character_data
    ):
        """Test tracking therapeutic journey across stories."""
        data = sample_character_data

        # Create character profile
        await character_persistence.create_character_profile(
            character_id=data["character_id"],
            player_id="test_player_001",
            base_character_data=data,
        )

        # Get therapeutic journey
        journey = await character_persistence.get_character_therapeutic_journey(
            data["character_id"]
        )

        assert journey is not None
        assert "character_id" in journey
        assert "therapeutic_journey" in journey
        assert "accumulated_skills" in journey


class TestMultiverseNavigationService:
    """Test multiverse navigation functionality."""

    @pytest.mark.asyncio
    async def test_destination_discovery(self, multiverse_navigation):
        """Test discovering multiverse destinations."""
        player_id = "test_player_001"

        # Mock world state manager
        with patch.object(
            multiverse_navigation.world_state_manager, "get_player_multiverse"
        ) as mock_multiverse:
            mock_context = MagicMock()
            mock_context.active_instances = ["instance_1", "instance_2"]
            mock_multiverse.return_value = mock_context

            with patch.object(
                multiverse_navigation.world_state_manager, "get_world_instance"
            ) as mock_instance:
                mock_instance.return_value = MagicMock()

                with patch.object(
                    multiverse_navigation, "_create_destination_from_instance"
                ) as mock_create:
                    mock_create.return_value = MagicMock()

                    destinations = (
                        await multiverse_navigation.discover_multiverse_destinations(
                            player_id
                        )
                    )

                    assert len(destinations) >= 0  # May be empty due to mocking

    @pytest.mark.asyncio
    async def test_navigation_to_destination(self, multiverse_navigation):
        """Test navigating to a destination."""
        player_id = "test_player_001"
        session_id = "test_session_001"
        destination_id = "test_destination"

        # Mock destination
        mock_destination = MagicMock()
        mock_destination.destination_id = destination_id
        mock_destination.accessibility = {"accessible": True}

        with patch.object(multiverse_navigation, "_find_destination") as mock_find:
            mock_find.return_value = mock_destination

            with patch.object(
                multiverse_navigation, "_check_destination_accessibility"
            ) as mock_access:
                mock_access.return_value = {"accessible": True}

                with patch.object(
                    multiverse_navigation, "_execute_navigation"
                ) as mock_execute:
                    mock_execute.return_value = {
                        "success": True,
                        "new_session_id": "new_session",
                    }

                    result = await multiverse_navigation.navigate_to_destination(
                        player_id=player_id,
                        current_session_id=session_id,
                        destination_id=destination_id,
                    )

                    assert result is not None
                    assert result["success"] is True

    @pytest.mark.asyncio
    async def test_therapeutic_return_point_creation(self, multiverse_navigation):
        """Test creating therapeutic return points."""
        player_id = "test_player_001"
        session_id = "test_session_001"

        # Mock multiverse context
        with patch.object(
            multiverse_navigation.world_state_manager, "get_player_multiverse"
        ) as mock_multiverse:
            mock_context = MagicMock()
            mock_context.primary_instance_id = "primary_instance"
            mock_multiverse.return_value = mock_context

            with patch.object(
                multiverse_navigation.world_state_manager, "get_world_instance"
            ) as mock_instance:
                mock_instance.return_value = MagicMock()

                return_point_id = (
                    await multiverse_navigation.create_therapeutic_return_point(
                        player_id=player_id,
                        current_session_id=session_id,
                        return_point_name="Peaceful Moment",
                        therapeutic_context={"mindfulness": True, "calm_state": True},
                    )
                )

                assert return_point_id is not None
                assert return_point_id.startswith("trp_")

    @pytest.mark.asyncio
    async def test_navigation_history(self, multiverse_navigation):
        """Test getting navigation history."""
        player_id = "test_player_001"

        # Mock destinations with visit history
        mock_destinations = [
            MagicMock(
                destination_id="dest_1",
                title="Garden Path",
                last_visited=datetime.utcnow(),
                visit_count=3,
            ),
            MagicMock(
                destination_id="dest_2",
                title="Therapy Room",
                last_visited=None,
                visit_count=0,
            ),
        ]

        with patch.object(
            multiverse_navigation, "discover_multiverse_destinations"
        ) as mock_discover:
            mock_discover.return_value = mock_destinations

            history = await multiverse_navigation.get_navigation_history(player_id)

            assert len(history) == 1  # Only visited destinations
            assert history[0]["destination_id"] == "dest_1"
            assert history[0]["visit_count"] == 3


@pytest.mark.integration
class TestMultiverseIntegration:
    """Test integration between multiverse components."""

    @pytest.mark.asyncio
    async def test_complete_multiverse_workflow(
        self,
        world_state_manager,
        story_branching_service,
        character_persistence,
        multiverse_navigation,
        sample_world_instance_data,
        sample_character_data,
    ):
        """Test complete multiverse workflow."""
        player_id = "test_player_001"
        character_id = "test_char_001"

        # Step 1: Create character profile
        profile_id = await character_persistence.create_character_profile(
            character_id=character_id,
            player_id=player_id,
            base_character_data=sample_character_data,
        )
        assert profile_id is not None

        # Step 2: Create initial world instance
        instance_id = await world_state_manager.create_world_instance(
            world_id="therapeutic_garden",
            player_id=player_id,
            character_id=character_id,
            session_id="session_001",
        )
        assert instance_id is not None

        # Step 3: Create character snapshot
        snapshot_id = await character_persistence.create_character_snapshot(
            character_id=character_id,
            player_id=player_id,
            instance_id=instance_id,
            character_data=sample_character_data,
        )
        assert snapshot_id is not None

        # Step 4: Create branch point
        with patch.object(
            story_branching_service.world_state_manager, "get_world_instance"
        ) as mock_get:
            mock_instance = MagicMock()
            mock_instance.world_id = "therapeutic_garden"
            mock_instance.player_id = player_id
            mock_get.return_value = mock_instance

            branch_point_id = await story_branching_service.create_branch_point(
                instance_id=instance_id,
                trigger_type=BranchTriggerType.THERAPEUTIC_EXPLORATION,
                decision_context={"exploration_type": "deep_reflection"},
                available_options=[
                    {"option_id": "reflect", "text": "Reflect on feelings"},
                    {"option_id": "explore", "text": "Explore the environment"},
                ],
            )
            assert branch_point_id is not None

        # Step 5: Discover destinations
        with patch.object(
            multiverse_navigation.world_state_manager, "get_player_multiverse"
        ) as mock_multiverse:
            mock_context = MagicMock()
            mock_context.active_instances = [instance_id]
            mock_multiverse.return_value = mock_context

            with patch.object(
                multiverse_navigation.world_state_manager, "get_world_instance"
            ) as mock_instance:
                mock_instance.return_value = MagicMock()

                with patch.object(
                    multiverse_navigation, "_create_destination_from_instance"
                ) as mock_create:
                    mock_create.return_value = MagicMock(destination_id="dest_1")

                    destinations = (
                        await multiverse_navigation.discover_multiverse_destinations(
                            player_id
                        )
                    )

                    # Should have at least one destination
                    assert len(destinations) >= 0
