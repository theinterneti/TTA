"""
CoherenceValidator extracted from narrative_coherence_engine.
Implements validation across lore, character, world rules, and therapeutic alignment.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from .models import (
    ConsistencyIssue,
    ConsistencyIssueType,
    LoreEntry,
    NarrativeContent,
    ValidationResult,
    ValidationSeverity,
)
from .rules import OVERALL_WEIGHTS, SEVERITY_WEIGHTS_LORE, SEVERITY_WEIGHTS_THERAPEUTIC

logger = logging.getLogger(__name__)


class CoherenceValidator:
    """
    Core validation system for narrative consistency.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.lore_database: dict[str, LoreEntry] = {}
        self.character_profiles: dict[str, dict[str, Any]] = {}
        self.world_rules: dict[str, dict[str, Any]] = {}
        self.therapeutic_guidelines: dict[str, dict[str, Any]] = {}

        # Validation thresholds
        self.consistency_threshold = config.get("consistency_threshold", 0.7)
        self.lore_compliance_threshold = config.get("lore_compliance_threshold", 0.8)
        self.character_consistency_threshold = config.get(
            "character_consistency_threshold", 0.75
        )

        logger.info("CoherenceValidator initialized")

    async def validate_narrative_consistency(
        self, content: NarrativeContent
    ) -> ValidationResult:
        try:
            logger.debug(
                f"Validating narrative consistency for content {content.content_id}"
            )

            result = ValidationResult(
                is_valid=True,
                consistency_score=1.0,
                validation_timestamp=datetime.now(),
            )

            # Lore
            lore_issues = await self._validate_lore_compliance(content)
            result.detected_issues.extend(lore_issues)
            result.lore_compliance = self._calculate_lore_compliance_score(lore_issues)

            # Character
            character_issues = await self._validate_character_consistency(content)
            result.detected_issues.extend(character_issues)
            result.character_consistency = self._calculate_character_consistency_score(
                character_issues
            )

            # World rules
            world_rule_issues = await self._validate_world_rules(content)
            result.detected_issues.extend(world_rule_issues)

            # Therapeutic
            therapeutic_issues = await self._validate_therapeutic_alignment(content)
            result.detected_issues.extend(therapeutic_issues)
            result.therapeutic_alignment = self._calculate_therapeutic_alignment_score(
                therapeutic_issues
            )

            # Overall
            result.consistency_score = self._calculate_overall_consistency_score(result)
            result.is_valid = (
                result.consistency_score >= self.consistency_threshold
                and result.lore_compliance >= self.lore_compliance_threshold
                and result.character_consistency >= self.character_consistency_threshold
            )

            result.suggested_corrections = await self._generate_corrections(
                result.detected_issues
            )
            logger.debug(
                f"Validation completed: score={result.consistency_score:.2f}, valid={result.is_valid}"
            )
            return result
        except Exception as e:
            logger.error(f"Error validating narrative consistency: {e}")
            return ValidationResult(
                is_valid=False,
                consistency_score=0.0,
                detected_issues=[
                    ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
                        severity=ValidationSeverity.ERROR,
                        description=f"Validation error: {str(e)}",
                    )
                ],
            )

    async def _validate_lore_compliance(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        try:
            for character in content.characters:
                character_lore = self._get_character_lore(character)
                if character_lore:
                    issues.extend(
                        await self._check_character_lore_compliance(
                            content, character, character_lore
                        )
                    )
            for location in content.locations:
                location_lore = self._get_location_lore(location)
                if location_lore:
                    issues.extend(
                        await self._check_location_lore_compliance(
                            content, location, location_lore
                        )
                    )
            for theme in content.themes:
                theme_lore = self._get_theme_lore(theme)
                if theme_lore:
                    issues.extend(
                        await self._check_theme_lore_compliance(
                            content, theme, theme_lore
                        )
                    )
            logger.debug(f"Found {len(issues)} lore compliance issues")
            return issues
        except Exception as e:
            logger.error(f"Error validating lore compliance: {e}")
            return [
                ConsistencyIssue(
                    issue_id=str(uuid.uuid4()),
                    issue_type=ConsistencyIssueType.LORE_VIOLATION,
                    severity=ValidationSeverity.ERROR,
                    description=f"Lore validation error: {str(e)}",
                )
            ]

    async def _validate_character_consistency(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        try:
            for character in content.characters:
                character_profile = self.character_profiles.get(character)
                if not character_profile:
                    issues.append(
                        ConsistencyIssue(
                            issue_id=str(uuid.uuid4()),
                            issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
                            severity=ValidationSeverity.WARNING,
                            description=f"Character '{character}' not found in character database",
                            affected_elements=[character],
                        )
                    )
                    continue
                issues.extend(
                    await self._check_personality_consistency(
                        content, character, character_profile
                    )
                )
                issues.extend(
                    await self._check_dialogue_consistency(
                        content, character, character_profile
                    )
                )
                issues.extend(
                    await self._check_behavioral_consistency(
                        content, character, character_profile
                    )
                )
            logger.debug(f"Found {len(issues)} character consistency issues")
            return issues
        except Exception as e:
            logger.error(f"Error validating character consistency: {e}")
            return [
                ConsistencyIssue(
                    issue_id=str(uuid.uuid4()),
                    issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
                    severity=ValidationSeverity.ERROR,
                    description=f"Character validation error: {str(e)}",
                )
            ]

    async def _validate_world_rules(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        try:
            issues.extend(await self._check_physics_rules(content))
            issues.extend(await self._check_supernatural_rules(content))
            issues.extend(await self._check_social_rules(content))
            issues.extend(await self._check_technological_rules(content))
            logger.debug(f"Found {len(issues)} world rule issues")
            return issues
        except Exception as e:
            logger.error(f"Error validating world rules: {e}")
            return [
                ConsistencyIssue(
                    issue_id=str(uuid.uuid4()),
                    issue_type=ConsistencyIssueType.WORLD_RULE_VIOLATION,
                    severity=ValidationSeverity.ERROR,
                    description=f"World rule validation error: {str(e)}",
                )
            ]

    async def _validate_therapeutic_alignment(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        try:
            issues.extend(await self._check_harmful_content(content))
            issues.extend(await self._check_therapeutic_concepts(content))
            issues.extend(await self._check_emotional_safety(content))
            issues.extend(await self._check_therapeutic_progression(content))
            logger.debug(f"Found {len(issues)} therapeutic alignment issues")
            return issues
        except Exception as e:
            logger.error(f"Error validating therapeutic alignment: {e}")
            return [
                ConsistencyIssue(
                    issue_id=str(uuid.uuid4()),
                    issue_type=ConsistencyIssueType.THERAPEUTIC_MISALIGNMENT,
                    severity=ValidationSeverity.ERROR,
                    description=f"Therapeutic validation error: {str(e)}",
                )
            ]

    # Lookups
    def _get_character_lore(self, character: str) -> LoreEntry | None:
        return self.lore_database.get(f"character_{character}")

    def _get_location_lore(self, location: str) -> LoreEntry | None:
        return self.lore_database.get(f"location_{location}")

    def _get_theme_lore(self, theme: str) -> LoreEntry | None:
        return self.lore_database.get(f"theme_{theme}")

    # Constraint checks
    async def _check_character_lore_compliance(
        self, content: NarrativeContent, character: str, lore: LoreEntry
    ) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        for constraint in lore.constraints:
            if not await self._check_constraint_compliance(content, constraint):
                issues.append(
                    ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.LORE_VIOLATION,
                        severity=ValidationSeverity.WARNING,
                        description=f"Character '{character}' violates lore constraint: {constraint}",
                        affected_elements=[character],
                        confidence_score=0.8,
                    )
                )
        return issues

    async def _check_location_lore_compliance(
        self, content: NarrativeContent, location: str, lore: LoreEntry
    ) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        for constraint in lore.constraints:
            if not await self._check_constraint_compliance(content, constraint):
                issues.append(
                    ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.LORE_VIOLATION,
                        severity=ValidationSeverity.WARNING,
                        description=f"Location '{location}' violates lore constraint: {constraint}",
                        affected_elements=[location],
                        confidence_score=0.8,
                    )
                )
        return issues

    async def _check_theme_lore_compliance(
        self, content: NarrativeContent, theme: str, lore: LoreEntry
    ) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        for constraint in lore.constraints:
            if not await self._check_constraint_compliance(content, constraint):
                issues.append(
                    ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.LORE_VIOLATION,
                        severity=ValidationSeverity.WARNING,
                        description=f"Theme '{theme}' violates lore constraint: {constraint}",
                        affected_elements=[theme],
                        confidence_score=0.8,
                    )
                )
        return issues

    async def _check_constraint_compliance(
        self, content: NarrativeContent, constraint: str
    ) -> bool:
        constraint_lower = constraint.lower()
        content_lower = content.text.lower()
        if "must not" in constraint_lower:
            forbidden_terms = constraint_lower.split("must not")[1].strip().split()
            for term in forbidden_terms:
                if term in content_lower:
                    return False
        if "must have" in constraint_lower:
            required_terms = constraint_lower.split("must have")[1].strip().split()
            for term in required_terms:
                if term not in content_lower:
                    return False
        return True

    # Character behavior checks (placeholders)
    async def _check_personality_consistency(
        self, content: NarrativeContent, character: str, profile: dict[str, Any]
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_dialogue_consistency(
        self, content: NarrativeContent, character: str, profile: dict[str, Any]
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_behavioral_consistency(
        self, content: NarrativeContent, character: str, profile: dict[str, Any]
    ) -> list[ConsistencyIssue]:
        return []

    # World rule checks (placeholders)
    async def _check_physics_rules(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_supernatural_rules(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_social_rules(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_technological_rules(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        return []

    # Therapeutic checks (placeholders)
    async def _check_harmful_content(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_therapeutic_concepts(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_emotional_safety(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        return []

    async def _check_therapeutic_progression(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        return []

    # Scoring helpers
    def _calculate_lore_compliance_score(self, issues: list[ConsistencyIssue]) -> float:
        if not issues:
            return 1.0
        total_penalty = sum(
            SEVERITY_WEIGHTS_LORE.get(issue.severity.name, 0.5) for issue in issues
        )
        max_penalty = len(issues) * 1.0
        return max(0.0, 1.0 - (total_penalty / max_penalty))

    def _calculate_character_consistency_score(
        self, issues: list[ConsistencyIssue]
    ) -> float:
        if not issues:
            return 1.0
        total_penalty = 0.0
        for issue in issues:
            severity_weight = SEVERITY_WEIGHTS_LORE.get(issue.severity.name, 0.5)
            total_penalty += severity_weight * issue.confidence_score
        max_penalty = len(issues) * 1.0
        return max(0.0, 1.0 - (total_penalty / max_penalty))

    def _calculate_therapeutic_alignment_score(
        self, issues: list[ConsistencyIssue]
    ) -> float:
        if not issues:
            return 1.0
        total_penalty = sum(
            SEVERITY_WEIGHTS_THERAPEUTIC.get(issue.severity.name, 0.5)
            for issue in issues
        )
        max_penalty = len(issues) * 1.0
        return max(0.0, 1.0 - (total_penalty / max_penalty))

    def _calculate_overall_consistency_score(self, result: ValidationResult) -> float:
        weights = OVERALL_WEIGHTS
        score = (
            weights["lore"] * result.lore_compliance
            + weights["character"] * result.character_consistency
            + weights["causal"] * result.causal_consistency
            + weights["therapeutic"] * result.therapeutic_alignment
        )
        return score

    async def _generate_corrections(self, issues: list[ConsistencyIssue]) -> list[str]:
        corrections: list[str] = []
        for issue in issues:
            if issue.suggested_fix:
                corrections.append(issue.suggested_fix)
            else:
                correction = await self._generate_generic_correction(issue)
                if correction:
                    corrections.append(correction)
        return corrections

    async def _generate_generic_correction(self, issue: ConsistencyIssue) -> str | None:
        if issue.issue_type == ConsistencyIssueType.LORE_VIOLATION:
            return f"Review and revise content to align with established lore for {', '.join(issue.affected_elements)}"
        elif issue.issue_type == ConsistencyIssueType.CHARACTER_INCONSISTENCY:
            return f"Adjust character behavior/dialogue to match established personality for {', '.join(issue.affected_elements)}"
        elif issue.issue_type == ConsistencyIssueType.WORLD_RULE_VIOLATION:
            return f"Modify content to comply with world rules affecting {', '.join(issue.affected_elements)}"
        elif issue.issue_type == ConsistencyIssueType.THERAPEUTIC_MISALIGNMENT:
            return "Revise content to ensure therapeutic appropriateness and safety"
        else:
            return f"Address {issue.issue_type.value} issue: {issue.description}"


__all__ = ["CoherenceValidator"]
