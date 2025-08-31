"""
Therapeutic Conversation Script Templates

This module provides structured conversation scripts with branching logic,
response validation, and adaptive prompting for character creation conversations.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum


class ConversationStage(str, Enum):
    """Conversation stages for character creation."""

    WELCOME = "welcome"
    IDENTITY = "identity"
    APPEARANCE = "appearance"
    BACKGROUND = "background"
    VALUES = "values"
    RELATIONSHIPS = "relationships"
    THERAPEUTIC_TRANSITION = "therapeutic_transition"
    CONCERNS = "concerns"
    GOALS = "goals"
    PREFERENCES = "preferences"
    READINESS = "readiness"
    SUMMARY = "summary"
    COMPLETION = "completion"


class ResponseType(str, Enum):
    """Types of user responses."""

    DETAILED = "detailed"
    BRIEF = "brief"
    EMOTIONAL = "emotional"
    RESISTANT = "resistant"
    UNCLEAR = "unclear"
    CRISIS = "crisis"


@dataclass
class ConversationPrompt:
    """A conversation prompt with branching logic."""

    stage: ConversationStage
    prompt_id: str
    primary_text: str
    context_text: str | None = None
    follow_up_prompts: list[str] = field(default_factory=list)
    validation_rules: list[str] = field(default_factory=list)
    crisis_indicators: list[str] = field(default_factory=list)
    data_fields: list[str] = field(default_factory=list)  # Fields this prompt collects


@dataclass
class ResponseBranch:
    """Branching logic based on response type."""

    response_type: ResponseType
    next_prompt: str
    validation_message: str | None = None
    therapeutic_response: str | None = None


@dataclass
class ConversationScript:
    """Complete conversation script with branching logic."""

    prompts: dict[str, ConversationPrompt] = field(default_factory=dict)
    branches: dict[str, list[ResponseBranch]] = field(default_factory=dict)
    stage_order: list[ConversationStage] = field(default_factory=list)


class ConversationScriptManager:
    """Manages conversation scripts and branching logic."""

    def __init__(self):
        self.scripts = self._initialize_scripts()
        self.response_classifiers = self._initialize_classifiers()

    def _initialize_scripts(self) -> ConversationScript:
        """Initialize conversation scripts."""
        script = ConversationScript()

        # Welcome Stage
        script.prompts["welcome_intro"] = ConversationPrompt(
            stage=ConversationStage.WELCOME,
            prompt_id="welcome_intro",
            primary_text=(
                "Hello! I'm here to help you create your therapeutic companion - "
                "a character that represents you in your healing journey. This is a safe, "
                "private space where you can share as much or as little as feels comfortable.\n\n"
                "What would you like me to call you?"
            ),
            context_text="Building initial rapport and establishing safety",
            validation_rules=["name_format", "length_check"],
            data_fields=["name"],
        )

        # Identity Stage
        script.prompts["identity_age"] = ConversationPrompt(
            stage=ConversationStage.IDENTITY,
            prompt_id="identity_age",
            primary_text=(
                "It's wonderful to meet you, {name}. I'm curious about how you see yourself. "
                "When you imagine yourself in your mind's eye, what stage of life are you in? "
                "Are you in your childhood years, teenage years, adult years, or perhaps your elder years?"
            ),
            context_text="Different life stages bring unique perspectives and wisdom to our journey.",
            validation_rules=["age_range_valid"],
            data_fields=["age_range"],
        )

        script.prompts["identity_gender"] = ConversationPrompt(
            stage=ConversationStage.IDENTITY,
            prompt_id="identity_gender",
            primary_text=(
                "Thank you for sharing that. How do you identify in terms of gender? "
                "I want to make sure I understand and respect how you see yourself. "
                "You can share whatever feels right for you."
            ),
            context_text="Gender identity is an important part of how we understand ourselves.",
            validation_rules=["non_empty"],
            data_fields=["gender_identity"],
        )

        # Appearance Stage
        script.prompts["appearance_description"] = ConversationPrompt(
            stage=ConversationStage.APPEARANCE,
            prompt_id="appearance_description",
            primary_text=(
                "Can you paint me a picture of how you see yourself? "
                "What do you look like when you imagine yourself in your mind's eye?"
            ),
            context_text="Sometimes how we see ourselves reflects how we feel inside.",
            follow_up_prompts=[
                "What style of clothing makes you feel most like yourself?",
                "Is there anything unique about your appearance that makes you, you?",
            ],
            validation_rules=["non_empty"],
            data_fields=[
                "physical_description",
                "clothing_style",
                "distinctive_features",
            ],
        )

        # Background Stage
        script.prompts["background_story"] = ConversationPrompt(
            stage=ConversationStage.BACKGROUND,
            prompt_id="background_story",
            primary_text=(
                "Every person has a story that brought them to where they are today. "
                "What's your story? What experiences have shaped who you are? "
                "You can share as much or as little as feels comfortable right now."
            ),
            context_text="Your story is unique and valuable.",
            validation_rules=["non_empty"],
            data_fields=["backstory"],
        )

        script.prompts["background_personality"] = ConversationPrompt(
            stage=ConversationStage.BACKGROUND,
            prompt_id="background_personality",
            primary_text=(
                "If someone who knows you well were describing you to a new friend, "
                "what would they say about your personality? What words capture who you are at your core?"
            ),
            context_text="Our personality traits are like colors on a palette - each one adds richness to who we are.",
            validation_rules=["list_format"],
            data_fields=["personality_traits"],
        )

        # Values Stage
        script.prompts["values_core"] = ConversationPrompt(
            stage=ConversationStage.VALUES,
            prompt_id="values_core",
            primary_text=(
                "What matters most to you in life? What principles guide your decisions "
                "when things get complicated?"
            ),
            context_text="Understanding our values helps us make choices that align with who we truly are.",
            validation_rules=["list_format"],
            data_fields=["core_values"],
        )

        script.prompts["values_strengths"] = ConversationPrompt(
            stage=ConversationStage.VALUES,
            prompt_id="values_strengths",
            primary_text=(
                "Let's focus on your strengths for a moment. What are you good at? "
                "What abilities or qualities are you proud of? Sometimes we forget to acknowledge our own gifts."
            ),
            context_text="These strengths will be important resources in your therapeutic journey.",
            validation_rules=["list_format"],
            data_fields=["strengths_and_skills"],
        )

        # Therapeutic Transition
        script.prompts["therapeutic_transition"] = ConversationPrompt(
            stage=ConversationStage.THERAPEUTIC_TRANSITION,
            prompt_id="therapeutic_transition",
            primary_text=(
                "You've shared so much about who you are, and I'm grateful for your openness. "
                "Now I'd like to understand what brought you here today. What are some areas "
                "of your life where you'd like to see positive change or growth?"
            ),
            context_text=(
                "Many people seek support for things like stress, relationships, self-confidence, "
                "life transitions, or simply wanting to understand themselves better."
            ),
            crisis_indicators=["suicide", "self-harm", "abuse", "crisis"],
            validation_rules=["list_format"],
            data_fields=["primary_concerns"],
        )

        # Goals Stage
        script.prompts["goals_vision"] = ConversationPrompt(
            stage=ConversationStage.GOALS,
            prompt_id="goals_vision",
            primary_text=(
                "What would success look like for you in this therapeutic journey? "
                "If we were meeting six months from now and you felt this experience had been worthwhile, "
                "what changes would you notice in your life?"
            ),
            context_text="Goals give us direction and purpose in our journey.",
            validation_rules=["list_format"],
            data_fields=["life_goals", "therapeutic_goals"],
        )

        # Preferences Stage
        script.prompts["preferences_intensity"] = ConversationPrompt(
            stage=ConversationStage.PREFERENCES,
            prompt_id="preferences_intensity",
            primary_text=(
                "Everyone has their own pace for growth and change. Some people prefer a gentle, "
                "supportive approach that feels safe and comfortable. Others want a balanced middle ground. "
                "And some are ready for more intensive therapeutic work that challenges them to grow quickly. "
                "What feels right for you?"
            ),
            context_text=(
                "• Gentle: Focuses on building safety, self-compassion, and gradual exploration\n"
                "• Balanced: Combines support with gentle challenges for steady progress\n"
                "• Intensive: Includes deeper exploration and more direct therapeutic interventions"
            ),
            validation_rules=["intensity_valid"],
            data_fields=["preferred_intensity"],
        )

        script.prompts["preferences_comfort"] = ConversationPrompt(
            stage=ConversationStage.PREFERENCES,
            prompt_id="preferences_comfort",
            primary_text=(
                "What topics or activities feel safe and comfortable for you to explore? "
                "These comfort zones are important - they're your foundation for growth."
            ),
            follow_up_prompts=[
                "Are there areas where you feel ready to be gently challenged or pushed to grow? "
                "Identifying these shows real courage."
            ],
            validation_rules=["list_format"],
            data_fields=["comfort_zones", "challenge_areas"],
        )

        # Readiness Stage
        script.prompts["readiness_assessment"] = ConversationPrompt(
            stage=ConversationStage.READINESS,
            prompt_id="readiness_assessment",
            primary_text=(
                "On a scale where you feel completely ready for change and growth, "
                "where would you place yourself today? There's no right or wrong answer - "
                "this helps me understand how to best support you."
            ),
            context_text="Readiness for change varies and can fluctuate - that's completely normal.",
            validation_rules=["readiness_scale"],
            data_fields=["readiness_level"],
        )

        # Initialize branching logic
        self._initialize_branches(script)

        # Set stage order
        script.stage_order = [
            ConversationStage.WELCOME,
            ConversationStage.IDENTITY,
            ConversationStage.APPEARANCE,
            ConversationStage.BACKGROUND,
            ConversationStage.VALUES,
            ConversationStage.RELATIONSHIPS,
            ConversationStage.THERAPEUTIC_TRANSITION,
            ConversationStage.CONCERNS,
            ConversationStage.GOALS,
            ConversationStage.PREFERENCES,
            ConversationStage.READINESS,
            ConversationStage.SUMMARY,
            ConversationStage.COMPLETION,
        ]

        return script

    def _initialize_branches(self, script: ConversationScript) -> None:
        """Initialize branching logic for responses."""

        # Welcome stage branching
        script.branches["welcome_intro"] = [
            ResponseBranch(
                response_type=ResponseType.DETAILED,
                next_prompt="identity_age",
                therapeutic_response="Thank you for sharing that with me, {name}.",
            ),
            ResponseBranch(
                response_type=ResponseType.BRIEF,
                next_prompt="identity_age",
                therapeutic_response="It's wonderful to meet you, {name}.",
            ),
            ResponseBranch(
                response_type=ResponseType.UNCLEAR,
                next_prompt="welcome_intro",
                validation_message="I want to make sure I heard that right. What would you like me to call you?",
            ),
        ]

        # Identity stage branching
        script.branches["identity_age"] = [
            ResponseBranch(
                response_type=ResponseType.DETAILED,
                next_prompt="identity_gender",
                therapeutic_response="That gives me a good sense of where you are in life.",
            ),
            ResponseBranch(
                response_type=ResponseType.BRIEF,
                next_prompt="identity_gender",
                therapeutic_response="Thank you for sharing that.",
            ),
        ]

        # Therapeutic transition branching
        script.branches["therapeutic_transition"] = [
            ResponseBranch(
                response_type=ResponseType.CRISIS,
                next_prompt="crisis_support",
                therapeutic_response="I hear that you're going through something really difficult right now.",
            ),
            ResponseBranch(
                response_type=ResponseType.EMOTIONAL,
                next_prompt="goals_vision",
                therapeutic_response="Thank you for trusting me with something so personal.",
            ),
            ResponseBranch(
                response_type=ResponseType.DETAILED,
                next_prompt="goals_vision",
                therapeutic_response="These concerns you've shared are completely valid and common.",
            ),
            ResponseBranch(
                response_type=ResponseType.RESISTANT,
                next_prompt="goals_vision",
                therapeutic_response="That's perfectly okay. We can explore this at whatever pace feels right for you.",
            ),
        ]

    def _initialize_classifiers(self) -> dict[str, Callable]:
        """Initialize response classification functions."""
        return {
            "detailed": self._is_detailed_response,
            "brief": self._is_brief_response,
            "emotional": self._is_emotional_response,
            "resistant": self._is_resistant_response,
            "unclear": self._is_unclear_response,
            "crisis": self._is_crisis_response,
        }

    def classify_response(self, response: str, prompt_id: str) -> ResponseType:
        """Classify user response type for branching logic."""
        response_lower = response.lower().strip()

        # Crisis detection (highest priority)
        if self._is_crisis_response(response_lower, prompt_id):
            return ResponseType.CRISIS

        # Emotional response detection
        if self._is_emotional_response(response_lower, prompt_id):
            return ResponseType.EMOTIONAL

        # Resistance detection
        if self._is_resistant_response(response_lower, prompt_id):
            return ResponseType.RESISTANT

        # Unclear response detection
        if self._is_unclear_response(response_lower, prompt_id):
            return ResponseType.UNCLEAR

        # Length-based classification
        if len(response.split()) > 20:
            return ResponseType.DETAILED
        else:
            return ResponseType.BRIEF

    def _is_detailed_response(self, response: str, prompt_id: str) -> bool:
        """Check if response is detailed."""
        return len(response.split()) > 20

    def _is_brief_response(self, response: str, prompt_id: str) -> bool:
        """Check if response is brief."""
        return len(response.split()) <= 20 and len(response.strip()) > 0

    def _is_emotional_response(self, response: str, prompt_id: str) -> bool:
        """Check if response contains emotional indicators."""
        emotional_indicators = [
            "feel",
            "feeling",
            "felt",
            "emotion",
            "sad",
            "happy",
            "angry",
            "scared",
            "anxious",
            "depressed",
            "overwhelmed",
            "hurt",
            "pain",
            "difficult",
            "hard",
            "struggle",
            "crying",
            "tears",
        ]
        return any(indicator in response for indicator in emotional_indicators)

    def _is_resistant_response(self, response: str, prompt_id: str) -> bool:
        """Check if response shows resistance."""
        resistance_indicators = [
            "don't want",
            "not ready",
            "prefer not",
            "rather not",
            "uncomfortable",
            "private",
            "personal",
            "skip",
            "pass",
            "next question",
        ]
        return any(indicator in response for indicator in resistance_indicators)

    def _is_unclear_response(self, response: str, prompt_id: str) -> bool:
        """Check if response is unclear or needs clarification."""
        if len(response.strip()) < 2:
            return True

        unclear_indicators = ["?", "what", "huh", "unclear", "don't understand"]
        return any(indicator in response for indicator in unclear_indicators)

    def _is_crisis_response(self, response: str, prompt_id: str) -> bool:
        """Check if response indicates crisis situation."""
        crisis_indicators = [
            "suicide",
            "kill myself",
            "end it all",
            "don't want to live",
            "self-harm",
            "hurt myself",
            "cutting",
            "abuse",
            "violence",
            "emergency",
            "crisis",
            "help me",
        ]
        return any(indicator in response for indicator in crisis_indicators)

    def get_next_prompt(self, current_prompt_id: str, response: str) -> str | None:
        """Get next prompt based on current prompt and response."""
        response_type = self.classify_response(response, current_prompt_id)

        if current_prompt_id in self.scripts.branches:
            for branch in self.scripts.branches[current_prompt_id]:
                if branch.response_type == response_type:
                    return branch.next_prompt

        return None

    def get_therapeutic_response(
        self, current_prompt_id: str, response: str
    ) -> str | None:
        """Get therapeutic response based on user input."""
        response_type = self.classify_response(response, current_prompt_id)

        if current_prompt_id in self.scripts.branches:
            for branch in self.scripts.branches[current_prompt_id]:
                if branch.response_type == response_type:
                    return branch.therapeutic_response

        return None
