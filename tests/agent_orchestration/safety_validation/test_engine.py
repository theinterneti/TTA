"""Tests for safety rule engine."""

import pytest

from src.agent_orchestration.safety_validation.engine import SafetyRuleEngine
from src.agent_orchestration.safety_validation.enums import SafetyLevel, ValidationType
from src.agent_orchestration.safety_validation.models import SafetyRule


class TestSafetyRuleEngine:
    """Test SafetyRuleEngine class."""

    def test_create_engine_with_rules(self) -> None:
        """Test creating engine with a list of rules."""
        rules = [
            SafetyRule(
                id="rule1",
                category="test",
                priority=50,
                level=SafetyLevel.WARNING,
                pattern=r"test",
            )
        ]
        engine = SafetyRuleEngine(rules)
        assert len(engine._rules) == 1

    def test_from_config(self) -> None:
        """Test creating engine from configuration."""
        config = {
            "rules": [
                {
                    "id": "test_rule",
                    "category": "test",
                    "priority": 50,
                    "level": "warning",
                    "pattern": r"test",
                }
            ]
        }
        engine = SafetyRuleEngine.from_config(config)
        assert len(engine._rules) == 1
        assert engine._rules[0].id == "test_rule"

    def test_evaluate_placeholder(self) -> None:
        """Test evaluate method (placeholder implementation)."""
        rules = [
            SafetyRule(
                id="rule1",
                category="test",
                priority=50,
                level=SafetyLevel.WARNING,
                pattern=r"test",
            )
        ]
        engine = SafetyRuleEngine(rules)
        findings = engine.evaluate("test text")
        # Placeholder returns empty list
        assert findings == []

