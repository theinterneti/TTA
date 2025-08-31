"""
Narrative Coherence Engine Component

This module implements the Narrative Coherence Engine that ensures story consistency
and logical narrative flow across all temporal scales in the TTA platform.

The engine validates narrative consistency against established lore, detects
contradictions, and maintains logical cause-and-effect relationships across
all possible narrative branches.

Classes:
    NarrativeCoherenceEngine: Main component for narrative coherence validation
    CoherenceValidator: Core validation system for narrative consistency
    ContradictionDetector: System for detecting narrative contradictions
    CausalValidator: Validator for cause-and-effect relationships
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ..orchestration.component import Component

logger = logging.getLogger(__name__)


# NOTE: Models moved to src/components/narrative_coherence/models.py
from .narrative_coherence.models import (
    ConsistencyIssue,
    ConsistencyIssueType,
    Contradiction,
    ConvergenceValidation,
    CreativeSolution,
    LoreEntry,
    NarrativeContent,
    NarrativeResolution,
    RetroactiveChange,
    StorylineThread,
    ValidationResult,
    ValidationSeverity,
)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ConsistencyIssueType(Enum):
    """Types of consistency issues that can be detected."""

    LORE_VIOLATION = "lore_violation"
    CHARACTER_INCONSISTENCY = "character_inconsistency"
    WORLD_RULE_VIOLATION = "world_rule_violation"
    TEMPORAL_PARADOX = "temporal_paradox"
    CAUSAL_INCONSISTENCY = "causal_inconsistency"
    THEMATIC_CONFLICT = "thematic_conflict"
    THERAPEUTIC_MISALIGNMENT = "therapeutic_misalignment"


@dataclass
class ConsistencyIssue:
    """Represents a consistency issue found during validation."""

    issue_id: str
    issue_type: ConsistencyIssueType
    severity: ValidationSeverity
    description: str
    affected_elements: list[str] = field(default_factory=list)
    suggested_fix: str | None = None
    confidence_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    """Result of narrative consistency validation."""

    is_valid: bool
    consistency_score: float  # 0.0 to 1.0
    detected_issues: list[ConsistencyIssue] = field(default_factory=list)
    suggested_corrections: list[str] = field(default_factory=list)
    lore_compliance: float = 0.0
    character_consistency: float = 0.0
    causal_consistency: float = 0.0
    therapeutic_alignment: float = 0.0
    validation_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NarrativeContent:
    """Represents narrative content to be validated."""

    content_id: str
    content_type: str  # "scene", "dialogue", "action", "description"
    text: str
    characters: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    causal_dependencies: list[str] = field(default_factory=list)
    therapeutic_concepts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LoreEntry:
    """Represents an entry in the established lore database."""

    lore_id: str
    category: str  # "character", "location", "world_rule", "history", "culture"
    title: str
    description: str
    constraints: list[str] = field(default_factory=list)
    related_entries: list[str] = field(default_factory=list)
    importance_weight: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Contradiction:
    """Represents a detected contradiction in the narrative."""

    contradiction_id: str
    type: str  # "direct", "implicit", "temporal", "causal"
    severity: ValidationSeverity
    description: str
    conflicting_elements: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    resolution_suggestions: list[str] = field(default_factory=list)
    confidence_score: float = 0.0
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class CreativeSolution:
    """Represents a creative solution for resolving narrative contradictions."""

    solution_id: str
    solution_type: str  # "character_driven", "temporal", "perspective_based", etc.
    description: str
    implementation_steps: list[str] = field(default_factory=list)
    in_world_explanation: str = ""
    effectiveness_score: float = 0.0
    narrative_cost: float = 0.0  # Cost to overall narrative coherence
    player_impact: float = 0.0  # Impact on player experience
    required_changes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NarrativeResolution:
    """Represents a completed resolution of a narrative conflict."""

    resolution_id: str
    conflict_id: str
    solution_used: CreativeSolution
    implementation_success: bool
    narrative_changes: list[str] = field(default_factory=list)
    player_explanation: str = ""
    resolution_timestamp: datetime = field(default_factory=datetime.now)
    effectiveness_rating: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetroactiveChange:
    """Represents a retroactive change to narrative content."""

    change_id: str
    target_content_id: str
    change_type: str  # "modification", "addition", "recontextualization"
    original_content: str
    modified_content: str
    justification: str
    in_world_explanation: str = ""
    impact_scope: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StorylineThread:
    """Represents a storyline thread for convergence validation."""

    thread_id: str
    title: str
    participants: list[str] = field(default_factory=list)
    key_events: list[str] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    current_tension: float = 0.0
    resolution_target: str | None = None
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConvergenceValidation:
    """Results of storyline convergence validation."""

    session_id: str
    storyline_count: int
    is_convergent: bool
    convergence_score: float
    integration_issues: list[str] = field(default_factory=list)
    convergence_points: list[str] = field(default_factory=list)
    recommended_adjustments: list[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)


class CoherenceValidator:
    """
    Core validation system for narrative consistency.

    This class handles validation of narrative content against established lore,
    character consistency, world rules, and therapeutic alignment.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize the coherence validator."""
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
        """
        Validate narrative content for consistency across all dimensions.

        Args:
            content: The narrative content to validate

        Returns:
            ValidationResult: Comprehensive validation results
        """
        try:
            logger.debug(
                f"Validating narrative consistency for content {content.content_id}"
            )

            # Initialize validation result
            result = ValidationResult(
                is_valid=True,
                consistency_score=1.0,
                validation_timestamp=datetime.now(),
            )

            # Validate against established lore
            lore_issues = await self._validate_lore_compliance(content)
            result.detected_issues.extend(lore_issues)
            result.lore_compliance = self._calculate_lore_compliance_score(lore_issues)

            # Validate character consistency
            character_issues = await self._validate_character_consistency(content)
            result.detected_issues.extend(character_issues)
            result.character_consistency = self._calculate_character_consistency_score(
                character_issues
            )

            # Validate world rules
            world_rule_issues = await self._validate_world_rules(content)
            result.detected_issues.extend(world_rule_issues)

            # Validate therapeutic alignment
            therapeutic_issues = await self._validate_therapeutic_alignment(content)
            result.detected_issues.extend(therapeutic_issues)
            result.therapeutic_alignment = self._calculate_therapeutic_alignment_score(
                therapeutic_issues
            )

            # Calculate overall consistency score
            result.consistency_score = self._calculate_overall_consistency_score(result)

            # Determine if content is valid
            result.is_valid = (
                result.consistency_score >= self.consistency_threshold
                and result.lore_compliance >= self.lore_compliance_threshold
                and result.character_consistency >= self.character_consistency_threshold
            )

            # Generate suggested corrections
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
        """Validate content against established lore."""
        issues = []

        try:
            # Check character lore compliance
            for character in content.characters:
                character_lore = self._get_character_lore(character)
                if character_lore:
                    character_issues = await self._check_character_lore_compliance(
                        content, character, character_lore
                    )
                    issues.extend(character_issues)

            # Check location lore compliance
            for location in content.locations:
                location_lore = self._get_location_lore(location)
                if location_lore:
                    location_issues = await self._check_location_lore_compliance(
                        content, location, location_lore
                    )
                    issues.extend(location_issues)

            # Check thematic lore compliance
            for theme in content.themes:
                theme_lore = self._get_theme_lore(theme)
                if theme_lore:
                    theme_issues = await self._check_theme_lore_compliance(
                        content, theme, theme_lore
                    )
                    issues.extend(theme_issues)

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
        """Validate character behavior and dialogue consistency."""
        issues = []

        try:
            for character in content.characters:
                character_profile = self.character_profiles.get(character)
                if not character_profile:
                    # Character not in database - create issue
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

                # Check personality consistency
                personality_issues = await self._check_personality_consistency(
                    content, character, character_profile
                )
                issues.extend(personality_issues)

                # Check dialogue consistency
                dialogue_issues = await self._check_dialogue_consistency(
                    content, character, character_profile
                )
                issues.extend(dialogue_issues)

                # Check behavioral consistency
                behavior_issues = await self._check_behavioral_consistency(
                    content, character, character_profile
                )
                issues.extend(behavior_issues)

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
        """Validate content against established world rules."""
        issues = []

        try:
            # Check physics rules
            physics_issues = await self._check_physics_rules(content)
            issues.extend(physics_issues)

            # Check magic/supernatural rules
            supernatural_issues = await self._check_supernatural_rules(content)
            issues.extend(supernatural_issues)

            # Check social/cultural rules
            social_issues = await self._check_social_rules(content)
            issues.extend(social_issues)

            # Check technological rules
            tech_issues = await self._check_technological_rules(content)
            issues.extend(tech_issues)

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
        """Validate therapeutic appropriateness and alignment."""
        issues = []

        try:
            # Check for harmful content
            harmful_content_issues = await self._check_harmful_content(content)
            issues.extend(harmful_content_issues)

            # Check therapeutic concept consistency
            therapeutic_issues = await self._check_therapeutic_concepts(content)
            issues.extend(therapeutic_issues)

            # Check emotional safety
            safety_issues = await self._check_emotional_safety(content)
            issues.extend(safety_issues)

            # Check therapeutic progression appropriateness
            progression_issues = await self._check_therapeutic_progression(content)
            issues.extend(progression_issues)

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

    # Helper methods for lore validation

    def _get_character_lore(self, character: str) -> LoreEntry | None:
        """Get lore entry for a character."""
        return self.lore_database.get(f"character_{character}")

    def _get_location_lore(self, location: str) -> LoreEntry | None:
        """Get lore entry for a location."""
        return self.lore_database.get(f"location_{location}")

    def _get_theme_lore(self, theme: str) -> LoreEntry | None:
        """Get lore entry for a theme."""
        return self.lore_database.get(f"theme_{theme}")

    async def _check_character_lore_compliance(
        self, content: NarrativeContent, character: str, lore: LoreEntry
    ) -> list[ConsistencyIssue]:
        """Check if character usage complies with established lore."""
        issues = []

        # Check against character constraints
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
        """Check if location usage complies with established lore."""
        issues = []

        # Check against location constraints
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
        """Check if theme usage complies with established lore."""
        issues = []

        # Check against theme constraints
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
        """Check if content complies with a specific constraint."""
        # This is a simplified implementation - in practice, this would use
        # more sophisticated NLP and rule-based checking

        # Basic keyword-based checking
        constraint_lower = constraint.lower()
        content_lower = content.text.lower()

        # Check for explicit violations
        if "must not" in constraint_lower:
            forbidden_terms = constraint_lower.split("must not")[1].strip().split()
            for term in forbidden_terms:
                if term in content_lower:
                    return False

        # Check for required elements
        if "must have" in constraint_lower:
            required_terms = constraint_lower.split("must have")[1].strip().split()
            for term in required_terms:
                if term not in content_lower:
                    return False

        return True

    # Helper methods for character consistency validation

    async def _check_personality_consistency(
        self, content: NarrativeContent, character: str, profile: dict[str, Any]
    ) -> list[ConsistencyIssue]:
        """Check if character behavior matches their personality profile."""
        issues = []

        personality_traits = profile.get("personality", {})

        # Check for personality trait violations
        for trait, value in personality_traits.items():
            if not await self._check_personality_trait_consistency(
                content, character, trait, value
            ):
                issues.append(
                    ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
                        severity=ValidationSeverity.WARNING,
                        description=f"Character '{character}' behavior inconsistent with {trait} trait (value: {value})",
                        affected_elements=[character],
                        confidence_score=0.7,
                    )
                )

        return issues

    async def _check_dialogue_consistency(
        self, content: NarrativeContent, character: str, profile: dict[str, Any]
    ) -> list[ConsistencyIssue]:
        """Check if character dialogue matches their speech patterns."""
        issues = []

        speech_patterns = profile.get("speech_patterns", {})

        # Extract character dialogue from content
        character_dialogue = await self._extract_character_dialogue(content, character)

        if character_dialogue:
            # Check speech pattern consistency
            for pattern, expected in speech_patterns.items():
                if not await self._check_speech_pattern_consistency(
                    character_dialogue, pattern, expected
                ):
                    issues.append(
                        ConsistencyIssue(
                            issue_id=str(uuid.uuid4()),
                            issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
                            severity=ValidationSeverity.INFO,
                            description=f"Character '{character}' dialogue inconsistent with {pattern} pattern",
                            affected_elements=[character],
                            confidence_score=0.6,
                        )
                    )

        return issues

    async def _check_behavioral_consistency(
        self, content: NarrativeContent, character: str, profile: dict[str, Any]
    ) -> list[ConsistencyIssue]:
        """Check if character actions match their behavioral patterns."""
        issues = []

        behavioral_patterns = profile.get("behavioral_patterns", {})

        # Extract character actions from content
        character_actions = await self._extract_character_actions(content, character)

        if character_actions:
            # Check behavioral pattern consistency
            for pattern, expected in behavioral_patterns.items():
                if not await self._check_behavioral_pattern_consistency(
                    character_actions, pattern, expected
                ):
                    issues.append(
                        ConsistencyIssue(
                            issue_id=str(uuid.uuid4()),
                            issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
                            severity=ValidationSeverity.WARNING,
                            description=f"Character '{character}' actions inconsistent with {pattern} pattern",
                            affected_elements=[character],
                            confidence_score=0.7,
                        )
                    )

        return issues

    # Scoring methods

    def _calculate_lore_compliance_score(self, issues: list[ConsistencyIssue]) -> float:
        """Calculate lore compliance score based on detected issues."""
        if not issues:
            return 1.0

        # Weight issues by severity
        severity_weights = {
            ValidationSeverity.INFO: 0.1,
            ValidationSeverity.WARNING: 0.3,
            ValidationSeverity.ERROR: 0.7,
            ValidationSeverity.CRITICAL: 1.0,
        }

        total_penalty = sum(
            severity_weights.get(issue.severity, 0.5) for issue in issues
        )
        max_penalty = len(issues) * 1.0  # Maximum possible penalty

        score = max(0.0, 1.0 - (total_penalty / max_penalty))
        return score

    def _calculate_character_consistency_score(
        self, issues: list[ConsistencyIssue]
    ) -> float:
        """Calculate character consistency score based on detected issues."""
        if not issues:
            return 1.0

        # Weight issues by confidence and severity
        total_penalty = 0.0
        for issue in issues:
            severity_weight = {
                ValidationSeverity.INFO: 0.1,
                ValidationSeverity.WARNING: 0.3,
                ValidationSeverity.ERROR: 0.7,
                ValidationSeverity.CRITICAL: 1.0,
            }.get(issue.severity, 0.5)

            penalty = severity_weight * issue.confidence_score
            total_penalty += penalty

        max_penalty = len(issues) * 1.0
        score = max(0.0, 1.0 - (total_penalty / max_penalty))
        return score

    def _calculate_therapeutic_alignment_score(
        self, issues: list[ConsistencyIssue]
    ) -> float:
        """Calculate therapeutic alignment score based on detected issues."""
        if not issues:
            return 1.0

        # Therapeutic issues are weighted more heavily
        severity_weights = {
            ValidationSeverity.INFO: 0.2,
            ValidationSeverity.WARNING: 0.5,
            ValidationSeverity.ERROR: 0.8,
            ValidationSeverity.CRITICAL: 1.0,
        }

        total_penalty = sum(
            severity_weights.get(issue.severity, 0.5) for issue in issues
        )
        max_penalty = len(issues) * 1.0

        score = max(0.0, 1.0 - (total_penalty / max_penalty))
        return score

    def _calculate_overall_consistency_score(self, result: ValidationResult) -> float:
        """Calculate overall consistency score from component scores."""
        # Weighted average of component scores
        weights = {"lore": 0.3, "character": 0.25, "causal": 0.25, "therapeutic": 0.2}

        score = (
            weights["lore"] * result.lore_compliance
            + weights["character"] * result.character_consistency
            + weights["causal"] * result.causal_consistency
            + weights["therapeutic"] * result.therapeutic_alignment
        )

        return score

    async def _generate_corrections(self, issues: list[ConsistencyIssue]) -> list[str]:
        """Generate suggested corrections for detected issues."""
        corrections = []

        for issue in issues:
            if issue.suggested_fix:
                corrections.append(issue.suggested_fix)
            else:
                # Generate generic correction based on issue type
                correction = await self._generate_generic_correction(issue)
                if correction:
                    corrections.append(correction)

        return corrections

    async def _generate_generic_correction(self, issue: ConsistencyIssue) -> str | None:
        """Generate a generic correction suggestion for an issue."""
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

    # Placeholder methods for detailed validation (to be implemented)

    async def _check_personality_trait_consistency(
        self, content: NarrativeContent, character: str, trait: str, value: Any
    ) -> bool:
        """Check if content is consistent with a character's personality trait."""
        # Placeholder implementation
        return True

    async def _extract_character_dialogue(
        self, content: NarrativeContent, character: str
    ) -> list[str]:
        """Extract dialogue lines for a specific character."""
        # Placeholder implementation
        return []

    async def _check_speech_pattern_consistency(
        self, dialogue: list[str], pattern: str, expected: Any
    ) -> bool:
        """Check if dialogue matches expected speech patterns."""
        # Placeholder implementation
        return True

    async def _extract_character_actions(
        self, content: NarrativeContent, character: str
    ) -> list[str]:
        """Extract action descriptions for a specific character."""
        # Placeholder implementation
        return []

    async def _check_behavioral_pattern_consistency(
        self, actions: list[str], pattern: str, expected: Any
    ) -> bool:
        """Check if actions match expected behavioral patterns."""
        # Placeholder implementation
        return True

    async def _check_physics_rules(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        """Check content against physics rules."""
        # Placeholder implementation
        return []

    async def _check_supernatural_rules(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        """Check content against supernatural/magic rules."""
        # Placeholder implementation
        return []

    async def _check_social_rules(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        """Check content against social/cultural rules."""
        # Placeholder implementation
        return []

    async def _check_technological_rules(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        """Check content against technological rules."""
        # Placeholder implementation
        return []

    async def _check_harmful_content(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        """Check for potentially harmful content."""
        # Placeholder implementation
        return []

    async def _check_therapeutic_concepts(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        """Check therapeutic concept consistency."""
        # Placeholder implementation
        return []

    async def _check_emotional_safety(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        """Check emotional safety of content."""
        # Placeholder implementation
        return []

    async def _check_therapeutic_progression(
        self, content: NarrativeContent
    ) -> list[ConsistencyIssue]:
        """Check therapeutic progression appropriateness."""
        # Placeholder implementation
        return []


class ContradictionDetector:
    """
    System for detecting narrative contradictions.

    This class implements algorithms to detect various types of contradictions
    in narrative content, including direct contradictions, implicit conflicts,
    and temporal inconsistencies.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize the contradiction detector."""
        self.config = config
        self.contradiction_patterns: dict[str, list[str]] = {}
        self.temporal_markers: list[str] = []
        self.causal_indicators: list[str] = []

        # Load detection patterns
        self._load_contradiction_patterns()
        self._load_temporal_markers()
        self._load_causal_indicators()

        logger.info("ContradictionDetector initialized")

    async def detect_contradictions(
        self, content_history: list[NarrativeContent]
    ) -> list[Contradiction]:
        """
        Detect contradictions across a history of narrative content.

        Args:
            content_history: List of narrative content to analyze for contradictions

        Returns:
            List of detected contradictions
        """
        try:
            logger.debug(
                f"Detecting contradictions across {len(content_history)} content pieces"
            )

            contradictions = []

            # Detect direct contradictions
            direct_contradictions = await self._detect_direct_contradictions(
                content_history
            )
            contradictions.extend(direct_contradictions)

            # Detect implicit contradictions
            implicit_contradictions = await self._detect_implicit_contradictions(
                content_history
            )
            contradictions.extend(implicit_contradictions)

            # Detect temporal contradictions
            temporal_contradictions = await self._detect_temporal_contradictions(
                content_history
            )
            contradictions.extend(temporal_contradictions)

            # Detect causal contradictions
            causal_contradictions = await self._detect_causal_contradictions(
                content_history
            )
            contradictions.extend(causal_contradictions)

            logger.info(f"Detected {len(contradictions)} contradictions")
            return contradictions

        except Exception as e:
            logger.error(f"Error detecting contradictions: {e}")
            return []

    def _load_contradiction_patterns(self):
        """Load patterns for detecting contradictions."""
        self.contradiction_patterns = {
            "negation": [
                "not",
                "never",
                "no",
                "none",
                "neither",
                "cannot",
                "won't",
                "doesn't",
            ],
            "affirmation": [
                "yes",
                "always",
                "definitely",
                "certainly",
                "absolutely",
                "indeed",
            ],
            "temporal_conflict": [
                "before",
                "after",
                "during",
                "while",
                "when",
                "then",
                "now",
                "previously",
            ],
            "state_change": [
                "became",
                "turned into",
                "transformed",
                "changed",
                "evolved",
                "grew",
            ],
            "existence": ["exists", "is", "was", "are", "were", "has", "have", "had"],
        }

    def _load_temporal_markers(self):
        """Load temporal markers for detecting time-based contradictions."""
        self.temporal_markers = [
            "yesterday",
            "today",
            "tomorrow",
            "now",
            "then",
            "before",
            "after",
            "during",
            "while",
            "when",
            "since",
            "until",
            "ago",
            "later",
            "morning",
            "afternoon",
            "evening",
            "night",
            "dawn",
            "dusk",
        ]

    def _load_causal_indicators(self):
        """Load causal indicators for detecting cause-effect contradictions."""
        self.causal_indicators = [
            "because",
            "since",
            "due to",
            "as a result",
            "therefore",
            "thus",
            "consequently",
            "hence",
            "so",
            "caused by",
            "led to",
            "resulted in",
        ]

    async def _detect_direct_contradictions(
        self, content_history: list[NarrativeContent]
    ) -> list[Contradiction]:
        """Detect direct contradictions between content pieces."""
        contradictions = []

        try:
            # Compare each pair of content pieces
            for i in range(len(content_history)):
                for j in range(i + 1, len(content_history)):
                    content1 = content_history[i]
                    content2 = content_history[j]

                    # Check for direct contradictions
                    direct_conflicts = await self._find_direct_conflicts(
                        content1, content2
                    )
                    contradictions.extend(direct_conflicts)

            return contradictions

        except Exception as e:
            logger.error(f"Error detecting direct contradictions: {e}")
            return []

    async def _detect_implicit_contradictions(
        self, content_history: list[NarrativeContent]
    ) -> list[Contradiction]:
        """Detect implicit contradictions that require inference."""
        contradictions = []

        try:
            # Analyze content for implicit conflicts
            for i in range(len(content_history)):
                for j in range(i + 1, len(content_history)):
                    content1 = content_history[i]
                    content2 = content_history[j]

                    # Check for implicit contradictions
                    implicit_conflicts = await self._find_implicit_conflicts(
                        content1, content2
                    )
                    contradictions.extend(implicit_conflicts)

            return contradictions

        except Exception as e:
            logger.error(f"Error detecting implicit contradictions: {e}")
            return []

    async def _detect_temporal_contradictions(
        self, content_history: list[NarrativeContent]
    ) -> list[Contradiction]:
        """Detect temporal contradictions in the narrative timeline."""
        contradictions = []

        try:
            # Build temporal sequence from content
            temporal_events = await self._extract_temporal_events(content_history)

            # Check for temporal inconsistencies
            for i in range(len(temporal_events)):
                for j in range(i + 1, len(temporal_events)):
                    event1 = temporal_events[i]
                    event2 = temporal_events[j]

                    # Check for temporal conflicts
                    temporal_conflicts = await self._find_temporal_conflicts(
                        event1, event2
                    )
                    contradictions.extend(temporal_conflicts)

            return contradictions

        except Exception as e:
            logger.error(f"Error detecting temporal contradictions: {e}")
            return []

    async def _detect_causal_contradictions(
        self, content_history: list[NarrativeContent]
    ) -> list[Contradiction]:
        """Detect causal contradictions in cause-effect relationships."""
        contradictions = []

        try:
            # Extract causal relationships
            causal_chains = await self._extract_causal_chains(content_history)

            # Check for causal inconsistencies
            for chain in causal_chains:
                causal_conflicts = await self._find_causal_conflicts(chain)
                contradictions.extend(causal_conflicts)

            return contradictions

        except Exception as e:
            logger.error(f"Error detecting causal contradictions: {e}")
            return []

    # Placeholder methods for detailed contradiction detection

    async def _find_direct_conflicts(
        self, content1: NarrativeContent, content2: NarrativeContent
    ) -> list[Contradiction]:
        """Find direct conflicts between two content pieces."""
        # Placeholder implementation
        return []

    async def _find_implicit_conflicts(
        self, content1: NarrativeContent, content2: NarrativeContent
    ) -> list[Contradiction]:
        """Find implicit conflicts between two content pieces."""
        # Placeholder implementation
        return []

    async def _extract_temporal_events(
        self, content_history: list[NarrativeContent]
    ) -> list[dict[str, Any]]:
        """Extract temporal events from content history."""
        # Placeholder implementation
        return []

    async def _find_temporal_conflicts(
        self, event1: dict[str, Any], event2: dict[str, Any]
    ) -> list[Contradiction]:
        """Find temporal conflicts between two events."""
        # Placeholder implementation
        return []

    async def _extract_causal_chains(
        self, content_history: list[NarrativeContent]
    ) -> list[list[dict[str, Any]]]:
        """Extract causal chains from content history."""
        # Placeholder implementation
        return []

    async def _find_causal_conflicts(
        self, causal_chain: list[dict[str, Any]]
    ) -> list[Contradiction]:
        """Find causal conflicts within a causal chain."""
        # Placeholder implementation
        return []


class CausalValidator:
    """
    Validator for logical cause-and-effect relationships in narrative branches.

    This class ensures that narrative events follow logical causal relationships
    and that player choices lead to believable consequences across all narrative scales.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize the causal validator."""
        self.config = config
        self.causal_rules: dict[str, dict[str, Any]] = {}
        self.logical_operators: list[str] = []
        self.consequence_patterns: dict[str, list[str]] = {}

        # Load causal validation rules
        self._load_causal_rules()
        self._load_logical_operators()
        self._load_consequence_patterns()

        logger.info("CausalValidator initialized")

    async def validate_causal_logic(
        self, narrative_branch: list[NarrativeContent]
    ) -> ValidationResult:
        """
        Validate the causal logic of a narrative branch.

        Args:
            narrative_branch: Sequence of narrative content representing a branch

        Returns:
            ValidationResult: Results of causal validation
        """
        try:
            logger.debug(
                f"Validating causal logic for branch with {len(narrative_branch)} elements"
            )

            # Initialize validation result
            result = ValidationResult(
                is_valid=True,
                consistency_score=1.0,
                causal_consistency=1.0,
                validation_timestamp=datetime.now(),
            )

            # Validate causal chains
            causal_issues = await self._validate_causal_chains(narrative_branch)
            result.detected_issues.extend(causal_issues)

            # Validate logical consistency
            logical_issues = await self._validate_logical_consistency(narrative_branch)
            result.detected_issues.extend(logical_issues)

            # Validate consequence appropriateness
            consequence_issues = await self._validate_consequences(narrative_branch)
            result.detected_issues.extend(consequence_issues)

            # Calculate causal consistency score
            result.causal_consistency = self._calculate_causal_consistency_score(
                result.detected_issues
            )

            # Update overall consistency score
            result.consistency_score = result.causal_consistency

            # Determine validity
            result.is_valid = result.causal_consistency >= self.config.get(
                "causal_threshold", 0.7
            )

            # Generate corrections
            result.suggested_corrections = await self._generate_causal_corrections(
                result.detected_issues
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
        """Load rules for causal validation."""
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
        """Load logical operators for causal analysis."""
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
        """Load patterns for consequence validation."""
        self.consequence_patterns = {
            "immediate": ["immediately", "instantly", "right away", "at once"],
            "delayed": ["later", "eventually", "after a while", "in time"],
            "gradual": ["slowly", "gradually", "over time", "bit by bit"],
            "sudden": ["suddenly", "abruptly", "all at once", "without warning"],
        }

    async def _validate_causal_chains(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        """Validate causal chains within the narrative branch."""
        issues = []

        try:
            # Extract causal relationships
            causal_relationships = await self._extract_causal_relationships(
                narrative_branch
            )

            # Validate each causal relationship
            for relationship in causal_relationships:
                relationship_issues = await self._validate_causal_relationship(
                    relationship
                )
                issues.extend(relationship_issues)

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
        """Validate logical consistency of the narrative branch."""
        issues = []

        try:
            # Check for logical fallacies
            fallacy_issues = await self._check_logical_fallacies(narrative_branch)
            issues.extend(fallacy_issues)

            # Check for impossible scenarios
            impossibility_issues = await self._check_impossible_scenarios(
                narrative_branch
            )
            issues.extend(impossibility_issues)

            # Check for circular reasoning
            circular_issues = await self._check_circular_reasoning(narrative_branch)
            issues.extend(circular_issues)

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
        """Validate appropriateness of consequences."""
        issues = []

        try:
            # Check consequence proportionality
            proportionality_issues = await self._check_consequence_proportionality(
                narrative_branch
            )
            issues.extend(proportionality_issues)

            # Check consequence timing
            timing_issues = await self._check_consequence_timing(narrative_branch)
            issues.extend(timing_issues)

            # Check consequence believability
            believability_issues = await self._check_consequence_believability(
                narrative_branch
            )
            issues.extend(believability_issues)

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
        """Calculate causal consistency score based on detected issues."""
        if not issues:
            return 1.0

        # Weight issues by severity and type
        total_penalty = 0.0
        for issue in issues:
            severity_weight = {
                ValidationSeverity.INFO: 0.1,
                ValidationSeverity.WARNING: 0.3,
                ValidationSeverity.ERROR: 0.7,
                ValidationSeverity.CRITICAL: 1.0,
            }.get(issue.severity, 0.5)

            # Causal issues are weighted by confidence
            penalty = severity_weight * issue.confidence_score
            total_penalty += penalty

        max_penalty = len(issues) * 1.0
        score = max(0.0, 1.0 - (total_penalty / max_penalty))
        return score

    async def _generate_causal_corrections(
        self, issues: list[ConsistencyIssue]
    ) -> list[str]:
        """Generate corrections for causal consistency issues."""
        corrections = []

        for issue in issues:
            if issue.issue_type == ConsistencyIssueType.CAUSAL_INCONSISTENCY:
                correction = f"Review causal relationship: {issue.description}"
                corrections.append(correction)

        return corrections

    # Placeholder methods for detailed causal validation

    async def _extract_causal_relationships(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[dict[str, Any]]:
        """Extract causal relationships from narrative branch."""
        # Placeholder implementation
        return []

    async def _validate_causal_relationship(
        self, relationship: dict[str, Any]
    ) -> list[ConsistencyIssue]:
        """Validate a specific causal relationship."""
        # Placeholder implementation
        return []

    async def _check_logical_fallacies(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        """Check for logical fallacies in the narrative."""
        # Placeholder implementation
        return []

    async def _check_impossible_scenarios(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        """Check for impossible scenarios."""
        # Placeholder implementation
        return []

    async def _check_circular_reasoning(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        """Check for circular reasoning."""
        # Placeholder implementation
        return []

    async def _check_consequence_proportionality(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        """Check if consequences are proportional to their causes."""
        # Placeholder implementation
        return []

    async def _check_consequence_timing(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        """Check if consequence timing is appropriate."""
        # Placeholder implementation
        return []

    async def _check_consequence_believability(
        self, narrative_branch: list[NarrativeContent]
    ) -> list[ConsistencyIssue]:
        """Check if consequences are believable."""
        # Placeholder implementation
        return []


class NarrativeCoherenceEngine(Component):
    """
    Main component for narrative coherence validation and management.

    This component orchestrates the various coherence validation systems
    and provides a unified interface for ensuring narrative consistency
    across the TTA platform.
    """

    def __init__(self, config: Any):
        """Initialize the Narrative Coherence Engine component."""
        super().__init__(
            config=config,
            name="narrative_coherence_engine",
            dependencies=["neo4j", "redis"],
        )

        # Get component configuration
        self.component_config = self.get_config()

        # Initialize validation systems
        self.coherence_validator = CoherenceValidator(self.component_config)
        self.contradiction_detector = ContradictionDetector(self.component_config)
        self.causal_validator = CausalValidator(self.component_config)

        # Content history for contradiction detection
        self.content_history: dict[str, list[NarrativeContent]] = {}

        # Validation cache
        self.validation_cache: dict[str, ValidationResult] = {}
        self.cache_ttl = self.component_config.get("cache_ttl", 300)  # 5 minutes

        logger.info("NarrativeCoherenceEngine component initialized")

    def _start_impl(self) -> bool:
        """Start the Narrative Coherence Engine component."""
        try:
            logger.info("Starting Narrative Coherence Engine")

            # Initialize validation systems
            logger.info("Coherence validation systems initialized")

            # Load lore database (placeholder)
            self._load_lore_database()

            # Load character profiles (placeholder)
            self._load_character_profiles()

            # Load world rules (placeholder)
            self._load_world_rules()

            # Load therapeutic guidelines (placeholder)
            self._load_therapeutic_guidelines()

            logger.info("Narrative Coherence Engine started successfully")
            return True

        except Exception as e:
            logger.error(f"Error starting Narrative Coherence Engine: {e}")
            return False

    def _stop_impl(self) -> bool:
        """Stop the Narrative Coherence Engine component."""
        try:
            logger.info("Stopping Narrative Coherence Engine")

            # Clear caches
            self.content_history.clear()
            self.validation_cache.clear()

            logger.info("Narrative Coherence Engine stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Error stopping Narrative Coherence Engine: {e}")
            return False

    async def validate_narrative_consistency(
        self, content: NarrativeContent, session_id: str
    ) -> ValidationResult:
        """
        Validate narrative content for consistency.

        Args:
            content: The narrative content to validate
            session_id: Session ID for context

        Returns:
            ValidationResult: Comprehensive validation results
        """
        try:
            logger.debug(f"Validating narrative consistency for session {session_id}")

            # Check cache first
            cache_key = f"{session_id}_{content.content_id}"
            cached_result = self._get_cached_validation(cache_key)
            if cached_result:
                logger.debug("Returning cached validation result")
                return cached_result

            # Perform validation
            result = await self.coherence_validator.validate_narrative_consistency(
                content
            )

            # Add content to history for contradiction detection
            if session_id not in self.content_history:
                self.content_history[session_id] = []
            self.content_history[session_id].append(content)

            # Detect contradictions with previous content
            if len(self.content_history[session_id]) > 1:
                contradictions = (
                    await self.contradiction_detector.detect_contradictions(
                        self.content_history[session_id]
                    )
                )

                # Add contradiction issues to result
                for contradiction in contradictions:
                    issue = ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
                        severity=contradiction.severity,
                        description=contradiction.description,
                        affected_elements=contradiction.conflicting_elements,
                        confidence_score=contradiction.confidence_score,
                    )
                    result.detected_issues.append(issue)

            # Cache result
            self._cache_validation_result(cache_key, result)

            logger.debug(
                f"Validation completed: {len(result.detected_issues)} issues found"
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

    async def detect_contradictions(self, session_id: str) -> list[Contradiction]:
        """
        Detect contradictions in the narrative history for a session.

        Args:
            session_id: Session ID to check for contradictions

        Returns:
            List of detected contradictions
        """
        try:
            logger.debug(f"Detecting contradictions for session {session_id}")

            content_history = self.content_history.get(session_id, [])
            if len(content_history) < 2:
                logger.debug("Not enough content history for contradiction detection")
                return []

            contradictions = await self.contradiction_detector.detect_contradictions(
                content_history
            )

            logger.info(
                f"Detected {len(contradictions)} contradictions for session {session_id}"
            )
            return contradictions

        except Exception as e:
            logger.error(f"Error detecting contradictions: {e}")
            return []

    async def validate_causal_logic(
        self, narrative_branch: list[NarrativeContent]
    ) -> ValidationResult:
        """
        Validate the causal logic of a narrative branch.

        Args:
            narrative_branch: Sequence of narrative content representing a branch

        Returns:
            ValidationResult: Results of causal validation
        """
        try:
            logger.debug(
                f"Validating causal logic for branch with {len(narrative_branch)} elements"
            )

            result = await self.causal_validator.validate_causal_logic(narrative_branch)

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

    async def get_coherence_status(self, session_id: str) -> dict[str, Any]:
        """
        Get the current coherence status for a session.

        Args:
            session_id: Session ID to get status for

        Returns:
            Dictionary containing coherence status information
        """
        try:
            content_history = self.content_history.get(session_id, [])

            if not content_history:
                return {
                    "session_id": session_id,
                    "content_count": 0,
                    "overall_coherence": 1.0,
                    "contradiction_count": 0,
                    "last_validation": None,
                }

            # Get latest validation results
            latest_content = content_history[-1]
            latest_validation = await self.validate_narrative_consistency(
                latest_content, session_id
            )

            # Detect contradictions
            contradictions = await self.detect_contradictions(session_id)

            return {
                "session_id": session_id,
                "content_count": len(content_history),
                "overall_coherence": latest_validation.consistency_score,
                "lore_compliance": latest_validation.lore_compliance,
                "character_consistency": latest_validation.character_consistency,
                "causal_consistency": latest_validation.causal_consistency,
                "therapeutic_alignment": latest_validation.therapeutic_alignment,
                "contradiction_count": len(contradictions),
                "issue_count": len(latest_validation.detected_issues),
                "last_validation": latest_validation.validation_timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting coherence status: {e}")
            return {"session_id": session_id, "error": str(e)}

    def _get_cached_validation(self, cache_key: str) -> ValidationResult | None:
        """Get cached validation result if still valid."""
        if cache_key in self.validation_cache:
            cached_result = self.validation_cache[cache_key]
            # Check if cache is still valid
            age = datetime.now() - cached_result.validation_timestamp
            if age.total_seconds() < self.cache_ttl:
                return cached_result
            else:
                # Remove expired cache entry
                del self.validation_cache[cache_key]

        return None

    def _cache_validation_result(self, cache_key: str, result: ValidationResult):
        """Cache validation result."""
        self.validation_cache[cache_key] = result

        # Clean up old cache entries periodically
        if len(self.validation_cache) > 1000:  # Arbitrary limit
            self._cleanup_cache()

    def _cleanup_cache(self):
        """Clean up expired cache entries."""
        current_time = datetime.now()
        expired_keys = []

        for key, result in self.validation_cache.items():
            age = current_time - result.validation_timestamp
            if age.total_seconds() > self.cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self.validation_cache[key]

        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    # Placeholder methods for loading data (to be implemented with actual data sources)

    def _load_lore_database(self):
        """Load the lore database from storage."""
        # Placeholder implementation
        logger.info("Lore database loaded (placeholder)")

    def _load_character_profiles(self):
        """Load character profiles from storage."""
        # Placeholder implementation
        logger.info("Character profiles loaded (placeholder)")

    def _load_world_rules(self):
        """Load world rules from storage."""
        # Placeholder implementation
        logger.info("World rules loaded (placeholder)")

    def _load_therapeutic_guidelines(self):
        """Load therapeutic guidelines from storage."""
        # Placeholder implementation
        logger.info("Therapeutic guidelines loaded (placeholder)")

    # Conflict Resolution Methods (Task 4.2 Implementation)

    async def resolve_narrative_conflicts(
        self, conflicts: list[Contradiction], session_id: str
    ) -> list["NarrativeResolution"]:
        """
        Resolve narrative conflicts through creative solutions and retroactive changes.

        Args:
            conflicts: List of contradictions to resolve
            session_id: Session ID for context

        Returns:
            List of narrative resolutions
        """
        try:
            logger.info(
                f"Resolving {len(conflicts)} narrative conflicts for session {session_id}"
            )

            resolutions = []

            for conflict in conflicts:
                logger.debug(
                    f"Resolving conflict {conflict.contradiction_id}: {conflict.type}"
                )

                # Generate creative solutions for the conflict
                creative_solutions = await self.generate_creative_solutions(
                    conflict, session_id
                )

                # Select the best solution based on narrative cost and effectiveness
                best_solution = await self._select_best_solution(
                    creative_solutions, conflict
                )

                if best_solution:
                    # Implement the resolution
                    resolution = await self._implement_conflict_resolution(
                        best_solution, conflict, session_id
                    )
                    if resolution:
                        resolutions.append(resolution)
                        logger.debug(
                            f"Successfully resolved conflict {conflict.contradiction_id}"
                        )
                    else:
                        logger.warning(
                            f"Failed to implement resolution for conflict {conflict.contradiction_id}"
                        )
                else:
                    logger.warning(
                        f"No viable solution found for conflict {conflict.contradiction_id}"
                    )

            logger.info(
                f"Successfully resolved {len(resolutions)} out of {len(conflicts)} conflicts"
            )
            return resolutions

        except Exception as e:
            logger.error(f"Error resolving narrative conflicts: {e}")
            return []

    async def generate_creative_solutions(
        self, conflict: Contradiction, session_id: str
    ) -> list["CreativeSolution"]:
        """
        Generate creative narrative solutions for contradictions.

        Args:
            conflict: The contradiction to resolve
            session_id: Session ID for context

        Returns:
            List of creative solutions
        """
        try:
            logger.debug(
                f"Generating creative solutions for conflict {conflict.contradiction_id}"
            )

            solutions = []

            # Get narrative context
            content_history = self.content_history.get(session_id, [])

            # Generate different types of creative solutions based on conflict type
            if conflict.type == "direct":
                # Direct contradictions need character-driven explanations
                solutions.extend(
                    await self._generate_character_driven_solutions(
                        conflict, content_history
                    )
                )
                solutions.extend(
                    await self._generate_perspective_based_solutions(
                        conflict, content_history
                    )
                )

            elif conflict.type == "temporal":
                # Temporal conflicts need time-based explanations
                solutions.extend(
                    await self._generate_temporal_solutions(conflict, content_history)
                )
                solutions.extend(
                    await self._generate_memory_based_solutions(
                        conflict, content_history
                    )
                )

            elif conflict.type == "causal":
                # Causal conflicts need logical bridging
                solutions.extend(
                    await self._generate_causal_bridge_solutions(
                        conflict, content_history
                    )
                )
                solutions.extend(
                    await self._generate_hidden_factor_solutions(
                        conflict, content_history
                    )
                )

            elif conflict.type == "implicit":
                # Implicit conflicts need subtle recontextualization
                solutions.extend(
                    await self._generate_recontextualization_solutions(
                        conflict, content_history
                    )
                )
                solutions.extend(
                    await self._generate_subtext_solutions(conflict, content_history)
                )

            # Add universal solution types that work for any conflict
            solutions.extend(
                await self._generate_universal_solutions(conflict, content_history)
            )

            # Score and rank solutions
            for solution in solutions:
                solution.effectiveness_score = (
                    await self._calculate_solution_effectiveness(solution, conflict)
                )
                solution.narrative_cost = await self._calculate_narrative_cost(
                    solution, content_history
                )
                solution.player_impact = await self._calculate_player_impact(
                    solution, session_id
                )

            # Sort by effectiveness and narrative cost
            solutions.sort(
                key=lambda s: (s.effectiveness_score, -s.narrative_cost), reverse=True
            )

            logger.debug(f"Generated {len(solutions)} creative solutions")
            return solutions

        except Exception as e:
            logger.error(f"Error generating creative solutions: {e}")
            return []

    async def manage_retroactive_changes(
        self, changes: list["RetroactiveChange"], session_id: str
    ) -> bool:
        """
        Manage retroactive changes with in-world explanations.

        Args:
            changes: List of retroactive changes to implement
            session_id: Session ID for context

        Returns:
            bool: True if changes were successfully managed
        """
        try:
            logger.info(
                f"Managing {len(changes)} retroactive changes for session {session_id}"
            )

            # Validate changes don't create new conflicts
            validation_result = await self._validate_retroactive_changes(
                changes, session_id
            )
            if not validation_result.is_valid:
                logger.warning(
                    "Retroactive changes would create new conflicts, aborting"
                )
                return False

            # Generate in-world explanations for each change
            explanations = []
            for change in changes:
                explanation = await self._generate_in_world_explanation(
                    change, session_id
                )
                if explanation:
                    explanations.append(explanation)
                else:
                    logger.warning(
                        f"Could not generate explanation for change {change.change_id}"
                    )
                    return False

            # Apply changes with explanations
            for change, explanation in zip(changes, explanations, strict=False):
                success = await self._apply_retroactive_change(
                    change, explanation, session_id
                )
                if not success:
                    logger.error(
                        f"Failed to apply retroactive change {change.change_id}"
                    )
                    return False

            # Update content history to reflect changes
            await self._update_content_history_with_changes(changes, session_id)

            logger.info("Successfully managed all retroactive changes")
            return True

        except Exception as e:
            logger.error(f"Error managing retroactive changes: {e}")
            return False

    async def validate_storyline_convergence(
        self, storylines: list["StorylineThread"], session_id: str
    ) -> "ConvergenceValidation":
        """
        Validate storyline convergence and integration.

        Args:
            storylines: List of storyline threads to validate convergence for
            session_id: Session ID for context

        Returns:
            ConvergenceValidation: Results of convergence validation
        """
        try:
            logger.debug(
                f"Validating convergence of {len(storylines)} storylines for session {session_id}"
            )

            # Initialize validation result
            validation = ConvergenceValidation(
                session_id=session_id,
                storyline_count=len(storylines),
                is_convergent=True,
                convergence_score=1.0,
                integration_issues=[],
                convergence_points=[],
                recommended_adjustments=[],
            )

            # Check for convergence conflicts
            conflicts = await self._detect_convergence_conflicts(storylines)
            validation.integration_issues.extend(conflicts)

            # Identify natural convergence points
            convergence_points = await self._identify_convergence_points(storylines)
            validation.convergence_points = convergence_points

            # Validate character consistency across storylines
            character_issues = (
                await self._validate_cross_storyline_character_consistency(storylines)
            )
            validation.integration_issues.extend(character_issues)

            # Validate thematic coherence
            thematic_issues = await self._validate_thematic_coherence_across_storylines(
                storylines
            )
            validation.integration_issues.extend(thematic_issues)

            # Validate pacing and tension balance
            pacing_issues = await self._validate_convergence_pacing(storylines)
            validation.integration_issues.extend(pacing_issues)

            # Calculate overall convergence score
            validation.convergence_score = await self._calculate_convergence_score(
                validation
            )
            validation.is_convergent = (
                validation.convergence_score >= 0.7
            )  # Threshold for acceptable convergence

            # Generate recommendations if convergence is poor
            if not validation.is_convergent:
                validation.recommended_adjustments = (
                    await self._generate_convergence_recommendations(
                        validation, storylines
                    )
                )

            logger.debug(
                f"Convergence validation completed: score={validation.convergence_score:.2f}, convergent={validation.is_convergent}"
            )
            return validation

        except Exception as e:
            logger.error(f"Error validating storyline convergence: {e}")
            return ConvergenceValidation(
                session_id=session_id,
                storyline_count=len(storylines),
                is_convergent=False,
                convergence_score=0.0,
                integration_issues=[f"Validation error: {str(e)}"],
                convergence_points=[],
                recommended_adjustments=[],
            )

    # Helper methods for conflict resolution

    async def _select_best_solution(
        self, solutions: list[CreativeSolution], conflict: Contradiction
    ) -> CreativeSolution | None:
        """Select the best solution from available options."""
        if not solutions:
            return None

        # Weight factors for solution selection
        effectiveness_weight = 0.4
        narrative_cost_weight = 0.3
        player_impact_weight = 0.3

        best_solution = None
        best_score = -1.0

        for solution in solutions:
            # Calculate composite score (higher is better)
            score = (
                effectiveness_weight * solution.effectiveness_score
                + narrative_cost_weight
                * (1.0 - solution.narrative_cost)  # Lower cost is better
                + player_impact_weight
                * (1.0 - abs(solution.player_impact))  # Minimal impact is better
            )

            if score > best_score:
                best_score = score
                best_solution = solution

        logger.debug(
            f"Selected solution {best_solution.solution_id} with score {best_score:.2f}"
        )
        return best_solution

    async def _implement_conflict_resolution(
        self, solution: CreativeSolution, conflict: Contradiction, session_id: str
    ) -> NarrativeResolution | None:
        """Implement a conflict resolution solution."""
        try:
            resolution_id = str(uuid.uuid4())

            # Apply the solution's implementation steps
            narrative_changes = []
            for step in solution.implementation_steps:
                change = await self._apply_implementation_step(step, session_id)
                if change:
                    narrative_changes.append(change)

            # Generate player explanation
            player_explanation = await self._generate_player_explanation(
                solution, conflict
            )

            # Create resolution record
            resolution = NarrativeResolution(
                resolution_id=resolution_id,
                conflict_id=conflict.contradiction_id,
                solution_used=solution,
                implementation_success=True,
                narrative_changes=narrative_changes,
                player_explanation=player_explanation,
                effectiveness_rating=solution.effectiveness_score,
            )

            logger.debug(f"Successfully implemented resolution {resolution_id}")
            return resolution

        except Exception as e:
            logger.error(f"Error implementing conflict resolution: {e}")
            return None

    async def _generate_character_driven_solutions(
        self, conflict: Contradiction, content_history: list[NarrativeContent]
    ) -> list[CreativeSolution]:
        """Generate character-driven solutions for conflicts."""
        solutions = []

        # Solution: Character misunderstanding or miscommunication
        solutions.append(
            CreativeSolution(
                solution_id=str(uuid.uuid4()),
                solution_type="character_driven",
                description="Resolve contradiction through character misunderstanding or selective memory",
                implementation_steps=[
                    "Identify character involved in contradiction",
                    "Create plausible reason for character's different perspective",
                    "Add dialogue or internal monologue explaining the discrepancy",
                    "Maintain character consistency while resolving conflict",
                ],
                in_world_explanation="Characters may have different perspectives, incomplete information, or selective memory about events",
            )
        )

        # Solution: Character growth or change
        solutions.append(
            CreativeSolution(
                solution_id=str(uuid.uuid4()),
                solution_type="character_driven",
                description="Resolve contradiction through character development and change",
                implementation_steps=[
                    "Identify how character has grown or changed",
                    "Show progression from old behavior to new behavior",
                    "Add narrative elements showing the transformation",
                    "Connect change to therapeutic themes if appropriate",
                ],
                in_world_explanation="Characters evolve and change over time, leading to different behaviors and perspectives",
            )
        )

        return solutions

    async def _generate_perspective_based_solutions(
        self, conflict: Contradiction, content_history: list[NarrativeContent]
    ) -> list[CreativeSolution]:
        """Generate perspective-based solutions for conflicts."""
        solutions = []

        # Solution: Multiple valid perspectives
        solutions.append(
            CreativeSolution(
                solution_id=str(uuid.uuid4()),
                solution_type="perspective_based",
                description="Resolve contradiction by showing multiple valid perspectives on the same event",
                implementation_steps=[
                    "Identify different viewpoints on the conflicting information",
                    "Show how each perspective is valid from that character's experience",
                    "Add narrative elements that bridge the perspectives",
                    "Maintain respect for all viewpoints while resolving the conflict",
                ],
                in_world_explanation="Different characters may experience and remember the same events differently based on their unique perspectives",
            )
        )

        return solutions

    async def _generate_temporal_solutions(
        self, conflict: Contradiction, content_history: list[NarrativeContent]
    ) -> list[CreativeSolution]:
        """Generate temporal solutions for time-based conflicts."""
        solutions = []

        # Solution: Time passage and change
        solutions.append(
            CreativeSolution(
                solution_id=str(uuid.uuid4()),
                solution_type="temporal",
                description="Resolve contradiction through passage of time and natural change",
                implementation_steps=[
                    "Identify time gap between conflicting events",
                    "Show natural progression and change over time",
                    "Add temporal markers to clarify sequence",
                    "Explain how circumstances changed between events",
                ],
                in_world_explanation="Time brings change, and what was true at one point may no longer be true later",
            )
        )

        return solutions

    async def _generate_memory_based_solutions(
        self, conflict: Contradiction, content_history: list[NarrativeContent]
    ) -> list[CreativeSolution]:
        """Generate memory-based solutions for conflicts."""
        solutions = []

        # Solution: Imperfect memory
        solutions.append(
            CreativeSolution(
                solution_id=str(uuid.uuid4()),
                solution_type="memory_based",
                description="Resolve contradiction through imperfect or selective memory",
                implementation_steps=[
                    "Identify which memories might be imperfect",
                    "Show character realizing their memory was incomplete",
                    "Add new information that clarifies the situation",
                    "Maintain therapeutic appropriateness of memory themes",
                ],
                in_world_explanation="Memory is imperfect, and people may remember events differently or incompletely",
            )
        )

        return solutions

    async def _generate_causal_bridge_solutions(
        self, conflict: Contradiction, content_history: list[NarrativeContent]
    ) -> list[CreativeSolution]:
        """Generate causal bridge solutions for logical conflicts."""
        solutions = []

        # Solution: Hidden causal factor
        solutions.append(
            CreativeSolution(
                solution_id=str(uuid.uuid4()),
                solution_type="causal_bridge",
                description="Resolve contradiction by revealing hidden causal factors",
                implementation_steps=[
                    "Identify missing link in causal chain",
                    "Introduce previously unknown factor that explains the contradiction",
                    "Show how this factor connects the conflicting elements",
                    "Maintain logical consistency with established narrative",
                ],
                in_world_explanation="Sometimes important factors are not immediately apparent, but become clear with more information",
            )
        )

        return solutions

    async def _generate_hidden_factor_solutions(
        self, conflict: Contradiction, content_history: list[NarrativeContent]
    ) -> list[CreativeSolution]:
        """Generate hidden factor solutions for conflicts."""
        solutions = []

        # Solution: Previously unknown information
        solutions.append(
            CreativeSolution(
                solution_id=str(uuid.uuid4()),
                solution_type="hidden_factor",
                description="Resolve contradiction by revealing previously unknown information",
                implementation_steps=[
                    "Identify what information was missing",
                    "Introduce the new information naturally",
                    "Show how this information resolves the contradiction",
                    "Ensure the revelation feels earned and logical",
                ],
                in_world_explanation="New information can change our understanding of past events",
            )
        )

        return solutions

    async def _generate_recontextualization_solutions(
        self, conflict: Contradiction, content_history: list[NarrativeContent]
    ) -> list[CreativeSolution]:
        """Generate recontextualization solutions for implicit conflicts."""
        solutions = []

        # Solution: Different context
        solutions.append(
            CreativeSolution(
                solution_id=str(uuid.uuid4()),
                solution_type="recontextualization",
                description="Resolve contradiction by providing different context for events",
                implementation_steps=[
                    "Identify how context affects interpretation",
                    "Provide additional context that changes meaning",
                    "Show how the new context resolves the contradiction",
                    "Maintain consistency with overall narrative",
                ],
                in_world_explanation="Context shapes meaning, and additional context can change our understanding of events",
            )
        )

        return solutions

    async def _generate_subtext_solutions(
        self, conflict: Contradiction, content_history: list[NarrativeContent]
    ) -> list[CreativeSolution]:
        """Generate subtext-based solutions for conflicts."""
        solutions = []

        # Solution: Subtext and hidden meaning
        solutions.append(
            CreativeSolution(
                solution_id=str(uuid.uuid4()),
                solution_type="subtext",
                description="Resolve contradiction through subtext and hidden meanings",
                implementation_steps=[
                    "Identify potential subtext in conflicting elements",
                    "Reveal the hidden meaning behind surface contradictions",
                    "Show how subtext resolves the apparent conflict",
                    "Maintain narrative depth and complexity",
                ],
                in_world_explanation="Sometimes what appears contradictory on the surface has deeper meaning that resolves the conflict",
            )
        )

        return solutions

    async def _generate_universal_solutions(
        self, conflict: Contradiction, content_history: list[NarrativeContent]
    ) -> list[CreativeSolution]:
        """Generate universal solutions that work for any conflict type."""
        solutions = []

        # Solution: Gradual revelation
        solutions.append(
            CreativeSolution(
                solution_id=str(uuid.uuid4()),
                solution_type="universal",
                description="Resolve contradiction through gradual revelation of the full truth",
                implementation_steps=[
                    "Plan gradual revelation of information",
                    "Show how partial information led to apparent contradiction",
                    "Reveal complete picture that resolves the conflict",
                    "Maintain narrative tension and interest",
                ],
                in_world_explanation="The full truth is often revealed gradually, and partial information can create apparent contradictions",
            )
        )

        return solutions

    async def _calculate_solution_effectiveness(
        self, solution: CreativeSolution, conflict: Contradiction
    ) -> float:
        """Calculate the effectiveness score for a solution."""
        base_effectiveness = 0.5

        # Adjust based on solution type and conflict type compatibility
        compatibility_bonus = 0.0
        if conflict.type == "direct" and solution.solution_type in [
            "character_driven",
            "perspective_based",
        ]:
            compatibility_bonus = 0.3
        elif conflict.type == "temporal" and solution.solution_type in [
            "temporal",
            "memory_based",
        ]:
            compatibility_bonus = 0.3
        elif conflict.type == "causal" and solution.solution_type in [
            "causal_bridge",
            "hidden_factor",
        ]:
            compatibility_bonus = 0.3
        elif conflict.type == "implicit" and solution.solution_type in [
            "recontextualization",
            "subtext",
        ]:
            compatibility_bonus = 0.3

        # Universal solutions work for everything but with lower effectiveness
        if solution.solution_type == "universal":
            compatibility_bonus = 0.1

        effectiveness = min(1.0, base_effectiveness + compatibility_bonus)
        return effectiveness

    async def _calculate_narrative_cost(
        self, solution: CreativeSolution, content_history: list[NarrativeContent]
    ) -> float:
        """Calculate the narrative cost of implementing a solution."""
        base_cost = 0.2

        # Higher cost for solutions that require major changes
        if len(solution.required_changes) > 3:
            base_cost += 0.3

        # Lower cost for character-driven solutions (more natural)
        if solution.solution_type == "character_driven":
            base_cost -= 0.1

        # Higher cost for solutions that affect many content pieces
        affected_content_ratio = len(solution.required_changes) / max(
            1, len(content_history)
        )
        base_cost += affected_content_ratio * 0.2

        return min(1.0, max(0.0, base_cost))

    async def _calculate_player_impact(
        self, solution: CreativeSolution, session_id: str
    ) -> float:
        """Calculate the impact on player experience."""
        # For now, return a moderate impact
        # In a full implementation, this would consider player preferences,
        # current emotional state, therapeutic goals, etc.
        return 0.3

    async def _apply_implementation_step(
        self, step: str, session_id: str
    ) -> str | None:
        """Apply an implementation step and return the change made."""
        # Placeholder implementation - in practice, this would interact with
        # the narrative generation system to make actual changes
        logger.debug(f"Applying implementation step: {step}")
        return f"Applied: {step}"

    async def _generate_player_explanation(
        self, solution: CreativeSolution, conflict: Contradiction
    ) -> str:
        """Generate an explanation for the player about how the conflict was resolved."""
        return f"The apparent contradiction has been resolved: {solution.in_world_explanation}"

    # Helper methods for retroactive change management

    async def _validate_retroactive_changes(
        self, changes: list[RetroactiveChange], session_id: str
    ) -> ValidationResult:
        """Validate that retroactive changes don't create new conflicts."""
        try:
            logger.debug(
                f"Validating {len(changes)} retroactive changes for session {session_id}"
            )

            # Initialize validation result
            result = ValidationResult(
                is_valid=True,
                consistency_score=1.0,
                validation_timestamp=datetime.now(),
            )

            # Get current content history
            content_history = self.content_history.get(session_id, [])

            # Simulate applying changes and check for new conflicts
            simulated_history = await self._simulate_retroactive_changes(
                content_history, changes
            )

            # Validate the simulated history for new contradictions
            new_contradictions = await self.detect_contradictions(simulated_history)

            if new_contradictions:
                # Check if these are genuinely new contradictions
                original_contradictions = await self.detect_contradictions(
                    content_history
                )
                original_ids = {c.contradiction_id for c in original_contradictions}

                genuinely_new = [
                    c
                    for c in new_contradictions
                    if c.contradiction_id not in original_ids
                ]

                if genuinely_new:
                    result.is_valid = False
                    result.consistency_score = max(
                        0.0, 1.0 - (len(genuinely_new) * 0.2)
                    )

                    for contradiction in genuinely_new:
                        result.detected_issues.append(
                            ConsistencyIssue(
                                issue_id=str(uuid.uuid4()),
                                issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
                                severity=ValidationSeverity.ERROR,
                                description=f"Retroactive change would create new contradiction: {contradiction.description}",
                                affected_elements=contradiction.conflicting_elements,
                                confidence_score=contradiction.confidence_score,
                            )
                        )

            # Check for causal consistency after changes
            causal_issues = await self._validate_causal_consistency_after_changes(
                simulated_history, changes
            )
            result.detected_issues.extend(causal_issues)

            # Check for character consistency after changes
            character_issues = await self._validate_character_consistency_after_changes(
                simulated_history, changes
            )
            result.detected_issues.extend(character_issues)

            # Update overall score based on all issues
            if result.detected_issues:
                issue_penalty = len(result.detected_issues) * 0.1
                result.consistency_score = max(
                    0.0, result.consistency_score - issue_penalty
                )
                result.is_valid = result.consistency_score >= 0.7

            logger.debug(
                f"Retroactive change validation completed: valid={result.is_valid}, score={result.consistency_score:.2f}"
            )
            return result

        except Exception as e:
            logger.error(f"Error validating retroactive changes: {e}")
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

    async def _generate_in_world_explanation(
        self, change: RetroactiveChange, session_id: str
    ) -> str | None:
        """Generate an in-world explanation for a retroactive change."""
        if change.in_world_explanation:
            return change.in_world_explanation

        # Generate explanation based on change type
        if change.change_type == "modification":
            return f"Upon reflection, the situation was actually: {change.modified_content}"
        elif change.change_type == "addition":
            return f"Additional details have come to light: {change.modified_content}"
        elif change.change_type == "recontextualization":
            return f"The context of the situation was: {change.modified_content}"

        return f"The situation has been clarified: {change.modified_content}"

    async def _apply_retroactive_change(
        self, change: RetroactiveChange, explanation: str, session_id: str
    ) -> bool:
        """Apply a retroactive change with its explanation."""
        try:
            logger.debug(
                f"Applying retroactive change {change.change_id}: {explanation}"
            )

            # Get current content history
            content_history = self.content_history.get(session_id, [])

            # Find the target content to modify
            target_content = None
            target_index = -1
            for i, content in enumerate(content_history):
                if content.content_id == change.target_content_id:
                    target_content = content
                    target_index = i
                    break

            if not target_content:
                logger.error(
                    f"Target content {change.target_content_id} not found for retroactive change"
                )
                return False

            # Create modified content based on change type
            if change.change_type == "modification":
                # Replace the content text
                modified_content = NarrativeContent(
                    content_id=target_content.content_id,
                    content_type=target_content.content_type,
                    text=change.modified_content,
                    characters=target_content.characters,
                    locations=target_content.locations,
                    themes=target_content.themes,
                    causal_dependencies=target_content.causal_dependencies,
                    therapeutic_concepts=target_content.therapeutic_concepts,
                    metadata={
                        **target_content.metadata,
                        "retroactive_change": {
                            "change_id": change.change_id,
                            "original_content": change.original_content,
                            "explanation": explanation,
                            "timestamp": datetime.now().isoformat(),
                        },
                    },
                )

            elif change.change_type == "addition":
                # Add to existing content
                modified_content = NarrativeContent(
                    content_id=target_content.content_id,
                    content_type=target_content.content_type,
                    text=f"{target_content.text}\n\n{change.modified_content}",
                    characters=target_content.characters,
                    locations=target_content.locations,
                    themes=target_content.themes,
                    causal_dependencies=target_content.causal_dependencies,
                    therapeutic_concepts=target_content.therapeutic_concepts,
                    metadata={
                        **target_content.metadata,
                        "retroactive_addition": {
                            "change_id": change.change_id,
                            "added_content": change.modified_content,
                            "explanation": explanation,
                            "timestamp": datetime.now().isoformat(),
                        },
                    },
                )

            elif change.change_type == "recontextualization":
                # Recontextualize existing content
                modified_content = NarrativeContent(
                    content_id=target_content.content_id,
                    content_type=target_content.content_type,
                    text=target_content.text,
                    characters=target_content.characters,
                    locations=target_content.locations,
                    themes=target_content.themes,
                    causal_dependencies=target_content.causal_dependencies,
                    therapeutic_concepts=target_content.therapeutic_concepts,
                    metadata={
                        **target_content.metadata,
                        "recontextualization": {
                            "change_id": change.change_id,
                            "new_context": change.modified_content,
                            "explanation": explanation,
                            "timestamp": datetime.now().isoformat(),
                        },
                    },
                )
            else:
                logger.error(f"Unknown change type: {change.change_type}")
                return False

            # Update the content history
            content_history[target_index] = modified_content
            self.content_history[session_id] = content_history

            # Log the change for audit purposes
            logger.info(
                f"Successfully applied retroactive change {change.change_id} to content {change.target_content_id}"
            )

            # Store the change record for future reference
            if not hasattr(self, "applied_changes"):
                self.applied_changes = {}
            if session_id not in self.applied_changes:
                self.applied_changes[session_id] = []

            self.applied_changes[session_id].append(
                {
                    "change": change,
                    "explanation": explanation,
                    "applied_at": datetime.now(),
                    "success": True,
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error applying retroactive change {change.change_id}: {e}")
            return False

    async def _update_content_history_with_changes(
        self, changes: list[RetroactiveChange], session_id: str
    ) -> None:
        """Update content history to reflect retroactive changes."""
        try:
            logger.debug(
                f"Updating content history with {len(changes)} retroactive changes"
            )

            # Get current content history
            content_history = self.content_history.get(session_id, [])

            # Create a mapping of content IDs to their positions
            content_map = {
                content.content_id: i for i, content in enumerate(content_history)
            }

            # Apply each change to the content history
            for change in changes:
                if change.target_content_id in content_map:
                    index = content_map[change.target_content_id]
                    original_content = content_history[index]

                    # Update the content's metadata to reflect the change
                    updated_metadata = {
                        **original_content.metadata,
                        "retroactive_changes": original_content.metadata.get(
                            "retroactive_changes", []
                        )
                        + [
                            {
                                "change_id": change.change_id,
                                "change_type": change.change_type,
                                "justification": change.justification,
                                "in_world_explanation": change.in_world_explanation,
                                "timestamp": change.timestamp.isoformat(),
                                "impact_scope": change.impact_scope,
                            }
                        ],
                    }

                    # Create updated content with change metadata
                    updated_content = NarrativeContent(
                        content_id=original_content.content_id,
                        content_type=original_content.content_type,
                        text=original_content.text,
                        characters=original_content.characters,
                        locations=original_content.locations,
                        themes=original_content.themes,
                        causal_dependencies=original_content.causal_dependencies,
                        therapeutic_concepts=original_content.therapeutic_concepts,
                        metadata=updated_metadata,
                        timestamp=original_content.timestamp,
                    )

                    content_history[index] = updated_content
                    logger.debug(
                        f"Updated content {change.target_content_id} with retroactive change metadata"
                    )
                else:
                    logger.warning(
                        f"Target content {change.target_content_id} not found in history"
                    )

            # Update the stored content history
            self.content_history[session_id] = content_history

            # Update any dependent systems that need to know about the changes
            await self._notify_dependent_systems_of_changes(changes, session_id)

            logger.info(
                f"Successfully updated content history with {len(changes)} retroactive changes"
            )

        except Exception as e:
            logger.error(f"Error updating content history with changes: {e}")
            raise

    # Helper methods for storyline convergence validation

    async def _detect_convergence_conflicts(
        self, storylines: list[StorylineThread]
    ) -> list[str]:
        """Detect conflicts in storyline convergence."""
        conflicts = []

        # Check for character conflicts across storylines
        character_conflicts = await self._detect_character_conflicts_across_storylines(
            storylines
        )
        conflicts.extend(character_conflicts)

        # Check for thematic conflicts
        thematic_conflicts = await self._detect_thematic_conflicts_across_storylines(
            storylines
        )
        conflicts.extend(thematic_conflicts)

        # Check for pacing conflicts
        pacing_conflicts = await self._detect_pacing_conflicts_across_storylines(
            storylines
        )
        conflicts.extend(pacing_conflicts)

        return conflicts

    async def _identify_convergence_points(
        self, storylines: list[StorylineThread]
    ) -> list[str]:
        """Identify natural convergence points for storylines."""
        convergence_points = []

        # Look for shared characters
        all_participants = set()
        for storyline in storylines:
            all_participants.update(storyline.participants)

        shared_participants = []
        for participant in all_participants:
            storylines_with_participant = [
                s for s in storylines if participant in s.participants
            ]
            if len(storylines_with_participant) > 1:
                shared_participants.append(participant)

        for participant in shared_participants:
            convergence_points.append(f"Character convergence point: {participant}")

        # Look for shared themes
        all_themes = set()
        for storyline in storylines:
            all_themes.update(storyline.themes)

        shared_themes = []
        for theme in all_themes:
            storylines_with_theme = [s for s in storylines if theme in s.themes]
            if len(storylines_with_theme) > 1:
                shared_themes.append(theme)

        for theme in shared_themes:
            convergence_points.append(f"Thematic convergence point: {theme}")

        return convergence_points

    async def _validate_cross_storyline_character_consistency(
        self, storylines: list[StorylineThread]
    ) -> list[str]:
        """Validate character consistency across storylines."""
        issues = []

        try:
            # Find characters that appear in multiple storylines
            character_storylines = {}
            for storyline in storylines:
                for participant in storyline.participants:
                    if participant not in character_storylines:
                        character_storylines[participant] = []
                    character_storylines[participant].append(storyline)

            # Check consistency for characters in multiple storylines
            for character, char_storylines in character_storylines.items():
                if len(char_storylines) > 1:
                    consistency_issues = (
                        await self._check_character_consistency_across_storylines(
                            character, char_storylines
                        )
                    )
                    issues.extend(consistency_issues)

            return issues

        except Exception as e:
            logger.error(f"Error validating cross-storyline character consistency: {e}")
            return []

    async def _validate_thematic_coherence_across_storylines(
        self, storylines: list[StorylineThread]
    ) -> list[str]:
        """Validate thematic coherence across storylines."""
        issues = []

        try:
            # Collect all themes across storylines
            all_themes = set()
            theme_storylines = {}

            for storyline in storylines:
                for theme in storyline.themes:
                    all_themes.add(theme)
                    if theme not in theme_storylines:
                        theme_storylines[theme] = []
                    theme_storylines[theme].append(storyline)

            # Check for conflicting themes
            conflicting_themes = await self._identify_conflicting_themes(
                list(all_themes)
            )

            for theme1, theme2 in conflicting_themes:
                # Check if conflicting themes appear in overlapping storylines
                storylines1 = set(s.thread_id for s in theme_storylines.get(theme1, []))
                storylines2 = set(s.thread_id for s in theme_storylines.get(theme2, []))

                if storylines1.intersection(storylines2):
                    issues.append(
                        f"Conflicting themes '{theme1}' and '{theme2}' appear in overlapping storylines"
                    )

            # Check for thematic consistency within shared themes
            for theme, theme_storylines_list in theme_storylines.items():
                if len(theme_storylines_list) > 1:
                    consistency_issues = (
                        await self._check_thematic_consistency_across_storylines(
                            theme, theme_storylines_list
                        )
                    )
                    issues.extend(consistency_issues)

            return issues

        except Exception as e:
            logger.error(f"Error validating thematic coherence across storylines: {e}")
            return []

    async def _validate_convergence_pacing(
        self, storylines: list[StorylineThread]
    ) -> list[str]:
        """Validate pacing balance in storyline convergence."""
        # Placeholder implementation
        return []

    async def _calculate_convergence_score(
        self, validation: ConvergenceValidation
    ) -> float:
        """Calculate overall convergence score."""
        base_score = 1.0

        # Reduce score based on number of issues
        issue_penalty = len(validation.integration_issues) * 0.1
        base_score -= issue_penalty

        # Increase score based on convergence points
        convergence_bonus = len(validation.convergence_points) * 0.05
        base_score += convergence_bonus

        return max(0.0, min(1.0, base_score))

    async def _generate_convergence_recommendations(
        self, validation: ConvergenceValidation, storylines: list[StorylineThread]
    ) -> list[str]:
        """Generate recommendations for improving storyline convergence."""
        recommendations = []

        if len(validation.convergence_points) == 0:
            recommendations.append(
                "Consider adding shared characters or themes to create natural convergence points"
            )

        if len(validation.integration_issues) > 3:
            recommendations.append(
                "Reduce the number of conflicting elements between storylines"
            )

        if validation.convergence_score < 0.5:
            recommendations.append(
                "Consider simplifying the convergence by focusing on fewer storylines"
            )

        return recommendations

    # Placeholder helper methods for detailed conflict detection

    async def _detect_character_conflicts_across_storylines(
        self, storylines: list[StorylineThread]
    ) -> list[str]:
        """Detect character conflicts across storylines."""
        return []

    async def _detect_thematic_conflicts_across_storylines(
        self, storylines: list[StorylineThread]
    ) -> list[str]:
        """Detect thematic conflicts across storylines."""
        return []

    async def _detect_pacing_conflicts_across_storylines(
        self, storylines: list[StorylineThread]
    ) -> list[str]:
        """Detect pacing conflicts across storylines."""
        return []

    # Helper methods for retroactive change validation

    async def _simulate_retroactive_changes(
        self, content_history: list[NarrativeContent], changes: list[RetroactiveChange]
    ) -> list[NarrativeContent]:
        """Simulate applying retroactive changes to content history."""
        try:
            # Create a copy of the content history
            simulated_history = [
                NarrativeContent(
                    content_id=content.content_id,
                    content_type=content.content_type,
                    text=content.text,
                    characters=content.characters.copy(),
                    locations=content.locations.copy(),
                    themes=content.themes.copy(),
                    causal_dependencies=content.causal_dependencies.copy(),
                    therapeutic_concepts=content.therapeutic_concepts.copy(),
                    metadata=content.metadata.copy(),
                    timestamp=content.timestamp,
                )
                for content in content_history
            ]

            # Apply each change to the simulated history
            for change in changes:
                # Find the target content
                for i, content in enumerate(simulated_history):
                    if content.content_id == change.target_content_id:
                        if change.change_type == "modification":
                            simulated_history[i].text = change.modified_content
                        elif change.change_type == "addition":
                            simulated_history[
                                i
                            ].text += f"\n\n{change.modified_content}"
                        elif change.change_type == "recontextualization":
                            # Add context metadata
                            simulated_history[i].metadata[
                                "recontextualization"
                            ] = change.modified_content
                        break

            return simulated_history

        except Exception as e:
            logger.error(f"Error simulating retroactive changes: {e}")
            return content_history

    async def _validate_causal_consistency_after_changes(
        self,
        simulated_history: list[NarrativeContent],
        changes: list[RetroactiveChange],
    ) -> list[ConsistencyIssue]:
        """Validate causal consistency after applying retroactive changes."""
        issues = []

        try:
            # Check if changes break causal chains
            for change in changes:
                # Find content that depends on the changed content
                dependent_content = [
                    content
                    for content in simulated_history
                    if change.target_content_id in content.causal_dependencies
                ]

                for dependent in dependent_content:
                    # Check if the change makes the dependency invalid
                    if await self._change_breaks_causal_dependency(change, dependent):
                        issues.append(
                            ConsistencyIssue(
                                issue_id=str(uuid.uuid4()),
                                issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
                                severity=ValidationSeverity.WARNING,
                                description=f"Retroactive change {change.change_id} may break causal dependency in content {dependent.content_id}",
                                affected_elements=[
                                    change.target_content_id,
                                    dependent.content_id,
                                ],
                                confidence_score=0.7,
                            )
                        )

            return issues

        except Exception as e:
            logger.error(f"Error validating causal consistency after changes: {e}")
            return []

    async def _validate_character_consistency_after_changes(
        self,
        simulated_history: list[NarrativeContent],
        changes: list[RetroactiveChange],
    ) -> list[ConsistencyIssue]:
        """Validate character consistency after applying retroactive changes."""
        issues = []

        try:
            # Check if changes affect character consistency
            for change in changes:
                # Find the changed content
                changed_content = None
                for content in simulated_history:
                    if content.content_id == change.target_content_id:
                        changed_content = content
                        break

                if changed_content:
                    # Check character consistency for the changed content
                    for character in changed_content.characters:
                        character_profile = self.character_profiles.get(character)
                        if character_profile:
                            consistency_issues = (
                                await self._check_character_consistency_with_change(
                                    changed_content,
                                    character,
                                    character_profile,
                                    change,
                                )
                            )
                            issues.extend(consistency_issues)

            return issues

        except Exception as e:
            logger.error(f"Error validating character consistency after changes: {e}")
            return []

    async def _change_breaks_causal_dependency(
        self, change: RetroactiveChange, dependent_content: NarrativeContent
    ) -> bool:
        """Check if a retroactive change breaks a causal dependency."""
        try:
            # Simple heuristic: if the change significantly alters the meaning,
            # it might break dependencies
            if change.change_type == "modification":
                # Check if the modification changes key causal elements
                original_words = set(change.original_content.lower().split())
                modified_words = set(change.modified_content.lower().split())

                # Calculate word overlap
                overlap = len(original_words.intersection(modified_words))
                total_words = len(original_words.union(modified_words))

                if total_words > 0:
                    similarity = overlap / total_words
                    # If similarity is low, the change might break dependencies
                    return similarity < 0.5

            return False

        except Exception as e:
            logger.error(f"Error checking if change breaks causal dependency: {e}")
            return False

    async def _check_character_consistency_with_change(
        self,
        content: NarrativeContent,
        character: str,
        profile: dict[str, Any],
        change: RetroactiveChange,
    ) -> list[ConsistencyIssue]:
        """Check character consistency after a retroactive change."""
        issues = []

        try:
            # Check if the change affects character behavior or dialogue
            if character in content.text.lower():
                # Use existing character consistency validation
                character_issues = await self._check_personality_consistency(
                    content, character, profile
                )

                # Mark these as related to the retroactive change
                for issue in character_issues:
                    issue.metadata["retroactive_change_id"] = change.change_id
                    issue.description += (
                        f" (after retroactive change {change.change_id})"
                    )

                issues.extend(character_issues)

            return issues

        except Exception as e:
            logger.error(f"Error checking character consistency with change: {e}")
            return []

    async def _notify_dependent_systems_of_changes(
        self, changes: list[RetroactiveChange], session_id: str
    ) -> None:
        """Notify dependent systems about retroactive changes."""
        try:
            # This would notify other components that depend on narrative content
            # For now, just log the notification
            logger.debug(
                f"Notifying dependent systems of {len(changes)} retroactive changes for session {session_id}"
            )

            # In a full implementation, this might:
            # - Update character arc managers
            # - Notify pacing controllers
            # - Update choice impact trackers
            # - Refresh emergent narrative generators

        except Exception as e:
            logger.error(f"Error notifying dependent systems of changes: {e}")


# Facade re-exports: prefer extracted implementations
try:
    from .narrative_coherence.causal_validator import (
        CausalValidator as _ExtractedCausalValidator,
    )
    from .narrative_coherence.coherence_validator import (
        CoherenceValidator as _ExtractedCoherenceValidator,
    )
    from .narrative_coherence.contradiction_detector import (
        ContradictionDetector as _ExtractedContradictionDetector,
    )

    CoherenceValidator = _ExtractedCoherenceValidator  # type: ignore
    ContradictionDetector = _ExtractedContradictionDetector  # type: ignore
    CausalValidator = _ExtractedCausalValidator  # type: ignore
except Exception:  # pragma: no cover
    # If extracted modules are unavailable, fall back to in-file definitions
    pass
