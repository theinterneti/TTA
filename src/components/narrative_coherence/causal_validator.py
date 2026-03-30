"""CausalValidator extracted from narrative_coherence_engine.

Ensures logical cause-and-effect across narrative branches.
"""

# Logseq: [[TTA/Components/Narrative_coherence/Causal_validator]]

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from .models import (
    ConsistencyIssue,
    ConsistencyIssueType,
    NarrativeContent,
    ValidationResult,
    ValidationSeverity,
)

logger = logging.getLogger(__name__)


class CausalValidator:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.causal_rules: dict[str, dict[str, Any]] = {}
        self.logical_operators: list[str] = []
        self.consequence_patterns: dict[str, list[str]] = {}
        self._load_causal_rules()
        self._load_logical_operators()
        self._load_consequence_patterns()
        logger.info("CausalValidator initialized")

    async def validate_causal_logic(
        self, narrative_branch: list[NarrativeContent]
    ) -> ValidationResult:
        try:
            logger.debug(
                f"Validating causal logic for branch with {len(narrative_branch)} elements"
            )
            result = ValidationResult(
                is_valid=True,
                consistency_score=1.0,
                causal_consistency=1.0,
                validation_timestamp=datetime.now(),
            )
            issues = []
            issues.extend(await self._validate_causal_chains(narrative_branch))
            issues.extend(await self._validate_logical_consistency(narrative_branch))
            issues.extend(await self._validate_consequences(narrative_branch))
            result.detected_issues.extend(issues)
            result.causal_consistency = self._calculate_causal_consistency_score(issues)
            result.consistency_score = result.causal_consistency
            result.is_valid = result.causal_consistency >= self.config.get(
                "causal_threshold", 0.7
            )
            result.suggested_corrections = await self._generate_causal_corrections(
                issues
            )
            logger.debug(
                f"Causal validation completed: score={result.causal_consistency:.2f}"
            )
            return result
        except Exception as e:
            logger.error(f"Error validating causal logic: {e}")
            return ValidationResult(
                is_valid=False,
                consistency_score=0.0,
                causal_consistency=0.0,
                detected_issues=[
                    ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
                        severity=ValidationSeverity.ERROR,
                        description=f"Causal validation error: {str(e)}",
                    )
                ],
            )

    def _load_causal_rules(self):
        self.causal_rules = {
            "temporal_precedence": {
                "description": "Causes must precede effects in time",
                "weight": 1.0,
            },
            "logical_necessity": {
                "description": "Effects must be logically possible given their causes",
                "weight": 0.9,
            },
            "proportional_response": {
                "description": "Effects should be proportional to their causes",
                "weight": 0.7,
            },
            "causal_sufficiency": {
                "description": "Causes should be sufficient to produce their effects",
                "weight": 0.8,
            },
        }

    def _load_logical_operators(self):
        self.logical_operators = [
            "if",
            "then",
            "because",
            "since",
            "therefore",
            "thus",
            "hence",
            "as a result",
            "consequently",
            "due to",
            "caused by",
            "led to",
        ]

    def _load_consequence_patterns(self):
        self.consequence_patterns = {
            "immediate": ["immediately", "instantly", "right away", "at once"],
            "delayed": ["later", "eventually", "after a while", "in time"],
            "gradual": ["slowly", "gradually", "over time", "bit by bit"],
            "sudden": ["suddenly", "abruptly", "all at once", "without warning"],
        }

    async def _validate_causal_chains(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        try:
            causal_relationships = await self._extract_causal_relationships(
                narrative_branch
            )
            for relationship in causal_relationships:
                issues.extend(await self._validate_causal_relationship(relationship))
            return issues
        except Exception as e:
            logger.error(f"Error validating causal chains: {e}")
            return [
                ConsistencyIssue(
                    issue_id=str(uuid.uuid4()),
                    issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
                    severity=ValidationSeverity.ERROR,
                    description=f"Causal chain validation error: {str(e)}",
                )
            ]

    async def _validate_logical_consistency(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        try:
            issues.extend(await self._check_logical_fallacies(narrative_branch))
            issues.extend(await self._check_impossible_scenarios(narrative_branch))
            issues.extend(await self._check_circular_reasoning(narrative_branch))
            return issues
        except Exception as e:
            logger.error(f"Error validating logical consistency: {e}")
            return [
                ConsistencyIssue(
                    issue_id=str(uuid.uuid4()),
                    issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
                    severity=ValidationSeverity.ERROR,
                    description=f"Logical consistency validation error: {str(e)}",
                )
            ]

    async def _validate_consequences(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        try:
            issues.extend(
                await self._check_consequence_proportionality(narrative_branch)
            )
            issues.extend(await self._check_consequence_timing(narrative_branch))
            issues.extend(await self._check_consequence_believability(narrative_branch))
            return issues
        except Exception as e:
            logger.error(f"Error validating consequences: {e}")
            return [
                ConsistencyIssue(
                    issue_id=str(uuid.uuid4()),
                    issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
                    severity=ValidationSeverity.ERROR,
                    description=f"Consequence validation error: {str(e)}",
                )
            ]

    def _calculate_causal_consistency_score(
        self, issues: list[ConsistencyIssue]
    ) -> float:
        if not issues:
            return 1.0
        total_penalty = 0.0
        for issue in issues:
            severity_weight = {
                ValidationSeverity.INFO: 0.1,
                ValidationSeverity.WARNING: 0.3,
                ValidationSeverity.ERROR: 0.7,
                ValidationSeverity.CRITICAL: 1.0,
            }.get(issue.severity, 0.5)
            total_penalty += severity_weight * issue.confidence_score
        max_penalty = len(issues) * 1.0
        return max(0.0, 1.0 - (total_penalty / max_penalty))

    async def _generate_causal_corrections(
        self, issues: list[ConsistencyIssue]
    ) -> list[str]:
        return [f"Review causal relationship: {issue.description}" for issue in issues]

    # Placeholders for detailed causal analysis
    async def _extract_causal_relationships(
        self, _narrative_branch: list[NarrativeContent]
    ) -> list[dict[str, Any]]:
        return []

    async def _validate_causal_relationship(
        self, _relationship: dict[str, Any]
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_logical_fallacies(
        self, _narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_impossible_scenarios(
        self, _narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_circular_reasoning(
        self, _narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_consequence_proportionality(
        self, _narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_consequence_timing(
        self, _narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_consequence_believability(
        self, _narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        return []


__all__ = ["CausalValidator"]
