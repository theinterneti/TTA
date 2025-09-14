"""
LangGraph Integration for TTA Prototype

This module extends existing IPA and NGA agents for therapeutic text adventure context,
implements narrative context passing between agents, and adds error handling and fallback
mechanisms for agent failures.

Classes:
    TherapeuticIPA: Enhanced Input Processing Agent for therapeutic context
    TherapeuticNGA: Enhanced Narrative Generator Agent for therapeutic content
    TherapeuticAgentOrchestrator: Orchestrates therapeutic agents with context passing
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TherapeuticContext:
    """Context object for therapeutic narrative generation."""
    session_id: str
    user_emotional_state: dict[str, Any] = field(default_factory=dict)
    therapeutic_goals: list[str] = field(default_factory=list)
    character_relationships: dict[str, float] = field(default_factory=dict)
    narrative_history: list[str] = field(default_factory=list)
    current_location: str = ""
    available_characters: list[str] = field(default_factory=list)
    therapeutic_opportunities: list[str] = field(default_factory=list)
    user_progress: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for agent processing."""
        return {
            "session_id": self.session_id,
            "emotional_state": self.user_emotional_state,
            "therapeutic_goals": self.therapeutic_goals,
            "relationships": self.character_relationships,
            "narrative_history": self.narrative_history[-5:],  # Last 5 entries
            "location": self.current_location,
            "characters": self.available_characters,
            "therapeutic_opportunities": self.therapeutic_opportunities,
            "progress": self.user_progress
        }


@dataclass
class AgentResponse:
    """Response from a therapeutic agent."""
    agent_type: str
    success: bool
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    therapeutic_value: float = 0.0

    def is_valid(self) -> bool:
        """Check if the response is valid."""
        return self.success and bool(self.content.strip())


class TherapeuticIPA:
    """
    Enhanced Input Processing Agent for therapeutic text adventure context.

    Extends the basic IPA functionality to understand therapeutic intent,
    emotional context, and therapeutic opportunities in user input.
    """

    def __init__(self):
        """Initialize the Therapeutic IPA."""
        self.therapeutic_intent_patterns = self._initialize_therapeutic_patterns()
        self.emotional_indicators = self._initialize_emotional_indicators()
        logger.info("TherapeuticIPA initialized")

    def _initialize_therapeutic_patterns(self) -> dict[str, list[str]]:
        """Initialize patterns for recognizing therapeutic intent."""
        return {
            "anxiety_management": [
                "anxious", "worried", "nervous", "panic", "overwhelmed",
                "breathing", "calm", "relax", "stress"
            ],
            "emotional_regulation": [
                "angry", "sad", "frustrated", "upset", "emotional",
                "feelings", "mood", "regulate", "control"
            ],
            "social_connection": [
                "lonely", "isolated", "talk", "connect", "relationship",
                "friend", "support", "understand"
            ],
            "self_reflection": [
                "think", "reflect", "consider", "understand", "realize",
                "insight", "awareness", "mindful"
            ],
            "coping_strategies": [
                "cope", "handle", "manage", "deal with", "strategy",
                "technique", "skill", "practice"
            ]
        }

    def _initialize_emotional_indicators(self) -> dict[str, list[str]]:
        """Initialize patterns for recognizing emotional states."""
        return {
            "anxious": ["anxious", "worried", "nervous", "scared", "tense"],
            "depressed": ["sad", "down", "hopeless", "empty", "depressed"],
            "angry": ["angry", "mad", "furious", "irritated", "frustrated"],
            "excited": ["excited", "happy", "thrilled", "energetic", "joyful"],
            "confused": ["confused", "lost", "uncertain", "unclear", "puzzled"],
            "calm": ["calm", "peaceful", "relaxed", "serene", "tranquil"]
        }

    def process_input(self, user_input: str, therapeutic_context: TherapeuticContext) -> dict[str, Any]:
        """
        Process user input with therapeutic context awareness.

        Args:
            user_input: Raw user input
            therapeutic_context: Current therapeutic context

        Returns:
            Dict[str, Any]: Enhanced parsed input with therapeutic insights
        """
        try:
            # Start with basic parsing
            parsed_input = self._basic_input_parsing(user_input)

            # Add therapeutic intent analysis
            therapeutic_intent = self._analyze_therapeutic_intent(user_input)
            parsed_input["therapeutic_intent"] = therapeutic_intent

            # Add emotional state detection
            detected_emotions = self._detect_emotional_indicators(user_input)
            parsed_input["detected_emotions"] = detected_emotions

            # Add context-aware enhancements
            context_enhancements = self._enhance_with_context(parsed_input, therapeutic_context)
            parsed_input.update(context_enhancements)

            # Calculate therapeutic priority
            parsed_input["therapeutic_priority"] = self._calculate_therapeutic_priority(
                parsed_input, therapeutic_context
            )

            logger.info(f"Processed input with therapeutic intent: {therapeutic_intent}")
            return parsed_input

        except Exception as e:
            logger.error(f"Error in TherapeuticIPA processing: {e}")
            return self._fallback_parsing(user_input)

    def _basic_input_parsing(self, user_input: str) -> dict[str, Any]:
        """Basic input parsing similar to original IPA."""
        user_input = user_input.lower().strip()

        # Default values
        intent = "unknown"
        direction = None
        item_name = None
        character_name = None

        # Basic commands
        if user_input in ["look", "look around", "l"]:
            intent = "look"
        elif user_input in ["inventory", "inv", "i"]:
            intent = "inventory"
        elif user_input in ["help", "what can i do"]:
            intent = "help"

        # Movement commands
        elif user_input in ["north", "n", "go north"]:
            intent = "move"
            direction = "north"
        elif user_input in ["south", "s", "go south"]:
            intent = "move"
            direction = "south"
        elif user_input in ["east", "e", "go east"]:
            intent = "move"
            direction = "east"
        elif user_input in ["west", "w", "go west"]:
            intent = "move"
            direction = "west"

        # Item interaction
        elif user_input.startswith("take ") or user_input.startswith("get "):
            intent = "take"
            item_name = user_input.split(" ", 1)[1] if " " in user_input else ""
        elif user_input.startswith("examine ") or user_input.startswith("look at "):
            intent = "examine"
            item_name = user_input.split(" ", 1)[1] if " " in user_input else ""

        # Character interaction
        elif user_input.startswith("talk to ") or user_input.startswith("talk with "):
            intent = "talk"
            character_name = user_input.split(" ", 2)[2] if len(user_input.split(" ")) > 2 else ""

        return {
            "intent": intent,
            "direction": direction,
            "item_name": item_name,
            "character_name": character_name,
            "original_input": user_input
        }

    def _analyze_therapeutic_intent(self, user_input: str) -> list[str]:
        """Analyze input for therapeutic intent."""
        user_input_lower = user_input.lower()
        therapeutic_intents = []

        for intent_type, patterns in self.therapeutic_intent_patterns.items():
            if any(pattern in user_input_lower for pattern in patterns):
                therapeutic_intents.append(intent_type)

        return therapeutic_intents

    def _detect_emotional_indicators(self, user_input: str) -> dict[str, float]:
        """Detect emotional indicators in user input."""
        user_input_lower = user_input.lower()
        emotional_scores = {}

        for emotion, indicators in self.emotional_indicators.items():
            score = sum(1 for indicator in indicators if indicator in user_input_lower)
            if score > 0:
                emotional_scores[emotion] = min(score / len(indicators), 1.0)

        return emotional_scores

    def _enhance_with_context(self, parsed_input: dict[str, Any],
                            therapeutic_context: TherapeuticContext) -> dict[str, Any]:
        """Enhance parsing with therapeutic context."""
        enhancements = {}

        # Check if input relates to current therapeutic goals
        relevant_goals = []
        for goal in therapeutic_context.therapeutic_goals:
            if any(word in parsed_input["original_input"].lower()
                  for word in goal.lower().split()):
                relevant_goals.append(goal)
        enhancements["relevant_therapeutic_goals"] = relevant_goals

        # Check character relationship context
        if parsed_input.get("character_name"):
            char_name = parsed_input["character_name"]
            if char_name in therapeutic_context.character_relationships:
                enhancements["character_relationship_score"] = therapeutic_context.character_relationships[char_name]

        # Add location-specific therapeutic opportunities
        location_opportunities = []
        for opportunity in therapeutic_context.therapeutic_opportunities:
            if therapeutic_context.current_location.lower() in opportunity.lower():
                location_opportunities.append(opportunity)
        enhancements["location_therapeutic_opportunities"] = location_opportunities

        return enhancements

    def _calculate_therapeutic_priority(self, parsed_input: dict[str, Any],
                                      therapeutic_context: TherapeuticContext) -> float:
        """Calculate therapeutic priority score for the input."""
        priority = 0.0

        # High priority for therapeutic intents
        if parsed_input.get("therapeutic_intent"):
            priority += 0.4 * len(parsed_input["therapeutic_intent"])

        # High priority for emotional indicators
        if parsed_input.get("detected_emotions"):
            priority += 0.3 * len(parsed_input["detected_emotions"])

        # Medium priority for relevant therapeutic goals
        if parsed_input.get("relevant_therapeutic_goals"):
            priority += 0.2 * len(parsed_input["relevant_therapeutic_goals"])

        # Low priority for location opportunities
        if parsed_input.get("location_therapeutic_opportunities"):
            priority += 0.1 * len(parsed_input["location_therapeutic_opportunities"])

        return min(priority, 1.0)

    def _fallback_parsing(self, user_input: str) -> dict[str, Any]:
        """Fallback parsing when main processing fails."""
        return {
            "intent": "unknown",
            "original_input": user_input.lower().strip(),
            "therapeutic_intent": [],
            "detected_emotions": {},
            "therapeutic_priority": 0.1,
            "error": "Fallback parsing used"
        }


class TherapeuticNGA:
    """
    Enhanced Narrative Generator Agent for therapeutic content.

    Extends the basic NGA functionality to generate therapeutically-informed
    narrative content that integrates seamlessly with therapeutic interventions.
    """

    def __init__(self):
        """Initialize the Therapeutic NGA."""
        self.therapeutic_narrative_templates = self._initialize_therapeutic_templates()
        self.emotional_tone_mappings = self._initialize_emotional_tones()
        logger.info("TherapeuticNGA initialized")

    def _initialize_therapeutic_templates(self) -> dict[str, dict[str, list[str]]]:
        """Initialize therapeutic narrative templates."""
        return {
            "anxiety_management": {
                "introduction": [
                    "As you notice the tension in your body, you remember the breathing techniques you've learned.",
                    "The familiar feeling of anxiety begins to rise, but you recognize it as an opportunity to practice your coping skills.",
                    "Your heart rate increases slightly, and you take this as a cue to engage in some self-care."
                ],
                "action_response": [
                    "As you focus on your breathing, you feel your shoulders begin to relax and your mind becomes clearer.",
                    "The grounding technique helps you feel more connected to the present moment and less overwhelmed.",
                    "With each mindful breath, you notice the anxiety beginning to subside, replaced by a sense of calm control."
                ],
                "reflection": [
                    "You take a moment to appreciate how you've learned to manage these feelings more effectively.",
                    "This experience reminds you of your growing ability to cope with challenging emotions.",
                    "You feel proud of yourself for recognizing the anxiety and taking positive action."
                ]
            },
            "emotional_regulation": {
                "introduction": [
                    "Strong emotions wash over you, and you pause to acknowledge what you're feeling.",
                    "You notice the intensity of your emotions and remember that feelings are temporary and manageable.",
                    "The emotional wave feels overwhelming at first, but you've learned strategies to navigate these moments."
                ],
                "action_response": [
                    "By naming your emotions, you create some distance from them and feel more in control.",
                    "The reframing technique helps you see the situation from a different, more balanced perspective.",
                    "As you practice emotional regulation, you feel your intense feelings beginning to settle into something more manageable."
                ],
                "reflection": [
                    "You recognize how much you've grown in your ability to handle difficult emotions.",
                    "This moment of emotional regulation feels like a small victory in your ongoing journey.",
                    "You appreciate the tools you've developed for managing your emotional responses."
                ]
            },
            "social_connection": {
                "introduction": [
                    "The opportunity for meaningful connection presents itself, and you consider how to engage authentically.",
                    "You notice your desire for connection and remember the importance of healthy relationships in your wellbeing.",
                    "The presence of others reminds you of your need for social support and understanding."
                ],
                "action_response": [
                    "Your genuine expression of empathy creates a moment of real connection and mutual understanding.",
                    "By setting a healthy boundary, you demonstrate self-respect while maintaining the relationship.",
                    "The conversation flows naturally, and you feel the warmth of authentic human connection."
                ],
                "reflection": [
                    "You feel grateful for the meaningful connections in your life and your ability to nurture them.",
                    "This interaction reminds you of your capacity for both giving and receiving support.",
                    "You appreciate how healthy relationships contribute to your overall sense of wellbeing."
                ]
            }
        }

    def _initialize_emotional_tones(self) -> dict[str, dict[str, str]]:
        """Initialize emotional tone mappings for narrative generation."""
        return {
            "calming": {
                "atmosphere": "peaceful and serene",
                "sensory": "soft sounds and gentle lighting",
                "pacing": "slow and deliberate"
            },
            "hopeful": {
                "atmosphere": "bright and encouraging",
                "sensory": "warm colors and uplifting sounds",
                "pacing": "steady and forward-moving"
            },
            "supportive": {
                "atmosphere": "safe and understanding",
                "sensory": "comfortable surroundings and welcoming presence",
                "pacing": "patient and accommodating"
            },
            "empowering": {
                "atmosphere": "confident and strong",
                "sensory": "clear vision and solid ground",
                "pacing": "purposeful and determined"
            }
        }

    def generate_narrative(self, parsed_input: dict[str, Any],
                         therapeutic_context: TherapeuticContext,
                         agent_state: Any | None = None) -> AgentResponse:
        """
        Generate therapeutic narrative content.

        Args:
            parsed_input: Processed input from TherapeuticIPA
            therapeutic_context: Current therapeutic context
            agent_state: Optional LangGraph agent state

        Returns:
            AgentResponse: Generated narrative response
        """
        try:
            # Determine narrative type based on therapeutic intent
            narrative_type = self._determine_narrative_type(parsed_input, therapeutic_context)

            # Generate base narrative content
            base_content = self._generate_base_narrative(parsed_input, narrative_type)

            # Add therapeutic enhancements
            therapeutic_content = self._add_therapeutic_enhancements(
                base_content, parsed_input, therapeutic_context
            )

            # Apply emotional tone
            final_content = self._apply_emotional_tone(
                therapeutic_content, parsed_input, therapeutic_context
            )

            # Calculate therapeutic value
            therapeutic_value = self._calculate_therapeutic_value(parsed_input, therapeutic_context)

            return AgentResponse(
                agent_type="therapeutic_nga",
                success=True,
                content=final_content,
                therapeutic_value=therapeutic_value,
                metadata={
                    "narrative_type": narrative_type,
                    "therapeutic_intent": parsed_input.get("therapeutic_intent", []),
                    "emotional_tone": self._determine_emotional_tone(parsed_input, therapeutic_context)
                }
            )

        except Exception as e:
            logger.error(f"Error in TherapeuticNGA generation: {e}")
            return self._generate_fallback_narrative(parsed_input)

    def _determine_narrative_type(self, parsed_input: dict[str, Any],
                                therapeutic_context: TherapeuticContext) -> str:
        """Determine the type of narrative to generate."""
        # Check for high therapeutic priority
        if parsed_input.get("therapeutic_priority", 0) > 0.5:
            therapeutic_intents = parsed_input.get("therapeutic_intent", [])
            if therapeutic_intents:
                return therapeutic_intents[0]  # Use primary therapeutic intent

        # Check for emotional indicators
        detected_emotions = parsed_input.get("detected_emotions", {})
        if detected_emotions:
            strongest_emotion = max(detected_emotions.items(), key=lambda x: x[1])
            if strongest_emotion[1] > 0.5:
                if strongest_emotion[0] in ["anxious", "worried"]:
                    return "anxiety_management"
                elif strongest_emotion[0] in ["angry", "sad"]:
                    return "emotional_regulation"

        # Default to general therapeutic narrative
        return "general_therapeutic"

    def _generate_base_narrative(self, parsed_input: dict[str, Any], narrative_type: str) -> str:
        """Generate base narrative content."""
        intent = parsed_input.get("intent", "unknown")

        if intent == "look":
            return "You take a moment to observe your surroundings with mindful attention."
        elif intent == "move":
            direction = parsed_input.get("direction", "forward")
            return f"You move {direction}, taking each step with intention and awareness."
        elif intent == "talk":
            character = parsed_input.get("character_name", "someone")
            return f"You approach {character} with openness and genuine interest in connecting."
        elif intent == "take":
            item = parsed_input.get("item_name", "the item")
            return f"You reach for {item}, considering its significance in your journey."
        else:
            return "You pause to consider your next action, staying present in this moment."

    def _add_therapeutic_enhancements(self, base_content: str, parsed_input: dict[str, Any],
                                    therapeutic_context: TherapeuticContext) -> str:
        """Add therapeutic enhancements to base narrative."""
        therapeutic_intents = parsed_input.get("therapeutic_intent", [])

        if not therapeutic_intents:
            return base_content

        primary_intent = therapeutic_intents[0]
        templates = self.therapeutic_narrative_templates.get(primary_intent, {})

        # Add therapeutic context
        if "action_response" in templates and templates["action_response"]:
            therapeutic_addition = templates["action_response"][0]  # Use first template
            enhanced_content = f"{base_content} {therapeutic_addition}"
        else:
            enhanced_content = base_content

        # Add progress acknowledgment if relevant
        if therapeutic_context.user_progress:
            progress_note = " You notice how your therapeutic skills continue to develop with each mindful choice you make."
            enhanced_content += progress_note

        return enhanced_content

    def _apply_emotional_tone(self, content: str, parsed_input: dict[str, Any],
                            therapeutic_context: TherapeuticContext) -> str:
        """Apply appropriate emotional tone to the narrative."""
        tone = self._determine_emotional_tone(parsed_input, therapeutic_context)
        tone_mapping = self.emotional_tone_mappings.get(tone, {})

        if tone_mapping:
            atmosphere = tone_mapping.get("atmosphere", "")
            if atmosphere:
                content += f" The atmosphere around you feels {atmosphere}."

        return content

    def _determine_emotional_tone(self, parsed_input: dict[str, Any],
                                therapeutic_context: TherapeuticContext) -> str:
        """Determine appropriate emotional tone for the narrative."""
        therapeutic_intents = parsed_input.get("therapeutic_intent", [])

        if "anxiety_management" in therapeutic_intents:
            return "calming"
        elif "emotional_regulation" in therapeutic_intents:
            return "supportive"
        elif "social_connection" in therapeutic_intents:
            return "hopeful"
        elif "self_reflection" in therapeutic_intents:
            return "empowering"
        else:
            return "supportive"

    def _calculate_therapeutic_value(self, parsed_input: dict[str, Any],
                                   therapeutic_context: TherapeuticContext) -> float:
        """Calculate the therapeutic value of the generated narrative."""
        value = 0.0

        # Base value from therapeutic priority
        value += parsed_input.get("therapeutic_priority", 0) * 0.4

        # Additional value for relevant therapeutic goals
        relevant_goals = parsed_input.get("relevant_therapeutic_goals", [])
        value += len(relevant_goals) * 0.2

        # Additional value for emotional processing
        detected_emotions = parsed_input.get("detected_emotions", {})
        if detected_emotions:
            value += 0.3

        return min(value, 1.0)

    def _generate_fallback_narrative(self, parsed_input: dict[str, Any]) -> AgentResponse:
        """Generate fallback narrative when main generation fails."""
        return AgentResponse(
            agent_type="therapeutic_nga",
            success=True,
            content="You continue your therapeutic journey, staying present and mindful of your experiences.",
            therapeutic_value=0.2,
            metadata={"fallback": True}
        )


class TherapeuticAgentOrchestrator:
    """
    Orchestrates therapeutic agents with context passing and error handling.

    Manages the flow between TherapeuticIPA and TherapeuticNGA, handles agent failures,
    and maintains therapeutic context throughout the interaction.
    """

    def __init__(self):
        """Initialize the Therapeutic Agent Orchestrator."""
        self.ipa = TherapeuticIPA()
        self.nga = TherapeuticNGA()
        self.error_count = 0
        self.max_errors = 3
        logger.info("TherapeuticAgentOrchestrator initialized")

    def process_user_interaction(self, user_input: str, therapeutic_context: TherapeuticContext,
                               langgraph_state: Any | None = None) -> tuple[AgentResponse, TherapeuticContext]:
        """
        Process a complete user interaction through the therapeutic agent pipeline.

        Args:
            user_input: Raw user input
            therapeutic_context: Current therapeutic context
            langgraph_state: Optional LangGraph state for integration

        Returns:
            Tuple[AgentResponse, TherapeuticContext]: Generated response and updated context
        """
        try:
            # Reset error count on successful start
            self.error_count = 0

            # Step 1: Process input through TherapeuticIPA
            ipa_response = self._process_with_ipa(user_input, therapeutic_context)
            if not ipa_response:
                return self._handle_ipa_failure(user_input, therapeutic_context)

            # Step 2: Generate narrative through TherapeuticNGA
            nga_response = self._process_with_nga(ipa_response, therapeutic_context, langgraph_state)
            if not nga_response.is_valid():
                return self._handle_nga_failure(ipa_response, therapeutic_context)

            # Step 3: Update therapeutic context
            updated_context = self._update_therapeutic_context(
                therapeutic_context, ipa_response, nga_response
            )

            logger.info(f"Successfully processed interaction with therapeutic value: {nga_response.therapeutic_value}")
            return nga_response, updated_context

        except Exception as e:
            logger.error(f"Error in therapeutic agent orchestration: {e}")
            return self._handle_orchestration_failure(user_input, therapeutic_context)

    def _process_with_ipa(self, user_input: str, therapeutic_context: TherapeuticContext) -> dict[str, Any] | None:
        """Process input with TherapeuticIPA."""
        try:
            return self.ipa.process_input(user_input, therapeutic_context)
        except Exception as e:
            logger.error(f"TherapeuticIPA processing failed: {e}")
            self.error_count += 1
            return None

    def _process_with_nga(self, parsed_input: dict[str, Any], therapeutic_context: TherapeuticContext,
                         langgraph_state: Any | None = None) -> AgentResponse:
        """Process with TherapeuticNGA."""
        try:
            return self.nga.generate_narrative(parsed_input, therapeutic_context, langgraph_state)
        except Exception as e:
            logger.error(f"TherapeuticNGA processing failed: {e}")
            self.error_count += 1
            return AgentResponse(
                agent_type="therapeutic_nga",
                success=False,
                error_message=str(e)
            )

    def _update_therapeutic_context(self, context: TherapeuticContext,
                                  parsed_input: dict[str, Any],
                                  nga_response: AgentResponse) -> TherapeuticContext:
        """Update therapeutic context based on interaction."""
        # Add to narrative history
        context.narrative_history.append(nga_response.content)

        # Update emotional state if detected
        detected_emotions = parsed_input.get("detected_emotions", {})
        if detected_emotions:
            context.user_emotional_state.update(detected_emotions)

        # Update progress based on therapeutic value
        if nga_response.therapeutic_value > 0:
            therapeutic_intents = parsed_input.get("therapeutic_intent", [])
            for intent in therapeutic_intents:
                current_progress = context.user_progress.get(intent, 0.0)
                context.user_progress[intent] = min(current_progress + nga_response.therapeutic_value * 0.1, 1.0)

        return context

    def _handle_ipa_failure(self, user_input: str, therapeutic_context: TherapeuticContext) -> tuple[AgentResponse, TherapeuticContext]:
        """Handle IPA processing failure."""
        logger.warning("IPA processing failed, using fallback")

        fallback_response = AgentResponse(
            agent_type="fallback",
            success=True,
            content=f"I understand you said '{user_input}'. Let me help you continue your therapeutic journey.",
            therapeutic_value=0.1,
            metadata={"fallback_reason": "ipa_failure"}
        )

        return fallback_response, therapeutic_context

    def _handle_nga_failure(self, parsed_input: dict[str, Any], therapeutic_context: TherapeuticContext) -> tuple[AgentResponse, TherapeuticContext]:
        """Handle NGA processing failure."""
        logger.warning("NGA processing failed, using fallback")

        intent = parsed_input.get("intent", "unknown")
        fallback_content = f"You {intent} thoughtfully. This moment offers an opportunity for reflection and growth."

        fallback_response = AgentResponse(
            agent_type="fallback",
            success=True,
            content=fallback_content,
            therapeutic_value=0.2,
            metadata={"fallback_reason": "nga_failure"}
        )

        return fallback_response, therapeutic_context

    def _handle_orchestration_failure(self, user_input: str, therapeutic_context: TherapeuticContext) -> tuple[AgentResponse, TherapeuticContext]:
        """Handle complete orchestration failure."""
        logger.error("Complete orchestration failure, using emergency fallback")

        self.error_count += 1

        if self.error_count >= self.max_errors:
            content = "I'm experiencing some technical difficulties, but I'm here to support you. Please try rephrasing your input or let me know how else I can help."
        else:
            content = "Let me take a moment to process that. Your therapeutic journey continues, and every step is meaningful."

        emergency_response = AgentResponse(
            agent_type="emergency_fallback",
            success=True,
            content=content,
            therapeutic_value=0.1,
            metadata={"error_count": self.error_count}
        )

        return emergency_response, therapeutic_context

    def get_agent_status(self) -> dict[str, Any]:
        """Get status of all agents."""
        return {
            "ipa_status": "operational",
            "nga_status": "operational",
            "error_count": self.error_count,
            "max_errors": self.max_errors,
            "health": "healthy" if self.error_count < self.max_errors else "degraded"
        }

    def reset_error_count(self) -> None:
        """Reset error count (useful for recovery)."""
        self.error_count = 0
        logger.info("Error count reset")
