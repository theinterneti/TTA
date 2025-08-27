"""
Tests for ReplayabilitySystem

This module tests alternative path exploration, progress preservation during experimentation,
outcome comparison and learning insights, scenario restart capabilities, and comprehensive
integration with therapeutic and character development systems.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from src.components.gameplay_loop.narrative.replayability_system import (
    ReplayabilitySystem, ExplorationSnapshot, AlternativePath, PathComparison, ExplorationSession,
    ExplorationMode, PathType, ComparisonMetric
)
from src.components.gameplay_loop.narrative.character_development_system import (
    CharacterDevelopmentSystem, CharacterAttribute
)
from src.components.gameplay_loop.services.session_state import SessionState, SessionStateType
from src.components.gameplay_loop.models.core import UserChoice, ChoiceType
from src.components.gameplay_loop.narrative.events import EventBus


class TestReplayabilitySystem:
    """Test ReplayabilitySystem functionality."""
    
    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus
    
    @pytest.fixture
    def character_development(self, event_bus):
        """Create mock character development system."""
        return CharacterDevelopmentSystem(event_bus)
    
    @pytest.fixture
    def replayability_system(self, event_bus, character_development):
        """Create replayability system instance."""
        return ReplayabilitySystem(event_bus, character_development)
    
    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = SessionState(
            session_id="test_session_123",
            user_id="test_user_456",
            state=SessionStateType.ACTIVE,
            therapeutic_goals=["anxiety_management", "communication_skills"]
        )
        state.current_scene_id = "scene_1"
        state.scene_history = ["intro", "scene_1"]
        state.choice_history = [
            Mock(choice_id="choice_1", text="Help the character", choice_type=ChoiceType.EMOTIONAL_REGULATION),
            Mock(choice_id="choice_2", text="Listen carefully", choice_type=ChoiceType.COMMUNICATION)
        ]
        state.context = {
            "therapeutic_progress": {
                "concepts_integrated": 2,
                "goals_addressed": ["anxiety_management"],
                "skills_practiced": ["breathing_techniques"]
            },
            "narrative_context": {
                "current_theme": "overcoming_challenges",
                "emotional_tone": "hopeful"
            }
        }
        return state
    
    @pytest.fixture
    def user_choice(self):
        """Create mock user choice."""
        choice = Mock(spec=UserChoice)
        choice.choice_id = "test_choice_789"
        choice.text = "Try a different approach"
        choice.choice_type = ChoiceType.PROBLEM_SOLVING
        choice.therapeutic_relevance = 0.8
        return choice
    
    @pytest.mark.asyncio
    async def test_create_exploration_snapshot(self, replayability_system, session_state, event_bus):
        """Test creating exploration snapshots."""
        snapshot = await replayability_system.create_exploration_snapshot(
            session_state, "Test Snapshot", "Testing snapshot creation"
        )
        
        # Check snapshot structure
        assert isinstance(snapshot, ExplorationSnapshot)
        assert snapshot.session_id == session_state.session_id
        assert snapshot.user_id == session_state.user_id
        assert snapshot.snapshot_name == "Test Snapshot"
        assert snapshot.description == "Testing snapshot creation"
        
        # Check session state preservation
        assert snapshot.session_state is not None
        assert snapshot.session_state.session_id == session_state.session_id
        assert snapshot.session_state.current_scene_id == session_state.current_scene_id
        
        # Check context preservation
        assert snapshot.therapeutic_progress == session_state.context["therapeutic_progress"]
        assert snapshot.narrative_context == session_state.context["narrative_context"]
        assert len(snapshot.choice_history) == len(session_state.choice_history)
        
        # Check storage
        assert snapshot.snapshot_id in replayability_system.exploration_snapshots
        assert session_state.user_id in replayability_system.user_snapshots
        assert snapshot.snapshot_id in replayability_system.user_snapshots[session_state.user_id]
        
        # Check event publication
        event_bus.publish.assert_called()
        
        # Check metrics
        assert replayability_system.metrics["snapshots_created"] == 1
    
    @pytest.mark.asyncio
    async def test_start_exploration_session(self, replayability_system, event_bus):
        """Test starting exploration sessions."""
        exploration = await replayability_system.start_exploration_session(
            "test_user_456", "test_session_123", ExplorationMode.GUIDED, "character_development"
        )
        
        # Check exploration structure
        assert isinstance(exploration, ExplorationSession)
        assert exploration.user_id == "test_user_456"
        assert exploration.base_session_id == "test_session_123"
        assert exploration.exploration_mode == ExplorationMode.GUIDED
        assert exploration.focus_area == "character_development"
        assert exploration.is_active == True
        
        # Check storage
        assert exploration.exploration_id in replayability_system.exploration_sessions
        assert "test_user_456" in replayability_system.user_explorations
        assert exploration.exploration_id in replayability_system.user_explorations["test_user_456"]
        
        # Check event publication
        event_bus.publish.assert_called()
        
        # Check metrics
        assert replayability_system.metrics["exploration_sessions_started"] == 1
    
    @pytest.mark.asyncio
    async def test_create_alternative_path(self, replayability_system, session_state, event_bus):
        """Test creating alternative paths."""
        # First create snapshot and exploration session
        snapshot = await replayability_system.create_exploration_snapshot(session_state)
        exploration = await replayability_system.start_exploration_session(
            session_state.user_id, session_state.session_id
        )
        
        # Create alternative path
        path = await replayability_system.create_alternative_path(
            exploration.exploration_id, snapshot.snapshot_id, PathType.THERAPEUTIC_APPROACH,
            "Therapeutic Path", "Exploring therapeutic approaches"
        )
        
        # Check path structure
        assert isinstance(path, AlternativePath)
        assert path.session_id == session_state.session_id
        assert path.user_id == session_state.user_id
        assert path.path_type == PathType.THERAPEUTIC_APPROACH
        assert path.path_name == "Therapeutic Path"
        assert path.starting_snapshot_id == snapshot.snapshot_id
        
        # Check storage
        assert path.path_id in replayability_system.alternative_paths
        assert session_state.user_id in replayability_system.user_paths
        assert path.path_id in replayability_system.user_paths[session_state.user_id]
        
        # Check exploration session update
        exploration = replayability_system.exploration_sessions[exploration.exploration_id]
        assert path.path_id in exploration.paths_explored
        assert exploration.current_path_id == path.path_id
        
        # Check event publication
        event_bus.publish.assert_called()
        
        # Check metrics
        assert replayability_system.metrics["paths_explored"] == 1
    
    @pytest.mark.asyncio
    async def test_restore_from_snapshot(self, replayability_system, session_state, character_development, event_bus):
        """Test restoring session state from snapshots."""
        # Initialize character development for user
        await character_development._initialize_character_attributes(session_state.user_id)
        
        # Create snapshot
        snapshot = await replayability_system.create_exploration_snapshot(session_state)
        
        # Create new session state to restore to
        target_state = SessionState(
            session_id="new_session_789",
            user_id=session_state.user_id,
            state=SessionStateType.ACTIVE
        )
        
        # Restore from snapshot
        restored_state = await replayability_system.restore_from_snapshot(snapshot.snapshot_id, target_state)
        
        # Check restoration
        assert restored_state.session_id == target_state.session_id  # Should use new session ID
        assert restored_state.user_id == session_state.user_id
        assert restored_state.current_scene_id == session_state.current_scene_id
        assert restored_state.scene_history == session_state.scene_history
        
        # Check exploration context
        assert restored_state.context["exploration_mode"] == True
        assert restored_state.context["restored_from_snapshot"] == snapshot.snapshot_id
        
        # Check event publication
        event_bus.publish.assert_called()
    
    @pytest.mark.asyncio
    async def test_record_path_choice(self, replayability_system, session_state, user_choice):
        """Test recording choices and outcomes for paths."""
        # Create snapshot, exploration, and path
        snapshot = await replayability_system.create_exploration_snapshot(session_state)
        exploration = await replayability_system.start_exploration_session(
            session_state.user_id, session_state.session_id
        )
        path = await replayability_system.create_alternative_path(
            exploration.exploration_id, snapshot.snapshot_id
        )
        
        # Record choice with outcomes
        outcomes = [
            {
                "outcome_id": "outcome_1",
                "description": "Character feels more confident",
                "outcome_type": "emotional",
                "therapeutic_value": 0.7,
                "character_impact": {"courage": 0.3}
            },
            {
                "outcome_id": "outcome_2", 
                "description": "New dialogue options unlocked",
                "outcome_type": "narrative",
                "therapeutic_value": 0.5
            }
        ]
        
        await replayability_system.record_path_choice(path.path_id, user_choice, outcomes)
        
        # Check path updates
        updated_path = replayability_system.alternative_paths[path.path_id]
        assert len(updated_path.choices_made) == 1
        assert len(updated_path.outcomes_achieved) == 2
        
        # Check choice record
        choice_record = updated_path.choices_made[0]
        assert choice_record["text"] == user_choice.text
        assert choice_record["choice_type"] == user_choice.choice_type.value
        assert choice_record["therapeutic_relevance"] == user_choice.therapeutic_relevance
        
        # Check outcome records
        outcome_record = updated_path.outcomes_achieved[0]
        assert outcome_record["description"] == "Character feels more confident"
        assert outcome_record["therapeutic_value"] == 0.7
    
    @pytest.mark.asyncio
    async def test_complete_alternative_path(self, replayability_system, session_state, event_bus):
        """Test completing alternative paths."""
        # Create snapshot, exploration, and path
        snapshot = await replayability_system.create_exploration_snapshot(session_state)
        exploration = await replayability_system.start_exploration_session(
            session_state.user_id, session_state.session_id
        )
        path = await replayability_system.create_alternative_path(
            exploration.exploration_id, snapshot.snapshot_id
        )
        
        # Complete path with final outcomes
        final_outcomes = {
            "therapeutic_outcomes": {
                "goals_achieved": 2,
                "skills_practiced": ["breathing", "communication"],
                "emotional_regulation_events": 3
            },
            "character_development": {
                "attributes_improved": {"courage": 0.5, "wisdom": 0.3},
                "milestones_achieved": ["first_brave_act"],
                "abilities_unlocked": ["mindful_breathing"]
            },
            "emotional_journey": [
                {"emotion_type": "anxiety", "intensity": 0.7},
                {"emotion_type": "confidence", "intensity": 0.8}
            ]
        }
        
        completed_path = await replayability_system.complete_alternative_path(path.path_id, final_outcomes)
        
        # Check completion
        assert completed_path.is_completed == True
        assert completed_path.completed_at is not None
        assert completed_path.completion_time_minutes > 0
        
        # Check final outcomes
        assert completed_path.therapeutic_outcomes == final_outcomes["therapeutic_outcomes"]
        assert completed_path.character_development == final_outcomes["character_development"]
        assert completed_path.emotional_journey == final_outcomes["emotional_journey"]
        
        # Check analytics
        assert completed_path.therapeutic_effectiveness > 0
        assert completed_path.engagement_score >= 0
        assert completed_path.learning_value >= 0
        
        # Check event publication
        event_bus.publish.assert_called()
    
    @pytest.mark.asyncio
    async def test_compare_paths(self, replayability_system, session_state, event_bus):
        """Test comparing multiple alternative paths."""
        # Create snapshot and exploration
        snapshot = await replayability_system.create_exploration_snapshot(session_state)
        exploration = await replayability_system.start_exploration_session(
            session_state.user_id, session_state.session_id
        )
        
        # Create two alternative paths
        path1 = await replayability_system.create_alternative_path(
            exploration.exploration_id, snapshot.snapshot_id, PathType.THERAPEUTIC_APPROACH, "Therapeutic Path"
        )
        path2 = await replayability_system.create_alternative_path(
            exploration.exploration_id, snapshot.snapshot_id, PathType.CHARACTER_DEVELOPMENT, "Character Path"
        )
        
        # Complete both paths with different outcomes
        await replayability_system.complete_alternative_path(path1.path_id, {
            "therapeutic_outcomes": {"goals_achieved": 3, "skills_practiced": ["breathing", "mindfulness"]},
            "character_development": {"attributes_improved": {"courage": 0.3}}
        })
        
        await replayability_system.complete_alternative_path(path2.path_id, {
            "therapeutic_outcomes": {"goals_achieved": 1, "skills_practiced": ["communication"]},
            "character_development": {"attributes_improved": {"courage": 0.7, "wisdom": 0.4}}
        })
        
        # Compare paths
        comparison = await replayability_system.compare_paths(
            [path1.path_id, path2.path_id], "Therapeutic vs Character Focus",
            [ComparisonMetric.THERAPEUTIC_EFFECTIVENESS, ComparisonMetric.CHARACTER_GROWTH]
        )
        
        # Check comparison structure
        assert isinstance(comparison, PathComparison)
        assert comparison.user_id == session_state.user_id
        assert comparison.comparison_name == "Therapeutic vs Character Focus"
        assert len(comparison.paths_compared) == 2
        
        # Check metric comparisons
        assert ComparisonMetric.THERAPEUTIC_EFFECTIVENESS in comparison.metric_comparisons
        assert ComparisonMetric.CHARACTER_GROWTH in comparison.metric_comparisons
        
        # Check insights
        assert len(comparison.key_differences) > 0
        assert len(comparison.therapeutic_insights) > 0
        assert len(comparison.character_development_insights) > 0
        
        # Check recommendations
        assert comparison.recommended_approach is not None
        assert comparison.recommendation_reasoning != ""
        assert len(comparison.learning_opportunities) > 0
        
        # Check storage
        assert comparison.comparison_id in replayability_system.path_comparisons
        
        # Check event publication
        event_bus.publish.assert_called()
        
        # Check metrics
        assert replayability_system.metrics["comparisons_generated"] == 1
    
    def test_exploration_templates_loading(self, replayability_system):
        """Test that exploration templates are properly loaded."""
        templates = replayability_system.exploration_templates
        
        # Check that all exploration modes are configured
        for mode in ExplorationMode:
            assert mode in templates
            template = templates[mode]
            assert "name" in template
            assert "description" in template
            assert "features" in template
            assert "guidance_level" in template
            assert "learning_focus" in template
    
    def test_comparison_algorithms_loading(self, replayability_system):
        """Test that comparison algorithms are properly loaded."""
        algorithms = replayability_system.comparison_algorithms
        
        # Check that key metrics are configured
        key_metrics = [
            ComparisonMetric.THERAPEUTIC_EFFECTIVENESS,
            ComparisonMetric.CHARACTER_GROWTH,
            ComparisonMetric.EMOTIONAL_IMPACT,
            ComparisonMetric.ENGAGEMENT_LEVEL
        ]
        
        for metric in key_metrics:
            assert metric in algorithms
            algorithm = algorithms[metric]
            assert "weight_factors" in algorithm
            assert "calculation_method" in algorithm
            assert "normalization" in algorithm
    
    def test_insight_generators_loading(self, replayability_system):
        """Test that insight generators are properly loaded."""
        generators = replayability_system.insight_generators
        
        # Check that key insight types are configured
        assert "therapeutic_insights" in generators
        assert "character_development_insights" in generators
        assert "learning_insights" in generators
        
        # Check generator structure
        for generator_type, generator in generators.items():
            assert "patterns" in generator
            assert "templates" in generator
            assert isinstance(generator["patterns"], list)
            assert isinstance(generator["templates"], list)
    
    def test_get_user_exploration_summary(self, replayability_system, session_state):
        """Test user exploration summary generation."""
        user_id = session_state.user_id
        
        # Add some exploration data
        replayability_system.user_snapshots[user_id] = ["snapshot_1", "snapshot_2"]
        replayability_system.user_paths[user_id] = ["path_1", "path_2"]
        replayability_system.user_explorations[user_id] = ["exploration_1"]
        
        # Add mock paths
        path1 = AlternativePath(
            path_id="path_1",
            user_id=user_id,
            path_type=PathType.THERAPEUTIC_APPROACH,
            path_name="Test Path 1",
            is_completed=True,
            therapeutic_effectiveness=0.8,
            engagement_score=0.7,
            completion_time_minutes=25.0
        )
        path2 = AlternativePath(
            path_id="path_2",
            user_id=user_id,
            path_type=PathType.CHARACTER_DEVELOPMENT,
            path_name="Test Path 2",
            is_completed=True,
            therapeutic_effectiveness=0.6,
            engagement_score=0.9,
            completion_time_minutes=30.0
        )
        
        replayability_system.alternative_paths["path_1"] = path1
        replayability_system.alternative_paths["path_2"] = path2
        
        summary = replayability_system.get_user_exploration_summary(user_id)
        
        # Check summary structure
        assert "user_id" in summary
        assert "exploration_summary" in summary
        assert "exploration_analytics" in summary
        assert "recent_paths" in summary
        assert "recent_comparisons" in summary
        
        # Check summary values
        exploration_summary = summary["exploration_summary"]
        assert exploration_summary["snapshots_created"] == 2
        assert exploration_summary["paths_explored"] == 2
        assert exploration_summary["paths_completed"] == 2
        assert exploration_summary["exploration_sessions"] == 1
        
        # Check analytics
        analytics = summary["exploration_analytics"]
        assert analytics["total_exploration_time_minutes"] == 55.0
        assert analytics["average_therapeutic_effectiveness"] == 0.7
        assert analytics["average_engagement_score"] == 0.8
    
    def test_get_user_exploration_summary_no_data(self, replayability_system):
        """Test user exploration summary when no data exists."""
        summary = replayability_system.get_user_exploration_summary("nonexistent_user")
        
        # Should return empty summary, not error
        assert "user_id" in summary
        assert summary["exploration_summary"]["snapshots_created"] == 0
        assert summary["exploration_summary"]["paths_explored"] == 0
    
    def test_metrics_tracking(self, replayability_system):
        """Test metrics tracking."""
        initial_metrics = replayability_system.get_metrics()
        
        # Check metric structure
        assert "snapshots_created" in initial_metrics
        assert "paths_explored" in initial_metrics
        assert "comparisons_generated" in initial_metrics
        assert "insights_discovered" in initial_metrics
        assert "exploration_sessions_started" in initial_metrics
        assert "therapeutic_learning_events" in initial_metrics
        assert "total_snapshots" in initial_metrics
        assert "total_paths" in initial_metrics
        assert "total_comparisons" in initial_metrics
        
        # Initially should be zero
        assert initial_metrics["snapshots_created"] == 0
        assert initial_metrics["paths_explored"] == 0
        assert initial_metrics["comparisons_generated"] == 0
    
    @pytest.mark.asyncio
    async def test_health_check(self, replayability_system):
        """Test health check functionality."""
        health = await replayability_system.health_check()
        
        assert health["status"] == "healthy"
        assert "exploration_templates_loaded" in health
        assert "comparison_algorithms_loaded" in health
        assert "insight_generators_loaded" in health
        assert "snapshots_stored" in health
        assert "paths_stored" in health
        assert "comparisons_stored" in health
        assert "exploration_sessions_stored" in health
        assert "metrics" in health
        
        # Should have loaded templates and algorithms
        assert health["exploration_templates_loaded"] > 0
        assert health["comparison_algorithms_loaded"] > 0
        assert health["insight_generators_loaded"] > 0
