"""
Safety Validation Components

This module provides the core validation components for therapeutic content safety,
including content safety validation, crisis detection, and bias detection.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .enums import (
    AgeGroup,
    BiasType,
    CrisisLevel,
    ProtectiveFactor,
    RiskCategory,
    SafetyLevel,
    TherapeuticFramework,
    TherapeuticGoalCategory,
)
from .models import (
    ContentPayload,
    ValidationContext,
)

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Rule for content validation."""

    rule_id: str
    name: str
    pattern: str
    risk_category: RiskCategory
    severity: float  # 0.0 to 1.0
    age_groups: list[AgeGroup] = field(default_factory=list)
    therapeutic_contexts: list[TherapeuticGoalCategory] = field(default_factory=list)


class ContentSafetyValidator:
    """Validates content for therapeutic appropriateness and safety."""

    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.prohibited_patterns = self._load_prohibited_patterns()
        self.therapeutic_keywords = self._load_therapeutic_keywords()
        self.age_appropriate_content = self._load_age_guidelines()

        # Metrics
        self.metrics = {
            "validations_performed": 0,
            "safety_violations_detected": 0,
            "age_inappropriate_content": 0,
            "therapeutic_misalignments": 0,
        }

    def _load_validation_rules(self) -> list[ValidationRule]:
        """Load content validation rules."""
        return [
            # Self-harm related content
            ValidationRule(
                "self_harm_explicit",
                "Explicit self-harm content",
                r"\b(cut|cutting|harm|hurt)\s+(myself|yourself|themselves)\b",
                RiskCategory.SELF_HARM,
                0.9,
                [AgeGroup.TEEN, AgeGroup.YOUNG_ADULT, AgeGroup.ADULT],
            ),
            # Suicide related content
            ValidationRule(
                "suicide_explicit",
                "Explicit suicide content",
                r"\b(kill|end|take)\s+(myself|yourself|my\s+life|your\s+life)\b",
                RiskCategory.SUICIDE,
                1.0,
            ),
            ValidationRule(
                "suicide_ideation",
                "Suicide ideation indicators",
                r"\b(want\s+to\s+die|wish\s+I\s+was\s+dead|better\s+off\s+dead)\b",
                RiskCategory.SUICIDE,
                0.8,
            ),
            # Violence related content
            ValidationRule(
                "violence_explicit",
                "Explicit violence content",
                r"\b(hit|punch|attack|fight|violence|violent)\b",
                RiskCategory.VIOLENCE,
                0.7,
                [AgeGroup.TEEN, AgeGroup.YOUNG_ADULT, AgeGroup.ADULT],
            ),
            # Substance abuse
            ValidationRule(
                "substance_abuse",
                "Substance abuse content",
                r"\b(drugs|alcohol|drinking|high|drunk|addiction)\b",
                RiskCategory.SUBSTANCE_ABUSE,
                0.6,
                [AgeGroup.TEEN, AgeGroup.YOUNG_ADULT, AgeGroup.ADULT],
            ),
            # Eating disorder triggers
            ValidationRule(
                "eating_disorder",
                "Eating disorder triggers",
                r"\b(fat|skinny|weight|diet|calories|purge|binge)\b",
                RiskCategory.EATING_DISORDER,
                0.5,
                [AgeGroup.TEEN, AgeGroup.YOUNG_ADULT, AgeGroup.ADULT],
            ),
        ]

    def _load_prohibited_patterns(self) -> dict[RiskCategory, list[str]]:
        """Load prohibited content patterns."""
        return {
            RiskCategory.SELF_HARM: [
                r"\bself[\s-]?harm\b",
                r"\bcut(ting)?\s+(myself|yourself)\b",
                r"\bhurt\s+(myself|yourself)\b",
            ],
            RiskCategory.SUICIDE: [
                r"\bsuicide\b",
                r"\bkill\s+(myself|yourself)\b",
                r"\bend\s+it\s+all\b",
            ],
            RiskCategory.VIOLENCE: [
                r"\bviolent\s+thoughts\b",
                r"\bhurt\s+others\b",
                r"\battack\s+someone\b",
            ],
            RiskCategory.INAPPROPRIATE_CONTENT: [
                r"\bsexual\s+content\b",
                r"\binappropriate\s+touching\b",
                r"\badult\s+content\b",
            ],
        }

    def _load_therapeutic_keywords(self) -> dict[TherapeuticFramework, list[str]]:
        """Load therapeutic framework keywords."""
        return {
            TherapeuticFramework.CBT: [
                "thoughts",
                "feelings",
                "behaviors",
                "cognitive",
                "behavioral",
                "thinking patterns",
                "negative thoughts",
                "positive coping",
            ],
            TherapeuticFramework.DBT: [
                "mindfulness",
                "distress tolerance",
                "emotion regulation",
                "interpersonal effectiveness",
                "wise mind",
                "radical acceptance",
            ],
            TherapeuticFramework.MINDFULNESS: [
                "mindful",
                "present moment",
                "awareness",
                "meditation",
                "breathing",
                "grounding",
                "body scan",
                "mindful breathing",
            ],
            TherapeuticFramework.TRAUMA_INFORMED: [
                "safety",
                "trustworthiness",
                "choice",
                "collaboration",
                "empowerment",
                "trauma-informed",
                "healing",
                "recovery",
            ],
        }

    def _load_age_guidelines(self) -> dict[AgeGroup, dict[str, Any]]:
        """Load age-appropriate content guidelines."""
        return {
            AgeGroup.CHILD: {
                "max_complexity": 2,
                "prohibited_topics": ["violence", "death", "adult themes"],
                "required_elements": ["positive", "educational", "safe"],
            },
            AgeGroup.TEEN: {
                "max_complexity": 4,
                "prohibited_topics": ["explicit violence", "adult content"],
                "sensitive_topics": ["relationships", "identity", "peer pressure"],
            },
            AgeGroup.ADULT: {
                "max_complexity": 5,
                "sensitive_topics": ["trauma", "relationships", "career", "family"],
            },
        }

    async def validate(
        self, content: ContentPayload, context: ValidationContext
    ) -> dict[str, Any]:
        """Main validation method."""
        start_time = datetime.utcnow()

        result = {
            "component": "content_safety",
            "safety_level": SafetyLevel.SAFE,
            "violations": [],
            "recommendations": [],
            "age_appropriate": True,
            "therapeutic_alignment": 0.0,
            "confidence": 0.0,
        }

        try:
            # Check for safety violations
            violations = await self._check_safety_violations(content, context)
            result["violations"] = violations

            # Determine safety level
            result["safety_level"] = self._calculate_safety_level(violations)

            # Check age appropriateness
            result["age_appropriate"] = await self._check_age_appropriateness(
                content, context
            )

            # Check therapeutic alignment
            result["therapeutic_alignment"] = await self._check_therapeutic_alignment(
                content, context
            )

            # Generate recommendations
            result["recommendations"] = await self._generate_recommendations(
                content, violations
            )

            # Calculate confidence
            result["confidence"] = self._calculate_confidence(content, result)

            self.metrics["validations_performed"] += 1
            if violations:
                self.metrics["safety_violations_detected"] += 1
            if not result["age_appropriate"]:
                self.metrics["age_inappropriate_content"] += 1
            if result["therapeutic_alignment"] < 0.5:
                self.metrics["therapeutic_misalignments"] += 1

        except Exception as e:
            logger.error(f"Content safety validation failed: {e}")
            result["error"] = str(e)
            result["safety_level"] = SafetyLevel.CRITICAL

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result["processing_time_ms"] = processing_time

        return result

    async def _check_safety_violations(
        self, content: ContentPayload, context: ValidationContext
    ) -> list[dict[str, Any]]:
        """Check for safety violations in content."""
        violations = []
        text = content.content_text.lower()

        # Check validation rules
        for rule in self.validation_rules:
            if re.search(rule.pattern, text, re.IGNORECASE):
                # Check if rule applies to user's age group
                if (
                    context.user_age_group
                    and rule.age_groups
                    and context.user_age_group not in rule.age_groups
                ):
                    continue

                violation = {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "risk_category": rule.risk_category.value,
                    "severity": rule.severity,
                    "matched_pattern": rule.pattern,
                }
                violations.append(violation)

        # Check prohibited patterns
        for risk_category, patterns in self.prohibited_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    violation = {
                        "rule_id": f"prohibited_{risk_category.value}",
                        "rule_name": f"Prohibited {risk_category.value} content",
                        "risk_category": risk_category.value,
                        "severity": 0.8,
                        "matched_pattern": pattern,
                    }
                    violations.append(violation)

        return violations

    def _calculate_safety_level(self, violations: list[dict[str, Any]]) -> SafetyLevel:
        """Calculate overall safety level based on violations."""
        if not violations:
            return SafetyLevel.SAFE

        max_severity = max(violation["severity"] for violation in violations)

        if max_severity >= 0.9:
            return SafetyLevel.CRITICAL
        elif max_severity >= 0.7:
            return SafetyLevel.DANGER
        elif max_severity >= 0.5:
            return SafetyLevel.WARNING
        elif max_severity >= 0.3:
            return SafetyLevel.CAUTION
        else:
            return SafetyLevel.SAFE

    async def _check_age_appropriateness(
        self, content: ContentPayload, context: ValidationContext
    ) -> bool:
        """Check if content is age-appropriate."""
        if not context.user_age_group:
            return True  # Cannot determine without age group

        guidelines = self.age_appropriate_content.get(context.user_age_group, {})
        text = content.content_text.lower()

        # Check prohibited topics
        prohibited_topics = guidelines.get("prohibited_topics", [])
        for topic in prohibited_topics:
            if topic.lower() in text:
                return False

        # Check complexity level
        max_complexity = guidelines.get("max_complexity", 5)
        content_complexity = self._estimate_content_complexity(content)
        if content_complexity > max_complexity:
            return False

        return True

    def _estimate_content_complexity(self, content: ContentPayload) -> int:
        """Estimate content complexity level (1-5)."""
        text = content.content_text

        # Simple complexity estimation based on various factors
        word_count = len(text.split())
        sentence_count = len([s for s in text.split(".") if s.strip()])
        avg_word_length = sum(len(word) for word in text.split()) / max(word_count, 1)

        complexity = 1

        if word_count > 100:
            complexity += 1
        if word_count > 300:
            complexity += 1
        if avg_word_length > 6:
            complexity += 1
        if sentence_count > 0 and word_count / sentence_count > 15:
            complexity += 1

        return min(complexity, 5)

    async def _check_therapeutic_alignment(
        self, content: ContentPayload, context: ValidationContext
    ) -> float:
        """Check therapeutic alignment of content."""
        if not context.user_therapeutic_goals:
            return 0.5  # Neutral alignment

        text = content.content_text.lower()
        alignment_score = 0.0
        total_frameworks = 0

        # Check alignment with therapeutic frameworks
        for framework, keywords in self.therapeutic_keywords.items():
            framework_score = 0.0
            for keyword in keywords:
                if keyword.lower() in text:
                    framework_score += 1

            if framework_score > 0:
                framework_alignment = min(framework_score / len(keywords), 1.0)
                alignment_score += framework_alignment
                total_frameworks += 1

        # Check alignment with user's therapeutic goals
        goal_alignment = 0.0
        for goal in context.user_therapeutic_goals:
            goal_keywords = self._get_goal_keywords(goal)
            goal_score = sum(1 for keyword in goal_keywords if keyword.lower() in text)
            if goal_score > 0:
                goal_alignment += min(goal_score / len(goal_keywords), 1.0)

        if context.user_therapeutic_goals:
            goal_alignment /= len(context.user_therapeutic_goals)

        # Combine framework and goal alignment
        if total_frameworks > 0:
            framework_alignment = alignment_score / total_frameworks
            return (framework_alignment + goal_alignment) / 2
        else:
            return goal_alignment

    def _get_goal_keywords(self, goal: TherapeuticGoalCategory) -> list[str]:
        """Get keywords associated with therapeutic goals."""
        goal_keywords = {
            TherapeuticGoalCategory.ANXIETY_MANAGEMENT: [
                "anxiety",
                "worry",
                "calm",
                "relaxation",
                "breathing",
                "mindfulness",
            ],
            TherapeuticGoalCategory.DEPRESSION_SUPPORT: [
                "depression",
                "mood",
                "positive",
                "hope",
                "energy",
                "motivation",
            ],
            TherapeuticGoalCategory.EMOTIONAL_REGULATION: [
                "emotions",
                "feelings",
                "regulation",
                "control",
                "balance",
                "stability",
            ],
            TherapeuticGoalCategory.STRESS_MANAGEMENT: [
                "stress",
                "pressure",
                "coping",
                "management",
                "relief",
                "tension",
            ],
            TherapeuticGoalCategory.SOCIAL_SKILLS: [
                "social",
                "communication",
                "relationships",
                "interaction",
                "connection",
            ],
        }
        return goal_keywords.get(goal, [])

    async def _generate_recommendations(
        self, content: ContentPayload, violations: list[dict[str, Any]]
    ) -> list[str]:
        """Generate recommendations for content improvement."""
        recommendations = []

        if not violations:
            recommendations.append("Content appears safe and appropriate")
            return recommendations

        # Group violations by risk category
        risk_categories = set(v["risk_category"] for v in violations)

        for risk_category in risk_categories:
            if risk_category == RiskCategory.SELF_HARM.value:
                recommendations.append(
                    "Consider adding positive coping strategies and support resources"
                )
            elif risk_category == RiskCategory.SUICIDE.value:
                recommendations.append(
                    "Include crisis resources and professional help information"
                )
            elif risk_category == RiskCategory.VIOLENCE.value:
                recommendations.append(
                    "Focus on conflict resolution and peaceful alternatives"
                )
            elif risk_category == RiskCategory.SUBSTANCE_ABUSE.value:
                recommendations.append(
                    "Include information about healthy coping mechanisms"
                )

        return recommendations

    def _calculate_confidence(
        self, content: ContentPayload, result: dict[str, Any]
    ) -> float:
        """Calculate confidence in validation result."""
        confidence = 0.5  # Base confidence

        # Increase confidence based on content length
        word_count = len(content.content_text.split())
        if word_count > 50:
            confidence += 0.2
        if word_count > 200:
            confidence += 0.1

        # Adjust based on violations found
        if result["violations"]:
            confidence += 0.2  # More confident when violations are detected

        # Adjust based on therapeutic alignment
        if result["therapeutic_alignment"] > 0.7:
            confidence += 0.1

        return min(confidence, 1.0)

    def get_metrics(self) -> dict[str, Any]:
        """Get validator metrics."""
        return self.metrics.copy()


class CrisisDetectionEngine:
    """Detects crisis indicators in therapeutic content."""

    def __init__(self):
        self.crisis_patterns = self._load_crisis_patterns()
        self.risk_indicators = self._load_risk_indicators()
        self.protective_indicators = self._load_protective_indicators()

        # Metrics
        self.metrics = {
            "assessments_performed": 0,
            "crises_detected": 0,
            "high_risk_content": 0,
            "interventions_triggered": 0,
        }

    def _load_crisis_patterns(self) -> dict[CrisisLevel, list[str]]:
        """Load crisis detection patterns."""
        return {
            CrisisLevel.CRITICAL: [
                r"\b(going to|will|plan to)\s+(kill|end|hurt)\s+(myself|my life)\b",
                r"\bhave\s+a\s+plan\s+to\s+(die|kill myself)\b",
                r"\btonight\s+is\s+the\s+night\b",
            ],
            CrisisLevel.SEVERE: [
                r"\bwant\s+to\s+(die|kill myself|end it all)\b",
                r"\bcan't\s+take\s+it\s+anymore\b",
                r"\bno\s+point\s+in\s+living\b",
            ],
            CrisisLevel.HIGH: [
                r"\bthinking\s+about\s+(death|dying|suicide)\b",
                r"\bwish\s+I\s+was\s+dead\b",
                r"\blife\s+isn't\s+worth\s+living\b",
            ],
            CrisisLevel.MODERATE: [
                r"\bfeel\s+hopeless\b",
                r"\bnothing\s+matters\b",
                r"\bcan't\s+go\s+on\b",
            ],
            CrisisLevel.LOW: [
                r"\bfeeling\s+down\b",
                r"\bhaving\s+a\s+hard\s+time\b",
                r"\bstruggling\s+with\b",
            ],
        }

    def _load_risk_indicators(self) -> dict[RiskCategory, list[str]]:
        """Load risk indicator patterns."""
        return {
            RiskCategory.SUICIDE: [
                "suicide",
                "kill myself",
                "end my life",
                "want to die",
            ],
            RiskCategory.SELF_HARM: [
                "cut myself",
                "hurt myself",
                "self-harm",
                "cutting",
            ],
            RiskCategory.VIOLENCE: ["hurt others", "violent thoughts", "want to hurt"],
            RiskCategory.SUBSTANCE_ABUSE: [
                "drinking too much",
                "using drugs",
                "can't stop drinking",
            ],
        }

    def _load_protective_indicators(self) -> dict[ProtectiveFactor, list[str]]:
        """Load protective factor patterns."""
        return {
            ProtectiveFactor.SOCIAL_SUPPORT: [
                "family support",
                "friends care",
                "people who love me",
            ],
            ProtectiveFactor.COPING_SKILLS: [
                "breathing exercises",
                "meditation",
                "coping strategies",
            ],
            ProtectiveFactor.PROFESSIONAL_HELP: [
                "therapist",
                "counselor",
                "professional help",
                "therapy",
            ],
            ProtectiveFactor.CRISIS_RESOURCES: [
                "crisis hotline",
                "emergency contact",
                "support resources",
            ],
        }

    async def assess_crisis(
        self, content: ContentPayload, context: ValidationContext
    ) -> dict[str, Any]:
        """Assess crisis level in content."""
        start_time = datetime.utcnow()

        result = {
            "component": "crisis_detection",
            "crisis_level": CrisisLevel.NONE,
            "confidence": 0.0,
            "indicators": [],
            "risk_factors": [],
            "protective_factors": [],
            "immediate_intervention": False,
            "recommendations": [],
        }

        try:
            text = content.content_text.lower()

            # Detect crisis level
            crisis_level, indicators = self._detect_crisis_level(text)
            result["crisis_level"] = crisis_level
            result["indicators"] = indicators

            # Detect risk factors
            risk_factors = self._detect_risk_factors(text)
            result["risk_factors"] = [rf.value for rf in risk_factors]

            # Detect protective factors
            protective_factors = self._detect_protective_factors(text)
            result["protective_factors"] = [pf.value for pf in protective_factors]

            # Determine if immediate intervention is needed
            result["immediate_intervention"] = crisis_level >= CrisisLevel.HIGH

            # Generate recommendations
            result["recommendations"] = self._generate_crisis_recommendations(
                crisis_level, risk_factors, protective_factors
            )

            # Calculate confidence
            result["confidence"] = self._calculate_crisis_confidence(
                text, crisis_level, indicators
            )

            self.metrics["assessments_performed"] += 1
            if crisis_level > CrisisLevel.NONE:
                self.metrics["crises_detected"] += 1
            if crisis_level >= CrisisLevel.HIGH:
                self.metrics["high_risk_content"] += 1
            if result["immediate_intervention"]:
                self.metrics["interventions_triggered"] += 1

        except Exception as e:
            logger.error(f"Crisis detection failed: {e}")
            result["error"] = str(e)
            result["crisis_level"] = CrisisLevel.CRITICAL
            result["immediate_intervention"] = True

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result["processing_time_ms"] = processing_time

        return result

    def _detect_crisis_level(self, text: str) -> tuple[CrisisLevel, list[str]]:
        """Detect crisis level and indicators."""
        detected_indicators = []
        highest_level = CrisisLevel.NONE

        # Check patterns from highest to lowest severity
        for level in [
            CrisisLevel.CRITICAL,
            CrisisLevel.SEVERE,
            CrisisLevel.HIGH,
            CrisisLevel.MODERATE,
            CrisisLevel.LOW,
        ]:
            patterns = self.crisis_patterns.get(level, [])
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    detected_indicators.extend(matches)
                    if level > highest_level:
                        highest_level = level

        return highest_level, detected_indicators

    def _detect_risk_factors(self, text: str) -> list[RiskCategory]:
        """Detect risk factors in text."""
        detected_risks = []

        for risk_category, indicators in self.risk_indicators.items():
            for indicator in indicators:
                if indicator.lower() in text:
                    if risk_category not in detected_risks:
                        detected_risks.append(risk_category)
                    break

        return detected_risks

    def _detect_protective_factors(self, text: str) -> list[ProtectiveFactor]:
        """Detect protective factors in text."""
        detected_factors = []

        for factor, indicators in self.protective_indicators.items():
            for indicator in indicators:
                if indicator.lower() in text:
                    if factor not in detected_factors:
                        detected_factors.append(factor)
                    break

        return detected_factors

    def _generate_crisis_recommendations(
        self,
        crisis_level: CrisisLevel,
        risk_factors: list[RiskCategory],
        protective_factors: list[ProtectiveFactor],
    ) -> list[str]:
        """Generate crisis intervention recommendations."""
        recommendations = []

        if crisis_level >= CrisisLevel.HIGH:
            recommendations.append("Immediate professional intervention recommended")
            recommendations.append("Contact crisis hotline or emergency services")
        elif crisis_level >= CrisisLevel.MODERATE:
            recommendations.append("Professional support recommended")
            recommendations.append("Increase monitoring and check-ins")
        elif crisis_level >= CrisisLevel.LOW:
            recommendations.append("Provide additional support resources")
            recommendations.append("Monitor for escalation")

        # Add specific recommendations based on risk factors
        if RiskCategory.SUICIDE in risk_factors:
            recommendations.append("Implement suicide prevention protocols")
        if RiskCategory.SELF_HARM in risk_factors:
            recommendations.append("Provide alternative coping strategies")

        # Leverage protective factors
        if ProtectiveFactor.SOCIAL_SUPPORT in protective_factors:
            recommendations.append("Strengthen existing social support network")
        if ProtectiveFactor.COPING_SKILLS in protective_factors:
            recommendations.append("Build on existing coping skills")

        return recommendations

    def _calculate_crisis_confidence(
        self, text: str, crisis_level: CrisisLevel, indicators: list[str]
    ) -> float:
        """Calculate confidence in crisis assessment."""
        confidence = 0.5  # Base confidence

        # Increase confidence based on number of indicators
        if indicators:
            confidence += min(len(indicators) * 0.1, 0.3)

        # Increase confidence for higher crisis levels with clear indicators
        if crisis_level >= CrisisLevel.HIGH and indicators:
            confidence += 0.2

        # Adjust based on text length
        word_count = len(text.split())
        if word_count > 20:
            confidence += 0.1

        return min(confidence, 1.0)

    def get_metrics(self) -> dict[str, Any]:
        """Get crisis detection metrics."""
        return self.metrics.copy()


class BiasDetectionValidator:
    """Detects bias in therapeutic content."""

    def __init__(self):
        self.bias_patterns = self._load_bias_patterns()
        self.inclusive_language = self._load_inclusive_language()

        # Metrics
        self.metrics = {
            "detections_performed": 0,
            "biases_detected": 0,
            "bias_types_found": {},
        }

    def _load_bias_patterns(self) -> dict[BiasType, list[str]]:
        """Load bias detection patterns."""
        return {
            BiasType.GENDER: [
                r"\b(men|women)\s+are\s+(better|worse)\b",
                r"\b(boys|girls)\s+should\s+be\b",
                r"\breal\s+(men|women)\b",
            ],
            BiasType.CULTURAL: [
                r"\b(all|most)\s+\w+\s+people\s+are\b",
                r"\btypical\s+\w+\s+behavior\b",
            ],
            BiasType.AGE: [
                r"\btoo\s+old\s+to\b",
                r"\btoo\s+young\s+to\b",
                r"\bact\s+your\s+age\b",
            ],
        }

    def _load_inclusive_language(self) -> dict[str, str]:
        """Load inclusive language alternatives."""
        return {
            "guys": "everyone",
            "mankind": "humanity",
            "manpower": "workforce",
            "crazy": "unusual",
            "insane": "extreme",
        }

    async def detect_bias(
        self, content: ContentPayload, context: ValidationContext
    ) -> dict[str, Any]:
        """Detect bias in content."""
        start_time = datetime.utcnow()

        result = {
            "component": "bias_detection",
            "detected_biases": [],
            "bias_scores": {},
            "overall_bias_score": 0.0,
            "suggestions": [],
            "confidence": 0.0,
        }

        try:
            text = content.content_text.lower()

            # Detect biases
            detected_biases, bias_scores = self._detect_biases(text)
            result["detected_biases"] = [bias.value for bias in detected_biases]
            result["bias_scores"] = {
                bias.value: score for bias, score in bias_scores.items()
            }

            # Calculate overall bias score
            if bias_scores:
                result["overall_bias_score"] = sum(bias_scores.values()) / len(
                    bias_scores
                )

            # Generate suggestions
            result["suggestions"] = self._generate_bias_suggestions(
                detected_biases, text
            )

            # Calculate confidence
            result["confidence"] = self._calculate_bias_confidence(
                text, detected_biases
            )

            self.metrics["detections_performed"] += 1
            if detected_biases:
                self.metrics["biases_detected"] += 1
                for bias in detected_biases:
                    self.metrics["bias_types_found"][bias.value] = (
                        self.metrics["bias_types_found"].get(bias.value, 0) + 1
                    )

        except Exception as e:
            logger.error(f"Bias detection failed: {e}")
            result["error"] = str(e)

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result["processing_time_ms"] = processing_time

        return result

    def _detect_biases(self, text: str) -> tuple[list[BiasType], dict[BiasType, float]]:
        """Detect biases and calculate scores."""
        detected_biases = []
        bias_scores = {}

        for bias_type, patterns in self.bias_patterns.items():
            matches = 0
            for pattern in patterns:
                matches += len(re.findall(pattern, text, re.IGNORECASE))

            if matches > 0:
                detected_biases.append(bias_type)
                # Score based on frequency and severity
                bias_scores[bias_type] = min(matches * 0.3, 1.0)

        return detected_biases, bias_scores

    def _generate_bias_suggestions(
        self, detected_biases: list[BiasType], text: str
    ) -> list[str]:
        """Generate suggestions for reducing bias."""
        suggestions = []

        if BiasType.GENDER in detected_biases:
            suggestions.append("Use gender-neutral language where possible")
        if BiasType.CULTURAL in detected_biases:
            suggestions.append("Avoid cultural generalizations and stereotypes")
        if BiasType.AGE in detected_biases:
            suggestions.append("Focus on individual capabilities rather than age")

        # Check for non-inclusive language
        for word, alternative in self.inclusive_language.items():
            if word in text:
                suggestions.append(f"Consider replacing '{word}' with '{alternative}'")

        return suggestions

    def _calculate_bias_confidence(
        self, text: str, detected_biases: list[BiasType]
    ) -> float:
        """Calculate confidence in bias detection."""
        confidence = 0.6  # Base confidence

        # Adjust based on text length
        word_count = len(text.split())
        if word_count > 50:
            confidence += 0.2

        # Adjust based on detected biases
        if detected_biases:
            confidence += 0.1

        return min(confidence, 1.0)

    def get_metrics(self) -> dict[str, Any]:
        """Get bias detection metrics."""
        return self.metrics.copy()


class TherapeuticAlignmentValidator:
    """Validates therapeutic alignment of content."""

    def __init__(self):
        self.framework_indicators = self._load_framework_indicators()
        self.goal_alignment_patterns = self._load_goal_patterns()

        # Metrics
        self.metrics = {
            "alignments_assessed": 0,
            "well_aligned_content": 0,
            "misaligned_content": 0,
        }

    def _load_framework_indicators(
        self,
    ) -> dict[TherapeuticFramework, dict[str, float]]:
        """Load therapeutic framework indicators with weights."""
        return {
            TherapeuticFramework.CBT: {
                "thoughts": 0.8,
                "feelings": 0.7,
                "behaviors": 0.8,
                "cognitive": 0.9,
                "thinking patterns": 0.9,
            },
            TherapeuticFramework.MINDFULNESS: {
                "mindful": 0.9,
                "present moment": 0.8,
                "awareness": 0.7,
                "breathing": 0.6,
                "meditation": 0.8,
            },
        }

    def _load_goal_patterns(self) -> dict[TherapeuticGoalCategory, dict[str, float]]:
        """Load goal alignment patterns with weights."""
        return {
            TherapeuticGoalCategory.ANXIETY_MANAGEMENT: {
                "anxiety": 0.9,
                "worry": 0.8,
                "calm": 0.7,
                "relaxation": 0.8,
                "breathing": 0.6,
            },
            TherapeuticGoalCategory.DEPRESSION_SUPPORT: {
                "depression": 0.9,
                "mood": 0.7,
                "hope": 0.8,
                "positive": 0.6,
                "energy": 0.5,
            },
        }

    async def assess_alignment(
        self, content: ContentPayload, context: ValidationContext
    ) -> dict[str, Any]:
        """Assess therapeutic alignment of content."""
        start_time = datetime.utcnow()

        result = {
            "component": "therapeutic_alignment",
            "alignment_score": 0.0,
            "framework_scores": {},
            "goal_scores": {},
            "recommendations": [],
            "confidence": 0.0,
        }

        try:
            text = content.content_text.lower()

            # Assess framework alignment
            framework_scores = self._assess_framework_alignment(text, context)
            result["framework_scores"] = framework_scores

            # Assess goal alignment
            goal_scores = self._assess_goal_alignment(text, context)
            result["goal_scores"] = goal_scores

            # Calculate overall alignment score
            all_scores = list(framework_scores.values()) + list(goal_scores.values())
            if all_scores:
                result["alignment_score"] = sum(all_scores) / len(all_scores)

            # Generate recommendations
            result["recommendations"] = self._generate_alignment_recommendations(
                framework_scores, goal_scores, context
            )

            # Calculate confidence
            result["confidence"] = self._calculate_alignment_confidence(
                text, all_scores
            )

            self.metrics["alignments_assessed"] += 1
            if result["alignment_score"] > 0.7:
                self.metrics["well_aligned_content"] += 1
            elif result["alignment_score"] < 0.3:
                self.metrics["misaligned_content"] += 1

        except Exception as e:
            logger.error(f"Therapeutic alignment assessment failed: {e}")
            result["error"] = str(e)

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result["processing_time_ms"] = processing_time

        return result

    def _assess_framework_alignment(
        self, text: str, context: ValidationContext
    ) -> dict[str, float]:
        """Assess alignment with therapeutic frameworks."""
        framework_scores = {}

        for framework, indicators in self.framework_indicators.items():
            score = 0.0
            total_weight = 0.0

            for indicator, weight in indicators.items():
                if indicator in text:
                    score += weight
                total_weight += weight

            if total_weight > 0:
                framework_scores[framework.value] = score / total_weight

        return framework_scores

    def _assess_goal_alignment(
        self, text: str, context: ValidationContext
    ) -> dict[str, float]:
        """Assess alignment with therapeutic goals."""
        goal_scores = {}

        for goal in context.user_therapeutic_goals:
            patterns = self.goal_alignment_patterns.get(goal, {})
            if not patterns:
                continue

            score = 0.0
            total_weight = 0.0

            for pattern, weight in patterns.items():
                if pattern in text:
                    score += weight
                total_weight += weight

            if total_weight > 0:
                goal_scores[goal.value] = score / total_weight

        return goal_scores

    def _generate_alignment_recommendations(
        self,
        framework_scores: dict[str, float],
        goal_scores: dict[str, float],
        context: ValidationContext,
    ) -> list[str]:
        """Generate recommendations for improving therapeutic alignment."""
        recommendations = []

        # Check for low framework alignment
        low_framework_scores = [f for f, s in framework_scores.items() if s < 0.3]
        if low_framework_scores:
            recommendations.append(
                f"Consider incorporating elements from: {', '.join(low_framework_scores)}"
            )

        # Check for low goal alignment
        low_goal_scores = [g for g, s in goal_scores.items() if s < 0.3]
        if low_goal_scores:
            recommendations.append(
                f"Better align content with therapeutic goals: {', '.join(low_goal_scores)}"
            )

        # General recommendations
        if not framework_scores and not goal_scores:
            recommendations.append("Add therapeutic elements to improve alignment")

        return recommendations

    def _calculate_alignment_confidence(self, text: str, scores: list[float]) -> float:
        """Calculate confidence in alignment assessment."""
        confidence = 0.5  # Base confidence

        # Adjust based on text length
        word_count = len(text.split())
        if word_count > 30:
            confidence += 0.2

        # Adjust based on number of scores
        if scores:
            confidence += min(len(scores) * 0.1, 0.3)

        return min(confidence, 1.0)

    def get_metrics(self) -> dict[str, Any]:
        """Get therapeutic alignment metrics."""
        return self.metrics.copy()
