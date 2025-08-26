"""
Tests for CrisisDetectionEngine

This module tests the crisis detection functionality for therapeutic content.
"""

import pytest
from unittest.mock import Mock

from src.components.therapeutic_safety.validators import CrisisDetectionEngine
from src.components.therapeutic_safety.models import ContentPayload, ValidationContext
from src.components.therapeutic_safety.enums import (
    CrisisLevel, ContentType, RiskCategory, ProtectiveFactor
)


class TestCrisisDetectionEngine:
    """Test CrisisDetectionEngine functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create crisis detection engine instance."""
        return CrisisDetectionEngine()
    
    @pytest.mark.asyncio
    async def test_no_crisis_detected(self, engine):
        """Test content with no crisis indicators."""
        content = ContentPayload(
            content_text="I'm feeling good today and looking forward to spending time with friends.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        assert result["component"] == "crisis_detection"
        assert result["crisis_level"] == CrisisLevel.NONE
        assert len(result["indicators"]) == 0
        assert result["immediate_intervention"] == False
        assert result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_low_crisis_level(self, engine):
        """Test content with low-level crisis indicators."""
        content = ContentPayload(
            content_text="I'm feeling down and having a hard time with things lately.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        assert result["crisis_level"] == CrisisLevel.LOW
        assert len(result["indicators"]) > 0
        assert result["immediate_intervention"] == False
        assert len(result["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_moderate_crisis_level(self, engine):
        """Test content with moderate crisis indicators."""
        content = ContentPayload(
            content_text="I feel hopeless and like nothing matters anymore. I can't go on like this.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        assert result["crisis_level"] == CrisisLevel.MODERATE
        assert len(result["indicators"]) > 0
        assert result["immediate_intervention"] == False
        assert "Professional support recommended" in result["recommendations"]
    
    @pytest.mark.asyncio
    async def test_high_crisis_level(self, engine):
        """Test content with high-level crisis indicators."""
        content = ContentPayload(
            content_text="I'm thinking about death and dying. I wish I was dead and life isn't worth living.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        assert result["crisis_level"] == CrisisLevel.HIGH
        assert len(result["indicators"]) > 0
        assert result["immediate_intervention"] == True
        assert "Immediate professional intervention recommended" in result["recommendations"]
    
    @pytest.mark.asyncio
    async def test_severe_crisis_level(self, engine):
        """Test content with severe crisis indicators."""
        content = ContentPayload(
            content_text="I want to die and kill myself. I can't take it anymore and there's no point in living.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        assert result["crisis_level"] == CrisisLevel.SEVERE
        assert len(result["indicators"]) > 0
        assert result["immediate_intervention"] == True
        assert "Contact crisis hotline or emergency services" in result["recommendations"]
    
    @pytest.mark.asyncio
    async def test_critical_crisis_level(self, engine):
        """Test content with critical crisis indicators."""
        content = ContentPayload(
            content_text="I'm going to kill myself tonight. I have a plan to end my life and I will do it.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        assert result["crisis_level"] == CrisisLevel.CRITICAL
        assert len(result["indicators"]) > 0
        assert result["immediate_intervention"] == True
        assert "Immediate professional intervention recommended" in result["recommendations"]
    
    @pytest.mark.asyncio
    async def test_suicide_risk_detection(self, engine):
        """Test specific suicide risk detection."""
        content = ContentPayload(
            content_text="I want to kill myself because nothing matters and I have no hope.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        # Should detect suicide risk
        assert RiskCategory.SUICIDE in [rf for rf in result["risk_factors"]]
        assert result["crisis_level"] >= CrisisLevel.HIGH
        assert "suicide prevention protocols" in " ".join(result["recommendations"]).lower()
    
    @pytest.mark.asyncio
    async def test_self_harm_risk_detection(self, engine):
        """Test specific self-harm risk detection."""
        content = ContentPayload(
            content_text="I want to cut myself and hurt myself because I can't cope.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        # Should detect self-harm risk
        assert RiskCategory.SELF_HARM in [rf for rf in result["risk_factors"]]
        assert result["crisis_level"] >= CrisisLevel.MODERATE
        assert "alternative coping strategies" in " ".join(result["recommendations"]).lower()
    
    @pytest.mark.asyncio
    async def test_violence_risk_detection(self, engine):
        """Test violence risk detection."""
        content = ContentPayload(
            content_text="I have violent thoughts and want to hurt others because I'm so angry.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        # Should detect violence risk
        assert RiskCategory.VIOLENCE in [rf for rf in result["risk_factors"]]
        assert result["crisis_level"] >= CrisisLevel.MODERATE
    
    @pytest.mark.asyncio
    async def test_substance_abuse_risk_detection(self, engine):
        """Test substance abuse risk detection."""
        content = ContentPayload(
            content_text="I can't stop drinking and using drugs to cope with my problems.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        # Should detect substance abuse risk
        assert RiskCategory.SUBSTANCE_ABUSE in [rf for rf in result["risk_factors"]]
    
    @pytest.mark.asyncio
    async def test_protective_factors_detection(self, engine):
        """Test protective factors detection."""
        content = ContentPayload(
            content_text="I'm struggling but I have family support and I'm seeing my therapist. "
                        "I use breathing exercises and meditation to cope.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        # Should detect protective factors
        protective_factors = result["protective_factors"]
        assert ProtectiveFactor.SOCIAL_SUPPORT.value in protective_factors
        assert ProtectiveFactor.PROFESSIONAL_HELP.value in protective_factors
        assert ProtectiveFactor.COPING_SKILLS.value in protective_factors
        
        # Recommendations should leverage protective factors
        recommendations_text = " ".join(result["recommendations"]).lower()
        assert "strengthen" in recommendations_text or "build on" in recommendations_text
    
    @pytest.mark.asyncio
    async def test_multiple_risk_factors(self, engine):
        """Test content with multiple risk factors."""
        content = ContentPayload(
            content_text="I want to hurt myself and others, I'm drinking too much, and I think about suicide.",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        # Should detect multiple risk factors
        risk_factors = result["risk_factors"]
        assert len(risk_factors) >= 3
        assert RiskCategory.SELF_HARM.value in risk_factors
        assert RiskCategory.VIOLENCE.value in risk_factors
        assert RiskCategory.SUBSTANCE_ABUSE.value in risk_factors
        assert RiskCategory.SUICIDE.value in risk_factors
        
        # Crisis level should be high due to multiple risks
        assert result["crisis_level"] >= CrisisLevel.HIGH
        assert result["immediate_intervention"] == True
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, engine):
        """Test confidence score calculation."""
        # Clear crisis indicators should have high confidence
        high_crisis_content = ContentPayload(
            content_text="I want to kill myself and end my life. I have a plan and I'm going to do it tonight.",
            content_type=ContentType.USER_INPUT
        )
        high_crisis_context = ValidationContext(user_id="test_user")
        high_crisis_result = await engine.assess_crisis(high_crisis_content, high_crisis_context)
        
        # Ambiguous content should have lower confidence
        ambiguous_content = ContentPayload(
            content_text="Bad day.",
            content_type=ContentType.USER_INPUT
        )
        ambiguous_context = ValidationContext(user_id="test_user")
        ambiguous_result = await engine.assess_crisis(ambiguous_content, ambiguous_context)
        
        assert high_crisis_result["confidence"] > ambiguous_result["confidence"]
    
    @pytest.mark.asyncio
    async def test_crisis_recommendations_specificity(self, engine):
        """Test that recommendations are specific to detected risks."""
        # Test suicide-specific recommendations
        suicide_content = ContentPayload(
            content_text="I want to kill myself and end my life.",
            content_type=ContentType.USER_INPUT
        )
        suicide_context = ValidationContext(user_id="test_user")
        suicide_result = await engine.assess_crisis(suicide_content, suicide_context)
        
        suicide_recommendations = " ".join(suicide_result["recommendations"]).lower()
        assert "suicide prevention" in suicide_recommendations
        
        # Test self-harm specific recommendations
        self_harm_content = ContentPayload(
            content_text="I want to cut myself and hurt myself.",
            content_type=ContentType.USER_INPUT
        )
        self_harm_context = ValidationContext(user_id="test_user")
        self_harm_result = await engine.assess_crisis(self_harm_content, self_harm_context)
        
        self_harm_recommendations = " ".join(self_harm_result["recommendations"]).lower()
        assert "coping strategies" in self_harm_recommendations
    
    def test_crisis_patterns_loading(self, engine):
        """Test that crisis patterns are properly loaded."""
        assert len(engine.crisis_patterns) > 0
        assert CrisisLevel.CRITICAL in engine.crisis_patterns
        assert CrisisLevel.SEVERE in engine.crisis_patterns
        assert CrisisLevel.HIGH in engine.crisis_patterns
        assert CrisisLevel.MODERATE in engine.crisis_patterns
        assert CrisisLevel.LOW in engine.crisis_patterns
        
        # Check that patterns exist for each level
        for level, patterns in engine.crisis_patterns.items():
            assert len(patterns) > 0
            assert all(isinstance(pattern, str) for pattern in patterns)
    
    def test_risk_indicators_loading(self, engine):
        """Test that risk indicators are properly loaded."""
        assert len(engine.risk_indicators) > 0
        assert RiskCategory.SUICIDE in engine.risk_indicators
        assert RiskCategory.SELF_HARM in engine.risk_indicators
        assert RiskCategory.VIOLENCE in engine.risk_indicators
        assert RiskCategory.SUBSTANCE_ABUSE in engine.risk_indicators
        
        # Check that indicators exist for each category
        for category, indicators in engine.risk_indicators.items():
            assert len(indicators) > 0
            assert all(isinstance(indicator, str) for indicator in indicators)
    
    def test_protective_indicators_loading(self, engine):
        """Test that protective indicators are properly loaded."""
        assert len(engine.protective_indicators) > 0
        assert ProtectiveFactor.SOCIAL_SUPPORT in engine.protective_indicators
        assert ProtectiveFactor.COPING_SKILLS in engine.protective_indicators
        assert ProtectiveFactor.PROFESSIONAL_HELP in engine.protective_indicators
        assert ProtectiveFactor.CRISIS_RESOURCES in engine.protective_indicators
        
        # Check that indicators exist for each factor
        for factor, indicators in engine.protective_indicators.items():
            assert len(indicators) > 0
            assert all(isinstance(indicator, str) for indicator in indicators)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, engine):
        """Test error handling in crisis detection."""
        # Test with empty content
        content = ContentPayload(content_text="", content_type=ContentType.USER_INPUT)
        context = ValidationContext(user_id="test_user")
        
        result = await engine.assess_crisis(content, context)
        
        # Should handle gracefully
        assert "component" in result
        assert "crisis_level" in result
        assert "processing_time_ms" in result
    
    def test_get_metrics(self, engine):
        """Test metrics collection."""
        metrics = engine.get_metrics()
        
        assert "assessments_performed" in metrics
        assert "crises_detected" in metrics
        assert "high_risk_content" in metrics
        assert "interventions_triggered" in metrics
        
        # Initially should be zero
        assert metrics["assessments_performed"] == 0
        assert metrics["crises_detected"] == 0
    
    @pytest.mark.asyncio
    async def test_metrics_update(self, engine):
        """Test that metrics are updated during assessment."""
        # Perform assessment with crisis
        content = ContentPayload(
            content_text="I want to kill myself",
            content_type=ContentType.USER_INPUT
        )
        context = ValidationContext(user_id="test_user")
        
        await engine.assess_crisis(content, context)
        
        metrics = engine.get_metrics()
        
        # Metrics should be updated
        assert metrics["assessments_performed"] == 1
        assert metrics["crises_detected"] == 1
        assert metrics["high_risk_content"] == 1
        assert metrics["interventions_triggered"] == 1
