"""
Tests for TherapeuticReplayabilitySystem

This module tests the production replayability system implementation
including safe exploration environment, outcome comparison, and alternative path exploration.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.components.therapeutic_systems.replayability_system import (
    AlternativePath,
    ComparisonMetric,
    ExplorationMode,
    ExplorationSession,
    ExplorationSnapshot,
    PathComparison,
    PathType,
    TherapeuticReplayabilitySystem,
)


class TestTherapeuticReplayabilitySystem:
    """Test TherapeuticReplayabilitySystem functionality."""

    @pytest.fixture
    def replayability_system(self):
        """Create replayability system instance."""
        return TherapeuticReplayabilitySystem()

    @pytest.fixture
    def mock_therapeutic_systems(self):
        """Create mock therapeutic systems."""
        return {
            "consequence_system": AsyncMock(),
            "emotional_safety_system": AsyncMock(),
            "adaptive_difficulty_engine": AsyncMock(),
            "character_development_system": AsyncMock(),
            "therapeutic_integration_system": AsyncMock(),
            "gameplay_loop_controller": AsyncMock(),
        }

    @pytest.fixture
    def sample_session_state(self):
        """Create sample session state for testing."""
        return {
            "current_phase": "active_gameplay",
            "character_attributes": {"courage": 5.0, "wisdom": 4.0, "compassion": 6.0},
            "therapeutic_value_accumulated": 12.5,
            "choices_made": 5,
            "milestones_achieved": 2,
            "choice_history": [
                {"text": "approach_confidently", "timestamp": datetime.utcnow().isoformat()},
                {"text": "listen_empathetically", "timestamp": datetime.utcnow().isoformat()},
            ],
            "scenario_context": {"scenario_type": "social_interaction", "difficulty": "moderate"},
            "therapeutic_goals": ["confidence_building", "empathy_development"],
            "current_framework": "cbt",
            "difficulty_level": "moderate",
            "emotional_safety_status": {"crisis_detected": False, "safety_level": "standard"},
        }

    @pytest.mark.asyncio
    async def test_initialization(self, replayability_system):
        """Test system initialization."""
        await replayability_system.initialize()

        # Should have empty exploration tracking
        assert len(replayability_system.exploration_snapshots) == 0
        assert len(replayability_system.alternative_paths) == 0
        assert len(replayability_system.path_comparisons) == 0
        assert len(replayability_system.exploration_sessions) == 0

        # Should have default configuration
        assert replayability_system.max_snapshots_per_user == 10
        assert replayability_system.max_paths_per_exploration == 5
        assert replayability_system.snapshot_retention_days == 30
        assert replayability_system.enable_predictive_analysis is True

        # Should have initialized metrics
        assert "snapshots_created" in replayability_system.metrics
        assert "paths_explored" in replayability_system.metrics
        assert replayability_system.metrics["snapshots_created"] == 0

    def test_therapeutic_system_injection(self, replayability_system, mock_therapeutic_systems):
        """Test therapeutic system dependency injection."""
        replayability_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Should have all systems injected
        assert replayability_system.consequence_system is not None
        assert replayability_system.emotional_safety_system is not None
        assert replayability_system.adaptive_difficulty_engine is not None
        assert replayability_system.character_development_system is not None
        assert replayability_system.therapeutic_integration_system is not None
        assert replayability_system.gameplay_loop_controller is not None

    @pytest.mark.asyncio
    async def test_create_exploration_snapshot(self, replayability_system, sample_session_state):
        """Test exploration snapshot creation."""
        await replayability_system.initialize()

        snapshot = await replayability_system.create_exploration_snapshot(
            session_id="session_001",
            user_id="test_user_001",
            session_state=sample_session_state,
            description="Test snapshot for exploration"
        )

        # Should return valid snapshot
        assert isinstance(snapshot, ExplorationSnapshot)
        assert snapshot.session_id == "session_001"
        assert snapshot.user_id == "test_user_001"
        assert snapshot.session_phase == "active_gameplay"
        assert snapshot.character_state["courage"] == 5.0
        assert snapshot.therapeutic_progress["therapeutic_value"] == 12.5
        assert len(snapshot.choice_history) == 2
        assert len(snapshot.therapeutic_goals) == 2

        # Should track snapshot
        assert len(replayability_system.exploration_snapshots) == 1
        assert snapshot.snapshot_id in replayability_system.exploration_snapshots
        assert "test_user_001" in replayability_system.user_snapshots

        # Should update metrics
        assert replayability_system.metrics["snapshots_created"] == 1

    @pytest.mark.asyncio
    async def test_start_exploration_session(self, replayability_system):
        """Test exploration session start."""
        await replayability_system.initialize()

        exploration = await replayability_system.start_exploration_session(
            user_id="test_user_002",
            base_session_id="session_002",
            exploration_mode=ExplorationMode.COMPARATIVE,
            focus_area="therapeutic_approaches",
            therapeutic_goals=["anxiety_management", "confidence_building"]
        )

        # Should return valid exploration session
        assert isinstance(exploration, ExplorationSession)
        assert exploration.user_id == "test_user_002"
        assert exploration.base_session_id == "session_002"
        assert exploration.exploration_mode == ExplorationMode.COMPARATIVE
        assert exploration.focus_area == "therapeutic_approaches"
        assert len(exploration.therapeutic_goals) == 2
        assert exploration.is_active is True

        # Should track exploration
        assert len(replayability_system.exploration_sessions) == 1
        assert exploration.exploration_id in replayability_system.exploration_sessions
        assert "test_user_002" in replayability_system.user_explorations

    @pytest.mark.asyncio
    async def test_create_alternative_path(self, replayability_system, sample_session_state, mock_therapeutic_systems):
        """Test alternative path creation."""
        await replayability_system.initialize()
        replayability_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses for predictive analysis
        mock_therapeutic_systems["consequence_system"].process_choice_consequence.return_value = {
            "therapeutic_value": 3.0, "character_impact": {"courage": 1.0}
        }
        mock_therapeutic_systems["therapeutic_integration_system"].generate_personalized_recommendations.return_value = [
            Mock(framework=Mock(value="dbt"))
        ]
        mock_therapeutic_systems["emotional_safety_system"].assess_crisis_risk.return_value = {
            "crisis_detected": False, "safety_level": "standard"
        }

        # Create snapshot first
        snapshot = await replayability_system.create_exploration_snapshot(
            session_id="session_003",
            user_id="test_user_003",
            session_state=sample_session_state
        )

        # Create exploration session
        exploration = await replayability_system.start_exploration_session(
            user_id="test_user_003",
            base_session_id="session_003"
        )

        # Create alternative path
        alternative_choices = [
            {"text": "approach_cautiously", "choice_type": "therapeutic"},
            {"text": "seek_support_first", "choice_type": "safety"}
        ]

        path = await replayability_system.create_alternative_path(
            exploration_id=exploration.exploration_id,
            snapshot_id=snapshot.snapshot_id,
            path_type=PathType.THERAPEUTIC_APPROACH,
            path_name="Cautious Approach",
            alternative_choices=alternative_choices,
            path_description="A more cautious therapeutic approach"
        )

        # Should return valid alternative path
        assert isinstance(path, AlternativePath)
        assert path.exploration_id == exploration.exploration_id
        assert path.snapshot_id == snapshot.snapshot_id
        assert path.path_type == PathType.THERAPEUTIC_APPROACH
        assert path.path_name == "Cautious Approach"
        assert len(path.alternative_choices) == 2
        assert path.therapeutic_value > 0  # Should have predicted value

        # Should track path
        assert len(replayability_system.alternative_paths) == 1
        assert path.path_id in replayability_system.alternative_paths
        assert path.path_id in exploration.paths_explored

        # Should update metrics
        assert replayability_system.metrics["paths_explored"] == 1

    @pytest.mark.asyncio
    async def test_compare_alternative_paths(self, replayability_system, sample_session_state, mock_therapeutic_systems):
        """Test alternative path comparison."""
        await replayability_system.initialize()
        replayability_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses with different values for different paths
        def mock_consequence_response(*args, **kwargs):
            choice = kwargs.get("choice", "")
            if "directly" in choice:
                return {"therapeutic_value": 3.0, "character_impact": {"courage": 1.0}}
            else:
                return {"therapeutic_value": 1.5, "character_impact": {"compassion": 0.8}}

        mock_therapeutic_systems["consequence_system"].process_choice_consequence.side_effect = mock_consequence_response
        mock_therapeutic_systems["therapeutic_integration_system"].generate_personalized_recommendations.return_value = [
            Mock(framework=Mock(value="cbt"))
        ]
        mock_therapeutic_systems["emotional_safety_system"].assess_crisis_risk.return_value = {
            "crisis_detected": False, "safety_level": "standard"
        }

        # Create snapshot and exploration
        snapshot = await replayability_system.create_exploration_snapshot(
            session_id="session_004",
            user_id="test_user_004",
            session_state=sample_session_state
        )

        exploration = await replayability_system.start_exploration_session(
            user_id="test_user_004",
            base_session_id="session_004"
        )

        # Create two alternative paths
        path1 = await replayability_system.create_alternative_path(
            exploration_id=exploration.exploration_id,
            snapshot_id=snapshot.snapshot_id,
            path_type=PathType.THERAPEUTIC_APPROACH,
            path_name="Direct Approach",
            alternative_choices=[{"text": "confront_directly"}]
        )

        path2 = await replayability_system.create_alternative_path(
            exploration_id=exploration.exploration_id,
            snapshot_id=snapshot.snapshot_id,
            path_type=PathType.THERAPEUTIC_APPROACH,
            path_name="Gentle Approach",
            alternative_choices=[{"text": "approach_gently"}]
        )

        # Compare paths
        comparison = await replayability_system.compare_alternative_paths(
            exploration_id=exploration.exploration_id,
            path_ids=[path1.path_id, path2.path_id],
            comparison_metrics=[ComparisonMetric.THERAPEUTIC_VALUE, ComparisonMetric.CHARACTER_GROWTH]
        )

        # Should return valid comparison
        assert isinstance(comparison, PathComparison)
        assert comparison.exploration_id == exploration.exploration_id
        assert len(comparison.path_ids) == 2
        assert len(comparison.comparison_metrics) == 2
        assert len(comparison.metric_scores) > 0
        assert len(comparison.overall_rankings) == 2
        assert len(comparison.key_differences) > 0
        assert len(comparison.therapeutic_insights) > 0

        # Should track comparison
        assert len(replayability_system.path_comparisons) == 1
        assert comparison.comparison_id in replayability_system.path_comparisons
        assert comparison.comparison_id in exploration.comparisons_generated

        # Should update metrics
        assert replayability_system.metrics["comparisons_generated"] == 1

    @pytest.mark.asyncio
    async def test_restore_from_snapshot(self, replayability_system, sample_session_state):
        """Test session state restoration from snapshot."""
        await replayability_system.initialize()

        # Create snapshot
        snapshot = await replayability_system.create_exploration_snapshot(
            session_id="session_005",
            user_id="test_user_005",
            session_state=sample_session_state
        )

        # Restore from snapshot
        restoration_result = await replayability_system.restore_from_snapshot(
            snapshot_id=snapshot.snapshot_id,
            target_session_id="session_005_restored"
        )

        # Should return successful restoration
        assert restoration_result["restoration_successful"] is True
        assert restoration_result["snapshot_id"] == snapshot.snapshot_id
        assert restoration_result["target_session_id"] == "session_005_restored"
        assert "restored_state" in restoration_result

        # Restored state should match original
        restored_state = restoration_result["restored_state"]
        assert restored_state["user_id"] == "test_user_005"
        assert restored_state["current_phase"] == "active_gameplay"
        assert restored_state["character_attributes"]["courage"] == 5.0
        assert restored_state["therapeutic_value_accumulated"] == 12.5

    @pytest.mark.asyncio
    async def test_exploration_modes(self, replayability_system):
        """Test different exploration modes."""
        await replayability_system.initialize()

        # Test all exploration modes
        modes = [
            ExplorationMode.SANDBOX,
            ExplorationMode.GUIDED,
            ExplorationMode.COMPARATIVE,
            ExplorationMode.THERAPEUTIC,
            ExplorationMode.CHARACTER_FOCUSED,
        ]

        for mode in modes:
            exploration = await replayability_system.start_exploration_session(
                user_id=f"test_user_{mode.value}",
                base_session_id=f"session_{mode.value}",
                exploration_mode=mode
            )

            assert exploration.exploration_mode == mode
            assert mode.value.title() in exploration.exploration_name

    @pytest.mark.asyncio
    async def test_path_types(self, replayability_system, sample_session_state):
        """Test different path types."""
        await replayability_system.initialize()

        # Create snapshot and exploration
        snapshot = await replayability_system.create_exploration_snapshot(
            session_id="session_006",
            user_id="test_user_006",
            session_state=sample_session_state
        )

        exploration = await replayability_system.start_exploration_session(
            user_id="test_user_006",
            base_session_id="session_006"
        )

        # Test all path types
        path_types = [
            PathType.CHOICE_ALTERNATIVE,
            PathType.THERAPEUTIC_APPROACH,
            PathType.CHARACTER_DEVELOPMENT,
            PathType.EMOTIONAL_RESPONSE,
            PathType.SKILL_APPLICATION,
            PathType.SCENARIO_VARIATION,
        ]

        for path_type in path_types:
            path = await replayability_system.create_alternative_path(
                exploration_id=exploration.exploration_id,
                snapshot_id=snapshot.snapshot_id,
                path_type=path_type,
                path_name=f"Test {path_type.value}",
            )

            assert path.path_type == path_type

    @pytest.mark.asyncio
    async def test_snapshot_cleanup(self, replayability_system, sample_session_state):
        """Test automatic snapshot cleanup."""
        await replayability_system.initialize()
        replayability_system.max_snapshots_per_user = 3  # Set low limit for testing

        user_id = "test_user_cleanup"

        # Create more snapshots than the limit
        for i in range(5):
            await replayability_system.create_exploration_snapshot(
                session_id=f"session_{i}",
                user_id=user_id,
                session_state=sample_session_state,
                description=f"Snapshot {i}"
            )

        # Should have cleaned up to the limit
        assert len(replayability_system.user_snapshots[user_id]) <= 3
        assert len(replayability_system.exploration_snapshots) <= 3

    @pytest.mark.asyncio
    async def test_error_handling(self, replayability_system):
        """Test error handling in various operations."""
        await replayability_system.initialize()

        # Test creating path with invalid exploration
        path = await replayability_system.create_alternative_path(
            exploration_id="non_existent",
            snapshot_id="non_existent",
            path_type=PathType.CHOICE_ALTERNATIVE,
            path_name="Error Path"
        )

        assert "Error Path" in path.path_name

        # Test comparison with insufficient paths
        comparison = await replayability_system.compare_alternative_paths(
            exploration_id="non_existent",
            path_ids=["single_path"]
        )

        assert "Error" in comparison.key_differences[0]

    @pytest.mark.asyncio
    async def test_health_check(self, replayability_system, mock_therapeutic_systems):
        """Test system health check."""
        await replayability_system.initialize()
        replayability_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        health = await replayability_system.health_check()

        assert "status" in health
        assert health["status"] == "healthy"  # All 6 systems available
        assert "exploration_modes" in health
        assert health["exploration_modes"] == 5
        assert "path_types" in health
        assert health["path_types"] == 6
        assert "comparison_metrics" in health
        assert health["comparison_metrics"] == 8
        assert "therapeutic_systems" in health
        assert health["systems_available"] == "6/6"

    @pytest.mark.asyncio
    async def test_health_check_degraded(self, replayability_system):
        """Test health check with missing systems."""
        await replayability_system.initialize()
        # Don't inject all systems

        health = await replayability_system.health_check()

        assert health["status"] == "degraded"  # Less than 3 systems available
        assert health["systems_available"] == "0/6"

    def test_get_metrics(self, replayability_system):
        """Test metrics collection."""
        # Add some test data
        replayability_system.metrics["snapshots_created"] = 5
        replayability_system.metrics["paths_explored"] = 3
        replayability_system.exploration_snapshots["test"] = Mock()
        replayability_system.exploration_sessions["test"] = Mock(is_active=True)
        replayability_system.alternative_paths["test"] = Mock()

        metrics = replayability_system.get_metrics()

        assert isinstance(metrics, dict)
        assert "snapshots_created" in metrics
        assert "paths_explored" in metrics
        assert "active_snapshots" in metrics
        assert "active_explorations" in metrics
        assert "alternative_paths_created" in metrics
        assert metrics["snapshots_created"] == 5
        assert metrics["active_snapshots"] == 1
        assert metrics["active_explorations"] == 1

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, replayability_system, sample_session_state, mock_therapeutic_systems):
        """Test compatibility with E2E test interface expectations."""
        await replayability_system.initialize()
        replayability_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock system responses for E2E compatibility
        mock_therapeutic_systems["consequence_system"].process_choice_consequence.return_value = {
            "therapeutic_value": 1.5, "character_impact": {"courage": 0.3}
        }
        mock_therapeutic_systems["therapeutic_integration_system"].generate_personalized_recommendations.return_value = [
            Mock(framework=Mock(value="mindfulness"))
        ]
        mock_therapeutic_systems["emotional_safety_system"].assess_crisis_risk.return_value = {
            "crisis_detected": False, "safety_level": "standard"
        }

        # Test snapshot creation (E2E interface)
        snapshot = await replayability_system.create_exploration_snapshot(
            session_id="demo_session_001",
            user_id="demo_user_001",
            session_state=sample_session_state
        )

        # Should match expected structure
        assert hasattr(snapshot, "snapshot_id")
        assert hasattr(snapshot, "session_id")
        assert hasattr(snapshot, "user_id")
        assert hasattr(snapshot, "character_state")
        assert hasattr(snapshot, "therapeutic_progress")

        # Test exploration session (E2E interface)
        exploration = await replayability_system.start_exploration_session(
            user_id="demo_user_001",
            base_session_id="demo_session_001"
        )

        # Should match expected structure
        assert hasattr(exploration, "exploration_id")
        assert hasattr(exploration, "user_id")
        assert hasattr(exploration, "exploration_mode")
        assert hasattr(exploration, "is_active")

        # Test alternative path creation (E2E interface)
        path = await replayability_system.create_alternative_path(
            exploration_id=exploration.exploration_id,
            snapshot_id=snapshot.snapshot_id,
            path_type=PathType.THERAPEUTIC_APPROACH,
            path_name="Demo Path"
        )

        # Should match expected structure
        assert hasattr(path, "path_id")
        assert hasattr(path, "path_type")
        assert hasattr(path, "therapeutic_value")
        assert hasattr(path, "character_impact")
