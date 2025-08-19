"""
Comprehensive tests for player experience data models.
"""

import unittest
from datetime import datetime, timedelta
from typing import List

from src.player_experience.models import (
    PlayerProfile, TherapeuticPreferences, PrivacySettings, CrisisContactInfo,
    Character, CharacterAppearance, CharacterBackground, TherapeuticProfile, TherapeuticGoal,
    WorldSummary, WorldDetails, WorldParameters, CompatibilityReport, CompatibilityFactor,
    SessionContext, TherapeuticSettings, ProgressMarker, PlayerDashboard, Recommendation,
    ProgressSummary, ProgressHighlight, Milestone, EngagementMetrics,
    IntensityLevel, TherapeuticApproach, DifficultyLevel, SessionStatus, ProgressMarkerType
)
from src.player_experience.utils import ValidationError, validate_model, serialize_model, deserialize_model


class TestPlayerModels(unittest.TestCase):
    """Test player-related data models."""
    
    def test_therapeutic_preferences_creation(self):
        """Test creating therapeutic preferences."""
        prefs = TherapeuticPreferences(
            intensity_level=IntensityLevel.HIGH,
            preferred_approaches=[TherapeuticApproach.CBT, TherapeuticApproach.MINDFULNESS],
            trigger_warnings=["violence", "abandonment"],
            comfort_topics=["nature", "creativity"],
            session_duration_preference=45
        )
        
        self.assertEqual(prefs.intensity_level, IntensityLevel.HIGH)
        self.assertEqual(len(prefs.preferred_approaches), 2)
        self.assertEqual(prefs.session_duration_preference, 45)
    
    def test_therapeutic_preferences_validation(self):
        """Test therapeutic preferences validation."""
        with self.assertRaises(ValueError):
            TherapeuticPreferences(session_duration_preference=5)  # Too short
        
        with self.assertRaises(ValueError):
            TherapeuticPreferences(session_duration_preference=150)  # Too long
    
    def test_privacy_settings_creation(self):
        """Test creating privacy settings."""
        privacy = PrivacySettings(
            data_collection_consent=True,
            research_participation_consent=False,
            data_retention_period_days=180
        )
        
        self.assertTrue(privacy.data_collection_consent)
        self.assertFalse(privacy.research_participation_consent)
        self.assertEqual(privacy.data_retention_period_days, 180)
    
    def test_privacy_settings_validation(self):
        """Test privacy settings validation."""
        with self.assertRaises(ValueError):
            PrivacySettings(data_retention_period_days=20)  # Too short
        
        with self.assertRaises(ValueError):
            PrivacySettings(data_retention_period_days=3000)  # Too long
    
    def test_player_profile_creation(self):
        """Test creating a complete player profile."""
        profile = PlayerProfile(
            player_id="player_123",
            username="testuser",
            email="test@example.com",
            created_at=datetime.now()
        )
        
        self.assertEqual(profile.player_id, "player_123")
        self.assertEqual(profile.username, "testuser")
        self.assertEqual(profile.email, "test@example.com")
        self.assertEqual(len(profile.characters), 0)
        self.assertTrue(profile.is_active)
    
    def test_player_profile_validation(self):
        """Test player profile validation."""
        with self.assertRaises(ValueError):
            PlayerProfile(
                player_id="",
                username="testuser",
                email="test@example.com",
                created_at=datetime.now()
            )
        
        with self.assertRaises(ValueError):
            PlayerProfile(
                player_id="player_123",
                username="ab",  # Too short
                email="test@example.com",
                created_at=datetime.now()
            )
        
        with self.assertRaises(ValueError):
            PlayerProfile(
                player_id="player_123",
                username="testuser",
                email="invalid_email",  # Invalid email
                created_at=datetime.now()
            )
    
    def test_player_character_management(self):
        """Test player character management methods."""
        profile = PlayerProfile(
            player_id="player_123",
            username="testuser",
            email="test@example.com",
            created_at=datetime.now()
        )
        
        # Add characters
        profile.add_character("char_1")
        profile.add_character("char_2")
        self.assertEqual(len(profile.characters), 2)
        
        # Test character limit
        for i in range(3, 6):
            profile.add_character(f"char_{i}")
        
        with self.assertRaises(ValueError):
            profile.add_character("char_6")  # Exceeds limit
        
        # Remove character
        profile.remove_character("char_1")
        self.assertEqual(len(profile.characters), 4)
        self.assertNotIn("char_1", profile.characters)


class TestCharacterModels(unittest.TestCase):
    """Test character-related data models."""
    
    def test_character_appearance_creation(self):
        """Test creating character appearance."""
        appearance = CharacterAppearance(
            age_range="adult",
            gender_identity="female",
            physical_description="Tall with brown hair",
            clothing_style="professional"
        )
        
        self.assertEqual(appearance.age_range, "adult")
        self.assertEqual(appearance.gender_identity, "female")
    
    def test_character_appearance_validation(self):
        """Test character appearance validation."""
        with self.assertRaises(ValueError):
            CharacterAppearance(age_range="invalid")  # Invalid age range
    
    def test_character_background_creation(self):
        """Test creating character background."""
        background = CharacterBackground(
            name="Alice Johnson",
            backstory="A dedicated teacher seeking work-life balance",
            personality_traits=["empathetic", "organized", "perfectionist"],
            core_values=["education", "family", "integrity"]
        )
        
        self.assertEqual(background.name, "Alice Johnson")
        self.assertEqual(len(background.personality_traits), 3)
        self.assertEqual(len(background.core_values), 3)
    
    def test_character_background_validation(self):
        """Test character background validation."""
        with self.assertRaises(ValueError):
            CharacterBackground(name="A")  # Too short
        
        with self.assertRaises(ValueError):
            CharacterBackground(name="A" * 60)  # Too long
        
        with self.assertRaises(ValueError):
            CharacterBackground(name="Alice123")  # Invalid characters
    
    def test_therapeutic_goal_creation(self):
        """Test creating therapeutic goals."""
        goal = TherapeuticGoal(
            goal_id="goal_1",
            description="Improve stress management skills",
            progress_percentage=25.0,
            therapeutic_approaches=[TherapeuticApproach.CBT, TherapeuticApproach.MINDFULNESS]
        )
        
        self.assertEqual(goal.goal_id, "goal_1")
        self.assertEqual(goal.progress_percentage, 25.0)
        self.assertTrue(goal.is_active)
    
    def test_therapeutic_goal_validation(self):
        """Test therapeutic goal validation."""
        with self.assertRaises(ValueError):
            TherapeuticGoal(
                goal_id="goal_1",
                description="Test goal",
                progress_percentage=150.0  # Invalid percentage
            )
    
    def test_therapeutic_profile_creation(self):
        """Test creating therapeutic profile."""
        goal = TherapeuticGoal(
            goal_id="goal_1",
            description="Improve stress management",
            progress_percentage=30.0
        )
        
        profile = TherapeuticProfile(
            primary_concerns=["anxiety", "work stress"],
            therapeutic_goals=[goal],
            preferred_intensity=IntensityLevel.MEDIUM,
            readiness_level=0.7
        )
        
        self.assertEqual(len(profile.primary_concerns), 2)
        self.assertEqual(len(profile.therapeutic_goals), 1)
        self.assertEqual(profile.readiness_level, 0.7)
    
    def test_character_creation(self):
        """Test creating a complete character."""
        appearance = CharacterAppearance(age_range="adult")
        background = CharacterBackground(name="Test Character")
        therapeutic_profile = TherapeuticProfile()
        
        character = Character(
            character_id="char_123",
            player_id="player_123",
            name="Test Character",
            appearance=appearance,
            background=background,
            therapeutic_profile=therapeutic_profile,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        self.assertEqual(character.character_id, "char_123")
        self.assertEqual(character.name, "Test Character")
        self.assertEqual(character.session_count, 0)
        self.assertTrue(character.is_active)


class TestWorldModels(unittest.TestCase):
    """Test world-related data models."""
    
    def test_world_parameters_creation(self):
        """Test creating world parameters."""
        params = WorldParameters(
            therapeutic_intensity=0.7,
            narrative_pace="fast",
            interaction_frequency="frequent",
            challenge_level=DifficultyLevel.ADVANCED
        )
        
        self.assertEqual(params.therapeutic_intensity, 0.7)
        self.assertEqual(params.narrative_pace, "fast")
        self.assertEqual(params.challenge_level, DifficultyLevel.ADVANCED)
    
    def test_world_parameters_validation(self):
        """Test world parameters validation."""
        with self.assertRaises(ValueError):
            WorldParameters(therapeutic_intensity=1.5)  # Out of range
        
        with self.assertRaises(ValueError):
            WorldParameters(narrative_pace="invalid")  # Invalid pace
    
    def test_world_summary_creation(self):
        """Test creating world summary."""
        summary = WorldSummary(
            world_id="world_123",
            name="Peaceful Garden",
            description="A calming therapeutic environment",
            therapeutic_themes=["mindfulness", "nature therapy"],
            difficulty_level=DifficultyLevel.BEGINNER,
            compatibility_score=0.85
        )
        
        self.assertEqual(summary.world_id, "world_123")
        self.assertEqual(summary.name, "Peaceful Garden")
        self.assertEqual(summary.compatibility_score, 0.85)
    
    def test_compatibility_report_creation(self):
        """Test creating compatibility report."""
        factor = CompatibilityFactor(
            factor_name="therapeutic_approach_match",
            score=0.8,
            explanation="Good match for CBT approaches"
        )
        
        report = CompatibilityReport(
            character_id="char_123",
            world_id="world_123",
            overall_score=0.75,
            compatibility_factors=[factor]
        )
        
        self.assertEqual(report.overall_score, 0.75)
        self.assertEqual(len(report.compatibility_factors), 1)


class TestSessionModels(unittest.TestCase):
    """Test session-related data models."""
    
    def test_therapeutic_settings_creation(self):
        """Test creating therapeutic settings."""
        settings = TherapeuticSettings(
            intensity_level=0.6,
            preferred_approaches=[TherapeuticApproach.CBT],
            intervention_frequency="balanced",
            crisis_monitoring_enabled=True
        )
        
        self.assertEqual(settings.intensity_level, 0.6)
        self.assertTrue(settings.crisis_monitoring_enabled)
    
    def test_session_context_creation(self):
        """Test creating session context."""
        settings = TherapeuticSettings()
        
        context = SessionContext(
            session_id="session_123",
            player_id="player_123",
            character_id="char_123",
            world_id="world_123",
            therapeutic_settings=settings
        )
        
        self.assertEqual(context.session_id, "session_123")
        self.assertEqual(context.status, SessionStatus.ACTIVE)
        self.assertEqual(context.interaction_count, 0)
        self.assertTrue(context.is_active())
    
    def test_progress_marker_creation(self):
        """Test creating progress markers."""
        marker = ProgressMarker(
            marker_id="marker_1",
            marker_type=ProgressMarkerType.MILESTONE,
            description="Completed first therapeutic exercise",
            achieved_at=datetime.now(),
            therapeutic_value=0.8
        )
        
        self.assertEqual(marker.marker_type, ProgressMarkerType.MILESTONE)
        self.assertEqual(marker.therapeutic_value, 0.8)


class TestProgressModels(unittest.TestCase):
    """Test progress tracking data models."""
    
    def test_milestone_creation(self):
        """Test creating milestones."""
        milestone = Milestone(
            milestone_id="milestone_1",
            title="First Week Complete",
            description="Successfully completed first week of therapy",
            progress_percentage=100.0,
            is_achieved=True
        )
        
        self.assertEqual(milestone.title, "First Week Complete")
        self.assertTrue(milestone.is_achieved)
        self.assertIsNotNone(milestone.achieved_date)
    
    def test_engagement_metrics_creation(self):
        """Test creating engagement metrics."""
        metrics = EngagementMetrics(
            total_sessions=10,
            total_time_minutes=300,
            current_streak_days=5,
            dropout_risk_score=0.2
        )
        
        self.assertEqual(metrics.total_sessions, 10)
        self.assertEqual(metrics.current_streak_days, 5)
        self.assertEqual(metrics.dropout_risk_score, 0.2)
    
    def test_progress_summary_creation(self):
        """Test creating progress summary."""
        milestone = Milestone(
            milestone_id="milestone_1",
            title="Test Milestone",
            description="Test description",
            is_achieved=True
        )
        
        summary = ProgressSummary(
            player_id="player_123",
            milestones_achieved=[milestone],
            therapeutic_momentum=0.7,
            progress_trend="improving"
        )
        
        self.assertEqual(summary.player_id, "player_123")
        self.assertEqual(len(summary.milestones_achieved), 1)
        self.assertEqual(summary.therapeutic_momentum, 0.7)


class TestSerialization(unittest.TestCase):
    """Test serialization and deserialization of models."""
    
    def test_player_profile_serialization(self):
        """Test serializing and deserializing player profile."""
        original = PlayerProfile(
            player_id="player_123",
            username="testuser",
            email="test@example.com",
            created_at=datetime.now()
        )
        
        # Serialize to JSON
        json_data = serialize_model(original)
        self.assertIsInstance(json_data, str)
        
        # Deserialize back
        deserialized = deserialize_model(json_data, PlayerProfile)
        self.assertEqual(deserialized.player_id, original.player_id)
        self.assertEqual(deserialized.username, original.username)
        self.assertEqual(deserialized.email, original.email)
    
    def test_character_serialization(self):
        """Test serializing and deserializing character."""
        appearance = CharacterAppearance(age_range="adult")
        background = CharacterBackground(name="Test Character")
        therapeutic_profile = TherapeuticProfile()
        
        original = Character(
            character_id="char_123",
            player_id="player_123",
            name="Test Character",
            appearance=appearance,
            background=background,
            therapeutic_profile=therapeutic_profile,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        # Serialize to JSON
        json_data = serialize_model(original)
        self.assertIsInstance(json_data, str)
        
        # Deserialize back
        deserialized = deserialize_model(json_data, Character)
        self.assertEqual(deserialized.character_id, original.character_id)
        self.assertEqual(deserialized.name, original.name)


class TestValidation(unittest.TestCase):
    """Test validation utilities."""
    
    def test_validate_model_success(self):
        """Test successful model validation."""
        profile = PlayerProfile(
            player_id="player_123",
            username="testuser",
            email="test@example.com",
            created_at=datetime.now()
        )
        
        # Should not raise any exception
        validate_model(profile)
    
    def test_validate_model_failure(self):
        """Test model validation failure."""
        # Create an invalid profile (this will fail in __post_init__)
        with self.assertRaises(ValueError):
            profile = PlayerProfile(
                player_id="",  # Invalid empty ID
                username="testuser",
                email="test@example.com",
                created_at=datetime.now()
            )


if __name__ == '__main__':
    unittest.main()