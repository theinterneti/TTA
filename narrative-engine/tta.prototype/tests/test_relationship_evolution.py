"""
Integration Tests for Relationship Evolution System

This module contains comprehensive integration tests for the advanced relationship
tracking and character evolution system, including relationship dynamics,
character growth patterns, and personality consistency validation.
"""

import sys
import unittest
from datetime import timedelta
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent.parent / "core"
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from character_development_system import Interaction
    from data_models import CharacterState, DialogueStyle, ValidationError
    from relationship_evolution import (
        CharacterGrowthMetrics,
        CharacterGrowthTracker,
        GrowthPattern,
        PersonalityConsistencyValidator,
        RelationshipEvolutionEngine,
        RelationshipMetrics,
        RelationshipType,
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for when running as part of package
    from ..core.character_development_system import Interaction
    from ..core.relationship_evolution import (
        CharacterGrowthMetrics,
        CharacterGrowthTracker,
        GrowthPattern,
        PersonalityConsistencyValidator,
        RelationshipEvolutionEngine,
        RelationshipMetrics,
        RelationshipType,
    )
    from ..models.data_models import CharacterState, DialogueStyle, ValidationError


class TestRelationshipMetrics(unittest.TestCase):
    """Test RelationshipMetrics dataclass."""

    def test_valid_relationship_metrics(self):
        """Test creating valid relationship metrics."""
        metrics = RelationshipMetrics(
            character1_id="char1",
            character2_id="char2",
            relationship_type=RelationshipType.THERAPEUTIC,
            trust_level=0.5,
            intimacy_level=0.3,
            conflict_level=0.1,
            communication_quality=0.8,
            therapeutic_alliance=0.6
        )
        self.assertTrue(metrics.validate())

    def test_invalid_trust_level(self):
        """Test validation fails for invalid trust level."""
        with self.assertRaises(ValidationError):
            metrics = RelationshipMetrics(trust_level=1.5)
            metrics.validate()

    def test_invalid_intimacy_level(self):
        """Test validation fails for invalid intimacy level."""
        with self.assertRaises(ValidationError):
            metrics = RelationshipMetrics(intimacy_level=-0.1)
            metrics.validate()

    def test_calculate_overall_relationship_score(self):
        """Test overall relationship score calculation."""
        metrics = RelationshipMetrics(
            trust_level=0.8,
            intimacy_level=0.6,
            conflict_level=0.2,
            communication_quality=0.9,
            mutual_understanding=0.7,
            therapeutic_alliance=0.8,
            relationship_stability=0.8
        )

        score = metrics.calculate_overall_relationship_score()
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, -1.0)
        self.assertLessEqual(score, 1.0)
        self.assertGreater(score, 0.0)  # Should be positive with good metrics


class TestCharacterGrowthMetrics(unittest.TestCase):
    """Test CharacterGrowthMetrics dataclass."""

    def test_valid_growth_metrics(self):
        """Test creating valid growth metrics."""
        metrics = CharacterGrowthMetrics(
            character_id="test_char",
            growth_pattern=GrowthPattern.STEADY_IMPROVEMENT,
            therapeutic_progress=0.6,
            emotional_resilience=0.7,
            social_competence=0.5,
            self_awareness=0.8,
            coping_effectiveness=0.6
        )
        self.assertTrue(metrics.validate())

    def test_invalid_therapeutic_progress(self):
        """Test validation fails for invalid therapeutic progress."""
        with self.assertRaises(ValidationError):
            metrics = CharacterGrowthMetrics(
                character_id="test_char",
                therapeutic_progress=1.5
            )
            metrics.validate()

    def test_invalid_personality_stability(self):
        """Test validation fails for invalid personality stability."""
        with self.assertRaises(ValidationError):
            metrics = CharacterGrowthMetrics(
                character_id="test_char",
                personality_stability={"empathy": 1.5}
            )
            metrics.validate()


class TestRelationshipEvolutionEngine(unittest.TestCase):
    """Test RelationshipEvolutionEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = RelationshipEvolutionEngine()

    def test_initialize_relationship(self):
        """Test initializing a new relationship."""
        metrics = self.engine.initialize_relationship(
            "char1", "char2", RelationshipType.THERAPEUTIC
        )

        self.assertIsInstance(metrics, RelationshipMetrics)
        self.assertEqual(metrics.relationship_type, RelationshipType.THERAPEUTIC)
        self.assertEqual(metrics.character1_id, "char1")
        self.assertEqual(metrics.character2_id, "char2")
        self.assertGreater(metrics.therapeutic_alliance, 0.0)  # Should have initial alliance

    def test_get_relationship_key(self):
        """Test relationship key generation is consistent."""
        key1 = self.engine.get_relationship_key("char1", "char2")
        key2 = self.engine.get_relationship_key("char2", "char1")
        self.assertEqual(key1, key2)  # Should be the same regardless of order

    def test_update_relationship_from_interaction(self):
        """Test updating relationship from interaction."""
        # Initialize relationship
        initial_metrics = self.engine.initialize_relationship(
            "therapist", "patient", RelationshipType.THERAPEUTIC
        )
        initial_trust = initial_metrics.trust_level
        initial_alliance = initial_metrics.therapeutic_alliance

        # Create positive therapeutic interaction
        interaction = Interaction(
            participants=["therapist", "patient"],
            interaction_type="therapeutic",
            content="Successful therapy session with breakthrough",
            emotional_impact=0.7,
            therapeutic_value=0.9
        )

        # Update relationship
        updated_metrics = self.engine.update_relationship_from_interaction(
            "therapist", "patient", interaction
        )

        # Verify improvements
        self.assertGreater(updated_metrics.trust_level, initial_trust)
        self.assertGreater(updated_metrics.therapeutic_alliance, initial_alliance)
        self.assertGreater(updated_metrics.communication_quality, 0.5)

    def test_update_relationship_conflict(self):
        """Test relationship update with conflict interaction."""
        # Initialize relationship
        self.engine.initialize_relationship("char1", "char2", RelationshipType.FRIENDSHIP)

        # Create conflict interaction
        conflict_interaction = Interaction(
            participants=["char1", "char2"],
            interaction_type="conflict",
            content="Disagreement about treatment approach",
            emotional_impact=-0.6,
            therapeutic_value=0.1
        )

        # Update relationship
        updated_metrics = self.engine.update_relationship_from_interaction(
            "char1", "char2", conflict_interaction
        )

        # Verify conflict effects
        self.assertGreater(updated_metrics.conflict_level, 0.0)
        self.assertLess(updated_metrics.trust_level, 0.0)  # Trust should decrease

    def test_evolve_relationship_over_time(self):
        """Test relationship evolution over time without interactions."""
        # Initialize relationship with high values
        metrics = self.engine.initialize_relationship("char1", "char2")
        metrics.trust_level = 0.8
        metrics.intimacy_level = 0.7
        metrics.conflict_level = 0.3

        # Evolve over 30 days without interaction
        evolved_metrics = self.engine.evolve_relationship_over_time(
            "char1", "char2", timedelta(days=30)
        )

        # Verify natural decay
        self.assertLess(evolved_metrics.trust_level, 0.8)
        self.assertLess(evolved_metrics.intimacy_level, 0.7)
        self.assertLess(evolved_metrics.conflict_level, 0.3)  # Conflict should reduce

    def test_get_relationship_analysis(self):
        """Test getting relationship analysis."""
        # Initialize and update relationship
        self.engine.initialize_relationship("char1", "char2", RelationshipType.THERAPEUTIC)

        interaction = Interaction(
            participants=["char1", "char2"],
            interaction_type="therapeutic",
            emotional_impact=0.5,
            therapeutic_value=0.7
        )
        self.engine.update_relationship_from_interaction("char1", "char2", interaction)

        # Get analysis
        analysis = self.engine.get_relationship_analysis("char1", "char2")

        self.assertIn("relationship_type", analysis)
        self.assertIn("overall_score", analysis)
        self.assertIn("metrics", analysis)
        self.assertEqual(analysis["relationship_type"], "therapeutic")
        self.assertIsInstance(analysis["overall_score"], float)

    def test_nonexistent_relationship_analysis(self):
        """Test analysis of non-existent relationship."""
        analysis = self.engine.get_relationship_analysis("nonexistent1", "nonexistent2")
        self.assertIn("error", analysis)


class TestCharacterGrowthTracker(unittest.TestCase):
    """Test CharacterGrowthTracker class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracker = CharacterGrowthTracker()
        self.character_state = CharacterState(
            character_id="test_char",
            name="Test Character",
            personality_traits={
                "empathy": 0.6,
                "neuroticism": 0.4,
                "emotional_resilience": 0.5
            },
            therapeutic_role="patient"
        )

    def test_initialize_character_growth(self):
        """Test initializing character growth tracking."""
        metrics = self.tracker.initialize_character_growth(
            "test_char", GrowthPattern.STEADY_IMPROVEMENT
        )

        self.assertIsInstance(metrics, CharacterGrowthMetrics)
        self.assertEqual(metrics.character_id, "test_char")
        self.assertEqual(metrics.growth_pattern, GrowthPattern.STEADY_IMPROVEMENT)
        self.assertTrue(metrics.validate())

    def test_update_character_growth_therapeutic(self):
        """Test updating character growth with therapeutic interactions."""
        # Initialize growth tracking
        initial_metrics = self.tracker.initialize_character_growth("test_char")
        initial_progress = initial_metrics.therapeutic_progress

        # Create therapeutic interactions
        therapeutic_interactions = [
            Interaction(
                participants=["test_char", "therapist"],
                interaction_type="therapeutic",
                content="Learned new coping strategy",
                emotional_impact=0.5,
                therapeutic_value=0.8
            ),
            Interaction(
                participants=["test_char", "therapist"],
                interaction_type="therapeutic",
                content="Breakthrough in understanding anxiety triggers",
                emotional_impact=0.7,
                therapeutic_value=0.9
            )
        ]

        # Update growth
        updated_metrics = self.tracker.update_character_growth(
            "test_char", self.character_state, therapeutic_interactions
        )

        # Verify therapeutic progress improvement
        self.assertGreater(updated_metrics.therapeutic_progress, initial_progress)
        self.assertTrue(updated_metrics.validate())

    def test_update_character_growth_resilience(self):
        """Test updating emotional resilience based on handling negative interactions."""
        # Initialize with some negative interactions
        negative_interactions = [
            Interaction(
                participants=["test_char", "stressor"],
                interaction_type="conflict",
                content="Difficult situation at work",
                emotional_impact=-0.4,
                therapeutic_value=0.1
            )
        ]

        # Character maintains neutral mood despite negative interaction
        self.character_state.current_mood = "neutral"

        # Update growth
        updated_metrics = self.tracker.update_character_growth(
            "test_char", self.character_state, negative_interactions
        )

        # Resilience should improve for handling negative situations well
        self.assertGreaterEqual(updated_metrics.emotional_resilience, 0.5)

    def test_update_character_growth_social_competence(self):
        """Test updating social competence based on relationships."""
        # Add positive relationships
        self.character_state.relationship_scores = {
            "friend1": 0.6,
            "friend2": 0.4,
            "therapist": 0.8
        }

        interactions = [
            Interaction(
                participants=["test_char", "friend1"],
                interaction_type="dialogue",
                emotional_impact=0.4
            )
        ]

        # Update growth
        updated_metrics = self.tracker.update_character_growth(
            "test_char", self.character_state, interactions
        )

        # Social competence should improve with good relationships
        self.assertGreaterEqual(updated_metrics.social_competence, 0.5)

    def test_detect_growth_milestones(self):
        """Test detection of growth milestones."""
        # Initialize with high therapeutic progress
        metrics = self.tracker.initialize_character_growth("test_char")
        metrics.therapeutic_progress = 0.6  # Should trigger 25% and 50% milestones

        # Update to trigger milestone detection
        updated_metrics = self.tracker.update_character_growth(
            "test_char", self.character_state, []
        )

        # Check for milestones
        self.assertIn("25% therapeutic progress", updated_metrics.growth_milestones)
        self.assertIn("50% therapeutic progress", updated_metrics.growth_milestones)

    def test_get_character_growth_analysis(self):
        """Test getting character growth analysis."""
        # Initialize and update character growth
        self.tracker.initialize_character_growth("test_char")

        interactions = [
            Interaction(
                participants=["test_char", "therapist"],
                interaction_type="therapeutic",
                therapeutic_value=0.7
            )
        ]

        self.tracker.update_character_growth("test_char", self.character_state, interactions)

        # Get analysis
        analysis = self.tracker.get_character_growth_analysis("test_char")

        self.assertIn("character_id", analysis)
        self.assertIn("growth_pattern", analysis)
        self.assertIn("overall_growth_score", analysis)
        self.assertIn("metrics", analysis)
        self.assertEqual(analysis["character_id"], "test_char")
        self.assertIsInstance(analysis["overall_growth_score"], float)

    def test_nonexistent_character_analysis(self):
        """Test analysis of non-existent character."""
        analysis = self.tracker.get_character_growth_analysis("nonexistent")
        self.assertIn("error", analysis)


class TestPersonalityConsistencyValidator(unittest.TestCase):
    """Test PersonalityConsistencyValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = PersonalityConsistencyValidator()
        self.character_state = CharacterState(
            character_id="test_char",
            name="Test Character",
            personality_traits={
                "empathy": 0.7,
                "neuroticism": 0.3,
                "extraversion": 0.6
            },
            current_mood="content",
            dialogue_style=DialogueStyle(
                formality_level=0.6,
                empathy_level=0.8,
                directness=0.5
            )
        )

    def test_validate_consistent_personality(self):
        """Test validation of consistent personality."""
        # Create historical state with similar traits
        historical_state = CharacterState(
            character_id="test_char",
            name="Test Character",
            personality_traits={
                "empathy": 0.68,  # Small change
                "neuroticism": 0.32,  # Small change
                "extraversion": 0.58  # Small change
            }
        )

        is_consistent, issues = self.validator.validate_personality_consistency(
            self.character_state, [historical_state], timedelta(days=7)
        )

        self.assertTrue(is_consistent)
        self.assertEqual(len(issues), 0)

    def test_validate_inconsistent_rapid_change(self):
        """Test validation catches rapid personality changes."""
        # Create historical state with very different traits
        historical_state = CharacterState(
            character_id="test_char",
            name="Test Character",
            personality_traits={
                "empathy": 0.2,  # Large change from 0.7
                "neuroticism": 0.8,  # Large change from 0.3
                "extraversion": 0.1  # Large change from 0.6
            }
        )

        is_consistent, issues = self.validator.validate_personality_consistency(
            self.character_state, [historical_state], timedelta(days=1)  # Very short time
        )

        self.assertFalse(is_consistent)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("change rate" in issue for issue in issues))

    def test_validate_mood_personality_consistency(self):
        """Test mood-personality consistency validation."""
        # Test inconsistent mood-personality combination
        inconsistent_character = CharacterState(
            character_id="test_char",
            name="Test Character",
            personality_traits={
                "neuroticism": 0.9,  # Very high neuroticism
                "extraversion": -0.5  # Low extraversion
            },
            current_mood="cheerful"  # Inconsistent with high neuroticism
        )

        is_consistent, issues = self.validator.validate_personality_consistency(
            inconsistent_character, [], timedelta(days=1)
        )

        self.assertFalse(is_consistent)
        self.assertTrue(any("mood inconsistent" in issue.lower() for issue in issues))

    def test_validate_dialogue_style_consistency(self):
        """Test dialogue style consistency validation."""
        # Create historical state with very different dialogue style
        historical_state = CharacterState(
            character_id="test_char",
            name="Test Character",
            dialogue_style=DialogueStyle(
                formality_level=0.1,  # Large change from 0.6
                empathy_level=0.2,    # Large change from 0.8
                directness=0.9        # Large change from 0.5
            )
        )

        is_consistent, issues = self.validator.validate_personality_consistency(
            self.character_state, [historical_state], timedelta(days=1)
        )

        self.assertFalse(is_consistent)
        self.assertTrue(any("dialogue" in issue.lower() for issue in issues))

    def test_suggest_personality_adjustments(self):
        """Test personality adjustment suggestions."""
        # Character with inconsistent mood-personality combination
        inconsistent_character = CharacterState(
            character_id="test_char",
            name="Test Character",
            personality_traits={
                "neuroticism": 0.8,
                "extraversion": 0.2
            },
            current_mood="cheerful",
            therapeutic_role="therapist"
        )

        suggestions = self.validator.suggest_personality_adjustments(inconsistent_character)

        self.assertIsInstance(suggestions, dict)
        # Should suggest reducing neuroticism for cheerful mood
        if "neuroticism" in suggestions:
            self.assertLess(suggestions["neuroticism"], 0.8)
        # Should suggest increasing extraversion for cheerful mood
        if "extraversion" in suggestions:
            self.assertGreater(suggestions["extraversion"], 0.2)


class TestSystemIntegration(unittest.TestCase):
    """Test integration between all relationship evolution components."""

    def setUp(self):
        """Set up test fixtures."""
        self.evolution_engine = RelationshipEvolutionEngine()
        self.growth_tracker = CharacterGrowthTracker()
        self.validator = PersonalityConsistencyValidator()

        # Create test characters
        self.therapist_state = CharacterState(
            character_id="therapist_001",
            name="Dr. Sarah Wilson",
            personality_traits={
                "empathy": 0.9,
                "patience": 0.8,
                "wisdom": 0.7
            },
            therapeutic_role="therapist"
        )

        self.patient_state = CharacterState(
            character_id="patient_001",
            name="Alex Johnson",
            personality_traits={
                "neuroticism": 0.6,
                "openness": 0.5,
                "emotional_resilience": 0.4
            },
            therapeutic_role="patient"
        )

    def test_full_therapeutic_relationship_evolution(self):
        """Test complete therapeutic relationship evolution over time."""
        # Initialize relationship
        initial_metrics = self.evolution_engine.initialize_relationship(
            "therapist_001", "patient_001", RelationshipType.THERAPEUTIC
        )

        # Initialize growth tracking
        self.growth_tracker.initialize_character_growth("patient_001")

        # Simulate series of therapeutic interactions
        interactions = [
            Interaction(
                participants=["therapist_001", "patient_001"],
                interaction_type="therapeutic",
                content="Initial assessment and goal setting",
                emotional_impact=0.3,
                therapeutic_value=0.6
            ),
            Interaction(
                participants=["therapist_001", "patient_001"],
                interaction_type="therapeutic",
                content="Cognitive behavioral therapy session",
                emotional_impact=0.5,
                therapeutic_value=0.8
            ),
            Interaction(
                participants=["therapist_001", "patient_001"],
                interaction_type="therapeutic",
                content="Breakthrough moment in understanding anxiety",
                emotional_impact=0.8,
                therapeutic_value=0.9
            )
        ]

        # Process each interaction
        final_relationship_metrics = None
        for interaction in interactions:
            final_relationship_metrics = self.evolution_engine.update_relationship_from_interaction(
                "therapist_001", "patient_001", interaction
            )

        # Update character growth
        final_growth_metrics = self.growth_tracker.update_character_growth(
            "patient_001", self.patient_state, interactions
        )

        # Validate consistency
        is_consistent, issues = self.validator.validate_personality_consistency(
            self.patient_state, [], timedelta(days=30)
        )

        # Verify relationship evolution
        self.assertGreater(final_relationship_metrics.trust_level, initial_metrics.trust_level)
        self.assertGreater(final_relationship_metrics.therapeutic_alliance, initial_metrics.therapeutic_alliance)
        self.assertGreater(final_relationship_metrics.communication_quality, 0.6)

        # Verify character growth
        self.assertGreater(final_growth_metrics.therapeutic_progress, 0.0)
        self.assertGreaterEqual(final_growth_metrics.self_awareness, 0.5)

        # Verify consistency
        self.assertTrue(is_consistent)

        # Get comprehensive analysis
        relationship_analysis = self.evolution_engine.get_relationship_analysis(
            "therapist_001", "patient_001"
        )
        growth_analysis = self.growth_tracker.get_character_growth_analysis("patient_001")

        self.assertGreater(relationship_analysis["overall_score"], 0.0)
        self.assertGreater(growth_analysis["overall_growth_score"], 0.0)

    def test_relationship_with_setbacks(self):
        """Test relationship evolution with conflicts and setbacks."""
        # Initialize relationship
        self.evolution_engine.initialize_relationship(
            "therapist_001", "patient_001", RelationshipType.THERAPEUTIC
        )
        self.growth_tracker.initialize_character_growth("patient_001")

        # Mix of positive and negative interactions
        mixed_interactions = [
            Interaction(
                participants=["therapist_001", "patient_001"],
                interaction_type="therapeutic",
                content="Good progress session",
                emotional_impact=0.6,
                therapeutic_value=0.8
            ),
            Interaction(
                participants=["therapist_001", "patient_001"],
                interaction_type="conflict",
                content="Disagreement about treatment approach",
                emotional_impact=-0.4,
                therapeutic_value=0.2
            ),
            Interaction(
                participants=["therapist_001", "patient_001"],
                interaction_type="therapeutic",
                content="Working through the disagreement",
                emotional_impact=0.4,
                therapeutic_value=0.7
            )
        ]

        # Process interactions
        for interaction in mixed_interactions:
            self.evolution_engine.update_relationship_from_interaction(
                "therapist_001", "patient_001", interaction
            )

        # Update growth
        growth_metrics = self.growth_tracker.update_character_growth(
            "patient_001", self.patient_state, mixed_interactions
        )

        # Get final analysis
        relationship_analysis = self.evolution_engine.get_relationship_analysis(
            "therapist_001", "patient_001"
        )

        # Should still show overall positive relationship despite conflict
        self.assertGreater(relationship_analysis["overall_score"], -0.5)
        # Should show some conflict level
        self.assertGreater(relationship_analysis["metrics"]["conflict_level"], 0.0)
        # Should still show therapeutic progress
        self.assertGreater(growth_metrics.therapeutic_progress, 0.0)


if __name__ == "__main__":
    unittest.main()
