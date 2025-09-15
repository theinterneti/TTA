"""
Tests for ContentSafetyValidator

This module tests the content safety validation functionality.
"""

import pytest

from src.components.therapeutic_safety.enums import (
    AgeGroup,
    ContentType,
    RiskCategory,
    SafetyLevel,
    TherapeuticGoalCategory,
)
from src.components.therapeutic_safety.models import ContentPayload, ValidationContext
from src.components.therapeutic_safety.validators import ContentSafetyValidator


class TestContentSafetyValidator:
    """Test ContentSafetyValidator functionality."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return ContentSafetyValidator()

    @pytest.mark.asyncio
    async def test_validate_safe_content(self, validator):
        """Test validation of safe content."""
        content = ContentPayload(
            content_text="This is a positive story about overcoming challenges through healthy coping strategies.",
            content_type=ContentType.NARRATIVE_SCENE,
        )
        context = ValidationContext(user_id="test_user")

        result = await validator.validate(content, context)

        assert result["component"] == "content_safety"
        assert result["safety_level"] == SafetyLevel.SAFE
        assert len(result["violations"]) == 0
        assert result["age_appropriate"]
        assert result["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_validate_self_harm_content(self, validator):
        """Test validation of self-harm content."""
        content = ContentPayload(
            content_text="I want to cut myself because I can't handle this pain anymore.",
            content_type=ContentType.USER_INPUT,
        )
        context = ValidationContext(user_id="test_user")

        result = await validator.validate(content, context)

        assert result["safety_level"] in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]
        assert len(result["violations"]) > 0

        # Check that self-harm violation was detected
        violation_categories = [v["risk_category"] for v in result["violations"]]
        assert RiskCategory.SELF_HARM.value in violation_categories

    @pytest.mark.asyncio
    async def test_validate_suicide_content(self, validator):
        """Test validation of suicide-related content."""
        content = ContentPayload(
            content_text="I want to kill myself and end my life because nothing matters anymore.",
            content_type=ContentType.USER_INPUT,
        )
        context = ValidationContext(user_id="test_user")

        result = await validator.validate(content, context)

        assert result["safety_level"] == SafetyLevel.CRITICAL
        assert len(result["violations"]) > 0

        # Check that suicide violation was detected
        violation_categories = [v["risk_category"] for v in result["violations"]]
        assert RiskCategory.SUICIDE.value in violation_categories

        # Check high severity
        max_severity = max(v["severity"] for v in result["violations"])
        assert max_severity >= 0.8

    @pytest.mark.asyncio
    async def test_validate_violence_content(self, validator):
        """Test validation of violence-related content."""
        content = ContentPayload(
            content_text="I want to hit someone and cause violence because I'm so angry.",
            content_type=ContentType.USER_INPUT,
        )
        context = ValidationContext(user_id="test_user")

        result = await validator.validate(content, context)

        assert result["safety_level"] in [SafetyLevel.WARNING, SafetyLevel.DANGER]
        assert len(result["violations"]) > 0

        # Check that violence violation was detected
        violation_categories = [v["risk_category"] for v in result["violations"]]
        assert RiskCategory.VIOLENCE.value in violation_categories

    @pytest.mark.asyncio
    async def test_age_appropriateness_child(self, validator):
        """Test age appropriateness for child users."""
        content = ContentPayload(
            content_text="This story contains violence and death themes that might be scary.",
            content_type=ContentType.NARRATIVE_SCENE,
        )
        context = ValidationContext(user_id="test_user", user_age_group=AgeGroup.CHILD)

        result = await validator.validate(content, context)

        # Should not be age appropriate for children
        assert not result["age_appropriate"]

    @pytest.mark.asyncio
    async def test_age_appropriateness_adult(self, validator):
        """Test age appropriateness for adult users."""
        content = ContentPayload(
            content_text="This story explores complex themes of relationships and career challenges.",
            content_type=ContentType.NARRATIVE_SCENE,
        )
        context = ValidationContext(user_id="test_user", user_age_group=AgeGroup.ADULT)

        result = await validator.validate(content, context)

        # Should be age appropriate for adults
        assert result["age_appropriate"]

    @pytest.mark.asyncio
    async def test_therapeutic_alignment_cbt(self, validator):
        """Test therapeutic alignment with CBT goals."""
        content = ContentPayload(
            content_text="Let's examine your thoughts and feelings about this situation. "
            "What thinking patterns do you notice? How do your thoughts affect your behaviors?",
            content_type=ContentType.THERAPEUTIC_INTERVENTION,
        )
        context = ValidationContext(
            user_id="test_user",
            user_therapeutic_goals=[TherapeuticGoalCategory.ANXIETY_MANAGEMENT],
        )

        result = await validator.validate(content, context)

        # Should have good therapeutic alignment
        assert result["therapeutic_alignment"] > 0.5

    @pytest.mark.asyncio
    async def test_therapeutic_alignment_poor(self, validator):
        """Test poor therapeutic alignment."""
        content = ContentPayload(
            content_text="Just ignore your problems and they'll go away. Don't think about it.",
            content_type=ContentType.NARRATIVE_SCENE,
        )
        context = ValidationContext(
            user_id="test_user",
            user_therapeutic_goals=[TherapeuticGoalCategory.ANXIETY_MANAGEMENT],
        )

        result = await validator.validate(content, context)

        # Should have poor therapeutic alignment
        assert result["therapeutic_alignment"] < 0.5

    @pytest.mark.asyncio
    async def test_content_complexity_estimation(self, validator):
        """Test content complexity estimation."""
        # Simple content
        simple_content = ContentPayload(
            content_text="This is simple. It has short words."
        )
        simple_complexity = validator._estimate_content_complexity(simple_content)

        # Complex content
        complex_content = ContentPayload(
            content_text="This is an extraordinarily sophisticated narrative that encompasses "
            "multifaceted psychological concepts and intricate therapeutic methodologies "
            "designed to facilitate comprehensive understanding of complex emotional "
            "regulation strategies through carefully constructed experiential learning "
            "opportunities that integrate evidence-based therapeutic frameworks."
        )
        complex_complexity = validator._estimate_content_complexity(complex_content)

        assert simple_complexity < complex_complexity
        assert simple_complexity >= 1
        assert complex_complexity <= 5

    @pytest.mark.asyncio
    async def test_recommendations_generation(self, validator):
        """Test recommendation generation for violations."""
        content = ContentPayload(
            content_text="I want to hurt myself and use drugs to cope with my problems.",
            content_type=ContentType.USER_INPUT,
        )
        context = ValidationContext(user_id="test_user")

        result = await validator.validate(content, context)

        # Should have recommendations
        assert len(result["recommendations"]) > 0

        # Check for specific recommendations based on detected risks
        recommendations_text = " ".join(result["recommendations"]).lower()
        if any(
            v["risk_category"] == RiskCategory.SELF_HARM.value
            for v in result["violations"]
        ):
            assert (
                "coping strategies" in recommendations_text
                or "support" in recommendations_text
            )

    @pytest.mark.asyncio
    async def test_confidence_calculation(self, validator):
        """Test confidence score calculation."""
        # Short content should have lower confidence
        short_content = ContentPayload(content_text="Hi")
        short_context = ValidationContext(user_id="test_user")
        short_result = await validator.validate(short_content, short_context)

        # Long content should have higher confidence
        long_content = ContentPayload(
            content_text="This is a much longer piece of content that provides more context "
            "and information for the validation system to analyze and make "
            "confident decisions about safety and therapeutic appropriateness."
        )
        long_context = ValidationContext(user_id="test_user")
        long_result = await validator.validate(long_content, long_context)

        assert long_result["confidence"] >= short_result["confidence"]

    @pytest.mark.asyncio
    async def test_multiple_violations(self, validator):
        """Test content with multiple safety violations."""
        content = ContentPayload(
            content_text="I want to hurt myself and others, drink alcohol, and I hate my body weight.",
            content_type=ContentType.USER_INPUT,
        )
        context = ValidationContext(user_id="test_user")

        result = await validator.validate(content, context)

        # Should detect multiple violations
        assert len(result["violations"]) > 1

        # Should have multiple risk categories
        violation_categories = {v["risk_category"] for v in result["violations"]}
        assert len(violation_categories) > 1

        # Safety level should reflect multiple violations
        assert result["safety_level"] in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]

    @pytest.mark.asyncio
    async def test_validation_error_handling(self, validator):
        """Test error handling in validation."""
        # Test with invalid content
        content = ContentPayload(content_text="")  # Empty content
        context = ValidationContext(user_id="test_user")

        result = await validator.validate(content, context)

        # Should handle gracefully
        assert "component" in result
        assert "safety_level" in result
        assert "processing_time_ms" in result

    def test_get_metrics(self, validator):
        """Test metrics collection."""
        # Initially should have zero metrics
        metrics = validator.get_metrics()

        assert metrics["validations_performed"] == 0
        assert metrics["safety_violations_detected"] == 0
        assert metrics["age_inappropriate_content"] == 0
        assert metrics["therapeutic_misalignments"] == 0

    @pytest.mark.asyncio
    async def test_metrics_update(self, validator):
        """Test that metrics are updated during validation."""
        # Perform validation with violations
        content = ContentPayload(
            content_text="I want to hurt myself", content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(
            user_id="test_user",
            user_age_group=AgeGroup.CHILD,  # Age inappropriate
        )

        await validator.validate(content, context)

        metrics = validator.get_metrics()

        # Metrics should be updated
        assert metrics["validations_performed"] == 1
        assert metrics["safety_violations_detected"] == 1
        assert metrics["age_inappropriate_content"] == 1

    @pytest.mark.asyncio
    async def test_goal_keywords_mapping(self, validator):
        """Test therapeutic goal keywords mapping."""
        anxiety_keywords = validator._get_goal_keywords(
            TherapeuticGoalCategory.ANXIETY_MANAGEMENT
        )
        depression_keywords = validator._get_goal_keywords(
            TherapeuticGoalCategory.DEPRESSION_SUPPORT
        )

        assert "anxiety" in anxiety_keywords
        assert "calm" in anxiety_keywords
        assert "depression" in depression_keywords
        assert "mood" in depression_keywords

        # Keywords should be different for different goals
        assert set(anxiety_keywords) != set(depression_keywords)

    @pytest.mark.asyncio
    async def test_prohibited_patterns_detection(self, validator):
        """Test prohibited patterns detection."""
        content = ContentPayload(
            content_text="I engage in self-harm behaviors and have suicidal thoughts.",
            content_type=ContentType.USER_INPUT,
        )
        context = ValidationContext(user_id="test_user")

        result = await validator.validate(content, context)

        # Should detect prohibited patterns
        assert len(result["violations"]) > 0

        # Check that prohibited pattern violations are detected
        violation_rules = [v["rule_id"] for v in result["violations"]]
        prohibited_violations = [
            rule for rule in violation_rules if "prohibited" in rule
        ]
        assert len(prohibited_violations) > 0
