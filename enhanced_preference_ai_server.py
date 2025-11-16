#!/usr/bin/env python3
"""
Enhanced TTA API Server with Player Preference Integration

This enhanced version demonstrates how player preferences can be integrated
into the AI processing pipeline for personalized therapeutic experiences.

Key Enhancements:
1. Player preference configuration and storage
2. Preference-aware context processing
3. Adaptive therapeutic prompt generation
4. Personalized response selection
5. Therapeutic intensity customization
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntensityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TherapeuticApproach(Enum):
    CBT = "cognitive_behavioral_therapy"
    MINDFULNESS = "mindfulness"
    NARRATIVE = "narrative_therapy"
    SOMATIC = "somatic_therapy"
    HUMANISTIC = "humanistic"


@dataclass
class PlayerPreferences:
    """Player preference configuration for personalized therapeutic experiences."""

    player_id: str
    intensity_level: IntensityLevel = IntensityLevel.MEDIUM
    preferred_approaches: list[TherapeuticApproach] = field(default_factory=list)
    therapeutic_goals: list[str] = field(default_factory=list)
    conversation_style: str = "supportive"  # supportive, direct, exploratory, gentle
    trigger_topics: list[str] = field(default_factory=list)
    comfort_topics: list[str] = field(default_factory=list)
    preferred_setting: str = "peaceful_forest"
    character_name: str = "Alex"
    session_duration_preference: int = 30
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class EnhancedContext:
    """Enhanced context with player preference integration."""

    user_message: str
    player_preferences: PlayerPreferences
    session_state: dict[str, Any]
    emotional_analysis: dict[str, Any] = field(default_factory=dict)
    therapeutic_context: dict[str, Any] = field(default_factory=dict)
    prompt_adaptations: list[str] = field(default_factory=list)
    turn_count: int = 1


class PreferenceAwareAIGenerator:
    """AI generator with comprehensive player preference integration."""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.has_api_key = bool(self.api_key)
        self.api_available = False

        # Player preference storage (in production, this would be a database)
        self.player_preferences: dict[str, PlayerPreferences] = {}

        logger.info(
            f"🤖 Preference-Aware AI Generator initialized - API Key: {'✅ Present' if self.has_api_key else '❌ Missing'}"
        )

    async def initialize(self):
        """Initialize AI generator and test API connectivity."""
        if self.has_api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/models",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                    )
                    if response.status_code == 200:
                        models = response.json()
                        self.api_available = True
                        logger.info(
                            f"✅ OpenRouter API connected - {len(models.get('data', []))} models available"
                        )
                    else:
                        logger.warning(
                            f"⚠️ OpenRouter API connection failed: {response.status_code}"
                        )
            except Exception as e:
                logger.warning(f"⚠️ OpenRouter API connection error: {e}")

    def set_player_preferences(self, preferences: PlayerPreferences):
        """Set player preferences for personalized AI processing."""
        self.player_preferences[preferences.player_id] = preferences
        logger.info(f"✅ Player preferences set for {preferences.player_id}")

    def get_player_preferences(self, player_id: str) -> PlayerPreferences | None:
        """Get player preferences by ID."""
        return self.player_preferences.get(player_id)

    async def generate_personalized_response(
        self, user_message: str, player_id: str, session_state: dict[str, Any] = None
    ) -> tuple[str, bool, dict[str, Any]]:
        """Generate personalized therapeutic response based on player preferences."""

        # Get player preferences
        preferences = self.get_player_preferences(player_id)
        if not preferences:
            # Create default preferences if none exist
            preferences = PlayerPreferences(player_id=player_id)
            self.set_player_preferences(preferences)

        # Build enhanced context
        enhanced_context = self._build_enhanced_context(
            user_message, preferences, session_state or {}
        )

        # Generate response using AI or enhanced fallback
        if self.api_available and self.has_api_key:
            ai_response = await self._generate_preference_aware_ai_response(
                enhanced_context
            )
            if ai_response:
                return ai_response, True, enhanced_context.therapeutic_context

        # Fallback to enhanced therapeutic responses
        enhanced_response = self._generate_preference_aware_enhanced_response(
            enhanced_context
        )
        return enhanced_response, False, enhanced_context.therapeutic_context

    def _build_enhanced_context(
        self,
        user_message: str,
        preferences: PlayerPreferences,
        session_state: dict[str, Any],
    ) -> EnhancedContext:
        """Build enhanced context with player preference integration."""

        context = EnhancedContext(
            user_message=user_message,
            player_preferences=preferences,
            session_state=session_state,
            turn_count=session_state.get("turn_count", 1),
        )

        # Perform emotional analysis
        context.emotional_analysis = self._analyze_emotional_content(user_message)

        # Build therapeutic context
        context.therapeutic_context = {
            "intensity_level": preferences.intensity_level.value,
            "preferred_approaches": [
                approach.value for approach in preferences.preferred_approaches
            ],
            "therapeutic_goals": preferences.therapeutic_goals,
            "conversation_style": preferences.conversation_style,
            "character_name": preferences.character_name,
            "preferred_setting": preferences.preferred_setting,
            "comfort_topics": preferences.comfort_topics,
            "trigger_topics": preferences.trigger_topics,
        }

        # Generate prompt adaptations
        context.prompt_adaptations = self._generate_prompt_adaptations(context)

        return context

    def _analyze_emotional_content(self, message: str) -> dict[str, Any]:
        """Analyze emotional content of user message."""
        message_lower = message.lower()

        # Enhanced emotional analysis
        emotions = {
            "anxiety": {
                "detected": any(
                    word in message_lower
                    for word in [
                        "anxious",
                        "worried",
                        "nervous",
                        "scared",
                        "afraid",
                        "stress",
                        "panic",
                        "overwhelmed",
                    ]
                ),
                "intensity": self._calculate_emotion_intensity(
                    message_lower,
                    [
                        "anxious",
                        "worried",
                        "nervous",
                        "scared",
                        "afraid",
                        "stress",
                        "panic",
                        "overwhelmed",
                    ],
                ),
            },
            "sadness": {
                "detected": any(
                    word in message_lower
                    for word in ["sad", "depressed", "down", "low", "hopeless", "empty"]
                ),
                "intensity": self._calculate_emotion_intensity(
                    message_lower,
                    ["sad", "depressed", "down", "low", "hopeless", "empty"],
                ),
            },
            "anger": {
                "detected": any(
                    word in message_lower
                    for word in ["angry", "mad", "frustrated", "irritated", "furious"]
                ),
                "intensity": self._calculate_emotion_intensity(
                    message_lower,
                    ["angry", "mad", "frustrated", "irritated", "furious"],
                ),
            },
            "joy": {
                "detected": any(
                    word in message_lower
                    for word in ["happy", "joyful", "excited", "glad", "content"]
                ),
                "intensity": self._calculate_emotion_intensity(
                    message_lower, ["happy", "joyful", "excited", "glad", "content"]
                ),
            },
            "calm": {
                "detected": any(
                    word in message_lower
                    for word in ["calm", "peaceful", "relaxed", "serene", "tranquil"]
                ),
                "intensity": self._calculate_emotion_intensity(
                    message_lower, ["calm", "peaceful", "relaxed", "serene", "tranquil"]
                ),
            },
        }

        # Determine primary emotion
        primary_emotion = None
        max_intensity = 0
        for emotion, data in emotions.items():
            if data["detected"] and data["intensity"] > max_intensity:
                primary_emotion = emotion
                max_intensity = data["intensity"]

        # Analyze therapeutic needs
        therapeutic_needs = {
            "grounding_needed": emotions["anxiety"]["detected"]
            and emotions["anxiety"]["intensity"] > 0.5,
            "validation_needed": emotions["sadness"]["detected"]
            or any(
                word in message_lower for word in ["alone", "misunderstood", "unheard"]
            ),
            "coping_strategies": any(
                word in message_lower for word in ["help", "manage", "cope", "handle"]
            ),
            "exploration_desired": any(
                word in message_lower
                for word in ["explore", "understand", "learn", "discover"]
            ),
            "crisis_indicators": any(
                phrase in message_lower
                for phrase in ["can't go on", "end it all", "no point", "hurt myself"]
            ),
        }

        return {
            "emotions": emotions,
            "primary_emotion": primary_emotion,
            "emotional_intensity": max_intensity,
            "therapeutic_needs": therapeutic_needs,
            "complexity_score": sum(
                1 for emotion in emotions.values() if emotion["detected"]
            ),
        }

    def _calculate_emotion_intensity(self, message: str, keywords: list[str]) -> float:
        """Calculate emotional intensity based on keyword presence and modifiers."""
        base_intensity = sum(1 for keyword in keywords if keyword in message) / len(
            keywords
        )

        # Intensity modifiers
        if any(
            modifier in message
            for modifier in ["very", "extremely", "really", "so", "incredibly"]
        ):
            base_intensity *= 1.5
        if any(
            modifier in message
            for modifier in ["a bit", "somewhat", "kind of", "sort of"]
        ):
            base_intensity *= 0.7

        return min(base_intensity, 1.0)

    def _generate_prompt_adaptations(self, context: EnhancedContext) -> list[str]:
        """Generate prompt adaptations based on context and preferences."""
        adaptations = []
        prefs = context.player_preferences
        emotional_analysis = context.emotional_analysis

        # Intensity-based adaptations
        if prefs.intensity_level == IntensityLevel.LOW:
            adaptations.extend(
                [
                    "Use gentle, non-confrontational language",
                    "Focus on comfort and safety",
                    "Avoid challenging or probing questions",
                    "Emphasize grounding and calming techniques",
                ]
            )
        elif prefs.intensity_level == IntensityLevel.HIGH:
            adaptations.extend(
                [
                    "Use direct, engaging language",
                    "Include challenging but supportive questions",
                    "Encourage deeper exploration",
                    "Focus on growth and transformation",
                ]
            )
        else:  # MEDIUM
            adaptations.extend(
                [
                    "Balance support with gentle challenges",
                    "Encourage exploration at comfortable pace",
                    "Include both grounding and growth elements",
                ]
            )

        # Approach-based adaptations
        for approach in prefs.preferred_approaches:
            if approach == TherapeuticApproach.CBT:
                adaptations.append(
                    "Focus on thoughts, feelings, and behavior connections"
                )
            elif approach == TherapeuticApproach.MINDFULNESS:
                adaptations.append("Include mindfulness and present-moment awareness")
            elif approach == TherapeuticApproach.NARRATIVE:
                adaptations.append("Use storytelling and meaning-making approaches")
            elif approach == TherapeuticApproach.SOMATIC:
                adaptations.append("Include body awareness and physical sensations")

        # Goal-based adaptations
        for goal in prefs.therapeutic_goals:
            if goal == "anxiety_reduction":
                adaptations.append("Include calming and grounding techniques")
            elif goal == "confidence_building":
                adaptations.append("Emphasize strengths and capabilities")
            elif goal == "emotional_processing":
                adaptations.append("Encourage emotional exploration and expression")
            elif goal == "mindfulness":
                adaptations.append("Focus on present-moment awareness")

        # Emotional state adaptations
        if emotional_analysis["therapeutic_needs"]["grounding_needed"]:
            adaptations.append("Prioritize grounding and stabilization techniques")
        if emotional_analysis["therapeutic_needs"]["validation_needed"]:
            adaptations.append("Provide validation and emotional support")
        if emotional_analysis["therapeutic_needs"]["crisis_indicators"]:
            adaptations.append(
                "CRISIS PROTOCOL: Provide immediate support and resources"
            )

        return adaptations

    async def _generate_preference_aware_ai_response(
        self, context: EnhancedContext
    ) -> str | None:
        """Generate AI response with preference-aware prompt engineering."""
        try:
            # Create adaptive therapeutic prompt
            therapeutic_prompt = self._create_adaptive_therapeutic_prompt(context)

            # Select model based on preferences
            model = self._select_optimal_model(context.player_preferences)

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": self._create_system_prompt(
                            context.player_preferences
                        ),
                    },
                    {"role": "user", "content": therapeutic_prompt},
                ],
                "temperature": self._calculate_temperature(context.player_preferences),
                "max_tokens": self._calculate_max_tokens(context.player_preferences),
                "top_p": 0.9,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    ai_response = data["choices"][0]["message"]["content"].strip()
                    logger.info(
                        f"✅ AI generated personalized therapeutic narrative ({len(ai_response)} chars)"
                    )
                    return ai_response
                logger.warning(f"⚠️ AI generation failed: {response.status_code}")
                return None

        except Exception as e:
            logger.warning(f"⚠️ AI generation error: {e}")
            return None

    def _create_system_prompt(self, preferences: PlayerPreferences) -> str:
        """Create personalized system prompt based on player preferences."""
        base_prompt = "You are a compassionate therapeutic storytelling AI that helps users explore emotions through immersive, calming narratives."

        # Add intensity-specific guidance
        if preferences.intensity_level == IntensityLevel.LOW:
            base_prompt += (
                " Use gentle, supportive language and focus on comfort and safety."
            )
        elif preferences.intensity_level == IntensityLevel.HIGH:
            base_prompt += (
                " Use engaging, direct language and encourage deeper exploration."
            )

        # Add approach-specific guidance
        if preferences.preferred_approaches:
            approaches = [
                approach.value.replace("_", " ")
                for approach in preferences.preferred_approaches
            ]
            base_prompt += (
                f" Incorporate {', '.join(approaches)} therapeutic approaches."
            )

        base_prompt += " Keep responses conversational and under 200 words."

        return base_prompt

    def _create_adaptive_therapeutic_prompt(self, context: EnhancedContext) -> str:
        """Create adaptive therapeutic prompt based on enhanced context."""
        prefs = context.player_preferences
        emotional_analysis = context.emotional_analysis

        prompt_parts = [
            f'Create a therapeutic narrative response for: "{context.user_message}"',
            "",
            "Player Context:",
            f"- Character: {prefs.character_name}",
            f"- Setting: {prefs.preferred_setting.replace('_', ' ')}",
            f"- Therapeutic Intensity: {prefs.intensity_level.value}",
            f"- Conversation Style: {prefs.conversation_style}",
            f"- Turn: {context.turn_count}",
            "",
        ]

        # Add emotional context
        if emotional_analysis["primary_emotion"]:
            prompt_parts.append(
                f"Detected Primary Emotion: {emotional_analysis['primary_emotion']} (intensity: {emotional_analysis['emotional_intensity']:.1f})"
            )

        # Add therapeutic goals
        if prefs.therapeutic_goals:
            prompt_parts.append(
                f"Therapeutic Goals: {', '.join(prefs.therapeutic_goals)}"
            )

        # Add adaptations
        if context.prompt_adaptations:
            prompt_parts.extend(["", "Therapeutic Adaptations:"])
            for adaptation in context.prompt_adaptations:
                prompt_parts.append(f"- {adaptation}")

        # Add comfort/trigger topic guidance
        if prefs.comfort_topics:
            prompt_parts.append(
                f"Comfort Topics to Include: {', '.join(prefs.comfort_topics)}"
            )
        if prefs.trigger_topics:
            prompt_parts.append(f"Topics to Avoid: {', '.join(prefs.trigger_topics)}")

        prompt_parts.extend(
            [
                "",
                "Response Requirements:",
                "- Acknowledge user's message with empathy",
                "- Continue immersive, therapeutic narrative",
                "- Include a gentle question for continued engagement",
                "- Maintain therapeutic boundaries",
                "- Keep response under 200 words",
            ]
        )

        return "\n".join(prompt_parts)

    def _select_optimal_model(self, preferences: PlayerPreferences) -> str:
        """Select optimal AI model based on player preferences."""
        # For high intensity, use larger models for more sophisticated responses
        if preferences.intensity_level == IntensityLevel.HIGH:
            return "meta-llama/llama-3.2-3b-instruct:free"
        # For low intensity, use gentler models
        if preferences.intensity_level == IntensityLevel.LOW:
            return "microsoft/phi-3-mini-128k-instruct:free"
        # Default for medium intensity
        return "meta-llama/llama-3.2-3b-instruct:free"

    def _calculate_temperature(self, preferences: PlayerPreferences) -> float:
        """Calculate temperature based on preferences."""
        if preferences.intensity_level == IntensityLevel.LOW:
            return 0.5  # More consistent, gentle responses
        if preferences.intensity_level == IntensityLevel.HIGH:
            return 0.8  # More creative, varied responses
        return 0.7  # Balanced creativity

    def _calculate_max_tokens(self, preferences: PlayerPreferences) -> int:
        """Calculate max tokens based on preferences."""
        if preferences.conversation_style == "direct":
            return 150  # Shorter, more direct responses
        if preferences.conversation_style == "exploratory":
            return 300  # Longer, more detailed responses
        return 200  # Standard length

    def _generate_preference_aware_enhanced_response(
        self, context: EnhancedContext
    ) -> str:
        """Generate enhanced therapeutic response with preference awareness."""
        prefs = context.player_preferences
        emotional_analysis = context.emotional_analysis
        user_lower = context.user_message.lower()

        # Select response category based on emotional analysis and preferences
        if emotional_analysis["therapeutic_needs"]["crisis_indicators"]:
            return self._generate_crisis_response(context)
        if emotional_analysis["emotions"]["anxiety"]["detected"]:
            return self._generate_anxiety_response(context)
        if emotional_analysis["emotions"]["calm"]["detected"]:
            return self._generate_calm_response(context)
        if emotional_analysis["therapeutic_needs"]["exploration_desired"]:
            return self._generate_exploration_response(context)
        return self._generate_general_response(context)

    def _generate_anxiety_response(self, context: EnhancedContext) -> str:
        """Generate anxiety-focused response based on preferences."""
        prefs = context.player_preferences
        intensity = prefs.intensity_level

        if intensity == IntensityLevel.LOW:
            responses = [
                f"I hear that you're feeling anxious, {prefs.character_name}, and that's completely okay. Let's imagine we're in your favorite {prefs.preferred_setting.replace('_', ' ')} where everything feels safe and calm. Can you take a gentle breath with me?",
                f"Anxiety can feel big sometimes, but you're safe here with me, {prefs.character_name}. Picture us sitting quietly in the {prefs.preferred_setting.replace('_', ' ')}. What small thing around us brings you a moment of peace?",
            ]
        elif intensity == IntensityLevel.HIGH:
            responses = [
                f"I recognize the anxiety you're experiencing, {prefs.character_name}. This is your mind trying to protect you, but let's work together to find your strength. In this {prefs.preferred_setting.replace('_', ' ')}, what would facing this anxiety with courage look like?",
                f"Anxiety is information, {prefs.character_name}, and you have the power to work with it. As we stand together in this {prefs.preferred_setting.replace('_', ' ')}, what would it mean to move through this feeling rather than around it?",
            ]
        else:  # MEDIUM
            responses = [
                f"I understand you're feeling anxious, {prefs.character_name}. Let's ground ourselves here in this peaceful {prefs.preferred_setting.replace('_', ' ')}. Can you tell me what you notice around us that helps you feel more centered?",
                f"Anxiety is trying to tell you something, {prefs.character_name}. Here in our safe {prefs.preferred_setting.replace('_', ' ')}, what do you think your anxiety might be trying to protect you from?",
            ]

        # Select response based on turn count
        response_index = min(context.turn_count - 1, len(responses) - 1)
        return responses[response_index]

    def _generate_calm_response(self, context: EnhancedContext) -> str:
        """Generate calm-focused response based on preferences."""
        prefs = context.player_preferences

        responses = [
            f"I'm so glad you're finding peace, {prefs.character_name}. This sense of calm in our {prefs.preferred_setting.replace('_', ' ')} is something you can carry with you. What about this moment feels most nurturing to you?",
            f"Your growing tranquility is beautiful to witness, {prefs.character_name}. Here in this serene {prefs.preferred_setting.replace('_', ' ')}, what would you like to explore about this feeling of peace?",
        ]

        response_index = min(context.turn_count - 1, len(responses) - 1)
        return responses[response_index]

    def _generate_exploration_response(self, context: EnhancedContext) -> str:
        """Generate exploration-focused response based on preferences."""
        prefs = context.player_preferences

        responses = [
            f"Your curiosity is inspiring, {prefs.character_name}. Let's venture deeper into this {prefs.preferred_setting.replace('_', ' ')} where new insights await. What aspect of yourself are you most curious to explore?",
            f"I love your willingness to explore, {prefs.character_name}. As we continue through this {prefs.preferred_setting.replace('_', ' ')}, what questions about yourself feel most important to you right now?",
        ]

        response_index = min(context.turn_count - 1, len(responses) - 1)
        return responses[response_index]

    def _generate_general_response(self, context: EnhancedContext) -> str:
        """Generate general therapeutic response based on preferences."""
        prefs = context.player_preferences

        responses = [
            f"Thank you for sharing that with me, {prefs.character_name}. Here in our peaceful {prefs.preferred_setting.replace('_', ' ')}, you have all the space you need. What feels most important for you to explore right now?",
            f"I appreciate your openness, {prefs.character_name}. In this safe space of our {prefs.preferred_setting.replace('_', ' ')}, what's stirring in your heart that you'd like to give voice to?",
        ]

        response_index = min(context.turn_count - 1, len(responses) - 1)
        return responses[response_index]

    def _generate_crisis_response(self, context: EnhancedContext) -> str:
        """Generate crisis-appropriate response with immediate support."""
        prefs = context.player_preferences

        return f"I hear that you're in a lot of pain right now, {prefs.character_name}, and I want you to know that you're not alone. Your life has value and meaning. If you're having thoughts of hurting yourself, please reach out to a crisis helpline immediately: 988 (Suicide & Crisis Lifeline). Right now, can you tell me one small thing that might bring you even a moment of comfort?"


# Example usage and testing
async def demonstrate_preference_integration():
    """Demonstrate enhanced player preference integration."""
    logger.info("🚀 DEMONSTRATING ENHANCED PREFERENCE INTEGRATION")
    logger.info("=" * 50)

    # Initialize AI generator
    ai_generator = PreferenceAwareAIGenerator()
    await ai_generator.initialize()

    # Create test player preferences
    test_preferences = [
        PlayerPreferences(
            player_id="gentle_user",
            intensity_level=IntensityLevel.LOW,
            preferred_approaches=[TherapeuticApproach.MINDFULNESS],
            therapeutic_goals=["anxiety_reduction", "stress_management"],
            conversation_style="gentle",
            comfort_topics=["nature", "breathing"],
            character_name="Sarah",
            preferred_setting="mountain_meadow",
        ),
        PlayerPreferences(
            player_id="direct_user",
            intensity_level=IntensityLevel.HIGH,
            preferred_approaches=[
                TherapeuticApproach.CBT,
                TherapeuticApproach.NARRATIVE,
            ],
            therapeutic_goals=["confidence_building", "emotional_processing"],
            conversation_style="direct",
            character_name="Marcus",
            preferred_setting="urban_garden",
        ),
    ]

    # Set preferences
    for prefs in test_preferences:
        ai_generator.set_player_preferences(prefs)

    # Test personalized responses
    test_messages = [
        "I'm feeling really anxious about my upcoming presentation.",
        "I've been feeling more at peace lately, especially when I'm in nature.",
    ]

    for i, prefs in enumerate(test_preferences):
        logger.info(f"\n👤 TESTING PREFERENCES FOR {prefs.player_id.upper()}")
        logger.info(f"   Intensity: {prefs.intensity_level.value}")
        logger.info(f"   Style: {prefs.conversation_style}")
        logger.info(f"   Goals: {', '.join(prefs.therapeutic_goals)}")

        response, is_ai, context = await ai_generator.generate_personalized_response(
            test_messages[i], prefs.player_id, {"turn_count": 1}
        )

        logger.info(f'   Response ({len(response)} chars): "{response[:100]}..."')
        logger.info(f"   AI Generated: {'✅' if is_ai else '❌'}")
        logger.info(
            f"   Adaptations Applied: {len(context.get('prompt_adaptations', []))}"
        )


if __name__ == "__main__":
    asyncio.run(demonstrate_preference_integration())
