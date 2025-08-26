"""
Comprehensive tests for gameplay loop data models.

This module tests all Pydantic models for therapeutic gameplay mechanics,
including validation, serialization, and business logic.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from src.components.gameplay_loop.models.core import (
    GameplaySession, NarrativeScene, UserChoice, ConsequenceSet, 
    TherapeuticOutcome, GameplayState, SceneType, ChoiceType, 
    ConsequenceType, SessionMetrics
)
from src.components.gameplay_loop.models.interactions import (
    UserInteraction, InteractionType, InteractionContext, 
    InteractionValidation, InteractionResponse, ValidationStatus, 
    ResponseType, InteractionBatch
)
from src.components.gameplay_loop.models.progress import (
    TherapeuticProgress, ProgressMetric, ProgressMilestone, 
    SkillDevelopment, EmotionalGrowth, BehavioralChange,
    ProgressType, MilestoneType, SkillLevel
)
from src.components.gameplay_loop.models.validation import (
    ValidationResult, ValidationRule, SafetyCheck, TherapeuticAlignment,
    ContentValidation, ValidationLevel, SafetyLevel, ValidationRuleType,
    TherapeuticAlignmentType
)


class TestCoreModels:
    """Test core gameplay loop models."""
    
    def test_gameplay_session_creation(self):
        """Test GameplaySession model creation and validation."""
        session = GameplaySession(
            user_id="user123",
            character_id="char456",
            therapeutic_goals=["anxiety_management", "social_skills"]
        )
        
        assert session.user_id == "user123"
        assert session.character_id == "char456"
        assert session.session_state == GameplayState.INITIALIZING
        assert len(session.therapeutic_goals) == 2
        assert session.safety_level == "standard"
        assert isinstance(session.session_metrics, SessionMetrics)
    
    def test_gameplay_session_invalid_safety_level(self):
        """Test GameplaySession validation with invalid safety level."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            GameplaySession(
                user_id="user123",
                safety_level="invalid_level"
            )
    
    def test_gameplay_session_completion_validation(self):
        """Test GameplaySession completion timestamp validation."""
        # Test that completed session gets timestamp
        session = GameplaySession(
            user_id="user123",
            session_state=GameplayState.COMPLETED
        )
        assert session.completed_at is not None
        
        # Test that non-completed session with timestamp raises error
        with pytest.raises(ValueError, match="Completed timestamp should only be set"):
            GameplaySession(
                user_id="user123",
                session_state=GameplayState.ACTIVE,
                completed_at=datetime.utcnow()
            )
    
    def test_narrative_scene_creation(self):
        """Test NarrativeScene model creation and validation."""
        scene = NarrativeScene(
            session_id="session123",
            title="Forest Clearing",
            description="A peaceful clearing in the woods",
            narrative_content="You find yourself in a serene forest clearing...",
            scene_type=SceneType.EXPLORATION,
            therapeutic_focus=["mindfulness", "grounding"],
            emotional_tone={"calm": 0.8, "curious": 0.6}
        )
        
        assert scene.session_id == "session123"
        assert scene.scene_type == SceneType.EXPLORATION
        assert len(scene.therapeutic_focus) == 2
        assert scene.emotional_tone["calm"] == 0.8
    
    def test_narrative_scene_invalid_emotional_tone(self):
        """Test NarrativeScene validation with invalid emotional tone."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            NarrativeScene(
                session_id="session123",
                title="Test Scene",
                description="Test description",
                narrative_content="Test content",
                emotional_tone={"anger": 1.5}  # Invalid intensity
            )
    
    def test_user_choice_creation(self):
        """Test UserChoice model creation and validation."""
        choice = UserChoice(
            scene_id="scene123",
            choice_text="Approach the mysterious figure",
            choice_type=ChoiceType.EXPLORATION,
            therapeutic_relevance=0.7,
            emotional_weight=0.5,
            difficulty_level=0.6
        )
        
        assert choice.scene_id == "scene123"
        assert choice.choice_type == ChoiceType.EXPLORATION
        assert choice.therapeutic_relevance == 0.7
    
    def test_user_choice_invalid_scores(self):
        """Test UserChoice validation with invalid scores."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UserChoice(
                scene_id="scene123",
                choice_text="Test choice",
                therapeutic_relevance=1.5  # Invalid score
            )
    
    def test_therapeutic_outcome_creation(self):
        """Test TherapeuticOutcome model creation and validation."""
        outcome = TherapeuticOutcome(
            outcome_type="skill_practice",
            description="Successfully practiced deep breathing",
            therapeutic_value=0.8,
            skills_practiced=["deep_breathing", "mindfulness"],
            emotional_growth={"anxiety": -0.3, "calm": 0.4}
        )
        
        assert outcome.outcome_type == "skill_practice"
        assert outcome.therapeutic_value == 0.8
        assert len(outcome.skills_practiced) == 2
    
    def test_consequence_set_creation(self):
        """Test ConsequenceSet model creation."""
        consequence_set = ConsequenceSet(
            choice_id="choice123",
            consequences=[{"type": "narrative", "description": "The figure smiles"}],
            consequence_type=ConsequenceType.IMMEDIATE,
            therapeutic_outcomes=[
                TherapeuticOutcome(
                    outcome_type="social_interaction",
                    description="Practiced approaching strangers",
                    therapeutic_value=0.6
                )
            ]
        )
        
        assert consequence_set.choice_id == "choice123"
        assert consequence_set.consequence_type == ConsequenceType.IMMEDIATE
        assert len(consequence_set.therapeutic_outcomes) == 1
    
    def test_session_metrics_defaults(self):
        """Test SessionMetrics default values."""
        metrics = SessionMetrics()
        
        assert metrics.choices_made == 0
        assert metrics.scenes_completed == 0
        assert metrics.therapeutic_moments == 0
        assert metrics.reflection_depth_score == 0.0
        assert metrics.engagement_score == 0.0
        assert metrics.safety_incidents == 0


class TestInteractionModels:
    """Test user interaction models."""
    
    def test_interaction_context_creation(self):
        """Test InteractionContext model creation."""
        context = InteractionContext(
            session_id="session123",
            scene_id="scene456",
            user_emotional_state={"anxiety": 0.6, "hope": 0.4},
            therapeutic_goals=["anxiety_management"],
            safety_level="standard"
        )
        
        assert context.session_id == "session123"
        assert context.user_emotional_state["anxiety"] == 0.6
        assert len(context.therapeutic_goals) == 1
    
    def test_interaction_context_invalid_emotional_state(self):
        """Test InteractionContext validation with invalid emotional state."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            InteractionContext(
                session_id="session123",
                user_emotional_state={"anxiety": 1.2}  # Invalid intensity
            )
    
    def test_user_interaction_creation(self):
        """Test UserInteraction model creation."""
        context = InteractionContext(session_id="session123")
        interaction = UserInteraction(
            session_id="session123",
            user_id="user456",
            interaction_type=InteractionType.TEXT_INPUT,
            content="I'm feeling anxious about this situation",
            context=context
        )
        
        assert interaction.session_id == "session123"
        assert interaction.interaction_type == InteractionType.TEXT_INPUT
        assert interaction.processed_at is None
    
    def test_user_interaction_processing(self):
        """Test UserInteraction processing methods."""
        context = InteractionContext(session_id="session123")
        interaction = UserInteraction(
            session_id="session123",
            user_id="user456",
            interaction_type=InteractionType.TEXT_INPUT,
            content="Test content",
            context=context
        )
        
        # Test marking as processed
        interaction.mark_processed(150.5)
        assert interaction.processed_at is not None
        assert interaction.processing_time_ms == 150.5
    
    def test_interaction_validation_creation(self):
        """Test InteractionValidation model creation."""
        validation = InteractionValidation(
            interaction_id="interaction123",
            status=ValidationStatus.VALID,
            safety_score=0.9,
            therapeutic_relevance=0.7,
            emotional_appropriateness=0.8
        )
        
        assert validation.interaction_id == "interaction123"
        assert validation.status == ValidationStatus.VALID
        assert validation.safety_score == 0.9
    
    def test_interaction_validation_invalid_scores(self):
        """Test InteractionValidation with invalid scores."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            InteractionValidation(
                interaction_id="interaction123",
                status=ValidationStatus.VALID,
                safety_score=1.5,  # Invalid score
                therapeutic_relevance=0.5,
                emotional_appropriateness=0.5
            )
    
    def test_interaction_response_creation(self):
        """Test InteractionResponse model creation."""
        response = InteractionResponse(
            interaction_id="interaction123",
            response_type=ResponseType.THERAPEUTIC_GUIDANCE,
            response_content="That's a natural response to uncertainty...",
            therapeutic_intent=["validation", "normalization"],
            emotional_tone={"empathy": 0.8, "support": 0.9}
        )
        
        assert response.interaction_id == "interaction123"
        assert response.response_type == ResponseType.THERAPEUTIC_GUIDANCE
        assert len(response.therapeutic_intent) == 2
    
    def test_interaction_batch_creation(self):
        """Test InteractionBatch model creation and methods."""
        batch = InteractionBatch(session_id="session123")
        
        context = InteractionContext(session_id="session123")
        interaction1 = UserInteraction(
            session_id="session123",
            user_id="user456",
            interaction_type=InteractionType.TEXT_INPUT,
            content="First interaction",
            context=context
        )
        interaction2 = UserInteraction(
            session_id="session123",
            user_id="user456",
            interaction_type=InteractionType.CHOICE_SELECTION,
            content="Second interaction",
            context=context
        )
        
        batch.add_interaction(interaction1)
        batch.add_interaction(interaction2)
        
        assert len(batch.interactions) == 2
        assert batch.processed_at is None
        
        # Test marking batch as processed
        batch.mark_processed(300.0)
        assert batch.processed_at is not None
        assert batch.processing_time_ms == 300.0
        assert all(interaction.processed_at is not None for interaction in batch.interactions)


class TestProgressModels:
    """Test progress tracking models."""
    
    def test_progress_metric_creation(self):
        """Test ProgressMetric model creation."""
        metric = ProgressMetric(
            metric_name="Anxiety Management",
            progress_type=ProgressType.SKILL_DEVELOPMENT,
            current_value=0.6,
            baseline_value=0.2,
            target_value=0.8,
            measurement_method="Self-report and behavioral observation"
        )
        
        assert metric.metric_name == "Anxiety Management"
        assert metric.progress_type == ProgressType.SKILL_DEVELOPMENT
        assert metric.current_value == 0.6
    
    def test_progress_metric_calculations(self):
        """Test ProgressMetric calculation methods."""
        metric = ProgressMetric(
            metric_name="Test Metric",
            progress_type=ProgressType.EMOTIONAL_GROWTH,
            current_value=0.6,
            baseline_value=0.2,
            target_value=0.8,
            measurement_method="Test method"
        )
        
        # Test progress percentage calculation
        progress_pct = metric.calculate_progress_percentage()
        expected = (0.6 - 0.2) / (0.8 - 0.2)  # 0.4 / 0.6 = 0.667
        assert abs(progress_pct - expected) < 0.001
        
        # Test improvement check
        assert metric.is_improving()
        
        # Test needs update (should be False for new metric)
        assert not metric.needs_update()
    
    def test_skill_development_creation(self):
        """Test SkillDevelopment model creation."""
        skill = SkillDevelopment(
            skill_name="Deep Breathing",
            skill_category="Anxiety Management",
            current_level=SkillLevel.DEVELOPING,
            proficiency_score=0.4,
            practice_sessions=5,
            successful_applications=3
        )
        
        assert skill.skill_name == "Deep Breathing"
        assert skill.current_level == SkillLevel.DEVELOPING
        assert skill.proficiency_score == 0.4
    
    def test_skill_development_level_advancement(self):
        """Test SkillDevelopment level advancement."""
        skill = SkillDevelopment(
            skill_name="Test Skill",
            skill_category="Test Category",
            current_level=SkillLevel.NOVICE,
            proficiency_score=0.3,  # Above threshold for DEVELOPING (0.2)
            practice_sessions=5  # Above minimum (3)
        )
        
        # Should advance from NOVICE to DEVELOPING
        advanced = skill.advance_level()
        assert advanced
        assert skill.current_level == SkillLevel.DEVELOPING
    
    def test_emotional_growth_creation(self):
        """Test EmotionalGrowth model creation."""
        growth = EmotionalGrowth(
            emotion_category="anxiety",
            regulation_score=0.6,
            awareness_score=0.7,
            expression_score=0.5,
            coping_strategies=["deep_breathing", "grounding"],
            effective_strategies=["deep_breathing"]
        )
        
        assert growth.emotion_category == "anxiety"
        assert growth.regulation_score == 0.6
        assert len(growth.coping_strategies) == 2
    
    def test_emotional_growth_calculations(self):
        """Test EmotionalGrowth calculation methods."""
        growth = EmotionalGrowth(
            emotion_category="anxiety",
            regulation_score=0.6,
            awareness_score=0.8,
            expression_score=0.4
        )
        
        overall_growth = growth.calculate_overall_growth()
        expected = (0.6 + 0.8 + 0.4) / 3.0  # 0.6
        assert abs(overall_growth - expected) < 0.001
    
    def test_behavioral_change_creation(self):
        """Test BehavioralChange model creation."""
        change = BehavioralChange(
            behavior_name="Avoidance Behavior",
            change_type="decrease",
            target_behavior="Approach challenging situations",
            baseline_frequency=5.0,
            current_frequency=3.0,
            target_frequency=1.0
        )
        
        assert change.behavior_name == "Avoidance Behavior"
        assert change.change_type == "decrease"
        assert change.baseline_frequency == 5.0
    
    def test_behavioral_change_calculations(self):
        """Test BehavioralChange calculation methods."""
        change = BehavioralChange(
            behavior_name="Test Behavior",
            change_type="decrease",
            target_behavior="Target",
            baseline_frequency=5.0,
            current_frequency=3.0,
            target_frequency=1.0
        )
        
        # Test change percentage
        change_pct = change.calculate_change_percentage()
        expected = (3.0 - 5.0) / 5.0  # -0.4 (40% decrease)
        assert abs(change_pct - expected) < 0.001
        
        # Test improvement (for decrease type, lower is better)
        assert change.is_improving()
    
    def test_progress_milestone_creation(self):
        """Test ProgressMilestone model creation."""
        milestone = ProgressMilestone(
            milestone_type=MilestoneType.BREAKTHROUGH,
            title="First Panic Attack Management",
            description="Successfully used breathing techniques during panic attack",
            therapeutic_significance=0.9,
            achievement_criteria=["Used technique", "Reduced symptoms", "Maintained control"]
        )
        
        assert milestone.milestone_type == MilestoneType.BREAKTHROUGH
        assert milestone.therapeutic_significance == 0.9
        assert len(milestone.achievement_criteria) == 3
    
    def test_therapeutic_progress_creation(self):
        """Test TherapeuticProgress model creation."""
        progress = TherapeuticProgress(
            user_id="user123",
            session_id="session456",
            overall_progress_score=0.7,
            therapeutic_momentum=0.8,
            engagement_level=0.6
        )
        
        assert progress.user_id == "user123"
        assert progress.overall_progress_score == 0.7
        assert progress.therapeutic_momentum == 0.8
    
    def test_therapeutic_progress_calculations(self):
        """Test TherapeuticProgress calculation methods."""
        # Create progress with metrics
        metric1 = ProgressMetric(
            metric_name="Metric 1",
            progress_type=ProgressType.SKILL_DEVELOPMENT,
            current_value=0.6,
            baseline_value=0.2,
            target_value=0.8,
            measurement_method="Test"
        )
        metric2 = ProgressMetric(
            metric_name="Metric 2", 
            progress_type=ProgressType.EMOTIONAL_GROWTH,
            current_value=0.8,
            baseline_value=0.4,
            target_value=1.0,
            measurement_method="Test"
        )
        
        progress = TherapeuticProgress(
            user_id="user123",
            progress_metrics=[metric1, metric2]
        )
        
        # Test overall progress calculation
        overall = progress.calculate_overall_progress()
        # metric1: (0.6-0.2)/(0.8-0.2) = 0.667
        # metric2: (0.8-0.4)/(1.0-0.4) = 0.667
        # average: 0.667
        assert abs(overall - 0.667) < 0.001
    
    def test_therapeutic_progress_needs_attention(self):
        """Test TherapeuticProgress needs attention check."""
        # Progress that needs attention
        progress_low = TherapeuticProgress(
            user_id="user123",
            overall_progress_score=0.2,  # Low progress
            therapeutic_momentum=0.2,    # Low momentum
            engagement_level=0.3         # Low engagement
        )
        assert progress_low.needs_attention()
        
        # Progress that doesn't need attention
        progress_good = TherapeuticProgress(
            user_id="user123",
            overall_progress_score=0.7,
            therapeutic_momentum=0.8,
            engagement_level=0.6
        )
        assert not progress_good.needs_attention()


class TestValidationModels:
    """Test validation models."""
    
    def test_validation_rule_creation(self):
        """Test ValidationRule model creation."""
        rule = ValidationRule(
            rule_name="Crisis Detection",
            rule_type=ValidationRuleType.CRISIS_DETECTION,
            description="Detects crisis language in user input",
            severity_level=ValidationLevel.CRITICAL,
            error_message="Crisis language detected"
        )
        
        assert rule.rule_name == "Crisis Detection"
        assert rule.rule_type == ValidationRuleType.CRISIS_DETECTION
        assert rule.severity_level == ValidationLevel.CRITICAL
    
    def test_safety_check_creation(self):
        """Test SafetyCheck model creation."""
        safety_check = SafetyCheck(
            content_id="content123",
            safety_level=SafetyLevel.SAFE,
            safety_score=0.9,
            risk_factors=["none"],
            protective_factors=["therapeutic_context", "positive_framing"]
        )
        
        assert safety_check.content_id == "content123"
        assert safety_check.safety_level == SafetyLevel.SAFE
        assert safety_check.safety_score == 0.9
    
    def test_safety_check_intervention_required(self):
        """Test SafetyCheck intervention requirement."""
        # Safe content - no intervention
        safe_check = SafetyCheck(
            content_id="content123",
            safety_level=SafetyLevel.SAFE,
            safety_score=0.9
        )
        assert not safe_check.requires_intervention()
        
        # Crisis content - requires intervention
        crisis_check = SafetyCheck(
            content_id="content456",
            safety_level=SafetyLevel.CRISIS,
            safety_score=0.1,
            crisis_indicators=["suicidal_ideation"]
        )
        assert crisis_check.requires_intervention()
    
    def test_therapeutic_alignment_creation(self):
        """Test TherapeuticAlignment model creation."""
        alignment = TherapeuticAlignment(
            content_id="content123",
            alignment_type=TherapeuticAlignmentType.SKILL_BUILDING,
            alignment_score=0.8,
            therapeutic_goals=["anxiety_management"],
            supported_skills=["deep_breathing", "grounding"]
        )
        
        assert alignment.content_id == "content123"
        assert alignment.alignment_type == TherapeuticAlignmentType.SKILL_BUILDING
        assert alignment.alignment_score == 0.8
    
    def test_therapeutic_alignment_beneficial(self):
        """Test TherapeuticAlignment beneficial check."""
        # Beneficial alignment
        good_alignment = TherapeuticAlignment(
            content_id="content123",
            alignment_type=TherapeuticAlignmentType.SKILL_BUILDING,
            alignment_score=0.8,
            therapeutic_goals=["anxiety_management"],
            contraindications=[]
        )
        assert good_alignment.is_therapeutically_beneficial()
        
        # Non-beneficial alignment (has contraindications)
        bad_alignment = TherapeuticAlignment(
            content_id="content456",
            alignment_type=TherapeuticAlignmentType.SKILL_BUILDING,
            alignment_score=0.8,
            therapeutic_goals=["anxiety_management"],
            contraindications=["trauma_trigger"]
        )
        assert not bad_alignment.is_therapeutically_beneficial()
    
    def test_content_validation_creation(self):
        """Test ContentValidation model creation."""
        safety_check = SafetyCheck(
            content_id="content123",
            safety_level=SafetyLevel.SAFE,
            safety_score=0.9
        )
        
        therapeutic_alignment = TherapeuticAlignment(
            content_id="content123",
            alignment_type=TherapeuticAlignmentType.SKILL_BUILDING,
            alignment_score=0.8,
            therapeutic_goals=["anxiety_management"]
        )
        
        validation = ContentValidation(
            content_id="content123",
            content_type="narrative_scene",
            safety_check=safety_check,
            therapeutic_alignment=therapeutic_alignment,
            is_approved=True
        )
        
        assert validation.content_id == "content123"
        assert validation.content_type == "narrative_scene"
        assert validation.is_approved
    
    def test_content_validation_score_calculation(self):
        """Test ContentValidation score calculation."""
        safety_check = SafetyCheck(
            content_id="content123",
            safety_level=SafetyLevel.SAFE,
            safety_score=0.8
        )
        
        therapeutic_alignment = TherapeuticAlignment(
            content_id="content123",
            alignment_type=TherapeuticAlignmentType.SKILL_BUILDING,
            alignment_score=0.6,
            therapeutic_goals=["test"]
        )
        
        validation = ContentValidation(
            content_id="content123",
            content_type="test",
            safety_check=safety_check,
            therapeutic_alignment=therapeutic_alignment
        )
        
        score = validation.calculate_overall_score()
        # safety: 0.8 * 0.4 = 0.32
        # therapeutic: 0.6 * 0.4 = 0.24
        # error penalty: 0.2 (no errors)
        # total: 0.32 + 0.24 + 0.2 = 0.76
        assert abs(score - 0.76) < 0.001
    
    def test_validation_result_creation(self):
        """Test ValidationResult model creation."""
        result = ValidationResult(
            session_id="session123",
            batch_safety_score=0.9,
            batch_therapeutic_score=0.8,
            overall_approval=True
        )
        
        assert result.session_id == "session123"
        assert result.batch_safety_score == 0.9
        assert result.overall_approval
